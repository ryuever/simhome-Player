import sys,io, os
from socket import *                # portable socket interface plus constants
from Tkinter import *
import Tkinter
import threading
from SimProcessing import *
from xml_operations import *
import time 
from datetime import date, datetime, timedelta
import dateutil.relativedelta
import numpy as np
from tk_calendar import *
from CalendarDialog import *

# import socket
# from SimProcessing import *

# for single client
if len(sys.argv) == 3:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
else:
    serverHost = 'localhost'
    serverPort = '50000'

# # for multi-clients
# if len(sys.argv) == 3:
#     print('first')
#     serverHost = sys.argv[1]
#     serverPort = sys.argv[2]
#     indicator = sys.argv[3]
# else:
#     print("second")
#     serverHost = 'localhost'
#     serverPort = '50000'
#     indicator = sys.argv[1]
#     print(serverHost, serverPort, indicator)

def recvall(sock):
    recv_data = sock.recv(1024)
    for i in range(len(recv_data)):
        if recv_data[i] == ' ':       # the item before space indicate length b' '= 32
            break
    
    recv_len = recv_data[:i]
    # data = b'' + recv_data[i + 1:]
    data = recv_data[i + 1:]

    amount_received = len(data)
    amount_expected = eval(recv_len)
    
    while amount_received < amount_expected:
        more = sock.recv(1024)
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (amount_expected, amount_received))
        data += more
        amount_received += len(more)
    return data

# arguments should be datetime object
def inquery_request(root, datetime_start, datetime_end):
    datetime_start_str = datetime_start.strftime("%Y-%m-%d %H:%M")
    datetime_end_str = datetime_end.strftime("%Y-%m-%d %H:%M")

    request = 'control <root method="inquery"><value send="" datetime_start="' \
              + datetime_start_str + '" datetime_end="' + datetime_end_str + '"></value></root>'
    b_request = request.encode()
    b_request_len = len(b_request)
    print request
    sockobj.sendall(str(b_request_len).encode() + b' ' + b_request)
    recv_data = recvall(sockobj)
    print recv_data.decode()
    splited_data = recv_data.decode().split("=")
    datetime_data = splited_data[0]
    datetime_temp_list = datetime_data.strip('[]').split(',')
    datetime_list = []
    for item in datetime_temp_list:
        print item
        datetime_list.append(datetime.strptime(item.strip(" '"),"%Y-%m-%d %H:%M"))
    print datetime_list

    value_data = splited_data[1]
    value_temp_list = value_data.strip('[]').split(',')
    value_list = []
    for item in value_temp_list:
        value_list.append(int(item.strip(" '")))
    print value_list

    sim_plotting(root, datetime_list, value_list)

def onclick(clicked_button, root, selected_date):
    cd = CalendarDialog(root)

    # cd is a datetime
    selected_date = cd.result.strftime("%Y-%m-%d")
    print "selected_date : ", selected_date
    clicked_button.config(text=selected_date)
    print cd.result

def send_xml_every_second():
    global first_line, time_data, value
    exec_path = os.path.dirname(os.path.abspath(__file__))
    src_file_path = os.path.join(exec_path, '../../' , "SampleDATA/xml_files/")

    with open(src_file_path + 'First2.xml') as fp:
        for line in fp:
            time.sleep(0.1)
            # print line
            xml_text = line.encode()
            xml_len  = len(xml_text)
            sockobj.sendall(str(xml_len).encode() + b' ' +xml_text)

            xml_sender, xml_date, xml_time, xml_value = single_xml2lst(line)
            py_date = datetime.strptime(xml_date + ' ' + xml_time,  '%Y%m%d %H:%M')            
            # print 'py_date : ', py_date
            if first_line == False:
                for i in reversed(range(100)):
                    pre_py_date = py_date - timedelta(minutes=i)
                    time_data.append(pre_py_date)
                    value.append(np.nan)
                    first_line = True
            time_data.append(py_date)
            value.append(xml_value.encode())

