import bpy

from . import util_helper

from .util_cycles import cycles_helper

class camera_dolly_helper:

	light_size=0.5
	name_light_top="light.top_auto"
	name_light_side="light.side_auto"
	name_light_back="light.back_auto"

	def __init__(self,thePanHelper):
		self.thePanHelper=thePanHelper
		self.light_size=0.9


	def setup_camera_rig(self,light_name,x,y,z,target_mat_name):

		util_helper.remove_object_by_name(light_name)

		_location=(x, y, z)

		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=self.light_size, location=_location)

		#light_scale=0.7
		newlight = bpy.context.active_object
		newlight.name=light_name

		#newlight.parent=self.light_target
		bpy.ops.object.material_slot_add()
		newlight.material_slots[0].material = bpy.data.materials[target_mat_name]

	def get_light_focus_object(self):
		light_focus_object_name="light_focus"

		light_focus=util_helper.find_object_by_name(light_focus_object_name)

		if light_focus==None:
			bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
			light_focus = bpy.context.active_object
			light_focus.name=light_focus_object_name

		return light_focus

	def setup_camera_rig2(self,light_name,x,y,z,target_mat_name):
		util_helper.remove_object_by_name(light_name)
		_location=(x, y, z)

		bpy.ops.mesh.primitive_plane_add(size=self.light_size, enter_editmode=False, location=_location)

		newlight = bpy.context.active_object
		newlight.name=light_name

		bpy.ops.object.material_slot_add()
		newlight.material_slots[0].material = bpy.data.materials[target_mat_name]

		track_new = newlight.constraints.new(type="TRACK_TO")
		track_new.track_axis = 'TRACK_Z'
		track_new.up_axis = 'UP_Y'

		track_new.target=self.get_light_focus_object()


	def setup_auto_lights(self,autoPanStep):

		total_frames=bpy.context.scene.frame_end

		keyframes = list()
		for i in range(0,self.thePanHelper.scenecount):
			keyframes.append((i*autoPanStep)+1)
	
		print("setup auto lights, total frames: %d"%(total_frames))

		frame_number_start=1
		frame_number_mid=total_frames/2
		frame_number_end=total_frames

		strength_off=0.2
		strength_max=1.0

		keyframes_left = []
		keyframes_left.append([keyframes[0],strength_max])
		keyframes_left.append([keyframes[1],strength_off])
		keyframes_left.append([keyframes[2],strength_max])
		keyframes_left.append([keyframes[3],strength_max])
		keyframes_left.append([keyframes[4],strength_max])

		keyframes_top = []
		keyframes_top.append([keyframes[0],strength_max])
		keyframes_top.append([keyframes[1],strength_max])
		keyframes_top.append([keyframes[2],strength_max])
		keyframes_top.append([keyframes[3],strength_off])
		keyframes_top.append([keyframes[4],strength_off])

		keyframes_right = []
		keyframes_right.append([keyframes[0],strength_off])
		keyframes_right.append([keyframes[1],strength_max])
		keyframes_right.append([keyframes[2],strength_off])
		keyframes_right.append([keyframes[3],strength_max])
		keyframes_right.append([keyframes[4],strength_max])


		renderer_name=bpy.context.scene.render.engine

		if renderer_name=="CYCLES":
			color_top=(1.0,1.0,1.0)
			color_side=(1.0,0.9,0.4)
			color_back=(0.4,0.5,1.0)
			mat_top = cycles_helper.make_emission_material_cycles(self.name_light_top,color_top)
			mat_side = cycles_helper.make_emission_material_cycles(self.name_light_side,color_side)
			mat_back = cycles_helper.make_emission_material_cycles(self.name_light_back,color_back)

			cycles_helper.animate_emission_cycles(mat_side,keyframes_left)
			cycles_helper.animate_emission_cycles(mat_back,keyframes_right)
			cycles_helper.animate_emission_cycles(mat_top,keyframes_top)

		elif renderer_name=="LUXCORE":

			util_lux.make_lux_lightgroup(self.name_light_back)
			util_lux.make_lux_lightgroup(self.name_light_side)
			util_lux.make_lux_lightgroup(self.name_light_top)
			
			mat_top = util_lux.make_lux_emission_material(self.name_light_top,6500)
			mat_side = util_lux.make_lux_emission_material(self.name_light_side,2700)
			mat_back = util_lux.make_lux_emission_material(self.name_light_back,20000)

			util_lux.animate_lightgroup(self.name_light_side,keyframes_left)
			util_lux.animate_lightgroup(self.name_light_back,keyframes_right)
			util_lux.animate_lightgroup(self.name_light_top,keyframes_top)


		self.setup_camera_rig2(self.name_light_top,0,0,6,self.name_light_top)
		self.setup_camera_rig2(self.name_light_side,-6,-4,1.2,self.name_light_side)
		self.setup_camera_rig2(self.name_light_back,6,-4,1.2,self.name_light_back)

	def adjust_lights_for_camera(self,panStep):

		oldFrameNumber = bpy.context.scene.frame_current

		cam = bpy.context.scene.camera
		light_top=util_helper.find_object_by_name(self.name_light_top)
		light_left=util_helper.find_object_by_name(self.name_light_side)
		light_back=util_helper.find_object_by_name(self.name_light_back)

		light_margin=self.light_size/2

		for i in range(0,self.thePanHelper.scenecount):
			bpy.context.scene.frame_set((i*panStep)+1)
			
			#print("Checking lights in front of camera... frame %d"%bpy.context.scene.frame_current)
			
			if light_top!=None:
				#print("checking %f %f %f"%(light_top.location.z,light_margin*2,cam.location.z))
				if (light_top.location.z-(light_margin*2))<cam.location.z:
					light_top.location.z=cam.location.z+(light_margin*2)
					#print("Adjusting top light")

			if light_left!=None:
				if (light_left.location.x+light_margin)>cam.location.x:
					light_left.location.x=cam.location.x-light_margin			
					#print("Adjusting left light")

			if light_back!=None:
				if (light_back.location.x-light_margin)<cam.location.x:
					light_back.location.x=cam.location.x+light_margin			
					#print("Adjusting back light")

		bpy.context.scene.frame_set(oldFrameNumber)

