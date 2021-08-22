#fake_utility.py, just generates lots of output over time
import time
import sys
i = 0
while True:
   print("%d"%i)
   sys.stdout.flush()
   i += 1
   time.sleep(0.5)
   if i>10:
       break

