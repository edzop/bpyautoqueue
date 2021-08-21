


bl_info = {
	"name": "bpyautoqueue",
	"description": "bpy auto queue",
	"author": "Ed Kraus",
	"version": (0, 0, 4),
	"blender": (2, 80, 0),
	"location": "3D View > Tools",
	"warning": "", # used for warning icon and text in addons panel
	"wiki_url": "...",
	"tracker_url": "",
	"category": "Development"
}


import bpy
from . import queue_ui
from . import camera_ui

from bpy.props import PointerProperty

classes = (
	queue_ui.queue_helper_properties,
	queue_ui.QueueSingleFrameOperator,
	queue_ui.PrintQueueOperator,
	queue_ui.ClearFileFromQueueOperator,
	queue_ui.ReQueueFileOperator,
	queue_ui.ResizeFileOperator,
	queue_ui.QueueHelperPanel,

	camera_ui.camera_helper_properties,
	camera_ui.SetupRenderSettingsLuxOperator,
	camera_ui.SetupRenderSettingsCyclesOperator,
	camera_ui.SetupRenderCameraDollyOperator,
	camera_ui.LinkRandomLuxHdriOperator,
	camera_ui.LoadSceneOperator,
	camera_ui.ClearSceneHelperOperator,
	camera_ui.Operator_Choose_World,
	camera_ui.Operator_Choose_Background,
	camera_ui.SetupLightingOperator,
	camera_ui.SetBackgroundSceneHelperOperator,
	camera_ui.SetupAutoPanOperator,
	camera_ui.DumpCamDataOperator,
	camera_ui.CamHelperPanel,

)

def register():


	for cls in classes:
		bpy.utils.register_class(cls)


	bpy.types.Scene.my_queue_tool = PointerProperty(type=queue_ui.queue_helper_properties)
	bpy.types.Scene.my_camera_tool = PointerProperty(type=camera_ui.camera_helper_properties)


def unregister():
	del bpy.types.Scene.my_queue_tool
	del bpy.types.Scene.my_camera_tool
	
	for cls in classes:
		bpy.utils.unregister_class(cls)

	
