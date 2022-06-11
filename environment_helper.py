import bpy
import glob
import os

from . import util_helper

class Environment_Helper():

	worldlist = None
	blacklist = None

	def __init__(self):
		self.worldlist=[]
		self.blacklist=[]


	def generate_world_list(self):

		worldpath='/home/blender/environment/alternate/'

		for infile in glob.glob( os.path.join(worldpath, '*.blend') ):
			if infile.find('black')==-1:
				self.worldlist.append(infile)
			else:
				self.blacklist.append(infile)

		self.worldlist.sort()
		self.blacklist.sort()

		#print(self.worldlist)


	# TODO reuse

	def get_blendfile_without_extension(self):
		blend_file = os.path.basename(bpy.context.blend_data.filepath)

		blendfile_without_extension = os.path.splitext(blend_file)[0]
		return blendfile_without_extension


	# TODO share function
	def getSequenceFromName(self,filename,maxVal):
		hashVal = util_helper.stringToHash(filename)
		print("hash: %s max %d"%(hashVal,maxVal))
		return hashVal % maxVal

	def assign_sequenced_environment(self):

		self.generate_world_list()

		if len(self.worldlist)<1:
			return None

		world_index = self.getSequenceFromName(self.get_blendfile_without_extension(),len(self.worldlist))
		world_file = self.worldlist[world_index]

		print("Assigning environment: %s"%world_file)
		bpy.ops.wm.link(directory=world_file + '/Collection/',files=[{'name': 'environment'}],relative_path=False)
