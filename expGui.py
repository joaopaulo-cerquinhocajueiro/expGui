import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import asksaveasfilename
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import csv
import time

import communication

# Global variables for the measurement
measurementNumber = -1 # index
measurementArray = [] # index array
inputArray = [] # input array
outputArray = [] # output array
spArray = [] # setpoint array

expTypeNumber = 0 # index for the experiment type
# the experiment type can be:
# experimentTypes = ['Step', 'PRBS', 'PID', 'Compensador', 'Step-PID', 'Step-Compensador', 'PRBS-PID', 'PRBS-Compensador']
## so far only the first three are defined
experimentTypes = ['Step', 'PRBS', 'PID', 'Compensador']

ard = None # later will be assigned to an SerialPort object, from communication.py
#			 can't run an experiment while ard is None

def setConnButton(a):
	if (comboPort.get() != "None"): # Can connect only if a port is selected
		connButton.configure(state='active')
	else:
		connButton.configure(state='disabled')

# Function to handle the connection with the arduino (or other platform) performing the experiment
def connectArduino():
	global ard
	if ard is None: # if there is no connection yet
		ard = communication.SerialPort(comboPort.get()) # get the selected port
		ard.connect() # and connect

		# change the button to disconnect
		connButton.configure(text="Disconnect")
		# and enable the runButton 
		runButton.configure(state="active")

	else: # If there is a ard object
		if ard.connected: # and it is already connected
			# then disconnect
			ard.disconnect()
			# change the button to connect
			connButton.configure(text="Connect")
			# and disable the runButton
			runButton.configure(state="disabled")

		else: # but if ard is not None but is not connected
			ard = communication.SerialPort(comboPort.get()) # get the selected port
			ard.connect() # and connect

			# change the button to disconnect
			connButton.configure(text="Disconnect")
			# and enable the runButton 
			runButton.configure(state="active")
	# wait half a second to guarantee the connection and the arduino reset 
	time.sleep(0.5)

# Execute the experiment
# The experiment type an all parameters are obtained from the GUI inputs - to change later
def runExperiment(_ard):
	global measurementArray,inputArray,outputArray,spArray,measurementNumber

	# initialize the plot
	ax.clear()  # clear the previous plot
	ax.plot([],[],'b')
	ax.plot([],[],'r')
	ax.plot([],[],'g')
	ax.set_xlabel("Measurement number")
	ax.set_ylabel("Input, Output and setPoint")
	ax.set_xlim([0,int(tTtwo.get())]) # Ttwo defines the number of measurements
	ax.set_ylim([0,1024])
	
	# initialize the measurement variables
	measurementNumber = 0
	measurementArray = []
	inputArray = []
	outputArray = []
	spArray = []
	ard = _ard

	# Configure the experiment
	# experiment = comboType.get()
	ard.setType(expTypeNumber) # expTypeNumber is set when the type is selected
	
	if ((expTypeNumber==1)): # if is PRBS
		# then set the minimum and maximum step times
		ard.setPRBSTimes(int(tPmin.get()), int(tPmax.get()))
	# set the times	
	ard.setTimes(int(tTone.get()), int(tTtwo.get()))
	if ((expTypeNumber==2)): # if is PID
		# set the PID constants 
		ard.setPID(float(tKp.get()),float(tKi.get()),float(tKd.get()))
	elif ((expTypeNumber==3)): # if is compensator:
		ard.setLeadLag(float(tKp.get()),float(tTc1.get()),float(tTc2.get()))
	# in all cases set the voltages
	ard.setVoltages(int(tVzero.get()), int(tVone.get()), int(tVtwo.get()))
	# get one measurement for sanity - should return 0
	ard.getMeasure()
	# and run the experiment

	ard.run()
		
root = Tk()

# This is the section of code which creates the main window
root.geometry('800x600')
root.configure(background='#FFEFDB')
root.title('Python Experimenter')


# Label and ComboBox for selecting the experiment type
Label(root, text='Experimento', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=12)

comboType= ttk.Combobox(root, values=experimentTypes, font=('arial', 12, 'normal'), width=10)
comboType.place(x=12, y=36)
comboType.current(0)

