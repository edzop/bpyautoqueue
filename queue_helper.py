bl_info = {
	"name": "Queue_Helper",
	"author": "zuka",
	"version": (1, 3, 1),
	"blender": (2, 80, 0),
	#"location": "User > Queue_Helper",
	"location": "3D View > Queue",
	"description": "Queue Helper",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "User"}

import bpy
import imp
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

render_db 	= imp.load_source('render_db','/home/blender/scripts/queue/render_db.py')




class PG_MyProperties(PropertyGroup):

   
	my_render_modes: EnumProperty(
		name="Dropdown:",
		description="Render Modes",
		items=[ ('pananim', "pananim", ""),
				('pankey', "pankey", ""),
				('anim', "anim", ""),
				('images', "images", ""),
			   ]
		)


	resolution_options=[ ('1920x1080', "1920x1080", ""),
				('960x540', "960x540", ""),
				('480x270', "480x270", ""),
			   ]



	my_resolutions: EnumProperty(
		items=resolution_options,
		description="Resolutions....",
		name="Resolution:",
		default="1920x1080"
	)



class QueueSingleFrameOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_single_frame_operator"
	bl_label = "Queue Frame"

	def execute(self, context):

		theDB = render_db.render_db()
		theDB.openDB()
		theDB.create_tables()

		filename = bpy.context.blend_data.filepath
		current_frame = bpy.context.scene.frame_current

		scene = context.scene
		my_queue_tool = scene.my_queue_tool

		resX,resY=my_queue_tool.my_resolutions.split("x")
		theDB.outputX=resX
		theDB.outputY=resY

		rendermode=my_queue_tool.my_render_modes

		theDB.configure_anim_mode(rendermode)

		print("Filename: %s Frame %d (%s %s) %s"%(filename,current_frame,resX,resY,rendermode))

		theDB.IgnoreHashVal=True

		theDB.insert_or_update_blend_file(filename,current_frame)

		return {'FINISHED'}


# total_frames=bpy.context.scene.frame_end
# bpy.context.scene.frame_start

class PrintQueueOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_print_queue"
	bl_label = "PrintQueue"

	def execute(self, context):

		theDB = render_db.render_db()
		theDB.openDB()
		theDB.create_tables()

		filename = bpy.context.blend_data.filepath

		print("Print queue Filename: %s"%filename)

		theDB.do_printDB(filename)

		return {'FINISHED'}

class ClearFileFromQueueOperator(bpy.types.Operator):
	bl_idname = "wm.render_queue_clear_file"
	bl_label = "UnQueueFile"

	def execute(self, context):

		theDB = render_db.render_db()
		theDB.openDB()
		theDB.create_tables()

		filename = bpy.context.blend_data.filepath

		theDB.clear_file_from_queue(filename)

		print("Clear Queue Filename: %s"%filename)

		return {'FINISHED'}


class ReQueueFileOperator(bpy.types.Operator):
	bl_idname = "wm.render_requeue_file_operator"
	bl_label = "ReQueue File"

	def execute(self, context):

		theDB = render_db.render_db()
		theDB.openDB()
		theDB.create_tables()

		filename = bpy.context.blend_data.filepath

		scene = context.scene
		#my_queue_tool = scene.my_queue_tool

		#print("enum state:", mytool.my_resolutions)

		print("Requeue Filename: %s"%filename)

		# 0 for all frames
		theDB.update_jobs_mark_file_queued(filename,0)

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

		layout.prop( my_queue_tool, "my_render_modes", text="Render Mode") 
		

		#layout.prop(scene, 'QueueSettings.my_resolutions')

		

		#layout.operator_menu_enum("QueueSettings.my_resolutions",
		#						  property="resolution",
		#						  text="Render Resolution...",
		#						  )


		#layout.prop(mytool, "my_render_modes", text="") 
		#layout.prop(mytool, "my_resolutions", text="") 

def register():
#	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_queue_tool = PointerProperty(type=PG_MyProperties)
	#print( bpy.types.Scene.my_queue_tool)

def unregister():
#	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.my_tool

#if __name__ == "__main__":
#	register()
