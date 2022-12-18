#include "timer.h"

#if (ARDUINO >= 100)
#include <Arduino.h>
#endif

static char datestr[15];

timer::timer() { reset(); }

unsigned long timer::get_elapsed_millis() {
#if (ARDUINO >= 100)
  unsigned long end_time = millis();
  return end_time - start_time;
#else
  return 0;
#endif
}

unsigned long timer::get_elapsed_seconds() {
  return get_elapsed_millis() / 1000;
}

unsigned long timer::get_elapsed_minutes() {
//  unsigned long elapsed_seconds=get_elapsed_millis();
  return get_elapsed_seconds() / 60;
}

char* timer::get_elapsed_text() {
  unsigned long elapsed_millis= millis() - start_time;

  unsigned long seconds =(elapsed_millis/1000)%60;
  
  unsigned long minutes =(elapsed_millis/(1000L*60))%60;
  unsigned long hours   =(elapsed_millis/(1000L*60*60))%24;
  unsigned long days    =(elapsed_millis/(1000L*60*60*24))%24;

  sprintf(datestr,"%02ld:%02ld:%02ld:%02ld",days,hours,minutes,seconds);
  return datestr;
}


void timer::reset() {

#if (ARDUINO >= 100)
  start_time = millis();
#endif
}
