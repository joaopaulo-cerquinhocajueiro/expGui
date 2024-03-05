//#define SERVO_OUTPUT

#ifdef SERVO_OUTPUT
#include <Servo.h>

// Brushless motor
Servo brushless;
#endif

// PID variables
#define outMax 255.0
#define outMin 0.0
double Setpoint, Input, Output, Offset;
double Kp=1.0, Ki=0.05, Kd=0.25;
double Integral = 0.0;
double lastInput = 0.0;

double PIDCompute(){

  double error = Setpoint - Input;

  double proportional = Kp * error;
  
  Integral += Ki*error;
  if(Integral > outMax)
    Integral = outMax;
  else if(Integral < outMin)
    Integral = outMin;

  double derivativo = Kd*(Input - lastInput);

  double PIDOut = proportional + Integral - derivativo + Offset;
  if(PIDOut > outMax)
    PIDOut = outMax;
  else if(PIDOut < outMin)
    PIDOut = outMin;

  lastInput = Input;

  return PIDOut;
}

///////// Lead Lag variables and computation ///////

// Using implementation described in (Krikelis, Fassois, 1984)
// y[n] = (T2/(T2 + Ta))*y[n-1] + (Kp*(T1 + Ta)/(T2 + Ta))*e[n] - (Kp*T1/(T2+Ta))*e[n-1]

// Many variables already defined for PID
// #define outMax 255.0
// #define outMin 0.0
// double Setpoint, Input, Output;
//double Kp=1.0, Ki=0.05, Kd=0.25;
double yAnt = 0.0; // y[n-1]
double eAnt = 0.0; // e[n-1]
double fT1;
double fT2;
double kyAnt; // (T2/(T2 + Ta))
double ke;    // (Kp*(T1 + Ta)/(T2 + Ta))
double keAnt; // (Kp*T1/(T2+Ta))

double leadLagCompute(){
  double error = Setpoint - Input;
  double leadLag = kyAnt*yAnt + ke*error - keAnt*eAnt + Offset;
  if(leadLag > outMax)
    leadLag = outMax;
  else if(leadLag < outMin)
    leadLag = outMin;
  yAnt = leadLag;
  eAnt = error;
  return leadLag;
}


#define SerialRate 115200
#define Ta 20000
float fTa = float(Ta)*1e-6;

#define pin_vout 5
#define pin_vin A0
#define pin_sp A5

byte input_buffer[16];

enum estado_t {parado, rodando, erro}estado;
enum experiment_t {step, prbs, pid, compensator}experiment;

int V1 = 100;
int V2 = 250;
int V0  = 175;

int T0 = 50;
int T1 = 200;
int Tmin = 10;
int Tmax = 50;

int expNumber = 0;
int prbsPulseCounter;
int prbsStep = random(0,2);

char vout;
int vin,vsp;

unsigned long int now, before;

