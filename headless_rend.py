import bpy
import os
import sys

from bpyautoqueue import rend_helper
from bpyautoqueue import camera_dolly_helper
from bpyautoqueue import render_db
from bpyautoqueue import auto_camera_pan


class headless_renderer:

	target_renderer=None
	theDB=None

	filename=None
	outputX=None
	outputY=None
	frameIndex=None
	jobID=None
	autopanstep=None
	moviemode=None
	cameraID=0
	sceneID=0

	frames_rendered=0


	def __init__(self):

		self.theDB = render_db.render_db()

	def get_next_renderjob(self):

		self.jobID=None

		renderjob = self.theDB.get_next_in_queue()

		if len(renderjob)==0:
			print("no files in queue - exiting")
			return

		self.filename = renderjob[0]
		self.outputX=renderjob[1]
		self.outputY=renderjob[2]
		self.frameIndex = renderjob[3]
		self.jobID = renderjob[4]
		self.target_renderer = renderjob[5]
		self.autopanstep = renderjob[6]
		self.moviemode = renderjob[7]
		self.cameraID=renderjob[8]

		
	def setup_render(self):

		try:

			if self.moviemode>0:
				self.useStamp=False
				self.isolate_files_into_directories=True
			else:
				self.useStamp=True
				self.isolate_files_into_directories=False

			#bpy.context.scene.render.engine = self.target_renderer.upper()
			
			self.theRendHelper = rend_helper.Rend_Helper(self.isolate_files_into_directories,self.autopanstep)

			self.theRendHelper.setup_resolution(self.outputX,self.outputY,100);
			self.theRendHelper.use_stamp = self.useStamp

			self.theRendHelper.setup_render_settings();

			if self.autopanstep>0:
				thePanHelper = auto_camera_pan.Cam_Pan_Helper()
				thePanHelper.setup_auto_pan(self.autopanstep)

			self.theRendHelper.setup_lighting();

			if self.autopanstep>0:
				theDolly = camera_dolly_helper.camera_dolly_helper()
				theDolly.adjust_lights_for_camera(self.autopanstep,thePanHelper.scenecount)

		except Exception as e:
			print("Setup Render Failed: %s"%(e))
			self.theDB.mark_item_failed(self.jobID)



	def do_render(self):

		result=False

		try:			

			print("Rendering frame:%d (%dx%d) step: %d scene: %d camera: %d renderer:%s file:%s" %(
				self.frameIndex,
				self.outputX,
				self.outputY,
				self.autopanstep,
				self.sceneID,
				self.cameraID,
				self.target_renderer,
				self.filename))

			#sys.stdout.flush()	

			if self.theRendHelper.do_render(self.frameIndex,self.cameraID,self.sceneID)==True:
				self.theDB.mark_item_finished(self.jobID,self.theRendHelper.last_frame_time,self.theRendHelper.get_samples())
				self.frames_rendered+=1
				result=True
			else:
				self.theDB.mark_item_failed(self.jobID)

		except Exception as e:
			print("Render Failed: %s"%(e))
			self.theDB.mark_item_failed(self.jobID)

		return result


the_headless_renderer=headless_renderer()

the_headless_renderer.get_next_renderjob()

frames_rendered=0

while the_headless_renderer.jobID!=None:

	# only need to setup once per file (first frame)
	if the_headless_renderer.frames_rendered==0:
		the_headless_renderer.setup_render()

	the_headless_renderer.do_render()

	print("Rendered: %d frames %s"%(the_headless_renderer.frames_rendered,the_headless_renderer.filename))

	last_filename=the_headless_renderer.filename
	last_autopanstep=the_headless_renderer.autopanstep
	last_jobID=the_headless_renderer.jobID

	the_headless_renderer.get_next_renderjob()

		

	# the objective is to reuse the open blender file for speed... if there are more frames left for this same file
	# we should render them together in this same session... it's faster than reloading the blend file each time for each frame
	if last_filename!=the_headless_renderer.filename or last_autopanstep!=the_headless_renderer.autopanstep:
		the_headless_renderer.jobID=None

