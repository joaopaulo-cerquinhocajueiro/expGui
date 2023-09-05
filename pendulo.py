# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
import serial
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize the Arduino serial connection
ser = serial.Serial('COM6', 115200, timeout=1)

# Function to send command packages to Arduino
def send_command_package(p_value):
    command_package = bytes([255, p_value, 0, 0, 0])
    ser.write(command_package)

# Function to receive measurement packages from Arduino
receiving = False
received = 0
def receive_measurement_package():
    global receiving,received
    while receiving:
        measurement_package = ser.read(5)
#         measurement_package = [255,2,120,0,0]
        if len(measurement_package) == 5 and measurement_package[0] == 255:
            angH = measurement_package[1]
            angL = measurement_package[2]
            angle = angH * 255 + angL
            print(angle)
            x1 = measurement_package[3]
            x2 = measurement_package[4]
            # Process measurement data as needed
            # You can update the plot here
            received = received + 1
        if received>= entry_t.get():
            receiving = False
            

# Function to start the communication thread
def start_communication_thread():
    receiving = True
    t = threading.Thread(target=receive_measurement_package)
    t.daemon = True
    t.start()

# Function to handle 'Rodar' button click
def rodar_button_click():
    # Get values from UI inputs
    t_value = int(entry_t.get())
    pmin_value = int(entry_pmin.get())
    pmax_value = int(entry_pmax.get())
    checkbox_value = checkbox_var.get()

    # Start communication thread to receive measurement packages
    start_communication_thread()

    # Generate P values based on checkbox selection
    if checkbox_value == 1:  # Degrau
        p_values = [pmin_value] * (t_value // 2) + [pmax_value] * (t_value // 2)
    elif checkbox_value == 2:  # PRBS
        p_values = np.random.choice([pmin_value, pmax_value], t_value , p=[0.5, 0.5])
    elif checkbox_value == 3:  # PRBS
        prbs_sequence = np.random.choice([pmin_value, pmax_value], t_value // 2, p=[0.5, 0.5])
        p_values = np.concatenate([np.array([pmin_value] * (t_value // 2)), prbs_sequence])
    else:
        p_values = [0]*t_value
    # Send command packages to Arduino
    for p_value in p_values:
        send_command_package(p_value)
        time.sleep(1 / 100)  # Send 100 packages per second
        print(p_value)

def update_plot(time_values, p_values, angle_values):
    ax.clear()
    ax.plot(time_values, p_values, label='P')
    ax.plot(time_values, angle_values, label='Angle')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    canvas.draw()

# Create the UI
root = tk.Tk()
root.title("Arduino Control UI")

# Create UI components
entry_t = tk.Entry(root)
entry_t.insert(0, 100)
entry_pmin = tk.Entry(root)
entry_pmin.insert(0, 100)
entry_pmax = tk.Entry(root)
entry_pmax.insert(0, 120)
checkbox_var = tk.IntVar()
checkbox_degrau = tk.Checkbutton(root, text="Degrau", variable=checkbox_var, onvalue=1)
checkbox_prbs = tk.Checkbutton(root, text="PRBS", variable=checkbox_var, onvalue=2)
checkbox_both = tk.Checkbutton(root, text="Ambos", variable=checkbox_var, onvalue=3)
button_rodar = tk.Button(root, text="Rodar", command=rodar_button_click)

# Layout UI components using grid layout
entry_t.grid(row=0, column=0)
entry_pmin.grid(row=0, column=1)
entry_pmax.grid(row=0, column=2)
checkbox_degrau.grid(row=1, column=0)
checkbox_prbs.grid(row=1, column=1)
checkbox_both.grid(row=1, column=2)
button_rodar.grid(row=2, column=1)

# Create the plot
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=3, columnspan=3)

# Start the main UI loop
root.mainloop()
ser.close()