const int pinMot = 5;
const int pinAng = A0;

const long int TS = 10000; //in microseconds
long int now,before;

byte inputBuffer[5];
byte outputBuffer[5];

int motorVal=0;
int angVal;

void setup() {
  // put your setup code here, to run once:
  pinMode(pinMot,OUTPUT);
  pinMode(pinAng,INPUT);
  Serial.begin(115200);
  before = micros();
  outputBuffer[0] = 255;
}

void loop() {
  // put your main code here, to run repeatedly:
  now = micros();
  if((now-before) >= TS){
    before+=TS;
    angVal = analogRead(pinAng);
    outputBuffer[1] = highByte(angVal);
    outputBuffer[2] = lowByte(angVal);
    Serial.write(outputBuffer,5);
    if(Serial.available()>=5){
      Serial.readBytes(inputBuffer,5);
      if(inputBuffer[0]==255){
        motorVal = inputBuffer[1];
        analogWrite(pinMot,motorVal);
      }
    }
  }
}
