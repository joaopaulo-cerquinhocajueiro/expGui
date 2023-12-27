import communication as c
import time

ports = c.listPorts()
if len(ports)>0:
    print("Achada a porta {}".format(ports[0].name))
    ard = c.SerialPort(ports[0].name)
    ard.connect()
    ard.setTimes(200,400)
    ard.setVoltages(120,255,100)
    print(ard.getMeasure())
    ard.run()
    measurement = 1
    time.sleep(0.1)
    while measurement != 0:
        measurement = ard.getMeasure()
        print(measurement)
    ard.disconnect()
else:
    print("Nenhuma porta disponível")