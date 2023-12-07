import tkinter as tk
from tkinter import ttk
from tkinter import * 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial
import time


ser = "None"
connected = False

# this is a function which returns the selected combo box item
def getSelectedComboItem():
	return comboType.get()

def setConnButton(a):
	if (comboPort.get() != "None"):
		connButton.configure(state='active')
	else:
		connButton.configure(state='disabled')

# this is a function to get the user input from the text input box

def setVoltages():
	# Setting voltage levels based on the values of the inputs
	Vmin = int(tVone.get())
	Vmax = int(tVtwo.get())
	Vsp = int(tVzero.get())
	voltageSetBuffer = b'V' + int(Vmin/256).to_bytes(1,'little') + (Vmin%256).to_bytes(1,'little') + int(Vmax/256).to_bytes(1,'little') + (Vmax%256).to_bytes(1,'little') +int(Vsp/256).to_bytes(1,'little') + (Vsp%256).to_bytes(1,'little') + int(55).to_bytes(1,'little')
	print("Setting voltages to {}, {} and {}".format(Vmin,Vmax,Vsp))
	# print(voltageSetBuffer)
	ser.write(voltageSetBuffer)



# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tTone.get()
	return userInput


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tTtwo.get()
	return userInput


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tPmin.get()
	return userInput


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tPmax.get()
	return userInput


# this is the function called when the button is clicked
def runExperiment():
	print('Run the experiment')
	runCommand = b'R7' # 'R' is the command to run the experiment, '7' (55) is the EoP
	ser.write(runCommand)


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

# Inputs for the experiment parameters
# Vzero
Label(root, text='V0', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=72)
tVzero = Entry(root)
tVzero.place(x=36, y=72)
# V1
Label(root, text='V1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=96)
tVone=Entry(root)
tVone.place(x=36, y=96)
# V2
Label(root, text='V2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=120)
tVtwo=Entry(root)
tVtwo.place(x=36, y=120)
# T1
Label(root, text='T1', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=144)
tTone=Entry(root)
tTone.place(x=36, y=144)
# T2
Label(root, text='T2', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=12, y=168)
tTtwo=Entry(root)
tTtwo.place(x=36, y=168)
# Pmin
Label(root, text='Pmin', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=192)
tPmin=Entry(root)
tPmin.place(x=48, y=192)
# Pmax
Label(root, text='Pmax', bg='#FFEFDB', font=('arial', 12, 'normal')).place(x=6, y=216)
tPmax=Entry(root)
tPmax.place(x=48, y=216)

fig = Figure(figsize=(6.4, 4.8), dpi=100)
ax = fig.add_subplot(111)
plotCanvas = FigureCanvasTkAgg(fig, master=root)
# plotCanvas.get_tk_widget().pack()
plotCanvas.get_tk_widget().place(x=200, y=12)
plotCanvas.draw()

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
def connectArduino():
	global ser,connected
	if (connected):
		ser.close()
		connButton.configure(text="Connect")
		runButton.configure(state="disabled")
		connected = False
	else:
		ser = serial.Serial(comboPort.get(), 115200)
		time.sleep(2)  # wait for the serial connection to initialize
		ser.read_until() # flush the serial port
		connButton.configure(text="Disconnect")
		runButton.configure(state="active")
		connected = True

connButton = Button(root, text='Connect', bg='#EEDFCC', font=('arial', 12, 'normal'), command=connectArduino)
connButton.place(x=12, y=320)
connButton.configure(state=DISABLED)

# Run button
runButton = Button(root, text='Run', bg='#EEDFCC', font=('arial', 12, 'normal'), command=runExperiment)
runButton.place(x=12, y=400)
runButton.configure(state="disabled")


root.mainloop()
