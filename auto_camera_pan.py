
import bpy
import math

import sys
import os.path
import os
import time
import functools
import string
import hashlib
import random
import glob

from . import util_helper
from . import camera_dolly_helper

#	Todo: Floating object, Black space (emitter scene)

class Cam_Pan_Helper:

	# How many auto scene positions we have
	scenecount=5
	
	def __init__(self):

		self.verbose=False
		
		self.DoDebug=True
		
		self.status_message="-"
		self.oX = 0
		self.oY = 0
		self.oZ = 0
		
		self.dof_object=None
		self.target_object=None
		
		self.minZ = 0.1
		self.maxZ = 100
		
		self.minLens = 8
		self.maxLens = 250
		
		self.max_arm = 0
		
		self.current_frame=0
		
		self.object_frame_name="object_frame"		
		self.object_scene_name="object_scene"
		self.dof_name="dof_focus"
		
		self.orignal_dof_X = 0
		self.orignal_dof_Y = 0
		self.orignal_dof_Z = 1

		
		#self.scenecount=5
		
		self.init_cam_data();
		
	def init_cam_data(self):
		self.cam = bpy.context.scene.camera

		if self.cam==None:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.camera_add(location=(0, -5, -5))
			self.cam = bpy.context.view_layer.objects.active



		self.cam.select_set(state=True)
		bpy.context.view_layer.objects.active = self.cam

		self.oX = self.cam.location.x
		self.oY = self.cam.location.y
		self.oZ = self.cam.location.z
		
		self.lens = self.cam.data.lens
		
		self.dof_object=self.find_dof(self.cam)

		if self.dof_object==None:
			bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
			self.dof_object=bpy.context.view_layer.objects.active
			self.dof_object.name=self.dof_name
			self.replace_cam_track_to_target(self.dof_object)
			


		if self.dof_object!=None:
#			print("found DOF")
			self.orignal_dof_X = self.dof_object.location.x
			self.orignal_dof_Y = self.dof_object.location.y
			self.orignal_dof_Z = self.dof_object.location.z
			
			self.dof_object.animation_data_clear()
			
			for constraint in self.dof_object.constraints:
				if constraint.type == 'COPY_LOCATION':
