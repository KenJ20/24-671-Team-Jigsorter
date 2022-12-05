// Include the Arduino Encoder Library
#include <Encoder.h>

// Include the Arduino Stepper Library
#include <Stepper.h>

#define P_I 3.14159

//set up conveyor motor pins
const int conv1 = 9;
const int conv2 = 8;
const int convEn = 10;

// define rotating ring motor pins
const int rot1 = 4;
const int rot2 = 5;
const int rotEn = 11;
const int rotEnc1 = 2;
const int rotEnc2 = 3;

// what zone are we trying to reach
int zone = 0;

// whether it is the first iteration of the loop
bool first = true;

// set up encoder variables
int encReading;  // current encoder reading
int newEnc;      // previous encoder reading
 
// what constant speed are we commanding
float rpmRef = 25;

// th variables
float thTrav = 0;    // current angle to system is at from home
float dTh;           // angular displacement between updates
float th;            // goal angle
float thStart;       // start angle
float thBound = 2;   // final theta allowed to be within +-thBound degrees of goal

// time variables
int timeExp;                 // expected time to reach goal theta based on rpmRef
unsigned long tPrev;         // previous time stamp
unsigned long t0;            // time at start of path
unsigned long t;             // current time
unsigned long dt;            // time between updates
unsigned long tRamp = 100;   // time to stop velocity before tExp to allow motor to slow down
unsigned long convt0;
unsigned long convt;
int sgn;              // direction of travel to reach goal th based on feedforward control
int diffSgn;          // direction of travel when feedback is added in
float velCom;         // desired rpm commanded to motor driver
int intVel;           // converted rpm value to (0-255) integer value to command to motor driver
int ctr = 0;
bool waiting = true;
// create instance of encoder library
Encoder rotEnc(rotEnc1, rotEnc2);

// stepper motor variables
const int stepEn1 = 7;
const int stepEn2 = 12;
// Number of steps per output rotation
const int stepsPerRevolution = 200;
const int pushSteps = 100;
// Create Instance of Stepper library
Stepper myStepper(stepsPerRevolution, 24,25,26,27);

// modes: 0, rotating conveyor motor / 1, rotating ring / 2, pushing / 3, reversing ring
int mode = 0;
bool needsSetup = true;
bool isDone;
bool started = false;

void setup() {
  // set pin modes and make sure motor is shut off
  pinMode(rot1, OUTPUT);
  pinMode(rot2, OUTPUT);
  pinMode(rotEn, OUTPUT);
  pinMode(rotEnc1, INPUT);
  pinMode(rotEnc2, INPUT);
  digitalWrite(rot1, LOW);
  digitalWrite(rot2, LOW);
  digitalWrite(stepEn1, LOW);
  digitalWrite(stepEn2, LOW);
  Serial.begin(115200);
  
  // Conveyor
  pinMode(conv1, OUTPUT);
  pinMode(conv2, OUTPUT);
  pinMode(convEn, OUTPUT);
  // Set initial Conveyor rotation direction
  digitalWrite(conv1, LOW);
  digitalWrite(conv2, HIGH);
}

void loop() {
  //put your main code here, to run repeatedly:
  if (!started){
    if (Serial.available()){
      if (Serial.read() == "start"){
        started = true;
      }
    }
    delay(5);
  }
  else{
    // if we're running the conveyor code
    if (mode == 0){
      // if we receive a message, set up timing, ends waiting for zone, reads zone
      if (Serial.available() > 0){
        convt0 = millis();
        waiting = false;
        zone = Serial.read();
      }
      // if we're not waiting and it's been two seconds
      else if ((!waiting) && ((millis() - t0) > 2000)){
        // stop conveyor, switch mode
        conveyorStop();
        mode = 1;
        needsSetup = true;
      }
      // run the conveyor otherwise
      else{
        conveyorRun();
        delay(5);
      }
    }
  
    else if (mode == 1){
      if (needsSetup){
        thBound = 2;
        setUpTransportation(zone);
        needsSetup = false;
        delay(5);
      }
      isDone = runTransportation();
      if (isDone){
        mode = 2;
      }
      else{
        delay(5);
      }
    }
  
    else if (mode == 2){
      pushPiece();
      needsSetup = true;
      mode = 3;
    }
  
    else if (mode == 3){
      if (needsSetup){
        thBound = .45;
        setUpTransportation(-1);
        needsSetup = false;
        delay(5);
      }
      isDone = runTransportation();
      if (isDone){
        if (zone != 5){
          mode = 4;
          zone = zone + 1;
          needsSetup = true;
          delay(2000);
        }  
        else{
          exit(0);
        }
      }
      else{
        //Serial.print(intVel);
        //Serial.print(" ");
        //Serial.print(thTrav);
        //Serial.print("\n");
        delay(5);
      }
    }
    else{
      if (needsSetup){
        convt0 = millis();
        convt = 0;
        needsSetup = false;
      }
      convt = millis() - t0;
      if (convt > 3000){
        conveyorStop();
        mode = 0;
        needsSetup = true;
        waiting = true;
        Serial.print('F');
      }
      else{
        conveyorReverse();
      }
    }
  }
}

void conveyorStop() {
  analogWrite(convEn, 0);
  delay(20);
}

void conveyorRun() {
  analogWrite(convEn, 255); // Send PWM signal to L298N Enable pin
  digitalWrite(conv1, HIGH);
  digitalWrite(conv2, LOW);
  delay(20);
}

