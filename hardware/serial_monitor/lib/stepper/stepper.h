#ifndef STEPPER_HEADER

#define STEPPER_HEADER

class stepper {

    public:
        stepper(int min,int max);
        void step();

        void set_range(int min,int max);

        int getValue() { return value; };
        int getLastValue() { return lastValue; };

    protected:
        unsigned int min;
        unsigned int max;
        int dir=1;
        int value;
        int lastValue;
};


#endif
