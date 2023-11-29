import tkinter as tk
from tkinter import ttk
from tkinter import * 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial
import time

# this is a function which returns the selected combo box item
def getSelectedComboItem():
	return comboType.get()


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tVzero.get()
	return userInput


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tVone.get()
	return userInput


# this is a function to get the user input from the text input box
def getInputBoxValue():
	userInput = tVtwo.get()
	return userInput


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
	print('clicked')



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
# This is the section of code which creates a text input box


# This is the section of code which creates a text input box

# First, we create a canvas to put the picture on
# worthAThousandWords= Canvas(root, height=480, width=640)
# # Then, we actually create the image file to use (it has to be a *.gif)
# picture_file = PhotoImage(file = '')  # <-- you will have to copy-paste the filepath here, for example 'C:\Desktop\pic.gif'
# # Finally, we create the image on the canvas and then place it onto the main window
# worthAThousandWords.create_image(480, 0, anchor=NE, image=picture_file)
# worthAThousandWords.place(x=800-640-12, y=12)

fig = Figure(figsize=(6.4, 4.8), dpi=100)
ax = fig.add_subplot(111)
plotCanvas = FigureCanvasTkAgg(fig, master=root)
# plotCanvas.get_tk_widget().pack()
plotCanvas.get_tk_widget().place(x=200, y=12)
plotCanvas.draw()

# This is the section of code which creates a button
Button(root, text='Run', bg='#EEDFCC', font=('arial', 12, 'normal'), command=runExperiment).place(x=12, y=400)


root.mainloop()
