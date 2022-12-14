import bpy
import sys
import os.path
import os
import time
import functools
import glob
import hashlib

def stringToHash(s):
	val = int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)
	return val

def remove_constraint_from_object(object,constraint_name):
	for constraint in object.constraints:
			if constraint.type == constraint_name:
				object.constraints.remove(constraint)
			
def get_output_filename(blendfile_without_extension,frameIndex,renderer_name,image_file_extension):
	image_output_filename = '%s.%04d.%s.%s' %(blendfile_without_extension,frameIndex,renderer_name,str.lower(image_file_extension))
	return image_output_filename


def generate_location_keyframes(target_object,current_frame):
	target_object.keyframe_insert(data_path="location", frame=current_frame, index=0)
	target_object.keyframe_insert(data_path="location", frame=current_frame, index=1)
	target_object.keyframe_insert(data_path="location", frame=current_frame, index=2)

def find_object_by_name(object_name):
	for obj in bpy.data.objects:
		if(obj.name==object_name):
			return obj
	
	return None	

def remove_object_by_name(object_name,starting_with=False):
	for obj in bpy.data.objects:
		if starting_with:
			if obj.name.startswith(object_name):
				bpy.data.objects.remove(obj)
		else:	
			if(obj.name==object_name):
				bpy.data.objects.remove(obj)

def do_save():
	bpy.ops.wm.save_mainfile(filepath=bpy.context.blend_data.filepath, 
		check_existing=True, 
		filter_blender=True, 
		compress=True, 
		relative_remap=False)

def IsNotNull(value):
	return value is not None and len(value) > 0

def add_sun_light():
	print("adding sun")
	bpy.ops.object.light_add(type='SUN', radius=1, location=(-4, -14, 15),rotation=(0.785, 0.0, -0.349))

def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

def getLastLine(f):
	
	lastline=""
	
	for line in f:
		if line.find('#')==-1:
			lastline=line
		
	return lastline

def secondsToStr(t):
	rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
	return "%d:%02d:%02d.%03d" % tuple(functools.reduce(rediv,[[t*1000,],1000,60,60]))

def inclusive_range(start, stop, step=1):
	l = []
	x = start
	while x <= stop:
		l.append(x)
		x += step
	return l

def get_blendfile_without_extension(blendfile=None):
	if blendfile==None:
		blend_file = os.path.basename(bpy.data.filepath)
		
	blendfile_without_extension = os.path.splitext(blend_file)[0]
	return blendfile_without_extension
		
def is_hemi(obj):
	if (obj.type=='LAMP') :
		if(obj.data.type == 'HEMI') :
			return True
		
	return False

def is_sun(obj):
	if (obj.type=='LAMP') :
		if(obj.data.type == 'SUN') :
			return True
		
	return False

def scene_has_light():	

	for obj in bpy.data.objects:
		if obj.type=="LIGHT":
			print("found light: %s type %s" %(obj.name,obj.type))
			return True
				
	return False

def scene_has_sun():	

	for obj in bpy.data.lights:
		if obj.type=="SUN":
				print("found sun light: %s" %(obj.name))
				return True

	print("NO sun")
				
	return False
				
def remove_all_texts():
	for text in bpy.data.texts:
		bpy.data.texts.remove(text)
		
		
def scene_remove_sun_light():
	for scene in bpy.data.scenes:
		for theobject in scene.objects:
			if is_sun(theobject):
				remove_object_by_name(theobject.name)
	
def scene_remove_hemi_light():
	for scene in bpy.data.scenes:
		for theobject in scene.objects:
			if is_hemi(theobject):
				remove_object_by_name(theobject.name)
				
def remove_group_by_name(searchname):
	for g in bpy.data.groups:
		if g.name==searchname:
			print("remove_group_by_name: %s"%searchname)
			bpy.data.groups.remove(g)

def check_file_saved(operator):
		filename = bpy.context.blend_data.filepath

		if len(filename)<1:
			operator.report({'ERROR'}, "need to save file first")
			return None

		return filename