import serial
import serial.tools.list_ports
import time
import struct

def listPorts():
     return serial.tools.list_ports.comports()

class SerialPort:
    def __init__(self, portName):
        self.name = portName
        self.connected = False
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(self.name, 115200,timeout=0.1)
        time.sleep(1)  # wait for the serial connection to initialize
        self.ser.read_all() # flush the serial port
        time.sleep(0.1)  # wait for the serial connection to initialize
        self.connected = True

    def disconnect(self):
        if self.ser == None:
             pass
        else:
            self.ser.close()
            self.connected = False

    def setType(self,expType):
        # Setting voltage levels based on the values of the inputs
        notCompleted = True
        attempts = 3
        typeSetBuffer = b'M' + int(expType).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting experiment to {}".format(['step', 'prbs', 'pid', 'compensator'][expType]))
        while notCompleted:
            attempts -= 1
            self.ser.write(typeSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "Experiment set to"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("Experiment type set")

    def setVoltages(self, Vsp, Vmin, Vmax):
        # Setting voltage levels based on the values of the inputs
        notCompleted = True
        attempts = 3
        voltageSetBuffer = b'V' + int(Vsp/256).to_bytes(1,'little') + (Vsp%256).to_bytes(1,'little') + int(Vmin/256).to_bytes(1,'little') + (Vmin%256).to_bytes(1,'little') +int(Vmax/256).to_bytes(1,'little') + (Vmax%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting voltages to {}, {} and {}".format(Vmin,Vmax,Vsp))
        # print(voltageSetBuffer)
        while notCompleted:
            attempts -= 1
            self.ser.write(voltageSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "V0, V1, V2:"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("out of voltage set")
        
    def setTimes(self, T1, T2):
        notCompleted = True
        attempts = 3
        timeSetBuffer = b'T' + int(T1/256).to_bytes(1,'little') + (T1%256).to_bytes(1,'little') + int(T2/256).to_bytes(1,'little') + (T2%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting timings to {} and {}".format(T1, T2))
        print(timeSetBuffer)
        while notCompleted:
            attempts -= 1
            self.ser.write(timeSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "T0, T1:"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("out of time set")

    def setPRBSTimes(self, Tmin, Tmax):
        notCompleted = True
        attempts = 3
        timeSetBuffer = b'B' + int(Tmin/256).to_bytes(1,'little') + (Tmin%256).to_bytes(1,'little') + int(Tmax/256).to_bytes(1,'little') + (Tmax%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting PRBS timings to {} and {}".format(Tmin, Tmax))
        print(timeSetBuffer)
        while notCompleted:
            attempts -= 1
            self.ser.write(timeSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "Tmin, Tmax (PRBS):"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("out of time set")

    def setPID(self, Kp, Ki, Kd):
        notCompleted = True
        attempts = 3
        pidSetBuffer = b'Q' + bytearray(struct.pack("f", Kp)) + bytearray(struct.pack("f", Ki))+ bytearray(struct.pack("f", Kd)) + int(55).to_bytes(1,'little')
        print("Setting PID constants to {}, {} and {}".format(Kp, Ki, Kd))
        print(pidSetBuffer)
        while notCompleted:
            attempts -= 1
            self.ser.write(pidSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "Kp, Ki, Kd:"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("out of PID set")

    def setLeadLag(self, Kp, Tc1, Tc2):
        notCompleted = True
        attempts = 3
        llSetBuffer = b'L' + bytearray(struct.pack("f", Kp)) + bytearray(struct.pack("f", Tc1))+ bytearray(struct.pack("f", Tc2)) + int(55).to_bytes(1,'little')
        print("Setting lead lag constants to {}, {} and {}".format(Kp, Tc1, Tc2))
        print(llSetBuffer)
        while notCompleted:
            attempts -= 1
            self.ser.write(llSetBuffer)
            time.sleep(0.01)
            response = self.getMeasure()
            if isinstance(response,int):
                notCompleted = True
            else:
                response = response.split(b'\t')
                if(response[0] == "Kp, Tc1, Tc2:"):
                    notCompleted = False
            if attempts == 0:
                notCompleted = False
        print(response)
        print("out of lead lag set")

    def run(self):
        runCommand = b'R7' # 'R' is the command to run the experiment, '7' (55) is the EoP
        self.ser.write(runCommand)
        print("Sent run command")
        time.sleep(0.1)


    def getMeasure(self):
        inputPackage = b"I"
        contador = 100
        inputPackage = self.ser.read_until().strip()
        # print("Received: {}".format(inputPackage))
        # print(inputPackage)
        if len(inputPackage)>1:
            if (inputPackage[0] == b'E'[0]) and (inputPackage[-1] == b'7'[0]):
                vInput = int(inputPackage[1])
                vOutput = int(inputPackage[2])*256 + int(inputPackage[3])
                vSp = int(inputPackage[4])*256 + int(inputPackage[5])
                return ('meas',vInput,vOutput,vSp)
            else:
                return inputPackage
        else:
            return(0)