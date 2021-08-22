import bpy
import os
import sys
from sys import exc_info 
import subprocess
import time
from mathutils import Matrix

# =========================================================================================================
from bpyautoqueue import bake_db
from bpyautoqueue import util_helper

from bpyautoqueue import util_helper
from bpyautoqueue import material_helper

import bmesh

#blend_file = os.path.basename(bpy.context.blend_data.filepath)


argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

bake_op=""
jobID=0

if len(argv)>1:
	jobID=argv[0]
	bake_op=int(argv[1])

def do_bake(obj,modifier):

	#bpy.ops.fluid.free_all()

	#modifier.show_viewport = False
	#bpy.context.view_layer.update() 
	

	settings=modifier.domain_settings
	
	bpy.ops.object.select_all(action='DESELECT')
	
	bpy.context.view_layer.objects.active = obj
	obj.select_set(state=True)

	bpy.context.scene.frame_current=1
	
	status_text = ""
	
	status_text=" - Resolution: %03d, end_frame: %04d, subframes: %02d, timesteps: %02d %02d" %(
		settings.resolution_max,
		settings.cache_frame_end,
		0,
		settings.timesteps_min,
		settings.timesteps_max)
		
	print(status_text)

	bake_time=0

	try:
		bake_start = time.time()
		#bpy.ops.fluid.free_all()
		bpy.ops.fluid.bake_all()
		bake_time = time.time() - bake_start
		
		status_text = ' - Bake Time: %s' %(util_helper.secondsToStr(bake_time))
	except Exception as e:
		e = sys.exc_info()[0]
		status_text = "ERROR - %s" %(str(exc_info()))
		#print(status_text)

	theDB = bake_db.bake_db()
	theDB.update_job_set_status(jobID,bake_db.bake_db.code_finished)

	cache_size="-"


	if os.path.isdir(settings.cache_directory):
		cache_size=subprocess.check_output(['du','-sh', settings.cache_directory]).split()[0].decode('utf-8')


	bpy.context.scene.frame_current=settings.cache_frame_end

	# With adaptive domain - the max domain size is usually at end of simulation as it gruws usually
	domain_size="%2.1f,%2.1f,%2.1f"%(obj.dimensions.x,obj.dimensions.y,obj.dimensions.z)

	
	blend_file = os.path.basename(bpy.context.blend_data.filepath)
	theDB.log_result(blend_file,bake_time,settings.cache_frame_end,settings.resolution_max,domain_size,cache_size)

	bpy.context.scene.frame_current=1
	
	#print(status_text)
	
	print(status_text)

	
def bake_all_fluids():
	for obj in bpy.data.objects:
		if obj.type=="MESH":
			for modifier in obj.modifiers:
				if modifier.type == 'FLUID':
					#print("Found fluid simulation on object: %s"%obj.name)
					if modifier.fluid_type == 'DOMAIN':	
						do_bake(obj,modifier)
						#assign_particles()
						#util_helper.do_save()


def disable_all_particles():
	for obj in bpy.data.objects:
		if obj.type=="MESH":
			for modifier in obj.modifiers:
				if modifier.type == 'FLUID':
					if modifier.fluid_type == 'DOMAIN':
						settings=modifier.domain_settings
						if settings.domain_type=="LIQUID":
							settings.use_flip_particles=False
							settings.use_spray_particles = False
							settings.use_foam_particles = False
							settings.use_bubble_particles = False


def update_fluid_objects(fluid_settings):
	#bpy.ops.fluid.free_all()

	for obj in bpy.data.objects:
		if obj.type=="MESH":
			for modifier in obj.modifiers:
				if modifier.type == 'FLUID':

					#print("Found fluid simulation on object: %s"%obj.name)

					if modifier.fluid_type == 'DOMAIN':
						configure_fluid_domain(obj,modifier.domain_settings,fluid_settings)
							
					if modifier.fluid_type=="FLOW":
						modifier.flow_settings.subframes = fluid_settings["flow_subframes"]
						
					if modifier.fluid_type=="EFFECTOR":
						modifier.effector_settings.subframes = fluid_settings["effector_subframes"]

					modifier.show_viewport = True
				
	util_helper.do_save()



