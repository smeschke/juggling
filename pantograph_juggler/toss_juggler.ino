#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 9,8);
AccelStepper stepper2(AccelStepper::DRIVER, 4,3);

int start = 0;
int side = 0;
int max_speed = 12000;
int max_acceleration = 13200;
int starting_rotation = 200;
int stepover = 250;
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
      delay(5500);
    }

    
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 0){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 1;
      //delay(500);
    }
      
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 1){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 2;
      //delay(500);
    }
    
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 2){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 3;
      //delay(500);
    }
      
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 3){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 4;
      //delay(500);
    }
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 4){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 5;
      //delay(500);
    }

    
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 5){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 6;
      //delay(500);
    }

    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 6){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 7;
      //delay(500);
    }

    
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 7){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 8;
      //delay(500);
    }

    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 8){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 9;
      //delay(500);
    }

    
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 9){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 10;
      //delay(500);
    }
    
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 10){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 11;
      //delay(500);
    }

    
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 11){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 12;
      //delay(500);
    }
    
    if (abs(stepper1.distanceToGo()) == 0 
          and abs(stepper2.distanceToGo()) < stepover 
          and side == 12){
      stepper1.moveTo(-800+stepper1.currentPosition());
      side = 13;
      //delay(500);
    }

    
    if (abs(stepper2.distanceToGo()) == 0
          and abs(stepper1.distanceToGo()) < stepover
          and side == 13){
      stepper2.moveTo(800+stepper2.currentPosition());
      side = 14;
      //delay(500);
    }

    if (side == 14 and abs(stepper1.distanceToGo()) == 0 and abs(stepper2.distanceToGo()) == 0){
      side = 0;
      delay(5500);
    }
    
    if (start == 1){
      stepper2.run();    
      stepper1.run();
    }
    
}
