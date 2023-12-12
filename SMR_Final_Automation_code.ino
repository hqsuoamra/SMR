// Motor and Pin Definitions
#define Echo 22
#define Trig 24

#define PWMA 12  
#define DIRA1 34 
#define DIRA2 35  
#define PWMB 8  
#define DIRB1 37 
#define DIRB2 36 
#define PWMC 9 
#define DIRC1 43 
#define DIRC2 42  
#define PWMD 5    
#define DIRD1 A4  
#define DIRD2 A5 


// Motor Control Macros
#define MOTORA_FORWARD(pwm)    do{digitalWrite(DIRA1,LOW); digitalWrite(DIRA2,HIGH);analogWrite(PWMA,pwm);}while(0)
#define MOTORA_STOP(x)         do{digitalWrite(DIRA1,LOW); digitalWrite(DIRA2,LOW); analogWrite(PWMA,0);}while(0)
#define MOTORA_BACKOFF(pwm)    do{digitalWrite(DIRA1,HIGH);digitalWrite(DIRA2,LOW); analogWrite(PWMA,pwm);}while(0)

#define MOTORB_FORWARD(pwm)    do{digitalWrite(DIRB1,HIGH); digitalWrite(DIRB2,LOW);analogWrite(PWMB,pwm);}while(0)
#define MOTORB_STOP(x)         do{digitalWrite(DIRB1,LOW); digitalWrite(DIRB2,LOW); analogWrite(PWMB,0);}while(0)
#define MOTORB_BACKOFF(pwm)    do{digitalWrite(DIRB1,LOW);digitalWrite(DIRB2,HIGH); analogWrite(PWMB,pwm);}while(0)
//左后轮
#define MOTORC_FORWARD(pwm)    do{digitalWrite(DIRC1,LOW); digitalWrite(DIRC2,HIGH);analogWrite(PWMC,pwm);}while(0)
#define MOTORC_STOP(x)         do{digitalWrite(DIRC1,LOW); digitalWrite(DIRC2,LOW); analogWrite(PWMC,0);}while(0)
#define MOTORC_BACKOFF(pwm)    do{digitalWrite(DIRC1,HIGH);digitalWrite(DIRC2,LOW); analogWrite(PWMC,pwm);}while(0)

#define MOTORD_FORWARD(pwm)    do{digitalWrite(DIRD1,HIGH); digitalWrite(DIRD2,LOW);analogWrite(PWMD,pwm);}while(0)
#define MOTORD_STOP(x)         do{digitalWrite(DIRD1,LOW); digitalWrite(DIRD2,LOW); analogWrite(PWMD,0);}while(0)
#define MOTORD_BACKOFF(pwm)    do{digitalWrite(DIRD1,LOW);digitalWrite(DIRD2,HIGH); analogWrite(PWMD,pwm);}while(0)

// Serial Definition
#define SERIAL  Serial

// PWM and Distance Constants
#define MAX_PWM   200
#define MIN_PWM   130

//Motors movement and direction
int Motor_PWM = 40;



//    ↑A-----B↑   
//     |  ↑  |
//     |  |  |
//    ↑C-----D↑
void ADVANCE()
{
  MOTORA_FORWARD(Motor_PWM);MOTORB_FORWARD(Motor_PWM);    
  MOTORC_FORWARD(Motor_PWM);MOTORD_FORWARD(Motor_PWM);    
}

//    ↓A-----B↓ 
//     |  |  |
//     |  ↓  |
//    ↓C-----D↓
void BACK()
{
  MOTORA_BACKOFF(Motor_PWM);MOTORB_BACKOFF(Motor_PWM);
  MOTORC_BACKOFF(Motor_PWM);MOTORD_BACKOFF(Motor_PWM);
}