def configure_fluid_domain(obj,settings,fluid_settings):
	
	cache_dir="unknown_domain"
	
	if settings.domain_type=="GAS":		
		cache_dir="smoke"
		settings.resolution_max=fluid_settings["gas_resolution"]

		settings.timesteps_max=1
		settings.timesteps_min=1
	
	if settings.domain_type=="LIQUID":

			print("particles on")
			settings.use_flip_particles=True
			settings.use_spray_particles = True
			settings.use_foam_particles = True
			settings.use_bubble_particles = True

			# sometimes we get ghost leftover particles... maybe a bug
			# maybe because some were created with UI some with script... 
			# flush them all out... 
			#delete_liquid_particles() # don't use this - it drops the fluid domain

			#return
			
			settings.simulation_method = 'APIC'

			#settings.use_flip_particles=False
			
			cache_dir="water"
			settings.use_mesh=True		
			settings.resolution_max=fluid_settings["fluid_resolution"]

			settings.use_adaptive_timesteps = True
			settings.timesteps_max=fluid_settings["timesteps_max"]
			settings.timesteps_min=fluid_settings["timesteps_min"]

			settings.sys_particle_maximum = 1000000

			assign_particles()

			material_name="auto_water"

			material_helper.delete_material(material_name)
			mat=material_helper.make_liquid_material(material_name,(0.5,0.9,1.0,1))
			material_helper.assign_material(obj,mat)

	full_cache_path = "/home/blender/cache/%s/%s/"%(cache_dir,util_helper.get_blendfile_without_extension())
		
	util_helper.ensure_dir(full_cache_path);	
	print("Cache Path: " + full_cache_path)
		
	settings.cache_type="ALL"
	settings.cache_directory=full_cache_path
	settings.cache_data_format = 'OPENVDB'

	settings.cache_frame_end=bpy.context.scene.frame_end
	bpy.context.scene.frame_current=1

	#util_helper.do_save()


def assign_particles():

	foam_obj_name="autogen_liquid_foam"
	spray_obj_name="autogen_liquid_spray"
	bubbles_obj_name="autogen_liquid_bubbles"

	util_helper.remove_object_by_name(foam_obj_name,starts_with=True)
	util_helper.remove_object_by_name(spray_obj_name,starts_with=True)
	util_helper.remove_object_by_name(bubbles_obj_name,starts_with=True)

	particle_size=0.12

	foam_obj = add_icosphere(foam_obj_name,particle_size,(0.3,0.6,1,1))
	spray_obj = add_icosphere(spray_obj_name,particle_size,(0.7,0.7,1.0,1))
	bubbles_obj = add_icosphere(bubbles_obj_name,particle_size,(1,1,1,1))

	for p in bpy.data.particles:
		p.display_percentage = 10

		print("assign particles: %s"%p.name)
		if p.name.startswith("Foam"):
			p.render_type = 'OBJECT'
			p.instance_object = foam_obj
			#print("found Foam")
			
		if p.name.startswith("Bubble"):
			p.render_type = 'OBJECT'
			p.instance_object = bubbles_obj
			#print("found Bubble")
			
		if p.name.startswith("Spray"):
			p.render_type = 'OBJECT'
			p.instance_object = spray_obj
			#print("found Spray")


# icosphere for particle system rendering
def add_icosphere(name,size,color):

	
	bm = bmesh.new()
	transform = Matrix.Identity(4)
	
	bmesh.ops.create_icosphere(
    bm,
    subdivisions=1,
    diameter=size,
    matrix=transform,
    calc_uvs=False)


	bmesh.ops.create_icosphere(bm, subdivisions=1, diameter=size,matrix=transform,calc_uvs=False) 
	#, matrix, calc_uvs)

	mesh = bpy.data.meshes.new(name)
	bm.to_mesh(mesh)
	bm.free()

	obj = bpy.data.objects.new(mesh.name, mesh)

	bpy.context.scene.collection.objects.link(obj) 
	
	#bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
	#ob = bpy.context.active_object
	#ob.name=name

	# hide it down below floor place
	obj.location.z=-2

	material_name=name

	material_helper.delete_material(material_name)

	mat=material_helper.make_diffuse_material(material_name,color)

	material_helper.assign_material(obj,mat)

	return obj


def delete_particle_systems():

	for p in bpy.data.particles:
		#print("found particle: %s"%p.name)
		
		if p.name.startswith("Bubble"):
			bpy.data.particles.remove(p)
		elif p.name.startswith("Foam"):
			bpy.data.particles.remove(p)
		elif p.name.startswith("Spray"):
			bpy.data.particles.remove(p)
		elif p.name.startswith("Liquid"):
			bpy.data.particles.remove(p)



def setup_final():

	fluid_settings = {
		"fluid_resolution": 64,
		"gas_resolution": 256,
		"timesteps_min": 8,
		"timesteps_max": 10,
		"flow_subframes": 50,
		"effector_subframes": 50
	}

	update_fluid_objects(fluid_settings)


def setup_draft():
	fluid_settings = {
		"fluid_resolution": 32,
		"gas_resolution": 120,
		"timesteps_min": 1,
		"timesteps_max": 4,
		"flow_subframes": 3,
		"effector_subframes": 3
	}

	update_fluid_objects(fluid_settings)


def clean_all():
	print("clean_all")
	#bpy.ops.fluid.free_all()
	disable_all_particles()
	#delete_particle_systems()
	util_helper.do_save()

if bake_op==bake_db.bake_db.code_bake_op_bake:
	bake_all_fluids()
elif bake_op==bake_db.bake_db.code_bake_op_setup_draft:
	setup_draft()
elif bake_op==bake_db.bake_db.code_bake_op_setup_final:
	setup_final()
elif bake_op==bake_db.bake_db.code_bake_op_clean:
	clean_all()
