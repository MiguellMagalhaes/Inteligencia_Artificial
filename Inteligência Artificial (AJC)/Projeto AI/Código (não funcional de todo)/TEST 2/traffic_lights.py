#import tkinter as tk
from tkinter import *
import time
import logging

logging.basicConfig(filename='lol.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
traffic_lights = Tk()
traffic_lights.title("Teste")
traffic_lights.geometry("600x800+600+150")
traffic_lights.resizable(False, False)
traffic_lights.iconbitmap("")
traffic_lights.config(bg="#4ea6a1")

myCanvas = Canvas(traffic_lights, height=800, width=600, bg="White")
myCanvas.pack()

#First traffic light
myCanvas.create_text(150, 36, text="Traffic Light nº 1")
myCanvas.create_rectangle(100, 50, 200, 350, fill="#4ea6a1", width=2)

#Second traffic light
myCanvas.create_text(350, 36, text="Traffic Light nº 2")
myCanvas.create_rectangle(300, 50, 400, 350, fill="#4ea6a1", width=2)

a=10
#Entry numero do semaforo + luz do semaforo + estado da luz
entry1A1 = myCanvas.create_oval(100, 50, 200, 150, fill="Green", width=2)
entry1A0 = myCanvas.create_oval(100, 50, 200, 150, fill="Black", width=2)
entry1B1 = myCanvas.create_oval(300, 250, 400, 350, fill="Orange", width=2)
entry1B0 = myCanvas.create_oval(300, 250, 400, 350, fill="Black", width=2)
entry1C1 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)
entry1C0 = myCanvas.create_oval(300, 250, 400, 350, fill="Black", width=2)

entry2A1 = myCanvas.create_oval(300, 250, 400, 350, fill="Green", width=2)
entry2A0 = myCanvas.create_oval(300, 250, 400, 350, fill="Black", width=2)
entry2B1 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)
entry2B0 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)
entry2C1 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)
entry2C0 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)

while True:
    def green():
        logging.info("Green light status:1")
        for i in range(a):
            green = myCanvas.create_oval(100, 50, 200, 150, fill="Green", width=2)
            entry2C1
            traffic_lights.update()
            time.sleep(0.50)
        #for i in range(a):
          #  red2 = myCanvas.create_oval(300, 250, 400, 350, fill="Red", width=2)
          #  traffic_lights.update()
          #  time.sleep(0.50)

    def greenb():
        logging.info("Green light status:0")
        for i in range(a):
            greenb = myCanvas.create_oval(100, 50, 200, 150, fill="Black", width=2)
            redb2 = myCanvas.create_oval(300, 250, 400, 350, fill="Black", width=2)
            traffic_lights.update()
            time.sleep(0.00001)
    
    def orange():
        logging.info("Orange light status:1")    
        for i in range(a):
            orange = myCanvas.create_oval(100, 150, 200, 250, fill="Orange", width=2)
            orange2 = myCanvas.create_oval(300, 150, 400, 250, fill="Orange", width=2)
            traffic_lights.update()
            time.sleep(0.1)
    
    def orangeb():
        logging.info("Orange light status:0")
        for i in range(a):
            orangeb = myCanvas.create_oval(100, 150, 200, 250, fill="Black", width=2)
            orangeb2 = myCanvas.create_oval(300, 150, 400, 250, fill="Black", width=2)
            traffic_lights.update()
            time.sleep(0.00001)
    
    def red():
        logging.info("Red light status:1")
        for i in range(a):
            red = myCanvas.create_oval(100, 250, 200, 350, fill="Red", width=2)
            green2 = myCanvas.create_oval(300, 50, 400, 150, fill="Green", width=2)
            traffic_lights.update()
            time.sleep(0.50)
    
    def redb():
        logging.info("TF1: Red light status:0")
        logging.info("TF2: Green light status:0") 
        for i in range(a):
            redb = myCanvas.create_oval(100, 250, 200, 350, fill="Black", width=2)
            greenb2 = myCanvas.create_oval(300, 50, 400, 150, fill="Black", width=2)
            traffic_lights.update()
            time.sleep(0.00001)
    green()
    greenb()
    orange()
    orangeb()
    red()
    redb()
traffic_lights.mainloop()