#					print("found target")
					self.target_object=constraint.target
					


		# max arm is the longest distance from the camera 
		# to the center of scene
		if abs(self.oX)>self.max_arm:
			self.max_arm=abs(self.oX)
			
		if abs(self.oY)>self.max_arm:
			self.max_arm=abs(self.oY)
			
		if abs(self.oZ)>self.max_arm:
			self.max_arm=abs(self.oZ)
		
		
		self.cam.data.animation_data_clear()
		self.cam.animation_data_clear()

	# cam.keyframe_delete(data_path="location")

	#bpy.context.active_object.animation_data_clear()
	
	def limit_range(self,input,min,max):
		newnum = input;
		
		if newnum < min:
			newnum = min
			
		if newnum > max:
			newnum = max
			
		return newnum
		
		
	def validate_settings(self):
		if self.dof_object==None:
			self.status_message="No DOF Object"
			return False
			
		return True
	
		
	def reset_dof_to_original(self):
		self.set_dof_position(self.orignal_dof_X,self.orignal_dof_Y,self.orignal_dof_Z,False)
		
	def get_dof_object(self):
		return self.dof_object
		
	def insert_dof_keyframes(self):
		self.dof_object.keyframe_insert(data_path="location", frame=self.current_frame, index=0)
		self.dof_object.keyframe_insert(data_path="location", frame=self.current_frame, index=1)
		self.dof_object.keyframe_insert(data_path="location", frame=self.current_frame, index=2)
		
		
	def set_dof_position(self,x,y,z,relative):
		
		if self.dof_object==None:
			return
			
		if relative==True:
			self.dof_object.location.x=self.orignal_dof_X + x
			self.dof_object.location.y=self.orignal_dof_Y + y
			self.dof_object.location.z=self.limit_range(self.orignal_dof_Z + z,self.minZ,self.maxZ)
		else:
			self.dof_object.location.x=x
			self.dof_object.location.y=y
			self.dof_object.location.z=self.limit_range(z,self.minZ,self.maxZ)

	def jump_to_frame(self,Curframe):
		self.current_frame=Curframe
		bpy.context.scene.frame_set(Curframe)
		
	def set_lens_length(self,length):
		self.cam.data.lens_unit="MILLIMETERS"
		self.cam.data.lens= self.limit_range(length,self.minLens,self.maxLens)	
		
	def insert_cam_keyframes(self):
		util_helper.generate_location_keyframes(self.cam,self.current_frame)
		
		self.cam.data.keyframe_insert(data_path="lens", frame=self.current_frame)
		

	def insert_cam_keyframe(self,x,y,z,lens,relative):
		
	#	self.jump_to_frame(self.current_frame)
			
		if relative==True:
			self.cam.location.x=self.oX + x
			self.cam.location.y=self.oY + y
			self.cam.location.z=self.limit_range(self.oZ + z,self.minZ,self.maxZ)
			
			self.set_lens_length(lens)
		else:
			self.cam.location.x=x
			self.cam.location.y=y
			self.cam.location.z=self.limit_range(z,self.minZ,self.maxZ)
			
			self.set_lens_length(lens)
			

		self.insert_cam_keyframes()
		

	def set_frames(self,frameStart,frameEnd):
		bpy.context.scene.frame_start=frameStart
		bpy.context.scene.frame_set(frameStart)
		bpy.context.scene.frame_end=frameEnd
		
	def find_dof(self,object):
		for constraint in object.constraints:
			if constraint.type == 'DAMPED_TRACK' or constraint.type == 'TRACK_TO':
				return constraint.target
		return None
		
	def replace_cam_track_to_target(self,newtarget):
		
		dof = self.find_dof(self.cam)
		
		if dof is None:
			#objs = self.cam.constraints.new(type='DAMPED_TRACK')
			#objs.track_axis='TRACK_NEGATIVE_Z'

			new_constraint = self.cam.constraints.new(type='TRACK_TO')
			new_constraint.track_axis='TRACK_NEGATIVE_Z'
			new_constraint.target = newtarget
							
		self.cam["dof_object"]=newtarget

		self.cam.rotation_euler[0]=math.radians(90)
		self.cam.rotation_euler[1]=math.radians(0)
		self.cam.rotation_euler[2]=math.radians(0)
				
	def set_view_sequence(self,sequence):
				
		if self.target_object!=None:
			
			target_height=self.target_object.scale.z
			target_length=self.target_object.scale.y
			target_width=self.target_object.scale.x
			
			target_aspect=target_width/target_length
			
			# should be 1.77 for 1920x1080
			cam_aspect=bpy.context.scene.render.resolution_x/bpy.context.scene.render.resolution_y
			
			cam_target_aspect=cam_aspect/target_aspect
				
#			aspect_adjusted_zoom=1.01
			
#			if target_aspect < 1.0:
#				aspect_adjusted_zoom=0.9
				
#			if target_aspect >= 1.0 and target_aspect < 1.2:
#				aspect_adjusted_zoom=0.85
				
#			if target_aspect > 1.2 and target_aspect < 1.5:
#				aspect_adjusted_zoom=0.87
				
#			if target_aspect > 1.5:
#				aspect_adjusted_zoom=0.9
				#cam_target_aspect=1
				
				
			# smaller number = more zoomed out
			# larger number = more zoomed in
			#aspect_adjusted_zoom=1.0
			
#			if target_aspect>1.2:
			if cam_aspect>=target_aspect:
				aspect_adjusted_zoom=0.98/cam_aspect
				#(target_aspect/cam_aspect)
			else:
				aspect_adjusted_zoom=0.98
				#(target_aspect/cam_aspect)
			
			
			object_deviation_from_zero=(target_aspect-1.0)
			
		#	aspect_adjusted_zoom=cam_target_aspect*0.5
			#aspect_adjusted_zoom-(object_deviation_from_zero*0.25)
			# + (target_aspect/6) + (object_deviation_from_zero/1.3)
			
			if self.verbose==True:
				print("object_deviation_from_zero %0.2f aspect_adjusted_zoom %0.2f target %0.2f" %(object_deviation_from_zero,aspect_adjusted_zoom,
																target_aspect))


			shift_z_factor=target_height
			shift_y_factor=target_length
			shift_x_factor=target_width
			
			infoText = "using target: %s size(%0.2f,%0.2f,%0.2f) Aspect(%2.2f) aspectzoom(%2.2f) camaspect(%2.2f)" %(self.target_object.name,target_width,target_length,target_height,target_aspect,aspect_adjusted_zoom,cam_target_aspect)

			if self.verbose==True:	
				print(infoText)
			
