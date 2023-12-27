import tkinter as tk
from tkinter.filedialog import asksaveasfilename
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import serial
import time

import csv

ArduinoComm = "COM4"
ArduinoBAUD = 115200

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.measurementArray = []
        self.currentArray = []
        self.speedArray = []
        self.measurementNumber = -1
        self.connected = False
        self.measureAble = False

    def create_widgets(self):
        self.connect_button = tk.Button(self)
        self.connect_button["text"] = "Connect"
        self.connect_button["command"] = self.connect_to_arduino
        self.connect_button.pack(side='left')

        self.cal_button = tk.Button(self)
        self.cal_button['state'] = 'disabled'
        self.cal_button["text"] = "Calibrate"
        self.cal_button["command"] = self.calibrateCurrent
        self.cal_button.pack(side='left')

        self.measure_button = tk.Button(self)
        self.measure_button['state'] = 'disabled'
        self.measure_button["text"] = "Measure"
        self.measure_button["command"] = self.startMeasurement
        self.measure_button.pack(side='left')

        self.save_button = tk.Button(self)
        self.save_button['state'] = 'disabled'
        self.save_button["text"] = "Save"
        self.save_button["command"] = self.saveMeasurement
        self.save_button.pack(side='left')

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot([],[],'b')
        self.ax.plot([],[],'r')
        # self.ax.axes(xlim=(0,1000),ylim=(0,1024))
        self.ax.set_xlabel("Measurement number")
        self.ax.set_ylabel("Current [bits] and Speed [Hz]")
        self.ax.set_xlim([0,1000])
        self.ax.set_ylim([0,1024])
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()        
        self.ser = None

    def connect_to_arduino(self):
        self.ser = serial.Serial(ArduinoComm, ArduinoBAUD)
        time.sleep(2)  # wait for the serial connection to initialize
        self.ser.flushInput()
        self.connected = True
        self.cal_button['state'] = 'normal'
        self.measure_button['state'] = 'normal'

    def startMeasurement(self):
        if self.ser:
            self.ser.flushInput()
            self.ser.write(b"t")  # send the measurement request
            self.ax.clear()  # clear the previous plot
            self.ax.plot([],[],'b')
            self.ax.plot([],[],'r')
            # self.ax.axes(xlim=(0,1000),ylim=(0,1024))
            self.ax.set_xlabel("Measurement number")
            self.ax.set_ylabel("Current [bits] and Speed [Hz]")
            self.ax.set_xlim([0,1000])
            self.ax.set_ylim([-500,500])
                
            self.measurementNumber = -1
            self.measurementArray = []
            self.currentArray = []
            self.speedArray = []
            self.measureAble = True
            # while(measurementNumber<999):
            #     measurementNumber = self.measure()
            self.save_button['state'] = 'normal'
        else:
            print("Please connect to the arduino first")

    def calibrateCurrent(self):
        if self.ser:
            self.ser.flushInput()
            self.ser.write(b"c")  # send the measurement request
            self.ax.clear()  # clear the previous plot
            self.measurementNumber = -1
            self.measurementArray = []
            self.currentArray = []
            self.speedArray = []
            self.measureAble = True
            # while(measurementNumber<999):
            #     measurementNumber = self.measure()
        else:
            print("Please connect to the arduino first")

    def measure(self):
        measurementNumber = -1
        while self.measureAble and (self.ser.in_waiting>0):
            data = self.ser.readline().strip()  # read the data from the serial port
            measurementNumber, current, speed = data.split(b",")  # parse the data into two variables
            measurementNumber = int(measurementNumber)
            self.measurementArray.append(measurementNumber)
            self.currentArray.append(float(current)-512)
            self.speedArray.append(-float(speed))
            # print(measurementNumber)
        else:
            print("Please connect to the arduino first")
        return measurementNumber

    def animate(self,i):
        # print("update ",i)
        if self.connected and self.measurementNumber<999:
            self.measurementNumber = self.measure()
        else:
            self.measureAble = False
        # self.ax.clear()
        self.ax.plot(self.measurementArray, self.currentArray, "b")  # create the new plot
        self.ax.plot(self.measurementArray, self.speedArray, "r")  # create the new plot
        #self.lineCur.set_data(self.measurementArray, self.currentArray)
        #self.lineSpd.set_data(self.measurementArray, self.speedArray)
        # self.canvas.draw()  # redraw the canvas

    def saveMeasurement(self):
        savefile = asksaveasfilename(filetypes=[('csv file','*.csv'),('text file','*.txt')], defaultextension='.csv')
        print(savefile)
        with open(savefile,'w') as f:
            write = csv.writer(f)
            write.writerow(['#', 'current [bits]', 'speed [Hz]'])
            for meas,curr,speed in zip(self.measurementArray,self.currentArray,self.speedArray):
                write.writerow([meas, curr, speed])

root = tk.Tk()
app = Application(master=root)
ani = animation.FuncAnimation(app.fig,app.animate, interval=10)
app.mainloop()