void setup() {
  pinMode(13,OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(SerialRate);
  Serial.setTimeout(200);
  Serial.readBytesUntil(byte(55),input_buffer,16);
  estado = parado;
  experiment = step;
  before = micros();
  #ifdef SERVO_OUTPUT
  // brushless motor controlled by pin_vout through an ESC
  brushless.attach(pin_out);
  brushless.write(0); //initialize the signal to 1000
  #endif
  #ifndef SERVO_OUTPUT
  pinMode(pin_vout,OUTPUT);
  #endif
}

void loop() {
  // put your main code here, to run repeatedly:
  switch(estado){
  case parado:
    digitalWrite(13,0);
    if (Serial.available()){
      // digitalWrite(13,1);
      Serial.readBytesUntil(byte(55),input_buffer,16);
      // Serial.println(input_buffer[0]);
      switch(input_buffer[0]){
        case 'r': // Run the experiment
        case 'R':
          Serial.println("Rodando7");
          delay(100);
          setExperiment();
          break;
        case 'v': // set the voltages
        case 'V':
          // V0 is the output value that the experiment starts
          V0 = int(input_buffer[1]) * 256 + int(input_buffer[2]);
          // V1 is the step value for the step or one of the values for the PRBS
          // It also serves as the offset of the PID experiment
          V1 = int(input_buffer[3]) * 256 + int(input_buffer[4]);
          // V2 is the other value for the PRBS
          V2  = int(input_buffer[5]) * 256 + int(input_buffer[6]);
          Serial.print("V0, V1, V2:\t");
          Serial.print(V0);
          Serial.print('\t');
          Serial.print(V1);
          Serial.print('\t');
          Serial.println(V2);
        break;
          case 't': // Set the general time constants
          case 'T':
          //            ---------------
          // __________/
          // 0         T0             T1
              T0 = int(input_buffer[1]) * 256 + int(input_buffer[2]);
              T1 = int(input_buffer[3]) * 256 + int(input_buffer[4]);
              Serial.print("T0, T1:\t");
              Serial.print(T0);
              Serial.print('\t');
              Serial.println(T1);
          break;
        case 'p': // Set the time constants for the PRBS signal
        case 'P':
          // Tmin is the minimum length of a PRBS pulse
          Tmin = int(input_buffer[1]) * 256 + int(input_buffer[2]);
          // Tmax is the maximum length of a PRBS pulse
          Tmax = int(input_buffer[3]) * 256 + int(input_buffer[4]);
              Serial.print("Tmin, Tmax (PRBS):\t");
              Serial.print(Tmin);
              Serial.print('\t');
              Serial.println(Tmax);
          break;
        case 'm': // define the experiment type
        case 'M':
          switch(input_buffer[1]){
            case 0:
            experiment = step;
            Serial.println("Experiment set to\tStep response");
            break;
            case 1:
              experiment = prbs;
            Serial.println("Experiment set to\tPRBS response");
            break;
            case 2:
            experiment = pid;
            Serial.println("Experiment set to\tPID control");
            break;
            case 3:
              experiment = compensator;
            Serial.println("Experiment set to\tcompensator control");
            break;
            default:
            experiment = step;
          }
          break;
        case 'q': // Set the PID parameters
        case 'Q':
          byte * bKp = (byte *) &Kp;
          bKp[0] = input_buffer[1];
          bKp[1] = input_buffer[2];
          bKp[2] = input_buffer[3];
          bKp[3] = input_buffer[4];
          byte * bKi = (byte *) &Ki;
          bKi[0] = input_buffer[5];
          bKi[1] = input_buffer[6];
          bKi[2] = input_buffer[7];
          bKi[3] = input_buffer[8];
          byte * bKd = (byte *) &Kd;
          bKd[0] = input_buffer[9];
          bKd[1] = input_buffer[10];
          bKd[2] = input_buffer[11];
          bKd[3] = input_buffer[12];
          Serial.print("Kp, Ki, Kd:\t");
          Serial.print(Kp);
          Serial.print('\t');
          Serial.print(Ki);
          Serial.print('\t');
          Serial.println(Kd);
          break;
        case 'l': // Set the lead/lag parameters
        case 'L':
          byte * bKll = (byte *) &Kp;
          bKll[0] = input_buffer[1];
          bKll[1] = input_buffer[2];
          bKll[2] = input_buffer[3];
          bKll[3] = input_buffer[4];
          byte * bT1 = (byte *) &fT1;
          bT1[0] = input_buffer[5];
          bT1[1] = input_buffer[6];
          bT1[2] = input_buffer[7];
          bT1[3] = input_buffer[8];
          byte * bT2 = (byte *) &fT2;
          bT2[0] = input_buffer[9];
          bT2[1] = input_buffer[10];
          bT2[2] = input_buffer[11];
          bT2[3] = input_buffer[12];
          // Adjust the leadLag specific constants
          // float fTa = float(Ta);
          kyAnt = (fT2/(fT2 + fTa));
          ke = (Kp*(fT1 + fTa)/(fT2 + fTa));
          keAnt = (Kp*fT1/(fT2+fTa));

              Serial.print("Kp, Tc1, Tc2:\t");
              Serial.print(Kp);
              Serial.print('\t');
              Serial.print(fT1);
              Serial.print('\t');
              Serial.println(fT2);
          break;
        default: break;
      }
    }
    break;
  case rodando:
    digitalWrite(13,1);
    now = micros();
    if((now-before)>=Ta){
      switch(experiment){
        case step:
          vout = expNumber<T0?V0:V1;
          #ifndef SERVO_OUTPUT
          analogWrite(pin_vout,vout);
          #endif
          #ifdef SERVO_OUTPUT
          brushless.write(map(vout,0,255,0,180));
          #endif
          vin = analogRead(pin_vin);
          break;
        case prbs:
          if(expNumber<T0){
            vout = V0;
          } else {
            if(prbsPulseCounter<=expNumber){
              prbsPulseCounter = expNumber + random(Tmin,Tmax);
              prbsStep = !prbsStep;
            }
            vout = prbsStep?V1:V2;
          }
          #ifndef SERVO_OUTPUT
          analogWrite(pin_vout,vout);
          #endif
          #ifdef SERVO_OUTPUT
          brushless.write(map(vout,0,255,0,180));
          #endif
          vin = analogRead(pin_vin);
          break;
        case pid:
          vsp = analogRead(pin_sp);
          Setpoint = (double)vsp;
          vin = analogRead(pin_vin);
          Input = (double)vin;
          Offset = (double)V1;
          Output = PIDCompute();
          vout = (int)Output;
          #ifndef SERVO_OUTPUT
          analogWrite(pin_vout,vout);
          #endif
          #ifdef SERVO_OUTPUT
          brushless.write(map(vout,0,255,0,180));
          #endif
          break;
        case compensator:
          vsp = analogRead(pin_sp);
          Setpoint = (double)vsp;
          vin = analogRead(pin_vin);
          Input = (double)vin;
          Offset = (double)V1;
          Output = leadLagCompute();
          vout = (int)Output;
          #ifndef SERVO_OUTPUT
          analogWrite(pin_vout,vout);
          #endif
          #ifdef SERVO_OUTPUT
          brushless.write(map(vout,0,255,0,180));
          #endif
          break;
        default: break;
      }
      Serial.print('E');
      Serial.write(byte(vout));
      Serial.write(byte(vin>>8));
      Serial.write(byte(vin%256));
      Serial.write(byte(vsp>>8));
      Serial.write(byte(vsp%256));
      Serial.write(55);
      Serial.println();
      before +=Ta;
      if(++expNumber>T1){
        estado = parado;
        analogWrite(pin_vout,0); // return to 0
      }
    }
    break;
  case erro:
  digitalWrite(13,1);
  delay(50);
  digitalWrite(13,0);
  delay(50);
  }
}

void setExperiment(){
  expNumber = 0;
  prbsPulseCounter = 0;
  estado = rodando;
  before = micros();
}
// AMDG