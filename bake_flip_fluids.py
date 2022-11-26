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


def get_domain_disk_cache_directory():
	domain_obj=get_flip_domain_object()

	if domain_obj is not None:
		return domain_obj.flip_fluid.domain.cache.cache_directory
	
	return None

def get_resolution(): 

	domain_obj=get_flip_domain_object()

	if domain_obj is not None:
		domain_obj.flip_fluid.domain.simulation.resolution = 33

	return 0


def convert_to_flip():
	
	#bpy.ops.flip_fluid_operators.reset_bake()

	for obj in bpy.data.objects:
		if obj.type=="MESH":

			
			for modifier in obj.modifiers:
				if modifier.type == 'FLUID':

					print("Found fluid simulation on object: %s (%s) - adding flip"%(obj.name,modifier.fluid_type))

					bpy.context.view_layer.objects.active=obj
					obj.select_set(True)

					bpy.ops.flip_fluid_operators.flip_fluid_add()

					if modifier.fluid_type=='DOMAIN':
						print("%s: Setting domain"%obj.name)

						bpy.context.scene.render.use_persistent_data=False
						obj.flip_fluid.object_type="TYPE_DOMAIN"

						cache_dir="flip"
						full_cache_path = "/home/blender/cache/%s/%s/"%(cache_dir,util_helper.get_blendfile_without_extension())
		
						util_helper.ensure_dir(full_cache_path);	
						print("Cache Path: " + full_cache_path)
						obj.flip_fluid.domain.cache.cache_directory = full_cache_path
						
						obj.flip_fluid.domain.materials.surface_material = 'FF Water (ocean 2)'
						obj.flip_fluid.domain.materials.whitewater_foam_material = 'FF Foam'
						obj.flip_fluid.domain.materials.whitewater_bubble_material = 'FF Bubble'
						obj.flip_fluid.domain.materials.whitewater_spray_material = 'FF Spray'
						obj.flip_fluid.domain.render.viewport_display = 'DISPLAY_PREVIEW'
						
						obj.flip_fluid.domain.simulation.auto_preview_resolution = False
						obj.flip_fluid.domain.simulation.preview_resolution = 32
						

					if modifier.fluid_type=='EFFECTOR':
						if modifier.effector_settings.effector_type=='COLLISION':
							obj.flip_fluid.object_type="TYPE_OBSTACLE"
	
					if modifier.fluid_type=="FLOW":
						obj.flip_fluid.object_type="TYPE_DOMAIN"
						
					if modifier.fluid_type=="FLOW":
						if modifier.flow_settings.flow_behavior=='INFLOW':
							obj.flip_fluid.object_type="TYPE_INFLOW"

						if modifier.flow_settings.flow_behavior=='OUTFLOW':
							obj.flip_fluid.object_type="TYPE_OUTFLOW"
						
						if modifier.flow_settings.flow_behavior=='GEOMETRY':
							obj.flip_fluid.object_type="TYPE_FLUID"
