#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 5,4);
AccelStepper stepper2(AccelStepper::DRIVER, 11,10);

int side = 0;

void setup()
{  
  stepper1.setMaxSpeed(2200);
  stepper1.setAcceleration(4000);  
  stepper2.setMaxSpeed(2200);
  stepper2.setAcceleration(4000);
}
void loop()
{
    if (abs(stepper2.distanceToGo()) < 200 and abs(stepper1.distanceToGo()) == 0 and side == 0){
      stepper1.moveTo(800+stepper1.currentPosition());
      side = 1;
    }
      
    if (abs(stepper2.distanceToGo()) == 0 and abs(stepper1.distanceToGo()) < 200 and side == 1){
      stepper2.moveTo(-800+stepper2.currentPosition());
      side = 0;
    }
    
    stepper2.run();    
    stepper1.run();
}
