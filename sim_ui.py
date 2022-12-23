import bpy

from . import bake_fluids


from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   EnumProperty,
					   PointerProperty,
					   )

from bpy.types import (Panel,
					   Operator,
					   PropertyGroup,
					   )

from . import bake_db

from . import material_helper
from . import util_helper

from . import bake_flip_fluids


texlibpath_materials="/home/blender/texlib.blend/Material"



class FluidAssignInflowOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_assign_inflow"
	bl_label = "Assign Inflow"

	@classmethod
	def poll(cls, context):
		return bpy.context.active_object != None
		
	def execute(self, context):
		sel = bpy.context.selected_objects
		for ob in sel:
			material_helper.assign_linked_material(ob,"fluid.inflow",texlibpath_materials)
		return{'FINISHED'}

class FluidAssignOutflowOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_assign_outflow"
	bl_label = "Assign Outflow"

	@classmethod
	def poll(cls, context):
		return bpy.context.active_object != None

	def execute(self, context):
		sel = bpy.context.selected_objects
		for ob in sel:
		#ob = bpy.context.active_object
			material_helper.assign_linked_material(ob,"fluid.outflow",texlibpath_materials)

		return{'FINISHED'}

class FluidAssignObstacleOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_assign_obstacle"
	bl_label = "Assign Obstacle"

	@classmethod
	def poll(cls, context):
		return bpy.context.active_object != None

	def execute(self, context):

		sel = bpy.context.selected_objects

		for ob in sel:
			material_helper.assign_linked_material(ob,"fluid.obstacle",texlibpath_materials)
		
		return{'FINISHED'}

class FluidAssignBevelOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_assign_bevel"
	bl_label = "Assign Bevel"

	@classmethod
	def poll(cls, context):
		return bpy.context.active_object != None

	def execute(self, context):
		sel = bpy.context.selected_objects
		for ob in sel:
			bevel = ob.modifiers.new(type="BEVEL", name="bevel")
			bevel.segments=3
			
		return{'FINISHED'}


class FluidAssignWireSkinOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_assign_wireskin"
	bl_label = "Assign Wireskin"

	@classmethod
	def poll(cls, context):
		return bpy.context.active_object != None

	def execute(self, context):
		ob = bpy.context.active_object

		# Assign to last slot (-1)
		material_helper.assign_linked_material(ob,"24kgold",texlibpath_materials,slot=-1)

		wireframe = ob.modifiers.new(type="WIREFRAME", name="wireframe")
		wireframe.use_replace = False
		wireframe.material_offset = 1
		wireframe.thickness = 0.01

		return{'FINISHED'}


class ReQueueBakeOperator(bpy.types.Operator):
	"""Requeue file for baking AND rendering if it exists in queue"""
	bl_idname = "wm.render_requeue_bake_operator"
	bl_label = "ReQueue Bake"
	

	def execute(self, context):

		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		theBakeDB = bake_db.bake_db()
		theDB = render_db.render_db()

		print("Requeue Bake Filename: %s"%filename)

		# 0 for all frames
		theDB.update_jobs_mark_file_queued(filename,0)

		theBakeDB.update_jobs_mark_file_queued(filename)

		return {'FINISHED'}



class SetupFlipSimOperator(bpy.types.Operator):
	"""Setup flip fluids and particles"""
	bl_idname = "wm.setupflipsim"
	bl_label = "Setup FlipSim"


	def execute(self, context):

		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		print("Setup Flip Sim...")

		bake_flip_fluids.setup_flip()

		return {'FINISHED'}



class SetupSimOperator(bpy.types.Operator):
	"""Setup fluids and particles"""
	bl_idname = "wm.setupsim"
	bl_label = "Setup Sim"


	def execute(self, context):

		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		print("Setup Sim...")

		bake_fluids.setup_draft()

		return {'FINISHED'}




class SimHelperPanel(Panel):
	bl_idname="PANEL_PT_simHelperPanel"
	bl_label = "Sim Helper"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "bpyAutoQueue"
	bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout

		row = layout.row()

		scene = context.scene
		my_queue_tool = scene.my_queue_tool


		layout.operator(FluidAssignInflowOperator.bl_idname)
		layout.operator(FluidAssignOutflowOperator.bl_idname)
		layout.operator(FluidAssignObstacleOperator.bl_idname)
		layout.operator(FluidAssignWireSkinOperator.bl_idname)
		layout.operator(FluidAssignBevelOperator.bl_idname)

		layout.operator(ReQueueBakeOperator.bl_idname)

		row = layout.row()
		layout.operator(SetupSimOperator.bl_idname)
		layout.operator(SetupFlipSimOperator.bl_idname)