#			self.set_lens_length(50)

			# rendered frames are +1, internally is zero based

			if sequence==4:
				
				#	Right Front Forward Closeup
				#aspect_shift = 0
				#(target_aspect-1.0)*0.04

				self.set_dof_position(self.target_object.location.x+(target_width*0.4), 
										self.target_object.location.y-(target_length*0.5), 
										self.target_object.location.z,False)

#				self.set_dof_position(self.target_object.location.x-(target_width*(0.5-aspect_shift)), self.target_object.location.y-(target_length*0.8), self.target_object.location.z+(target_height*0.2),False)
				self.zoom_out(self.target_object, +0.3, -0.3, 0.05, aspect_adjusted_zoom)
			
			elif sequence==3: 
		
				
				#	Top Down Far Out					
				self.set_dof_position(self.target_object.location.x, 
										self.target_object.location.y, 
										self.target_object.location.z+(target_height*0.75),False)
				self.zoom_out(self.target_object, 0.0, -0.05, 0.2, aspect_adjusted_zoom)

				#2.0 / (target_aspect * 1.0))
				# tweak the camera position slightly to prevent camera flipping when it crosses zero because of the track to modifier
				self.cam.location.y=self.cam.location.y-0.08
				


			# Frame 3
			elif sequence==2:
				
				#	Left Front far out				
				self.set_dof_position(self.target_object.location.x, 
										self.target_object.location.y-(target_length*0.5), 
										self.target_object.location.z+(target_height*0.05),False)
				self.zoom_out(self.target_object, 0.0, -0.2, -0.1, aspect_adjusted_zoom*0.9)


			# Frame 2	
			elif sequence==1:
				
				#	front close			
				self.set_dof_position(self.target_object.location.x-(target_width*0.3), 
										self.target_object.location.y-(target_length*0.75), 
										self.target_object.location.z,False)				
				self.zoom_out(self.target_object, -0.1, -0.2, 0.0, aspect_adjusted_zoom*1.5)
				
#				self.set_dof_position(self.target_object.location.x, self.target_object.location.y-(target_length*0.75), self.target_object.location.z-(target_height*0.3),False)
				


			# Frame 1
			elif sequence==0: 
				
				#	Left Front Forward Closeup
				#aspect_shift = 0
				#(target_aspect-1.0)*0.04

				self.set_dof_position(self.target_object.location.x-(target_width*0.3), 
										self.target_object.location.y-(target_length*0.5), 
										self.target_object.location.z,False)

#				self.set_dof_position(self.target_object.location.x-(target_width*(0.5-aspect_shift)), self.target_object.location.y-(target_length*0.8), self.target_object.location.z+(target_height*0.2),False)
				self.zoom_out(self.target_object, -0.3, -0.3, 0.05, aspect_adjusted_zoom)
			
#				print("Aspect Shift: %0.2f" % aspect_shift)

		#	Far Center Up
#		self.current_frame=self.current_frame+1
#		self.insert_cam_keyframe(self.current_frame,	0,-10,6,50,False)
#		self.insert_dof_keyframe(self.current_frame,0,-1,1,False)
		
		#	Low and wide
#		self.current_frame=self.current_frame+1
		
#		self.insert_cam_keyframe(self.current_frame,	0,-self.max_arm,self.max_arm,self.lens,False)
#		self.insert_cam_keyframe(self.current_frame,	0,-self.max_arm,-2,self.lens,False)
#		self.reset_dof_to_original(self.current_frame)
		
		#	Left side
