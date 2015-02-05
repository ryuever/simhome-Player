import sys,io, os
from socket import *                # portable socket interface plus constants
import time
from Tkinter import *
import Tkinter
import threading

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

def send_xml_every_second():
    exec_path = os.path.dirname(os.path.abspath(__file__))
    src_file_path = os.path.join(exec_path, '../../' , "SampleDATA/xml_files/")

    with open(src_file_path + 'First2.xml') as fp:
        for line in fp:
            time.sleep(0.1)
            print line
            xml_text = line.encode()
            xml_len  = len(xml_text)
            sockobj.sendall(str(xml_len).encode() + b' ' +xml_text)

sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
print("serverHost : ",serverHost)
print("port : ", serverPort)
sockobj.connect((serverHost, eval(serverPort)))   # connect to server machine + port            
childPid = os.fork()
if childPid == 0:
    print "in child process"
    send_xml_every_second()
    print "in child process : send successful"
else:
    print "in main process"
    time.sleep(1)
    text = '''control
    <root method='inquery'>
    <value sender = "" date="" time="13:14" flag='1-min'></value>
    <value sender = "" date="" time="23:54" flag='1-max'></value>
    </root>'''
    b_text = text.encode()
    b_len  = len(b_text)
    sockobj.sendall(str(b_len).encode() + b' ' + b_text)
    print "in main process : send successful"

# if len(sys.argv) > 1:       
#     serverHost = sys.argv[1]                # server from cmd line arg 1
#     if len(sys.argv) > 2:                   # text from cmd line args 2..n
#         message = (x.encode() for x in sys.argv[2:])  


root = Tk()
root.wm_title("Simulation Control Panel")
root.minsize(width=666, height=666)
buttonRow = Frame(root)

button1 = Tkinter.Button(master=buttonRow, text='recent one week', command=None)
button1.pack(side=Tkinter.LEFT)

button2 = Tkinter.Button(master=buttonRow, text='last month', command=None)
button2.pack(side=Tkinter.LEFT)

button3 = Tkinter.Button(master=buttonRow, text='last six monthes', command=None)
button3.pack(side=Tkinter.LEFT)
buttonRow.pack(side=TOP, fill=X, padx=5, pady=5)

timeDurationRow = Frame(root)
Label(master=timeDurationRow, text="choose a time duration").pack(side=BOTTOM)
timeDurationRow.pack(side=TOP, fill=X, padx=5, pady=5)
# combox 

entryRow = Frame(root)

ent1 = Entry(entryRow)
ent1.insert(0, 'YYYY-mm-DD HH:MM') # set text
ent1.pack(side=BOTTOM)
Label(master=entryRow, text="  ~  ").pack(side=BOTTOM)
ent2 = Entry(entryRow)
ent2.insert(0, 'YYYY-mm-DD HH:MM') # set text
ent2.pack(side=BOTTOM)
entryRow.pack(side=TOP, fill=X, padx=5, pady=5)
root.mainloop()


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
