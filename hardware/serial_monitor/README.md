This is an arduino based queue monitor utility current queue status on an SSD1306 OLED display.

The project is platformIO based and uses Arduino Nano + SSD1306 oled display.



============================
[Install PlatformIO Core](https://docs.platformio.org/page/core.html)


To Run: 
python3 console.py

The python code will send the time, files queued and files finished and CPU temp to the arduino which will display on screen. 

I wrote this utility because when I'm rendering a bunch of files I usually turn my screen off and leave the computer alone. I kept going back to check computer and wished I could just glance at a OLED summary display to see the current status. So now we have it. 