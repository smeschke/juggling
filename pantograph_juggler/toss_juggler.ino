#include <AccelStepper.h>
AccelStepper stepper1(AccelStepper::DRIVER, 9, 8);
AccelStepper stepper2(AccelStepper::DRIVER, 4, 3);

int start = 0;
int side = 0;
int max_speed = 5200;
int max_acceleration = 11000;
int starting_rotation = 200;
int stepover = 280;
int step_distance = 800;

void setup()
{
  //sdfsd
  stepper1.setMaxSpeed(max_speed);
  stepper2.setMaxSpeed(max_speed);
  stepper1.setAcceleration(1234);
  stepper2.setAcceleration(1234);
  stepper1.moveTo(600);
  stepper2.moveTo(-200);
}

void loop()
{

  if (start == 0) {
    while (abs(stepper1.distanceToGo()) != 0) {
      stepper1.run();
    }
    while (abs(stepper2.distanceToGo()) != 0) {
      stepper2.run();
    }
    start = 1;
    stepper1.setAcceleration(max_acceleration);
    stepper2.setAcceleration(max_acceleration);
    delay(500);
  }


  if (abs(stepper1.distanceToGo()) == 0
      and abs(stepper2.distanceToGo()) < stepover
      and side == 0) {
    stepper1.moveTo(step_distance + stepper1.currentPosition());
    side = 1;
  }

  if (abs(stepper2.distanceToGo()) == 0
      and abs(stepper1.distanceToGo()) < stepover
      and side == 1) {
    stepper2.moveTo(step_distance + stepper2.currentPosition());
    side = 0;
  }

  if (start == 1) {
    stepper2.run();
    stepper1.run();
  }
}
