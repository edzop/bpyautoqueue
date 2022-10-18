import bpy
import sys
import os.path
import os
import time
import functools
import glob
import hashlib

from . import util_helper

from .util_cycles import cycles_helper
from .util_cycles import cycles_world_helper

from . import auto_camera_pan
from . import camera_dolly_helper
from . import environment_helper

class Rend_Helper:

	engine_name_lux="LUXCORE"
	engine_name_cycles="CYCLES"

	inside_scene_name="inside_scene"
	object_scene_name="object_scene"
	autopanstep=0

	#image_file_extension = "PNG"
	image_file_extension = "exr"
	file_format="OPEN_EXR"

	def __init__(self,isolate_output_in_folder=False,autopanstep=0):

		self.autopanstep=autopanstep
		self.scene_lit = False
		self.renderer_name = ''
		self.use_stamp = True

		self.output_path="./output"
		self.max_frames=2
		self.isolate_output_in_folder=isolate_output_in_folder

		if self.isolate_output_in_folder==True:
			self.render_output_path = self.output_path + "/" + util_helper.get_blendfile_without_extension() + "/" + bpy.context.scene.render.engine + "/"
		else:
			self.render_output_path = self.output_path + "/"


		util_helper.ensure_dir(self.render_output_path);

	
		if self.autopanstep>0:
			self.thePanHelper = auto_camera_pan.Cam_Pan_Helper()


	def setup_common_settings(self):
		bpy.context.scene.display_settings.display_device='sRGB'
		return

	def setup_resolution(self,width,height,scale):
		bpy.context.scene.render.resolution_x=width
		bpy.context.scene.render.resolution_y=height
		bpy.context.scene.render.resolution_percentage=scale

	def setup_lighting(self):

		self.scene_lit=util_helper.scene_has_light()

		if bpy.context.scene.render.engine==self.engine_name_cycles:
			if self.scene_lit==False:
				self.scene_lit=cycles_helper.check_cycles_emission_material()

				if self.scene_lit==True:
					theDollyHelper = camera_dolly_helper.camera_dolly_helper()

					# force time rescale for all auto lights
					autopanstep=theDollyHelper.setup_auto_lights(0)
					theDollyHelper.adjust_lights_for_camera(autopanstep,auto_camera_pan.Cam_Pan_Helper.scenecount)
			
			if self.autopanstep>0:
				theWorldHelper = cycles_world_helper.World_Helper()
				#theWorldHelper.link_random_cycles_hdri()
				theWorldHelper.set_black_world()



		elif bpy.context.scene.render.engine==self.engine_name_lux:
			
			if self.autopanstep>0:
				util_lux.set_color_world((0,0,0))
			#util_lux.set_lux_sky_world()
			#util_lux.link_random_lux_hdri()

			#self.scene_lit=True

		if self.scene_lit==False:
			#auto_camera_pan 	= imp.load_source('auto_camera_pan','/home/blender/scripts/auto_camera_pan.py')
			print("Scene not lit - no lights (autopanstep: %d)"%self.autopanstep)

			# Force always setup auto lights (this will break anim renders but for debugging)
			if self.autopanstep>0:
				theDollyHelper = camera_dolly_helper.camera_dolly_helper()
				
				theDollyHelper.setup_auto_lights(self.autopanstep)
				theDollyHelper.adjust_lights_for_camera(self.autopanstep,self.thePanHelper.scenecount)

				theEnvironment_helper = environment_helper.Environment_Helper()

				theEnvironment_helper.assign_sequenced_environment()
				
				#util_helper.add_sun_light()
			else:

				#typically animation sequence 

				if bpy.context.scene.render.engine==self.engine_name_cycles:

					theWorldHelper = cycles_world_helper.World_Helper()

					worldfile = theWorldHelper.get_world_file()

					# Add an world background
					if worldfile==None:
						world_index = self.getSequenceFromName(util_helper.get_blendfile_without_extension(),len(theWorldHelper.worldlist))
						worldfile = theWorldHelper.worldlist[world_index]
						theWorldHelper.link_world_file(worldfile)
						self.scene_lit=True

				# and a matching sun light
				util_helper.add_sun_light()

			self.scene_lit=True
		else:
			print("Scene already lit - not adding lights")


	def get_samples(self):
		if bpy.context.scene.render.engine==self.engine_name_cycles:
			return cycles_helper.get_cycles_samples()

		return 0



	def setup_render_settings(self):

		self.renderer_name=bpy.context.scene.render.engine.lower()

		#self.create_auto_save_nodes()

		#bpy.context.scene.render.image_settings.file_format="PNG"
		bpy.context.scene.render.use_compositing=True

		if bpy.context.scene.render.engine==self.engine_name_cycles:

			#self.link_random_world()

			cycles_helper.setup_cycles_settings()
	#	elif bpy.context.scene.render.engine=="cyclesgpu":

			#self.link_random_world()

