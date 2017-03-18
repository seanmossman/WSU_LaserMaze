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
port = "COM4"
ser = serial.Serial(port, 9600)
buzzer = pyglet.media.load('buzzer.wav', streaming=False)
while not connected:
    serin = ser.read()
    connected = True

maze_running = False  #Global flag
start_time = 0.0      #Global time keeper

# Passcode for program exit:
Passcode = ['1']    #The actual passcode
Attempt = []    # Empty list to store users attempt at passcode
    
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
    def bMed(self):
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
        self.bQUIT["command"] = self.passcode
        self.bQUIT.grid(row=2, column=0, columnspan=2, sticky = "ew")
    def bCalibrate(self):
        self.bCalibrate = tk.Button(self, text="Calibrate", fg="green", bg="black")
        self.bCalibrate["command"] = self.calibrate
        self.bCalibrate.grid(row=2, column=2, columnspan=2,sticky="ew")
#========================================================================

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
    #==========================================================================
    # Here is the code used to generate the number pad and verify the passcode:

    def passcode(self): 
        # List of buttons for number pad
        btn_list = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3', '0']

        t = tk.Toplevel(self)
        r = 1
        c = 0
        for b in btn_list:
            # Loop through elements wanted on number pad, give each it's label
            # and command:
            cmd = lambda b=b: Attempt.append(b)
            if b == '0':
                self.b = tk.Button(t, text=b, width=10, height=5, command=cmd).grid(row=4,column=1)
            else:
                self.b = tk.Button(t, text=b, width=10, height=5, command=cmd).grid(row=r,column=c)
            c += 1
            if c > 2:
                c = 0
                r += 1
                                             
        self.Enter = tk.Button(t, text="Enter", width=10, height=5, fg="green",
                               command=self.verify).grid(row=4,column=0)        
        
        # Clears attempt in order to start from scratch
        self.Clear = tk.Button(t, text="Clear", width=10, height=5,
                               command=self.my_clear).grid(row=4,column=2)
           
        # If user decides to cancel password submission, then kill numberpad                  
        self.Cancel = tk.Button(t, text="Cancel", width=10, height=5, fg="red",
                              command=t.destroy).grid(row=4,column=3)

    def verify(self):
        # Verify the submitted password:
        global maze_running
        if Attempt == Passcode:
            # if correct, move forward
            ser.write(b'0')
            maze_running = False
            root.destroy()
        else:
            # if incorrect, clear contents and try again
            self.my_clear()
            self.wrong_pass_window()
                
    def my_clear(self):
        # empty list named Attempt
        del Attempt[:]
        
    def wrong_pass_window(self):
        w = tk.Toplevel(self)
        text = tk.Message(w, text='Try again.')
        text.pack()
        
#==============================================================================

root = tk.Tk()
root.title("Laser Maze")
root.configure(background="black")

photo_easy = tk.PhotoImage(file="./StickFigureEasy_v1.gif")
photo_med = tk.PhotoImage(file="./StickFigureMedium_v1.gif")
photo_hard = tk.PhotoImage(file="./StickFigureHard_v1.gif")
photo_random = tk.PhotoImage(file="./StickFigureRandom_v1.gif")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w,h))
root.overrideredirect(1)
#root.focus_set()


app = Application(master=root)
app.mainloop()
