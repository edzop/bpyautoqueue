import bpy
import os.path
import os
import time
import functools
import glob
import math

lux_found=False

from ..import util_helper
#util_helper 		= imp.load_source('util_helper','/home/blender/scripts/util_helper.py')
#rend_helper 		= imp.load_source('rend_helper','/home/blender/scripts/rend_helper.py')

import importlib
luxrender_spec = importlib.util.find_spec("luxrender")
lux_found = luxrender_spec is not None

if lux_found==True:
	from luxrender.export.scene import SceneExporter
	from luxrender.export.scene import SceneExporterProperties
	from luxrender.export import geometry as export_geometry
	from luxrender.export import LuxManager

#unwrap_uv_util 		= imp.load_source('unwrap_all_UVs','/home/blender/scripts/unwrap_all_UVs.py')

def setup_dof():
	bpy.context.scene.camera.data.luxcore.use_dof=True
	bpy.context.scene.camera.data.luxcore.fstop=0.95
#	bpy.context.scene.camera.data.luxrender_camera.blades=5
	bpy.context.scene.camera.data.luxcore.use_autofocus=False
	bpy.context.scene.camera.data.show_limits=True


def setup_lux_common_settings():
	bpy.context.scene.render.engine='LUXCORE'

def import_all_materials_from_filelist():
	material_list_file_name="/home/blender/materials.txt"
	texlib_filename = "/home/blender/texlib.blend"

	if os.path.exists(material_list_file_name)==False:
		print("%s not found!"%material_list_file_name)
		exit(1)

	if os.path.exists(texlib_filename)==False:
		print("%s not found!"%texlib_filename)
		exit(1)

	print("importing from " + material_list_file_name)

	if os.path.isfile(material_list_file_name):
		if os.path.getsize(material_list_file_name):

			materiallist = list()
			statusfile = open(material_list_file_name, 'r')
			materiallist = statusfile.readlines()

			material_object_list = []

			for name in materiallist:
				matname=name.strip()
				#print(matname)
				material_object_list.append({'name': matname});

			nob = bpy.ops.wm.link(directory=texlib_filename + '/Material/',files=material_object_list)

	return len(material_object_list)


def lux_scene_is_lit(scene):

	properties = SceneExporterProperties()
	properties.api_type == 'FILE'

	exp = SceneExporter()

	if LuxManager.GetActive() is None:
		LM = LuxManager(
			scene.name,
			api_type = 'FILE'    #properties.api_type,
		)
		LuxManager.SetActive(LM)
		created_lux_manager = True

	LuxManager.SetCurrentScene(scene)
	lux_context = LuxManager.GetActive().lux_context

	GE = export_geometry.GeometryExporter(lux_context, scene)

	is_lit=False

	#TODO - fix for some cases where lux world properties aren't set???
	return False

	try:
		print(scene)
		print(exp)
		exp.set_scene(scene)

		is_lit = exp.scene_is_lit(GE)
#	is_lit = False
		print("scene is lit:")
		print(is_lit)
	except (RuntimeError, TypeError, NameError):
		is_lit=False

	return is_lit


	# todo reuse code from cycles version
def remove_world():
	bpy.context.scene.world=None

		# first clear out all the old worlds
	for cworld in bpy.data.worlds:
	#			print("Removing world: " + str(cworld))
			bpy.data.worlds.remove(cworld)

def set_color_world(gain=(0,0,0)):
	colorworld = bpy.data.worlds.new("colorworld")
	bpy.context.scene.world = colorworld
	colorworld.luxcore.rgb_gain=gain

def set_lux_sky_world():
	luxworld = bpy.data.worlds.new("luxsky")
	bpy.context.scene.world = luxworld


def enable_lux_denoise():

	bpy.context.scene.use_nodes = True

	scene = bpy.context.scene

	render_layers_node=None
	composite_node=None

	#if denoiser not enabled = no denoiser node output, so make sure it's enabled before calling this function

	# need to enable denoiser before render - BUT - node won't be present until AFTER render is complete

	if scene.node_tree:
		nodes = scene.node_tree.nodes

		for node in nodes:               
			if node.type=="COMPOSITE":
				composite_node=node
				
			if node.type=="R_LAYERS":
				render_layers_node=node
				
		if render_layers_node!=None and composite_node!=None:
			scene.node_tree.links.new(render_layers_node.outputs['DENOISED'],composite_node.inputs[0])


def setup_lux_settings():
	setup_lux_common_settings()
	setup_dof()
