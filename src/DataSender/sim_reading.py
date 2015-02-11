# read from xml file, every 0.1s one record
# NumberSamples : how many point to display in the figure

import os, sys
import threading
import xml.etree.ElementTree as ET
import time 
from datetime import date, datetime, timedelta
import numpy as np
import matplotlib.dates as md
import pylab
from pylab import *
import Tkinter
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange

class Mythread(threading.Thread):
    def __init__(self, myId):
        self.myId = myId
        threading.Thread.__init__(self)
        
    def run(self):
        global  time_data, value, first_line
        exec_path = os.path.dirname(os.path.abspath(__file__))
        src_file_path = os.path.join(exec_path, '../../' , "SampleDATA/xml_files/")

        with open(src_file_path + 'First2.xml') as fp:
            for line in fp:
                time.sleep(0.2)
                t_data ='<root>' + line.decode() + '</root>'
                root = ET.fromstring(t_data)
                
                date = ''
                for item in root:
                    date = item.attrib["date"] + ' ' + item.attrib['time']
                    py_date = datetime.datetime.strptime(date, '%Y%m%d %H:%M')
                    print py_date
                    if first_line == False:
                        for i in reversed(range(100)):
                            pre_py_date = py_date - timedelta(minutes=i)
                            time_data.append(pre_py_date)
                            # value.append(int(item.text))                            
                            value.append(np.nan)
                            first_line = True
                    time_data.append(py_date)
                    value.append(int(item.text))                            
                    # print time_data, value
threads = []
thread = Mythread(1)
thread.start()
time_data = []
value = []
first_line = False

first_time = False
root = Tkinter.Tk()
root.wm_title("Extended Realtime Plotter")

fig = pylab.figure(1)
ax = fig.add_subplot(111)
ax.grid(True)
ax.set_title("Realtime Simulation")
ax.set_ylabel("generated power")
first_time = True
line1 = ''
# line1 = ax.plot(datetime.datetime.now(), np.nan, '-')

init_date = []
init_value = []

for i in reversed(range(100)):
    init_date.append(datetime.datetime.now() - timedelta(minutes=i))
    init_value.append(np.nan)
print init_date, init_value
ax.axis([init_date[0], init_date[-1], 0, 100])    
ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
ax.xaxis.set_major_locator(MinuteLocator(interval=5))
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.subplots_adjust(bottom=0.2)
ax.set_xlabel(datetime.datetime.now().strftime("%Y-%m-%d"))
line1 = ax.plot(init_date, init_value, '-')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

def RealtimePloter():
    global value,wRadio, first_time, line1, v
    radio_value = v.get()
    NumberSamples=min(len(value),radio_value)
    
    len_value = len(value)
    m_left_index = len_value-NumberSamples
    m_right_index = len_value - 1
    # line1[0].set_data(time_data[-NumberSamples:], value[-NumberSamples:])
    line1[0].set_data(time_data[-NumberSamples:], value[-NumberSamples:])
    ax.axis([time_data[m_left_index], time_data[m_right_index], 0, 100])    

    # ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d %H:%M') )
    # time only
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
    
    numDict2 = {'20':1, '100':5, '200':10, '300':15, '600':30}
    ax.xaxis.set_major_locator(MinuteLocator(interval=numDict2[str(radio_value)]))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.subplots_adjust(bottom=0.2)

    ax.relim()
    ax.autoscale_view(True,True,True)
    m_left_date = time_data[m_left_index].date()
    m_right_date = time_data[m_right_index].date()
    list_x_label = []
    if m_left_date == m_right_date:
        ax.set_xlabel(m_left_date.strftime("%Y-%m-%d"))
    else:
        diff_days = m_right_date - m_left_date
        int_diff_days = diff_days.days + 1
        for i in range(int_diff_days):
            date_str = (m_left_date + timedelta(days=i)).strftime("%Y-%m-%d")            
            list_x_label.append(date_str)
        ax.set_xlabel("   ".join(list_x_label))
    print('canvas draw()')
    canvas.draw()
    root.after(1000,RealtimePloter)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = Tkinter.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tkinter.BOTTOM)

Label(master=root, text="Choose a time frequency").pack(side=TOP)
numList = [('1', 20), ('5', 100), ('10', 200), ('15', 300), ('30', 600)]
v = IntVar()
v.set(100)
for radio_text, radio_value in numList:
    print "loop"
    wRadio=Tkinter.Radiobutton(master=root,text=radio_text,value=radio_value,variable =v)
    wRadio.pack(side=LEFT, anchor=W)

root.protocol("WM_DELETE_WINDOW", _quit)
root.after(1000,RealtimePloter)
Tkinter.mainloop()
