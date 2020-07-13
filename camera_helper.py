bl_info = {
	"name": "Camera_Helper",
	"author": "zuka",
	"version": (1, 3, 0),
	"blender": (2, 80, 0),
	"location": "User > Camera Helper",
	"description": "Camera Helper",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "User"}

import bpy
import imp

from bpy_extras.io_utils import ImportHelper

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


#  bpy.ops.wm.path_open().  bpy.ops.wm.path_open(filepath="C:\\folder with spaces\\")
# dir(bpy.types.UserPreferencesFilePaths)
# bpy.ops.wm.read_history()
# ./config/recent-files.txt


rend_helper 		= imp.load_source('util_helper','/home/blender/scripts/rend_helper.py')
auto_camera_pan 	= imp.load_source('auto_camera_pan','/home/blender/scripts/auto_camera_pan.py')
camera_dolly_helper = imp.load_source('camera_dolly_helper','/home/blender/scripts/camera_dolly_helper.py')
util_helper 		= imp.load_source('util_helper','/home/blender/scripts/util_helper.py')
util_lux 			= imp.load_source('util_lux','/home/blender/scripts/lux/util_lux_helper.py')
util_cycles 		= imp.load_source('util_cycles','/home/blender/scripts/cycles/util_cycles_helper.py')
util_world_helper	= imp.load_source('util_cycles','/home/blender/scripts/cycles/util_world_helper.py')


class camera_helper_properties(PropertyGroup):

	pan_step : IntProperty(
		name = "PanStep",
		description = "Steps between animation pan keyframes",
		default = 1,
		min = 0,
		max = 1000
		)





class SetupRenderSettingsLuxOperator(bpy.types.Operator):
	bl_idname = "wm.scene_setup_render_settings_lux"
	bl_label = "Lux Setup"

	def execute(self, context):

		bpy.context.scene.render.engine=rend_helper.Rend_Helper.engine_name_lux
		theRendHelper = rend_helper.Rend_Helper(False)
		theRendHelper.setup_render_settings()

		del theRendHelper

		return {'FINISHED'}

class SetupRenderSettingsCyclesOperator(bpy.types.Operator):
	bl_idname = "wm.scene_setup_render_settings_cycles"
	bl_label = "Cycles Setup "

	def execute(self, context):

		bpy.context.scene.render.engine=rend_helper.Rend_Helper.engine_name_cycles
		theRendHelper = rend_helper.Rend_Helper(False)
		theRendHelper.setup_render_settings()

		del theRendHelper

		return {'FINISHED'}


class SetupRenderCameraDollyOperator(bpy.types.Operator):
	bl_idname = "wm.scene_setup_render_camera_dolly"
	bl_label = "Setup Camera Dolly"

	def execute(self, context):

		thePanHelper = auto_camera_pan.Cam_Pan_Helper(None)
		theDolly = camera_dolly_helper.camera_dolly_helper(thePanHelper)
		autoPanStep=1
		theDolly.setup_auto_lights(autoPanStep)
		theDolly.adjust_lights_for_camera(autoPanStep)
		
		return {'FINISHED'}


class LinkRandomLuxHdriOperator(bpy.types.Operator):
	bl_idname = "wm.scene_link_random_lux_hdri"
	bl_label = "Random Lux HDRI"

	def execute(self, context):

		#theRendHelper = rend_helper.Rend_Helper(False)
		util_lux.link_random_lux_hdri()

		#del theRendHelper

		return {'FINISHED'}



class LoadSceneOperator(bpy.types.Operator):
	bl_idname = "wm.scene_load_background"
	bl_label = "Load Background"

	def execute(self, context):

		theRendHelper = rend_helper.Rend_Helper(False)
		scenefile = theRendHelper.get_scene_file()

		del theRendHelper

		bpy.ops.wm.path_open(filepath=scenefile)

		return {'FINISHED'}



class ClearSceneHelperOperator(bpy.types.Operator):
	bl_idname = "wm.scene_helper_clear"
	bl_label = "Clear Background"

	def execute(self, context):

		theRendHelper = rend_helper.Rend_Helper(False)
		theRendHelper.remove_scene()

		del theRendHelper



		return {'FINISHED'}


class Operator_Choose_World(bpy.types.Operator, ImportHelper):
	bl_idname = "wm.scene_helper_choose_world"
	bl_label = "Choose World"

    # From ImportHelper. Filter filenames.
	filename_ext = ".blend"
	#filter_glob = bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

	filepath : StringProperty(
        name="File Path",
        description="Path to World file",
        default="",
        maxlen=1024)

	#filepath = bpy.props.StringProperty(name="File Path", maxlen=1024, default="")

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		import bpy, os
		theRendHelper = rend_helper.Rend_Helper(False)

		theWorldHelper = util_world_helper.World_Helper()
		theWorldHelper.remove_world()
		theWorldHelper.link_world_file(self.properties.filepath)

		return{'FINISHED'}

