#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 9,8);
AccelStepper stepper2(AccelStepper::DRIVER, 4,3);

int start = 0;
int side = 0;
int max_speed = 8000;
int max_acceleration = 20000;
int starting_rotation = 200;
int stepover = 200;
void setup()
{  
  stepper1.setMaxSpeed(max_speed);
  stepper1.setAcceleration(max_acceleration);  
  stepper2.setMaxSpeed(max_speed);
  stepper2.setAcceleration(max_acceleration);
  stepper1.moveTo(starting_rotation);
  stepper2.moveTo(-starting_rotation);  
  }
  
void loop()
{
    if (start == 0){
      delay(2000);
      while (abs(stepper1.distanceToGo()) != 0 
              and abs(stepper2.distanceToGo()) != 0){
        stepper2.run();
        stepper1.run();
      }
      start = 1;
      delay(2000);
    }
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 0){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 1;
    }
      
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 1){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 3;
    }

    if (side == 3 and abs(stepper1.distanceToGo()) == 0 and abs(stepper2.distanceToGo()) == 0){
      side = 0;
      delay(3000);
    }
    
    if (start == 1){
      stepper2.run();    
      stepper1.run();
    }
    
}