#		self.current_frame=self.current_frame+1
#		self.insert_cam_keyframe(self.current_frame,	-self.max_arm,-self.max_arm,0,self.lens,False)
#		self.reset_dof_to_original(self.current_frame)
			
		else:		
			#print("no target to use: " + bpy.context.blend_data.filepath)	
			#	Left side
			self.insert_cam_keyframe(-self.max_arm,-self.max_arm,0,self.lens,False)
			self.reset_dof_to_original()

		
		
	def setup_auto_pan(self,frameInc=1):
	
		original_frame_number = self.current_frame

		frameStart=1
#		frameInc=85
		frameEnd=frameStart
		
		self.current_frame=1
		
		self.jump_to_frame(self.current_frame)
				
		sceneorder = list()
	
		for i in range(0,self.scenecount):
			sceneorder.append(i)
		
		#print(sceneorder)
				
		for i in sceneorder:
			frameEnd = self.current_frame
			self.set_view_sequence(i)
			self.insert_cam_keyframes()
			self.insert_dof_keyframes()
			
			self.jump_to_frame(self.current_frame+frameInc)

			
		self.set_frames(1,frameEnd)

		self.jump_to_frame(original_frame_number)



	def get_object_largest_dimension(self,obj,usescale=False):
		max_obj_dimension = 0
		
		if usescale==True:

			if obj.scale.x>max_obj_dimension:
				max_obj_dimension=obj.scale.x
				
			if obj.scale.y>max_obj_dimension:
				max_obj_dimension=obj.scale.y
				
			if obj.scale.z>max_obj_dimension:
				max_obj_dimension=obj.scale.z
				
			max_obj_dimension=max_obj_dimension*2
				
#			print("%2.2f %2.2f %2.2f = %2.2f" %(obj.scale.x,obj.scale.y,obj.scale.z,max_obj_dimension))
		
		else:	

			if obj.dimensions.x>max_obj_dimension:
				max_obj_dimension=obj.dimensions.x
				
			if obj.dimensions.y>max_obj_dimension:
				max_obj_dimension=obj.dimensions.y
				
			if obj.dimensions.z>max_obj_dimension:
				max_obj_dimension=obj.dimensions.z
				
				
#		print("Scale: %2.2f %2.2f %2.2f = %2.2f" %(obj.scale.x,obj.scale.y,obj.scale.z,max_obj_dimension))
#		print("Dim: %2.2f %2.2f %2.2f = %2.2f" %(obj.dimensions.x,obj.dimensions.y,obj.dimensions.z,max_obj_dimension))
						
		return max_obj_dimension
		
	def get_distance_between_objects(self,o1,o2):
		camObj = self.cam
		
		x1 = o1.location.x
		y1 = o1.location.y
		z1 = o1.location.z
		
		x2 = o2.location.x
		y2 = o2.location.y
		z2 = o2.location.z
		
		# for 2d points
#		dist = math.hypot(x2 - x1, y2 - y1)


		xd = x2-x1
		yd = y2-y1
		zd = z2-z1
		dist = math.sqrt(xd*xd + yd*yd + zd*zd)

		return dist
		
	def get_relative_angle(self,max_object_dimension,distance):
		
		a = math.atan( (0.5*max_object_dimension) / distance )
		
		conv = 57.2957795130823
		
		relative_angle=a * conv
		
		# * 2 ???
		
#		print("max_object_dimension(%0.2f) a(%0.2f) conv(%2.4f) distance(%0.2f) = relative_angle(%2.2f)" %(max_object_dimension,a,conv,distance,relative_angle))
		
		return relative_angle

	def zoom_out(self,obj,stepX,stepY,stepZ,zoom_factorX=1.0,zoom_limit=200):
		
		zoom_factor=zoom_factorX/2
		
		camObj = self.cam
		
		camObj.location.x = obj.location.x+stepX
		camObj.location.y = obj.location.y+stepY
		camObj.location.z = obj.location.z+stepZ
		
		camObj.location.x = self.dof_object.location.x+stepX
		camObj.location.y = self.dof_object.location.y+stepY
		camObj.location.z = self.dof_object.location.z+stepZ
		
		zoomlimit=util_helper.find_object_by_name("zoom_limit")
		
#		print("Zoomlimit: %2.2f %2.2f %2.2f" %(zoomlimit.scale.x,zoomlimit.scale.y,zoomlimit.scale.z))
		
