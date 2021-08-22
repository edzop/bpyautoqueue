import bpy
import glob
import os

from .. import util_helper

class World_Helper():

	worldlist = list()
	blacklist = list()

	#def __init__(self):
		


	def set_world_file(self,worldfile):
		bpy.context.scene["worldfile"]=worldfile

	def get_world_file(self):
		if "worldfile" in bpy.context.scene:
			return bpy.context.scene["worldfile"]
		else:
			return None

	def remove_world(self):
		bpy.context.scene.world=None

		# first clear out all the old worlds
		for cworld in bpy.data.worlds:
			bpy.data.worlds.remove(cworld)

	def generate_world_list(self):

		worldpath='/home/blender/worlds/'

		for infile in glob.glob( os.path.join(worldpath, '*.blend') ):
			if infile.find('black')==-1:
				self.worldlist.append(infile)
			else:
				self.blacklist.append(infile)

		self.worldlist.sort()
		self.blacklist.sort()

		print(self.worldlist)


	# TODO reuse

	def get_blendfile_without_extension(self):
		blend_file = os.path.basename(bpy.context.blend_data.filepath)

		blendfile_without_extension = os.path.splitext(blend_file)[0]
		return blendfile_without_extension


	def assign_world_file_from_sequence(self,world_index):

		scene_index = self.getSequenceFromName(self.get_blendfile_without_extension(),len(scenelist))
		world_file = self.worldlist[world_index]
		return world_file

		

	def link_random_world_file(self):

		world_index=0
	#		print("sequence " + str(image_seq) + " index [" + str(world_index) + "/" + str(len(worldlist)) + "] = " + worldlist[world_index])

	def link_world_file(self,world_file):
	 
		self.remove_world()

		bpy.ops.wm.link(directory=world_file + '/World/',files=[{'name': 'linkworld'}],relative_path=False)

		for cworld in bpy.data.worlds:
	#			print("Assiging world: " + str(cworld))
			bpy.context.scene.world=cworld

		self.set_world_file(world_file)

	def set_black_world(self):
		self.set_color_world(color=(0,0,0))

	def set_color_world(self,color=(0.0, 0.0,0.0)):
		colorworld = bpy.data.worlds.new("colorworld")
		bpy.context.scene.world = colorworld
		colorworld.use_nodes = True

		bg = colorworld.node_tree.nodes['Background']
		bg.inputs[0].default_value[:3] = color
		bg.inputs[1].default_value = 1.0


	# TODO share function
	def getSequenceFromName(self,filename,maxVal):
		hashVal = util_helper.stringToHash(filename)
		return hashVal % maxVal


	def set_hdri_world(self,world_hdri_file):
		bpy.context.scene.world.use_nodes = True
		tree = bpy.context.scene.world.node_tree

		# clear default nodes
		for n in tree.nodes:
			tree.nodes.remove(n)

		n_ev=tree.nodes.new("ShaderNodeTexEnvironment")     
		n_ev.location = 0,0

		img = bpy.data.images.load(world_hdri_file)
		n_ev.image=img

		n_bg = tree.nodes.new('ShaderNodeBackground')      
		n_bg.location = 200,0

		n_ow = tree.nodes.new('ShaderNodeOutputWorld')      
		n_ow.location = 400,0

		# link nodes
		links = tree.links
		link0 = links.new(n_ev.outputs[0],n_bg.inputs[0])
		link1 = links.new(n_bg.outputs[0],n_ow.inputs[0])

	def link_random_cycles_hdri(self):
		print("Linking random Cycles hdri")

		#util_helper.scene_remove_hemi_light()
		#util_helper.scene_remove_sun_light()

		self.remove_world()
		self.set_black_world()


		hdrilist = list()

		hdriindex_index=0

		hdripath='/home/blender/environment/output'

		for infile in glob.glob( os.path.join(hdripath, '*.hdr' )):
			hdrilist.append(infile)

		#for infile in glob.glob( os.path.join(hdripath, '*.exr' )):
		#	hdrilist.append(infile)

		hdrilist.sort()

		hdri_index = self.getSequenceFromName(self.get_blendfile_without_extension(),len(hdrilist))

		#print(hdrilist)
		
		hdri_filename=hdrilist[hdri_index]
		print("selected: %s"%hdri_filename)

		self.set_hdri_world(hdri_filename)
		
		#bpy.ops.image.open(filepath=hdri_filename)
		#filename_without_path=os.path.basename(hdri_filename)

		#img=bpy.ops.image.open(filepath=hdri_filename)


		#bpy.data.worlds[0].luxcore.light="infinite"
		#bpy.data.worlds[0].luxcore.image=bpy.data.images[filename_without_path]
		#bpy.data.worlds[0].luxcore.rotation=math.radians(90)

		#bpy.context.scene.luxcore.lightgroups.default.gain=0.5

