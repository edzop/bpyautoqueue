#include <led.h>

#include <Arduino.h>

#include "timer.h"

led::led(int _pin) : pin(_pin) {
  state = false;
  setFlashTiming(400, 400);

  doflash = false;
  timerLastStateChange = new timer();
}

void led::setup_default_status() {
  set_blink(true);
  setFlashTiming(40, 1600);
}

led::~led() { delete timerLastStateChange; }

void led::setFlashTiming(int onDelay, int offDelay) {
  flashOnDelay = onDelay;
  flashOffDelay = offDelay;
}

void led::extinguishLight_Temporarily() {
  setState(false);
  // update_hardware_state();
}

void led::setLight_Off() {
  doflash = false;
  setState(false);
}

void led::setLight_On() {
  doflash = false;
  setState(true);
}

void led::setState(bool newstate) {
  state = newstate;

  if (state)
    digitalWrite(pin, HIGH);
  else
    digitalWrite(pin, LOW);

  timerLastStateChange->reset();
}

void led::toggle() { setState(!state); }

void led::setup() {
  pinMode(pin, OUTPUT);
  setState(false);
}

void led::flash(int times, int ontime, int offtime) {

  for (int a = 0; a < times; a++) {
    setState(true);
    delay(ontime);
    setState(false);
    delay(offtime);
  }
}

void led::process() {
  //  time_last_state_switch = clock();

  //  printf("elapsed: %f\r\n",elapsed);

  if (doflash) {
    double elapsed = timerLastStateChange->get_elapsed_millis();

    if (state == true) {
      if (elapsed > flashOnDelay)
        toggle();
    } else {
      if (elapsed > flashOffDelay)
        toggle();
    }
  }
}

void led::set_blink(bool blink) { doflash = blink; }

void led::toggle_blink() {

  if (doflash)
    doflash = false;
  else
    doflash = true;
}
