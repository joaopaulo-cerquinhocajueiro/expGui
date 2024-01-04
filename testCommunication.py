import communication as c
import time

ports = c.listPorts()
if len(ports)>0:
    print("Achada a porta {}".format(ports[0].name))
    ard = c.SerialPort(ports[0].name)
    ard.connect()
    ard.setType(1)
    ard.setVoltages(100,255,0)
    ard.setTimes(500,1000)
    print(ard.getMeasure())
    time.sleep(0.1)
    ard.run()
    measurement = 1
    while (measurement != 0):
        measurement = ard.getMeasure()
        print(measurement)
    ard.disconnect()
else:
    print("Nenhuma porta disponível")