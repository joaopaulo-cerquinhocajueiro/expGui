import communication as c
import time

ports = c.listPorts()
if len(ports)>0:
    print("Achada a porta {}".format(ports[0].name))
    ard = c.SerialPort(ports[0].name)
    ard.connect()
    ard.setType(2)
    ard.setVoltages(100,255,0)
    ard.setTimes(200,1000)
    ard.setPID(3.756,0.019,1270.0)
    print(ard.getMeasure())
    time.sleep(0.1)
    ard.run()
    tic = time.perf_counter()
    measurement = 1
    while (measurement != 0):
        measurement = ard.getMeasure()
        if(measurement==0):
            measurement = ard.getMeasure()
        print(measurement)
    ard.disconnect()
    toc = time.perf_counter()
    print(f"Executou o experimento em {toc - tic:0.4f} segundos")
else:
    print("Nenhuma porta disponível")