# TODO: Fix how times are displayed on sidebar

import tkinter as tk
from tkinter import X,N,E,S,W, END
import time
import datetime
import pandas as pd

# App is divided into a timer class which does the timekeeping and the Application class which handles 
# the display on tkinter
class Timer:

    def __init__(self, running = False):
        # Initialize object variables
        self.startTime = 0
        self.endTime = 0
        self.totalTime = 0

        # Initial state is timer stopped and not paused - Paused is a state within running
        self.timerRunning = False
        self.timerPaused = False
        self.timeElapsed = 0             # Used to update the start time after a pause

        # If time is started from instantiation, start it
        if (running == True):
            self.timerRunning = True
            self.startTime = time.time()

    # Starts timer
    def startTimer(self):
        if (self.timerRunning == False):
            self.timerRunning = True
            self.startTime = time.time()

    # Stops timer, resets variables for next start. Updates total running time
    def stopTimer(self):
        if (self.timerRunning == True):
            self.endTime = time.time()                          # Activity ends now
            if (self.timerPaused == True):
                self.totalTime = self.timeElapsed               # If stopping during a pause, total time of activity was calculated when pause started
            else:
                self.totalTime = self.endTime - self.startTime  # If stopping when not paused, calculate time of activity

            # Reset to start state
            self.startTime = 0
            self.endTime = 0
            self.timerRunning = False
            self.timerPaused = False
            self.timeElapsed = 0
    
    # Pauses timer
    def pauseTimer(self):
        if (self.timerRunning == True):
            if (self.timerPaused == False):
                self.timerPaused = True
                self.timeElapsed = time.time() - self.startTime     # Calculate running time to compensate for time passed while paused
            else:
                self.timerPaused = False
                self.startTime =  time.time() - self.timeElapsed     # Set start time to account for time that we were paused

    # How much time has timer been running minus time paused
    def getTimeElapsed(self):
        if (self.timerRunning == True):
            if (self.timerPaused == True):
                return self.timeElapsed
            else:
                return (time.time() - self.startTime)
        else:
            return self.totalTime

    # Is the timer running
    def active(self):
        return self.timerRunning

    # Is the timer paused
    def paused(self):
        return self.timerPaused

# Class to record time recording activity
class timerRecord:
    filename = "TimeRecord.csv"
    def __init__(self):
        self.workStart = []
        self.workEnd = []
        self.workLength = []
        self.workActivity = []
        self.stoppage = []

    def addRow(self, start, end, length, activity, thisStoppage = True):
        self.workStart.append(start)
        self.workEnd.append(end)
        self.workLength.append(length)
        self.workActivity.append(activity)
        self.stoppage.append(thisStoppage)

    def addRowList(self, timeRow):
        self.workStart.append(timeRow[0])
        self.workEnd.append(timeRow[1])
        self.workLength.append(timeRow[2])
        self.workActivity.append(timeRow[3])
        self.stoppage.append(timeRow[4])


    def removeRowIndex(self, index):
        self.workStart.pop(index)
        self.workEnd.pop(index)
        self.workLength.pop(index)
        self.workActivity.pop(index)
        self.stoppage.pop(index)
    
    def writeOut(self):
        timerData = {"start":self.workStart, "end":self.workEnd, "length":self.workLength, "activity":self.workActivity, "stoppage":self.stoppage}
        df = pd.DataFrame(timerData, columns = ["start", "end", "length", "activity", "stoppage"])
        df.to_csv(self.filename, sep=",",na_rep='', index=False)

    def loadFile(self):
        try:
            df = pd.read_csv(self.filename, sep = ",", index_col = None)
        except FileNotFoundError:
            print("Time Record file not found. Continuing without it.")
            self.workStart = []
            self.workEnd = []
            self.workLength = []
            self.workActivity = []
            self.stoppage = []
        else:
            self.workStart = df["start"].tolist()
            self.workEnd = df["end"].tolist()
            self.workLength = df["length"].tolist()
            self.workActivity = df["activity"].tolist()
            self.stoppage = df["stoppage"].tolist()

