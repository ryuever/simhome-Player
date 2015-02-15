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
import matplotlib

def _quit(window):
    # window.quit()     # stops mainloop
    window.destroy()

def sim_plotting(master, datetime_list, value_list):
    fig = pylab.figure(1)
    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title("Query simulation")
    ax.set_ylabel("generated power")
    ax.axis([datetime_list[0], datetime_list[-1], 0, 100])    
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
    ax.xaxis.set_major_locator(MinuteLocator(interval=5))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.subplots_adjust(bottom=0.2)
    ax.plot(datetime_list, value_list, '-')
    window = Tkinter.Toplevel(master)
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.show()
    canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
    toolbar = NavigationToolbar2TkAgg(canvas, window)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
    button = Tkinter.Button(master=window, text='Quit', command=lambda:_quit(window))
    button.pack(side=Tkinter.BOTTOM)

    Label(master=window, text="Choose a time frequency").pack(side=TOP)

class SimProcessing():
    def __init__(self, window_title, root):
        # create initial data for simulation plotting
        self.init_date = []
        self.init_value = []
        for i in reversed(range(100)):
            self.init_date.append(datetime.datetime.now() - timedelta(minutes=i))
            self.init_value.append(np.nan)

        self.root = Toplevel(root)
        self.root.wm_title(window_title)
        self.fig = pylab.figure(1)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        self.ax.set_title("Realtime Simulation")
        self.ax.set_ylabel("generated power")
        self.line1 = ''
        # print self.init_date, self.init_value
        self.ax.axis([self.init_date[0], self.init_date[-1], 0, 100])    
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
        self.ax.xaxis.set_major_locator(MinuteLocator(interval=5))
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.subplots_adjust(bottom=0.2)
        self.ax.set_xlabel(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.line1 = self.ax.plot(self.init_date, self.init_value, '-')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.show()

        self.canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root )
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
        self.button = Tkinter.Button(master=self.root, text='Quit', command=self._quit)
        self.button.pack(side=Tkinter.BOTTOM)

        Label(master=self.root, text="Choose a time frequency").pack(side=TOP)
        numList = [('1', 20), ('5', 100), ('10', 200), ('15', 300), ('30', 600)]
        self.v = IntVar()
        self.v.set(100)
        for radio_text, radio_value in numList:
            print "SimProcessing : __init__ : radio button loop"
            wRadio=Tkinter.Radiobutton(master=self.root,text=radio_text,value=radio_value,variable =self.v)
            wRadio.pack(side=LEFT, anchor=W)

    def realtimePloter(self, time_data, value):
        print "real time simulation in realtimeploter"
        radio_value = self.v.get()
        NumberSamples=min(len(value),radio_value)
    
        len_value = len(value)
        m_left_index = len_value-NumberSamples
        m_right_index = len_value - 1

        self.line1[0].set_data(time_data[-NumberSamples:], value[-NumberSamples:])
        self.ax.axis([time_data[m_left_index], time_data[m_right_index], 0, 100])    

        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M') )
    
        numDict2 = {'20':1, '100':5, '200':10, '300':15, '600':30}
        self.ax.xaxis.set_major_locator(MinuteLocator(interval=numDict2[str(radio_value)]))
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.subplots_adjust(bottom=0.2)

        self.ax.relim()
        self.ax.autoscale_view(True,True,True)
        m_left_date = time_data[m_left_index].date()
        m_right_date = time_data[m_right_index].date()
        list_x_label = []
        if m_left_date == m_right_date:
            self.ax.set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        else:
            diff_days = m_right_date - m_left_date
            int_diff_days = diff_days.days + 1
            for i in range(int_diff_days):
                date_str = (m_left_date + timedelta(days=i)).strftime("%Y-%m-%d")            
                list_x_label.append(date_str)
            self.ax.set_xlabel("   ".join(list_x_label))
        print('canvas draw()')
        self.canvas.draw()
        self.root.after(1000,self.realtimePloter, time_data, value)

    def _quit(self):
        # self.root.quit()     # stops mainloop
        self.root.destroy()

    def start(self, time_data, value):
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.after(1000,self.realtimePloter, time_data, value)
        # Tkinter.mainloop()
        self.root.mainloop()


if __name__=='__main__':
    sim_object = SimProcessing()
    sim_object.realtimePloter()
    sim_object.start()