void conveyorReverse() {
  analogWrite(convEn, 255); // Send PWM signal to L298N Enable pin
  digitalWrite(conv1, LOW);
  digitalWrite(conv2, HIGH);
  delay(20);
}



void setUpTransportation(int zone){
  t0 = millis();
  tPrev = t0;
  encReading = rotEnc.read();
  th = mapZoneToTh(zone);
  timeExp = ceil(((abs(th-thTrav)/360.0)/rpmRef)*60000);
  thStart = thTrav;
  sgn = 1;
  if ((zone > 3) || (zone == -1)){
    sgn = -1*sgn;
  }
}

bool runTransportation(){
  // grab time and new encoder reading, and turn it into th updates
  t = millis() - t0;
  dt = t - tPrev;
  newEnc = rotEnc.read();
  dTh = ((float(newEnc - encReading))*360) / (34.014 * 48);
  thTrav = thTrav + dTh;
  
  // find commanded velocity and manipulate it for motor command
  velCom = findRpm(thStart, th, sgn, thTrav, t, dt, dTh);
  
  // use velcom sign to update diffSgn
  if (velCom < 0){
    diffSgn = -1;
  }
  else{
    diffSgn = 1;
  }
  velCom = velCom*diffSgn;
  intVel = motorCmmd(velCom);
  motorSet(intVel, diffSgn);

  // if we've arrived at goal and th is no longer changing significantly
  if (((fabs(th - thTrav) < thBound)&&(fabs(dTh) == 0)) && (ctr == 3)){
    // turn motor off
    ctr = 0;
    digitalWrite(rot1, LOW);
    digitalWrite(rot2, LOW);

    return true;
  }
  // set previous encoder and time reading to current encoder and time reading
  encReading = newEnc;
  tPrev = t;
  return false;
}

// finds what rpm should be commanded
float findRpm(float thStart, float thGoal, int sgn, float thTrav, unsigned long t, unsigned long dt, float dTh){
  // feedforward velocity is reference velocity, k is proportional constant for control
  float rpmFF = rpmRef;
  float k = .1;
  
  // calculate the expected angle at this time based on feedforward signal
  float thExp = thStart + ((float(t))/60000.0)*((sgn*rpmRef*360.0));

  // if we should have reached the goal angle, ff velocity is 0, thExp is goal theta
  if (((sgn > 0) && (thExp >= thGoal)) || ((sgn < 0) && (thExp <= thGoal))){
      rpmFF = 0;
      thExp = thGoal;
      // set sgn=0 to signal that we've reached the goal theta
      sgn = 0;
  }

  // calculate the control angular velocity, and convert it to rpm
  float wCont = k*((thExp - thTrav)/(float(dt)/1000));
  float rpmCont = wCont*(60.0/360.0);

  // check if we've reached the goal theta and set the control velocity = 0
  if (sgn == 0){
    if (((fabs(th - thTrav) < thBound)&&(fabs(dTh) == 0))){
      ctr = ctr + 1;
      if (ctr == 3){
        rpmCont = 0;
      }
    }
  }

  // combine the rpms
  float rpmComb = (sgn*rpmFF) + rpmCont;

  // if we are in the lag time shutoff, no rpm commanded
  if ((t > (timeExp - tRamp)) && (t < timeExp)){
      rpmComb = 0;
  }
  return rpmComb;
}

//takes in a float rpm and transforms it to a commandable int value
int motorCmmd(float rpm){
  // find 0-255 value based on best fit line of 0-255 value to rpm
  float volCom = (rpm + 26.906)/.5673;
  
  // limits the maximum speed
  if (volCom > 200){
      return 200;
  }
  // if rpm is zero, let it be zero (best fit line doesn't start at 0)
  else if (rpm == 0.0){
      return 0;
  }
  // limits minimum speed
  else if (volCom < 80){
      return 80;
  }
  // return the ceiling of the value
  return ceil(volCom);
}

// sets the motor given a 0-255 integer rpm-correlated value and direction
void motorSet(int volCom, int sgn){
  // set en pin to volCom value
  analogWrite(rotEn, volCom);
  // if going ccw
  if (sgn == 1){
    digitalWrite(rot1, LOW);
    digitalWrite(rot2, HIGH);
  }
  // if the motor shouldn't be moving
  else if (volCom == 0){
    digitalWrite(rot1, LOW);
    digitalWrite(rot2, LOW);
  }
  // if going cw
  else{
    digitalWrite(rot1, HIGH);
    digitalWrite(rot2, LOW);
  }
}

// maps a zone to a theta value
float mapZoneToTh(int zone){
  float th;
  if ((zone == -1) || (zone == 1)){
    th = 0;
  }
  else if (zone == 0){
    th = 60;
  }
  else if (zone == 3){
    th = 120;
  }
  else if (zone == 5){
    th = 180;
  }
  else if (zone == 2){
    th = -60;
  }
  else if (zone == 4){
    th = -120;
  }
  return th;
}

// pushes the puzzle piece
void pushPiece(){
    digitalWrite(stepEn1, HIGH);
    digitalWrite(stepEn2, HIGH);
    myStepper.setSpeed(45);
    myStepper.step(-pushSteps);
    myStepper.step(pushSteps);
    digitalWrite(stepEn1, LOW);
    digitalWrite(stepEn2, LOW);
}