#			self.renderer_name = util_cycles.setup_cyclesgpu_settings()

		elif bpy.context.scene.render.engine==self.engine_name_lux:
			
			#util_lux.import_all_materials_from_filelist()
			#util_lux.update_material_slots()

			util_lux.setup_lux_settings()

			#if self.scene_lit==False:
			#	self.scene_lit = util_lux.lux_scene_is_lit(bpy.context.scene)

			
			#self.scene_lit=True
			#if self.scene_lit==False:
			#	print("no ligh")
			#util_helper.add_sun_light()
			#self.scene_lit=True
				#self.link_random_lux_hdri()
				
			#bpy.ops.render.render(animation=False, write_still=False, layer="", scene="")

		#renderer_name = target_renderer

		self.setup_common_settings()

		if self.use_stamp==True:
			self.setup_stamp()
		else:
			bpy.context.scene.render.use_stamp=False
				
		#self.image_file_extension = "PNG"

		self.temp_dir = os.environ.get("TEMP")

		bpy.context.scene.render.image_settings.file_format=self.file_format

		bpy.context.scene.render.image_settings.exr_codec = 'DWAA'
		bpy.context.scene.render.image_settings.color_depth = '32'



		if self.temp_dir!=None:
			bpy.context.scene.render.filepath=self.temp_dir


	def create_auto_save_nodes_DISABLED(self):
		scene = bpy.context.scene

		frameIndex=bpy.context.scene.frame_current

		# make sure we have node tree
		if scene.node_tree==None:
			scene.use_nodes=True

		if scene.node_tree:
			nodes = scene.node_tree.nodes
			auto_save_output_label="auto_save"

			# remove previously auto created denoise nodes to prevent duplicates
			for node in nodes:
				if node.label==auto_save_output_label:
					nodes.remove(node)

			render_layer_node = nodes.new("CompositorNodeRLayers")
			render_layer_node.location=(0,0)
			render_layer_node.label=auto_save_output_label

			output_file_node = nodes.new("CompositorNodeOutputFile")
			output_file_node.location=(600,0)
			output_file_node.inputs[0].name="filename"
			output_file_node.base_path = self.render_output_path
			output_file_node.label=auto_save_output_label

			denoise_node = nodes.new("CompositorNodeDenoise")
			denoise_node.location=(300,-300)


			bpy.context.scene.render.use_file_extension=True

			output_filename=util_helper.get_blendfile_without_extension()
			
			slot_count=0

			doRaw=False
			doDenoise=True

			if doDenoise==True:
				scene.node_tree.links.new(render_layer_node.outputs['Image'],denoise_node.inputs["Image"])

				output_file_node.file_slots[slot_count].path="%s.%s.dn.####"%(output_filename,self.renderer_name)
				
				output_file_node.file_slots[slot_count].use_node_format=False
				output_file_node.file_slots[slot_count].format.file_format=self.file_format=self.image_file_extension
				scene.node_tree.links.new(denoise_node.outputs[0],output_file_node.inputs[slot_count])
				slot_count+=1
			
			if doRaw==True:
				if slot_count==1:
						output_file_node.file_slots.new("dn")

				output_file_node.file_slots[slot_count].path="%s.%s.####"%(output_filename,self.renderer_name)
				output_file_node.file_slots[slot_count].use_node_format=False
				output_file_node.file_slots[slot_count].format.file_format=self.file_format=self.image_file_extension
				scene.node_tree.links.new(render_layer_node.outputs['Image'],output_file_node.inputs[slot_count])				
				slot_count+=1

			# update composite node
			for node in nodes:
				if node.type=="COMPOSITE":
					scene.node_tree.links.new(denoise_node.outputs[0],node.inputs[0])
					node.location=(600,-300)

	last_frame_time=0
			

	def do_render(self,frameIndex):

		bpy.context.scene.frame_set(frameIndex)

		image_output_filename = util_helper.get_output_filename(util_helper.get_blendfile_without_extension(),frameIndex,self.renderer_name,self.image_file_extension)

		self.last_frame_time=0
		render_start = time.time()
		sys.stdout.flush()

		try:
			render_result = bpy.ops.render.render(animation=False, write_still=False, layer="", scene="")
		except Exception as e:
				print("Render Failed: d%s"%e)
				return False

		self.last_frame_time = time.time() - render_start

		if 'FINISHED' in render_result:

			if self.renderer_name=="luxcore":
				util_lux.enable_lux_denoise()

			full_output_image_path=self.render_output_path + image_output_filename

			bpy.data.images['Render Result'].save_render(filepath=full_output_image_path)

			print("Saved to: " + full_output_image_path)
		else:
			return False

		return True

	def is_inside_scene(self):
		inside_marker=util_helper.find_object_by_name(Rend_Helper.inside_scene_name)

		if inside_marker==None:
			return False
		else:
			return True


	def remove_scene(self):
		#util_helper.remove_group_by_name(self.object_scene_name)
		util_helper.remove_object_by_name(self.object_scene_name)

	def get_random_scene_file(self):

		if self.is_inside_scene()==True:
			print("Inside Scene - Skipping add random scene")
			return None
		else:
			print("not inside scene")

		found_scene=1

		scenelist = list()
		scene_index=0

		scenepath='/home/blender/scenes/macro'

		for infile in glob.glob( os.path.join(scenepath, '*.blend') ):
				scenelist.append(infile)

		scenelist.sort()

		scene_index = self.getSequenceFromName(util_helper.get_blendfile_without_extension(),len(scenelist))

		print(" index [" + str(scene_index) + "/" + str(len(scenelist)) + "] = " + scenelist[scene_index])

		return str(scenelist[scene_index])

	def link_scene_file(self,scenefile):

		if scenefile is not None:
			# TODO - Not always Link
			nob = bpy.ops.wm.link(directory=scenefile + '/Collection/',files=[{'name': 'object_scene'}],link=True)

			#print("Nob: "+str(nob))
			bpy.context.scene.objects['object_scene'].location=[0,0,0]
			#print(bpy.context.scene.objects['object_scene'])

			self.set_scene_file(scenefile)

	def set_scene_file(self,scenefile):
		bpy.context.scene["scenefile"]=scenefile

	def get_scene_file(self):
		if "scenefile" in bpy.context.scene:
			return bpy.context.scene["scenefile"]
		else:
			return None


	def setup_stamp(self):
		bpy.context.scene.render.use_stamp=False
		bpy.context.scene.render.stamp_font_size=9
		bpy.context.scene.render.use_stamp_time=False
		bpy.context.scene.render.use_stamp_date=True
		bpy.context.scene.render.use_stamp_frame=False
		bpy.context.scene.render.use_stamp_scene=False
		bpy.context.scene.render.use_stamp_camera=True
		bpy.context.scene.render.use_stamp_filename=False
		bpy.context.scene.render.use_stamp_lens=False
		bpy.context.scene.render.use_stamp_render_time=True
		bpy.context.scene.render.use_stamp_note=True
		bpy.context.scene.render.stamp_background[0]=0.0
		bpy.context.scene.render.stamp_background[1]=0.0
		bpy.context.scene.render.stamp_background[2]=0.0
		bpy.context.scene.render.stamp_background[3]=0.8
		bpy.context.scene.render.stamp_note_text=self.renderer_name

	def getSequenceFromName(self,filename,maxVal):
		hashVal = util_helper.stringToHash(filename)
		return hashVal % maxVal
