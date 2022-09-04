import os
import shutil
directory = "."

def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

step_size=85
steps=4
last_frame=step_size*steps

cwd=os.getcwd()



for filename in os.listdir(directory):
	basename, ext = os.path.splitext(filename)
	parts=basename.split(".")
	#print(parts)
	#print("file: %s ext %s"%(basename,ext))
	if ext != '.exr':
		continue
	try:
		number = int(parts[1])

	except ValueError:
		#print("not numeric")
		continue  # not numeric

	num_range=range(0,last_frame)
	for seq in range(0,steps):
		first_frame=(seq*step_size)+1
		last_frame=(seq+1)*step_size+1
		#print("Seq: %d (%d-%d)"%(seq,first_frame,last_frame))

		if first_frame <= number <= last_frame:
			# process file
			filename = os.path.join(directory, filename)
			print("seq: %d  = %s"%(seq,filename))

			target_dir="%s/%d/"%(cwd,seq)
			ensure_dir(target_dir)

			src_file="%s/%s%s"%(cwd,basename,ext)
			target_file="%s/%d/%s%s"%(cwd,seq,basename,ext)
			#print(target_file)

			print("src: %s target %s"%(src_file,target_file))
			#shutil.copyfile(filename,target_file)
			os.symlink(src_file,target_file)