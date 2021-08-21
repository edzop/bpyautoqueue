#!/usr/bin/python

import sys, getopt
import sqlite3
from datetime import date, datetime
import hashlib
import glob
import os
import subprocess


#this_script_file_path = os.path.realpath(__file__)

#import pathlib
#this_script_file_path=pathlib.Path(__file__).parent.resolve()

this_script_file_path=os.path.dirname(os.path.abspath(__file__))



class render_db:
	
	databasefile = ""
	conn=0
	verbose=False
	
	code_none=0
	code_queued=1
	code_finished=2
	code_failed=3
	
#	render_engine_cycles=1
#	render_engine_lux=2
	
	selected_render_engine="CYCLES"
	
	outputX=480
	outputY=270
	anim_mode="anim"
	autopanstep=1
	moviemode=0
	IgnoreHashVal=False
	
#	target_job_ID=0
	 
	def __init__(self):
		self.databasefile="%s/render_db.db"%(this_script_file_path)
		#self.databasefile=databasefile

		#self.configure_anim_mode(self.anim_mode)

		self.openDB()
	#theDB.connect
		self.create_tables()

	def configure_anim_mode(self,mode):

		self.anim_mode=mode

		if mode=="pananim":
			self.autopanstep=85
			self.moviemode=1
		elif mode=="pankey":
			self.autopanstep=1
			self.moviemode=0
		elif mode=="anim":
			self.autopanstep=0
			self.moviemode=1
		else:  						# image
			self.autopanstep=0
			self.moviemode=0

		
	def insert_or_update_blend_file(self,filename,frames):
			if self.blend_exists(filename,frames[0]):
				#print("Existing")
				return self.update_file_queued(filename,frames)
			else:
				#print("Insert")
				return self.insert_file(filename,frames)		

	def render_db(self):
		print("render")

		next_rend = self.get_next_in_queue()

		if len(next_rend)>0:
			args=["blender"]
			args.append("-b")
			args.append(next_rend[0])
			args.append("-P")
			#self.databasefile="%s/render_db.db"%(this_script_file_path)
			args.append("%s/headless_rend.py"%(this_script_file_path))

			out=subprocess.check_output(args)
			print(out)
		
	def iterate_blend_files(self,path):

		#import add_helper
		
		
		if os.path.isfile(path):
			args=["blender"]
			args.append("-b")
			args.append(path)
			args.append("-P")
			args.append("add_helper.py")
			args.append("--")
			args.append(self.selected_render_engine)
			args.append(self.anim_mode)
			#args.append(str(self.autopanstep))
			
			#print(args)
			#subprocess.Popen(args,stdout = subprocess.PIPE, stderr = subprocess.PIPE)

			out=subprocess.check_output(args)
			print(out)
			#self.insert_or_update_blend_file(path,[1])
		else:
			fq_path = "%s/*.blend" % path
			
			print("Searching %s" % fq_path)

			for f in glob.glob(fq_path):
				self.insert_or_update_blend_file(f,1)
				print("Found: %s"%f)

	def insert_file(self,filename,frames):
		timestamp = datetime.now()
		hashval = self.make_hash(filename)

		records = []

		for i in frames:
			records.append((	timestamp, \
				filename, \
				hashval, \
				self.autopanstep, \
				self.outputX, \
				self.outputY, \
				i, \
				self.code_queued, \
				self.selected_render_engine,
				self.moviemode))
		
		self.conn.executemany("INSERT INTO blendfiles(syncdate,filename,hashval," \
		"autopanstep,outputX,outputY,frameIndex,status,renderengine,moviemode) VALUES(?,?,?,?,?,?,?,?,?,?)",
		records)
			
		self.conn.commit()
		
		return True

	def change_resolution(self,filename=None):
		cursor = self.conn.cursor()

		if filename==None:
			cursor.execute("UPDATE blendfiles SET outputX=?, outputY=? WHERE renderengine = ?",
				(self.outputX,self.outputY,self.selected_render_engine))
		else:
			cursor.execute("UPDATE blendfiles SET outputX=?, outputY=? WHERE filename=?",
				(self.outputX,self.outputY,filename))
		self.conn.commit()


	def requeue_failed_jobs(self):
	
		cursor = self.conn.cursor()
		cursor.execute("UPDATE blendfiles SET status = ? WHERE status = ?",
			(self.code_queued,self.code_failed))
		self.conn.commit()

	def update_all_jobs_set_status(self,new_status):
		cursor = self.conn.cursor()
		cursor.execute("UPDATE blendfiles SET status = ? WHERE renderengine = ?",
			(new_status,self.selected_render_engine))
		self.conn.commit()

	def remove_file_from_queue(self,filename):

		cursor = self.conn.cursor()
		cursor.execute("DELETE FROM blendfiles WHERE filename like ?",('%'+filename+'%',))
		self.conn.commit()

	def update_jobs_mark_file_queued(self,filename,framenumber):

		cursor = self.conn.cursor()

		print(filename)

		if framenumber==0:	
			cursor.execute("UPDATE blendfiles SET status = ? WHERE filename like ?",
				(self.code_queued,'%'+filename+'%'))
		else:
			cursor.execute("UPDATE blendfiles SET status = ? WHERE filename = ? AND frameIndex = ?",
				(self.code_queued,filename,framenumber))

		self.conn.commit()

	# skips hash checking 
	def update_file_queued(self,filename,frames):
		
		records = []

		for i in frames:
			records.append((	
				self.code_queued, \
				filename, \
				self.selected_render_engine,
				i))
		
		cursor = self.conn.cursor()
		cursor.executemany("UPDATE blendfiles SET status = ? " \
			"WHERE filename = ? AND renderengine = ? AND frameIndex = ?",records)
		self.conn.commit()	
					
		return True
		
	# checks hash val to see if file changed
	def update_file_queued_check(self,filename,frameIndex):
		
		file_updated=False
		
		latest_hashval = self.make_hash(filename)
		timestamp = datetime.now()

		print("\n Checking frame:%d"%(frameIndex))
		
		c=self.conn.execute("SELECT filename,hashval FROM blendfiles " \
				"WHERE (filename='%s' AND renderengine='%s' AND frameIndex=%d) " \
				"LIMIT 1"%(filename,self.selected_render_engine,frameIndex))
			
		for row in c:
			old_hash_val=row[1]
			
			if self.IgnoreHashVal==False:
				print("\r\n %s = %s"%(old_hash_val,latest_hashval))
			
			if (old_hash_val!=latest_hashval) or (self.IgnoreHashVal==True):
		
				cursor = self.conn.cursor()
				cursor.execute("UPDATE blendfiles SET hashval = ?, syncdate = ?, status = ? " \
					"WHERE filename = ? AND renderengine = ? AND frameIndex = ?",
					(latest_hashval, timestamp,self.code_queued, \
					filename,self.selected_render_engine,frameIndex))
				self.conn.commit()
				
				if self.IgnoreHashVal:
					print("Updated frame")
				else:
					print("Updated because hashval changed")
					
				file_updated=True
			else:
				print("Skipping duplicate hashval")
					
		return file_updated
				
		
	def mark_item_finished(self,jobID):
		cursor = self.conn.cursor()
		cursor.execute('''UPDATE blendfiles SET status =? WHERE jobID = ? ''',
			(self.code_finished,jobID))
		self.conn.commit()
		
		
	def mark_item_failed(self,jobID):
			
		cursor = self.conn.cursor()
		cursor.execute('''UPDATE blendfiles SET status =? WHERE jobID = ? ''',
			(self.code_failed,jobID))
		self.conn.commit()		
		
	def blend_exists(self,filename,frameIndex):
		cursor = self.conn.cursor()
		cursor.execute("SELECT count(*) from blendfiles where filename=? AND renderengine=? and frameIndex=?",(filename,self.selected_render_engine,frameIndex))
		data=cursor.fetchone()[0]
		if data==0:
			return False
		else:
			return True
			
		
	def make_hash(self,filename, blocksize=65536):
		
		hash = hashlib.md5()
		with open(filename, "rb") as f:
			for block in iter(lambda: f.read(blocksize), b""):
				hash.update(block)
				
		hashval=hash.hexdigest()
		#print("\r\nFilename: %s hashval: %s"%(filename,hashval))
		return hashval

	def clear_file_from_queue(self,filename):
		if self.verbose:
			print("clearing database")
		cursor = self.conn.cursor()
		sqltext='''DELETE FROM blendfiles where filename="%s"'''%filename
		
		cursor.execute(sqltext)
		self.conn.commit()
          
	
	def clear_database(self):
		if self.verbose:
			print("clearing database")
		cursor = self.conn.cursor()
		cursor.execute('''DELETE FROM blendfiles''')
		self.conn.commit()
		
	def openDB(self):
		print("Opening database: %s"%self.databasefile)
		self.conn = sqlite3.connect(self.databasefile)

		
	def create_tables(self):
		# Create table
		self.conn.execute('''CREATE TABLE IF NOT EXISTS blendfiles
             (jobID INTEGER PRIMARY KEY AUTOINCREMENT, syncdate timestamp, filename text,hashval text, outputX int, outputY int,frameIndex int,status int default 0,renderengine text,autopanstep int, moviemode int default 0)''')
                  

	def get_next_in_queue(self):

		nextrend = []
