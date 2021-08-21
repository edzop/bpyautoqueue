import bpy
import sys
import os.path
import os
import time
import functools
import glob
import hashlib

from . import util_helper

#util_helper 	= imp.load_source('util_helper','/home/blender/scripts/util_helper.py')


class Logger:

	def get_progress(self):
# hack master accumulative_time from accumulative_time

		#					if frame_start_field!=-1:
#		self.frame_start = get_progress_setting(int(lastdata[frame_start_field])+1
#						print("resuming from frame %d" %(self.frame_start))
					
#					if accumulative_field!=-1:	
#						self.accumulative_time = float(lastdata[accumulative_field])
#						print("accumulative_time %s" %(secondsToStr(self.accumulative_time)))
							

#		self.get_progress_setting(self.log_file_name,-1,9)
		
		self.master_accumulative_time 	= float(self.get_progress_setting(self.log_file_name,8))
		
		self.frame_start				= int(self.get_progress_setting(self.status_file_name,0))+1
		self.accumulative_time			= float(self.get_progress_setting(self.status_file_name,2))


	def __init__(self,render_output_path,renderer_name):
		
		
		# To Setup from Parent Object
		#self.output_path="./output"

#		self.render_output_path
	
		#self.stamp_notes = None
		self.stamp_notes = list()
		
		self.status_onetime_data = list()
		self.status_extra_data = list()
		
		
		# Settings from status file
		self.frame_start=0
		self.accumulative_time=0
		self.master_accumulative_time=0
		
		self.log_file_name 		= './render_' + renderer_name + '.log'
		
		self.blendfile_without_extension = util_helper.get_blendfile_without_extension()
		
		self.status_file_name 	= render_output_path + self.blendfile_without_extension + "_" + renderer_name + ".status"
				
		#print("status file: %s" %self.status_file_name);
		#print("Log file: %s" %self.log_file_name);
		
		util_helper.ensure_dir(self.log_file_name);
		util_helper.ensure_dir(self.status_file_name);
		
		self.logfile = open(self.log_file_name, 'a')
		
	def logFail(self,s):
		self.log(self.logfile,s)
		
	def logStatus(self,s):
		self.log(self.logfile,s)
		
		
	def log(self,f,s):
		print(s)
		f.write(s + "\r\n")
		
		f.flush()
		
	def __del__(self):
		
		self.logfile.close()
		
	def add_status_onetime_data(self,data):
		self.status_onetime_data.append(data)
		
	def add_status_extra_data(self,data):
		self.status_extra_data.append(data)
		
		
	def dump_status_onetime_data(self):
	
		statusfile = open(self.status_file_name, 'a')
		
		if self.status_onetime_data!=None:
			if len(self.status_onetime_data)>0:		
				
				for logdata in self.status_onetime_data:										
					self.log(statusfile,"# " + logdata)
				
		statusfile.close()
		
		
	def dump_status_extra_data(self):
	
		statusfile = open(self.status_file_name, 'a')
		
		if self.status_extra_data!=None:
			if len(self.status_extra_data)>0:		
				
				for logdata in self.status_extra_data:										
					self.log(statusfile,"# " + logdata)
				
		statusfile.close()
		
	def update_render_log(self,current_frame,frame_time):
		status_text = '%s frame: %d frame_time: %s model_total: %s master_seconds: %s master_time: %s'%(self.blendfile_without_extension,current_frame,util_helper.secondsToStr(frame_time),util_helper.secondsToStr(self.master_accumulative_time),self.master_accumulative_time,util_helper.secondsToStr(self.master_accumulative_time))
		self.logStatus(status_text)
		
		
	def write_progress(self,current_frame,frame_time):
		# log current frame number for resuming
		statusfile = open(self.status_file_name, 'a')
		self.log(statusfile,'%d %f %f %s' %(current_frame,frame_time,self.accumulative_time,util_helper.secondsToStr(self.accumulative_time)))
		statusfile.close()
    
	def record_session_summary(self):
		self.add_status_extra_data("This Session: %s Accumulative %s" %(util_helper.secondsToStr(self.accumulative_time,
		util_helper.secondsToStr(self.master_accumulative_time))))
    
	def get_progress_setting(self,filename,field_index):
		
		val = 0
		
		# Get last rendered frame from status file if exists
		try:
			if os.path.isfile(filename):
				if os.path.getsize(filename):
					statusfile = open(filename, 'r')
					lastline = util_helper.getLastLine(statusfile)
					
					#print("lastLine: " + lastline)
					
					if(len(lastline)>0):
					
						lastdata = lastline.split(' ')
								
						if field_index<=len(lastdata):
							examine_field = lastdata[field_index].strip()
							
							#print("len OK: " + examine_field)
							
							try:
								val = float(examine_field)
							except ValueError:
								print("error parsing field %d from number from lastdata '%s'"%(field_index,examine_field));
								
							if isinstance(examine_field,int):
								#print("is int")
								val = int(examine_field)								
								
					
					statusfile.close()
				
		except IOError as e:
			print("({})".format(e))
		
		#print(" File:"+filename+" index:"+str(field_index) + " result:"+str(val))
			
		return val
	
	def increment_times(self,frametime):
		self.master_accumulative_time=self.master_accumulative_time+frametime	
		self.accumulative_time=self.accumulative_time+frametime
   		
			
	def appendToExtraStampNotes(self,extra_notes):
		self.stamp_notes.append(extra_notes)
		
		
		
	def log_resolution_info(self):
		width = bpy.context.scene.render.resolution_x
		height = bpy.context.scene.render.resolution_y
		scale = bpy.context.scene.render.resolution_percentage
		
		scaled_width = int(width * scale/100)
		scaled_height = int(height * scale/100)
		
		self.add_status_onetime_data("Resolution: " + str(scaled_width) + "x" + str(scaled_height))
		

