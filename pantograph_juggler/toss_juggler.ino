#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 9, 8);
AccelStepper stepper2(AccelStepper::DRIVER, 4, 3);

int start = 0;
int side = 0;
int max_speed = 6000;
int max_acceleration = 12000;
int starting_rotation = 200;
int stepover = 340;
int ledPinR = 7;
int ledPinL = 6;
int step_distance = 800;

void setup()
{
  stepper1.setMaxSpeed(max_speed);
  stepper1.setAcceleration(max_acceleration);
  stepper2.setMaxSpeed(max_speed);
  stepper2.setAcceleration(max_acceleration);
  stepper1.moveTo(starting_rotation);
  stepper2.moveTo(starting_rotation);
  pinMode(ledPinR, OUTPUT);
  pinMode(ledPinL, OUTPUT);
}

void loop()
{
  
  if (start == 0) {
    delay(2000);
    while (abs(stepper1.distanceToGo()) != 0
           and abs(stepper2.distanceToGo()) != 0) {
      stepper2.run();
      stepper1.run();
    }
    start = 1;
    digitalWrite(ledPinR, HIGH); digitalWrite(ledPinL, HIGH);
    for (int i = 0; i <= 15; i++){
      delay(75); digitalWrite(ledPinL, LOW); digitalWrite(ledPinR, LOW);
      delay(75); digitalWrite(ledPinL, HIGH); digitalWrite(ledPinR, HIGH);
    }
  }
  
  if (abs(stepper1.distanceToGo()) == 0
      and abs(stepper2.distanceToGo()) < stepover
      and side == 0) {
    //delay(2500);
    stepper1.moveTo(step_distance + stepper1.currentPosition());
    side = 1;
    digitalWrite(ledPinL, HIGH);
  }
  
  if (abs(stepper2.distanceToGo()) == 0
      and abs(stepper1.distanceToGo()) < stepover
      and side == 1) {
    //delay(2500);
    stepper2.moveTo(-step_distance + stepper2.currentPosition());
    side = 0;
    digitalWrite(ledPinR, HIGH);
  }
  
  if (start == 1) {
    stepper2.run();
    stepper1.run();
  }
  if (stepper1.distanceToGo()==0){ digitalWrite(ledPinL, LOW); }
  if (stepper2.distanceToGo()==0){ digitalWrite(ledPinR, LOW); }
}
