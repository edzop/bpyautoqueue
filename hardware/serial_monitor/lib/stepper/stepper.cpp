
#include "stepper.h"

stepper::stepper(int min,int max) : min(min), max(max) {
    value=min;
    lastValue=min;
}

void stepper::step() {
    lastValue=value;

    if(dir==1) {
        value++;

        if(value>max) {
            value=max;
            dir=0;
        }
    } else {
        value--;

        if(value<min) {
            value=min;
            dir=1;
        }
    }
}