def whenExpSelected(a):
	global expTypeNumber
	expType = comboType.get()
	if expType == "Step":
		expTypeNumber = 0
		tVzero.configure(state=NORMAL)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=NORMAL)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)
		tKp.configure(state=DISABLED)
		tKi.configure(state=DISABLED)
		tKd.configure(state=DISABLED)
		tTc1.configure(state=DISABLED)	
		tTc2.configure(state=DISABLED)	
	elif expType == 'PRBS':
		expTypeNumber = 1
		tVzero.configure(state=NORMAL)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=NORMAL)
		tTone.configure(state=NORMAL)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=NORMAL)
		tPmax.configure(state=NORMAL)
		tKp.configure(state=DISABLED)
		tKi.configure(state=DISABLED)
		tKd.configure(state=DISABLED)
		tTc1.configure(state=DISABLED)	
		tTc2.configure(state=DISABLED)	
	elif expType == 'PID':
		expTypeNumber = 2
		tVzero.configure(state=DISABLED)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=DISABLED)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)
		tKp.configure(state=NORMAL)
		tKi.configure(state=NORMAL)
		tKd.configure(state=NORMAL)
		tTc1.configure(state=DISABLED)	
		tTc2.configure(state=DISABLED)	
	elif expType == 'Compensador':
		expTypeNumber = 2
		tVzero.configure(state=DISABLED)
		tVone.configure(state=NORMAL)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=DISABLED)
		tTtwo.configure(state=NORMAL)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)
		tKp.configure(state=NORMAL)
		tKi.configure(state=DISABLED)
		tKd.configure(state=DISABLED)
		tTc1.configure(state=NORMAL)	
		tTc2.configure(state=NORMAL)	
	elif expType == 'Step-PID' or expType == 'Step-Compensador' or expType == 'PRBS-PID' or expType == 'PRBS-Compensador':
		expTypeNumber = 2
		tVzero.configure(state=DISABLED)
		tVone.configure(state=DISABLED)
		tVtwo.configure(state=DISABLED)
		tTone.configure(state=DISABLED)
		tTtwo.configure(state=DISABLED)
		tPmin.configure(state=DISABLED)
		tPmax.configure(state=DISABLED)
		tKp.configure(state=DISABLED)
		tKi.configure(state=DISABLED)
		tKd.configure(state=DISABLED)
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
tVzero = Entry(root, width = 6)
tVzero.insert(0,str(0))
tVzero.place(x=36, y=72)

# V1
Label(root, text='V1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=96)
tVone=Entry(root, width = 6)
tVone.insert(0,str(100))
tVone.place(x=36, y=96)
# V2
Label(root, text='V2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=100, y=96)
tVtwo=Entry(root, width=6)
tVtwo.insert(0,str(255))
tVtwo.place(x=124, y=96)
tVtwo.configure(state=DISABLED)

# T1
Label(root, text='T1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=120)
tTone=Entry(root,width=6)
tTone.insert(0,str(100))
tTone.place(x=36, y=120)
# T2
Label(root, text='T2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=100, y=120)
tTtwo=Entry(root,width=6)
tTtwo.insert(0,str(200))
tTtwo.place(x=124, y=120)

# Pmin
Label(root, text='Pmin', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=144)
tPmin=Entry(root,width=6)
tPmin.insert(0,str(10))
tPmin.place(x=48, y=144)
tPmin.configure(state=DISABLED)
# Pmax
Label(root, text='Pmax', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=100, y=144)
tPmax=Entry(root,width=6)
tPmax.insert(0,str(100))
tPmax.place(x=148, y=144)
tPmax.configure(state=DISABLED)

# Kp
Label(root, text='Kp', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=168)
tKp=Entry(root,width=6)
tKp.insert(0,str(0.1))
tKp.place(x=36, y=168)
tKp.configure(state=DISABLED)

# Ki
Label(root, text='Ki', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=192)
tKi=Entry(root,width=6)
tKi.insert(0,str(0.0))
tKi.place(x=36, y=192)
tKi.configure(state=DISABLED)
# Kd
Label(root, text='Kd', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=100, y=192)
tKd=Entry(root,width=6)
tKd.insert(0,str(0.01))
tKd.place(x=124, y=192)
tKd.configure(state=DISABLED)

# Tc1
Label(root, text='Tc1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=216)
tTc1=Entry(root,width=6)
tTc1.insert(0,str(0.0))
tTc1.place(x=48, y=216)
tTc1.configure(state=DISABLED)
# Tc2
Label(root, text='Tc2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=100, y=216)
tTc2=Entry(root,width=6)
tTc2.insert(0,str(0.01))
tTc2.place(x=136, y=216)
tTc2.configure(state=DISABLED)

fig = Figure(figsize=(6.4, 4.8), dpi=100)
ax = fig.add_subplot(111)
plotCanvas = FigureCanvasTkAgg(fig, master=root)
# plotCanvas.get_tk_widget().pack()
plotCanvas.get_tk_widget().place(x=200, y=12)
plotCanvas.draw()

def figAnimate(i):
	global measurementNumber, ard
	global measurementArray,inputArray, outputArray, spArray
	# print("{}.{}".format(type(measurementNumber),type(figXMax)))
	if ard is None:
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
						spArray.append(measurement[3])
						measurementNumber += 1
						# ax.plot(measurementArray, inputArray, "b")  # create the new plot
						# ax.plot(measurementArray, outputArray, "r")  # create the new plot
		# else:
			# ax.clear()
		ax.plot(measurementArray, inputArray, "b")  # create the new plot
		ax.plot(measurementArray, outputArray, "r")  # create the new plot
		ax.plot(measurementArray, spArray, "g")  # create the new plot

def saveMeasurement():
	savefile = asksaveasfilename(filetypes=[('csv file','*.csv'),('text file','*.txt')], defaultextension='.csv')
	with open(savefile,'w',newline="") as f:
		write = csv.writer(f)
		write.writerow(['#', 'input', 'output', 'setpoint'])
		for meas,inp,outp,sp in zip(measurementArray,inputArray,outputArray,spArray):
			write.writerow([meas,inp, outp, sp])

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

# Save button
saveButton = Button(root, text='Save', bg='#EEDFCC', font=('arial', 12, 'normal'), command=saveMeasurement)
saveButton.place(x=12, y=460)

ani = animation.FuncAnimation(fig,figAnimate, interval=50)
root.mainloop()
