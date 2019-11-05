#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 9, 8);
AccelStepper stepper2(AccelStepper::DRIVER, 4, 3);

int start = 0;
int side = 0;
int max_speed = 1800000;
int max_acceleration = 16000;
int starting_rotation = 200;
int stepover = 140;
int num_throws = 2000;
int idx = 0;
int ledPin = 13;

void setup()
{
  stepper1.setMaxSpeed(max_speed);
  stepper1.setAcceleration(max_acceleration);
  stepper2.setMaxSpeed(max_speed);
  stepper2.setAcceleration(max_acceleration);
  stepper1.moveTo(starting_rotation);
  stepper2.moveTo(starting_rotation);
  pinMode(ledPin, OUTPUT);
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
    delay(2000);
    digitalWrite(ledPin, HIGH);
  }
  
  if (abs(stepper1.distanceToGo()) == 0
      and abs(stepper2.distanceToGo()) < stepover
      and side == 0
      and idx < num_throws) {
    stepper1.moveTo(-800 + stepper1.currentPosition());
    side = 1;
  }
  
  if (abs(stepper2.distanceToGo()) == 0
      and abs(stepper1.distanceToGo()) < stepover
      and side == 1
      and idx < num_throws) {
    stepper2.moveTo(-800 + stepper2.currentPosition());
    side = 0;
    idx += 1;
  }
  
  if (start == 1) {
    stepper2.run();
    stepper1.run();
  }
  
  if (idx == num_throws and
      abs(stepper1.distanceToGo()) == 0
      and abs(stepper2.distanceToGo()) == 0) {
    digitalWrite(ledPin, LOW);
    delay(5000);
    digitalWrite(ledPin, HIGH);
    idx = 0;
  }
}
