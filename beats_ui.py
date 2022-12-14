import bpy
import os

from bpy_extras.io_utils import ImportHelper


from bpy.props import (StringProperty,
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


class AddTracksOperator(Operator,ImportHelper):
	bl_idname = "wm.add_tracks_operator"
	bl_label = "Add Tracks"

	filter_glob: StringProperty( default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'} )

	#some_boolean: BoolProperty( name='Do a thing', description='Do a thing with the file you\'ve selected', default=True, )

	def execute(self, context):
		print("Hello")

		filename, extension = os.path.splitext(self.filepath)

		print('Selected file:', self.filepath)
		print('File name:', filename)
		print('File extension:', extension)
		print('Some Boolean:', self.some_boolean)



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



