
import bpy

import os
import sys

# Adds frames from a blender file to database

from bpyautoqueue import render_db
from bpyautoqueue import rend_helper
from bpyautoqueue import auto_camera_pan


argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

target_renderer=argv[0]
anim_mode=argv[1]

def add_frames(target_renderer,anim_mode):
	theDB = render_db.render_db()

	theDB.selected_render_engine=target_renderer
	theDB.configure_anim_mode(anim_mode)

	theRendHelper = rend_helper.Rend_Helper(False,theDB.autopanstep)

	print("Autopan step: %d" %(theDB.autopanstep))

	if theDB.autopanstep>0:
		thePanHelper = auto_camera_pan.Cam_Pan_Helper()
		thePanHelper.setup_auto_pan(theDB.autopanstep)
		

	frame_start = bpy.context.scene.frame_start
	frame_end = bpy.context.scene.frame_end
		
	filename = bpy.context.blend_data.filepath

	print("Adding frames: %d - %d - renderer '%s' mode: %s"%(
		frame_start,
		frame_end,
		target_renderer,
		anim_mode))

	framelist = []

	for num in range(frame_start,frame_end+1):
		framelist.append(num)

	theDB.insert_or_update_blend_file(filename,framelist)

	print("Checked frames: %s"%framelist)


add_frames(target_renderer,anim_mode)