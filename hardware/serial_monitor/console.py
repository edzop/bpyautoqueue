# sudo apt install python3-pip
# sudo pip3 install pyserial

import serial
import time
from datetime import datetime
import subprocess
from subprocess import check_output
import psutil

SerialObj = serial.Serial('/dev/ttyUSB0',baudrate=115200)



print(SerialObj) #display default parameters

time.sleep(3)   # Only needed for Arduino,For AVR/PIC/MSP430 & other Micros not needed
				# opening the serial port from Python will reset the Arduino.
				# Both Arduino and Python code are sharing Com11 here.
				# 3 second delay allows the Arduino to settle down.

SerialObj.baudrate = 115200  # set Baud rate to 9600
SerialObj.bytesize = 8     # Number of data bits = 8
SerialObj.parity   ='N'    # No parity
SerialObj.stopbits = 1     # Number of Stop bits = 1


print("hello console")
print('\nStatus -> ',SerialObj)


val = 0

sequence=0
target_line=0

try:

	while True:
	
		time.sleep(2)
	
		now = datetime.now()

		text=""

		if sequence==0:    
			# dd/mm/YY H:M:S
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
			#print("date and time =", dt_string)	
			text=dt_string
		elif sequence==1:

			#out = check_output(["blq", "--superbrief"])

			p = subprocess.run(["blq", "--superbrief"], capture_output=True, text=True)
			return_text=p.stdout
			return_code=p.returncode
			#print("Return Code: %d text: %s"%(return_code,return_text))
			text=return_text

		elif sequence==2:
			text="counter %d"%val
		elif sequence==3:
			text="%s c"%(psutil.sensors_temperatures()['coretemp'][0].current)
		elif sequence==4:
			text="Yo"


		sequence=sequence+1


		if sequence>4:
			sequence=0

		target_line=target_line+1
		if target_line>3:
			target_line=0

		if len(text) > 0:
				
			print("Sending: %s"%text)
			utf8_text=bytearray("%d:%s"%(target_line,text),"utf8")
			byteswritten=SerialObj.write(utf8_text);
			print("wrote: %d bytes"%byteswritten)
			val+=1

		if SerialObj.inWaiting():
			line=SerialObj.readline()
		#if line.length()>0:
			print(line)
			
except KeyboardInterrupt:
	pass     
		
	
print("closing serial...")
SerialObj.close()    