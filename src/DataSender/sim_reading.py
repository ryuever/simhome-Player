# read from xml file, every 0.1s one record

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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange

time_data = []

value = []
first_line = False
class Mythread(threading.Thread):
    def __init__(self, myId):
        self.myId = myId
        threading.Thread.__init__(self)
        
    def run(self):
        global  time_data, value, first_line
        exec_path = os.path.dirname(os.path.abspath(__file__))
        src_file_path = os.path.join(exec_path, '../../' , "SampleDATA/xml_files/")
        # print "src_file_path : ", src_file_path

        with open(src_file_path + 'First.xml') as fp:
            for line in fp:
                time.sleep(0.2)
                # print line
                t_data ='<root>' + line.decode() + '</root>'
                root = ET.fromstring(t_data)
                
                date = ''
                for item in root:
                    date = item.attrib["date"] + ' ' + item.attrib['time']
                    # print date
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

root = Tkinter.Tk()
root.wm_title("Extended Realtime Plotter")

xAchse=pylab.arange(0,100,1)
yAchse=pylab.array([0]*100)

fig = pylab.figure(1)
ax = fig.add_subplot(111)
ax.grid(True)
ax.set_title("Realtime Simulation")

ax.set_ylabel("generated power")
# ax.axis([0,100,-1.5,1.5])
# ax.plot(xAchse,yAchse,'-')

# plt.plot([1,2,3], [3,4,5])
line1 = ax.plot(time_data, value, '-')
# line1=ax.plot(xAchse,yAchse,'-')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()
canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

def RealtimePloter():
    global value,wScale,wScale2
    NumberSamples=min(len(value),wScale.get())
    
    print value
    print time_data
    len_value = len(value)
    m_left_index = len_value-NumberSamples
    m_right_index = len_value - 1
    line1[0].set_data(time_data[-NumberSamples:], value[-NumberSamples:])
    ax.axis([time_data[m_left_index], time_data[m_right_index], 0, 100])    

    # ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d %H:%M') )
    # time only
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
    ax.xaxis.set_major_locator(MinuteLocator(interval=5))
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
    canvas.draw()
    root.after(1000,RealtimePloter)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = Tkinter.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tkinter.BOTTOM)

wScale = Tkinter.Scale(master=root,label="View Width:", from_=3,
                       to=1000,sliderlength=30, orient=Tkinter.HORIZONTAL)
wScale2 = Tkinter.Scale(master=root,label="Generation Speed:", from_=1,
                        to=200,sliderlength=30, orient=Tkinter.HORIZONTAL)
wScale2.pack(side=Tkinter.BOTTOM)
wScale.pack(side=Tkinter.BOTTOM)

wScale.set(100)
wScale2.set(wScale2['to']-10)

root.protocol("WM_DELETE_WINDOW", _quit)  #thanks aurelienvlg
# root.after(100,SinwaveformGenerator)
root.after(1000,RealtimePloter)
Tkinter.mainloop()
#pylab.show()



# fig = plt.figure()
# ax = fig.add_subplot(111)
# y_min, y_max = ax.get_ylim()
# ticks = [(tick - y_min)/(y_max - y_min) for tick in ax.get_yticks()]
# ax.tick_params(direction='out', length=6, width=2, colors='r')
# x = [1, 3, 5]
# y = [4, 5, 7]
# plt.plot(x,y)


# ax.xaxis.set_tick_params(width=15)
# ax.tick_params(direction='out', length=6, width=2, colors='r')

# ax.tick_params(direction='out', pad=50)
# >>> plt.show()

