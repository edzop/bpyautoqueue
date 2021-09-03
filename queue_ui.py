bl_info = {
	"name": "Queue_Helper",
	"author": "Ed Kraus",
	"version": (1, 3, 2),
	"blender": (2, 93, 0),
	"location": "3D View > Queue",
	"description": "Queue Helper",
	"warning": "",
	"wiki_url": "https://edzop.github.io/bpyautoqueue",
	"tracker_url": "",
	"category": "User"}

import bpy

from bpy.props import CollectionProperty
from bpy_extras.io_utils import ImportHelper

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

from . import render_db
from . import bake_db



class queue_helper_properties(PropertyGroup):

   
	my_render_modes: EnumProperty(
		name="Dropdown:",
		description="Render Modes",
		items=[ ('pananim', "pananim", ""),
				('pankey', "pankey", ""),
				('anim', "anim", ""),
				('images', "images", ""),
			   ]
		)


	resolution_options=[ 
				('2560x1440', '2560x1440', ""),
				('1920x1080', "1920x1080", ""),
				('960x540', "960x540", ""),
				('480x270', "480x270", ""),

			   ]


	my_resolutions: EnumProperty(
		items=resolution_options,
		description="Resolutions....",
		name="Resolution:",
		default="1920x1080"
	)

def check_file_saved(operator):
		filename = bpy.context.blend_data.filepath

		if len(filename)<1:
			operator.report({'ERROR'}, "need to save file first")
			return None

		return filename


class QueueSingleFrameOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_single_frame_operator"
	bl_label = "Queue Frame"

	def execute(self, context):
	
		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}

		theDB = render_db.render_db()

		current_frame = [ bpy.context.scene.frame_current ]

		scene = context.scene
		my_queue_tool = scene.my_queue_tool

		resX,resY=my_queue_tool.my_resolutions.split("x")
		theDB.outputX=resX
		theDB.outputY=resY

		rendermode=my_queue_tool.my_render_modes

		theDB.configure_anim_mode(rendermode)

		print("Filename: %s Frame: %d Resolution(%s %s) Mode: %s"%(
			filename,
			current_frame[0],
			resX,resY,
			rendermode))

		theDB.IgnoreHashVal=True

		theDB.insert_or_update_blend_file(filename,current_frame)

		return {'FINISHED'}


# total_frames=bpy.context.scene.frame_end
# bpy.context.scene.frame_start

class PrintQueueOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_print_queue"
	bl_label = "PrintQueue"

	def execute(self, context):
		
		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}

		theDB = render_db.render_db()
		theBakeDB = bake_db.bake_db()
		
		print("Print queue Filename: %s"%filename)

		theDB.do_printDB(filename)

		theBakeDB.do_printDB(filename)
		theBakeDB.do_print_results(filename)

		return {'FINISHED'}

class ClearFileFromQueueOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_clear_file"
	bl_label = "UnQueueFile"

	def execute(self, context):

		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		theDB = render_db.render_db()
		theDB.clear_file_from_queue(filename)

		theBakeDB = bake_db.bake_db()
		theBakeDB.clear_file_from_queue(filename)

		print("Clear Queue Filename: %s"%filename)

		return {'FINISHED'}


class ReQueueBakeOperator(bpy.types.Operator):
	"""Requeue file for baking AND rendering if it exists in queue"""
	bl_idname = "wm.render_requeue_bake_operator"
	bl_label = "ReQueue Bake"
	

	def execute(self, context):

		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		theBakeDB = bake_db.bake_db()
		theDB = render_db.render_db()

		print("Requeue Bake Filename: %s"%filename)

		# 0 for all frames
		theDB.update_jobs_mark_file_queued(filename,0)

		theBakeDB.update_jobs_mark_file_queued(filename)

		return {'FINISHED'}


class ReQueueFileOperator(bpy.types.Operator):
	"""Requeue file for rendering if it exists in render queue"""
	bl_idname = "wm.render_requeue_file_operator"
	bl_label = "ReQueue Rend"


	def execute(self, context):

		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}

		theDB = render_db.render_db()
	
		scene = context.scene

		print("Requeue Filename: %s"%filename)

		# 0 for all frames
		theDB.update_jobs_mark_file_queued(filename,0)

		return {'FINISHED'}


class ResizeFileOperator(bpy.types.Operator):
	bl_idname = "wm.resize_file_operator"
	bl_label = "ReSize File"

	def execute(self, context):

		filename=check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		theDB = render_db.render_db()

		scene = context.scene
		my_queue_tool = scene.my_queue_tool

		resX,resY=my_queue_tool.my_resolutions.split("x")
		theDB.outputX=resX
		theDB.outputY=resY
		theDB.change_resolution(filename)

		print("Resize file: %s (%sx%s)"%(filename,resX,resY))

		# 0 for all frames
		#theDB.update_jobs_mark_file_queued(filename,0)

		return {'FINISHED'}


class QueueHelperPanel(Panel):
	bl_idname="PANEL_PT_queueHelperPanel"
	bl_label = "Queue_Helper"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Queue"
	bl_context = "objectmode"   


#	bl_region_type = "TOOL_PROPS"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout

		row = layout.row()

		scene = context.scene
		my_queue_tool = scene.my_queue_tool

		layout.operator(ReQueueFileOperator.bl_idname)
		layout.operator(QueueSingleFrameOperator.bl_idname)
		layout.operator(PrintQueueOperator.bl_idname)
		layout.operator(ClearFileFromQueueOperator.bl_idname)
		layout.prop( my_queue_tool, "my_resolutions", text="Resolution") 
		layout.operator(ResizeFileOperator.bl_idname)
		layout.operator(ReQueueBakeOperator.bl_idname)

		layout.prop( my_queue_tool, "my_render_modes", text="Render Mode") 
		
