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

from .beats import beats_helper


class beat_helper_properties(PropertyGroup):

   
	bake_modes: EnumProperty(
		name="Dropdown:",
		description="Mode",
		items=[ ('all', "All", ""),
				('16bar', "16bar", "")
			   ]
		)
	
	hideoutput : BoolProperty(
		name = "Hide Output",
		default = True,
		description = "Hide output objects in vieport"
	)





def add_tracks(path):
	my_beats_tool = bpy.context.scene.my_beats_tool

	print("process: %s mode: %s" %(path,my_beats_tool.bake_modes))



	objects_added=beats_helper.add_bake(path,my_beats_tool.bake_modes)

	for o in objects_added:
		#if my_beats_tool.hideoutput==True:
		o.hide_set(my_beats_tool.hideoutput)
	
	beats_helper.get_speaker(path)

# hard coded path for testing
class AddTracksOperator(bpy.types.Operator):
	bl_idname = "wm.add_tracks_operator"
	bl_label = "Add Tracks"

	def execute(self, context):

		soundfile="/home/ek/Music/Super_Mario_Bros_Super_Show_-_02_-_supermario.mp3"
		add_tracks(soundfile)
		return {'FINISHED'}

class AddTracksOperatorX(Operator,ImportHelper):
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

		for soundfile in self.files:
			filepath=soundfile.name

			path = os.path.join(self.directory, soundfile.name)

			add_tracks(path)

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

		my_beats_tool = bpy.context.scene.my_beats_tool

		layout.prop( my_beats_tool, "bake_modes", text="Bake Mode") 

		layout.operator(AddTracksOperator.bl_idname)

		row = layout.row() 
		row.prop(my_beats_tool, "hideoutput")