class Operator_Choose_Background(bpy.types.Operator, ImportHelper):
	bl_idname = "wm.scene_helper_choose_background"
	bl_label = "Choose Background"

    # From ImportHelper. Filter filenames.
	filename_ext = ".blend"

	#filter_glob = bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})


	filepath : StringProperty(
        name="File Path",
        description="Path to Background file",
        default="",
        maxlen=1024)

	#filepath = bpy.props.StringProperty(name="File Path", maxlen=1024, default="")

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		import bpy, os
		theRendHelper = rend_helper.Rend_Helper(False)
		theRendHelper.remove_scene()
		theRendHelper.link_scene_file(self.properties.filepath)

		return{'FINISHED'}


class SetupLightingOperator(bpy.types.Operator):

	bl_idname = "wm.scene_helper_set_lighting"
	bl_label = "Setup Lighting"

	def execute(self, context):

		my_camera_tool = context.scene.my_camera_tool

		theRendHelper = rend_helper.Rend_Helper(isolate_output_in_folder=False,autopanstep=my_camera_tool.pan_step)
		theRendHelper.setup_lighting()

		del theRendHelper

		return {'FINISHED'}

	


class SetBackgroundSceneHelperOperator(bpy.types.Operator):
	bl_idname = "wm.scene_helper_set_background"
	bl_label = "Assign Background"

	def execute(self, context):

		theRendHelper = rend_helper.Rend_Helper(False)
		theRendHelper.remove_scene()

		random_scene_file = theRendHelper.get_random_scene_file()

		theRendHelper.link_scene_file(random_scene_file)

		del theRendHelper

		return {'FINISHED'}


class SetupAutoPanOperator(bpy.types.Operator):
	bl_idname = "wm.setup_auto_pan"
	bl_label = "Anim Keyframes"
	bl_description = "DESCRIPTION"

	def execute(self, context):

		thePanHelper = auto_camera_pan.Cam_Pan_Helper(None)

		my_camera_tool = context.scene.my_camera_tool

		print("Auto Pan: %d"%my_camera_tool.pan_step)
		if thePanHelper.validate_settings()==True:
			thePanHelper.setup_auto_pan(my_camera_tool.pan_step)
			theDolly = camera_dolly_helper.camera_dolly_helper(thePanHelper)
			theDolly.adjust_lights_for_camera(my_camera_tool.pan_step)
		else:
			self.report({'INFO'}, "camalign: %s" % thePanHelper.status_message)

		del thePanHelper

		return {'FINISHED'}

class DumpCamDataOperator(bpy.types.Operator):

	bl_idname = "wm.dumpcamoperator"
	bl_label = "dumpCam"
	bl_description = "DESCRIPTION"

	def execute(self, context):

		camTarget=None
		camObject=None

		# first find camTarget
		for obj in bpy.data.objects:
			if obj.type=="CAMERA":
				for constraint in obj.constraints:
					if constraint.type == 'TRACK_TO':
						camTarget=constraint.target
						camObject=obj

		for f in range(bpy.context.scene.frame_start,bpy.context.scene.frame_end+1):
			bpy.context.scene.frame_set(f)
			camLoc = camObject.location
			targetLoc = camTarget.location
			print("[ %d, [%f,%f,%f],[%f,%f,%f] ],"%(
				f,
				camLoc[0],camLoc[1],camLoc[2],
				targetLoc[0],targetLoc[1],targetLoc[2]))

		return {'FINISHED'}



class CamHelperPanel(bpy.types.Panel):
	bl_idname="PANEL_PT_cameraHelperPanel"
	bl_label = "Camera Helper"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'

	bl_category = "Camera"
	bl_context = "objectmode"   

	def draw(self, context):
		layout = self.layout

		scene = context.scene
		
#        row = layout.row()
#        row.label(text="Cam Align:")

#		split = layout.split()
#		col = split.column(align=True)

#        col.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
		layout.operator(Operator_Choose_World.bl_idname)
		layout.operator(Operator_Choose_Background.bl_idname)
		
		layout.operator(SetBackgroundSceneHelperOperator.bl_idname)
		layout.operator(LoadSceneOperator.bl_idname)
		layout.operator(ClearSceneHelperOperator.bl_idname)

		my_camera_tool = scene.my_camera_tool

		layout.prop( my_camera_tool, "pan_step")
		#layout.operator(SetupAutoViewOperator.bl_idname)
		layout.operator(SetupAutoPanOperator.bl_idname)
		

		layout.operator(SetupRenderSettingsLuxOperator.bl_idname)
		layout.operator(LinkRandomLuxHdriOperator.bl_idname)
		layout.operator(SetupRenderSettingsCyclesOperator.bl_idname)

		layout.operator(SetupRenderCameraDollyOperator.bl_idname)

		layout.operator(SetupLightingOperator.bl_idname)

		layout.operator(DumpCamDataOperator.bl_idname)

	@classmethod
	def poll(self,context):
		return context.object is not None


def register():
	bpy.types.Scene.my_camera_tool = PointerProperty(type=camera_helper_properties)
#	print()
	#bpy.utils.register_class()
	#bpy.utils.register_module(__name__)

	
def unregister():
	del bpy.types.Scene.my_camera_tool
	#bpy.utils.unregister_class( )
	#bpy.utils.unregister_module(__name__)

#if __name__ == "__main__":
#	register()
