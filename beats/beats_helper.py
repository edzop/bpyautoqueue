import bpy

import os

from .. import util_helper


def get_bake_target_object(soundfile,frequency_text):

	bake_obj_name="sb_%s_%s"%(os.path.splitext(os.path.basename(soundfile))[0],frequency_text)

	print("bake: %s"%bake_obj_name)

	bake_obj=util_helper.find_object_by_name(bake_obj_name)

	if bake_obj is None:
		bpy.ops.mesh.primitive_cube_add(size=0.5)
		bake_obj=bpy.context.view_layer.objects.active
		bake_obj.name=bake_obj_name

	return bake_obj

frequencies = {
   ( 0,25 ),
	(  25,40),
	 ( 40,63),
	 ( 63,100),
	 (100,160),
	 (160,250),
	 (250,400),
	 (400,630),
	 (630,1000),
	(1000,1600),
	(1600,2500),
	(2500,4000),
	(4000,6300),
	(6300,10000),
   (10000,16000),
   (16000,20000)
}


def bake_frequency(soundfile,low_freq,high_freq):

	#area = next((a for a in bpy.context.screen.areas if a.type == "GRAPH_EDITOR"), None)

	area=None
	for a in bpy.context.screen.areas:
		area=a
	
	print("Baking '%s'..."%soundfile)

	frequency_text="%06d-%06d"%(low_freq,high_freq)
	obj=get_bake_target_object(soundfile,frequency_text)

	#obj.hide_set(False)

	bpy.context.scene.frame_set(1)

	if area is not None:
		with bpy.context.temp_override(area=area):

			last_type=area.type
			area.type = "GRAPH_EDITOR"
			#bpy.ops.view3d.snap_cursor_to_selected()
			obj.animation_data_clear()
			obj["y"] = 0.0
			obj.keyframe_insert(data_path="location", frame=1, index=2)
			obj.select_set(True)
			bpy.ops.graph.sound_bake(filepath=soundfile,low=low_freq, high=high_freq)

			area.type=last_type

		obj.hide_render=True
		#obj.hide_viewport=True



	return obj


import bpy
import wave
import contextlib

def add_bake(soundfile,mode):

	objects_added=[]


	if mode=="all":
		obj=bake_frequency(soundfile,0,100000)
		objects_added.append(obj)
	if mode=="16bar":

		offset=0
		for f in frequencies:
			obj=bake_frequency(soundfile,f[0],f[1])
			offset=offset+0.5

			obj.location.y=offset
			objects_added.append(obj)

	for o in objects_added:
		print("Normalize")
		normalize_audio(o)

	return objects_added


def add_bake2(soundfile):
	with bpy.context.temp_override(area=area):
		last_type=area.type
		area.type = "GRAPH_EDITOR"
		obj = bpy.data.objects["Cube"]
		obj["y"] = 0.0
		#obj.keyframe_delete(data_path="location",index=2)
		obj.animation_data_clear()
		#Set Frame to frame zero
		obj.keyframe_insert(data_path="location", frame=1, index=2)
		#obj.keyframe_insert('["y"]', frame=1)
		obj.select_set(True)

		bpy.ops.graph.sound_bake(filepath=soundfile)
		print("bake")
		area.type=last_type


def normalize_audio(obj):
	
	frame_end=bpy.context.scene.frame_end
	frame_start=bpy.context.scene.frame_start

	max_val = 0
	min_val = 1

	fcurve=obj.animation_data.action.fcurves[0]

	range=fcurve.range()

	print("Range: %d %d",range[0],range[1])

	if range[1]>bpy.context.scene.frame_end:
		bpy.context.scene.frame_end=int(range[1])

	# Get min / max
	for f in fcurve.range():
		val=fcurve.evaluate(f)
		if val>max_val:
			max_val=val
			
		if val<min_val:
			min_val=val

	# Make sure we don't divide by zero
	if max_val==0:
		max_val=1
			
	scale_factor=1/max_val

	# normalize audio - multiply by scale factor
	for f in fcurve.range():

		val=obj.animation_data.action.fcurves[0].evaluate(f)
		obj.location.x=val*scale_factor
		obj.keyframe_insert(data_path="location", frame=f, index=0)

	print("Input range(%f-%f) - scale factor %f"%(min_val,max_val,scale_factor))
 

def get_speaker(soundfile):


	speaker_obj_name="sp_%s"%os.path.splitext(os.path.basename(soundfile))[0]

	print("speaker: %s"%speaker_obj_name)

	speaker_obj=util_helper.find_object_by_name(speaker_obj_name)

	if speaker_obj is None:
		bpy.ops.object.speaker_add(enter_editmode=False, location=(0, 0, 0))
		speaker_obj=bpy.context.view_layer.objects.active
		speaker_obj.name=speaker_obj_name
		speaker_obj.data.update_tag()

	speaker_obj.data.sound = bpy.data.sounds.load(soundfile)

	return speaker_obj