#		print("zoomlimit: " + str(zoomlimit))

		
		
		largest_obj_dim = self.get_object_largest_dimension(obj,True)
		
		cam_angle = math.degrees(camObj.data.angle)
		info = "============ Zoom frame %d ==zoom factor %2.2f ==Camera Angle %0.2f=================" %(bpy.context.scene.frame_current,zoom_factor,cam_angle)
		
		continue_zoom = True
			
		while continue_zoom:
			
#			print("\n")
			
			lastX = camObj.location.x
			lastY = camObj.location.y
			lastZ = camObj.location.z

			relative_angle = self.get_object_relative_angle(obj)
			
			angle_stop = cam_angle*zoom_factor
			
			# To Debug zooming out data
			#print("relative_angle(%2.2f) cam_angle(%2.2f) angle_stop(%2.2f)" %(relative_angle,cam_angle,angle_stop))
			
			if relative_angle<=angle_stop:
				
				if self.verbose==True:
					print("aborting - cam_angle(%2.2f) relative_angle(%2.2f) angle_stop(%2.2f)" %(cam_angle,relative_angle,angle_stop))
					
				continue_zoom=False
				
			else:
				camObj.location.x=camObj.location.x+stepX
				camObj.location.y=camObj.location.y+stepY
				camObj.location.z=camObj.location.z+stepZ
				
			floor = 0.1
			if camObj.location.z<floor:
				camObj.location.z=floor
				
			if zoomlimit!=None:
				ceiling=zoomlimit.location.z+(zoomlimit.scale.z)
				if camObj.location.z>ceiling:
					camObj.location.z=ceiling
										
				back=zoomlimit.location.y-(zoomlimit.scale.y)
				if camObj.location.y<back:
					camObj.location.y=back
					
				left=zoomlimit.location.x-(zoomlimit.scale.x)
				if camObj.location.x<left:
					camObj.location.x=left
					
				right=zoomlimit.location.x+(zoomlimit.scale.x)
				if camObj.location.x>right:
					camObj.location.x=right
				
			# prevent something crazy from happening		
			if abs(camObj.location.x)>zoom_limit:
				continue_zoom=False
				if self.verbose==True:
					print("aborting - zoom limit X")
				
			if abs(camObj.location.y)>zoom_limit:
				continue_zoom=False
				if self.verbose==True:
					print("aborting - zoom limit Y")
				
			if abs(camObj.location.z)>zoom_limit:
				continue_zoom=False
				if self.verbose==True:
					print("aborting - zoom limit Z")
				
			if continue_zoom:
				if lastX==camObj.location.x:
					if lastY==camObj.location.y:
						if lastZ==camObj.location.z:
							continue_zoom=False
							if self.verbose==True:
								print("aborting - no change")
						
			relative_angle = self.get_object_relative_angle(obj)
			
			#print("Cam Target Distance: %0.2f Max Obj Dim: %0.2f R: %2f" %(distance,max_object_dimension,math.degrees(relative_angle)))			
			
			status_text="(%0.2f,%0.2f,%0.2f) R%2.0f L%2.0f(%2.0fmm) tld%2.2f z%1.1f " %(camObj.location.x,camObj.location.y,camObj.location.z, relative_angle, cam_angle,self.cam.data.lens,largest_obj_dim,zoom_factor)
			
			if self.verbose==True:
				print(status_text)

			
#			bpy.context.scene.render.stamp_note_text=status_text
#			bpy.context.scene.render.use_stamp_note=True
							

	def get_object_relative_angle(self,obj):		

		camObj = self.cam
				
		distance = self.get_distance_between_objects(obj,camObj)

		
		max_object_dimension = self.get_object_largest_dimension(obj,True)

		
		relative_angle=self.get_relative_angle(max_object_dimension,distance)
		
#		print("Cam Target Distance: %0.2f Max Obj Dim: %0.2f R: %2f" %(distance,max_object_dimension,math.degrees(relative_angle)))
		
