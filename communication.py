import serial
import serial.tools.list_ports
import time

def listPorts():
     return serial.tools.list_ports.comports()

class SerialPort:
    def __init__(self, portName):
        self.name = portName
        self.connected = False
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(self.name, 115200,timeout=0.5)
        time.sleep(1)  # wait for the serial connection to initialize
        self.ser.read_all() # flush the serial port
        self.connected = True

    def disconnect(self):
        if self.ser == None:
             pass
        else:
            self.ser.close()
            self.connected = False

    def setVoltages(self, Vsp, Vmin, Vmax):
        # Setting voltage levels based on the values of the inputs
        voltageSetBuffer = b'V' + int(Vmin/256).to_bytes(1,'little') + (Vmin%256).to_bytes(1,'little') + int(Vmax/256).to_bytes(1,'little') + (Vmax%256).to_bytes(1,'little') +int(Vsp/256).to_bytes(1,'little') + (Vsp%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting voltages to {}, {} and {}".format(Vmin,Vmax,Vsp))
        # print(voltageSetBuffer)
        self.ser.write(voltageSetBuffer)

    def setTimes(self, T1, T2):
        timeSetBuffer = b'T' + int(T1/256).to_bytes(1,'little') + (T1%256).to_bytes(1,'little') + int(T2/256).to_bytes(1,'little') + (T2%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting timings to {} and {}".format(T1, T2))
        # print(voltageSetBuffer)
        self.ser.write(timeSetBuffer)

    def setPRBSTimes(self, Tmin, Tmax):
        prbsTimeSetBuffer = b'P' + int(Tmin/256).to_bytes(1,'little') + (Tmin%256).to_bytes(1,'little') + int(Tmax/256).to_bytes(1,'little') + (Tmax%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
        print("Setting minimun amaximun PRBS pulse widths to {} and {}".format(Tmin, Tmax))
        # print(voltageSetBuffer)
        self.ser.write(prbsTimeSetBuffer)

    def run(self):
        runCommand = b'R7' # 'R' is the command to run the experiment, '7' (55) is the EoP
        self.ser.write(runCommand)


    def getMeasure(self):
        inputPackage = b"I"
        contador = 100
        inputPackage = self.ser.read_until().strip()
        # print(inputPackage)
        if len(inputPackage)>1:
            if (inputPackage[0] == b'E'[0]) and (inputPackage[-1] == b'7'[0]):
                vInput = int(inputPackage[1])
                vOutput = int(inputPackage[2])*256 + int(inputPackage[3])
                return ('meas',vInput,vOutput)
            else:
                return inputPackage
        else:
            return(0)