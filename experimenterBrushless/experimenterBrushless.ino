#include <PID_v1.h>
#include <Servo.h>

// Brushless motor
Servo brushless;

// PID variables
double Setpoint, Input, Output;
double Kp=1, Ki=0.05, Kd=0.25;
//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

#define SerialRate 115200
#define Ta 20000

#define pin_out 5
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
  // board led used to identify when running an experiment
  pinMode(13,OUTPUT);

  // brushless motor controlled by pin_vout through an ESC
  brushless.attach(pin_out);
  brushless.writeMicroseconds(1000); //initialize the signal to 1000

  Serial.begin(SerialRate);
  Serial.setTimeout(200);
  Serial.readBytesUntil(byte(55),input_buffer,16);
  estado = parado;
  experiment = step;
  before = micros();
  myPID.SetMode(MANUAL);
  myPID.SetSampleTime(20); 
}

void loop() {
  myPID.Compute();
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
            myPID.SetMode(MANUAL);
            Serial.println("Experiment set to\tStep response");
            break;
            case 1:
              experiment = prbs;
            myPID.SetMode(MANUAL);
            Serial.println("Experiment set to\tPRBS response");
            break;
            case 2:
            experiment = pid;
            myPID.SetMode(AUTOMATIC);
            Serial.println("Experiment set to\tPID control");
            break;
            case 3:
              experiment = compensator;
            myPID.SetMode(MANUAL);
            Serial.println("Experiment set to\tcompensator control");
            break;
            default:
            experiment = step;
            myPID.SetMode(MANUAL);
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
        default: break;
      }
    }
    break;
  case rodando:
    myPID.Compute();
    digitalWrite(13,1);
    now = micros();
    if((now-before)>=Ta){
      switch(experiment){
        case step:
          vout = expNumber<T0?V0:V1;
          brushless.writeMicroseconds(map(vout,0,255,1000,2000));
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
          brushless.writeMicroseconds(map(vout,0,255,1000,2000));
          vin = analogRead(pin_vin);
          break;
        case pid:
        case compensator:
        vsp = analogRead(pin_sp);
        Setpoint = (double)vsp;
        vin = analogRead(pin_vin);
        Input = (double)vin;
        //myPID.Compute();
        vout = (int)Output;
//        vout = pid(vin,setPoint,Kp,Ki,Kd,vout,intVout);
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
        brushless.writeMicroseconds(1000); // return to 0
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