#		print(" Relative Angle: %0.2f" % math.degrees(relative_angle))
		
		return relative_angle
		

		
	def find_largest_object_and_set_dof_copy_constraint(self):
		
		
		if self.dof_object != None:
			
			largest_object=None
			largest_dimension=0
			
			for scene in bpy.data.scenes:
				for theobject in scene.objects:
					if theobject.type=="MESH":
						
						dimension = self.get_object_largest_dimension(theobject)

						if self.verbose==True:
							print("Found object:" + theobject.name + " size: " + str(dimension))
						
						if dimension>largest_dimension:
							largest_object=theobject
							largest_dimension=dimension
					
			if largest_object!=None:
				
				object_frame = util_helper.find_object_by_name(self.object_frame_name)
				
				if object_frame==None:
					object_frame=self.create_object_frame()
					
				object_frame.location.x=largest_object.location.x
				object_frame.location.y=largest_object.location.y
				object_frame.location.z=(largest_object.location.z+(largest_object.dimensions.z/2))
				

				if self.verbose==True:
					print("Scaling Frame Object: " + object_frame.name)
				
				object_frame.scale.x=(largest_object.dimensions.x/2)
				object_frame.scale.y=(largest_object.dimensions.y/2)
				object_frame.scale.z=(largest_object.dimensions.z/2)
				
				object_frame.rotation_euler.x=largest_object.rotation_euler.x
				object_frame.rotation_euler.y=largest_object.rotation_euler.y
				object_frame.rotation_euler.z=largest_object.rotation_euler.z
			
				util_helper.remove_constraint_from_object(self.dof_object,'COPY_LOCATION')
				objs = self.dof_object.constraints.new(type='COPY_LOCATION')
				objs.target = object_frame
				objs.use_x=False
				objs.use_y=False
				objs.use_z=False
								
	def create_object_frame(self):
		
		bpy.context.scene.cursor_location.x=0
		bpy.context.scene.cursor_location.y=0
		bpy.context.scene.cursor_location.z=0
		
		bpy.ops.object.empty_add(type='CUBE', location=(0,0,0))
		bpy.context.active_object.name=self.object_frame_name
		
		return bpy.context.active_object
		

	def setup_for_scene_only_render(self):
		
		# set inside scene tag so it doesn't append random scene when rendering
		util_helper.remove_object_by_name(util_helper.Util_Helper.inside_scene_name)
		frame = self.create_object_frame()
		frame.location.x=20
		frame.location.y=20
		frame.location.z=-10
		frame.name=util_helper.Util_Helper.inside_scene_name
		
		
		dof=self.get_dof_object()

		if dof!=None:
#			print("Dof:" + str(dof))
			util_helper.remove_constraint_from_object(self.cam,'TRACK_TO')
			util_helper.remove_object_by_name(dof.name)
		

		
		util_helper.remove_object_by_name(self.dof_name)
		dof=bpy.ops.object.empty_add(type='SINGLE_ARROW', location=(0,0,1))
		dof=bpy.context.active_object
		dof.name=self.dof_name

			
		self.replace_cam_track_to_target(dof)

		self.set_lens_length(14)


		util_helper.remove_object_by_name("object_frame.001")
		util_helper.remove_object_by_name("object_frame.002")
		util_helper.remove_object_by_name("object_frame.003")
		

		# add object frame so we can get a good pan view
		util_helper.remove_object_by_name(self.object_frame_name)
		frame = self.create_object_frame()
		frame.location.x=dof.location.x
		frame.location.y=dof.location.y
		frame.location.z=dof.location.z
#		frame.name=self.object_frame_name

		util_helper.remove_constraint_from_object(dof,'COPY_LOCATION')
		objs = dof.constraints.new(type='COPY_LOCATION')
		objs.target = frame
		objs.use_x=False
		objs.use_y=False
		objs.use_z=False
		
		monkey_name="Monkey"
		
		util_helper.remove_object_by_name("Suzanne")
		util_helper.remove_object_by_name("Suzanne.001")
		util_helper.remove_object_by_name("Suzanne.002")
		
		
		util_helper.remove_object_by_name(monkey_name)
		bpy.ops.mesh.primitive_monkey_add(radius=0.5, location=(dof.location.x,dof.location.y,dof.location.z))
		monkey=bpy.context.active_object
		monkey.rotation_euler[0] = 1.0821
		monkey.rotation_euler[1] = 0
		monkey.rotation_euler[2] = 0