#		print("ss=%d AND ff=%d"%(self.code_queued,self.code_finished))
		
		c=self.conn.execute("SELECT filename,outputX,outputY,frameIndex,jobID,renderengine,autopanstep,moviemode " \
			"FROM blendfiles WHERE (status=%d AND renderengine='%s') ORDER BY filename LIMIT 1"%(self.code_queued,self.selected_render_engine))
			
		for row in c:
			print("%s"%(row[0]))
			nextrend.append(row[0])
			nextrend.append(row[1])
			nextrend.append(row[2])
			nextrend.append(row[3])
			nextrend.append(row[4])
			nextrend.append(row[5])
			nextrend.append(row[6])
			nextrend.append(row[7])
			
		if len(nextrend)==0:
			print("0")
				
		return nextrend
			
		#sys.exit(5)

	def statuscode_to_text(self,status):

		if status==self.code_failed:
			return "Failed"
		elif status==self.code_finished:
			return "Finished"
		elif status==self.code_queued:
			return "Queued"

		return "unknown"


	def do_briefDB(self):
		c=self.conn.execute('''select count(jobID),status,renderengine from blendfiles group by status,renderengine''')

		for row in c:
#			status=row[1]
			count=row[0]
			engine=row[2]

			statustext=self.statuscode_to_text(row[1])

			print("{2}: {0} {1}".format(statustext,count,engine))


	def do_printDB(self,filename=None,status_code=code_none):
		if self.verbose:
			print("Printing Database:")
			
		count_finished=0
		count_queued=0
		count_failed=0

		fileselect=''
		codeselect=''

		if filename!=None:
			fileselect = ' where filename="%s"'%filename

		if status_code!=self.code_none:
			codeselect = ' where status="%d"'%status_code

		query_text='''SELECT jobID, frameIndex, outputX,outputY, filename,status,renderengine,autopanstep,moviemode FROM blendfiles%s%s'''%(fileselect,codeselect)
		
		c=self.conn.execute(query_text)
		for row in c:
			print('{0} {1}x{2} f:{3} pan:{7} movie:{8} {5}\t\t{6}\t{4}	'.format(row[0], row[2],row[3], row[1],row[4],self.statuscode_to_text(row[5]),row[6],row[7],row[8]))
		#	print(row)
		
			if row[5]==self.code_queued:
				count_queued=count_queued+1
			elif row[5]==self.code_finished:
				count_finished=count_finished+1
			elif row[5]==self.code_failed:
				count_failed=count_failed+1


		print("Finished Count: %d"%(count_finished))
		print("Queued Count: %d"%(count_queued))
		print("Failed Count: %d"%(count_failed))
		
		count_total = count_finished+count_queued+count_failed
		print("Total count: %d"%(count_total))
		
		
	def closeDB(self):
		self.conn.close()



