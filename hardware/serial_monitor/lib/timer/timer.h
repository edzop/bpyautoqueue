#ifndef TIMER_HEADER

#define TIMER_HEADER

    class timer {
public:
  timer();

  void reset();

  unsigned long get_elapsed_millis();
  unsigned long get_elapsed_seconds();
  unsigned long get_elapsed_minutes();
  char* get_elapsed_text();
protected:
  unsigned long start_time;
  unsigned long elapsed_time;


  
};

#endif