class Application(tk.Frame):
    def __init__(self, timer, record, master=None):
        super().__init__(master)
        self.timer = timer
        self.record = record
        self.timeLabel = tk.StringVar()         # StringVar allows us to force automatic label update when changed
        self.blinker = False                    # Blinking variable for bar when paused

        # Variables to keep start and end time for writing out
        self.sessionStart = 0
        self.sessionStop = 0

        # tkinter initiate widgets and grid layout
        self.create_widgets()
        self.grid()

        # Set automatic update for timer display and flasher for pause bar
        self.after(100, self.updateTimeDisplay, myTimer)
        self.after(500, self.updateBlinker, myTimer)

        # load data from existing timeRecord file
        self.record.loadFile()
        self.loadListBoxEntries()

    def startButton(self):
        self.timer.startTimer()
        self.sessionStart = time.time()
        #datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def stopButton(self):
        self.timer.stopTimer()
        self.sessionStop = time.time()
        #self.sessionStop = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        activityLength = int(myTimer.getTimeElapsed())
        activityLengthStr = str(int(activityLength))
        #str(activityLength/3600)+":"+str((activityLength%3600)/60)+":"+str(int(activityLength%3600)%60)
        #self.newRow = [self.sessionStart, self.sessionStop, datetime.timedelta(seconds=int(myTimer.getTimeElapsed())), self.activity_name.get(), True ]
        self.newRow = [self.sessionStart, self.sessionStop, activityLengthStr, self.activity_name.get(), True ]
        self.record.addRowList(self.newRow)
        self.loadListBoxEntries()                        # Refresh the list

    def quitButton(self):
        self.record.writeOut()
        root.destroy()

    # Create layout and buttons
    def create_widgets(self):
        self.left_top_frame = tk.Frame(root, width=210, height=50, pady=3, padx=3)
        self.left_center_frame = tk.Frame(root, width=210, height=40, padx=3, pady=3)
        self.right_frame = tk.Frame(root, width=50, height=130, pady=3, padx = 5)
        self.btm_frame = tk.Frame(root, width=200, height=40, pady=3, padx = 5)

        self.left_top_frame.grid(row=0, column=0, sticky=N+S+E+W)
        self.left_center_frame.grid(row=1, column=0, sticky=N+S+E+W)
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)
        self.btm_frame.grid(row=2, column=0, columnspan=2, sticky=E)


        self.time_display = tk.Label(self.left_top_frame, textvariable = self.timeLabel, bg = "white", font=("Consolas", 36), padx=10)
        self.time_display.grid(row=0, sticky=N+S+E+W)

        self.status_indicator = tk.Label(self.left_top_frame, text = "Stopped", fg = "white", bg="red", font=("Consolas", 8))
        self.status_indicator.grid(row=1, sticky=N+S+E+W)

        self.pause_button = tk.Button(self.left_center_frame, font=("Consolas", 16), width = 16, pady=2)
        self.pause_button.grid(row=0, columnspan=2, sticky=N+S+E+W)
        self.pause_button["text"] = "Pause"
        self.pause_button["command"] = self.timer.pauseTimer

        self.start_button = tk.Button(self.left_center_frame, font=("Consolas", 16))
        self.start_button.grid(row=1, column = 0, sticky=N+S+E+W)
        self.start_button["text"] = "Start"
        self.start_button["command"] = self.startButton

        self.stop_button = tk.Button(self.left_center_frame, font=("Consolas", 16))
        self.stop_button.grid(row=1, column = 1, sticky=N+S+E+W)
        self.stop_button["text"] = "Stop"
        self.stop_button["command"] = self.stopButton

        self.activity_label = tk.Label(self.right_frame, text = "Activity", font=("Consolas", 8))
        self.activity_label.grid(row=0, column = 0)
        
        self.activity_name = tk.Entry(self.right_frame, font=("Consolas", 10), width = 50)
        self.activity_name.grid(row=1, column = 0, sticky=N+S+E+W)

        self.scrollbar = tk.Scrollbar(self.right_frame)
        self.scrollbar.grid(row=2, column=2, sticky=N+S)

        self.work_list = tk.Listbox(self.right_frame, font=("Consolas", 8), width = 50, yscrollcommand=self.scrollbar.set)
        self.work_list.grid(row = 2, column=0, columnspan=2, sticky=N+S+E+W)

        self.scrollbar.config(command=self.work_list.yview)

        self.quit = tk.Button(self.btm_frame, text="QUIT", fg="red", font=("Consolas", 12))
        self.quit.grid(row=0, sticky=E)
        self.quit["command"] = self.quitButton

    def loadListBoxEntries(self):
        self.work_list.delete(0, END)
        for i in range(0,len(self.record.workStart)):
            lengthHMS = [int(int(self.record.workLength[i])/3600), int((int(self.record.workLength[i])%3600)/60), int((int(self.record.workLength[i])%3600)%3600)]
            currentEntry = str(self.record.workActivity[i]) + " | " +f"{lengthHMS[0]:02d}:{lengthHMS[1]:02d}:{lengthHMS[2]:02d}"+ " | " + datetime.datetime.fromtimestamp(self.record.workStart[i]).strftime('%Y-%m-%d %H:%M:%S') + " - " + datetime.datetime.fromtimestamp(self.record.workEnd[i]).strftime('%H:%M:%S')
            #currentEntry = str(self.record.workActivity[i]) + " | " +
            #currentEntry = str(self.record.workActivity[i]) + " | " + datetime.date.strftime(datetime.datetime.strptime(self.record.workStart[i], '%Y-%m-%d %H:%M:%S'), '%d-%b-%y, %H:%M') + " | " + datetime.date.strftime(datetime.datetime.strptime(self.record.workEnd[i], '%Y-%m-%d %H:%M:%S'), '%d-%b-%y, %H:%M')+" | " + str(self.record.workLength[i])
            self.work_list.insert(END,currentEntry)


    # Updates the label, reattaches the after function, enables/disables button based on timer state
    def updateTimeDisplay(self, myTimer):
        self.timeLabel.set(str(datetime.timedelta(seconds=int(myTimer.getTimeElapsed()))))

        self.after(100, self.updateTimeDisplay, myTimer)

        if (myTimer.active() == True):
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state = "normal")
            self.pause_button.configure(state="normal")
            if (myTimer.paused() == True):
                self.pause_button["text"] = "Unpause"
            else:
                self.pause_button["text"] = "Pause"
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.pause_button.configure(state="disabled")

    # Sets the blinker function to blink the pause bar and reattach the after function
    def updateBlinker(self, myTimer):
        self.blinker = not self.blinker
        self.after(500, self.updateBlinker, myTimer)

        if (myTimer.active() == True):
            if (myTimer.paused() == True):
                if(self.blinker):
                    self.status_indicator.configure(text="Paused", bg="yellow", fg="black")
                else:
                    self.status_indicator.configure(text="Paused", bg="white", fg="black")
            else:
                self.status_indicator.configure(text="Counting", bg="green", fg="black")
        else:
                self.status_indicator.configure(text="Stopped", bg="red", fg="white")


root = tk.Tk()
root.geometry('{}x{}'.format(590, 230))

root.title("Work Clock")
root.resizable(False, False)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
myTimer = Timer(False)
myRecord = timerRecord()
app = Application(myTimer, myRecord, master=root)
app.mainloop()