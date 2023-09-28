
#define SerialRate 115200
#define Ta 20000

#define pin_vout 5
#define pin_vin A0

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

int nExp = 100; // número de amostras por experimento
int n1 = 50; // momento de iniciar o experimento

int vout_buffer[200];
int vin_buffer[200];

unsigned long int now, before;

void setup() {
  pinMode(13,OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(SerialRate);
  Serial.setTimeout(20);
  Serial.readBytesUntil(byte(55),input_buffer,16);
  estado = parado;
  experiment = step;
  before = micros();
}

void loop() {
  // put your main code here, to run repeatedly:
  switch(estado){
  case parado:
    digitalWrite(13,0);
    if (Serial.available()){
      // digitalWrite(13,1);
      Serial.readBytesUntil(byte(55),input_buffer,16);
      //Serial.write(input_buffer[0]);
      switch(input_buffer[0]){
        case 'r': // Run the experiment
        case 'R':
          // Serial.println("Rodando7");
          // delay(100);
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
          Serial.println("V0, V1, V2");
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
              Serial.println("T0, T1");
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
              Serial.println("Tmin, Tmax (PRBS)");
              Serial.print(Tmin);
              Serial.print('\t');
              Serial.println(Tmax);
          break;
        case 'm': // define the experiment type
        case 'M':
          switch(input_buffer[1]){
            case 0:
            experiment = step;
            Serial.println("Experiment set to Step response");
            break;
            case 1:
              experiment = prbs;
            Serial.println("Experiment set to PRBS response");
            break;
            case 2:
            experiment = step;
            Serial.println("Experiment set to PID control");
            break;
            case 3:
              experiment = compensator;
            Serial.println("Experiment set to compensator control");
            break;
            default:
            experiment = step;
          }
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
        case prbs:
          analogWrite(pin_vout,vout_buffer[expNumber]);
          vin_buffer[expNumber] = analogRead(pin_vin);
          break;
        default: break;
      }
      Serial.print('E');
      Serial.write(byte(vout_buffer[expNumber]));
      Serial.write(byte(vin_buffer[expNumber]>>8));
      Serial.write(byte(vin_buffer[expNumber]%256));
      Serial.write(55);
      Serial.println();
      before +=Ta;
      if(++expNumber>nExp){
        estado = parado;
      }
    }
  }
}

void setExperiment(){
  expNumber = 0;
  estado = rodando;
  // Serial.println("a1");
  switch(experiment){
    case step:
		for(int i=0;i<n1;i++){
		  vout_buffer[i] = V0;
		}
		for(int i=n1;i<nExp;i++){
		  vout_buffer[i] = V2;
		}
		break;
    case prbs:
		int i = 0;
		for(i=0;i<n1;i++){
		  vout_buffer[i] = V0;
		}
		int step = random(0,2);
		while (i<T1){
			i+=random(Tmin,Tmax);
			i= i>T1?T1:i;
			for(int j=0;j<i;j++){
				vout_buffer[j] = step?V1:V2;
			}
			step = !step;
		}
		break;
	case pid:
	case compensator:
	default:
		break;
  }
  before = micros();
}