void MOVE_LEFT(uint8_t pwm_A,uint8_t pwm_B,uint8_t pwm_C,uint8_t pwm_D)
{
  MOTORA_BACKOFF(pwm_A);MOTORB_FORWARD(pwm_B);
  MOTORC_BACKOFF(pwm_C);MOTORD_FORWARD(pwm_D);
}

void MOVE_RIGHT(uint8_t pwm_A,uint8_t pwm_B,uint8_t pwm_C,uint8_t pwm_D)
{
  MOTORA_FORWARD(pwm_A);MOTORB_BACKOFF(pwm_B);
  MOTORC_FORWARD(pwm_C);MOTORD_BACKOFF(pwm_D);
}
//    =A-----B=  
//     |  =  |
//     |  =  |
//    =C-----D=
void STOP()
{
  MOTORA_STOP(Motor_PWM);MOTORB_STOP(Motor_PWM);
  MOTORC_STOP(Motor_PWM);MOTORD_STOP(Motor_PWM);
}

// Distance Variables
float echoDistance;
int leftDistance = 0;
int rightDistance = 0;
int forwardDistance = 0;
int backDistance = 0;

// Debug Logging
#define LOG_DEBUG

#ifdef LOG_DEBUG
#define M_LOG SERIAL.print
#else
#define M_LOG 
#endif

// Initialize IO pins
void IO_init()
{
  pinMode(PWMA, OUTPUT);
  pinMode(DIRA1, OUTPUT);pinMode(DIRA2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  
  // Add pinMode for other motor control pins...
  pinMode(DIRB1, OUTPUT);pinMode(DIRB2, OUTPUT);
  pinMode(PWMC, OUTPUT);
  pinMode(DIRC1, OUTPUT);pinMode(DIRC2, OUTPUT);
  pinMode(PWMD, OUTPUT);
  pinMode(DIRD1, OUTPUT);pinMode(DIRD2, OUTPUT);
  pinMode(Trig,OUTPUT);
  pinMode(Echo,INPUT);
  STOP();
}

// Ultrasonic Distance Measurement
int testDistance(){
  
  digitalWrite(Trig,LOW);
  delayMicroseconds(2);
  digitalWrite(Trig,HIGH);
  delayMicroseconds(20);
  digitalWrite(Trig,LOW);
  echoDistance = pulseIn(Echo,HIGH);
  // Convert echoDistance to centimeters
  echoDistance /= 58;// echoDistance= echoDistance÷58
  return (int)echoDistance;
}



void setup()
{
  SERIAL.begin(9600);
  IO_init();
}

unsigned long forwardStartTime = 0;  // Variable to store the time when the robot starts moving forward

void loop() {
  // Measure the distance in front of the robot
  forwardDistance = testDistance();

  if (forwardDistance > 60) {
    if (forwardStartTime == 0) {
      // Start the timer when the robot begins moving forward
      forwardStartTime = millis();
    }
    ADVANCE();
  } else if (forwardDistance <= 65) {
    // Reset the timer when the robot stops moving forward
    forwardStartTime = 0;

    BACK();
    delay(1000);
    // Turn right to scan for a clear path
    MOVE_RIGHT(Motor_PWM, Motor_PWM, Motor_PWM, Motor_PWM);
    delay(300);
    // If the path is clear, move forward
    if (forwardDistance > 65) {
      ADVANCE();
      delay(2000);
      MOVE_LEFT(Motor_PWM, Motor_PWM, Motor_PWM, Motor_PWM);
      delay(1000);
    }
  }

  // Check if the robot has been moving forward for a specified time (e.g., 5000 milliseconds or 5 seconds)
  if (forwardStartTime != 0 && millis() - forwardStartTime > 5000) {
    // Stop moving forward and turn left
    STOP();
    MOVE_LEFT(Motor_PWM, Motor_PWM, Motor_PWM, Motor_PWM);
    delay(1000);
    forwardStartTime = 0;  // Reset the timer after turning left
  }
  
  // Add any additional code or functions you need to run inside the loop
}
