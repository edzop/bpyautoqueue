#filters output
import subprocess
proc = subprocess.Popen(['python','fake.py'],stdout=subprocess.PIPE)
while True:
  line = proc.stdout.readline()
  if not line:
    break
  #the real code does filtering here
  print("test:", line.rstrip())