def main(argv):
	
	theDB = None
	
	frameIndex=0
	
	try:
		opts, args = getopt.getopt(argv,"vpbs:e:d:m:i:",[
				"markallfinished",
				"printqueued",
				"printfailed",
				"requeueall",
				"requeuefailed",
				"print",
				"render",
				"brief",
				"clear",
				"mode",
				"queue",
				"quartersize",
				"halfsize",
				"fullsize",
				"2ksize",
				"help",
				"dfile=","searchpath=","resolution=","requeuefile=","removefile="])
	except getopt.GetoptError as err:
		print("Error: %s"%err)
		print('render_db.py --help')
		sys.exit(2)


	#for opt, arg in opts:
	#	if opt in ("-d", "--dfile"):
	
	theDB=render_db()


	#if theDB==None:
	#	print("need to set database first! (-d option)")
	#	return

	for opt, arg in opts:	
		if opt in ("-e"):
			theDB.selected_render_engine=arg.upper()
		elif opt in ("-m","--mode"):
			theDB.configure_anim_mode(arg.lower())
		elif opt in ("-v","--verbose"):
			print("verbose")
			theDB.verbose=True
		elif opt in ("-i"):
			frameIndex=arg

	for opt, arg in opts:
		if opt in ("--halfsize"):
			theDB.outputX, theDB.outputY=960,540
			theDB.change_resolution()
		elif opt in ("--fullsize"):
			theDB.outputX,theDB.outputY=1920,1080
			theDB.change_resolution()
		elif opt in ("--quartersize"):
			theDB.outputX,theDB.outputY=480,270
			theDB.change_resolution()
		elif opt in ("--2ksize"):
			theDB.outputX,theDB.outputY=2560,1440
			theDB.change_resolution()
		elif opt in ("--clear"):
			theDB.clear_database()
		elif opt in ("--render"):
			theDB.render_db()
		elif opt in ("-p","--print"):
			theDB.do_printDB()
		elif opt in ("--printqueued"):
			theDB.do_printDB(None,theDB.code_queued)
		elif opt in ("--printfailed"):
			theDB.do_printDB(None,theDB.code_failed)
		elif opt in ("-b","--brief"):
			theDB.do_briefDB()
		elif opt in ("--queue"):
			theDB.get_next_in_queue()