def start_real_time_sim(root, time_data, value):
    print 'come to sim'
    sim_object = SimProcessing("Realtime Simulation on Client", root)
    sim_object.start(time_data, value)

def datetime_duration_submit(date_start_button,
                             date_end_button,
                             time_start_hr_var,
                             time_start_min_var,
                             time_end_hr_var,
                             time_end_min_var):
    print date_start_button['text']
    print date_end_button['text']
    datetime_start_time_hr = time_start_hr_var.get()
    datetime_start_time_min = time_start_min_var.get()
    datetime_end_time_hr = time_end_hr_var.get()
    datetime_end_time_min = time_end_min_var.get()

    datetime_start = date_start_button['text'] + ' ' + datetime_start_time_hr + ":" + datetime_start_time_min
    datetime_end = date_end_button['text'] + ' ' + datetime_end_time_hr + ":" + datetime_end_time_min
    print "datetime_start, datetime_end", datetime_start, datetime_end
    print type(datetime.strptime(datetime_start, "%Y-%m-%d %H:%M"))
    print datetime.strptime(datetime_end, "%Y-%m-%d %H:%M")
    
    # inquery_request(datetime_start, datetime_end)
    inquery_request(root, datetime.strptime(datetime_start, "%Y-%m-%d %H:%M"), datetime.strptime(datetime_end, "%Y-%m-%d %H:%M"))
    
def cre_ctrl_panel(root):
    root.wm_title("Simulation Control Panel -- Client")
    root.minsize(width=666, height=666)
    buttonRow = Frame(root)

    cur = datetime.now()
    button1_timestamp = datetime.now() - timedelta(days=7)
    button2_timestamp = datetime.now() - dateutil.relativedelta.relativedelta(months=-1)
    button3_timestamp = datetime.now() - dateutil.relativedelta.relativedelta(months=-6)
    
    button1 = Tkinter.Button(master=buttonRow, text='recent one week',
                             command=lambda:inquery_request(root, button1_timestamp, cur))
    button1.grid(row=0, column=0)
    button2 = Tkinter.Button(master=buttonRow, text='last month',
                             command=lambda:inquery_request(root, button2_timestamp, cur))
    button2.grid(row=0, column=1)
    button3 = Tkinter.Button(master=buttonRow, text='last six monthes',
                             command=lambda:inquery_request(root, button3_timestamp, cur))
    button3.grid(row=0, column=2)
    button4 = Tkinter.Button(master=buttonRow, text='realtime simulation',
                             command=lambda:start_real_time_sim(root, time_data, value))
    button4.grid(row=0, column=3)
    buttonRow.grid(row=0, column=0)
    
    # usd to specify a datetime duration
    time_hr_option = []
    time_min_option = []
    for i in range(23):
        time_hr_option.append("{0:0=2d}".format(i))

    for i in range(59):
        time_min_option.append(i+1)

    # for datetime using variables
    datetime_start_date = ''
    datetime_end_date = ''
    
    # datetime_duration_frame = Frame(root,borderwidth=10, highlightbackground=COLOR)
    datetime_duration_frame = Frame(root, borderwidth = 1, relief = SUNKEN, pady=20)
    Label(master=datetime_duration_frame, text="choose a timestamp").grid(row=0, column=2)

    today = date.today().strftime("%Y-%m-%d")
    # starting datetime
    datetime_start_label = Label(datetime_duration_frame, text="start time").grid(row=1, column=0)
    date_start_button = Tkinter.Button(datetime_duration_frame, text=today,
                                       command=lambda:onclick(date_start_button, root, datetime_start_date))
    date_start_button.grid(row=1,column=1)
    time_start_hr_var = StringVar(datetime_duration_frame)
    time_start_hr_var.set("00") # default value
    time_start_hr = apply(OptionMenu, (datetime_duration_frame, time_start_hr_var) + tuple(time_hr_option))
    time_start_hr.grid(row=1, column=2)
    time_start_min_var = StringVar(datetime_duration_frame)
    time_start_min_var.set("00") # default value
    time_start_min = apply(OptionMenu, (datetime_duration_frame, time_start_min_var) + tuple(time_min_option))
    time_start_min.grid(row=1, column=3)
    
    # end datetime 
    datetime_end_label = Label(datetime_duration_frame, text="end time").grid(row=2, column=0)
    date_end_button = Tkinter.Button(datetime_duration_frame, text=today,
                                     command=lambda:onclick(date_end_button, root, datetime_end_date))
    date_end_button.grid(row=2,column=1)
    time_end_hr_var = StringVar(datetime_duration_frame)
    time_end_hr_var.set("00") # default value
    time_end_hr = apply(OptionMenu, (datetime_duration_frame, time_end_hr_var) + tuple(time_hr_option))
    time_end_hr.grid(row=2, column=2)
    time_end_min_var = StringVar(datetime_duration_frame)
    time_end_min_var.set("00") # default value
    time_end_min = apply(OptionMenu, (datetime_duration_frame, time_end_min_var) + tuple(time_min_option))
    time_end_min.grid(row=2, column=3)

    datetime_submit = Tkinter.Button(master=datetime_duration_frame, text='submit',
                                    command=lambda:datetime_duration_submit(date_start_button, date_end_button,
                                                                            time_start_hr_var, time_start_min_var,
                                                                            time_end_hr_var, time_end_min_var))
    datetime_submit.grid(row=3, column=0)
    datetime_quit = Tkinter.Button(master=datetime_duration_frame, text='reset',
                                   command=lambda:datetime_duration_quit())
    datetime_quit.grid(row=3, column=2)
    datetime_duration_frame.grid(row=5, column=0)                                    
    root.mainloop()
    

