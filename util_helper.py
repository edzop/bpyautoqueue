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



def scene_has_light():	

	for obj in bpy.data.objects:
		if obj.type=="LIGHT":
			print("found light: %s type %s" %(obj.name,obj.type))
			return True
				
	return False

				
def remove_all_texts():
	for text in bpy.data.texts:
		bpy.data.texts.remove(text)
			
def check_file_saved(operator):
		filename = bpy.context.blend_data.filepath

		if len(filename)<1:
			operator.report({'ERROR'}, "need to save file first")
			return None

		return filename

def find_collection(context, item):
	collections = item.users_collection
	if len(collections) > 0:
		return collections[0]
	return context.scene.collection


def move_object_to_collection(new_collection,the_object):

	C_collection = find_collection(bpy, the_object)
	C_collection.objects.unlink(the_object)

	new_collection.objects.link(the_object)

def make_collection(collection_name, parent_collection):
	if collection_name in bpy.data.collections:
		return bpy.data.collections[collection_name]
	else:
		new_collection = bpy.data.collections.new(collection_name)
		bpy.context.scene.collection.children.link(new_collection)
		return new_collection


def move_to_scene_collection(obj):
	collection =  make_collection("scene",bpy.context.scene.collection.children)
	move_object_to_collection(collection,obj)


