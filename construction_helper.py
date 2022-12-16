import bpy

from . import material_helper
from . import util_helper

def make_backdrop():

	backdrop_name="Backdrop"

	ob=util_helper.find_object_by_name(backdrop_name)

	if ob is not None:
		util_helper.remove_object_by_name(backdrop_name)

	bpy.ops.mesh.primitive_plane_add(size=80, enter_editmode=False, location=(0, 0, 0))

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="EDGE")
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.mode_set(mode='OBJECT')

	ob = bpy.context.active_object
	ob.data.edges[3].select=True
	ob.name=backdrop_name

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 40)})

	bpy.ops.mesh.select_all(action='DESELECT')

	bpy.ops.object.mode_set(mode='OBJECT')
	ob.data.edges[3].select=True
	bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.bevel(offset=20, offset_pct=0, segments=10, release_confirm=True)

	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.shade_smooth()

	mat = material_helper.make_metalic_material("backdrop",[.6,.6,.6,1])
	material_helper.assign_material(ob,mat)

	util_helper.move_to_scene_collection(ob)

	return ob