#ifndef LED_HEADER
#define LED_HEADER

class timer;

class led {

public:
  led(int pin = 13);
  ~led();
  void toggle();
  void setState(bool state);
  void flash(int times, int on = 400, int off = 200);
  void setup();

  void setup_default_status();

  void setLight_On();
  void setLight_Off();

  void extinguishLight_Temporarily();

  void set_blink(bool blink);

  void toggle_blink();

  void process();

  void setFlashTiming(int onDelay, int offDelay);

protected:
  int pin;
  bool state;
  bool doflash;

  int flashOnDelay;
  int flashOffDelay;

  timer *timerLastStateChange;
};

#endif