#		elif opt in ("-k"):
#			theDB.change_resolution()
		elif opt in ("--requeueall"):
			theDB.update_all_jobs_set_status(theDB.code_queued)
		elif opt in ("--markallfinished"):
			theDB.update_all_jobs_set_status(theDB.code_finished)
		elif opt in ("--requeuefailed"):
			theDB.requeue_failed_jobs()
		elif opt in ("--requeuefile"):
			theDB.update_jobs_mark_file_queued(arg,frameIndex)
		elif opt in ("--removefile"):
			theDB.remove_file_from_queue(arg)
#		elif opt in ("--resolution"):
#			print("change resolution")
#			resX,resY=arg.split("x")
#			theDB.outputX=resX
#			theDB.outputY=resY
		elif opt in ("-s", "--searchpath"):
			theDB.iterate_blend_files(arg)
		elif opt in ("--help"):
			#print('render_db.py -d <databasefile>')
			print("====================================")
			print("--halfsize --fullsize --quartersize --2ksize - resize all renders to preset size")
			print("--clear  - clear DB")
			print("-s --searchpath  - add files to DB")
			print("-i - frame index")
			print("-m mode (anim/pananim/pankey)")
#			print("--resolution specify resolution ex: 200x400")
			print("-e engine: 'CYCLES' or 'LUXCORE'")
#			print("-k change resolution (must be used with -r)")
			print("--requeueall - requeue all jobs")
			print("--requeuefailed - requeue failed jobs")
			print("--requeuefile FILENAME - requeue specific file (searches like wildcard)")
			print("--removefile FILENAME - remove specific file (searches like wildcard)")
			print("--markallfinished - mark all files as finished")
			print("-p --print  - print all files")
			print("--render render files in queue")
			print("--printqueued - print queued files")
			print("--printfailed - print failed files")
			print("-b --brief  - brief summary of DB")
#			print("-j jobID")
			sys.exit(1)

	if theDB!=None:
		theDB.closeDB()

if __name__ == "__main__":
	main(sys.argv[1:])
