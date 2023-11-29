import serial
import time

# COM_PORT = '/dev/ttyACM0'
COM_PORT = 'COM3'

ser = serial.Serial(port=COM_PORT,baudrate=115200,timeout=1.0)

print("Espera um pouco para dar tempo de inicializar")
time.sleep(2)
# flush the serial port
ser.read_until()

def readAll():
	inputPackage = b'I'
	while (len(inputPackage) > 0):
		inputPackage = ser.read_until().strip()
		if len(inputPackage)>1:
			print(inputPackage[0],inputPackage[-1])
			if (inputPackage[0] == b'E'[0]) and (inputPackage[-1] == b'7'[0]):
				vInput = int(inputPackage[1])
				vOutput = int(inputPackage[2])*256 + int(inputPackage[3])
				print('Exp: {}\t{}'.format(vInput,vOutput))
			else:
				print(inputPackage)


print("test run")
runCommand = b'R7' # 'R' is the command to run the experiment, '7' (55) is the EoP
ser.write(runCommand)


readAll();

# Setting voltage levels
Vmin = int(100)
Vmax = int(355)
Vsp = int(256)
voltageSetBuffer = b'V' + int(Vmin/256).to_bytes(1,'little') + (Vmin%256).to_bytes(1,'little') + int(Vmax/256).to_bytes(1,'little') + (Vmax%256).to_bytes(1,'little') +int(Vsp/256).to_bytes(1,'little') + (Vsp%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
print("Setting voltages to {}, {} and {}".format(Vmin,Vmax,Vsp))
# print(voltageSetBuffer)
ser.write(voltageSetBuffer)

readAll()

print("second run")
ser.write(runCommand)
readAll()

setPrbs = b'M' + int(1).to_bytes(1,'little') + int(55).to_bytes(1,'little')
ser.write(setPrbs)
print("prbs run")
ser.write(runCommand)
readAll()
