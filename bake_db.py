
import sys, getopt
import sqlite3
from datetime import date, datetime
import glob
import os
import subprocess
import functools
import resource

this_script_file_path=os.path.dirname(os.path.abspath(__file__))

def human_readable_size(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"



class bake_db:

	verbose=False

	databasefile = ""

	code_none=0
	code_queued=1
	code_finished=2
	code_processing=3

	code_bake_op_bake=1
	code_bake_op_setup_draft=2
	code_bake_op_setup_final=3
	code_bake_op_clean=4
	code_bake_op_update_materials=5
	code_dump_frames=6
	code_set_frames=7
	code_bake_op_setup_highres=8
 

	code_bake_engine_blender=0
	code_bake_engine_flip_fluids=1

	bake_engine=code_bake_engine_blender

	code_convert_to_flip=10

	def __init__(self):
		self.databasefile="%s/bake_db.sqlite3"%(this_script_file_path)
		self.openDB()
		self.create_tables()

	def openDB(self):
		print("Opening database: %s"%self.databasefile)
		self.conn = sqlite3.connect(self.databasefile)

	def create_tables(self):

		self.conn.execute('''CREATE TABLE IF NOT EXISTS results
			 (resultID INTEGER PRIMARY KEY AUTOINCREMENT, finishdate timestamp, filename text,baketime int, frames int, resolution int,domain_size text,cachesize text,memused int,bake_engine int)''')
				 
		self.conn.execute('''CREATE TABLE IF NOT EXISTS bakes
			 (jobID INTEGER PRIMARY KEY AUTOINCREMENT, syncdate timestamp, filename text,status int default 0,bake_engine int default 0)''')

	def get_next_in_queue(self,mark_processing):

		nextbake = []
	
		c=self.conn.execute("SELECT filename,jobID " \
			"FROM bakes WHERE (status=%d) ORDER BY filename LIMIT 1"%(self.code_queued))
			
		for row in c:

			jobID=row[1]
			filename=row[0]

			nextbake.append(filename)
			nextbake.append(jobID)

			if mark_processing:
				cursor = self.conn.cursor()
				cursor.execute("UPDATE bakes SET status = ? WHERE jobID = ?",
				(self.code_processing,jobID))
				self.conn.commit()

			
		if len(nextbake)==0:
			print("#### no jobs found in queue ####")
				
		return nextbake

	def clear_file_from_queue(self,filename):
		if self.verbose:
			print("clearing database")
		cursor = self.conn.cursor()
		sqltext='''DELETE FROM bakes where filename="%s"'''%filename
		
		cursor.execute(sqltext)
		self.conn.commit()


	def clear_results(self):
		print("clearing resuts")
		cursor = self.conn.cursor()
		cursor.execute('''DELETE FROM results''')
		self.conn.commit()

	def clear_database(self):
		print("clearing database")
		cursor = self.conn.cursor()
		cursor.execute('''DELETE FROM bakes''')
		self.conn.commit()


	def bake_engine_to_text(self,engine_type):
		if engine_type==self.code_bake_engine_blender:
			return "blender"
		elif engine_type==self.code_bake_engine_flip_fluids:
			return "flip"

	def statuscode_to_text(self,status):

		if status==self.code_processing:
			return "Processing"
		elif status==self.code_finished:
			return "Finished"
		elif status==self.code_queued:
			return "Queued"

		return "unknown"


	def update_bake_result_last_memory_record(self,memused):
		query_text="UPDATE results set memused=%d where resultID=(SELECT MAX(resultID) FROM results)"%(memused)
		self.conn.execute(query_text)

		self.conn.commit()


	def log_result(self,filename,baketime,frames,resolution,domain_size,cache_size,bake_engine):
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
		self.conn.executemany("INSERT INTO results(finishdate,filename,baketime,frames,resolution,domain_size,cachesize,bake_engine)" \
		" VALUES(?,?,?,?,?,?,?,?)",[(timestamp,filename,baketime,frames,resolution,domain_size,cache_size,bake_engine)])
			
		self.conn.commit()
		
		return True



	def do_print_results(self,filename=None,status_code=code_none):
		print("================== Results =================")

		fileselect=''

		if filename!=None:
			fileselect = ' where filename=\"%s\"'%filename

		query_text="SELECT finishdate, filename,baketime,frames,resolution,domain_size,cachesize,memused,bake_engine FROM results%s"%fileselect

		c=self.conn.execute(query_text)
		for row in c:
			bakeSeconds=row[2]

			m, s = divmod(bakeSeconds, 60)
			h, m = divmod(m, 60)

			timeStr='{:02.0f}:{:02.0f}:{:02.0f}'.format(h, m, s)

			memory_used=row[7]
			memory_used*=1024

			human_readable_mem_used=human_readable_size(memory_used)

			#print(row[0])
			print('{0} baketime: {2}, engine: {8} frames: {3}, resolution: {4}, domain: ({5}), cache: {6}, memusage: {7} filename: {1} '
				.format(row[0], row[1],timeStr,row[3],row[4],row[5],row[6],human_readable_mem_used,self.bake_engine_to_text(row[8])))



	def do_printDB(self,filename=None,status_code=code_none):
		print("================== BakeDB =================")
			
		count_finished=0
		count_queued=0
		count_processing=0

		fileselect=''
		codeselect=''

		if filename!=None:
			fileselect = ' where filename="%s"'%filename

		if status_code!=self.code_none:
			codeselect = ' where status="%d"'%status_code

		query_text='''SELECT jobID, filename,status,bake_engine FROM bakes%s%s'''%(fileselect,codeselect)
		
		c=self.conn.execute(query_text)
		for row in c:
			print('#{0} status: {2} engine: {3} file: {1}'.format(row[0], 
				row[1],
				self.statuscode_to_text(row[2]),
				self.bake_engine_to_text(row[3])))
		#	print(row)
		
			if row[2]==self.code_queued:
				count_queued=count_queued+1
			elif row[2]==self.code_finished:
				count_finished=count_finished+1
			elif row[2]==self.code_processing:
				count_processing=count_processing+1


		print("Finished Count: %d"%(count_finished))
		print("Queued Count: %d"%(count_queued))
		print("Processing Count: %d"%(count_processing))
		
		count_total = count_finished+count_queued+count_processing
		print("Total count: %d"%(count_total))
		
		
	def closeDB(self):
		self.conn.close()

	def do_briefDB(self):
		c=self.conn.execute('''select count(jobID),status from bakes group by status''')

		for row in c:
#			status=row[1]
			count=row[0]
			status=row[1]

			statustext=self.statuscode_to_text(status)

			print("{1}: {0}".format(count,statustext))

	def do_bake(self,mark_processing,bake_op):
		doContinue=True

		while doContinue:
			nextbake=self.get_next_in_queue(mark_processing)

			if len(nextbake)==0:
				doContinue=False
			else:
				filename=nextbake[0]
				jobID=nextbake[1]
				print("Processing: #%d %s"%(jobID,filename))

				# /usr/bin/time -f '%M'

				if os.path.isfile(filename):

					args=["blender"]
					args.append("-b")
					args.append(filename)
					args.append("-P")
					args.append("%s/bake_fluids.py"%(this_script_file_path))
					args.append("--")
					args.append(str(jobID))
					args.append(str(bake_op))
					#print(args)

					proc = subprocess.Popen(args,
							 stdout=subprocess.PIPE,
							 encoding='utf-8')
	 
					while True:
						realtime_output = proc.stdout.readline()

						if realtime_output == '' and proc.poll() is not None:
							break

						if realtime_output:
							print(realtime_output.strip(), flush=True)

					#proc.wait()

					return_code = proc.returncode
					
					memory_used=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

					print("Return Code: %d Memory: %s"%(return_code,human_readable_size(memory_used)))

					if return_code==0:
						self.update_bake_result_last_memory_record(memory_used)


					try:
						while True:
							line = proc.stdout.readline()
							if not line:
								break

							print(line.decode(),end="")
							

					except BrokenPipeError:
						pass
					except KeyboardInterrupt:
						exit(0)
				else:
					print("file '%s' not found in path"%filename)

					#out=subprocess.check_output(args)
					#print(out)

	def get_bake_engine_by_jobID(self,jobID):
		cursor = self.conn.cursor()
		cursor.execute("SELECT bake_engine from bakes where jobID=?",(jobID,))
		data=cursor.fetchone()[0]
		cursor.close()
		
		return data

	def blend_exists(self,filename):
		cursor = self.conn.cursor()
		cursor.execute("SELECT count(*) from bakes where filename=? and bake_engine=?",(filename,self.bake_engine,))
		data=cursor.fetchone()[0]
		if data==0:
			return False
		else:
			return True


	def load_and_convert_flip(self,filename):
		if os.path.isfile(filename):

			args=["blender"]
			args.append("-b")
			args.append(filename)
			args.append("-P")
			args.append("%s/bake_fluids.py"%(this_script_file_path))
			args.append("--")
			args.append(str(0))
			args.append(str(self.code_convert_to_flip))
			#print(args)

			proc = subprocess.Popen(args,stdout=subprocess.PIPE)

			proc.wait()

			return_code = proc.returncode
			
			memory_used=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

			print("Return Code: %d Memory: %s"%(return_code,human_readable_size(memory_used)))

			try:
				while True:
					line = proc.stdout.readline()
					if not line:
						break

					print(line.decode(),end="")
					

			except BrokenPipeError:
				pass
			except KeyboardInterrupt:
				exit(0)
		else:
			print("file '%s' not found in path"%filename)


	def convertflip(self,path):

		if os.path.isfile(path):
			if self.blend_exists(path)==False:
				print("Found: %s"%path)
				self.load_and_convert_flip(path)
		else:
			fq_path = "%s*.blend" % path
			
			print("Searching %s" % fq_path)

			for f in glob.glob(fq_path):
				print(f)
				if self.blend_exists(f)==False:
					self.load_and_convert_flip(f)
				print("Found: %s"%f)


	def iterate_blend_files(self,path):

		if os.path.isfile(path):
			if self.blend_exists(path)==False:
				print("Found: %s"%path)
				self.insert_file(path)
		else:
			fq_path = "%s*.blend" % path
			
			print("Searching %s" % fq_path)

			for f in glob.glob(fq_path):
				print(f)
				if self.blend_exists(f)==False:
					self.insert_file(f)
				print("Found: %s"%f)


	def insert_file(self,filename):
		timestamp = datetime.now()
		#hashval = self.make_hash(filename)	
		self.conn.executemany("INSERT INTO bakes(syncdate,filename,status,bake_engine)" \
		" VALUES(?,?,?,?)",[(timestamp,filename,self.code_queued,self.bake_engine)])
			
		self.conn.commit()
		
		return True

	def requeue_failed_jobs(self):

		cursor = self.conn.cursor()
		cursor.execute("UPDATE bakes SET status = ? WHERE status = ?",
			(self.code_queued,self.code_processing))
		self.conn.commit()


	def update_job_set_status(self,jobID,new_status):
		print("update job Status: %s Job ID: %s"%(new_status,jobID))
		cursor = self.conn.cursor()
		cursor.execute("UPDATE bakes SET status = ? where jobID = ?",
			(new_status,jobID,))
		self.conn.commit()


	def update_all_jobs_set_status(self,new_status):
		cursor = self.conn.cursor()
		cursor.execute("UPDATE bakes SET status = ?",
			(new_status,))
		self.conn.commit()

	def remove_file_from_queue(self,filename):

		cursor = self.conn.cursor()
		cursor.execute("DELETE FROM bakes WHERE filename like ?",('%'+filename+'%',))
		self.conn.commit()


	def update_jobs_mark_file_queued(self,filename):
		
		cursor = self.conn.cursor()

		print(filename)
	
		cursor.execute("UPDATE bakes SET status = ? WHERE filename like ?",
			(self.code_queued,'%'+filename+'%'))

		self.conn.commit()


def main(argv):
	
	theDB = None

	try:
		opts, args = getopt.getopt(argv,"hpbr",[
				"print",
				"clearjobs",
				"clearresults",
				"bake",
				"brief",
				"results",
				"setupdraft",
				"setupfinal",
				"setuphighres",
				"updatematerials", 
				"convertflip=",
				"clean",
				"engineflip",
				"engineblender",
				"dumpframes",
				"requeueall","markallfinished","requeuefailed",
				"searchpath=",
				"removefile=",
				"help"])

	except getopt.GetoptError as err:
		print("Error: %s"%err)
		print('bake_db.py --help')
		sys.exit(2)

	theDB=bake_db()

	for opt, arg in opts:

		if opt=="-p":
			theDB.do_printDB()
		elif opt=="--bake":
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_bake)
		elif opt in ("--setupdraft"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_setup_draft) 
		elif opt in ("--setupfinal"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_setup_final) 
		elif opt in ("--setuphighres"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_setup_highres) 
		elif opt in ("--clean"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_clean) 
		elif opt in ("-r","--results"):
			theDB.do_print_results()
		elif opt=="--searchpath":
			theDB.iterate_blend_files(arg)
		elif opt=="--convertflip":
			theDB.convertflip(arg)
		elif opt in ("--requeueall"):
			theDB.update_all_jobs_set_status(theDB.code_queued)
		elif opt in ("--markallfinished"):
			theDB.update_all_jobs_set_status(theDB.code_finished)
		elif opt in ("--requeuefailed"):
			theDB.requeue_failed_jobs()
		elif opt in ("--removefile"):
			theDB.remove_file_from_queue(arg)
		elif opt in ("-b","--brief"):
			theDB.do_briefDB()
		elif opt in ("--clearresults"):
			theDB.clear_results()
		elif opt in ("--dumpframes"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_dump_frames) 
		elif opt in ("--setframes"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_set_frames) 
		elif opt in ("--clearjobs"):
			theDB.clear_database()
		elif opt in ("--engineflip"):
			theDB.bake_engine=bake_db.code_bake_engine_flip_fluids
		elif opt in ("--engineblender"):	
			theDB.bake_engine=bake_db.code_bake_engine_blender
		elif opt in ("--updatematerials"):
			theDB.do_bake(mark_processing=True,bake_op=theDB.code_bake_op_update_materials) 
		elif opt in ("-h","--help"):
			print("====================================")
			print("-p --print\t\t| print all files")
			print("-b --brief\t\t| brief summary of DB")
			print("--dumpframes\t\t dump number of frames for each file")
			print("--bake\t\t| bake remaining files in queue")
			print("--setupdraft\t\t| setup draft settings")
			print("--engineflip\t\t| use flip fluid bake engine")
			print("--engineblender\t\t| use blender bake engine (default)")
			print("--setupfinal\t\t| setup final settings")
			print("--setuphighres\t\t| setup highres settings")
			print("--clean\t\t| clean particles")
			print("--convertflip\t\t| convert from blender fluid to flip fluids")
			print("--clearresults\t\t| delete all bake results")
			print("--results -r\t\tPrint bake results")
			print("-s --searchpath\t\t| add files to DB")
			print("--clearjobs\t\t\t| clear DB")
			print("--markallfinished\t| mark all files as finished")
			print("--requeueall\t\t| requeue all jobs")
			print("--requeuefailed\t\t| requeue processing jobs (sometimes they get stuck)")
			print("--updatematerials\t\t| update fluid related materials")

	if theDB!=None:
		theDB.closeDB()


if __name__ == "__main__":
	main(sys.argv[1:])
