import tkinter as tk
from tkinter import ttk
from tkinter import * 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import csv
import time

import communication

measurementNumber = -1
measurementArray = []
inputArray = []
outputArray = []
measureAble = False

ard = None

def setConnButton(a):
	connected = True
	if (comboPort.get() != "None"):
		connButton.configure(state='active')
	else:
		connButton.configure(state='disabled')

def connectArduino():
	global ard
	if ard is None:
		connButton.configure(text="Disconnect")
		runButton.configure(state="active")
		ard = communication.SerialPort(comboPort.get())
		ard.connect()
	else:
		if ard.connected:
			ard.disconnect()
			connButton.configure(text="Connect")
			runButton.configure(state="disabled")
		else:
			connButton.configure(text="Disconnect")
			runButton.configure(state="active")
			ard = communication.SerialPort(comboPort.get())
			ard.connect()
	time.sleep(0.5)

def runExperiment(_ard):
	global measurementArray,inputArray,outputArray,measurementNumber
	ax.clear()  # clear the previous plot
	ax.plot([],[],'b')
	ax.plot([],[],'r')
	measurementNumber = 0
	measurementArray = []
	inputArray = []
	outputArray = []
	ard = _ard
	print('Run the experiment')
	# print("the ards are {} and {}".format(ard,_ard))
	experiment = comboType.get()
	ard.setTimes(int(tTone.get()), int(tTtwo.get()))
	# ard.setTimes(1000, 2000)
	# ard.getMeasure()
	ard.setVoltages(int(tVzero.get()), int(tVone.get()), int(tVtwo.get()))
	ard.getMeasure()
	# time.sleep(0.1)
	ard.run()
	# self.ax.axes(xlim=(0,1000),ylim=(0,1024))
	ax.set_xlabel("Measurement number")
	ax.set_ylabel("Input and Output")
	print(int(tTtwo.get()))
	ax.set_xlim([0,int(tTtwo.get())])
	ax.set_ylim([0,1024])
		
	measurementNumber = -1
	measurementArray = []
	currentArray = []
	speedArray = []
	measureAble = True

root = Tk()

# This is the section of code which creates the main window
root.geometry('800x600')
root.configure(background='#FFEFDB')
root.title('Python Experimenter')


# Label and ComboBox for selecting the experiment type
Label(root, text='Experimento', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=12)
comboType= ttk.Combobox(root, values=['Step', 'PRBS', 'PID', 'Compensador', 'Step-PID', 'Step-Compensador', 'PRBS-PID', 'PRBS-Compensador'], font=('arial', 12, 'normal'), width=10)
comboType.place(x=12, y=36)
comboType.current(0)

def whenExpSelected(a):
	expType = comboType.get()
	if expType == "Step":
		tVzero.configure(state=NORMAL)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=NORMAL)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)
	elif expType == 'PRBS':
		tVzero.configure(state=NORMAL)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=NORMAL)
		tTone.configure(state=NORMAL)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=NORMAL)
		tPmax.configure(state=NORMAL)
	elif expType == 'PID' or expType == 'Compensador' or expType == 'Step-PID' or expType == 'Step-Compensador' or expType == 'PRBS-PID' or expType == 'PRBS-Compensador':
		tVzero.configure(state=DISABLED)
		tVone.configure(state=DISABLED)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=DISABLED)
		tTtwo.configure(state=DISABLED)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)

comboType.bind("<<ComboboxSelected>>",whenExpSelected)

# Inputs for the experiment parameters
# Vzero
lVzero = Label(root, text='V0', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=72)
def validateVzero(P):
	if(P.isNumeric()):
		if int(P)>=0 and int(P)<=255 :
			return True
		else:
			return False
	else:
		# root.submit.config(state=(NORMAL if P else DISABLED))
		return False
vcmdVzero = root.register(validateVzero)
# tVzero = Entry(root, validate = 'key', validatecommand = (vcmdVzero, '%P'))
tVzero = Entry(root)
tVzero.insert(0,str(0))
tVzero.place(x=36, y=72)
# V1
Label(root, text='V1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=96)
tVone=Entry(root)
tVone.insert(0,str(100))
tVone.place(x=36, y=96)
# V2
Label(root, text='V2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=120)
tVtwo=Entry(root)
tVtwo.insert(0,str(255))
tVtwo.place(x=36, y=120)
# T1
Label(root, text='T1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=144)
tTone=Entry(root)
tTone.insert(0,str(100))
tTone.place(x=36, y=144)
# T2
Label(root, text='T2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=168)
tTtwo=Entry(root)
tTtwo.insert(0,str(200))
tTtwo.place(x=36, y=168)
# Pmin
Label(root, text='Pmin', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=192)
tPmin=Entry(root)
tPmin.insert(0,str(10))
tPmin.place(x=48, y=192)
# Pmax
Label(root, text='Pmax', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=216)
tPmax=Entry(root)
tPmax.insert(0,str(100))
tPmax.place(x=48, y=216)

fig = Figure(figsize=(6.4, 4.8), dpi=100)
ax = fig.add_subplot(111)
plotCanvas = FigureCanvasTkAgg(fig, master=root)
# plotCanvas.get_tk_widget().pack()
plotCanvas.get_tk_widget().place(x=200, y=12)
plotCanvas.draw()

def figAnimate(i):
	global measurementNumber, ard
	global measurementArray,inputArray, outputArray
	# print("{}.{}".format(type(measurementNumber),type(figXMax)))
	if ard is None:
			measureAble = False
			ax.clear()
	else:
		figXMax = int(tTtwo.get())
		if ard.connected and (measurementNumber<figXMax):
			while(ard.ser.in_waiting>0):
				measurement = ard.getMeasure()
				if isinstance(measurement, tuple):
					# print(measurement)
					if measurement[0] == 'meas':
						measurementArray.append(measurementNumber)
						inputArray.append(measurement[1])
						outputArray.append(measurement[2])
						measurementNumber += 1
						# ax.plot(measurementArray, inputArray, "b")  # create the new plot
						# ax.plot(measurementArray, outputArray, "r")  # create the new plot
		else:
			measureAble = False
			ax.clear()
		ax.plot(measurementArray, inputArray, "b")  # create the new plot
		ax.plot(measurementArray, outputArray, "r")  # create the new plot


# Arduino config
Label(root, text='Arduino Serial port', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=248)
import serial.tools.list_ports
ports = ["None"]
for port in serial.tools.list_ports.comports():
    ports.append(port.name)
comboPort= ttk.Combobox(root, values=ports, font=('arial', 12, 'normal'), width=10)
comboPort.place(x=12, y=280)
comboPort.current(0)
comboPort.bind("<<ComboboxSelected>>",setConnButton)
# Connect button

connButton = Button(root, text='Connect', bg='#EEDFCC', font=('arial', 12, 'normal'), command=connectArduino)
connButton.place(x=12, y=320)
connButton.configure(state=DISABLED)

# Run button
runButton = Button(root, text='Run', bg='#EEDFCC', font=('arial', 12, 'normal'), command=lambda: runExperiment(ard))
runButton.place(x=12, y=400)
runButton.configure(state="disabled")

ani = animation.FuncAnimation(fig,figAnimate, interval=50)
root.mainloop()