time_data = []
value = []
first_line = False

sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
print("serverHost : ",serverHost)
print("port : ", serverPort)
sockobj.connect((serverHost, eval(serverPort)))   # connect to server machine + port

# create_control_panel = threading.Thread(name='create control panel', target=cre_ctrl_panel)
# create_control_panel.start()


send_data = threading.Thread(name='send to server xml data every second', target=send_xml_every_second)
send_data.start()

root = Tk()
cre_ctrl_panel(root)


print 'not reach'
# if len(sys.argv) > 1:       
#     serverHost = sys.argv[1]                # server from cmd line arg 1
#     if len(sys.argv) > 2:                   # text from cmd line args 2..n
#         message = (x.encode() for x in sys.argv[2:])  



# # for single clients
# recv_data = recvall(sockobj)
# print('Client received:\n')
# print(recv_data.decode().strip())
# sockobj.close()                             # close socket to send eof to server        

# # for multi-clients
# recv_data = recvall(sockobj)
# export_file = "process{}.txt".format(eval(indicator))
# fp = open(export_file, "w")
# print('Client received:\n')
# print(recv_data.decode())
# fp.write(recv_data.decode())
# sockobj.close()                             # close socket to send eof to server        


# for matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import time 
import numpy as np
import matplotlib.dates as md

recv_data = recvall(sockobj)
import xml.etree.ElementTree as ET
t_data ='<root>' + recv_data.decode() + '</root>'
root = ET.fromstring(t_data)

date = ''
time_data = []
value = []
for item in root:
    date = item.attrib["date"] + ' ' + item.attrib['time']
    py_date = datetime.strptime(date, '%Y%m%d %H:%M')
    time_data.append(py_date)
    value.append(int(item.text))
print time_data, value


from matplotlib.dates import MinuteLocator
fig, ax = plt.subplots()
plt.plot(time_data, value)
print 'time_data[0] : ', time_data[0]
print 'time_data[len(time_data) - 1] : ', time_data[len(time_data) - 1]
ax.axis([time_data[100], time_data[len(time_data) - 1], 0, 100])
ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d %H:%M') )
# ax.xaxis.set_major_locator(MinuteLocator(interval=30))
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.subplots_adjust(bottom=0.2)

# ax.set_ylim([0, 25])
plt.show()

# for i in range(5):
#     print time[i], value[i]
#     time.append(time[i])
sockobj.close()
