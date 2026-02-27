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
import os

from bpy.props import CollectionProperty


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
from . import util_helper

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
				('3840x2160', '3840x2160', ""),
				('3840x1634', '3840x1634', ""),
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



class QueueAllFramesOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_all_frames_operator"
	bl_label = "Queue All Frames"

	def execute(self, context):
	
		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}
		
		print("Queue All Frames")

		theDB = render_db.render_db()

		frame_start=bpy.context.scene.frame_start
		frame_end=bpy.context.scene.frame_end

		scene = context.scene
		my_queue_tool = scene.my_queue_tool

		resX,resY=my_queue_tool.my_resolutions.split("x")
		theDB.outputX=resX
		theDB.outputY=resY

		rendermode=my_queue_tool.my_render_modes

		theDB.configure_anim_mode(rendermode)

		frames_to_add=[]

		for current_frame in range(frame_start,frame_end+1):
			frames_to_add.append(current_frame)

		theDB.IgnoreHashVal=True

		current_scene_index = util_helper.get_current_scene_index()

		theDB.insert_or_update_blend_file(filename,current_scene_index,frames_to_add,1)

		print("Filename: %s Frames: (%d-%d) Resolution(%s %s) Mode: %s"%(
				filename,
				frame_start,frame_end,
				resX,resY,
				rendermode))

		return {'FINISHED'}


class QueueSingleFrameOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_single_frame_operator"
	bl_label = "Queue Frame"

	def execute(self, context):
	
		filename=util_helper.check_file_saved(self)

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

		theDB.insert_or_update_blend_file(filename,current_frame,1)

		return {'FINISHED'}


# total_frames=bpy.context.scene.frame_end
# bpy.context.scene.frame_start

class PrintQueueOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_print_queue"
	bl_label = "PrintQueue"

	def execute(self, context):
		
		filename=util_helper.check_file_saved(self)

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

		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}


		theDB = render_db.render_db()
		theDB.clear_file_from_queue(filename)

		theBakeDB = bake_db.bake_db()
		theBakeDB.clear_file_from_queue(filename)

		print("Clear Queue Filename: %s"%filename)

		return {'FINISHED'}



class ReQueueFileOperator(bpy.types.Operator):
	"""Requeue file for rendering if it exists in render queue"""
	bl_idname = "wm.render_requeue_file_operator"
	bl_label = "ReQueue Rend"


	def execute(self, context):

		filename=util_helper.check_file_saved(self)

		if filename==None:
			return {'CANCELLED'}

		theDB = render_db.render_db()
	
		scene = context.scene
  
		basename = os.path.basename(filename)

		print("Requeue Filename: %s"%basename)

		current_scene_index = util_helper.get_current_scene_index()

		frames = 0

		# 0 for all frames
		theDB.update_jobs_mark_file_queued(basename,current_scene_index,frames)

		return {'FINISHED'}



class ResizeFileOperator(bpy.types.Operator):
	bl_idname = "wm.resize_file_operator"
	bl_label = "ReSize File"

	def execute(self, context):

		filename=util_helper.check_file_saved(self)

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

		return {'FINISHED'}

class QueueHelperPanel(Panel):
	bl_idname="PANEL_PT_queueHelperPanel"
	bl_label = "Queue"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "bpyAutoQueue"
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
		layout.operator(QueueAllFramesOperator.bl_idname)
		layout.operator(PrintQueueOperator.bl_idname)
		layout.operator(ClearFileFromQueueOperator.bl_idname)
		layout.prop( my_queue_tool, "my_resolutions", text="Resolution") 
		layout.operator(ResizeFileOperator.bl_idname)

		layout.prop( my_queue_tool, "my_render_modes", text="Render Mode") 
		