#	bpy.context.scene.render.engine='LUXCORE'
#	print("lux settings")
#	bpy.context.scene.luxrender_engine.selected_luxrender_api='LUXCORE'
	
	bidir=False

	if bidir==True:
		bpy.context.scene.luxcore.config.device='CPU'
		bpy.context.scene.luxcore.config.engine='BIDIR'
		bpy.context.scene.luxcore.config.sampler="METROPOLIS"
		bpy.context.scene.luxcore.config.filter_enabled = False
	else:
		bpy.context.scene.luxcore.config.device='CPU'
		bpy.context.scene.luxcore.config.engine='PATH'
		bpy.context.scene.luxcore.config.sampler="SOBOL"
		
		bpy.context.scene.luxcore.config.photongi.enabled=False
		
		if bpy.context.scene.frame_current==1:
			bpy.context.scene.luxcore.config.photongi.save_or_overwrite=True
		else:
			bpy.context.scene.luxcore.config.photongi.save_or_overwrite=False

		bpy.context.scene.luxcore.config.path.hybridbackforward_enable=True
			

	bpy.context.scene.camera.data.luxcore.imagepipeline.tonemapper.enabled = True
	bpy.context.scene.camera.data.luxcore.imagepipeline.tonemapper.type = 'TONEMAP_LINEAR'
	bpy.context.scene.camera.data.luxcore.imagepipeline.tonemapper.use_autolinear = True

	bpy.context.scene.view_settings.view_transform="Filmic"
	bpy.context.scene.view_settings.look="High Contrast"

	#bpy.context.object.data.luxcore.imagepipeline.tonemapper.type = 'TONEMAP_REINHARD02'

	
	#bpy.context.scene.luxcore.config.path.use_clamping=True
	
	# disable CPU - it gets hot on laptop for CPU + GPU
	#bpy.context.scene.luxcore.opencl.use_native_cpu=True

	bpy.context.scene.luxcore.halt.enable=True
	
#	bpy.context.scene.luxcore.config.filter="NONE"
	
#	bpy.context.scene.luxcore.config.sampler="RANDOM"
#	bpy.context.scene.luxcore.denoiser.enabled=True
#	bpy.context.scene.luxcore.denoiser.filter_spikes=True

	bpy.context.scene.luxcore.denoiser.enabled = True


#	bpy.context.scene.luxcore.halt.time=60
#	bpy.context.scene.luxcore.halt.use_time=True

	bpy.context.scene.luxcore.halt.use_samples=True
	bpy.context.scene.luxcore.halt.samples=200

#	bpy.context.scene.luxcore.halt.use_noise_thresh=True
#	bpy.context.scene.luxcore.halt.noise_thresh=255

	bpy.context.scene.luxcore.display.interval=240

	enable_lux_denoise()

	#remove_world()


def make_lux_emission_material(name,temp):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	
	tree = bpy.data.node_groups.new(name=name, type="luxcore_material_nodes")
	tree.use_fake_user = True
	mat.luxcore.node_tree = tree
	
	nodes=tree.nodes

	# clear all nodes to start clean
	for node in nodes:
		nodes.remove(node)

	node_emission = nodes.new(type='LuxCoreNodeMatEmission')
	node_emission.location = (0,0)
	node_emission.lightgroup=name
	
	node_black=nodes.new("LuxCoreNodeTexBlackbody")
	node_black.location=(-300,0)
	node_black.temperature=temp


	node_matte = nodes.new("LuxCoreNodeMatMatte")
	node_matte.location = (200, 0)
	node_matte.select = False

	node_output = nodes.new("LuxCoreNodeMatOutput")
	node_output.location = (400, 0)
	node_output.select = False

	tree.links.new(node_emission.outputs[0], node_matte.inputs[4]) 
	tree.links.new(node_matte.outputs[0], node_output.inputs[0]) 
	
	tree.links.new(node_black.outputs[0], node_emission.inputs[0]) 

	return mat

def make_lux_lightgroup(name):
	lg=bpy.context.scene.luxcore.lightgroups.add()
	lg.name=name

def animate_lightgroup(name,keyframes):

	for frame_number,strength_value in keyframes:
		gain = (strength_value*340)
		for lg in bpy.context.scene.luxcore.lightgroups.custom:
			if lg.name==name:
				lg.gain=gain
				lg.keyframe_insert("gain", frame=frame_number)

def animate_emission(mat,keyframes):
	nodes = mat.luxcore.node_tree.nodes
#	mat.luxcore.node_tree
#	nodes=mat.node_tree.nodes
	node_emission = nodes.get("Emission")

	for frame_number,strength_value in keyframes:
		node_emission.gain = (strength_value*400)
		node_emission.keyframe_insert("gain", frame=frame_number)

# TODO share function
def getSequenceFromName(filename,maxVal):
	hashVal = util_helper.stringToHash(filename)
	return hashVal % maxVal

def get_blendfile_without_extension():
	blend_file = os.path.basename(bpy.context.blend_data.filepath)

	blendfile_without_extension = os.path.splitext(blend_file)[0]
	return blendfile_without_extension

def link_random_lux_hdri():
	print("Linking random LUX hdri")

	hdrilist = list()

	hdriindex_index=0

	hdripath='/home/blender/environment/output'

	for infile in glob.glob( os.path.join(hdripath, '*.hdr' )):
		hdrilist.append(infile)

	#for infile in glob.glob( os.path.join(hdripath, '*.exr' )):
	#	hdrilist.append(infile)

	hdrilist.sort()

	hdri_index = getSequenceFromName(get_blendfile_without_extension(),len(hdrilist))

	#print(hdrilist)
	
	hdri_filename=hdrilist[hdri_index]
	print("selected: %s"%hdri_filename)
	bpy.ops.image.open(filepath=hdri_filename)
	filename_without_path=os.path.basename(hdri_filename)

	img=bpy.ops.image.open(filepath=hdri_filename)


	bpy.data.worlds[0].luxcore.light="infinite"
	bpy.data.worlds[0].luxcore.image=bpy.data.images[filename_without_path]
	bpy.data.worlds[0].luxcore.rotation=math.radians(90)

	bpy.context.scene.luxcore.lightgroups.default.gain=0.5

