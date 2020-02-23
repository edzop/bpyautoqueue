


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

from . import auto_load
auto_load.init()


def register():
	auto_load.register()
#	bpy.utils.register_module(__name__)

def unregister():
	auto_load.unregister()
