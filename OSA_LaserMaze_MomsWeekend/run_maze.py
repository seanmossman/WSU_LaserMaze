import tkinter as tk
import serial
import serial.tools.list_ports
import pyglet
import _thread
import time
import sys
sys.setrecursionlimit(10000)

#==============================================================================
# Connect to the serial port
connected = False
#port = list(serial.tools.list_ports.comports())[0][0]
port = "COM3"
ser = serial.Serial(port, 9600)
buzzer = pyglet.media.load('./AudioFiles/buzzer.wav', streaming=False)
while not connected:
    serin = ser.read()
    connected = True

maze_running = False  #Global flag
start_time = 0.0      #Global time keeper
    
#==============================================================================
# Button interface: where are they and what do they do
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.pack()
        self.bEasy()
        self.bMed()
        self.bHard()
        self.bRandom()
        self.timer()
        self.bQUIT()
        self.bCalibrate()

    def bEasy(self):
        self.bEasy = tk.Button(self, bg="black")
        self.bEasy["command"] = self.easy_maze
        self.bEasy["image"] = photo_easy
        self.bEasy.grid(row=0, column=0, sticky = "nsew")
t    def bMed(self):
        self.bMed = tk.Button(self, bg="black")
        self.bMed["command"] = self.med_maze
        self.bMed["image"] = photo_med
        self.bMed.grid(row=0, column=1, sticky = "nsew")
    def bHard(self):
        self.bHard = tk.Button(self, bg="black")
        self.bHard["command"] = self.hard_maze
        self.bHard["image"] = photo_hard
        self.bHard.grid(row=0, column=2, sticky = "nsew")
    def bRandom(self):
        self.bRandom = tk.Button(self, bg="black")
        self.bRandom["command"] = self.random_maze
        self.bRandom["image"] = photo_random
        self.bRandom.grid(row=0, column=3, sticky = "nsew")
    def timer(self):
        self.timer = tk.Label(self, font=('times', 150), fg = 'green', bg='black')
        self.timer.grid(row=1, column = 0, columnspan = 4, sticky = "nsew")
        self.timer.config(text="%02d:%04.1f" % (start_time//60, start_time%60))
    def bQUIT(self):
        self.bQUIT = tk.Button(self, text="Quit", bg="black", fg="red")
        self.bQUIT["command"] = self.quit_maze
        self.bQUIT.grid(row=2, column=0, columnspan=2, sticky = "ew")
    def bCalibrate(self):
        self.bCalibrate = tk.Button(self, text="Calibrate", fg="green", bg="black")
        self.bCalibrate["command"] = self.calibrate
        self.bCalibrate.grid(row=2, column=2, columnspan=2,sticky="ew")
#========================================================================
    def quit_maze(self):
        global maze_running        
        ser.write(b'0')
        maze_running = False
        root.destroy()
        
    def easy_maze(self):
        global maze_running 
        global start_time
        start_time = time.time()
        ser.write(b'1')
        if maze_running == False:
            maze_running = True
            _thread.start_new_thread(self.monitor, ())
            _thread.start_new_thread(self.timer_run, ())
        
    def med_maze(self):
        global maze_running
        global start_time
        start_time = time.time()
        ser.write(b'2')
        time.sleep(1)
        if maze_running == False:
            maze_running = True
            _thread.start_new_thread(self.monitor, ())
            _thread.start_new_thread(self.timer_run, ())        

    def hard_maze(self):
        global maze_running
        global start_time
        start_time = time.time()
        ser.write(b'3')
        if maze_running == False:
            maze_running = True
            _thread.start_new_thread(self.monitor, ())
            _thread.start_new_thread(self.timer_run, ())    

    def random_maze(self):
        global maze_running
        global start_time
        start_time = time.time()
        ser.write(b'4')
        if maze_running == False:
            maze_running = True
            _thread.start_new_thread(self.monitor, ())
            _thread.start_new_thread(self.timer_run, ())           
    
    def calibrate(self):
        global maze_running
        ser.write(b'5')
        if maze_runnning == True:
            maze_running = False

#==========================================================================
    # Here is the code for monitoring the maze
    
    def monitor(self):
        # When a lazer beam is broken, the arduino writes '2' to the monitor.
        # When the "finish button" is pressed at the end of the maze, the arduino
        # writes '3' to the monitor.
        global maze_running
        global start_time
        # We continually monitor the maze until player finishes
        while maze_running:
            maze_input = ser.read()
            if (maze_input == b'2'):
                # If beam is broken, play buzzer
                buzzer.play()
                start_time -= 1
            if (maze_input == b'3'):
                # Stop monitoring the serial port and end monitor thread
                maze_running = False
        return
#=============================================================================
    def timer_run(self):
        global maze_running
        global start_time
        while maze_running:
            time1 = 0.0
            time2 = round(time.time()-start_time, 2)
            if time2 != time1:
                time1 = time2
                self.timer.config(text="%02d:%04.1f" % (time2//60, time2%60))
            time.sleep(0.1)

#==============================================================================

root = tk.Toplevel()
root.title("Laser Maze")
root.configure(background="black")

photo_easy = tk.PhotoImage(file="./Figures/StickFigureEasy_v1.gif")
photo_med = tk.PhotoImage(file="./Figures/StickFigureMedium_v1.gif")
photo_hard = tk.PhotoImage(file="./Figures/StickFigureHard_v1.gif")
photo_random = tk.PhotoImage(file="./Figures/StickFigureRandom_v1.gif")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w,h))
root.overrideredirect(1)
#root.focus_set()


app = Application(master=root)
app.mainloop()
