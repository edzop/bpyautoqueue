import bpy
import os


from bpy_extras.io_utils import ImportHelper

from bpy.props import (StringProperty,
						CollectionProperty,
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

area=None

from . import util_helper

def get_bake_target_object(soundfile):

	bake_obj_name=os.path.splitext(os.path.basename(soundfile))[0]

	print("bake: %s"%bake_obj_name)

	bake_obj=util_helper.find_object_by_name(bake_obj_name)

	if bake_obj is None:
		bpy.ops.mesh.primitive_cube_add(size=0.5)
		bake_obj=bpy.context.view_layer.objects.active
		bake_obj.name=bake_obj_name

	return bake_obj


def normalize_audio(obj):
	
	frame_end=bpy.context.scene.frame_end
	frame_start=bpy.context.scene.frame_start

	max_val = 0
	min_val = 1

	# Get min / max
	for f in range(frame_start,frame_end):
		val=obj.animation_data.action.fcurves[0].evaluate(f)
		if val>max_val:
			max_val=val
			
		if val<min_val:
			min_val=val

	# Make sure we don't divide by zero
	if max_val==0:
		max_val=1
			
	scale_factor=1/max_val

	# normalize audio - multiply by scale factor
	for f in range(frame_start,frame_end):

		val=obj.animation_data.action.fcurves[0].evaluate(f)
		obj.location.x=val*scale_factor
		obj.keyframe_insert(data_path="location", frame=f, index=0)

	print("Input range(%f-%f) - scale factor %f"%(min_val,max_val,scale_factor))
 
def add_bake(soundfile):
	#area = next((a for a in bpy.context.screen.areas if a.type == "GRAPH_EDITOR"), None)

	area=None
	for a in bpy.context.screen.areas:
		area=a
	
	print("Baking '%s'..."%soundfile)

	obj = get_bake_target_object(soundfile)

	obj.hide_set(False)

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
			bpy.ops.graph.sound_bake(filepath=soundfile)

			area.type=last_type

		obj.hide_render=True
		#obj.hide_viewport=True
		obj.hide_set(True)

	normalize_audio(obj)

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


class AddTracksOperator2(bpy.types.Operator):
	bl_idname = "wm.add_tracks_operator"
	bl_label = "Add Tracks"

	def execute(self, context):

		add_bake("/home/ek/Music/Super_Mario_Bros_Super_Show_-_02_-_supermario.mp3")
		
		return {'FINISHED'}

def process_file(file):
	print(file)


class AddTracksOperator(Operator,ImportHelper):
	bl_idname = "wm.add_tracks_operator"
	bl_label = "Add Tracks"

	filter_glob: StringProperty( default='*.wav;*.mp3', options={'HIDDEN'} )

	#some_boolean: BoolProperty( name='Do a thing', description='Do a thing with the file you\'ve selected', default=True, )

	files: CollectionProperty(
		name="Sound Files",
		type=bpy.types.OperatorFileListElement
		)

	directory: StringProperty(subtype='DIR_PATH')

	def execute(self, context):
		print("Hello")

		for soundfile in self.files:
			filepath=soundfile.name

			path = os.path.join(self.directory, soundfile.name)
			print("process %s" % path)

			add_bake(path)


			#process_file(directory,files)

		#filename, extension = os.path.splitext(self.filepath)

		#print('Selected file:', self.filepath)
		#print('File name:', filename)
		#print('File extension:', extension)
		#print('Some Boolean:', self.some_boolean)

		#add_bake(self.filepath)

		return {'FINISHED'}



class BeatsHelperPanel(Panel):
	bl_idname="PANEL_PT_beatsHelperPanel"
	bl_label = "Beats Helper"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "bpyAutoQueue"
	bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout

		row = layout.row()

		scene = context.scene
		my_queue_tool = scene.my_queue_tool


		layout.operator(AddTracksOperator.bl_idname)



