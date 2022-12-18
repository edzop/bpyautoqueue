
#include <Arduino.h>

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "led.h"
#include "timer.h"

timer updateTimer;
timer scrollTimer;
timer lastcommTimer;
led statusLED(LED_BUILTIN);

#include "stepper.h"

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library. 
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

stepper scrollStepper(1,SCREEN_WIDTH);

void drawStepper(Adafruit_SSD1306 &display) {
  int box_width=5;
  int box_height=5;
  int box_left=scrollStepper.getValue();
  int last_left=scrollStepper.getLastValue();
  int box_top=SCREEN_HEIGHT-box_height;

  display.drawRect(last_left, box_top, box_width, box_height, SSD1306_BLACK);
  display.drawRect(box_left, box_top, box_width, box_height, SSD1306_WHITE);

  scrollStepper.step();
}

int target_display_line=0;

void setup()
{
  Serial.begin(115200);

  statusLED.setup();
  statusLED.setFlashTiming(200,400);

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 failed"));
    for(;;); // Don't proceed, loop forever
  }

  display.clearDisplay();
    
  display.display();
}

unsigned long counter=0;
#define BUFF_LEN 64
char buff[2][BUFF_LEN];

String teststr;
bool updateDisplay;

void loop()
{

  updateDisplay=false;
  

  statusLED.process();

  if(updateTimer.get_elapsed_millis()>1500) {

    //display.clearDisplay();
    display.setTextSize(1);             // Normal 1:1 pixel scale
    display.setTextColor(SSD1306_WHITE);        // Draw white text

    int target_line=0;

    switch(target_display_line) {
      case 0:
        target_line=0;
        break;
      case 1:
        target_line=15;
        break;
      case 2:
        target_line=30;
        break;
      case 3:
        target_line=45;
        break;
    }

    display.fillRect(0, target_line, SCREEN_WIDTH, 8, SSD1306_BLACK);
    display.setCursor(0,target_line);
 
    display.println(buff[0]);

    updateDisplay=true;

    counter=counter+1;

    updateTimer.reset();
  }

  if(scrollTimer.get_elapsed_millis()>10) {
    drawStepper(display);
    scrollTimer.reset();
    updateDisplay=true;
  }


  if(updateDisplay)
    display.display();

  if(Serial.available() > 0) {
    teststr = Serial.readString();  //read until timeout
    teststr.trim();

    int str_length=teststr.length();

    if(str_length>2) {
        int colonplace=teststr.indexOf(":");

        if(colonplace==1) {
          String command=teststr.substring(0,1);
          String data=teststr.substring(2,str_length);

          target_display_line=command.toInt();

          data.toCharArray(buff[0],BUFF_LEN);

          lastcommTimer.reset();

        }
        
    }
    
  }
 
}
