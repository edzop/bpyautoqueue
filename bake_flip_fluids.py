import bpy

from bpyautoqueue import util_helper


def bake_flip_fluids():
	#bpy.ops.flip_fluid_operators.export_fluid_simulation()
	bpy.ops.flip_fluid_operators.bake_fluid_simulation_cmd()

def get_flip_domain_object():
	for obj in bpy.data.objects:
		if obj.type=="MESH":
			if obj.flip_fluid.object_type=="TYPE_DOMAIN":
				return obj
	
	return None


def check_flip_fluids(obj):

	flip_fluids_exists=False

	for obj in bpy.data.objects:

		if hasattr(obj, "flip_fluid"):
			fluid_type = obj.flip_fluid.object_type
			if fluid_type != 'NONE':
				print(f"FLIP Fluid exists for '{obj.name}'. Type: {fluid_type}")
				flip_fluids_exists=True

	return flip_fluids_exists



def get_domain_disk_cache_directory():
	domain_obj=get_flip_domain_object()

	if domain_obj is not None:
		return domain_obj.flip_fluid.domain.cache.cache_directory
	
	return None

def get_resolution(): 

	domain_obj=get_flip_domain_object()

	if domain_obj is not None:
		return domain_obj.flip_fluid.domain.simulation.resolution

	return 0

def setup_flip():

	for obj in bpy.data.objects:

		if obj.flip_fluid is not None:

			flip=obj.flip_fluid

			if flip.object_type=="TYPE_DOMAIN":

				cache_dir="flip"
				full_cache_path = "/home/blender/cache/%s/%s/"%(cache_dir,util_helper.get_blendfile_without_extension())

				util_helper.ensure_dir(full_cache_path);	
				print("Cache Path: " + full_cache_path)
				flip.domain.cache.cache_directory = full_cache_path

					  
				flip.domain.whitewater.enable_whitewater_simulation = True

				flip.domain.render.viewport_display = 'DISPLAY_PREVIEW'
				
				flip.domain.simulation.auto_preview_resolution = False
				flip.domain.simulation.preview_resolution = 32

				flip.domain.simulation.resolution=64


				#obj.flip_fluid.domain.materials.surface_material = 'FF Water (ocean 2)'
				flip.domain.materials.whitewater_foam_material = 'FF Foam'
				flip.domain.materials.whitewater_bubble_material = 'FF Bubble'
				flip.domain.materials.whitewater_spray_material = 'FF Spray'
				

def convert_to_flip():
	
	#bpy.ops.flip_fluid_operators.reset_bake()
 
	found_fluid=False

	for obj in bpy.data.objects:
		if obj.type=="MESH":

			
			for modifier in obj.modifiers:
				if modifier.type == 'FLUID':
		
					found_fluid=True

					print("Found fluid simulation on object: %s (%s) - adding flip"%(obj.name,modifier.fluid_type))

					bpy.context.view_layer.objects.active=obj
					obj.select_set(True)

					bpy.ops.flip_fluid_operators.flip_fluid_add()

					if modifier.fluid_type=='DOMAIN':
						print("%s: Setting domain"%obj.name)

						bpy.context.scene.render.use_persistent_data=False
						obj.flip_fluid.object_type="TYPE_DOMAIN"
	  
						bpy.ops.flip_fluid_operators.reset_bake()


					if modifier.fluid_type=='EFFECTOR':
						if modifier.effector_settings.effector_type=='COLLISION':
							obj.flip_fluid.object_type="TYPE_OBSTACLE"
						
					if modifier.fluid_type=="FLOW":
						if modifier.flow_settings.flow_behavior=='INFLOW':
							obj.flip_fluid.object_type="TYPE_INFLOW"

						if modifier.flow_settings.flow_behavior=='OUTFLOW':
							obj.flip_fluid.object_type="TYPE_OUTFLOW"
						
						if modifier.flow_settings.flow_behavior=='GEOMETRY':
							obj.flip_fluid.object_type="TYPE_FLUID"
	   



	if found_fluid:
		setup_flip()

		util_helper.do_save()
