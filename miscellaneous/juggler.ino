#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::FULL4WIRE, 2,3,4,5);
AccelStepper stepper2(AccelStepper::FULL4WIRE, 10,11,12,13);

void setup()
{  
  // Change these to suit your stepper if you want
  stepper1.setMaxSpeed(300);
  stepper1.setAcceleration(1200);
  
  stepper2.setMaxSpeed(300);
  stepper2.setAcceleration(1200);
  
}

void loop()
{
    if (stepper1.distanceToGo() == 0 and stepper2.distanceToGo() == 0)
      stepper1.moveTo(-200+stepper1.currentPosition());
      stepper1.run();
    if (stepper2.distanceToGo() == 0 and stepper1.distanceToGo() == 0)
      stepper2.moveTo(200+stepper2.currentPosition());
      stepper2.run();    
}
