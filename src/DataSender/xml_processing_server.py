# fork_server.py
import os, time, sys, xml.etree.ElementTree as ET
from xml_operations import *
from db_operations import *
import json
from socket import *
import io
import socket
from SimProcessing import *
import threading
import time 
from datetime import date, datetime, timedelta
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def now():                                       # current time on server
    return time.ctime(time.time())

def recvall(connection):
    recv_data = connection.recv(1024)             # till eof when socket closed

    for i in range(len(recv_data)):
        if recv_data[i] == ' ':
            break
    
    recv_len = recv_data[:i]
    data = b'' + recv_data[i+1:]
    # print("received data's length : ", recv_len)
    amount_received = len(data)
    # print('recv_len : ', recv_len)
    # print('data: ', data)
    amount_expected = eval(recv_len)
    
    while amount_received < amount_expected:
        more = connection.recv(1024)
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (amount_expected, amount_received))
        data += more
        amount_received += len(more)
    return data

# for zombie process
activeChildren = []
def reapChildren():                              # reap any dead child processes
    while activeChildren:                        # else may fill up system table
        pid, stat = os.waitpid(0, os.WNOHANG)    # don't hang if no child exited
        if not pid: break
        activeChildren.remove(pid)

def parse_request(request_xml_data):
    request_root = ET.fromstring(request_xml_data)
    print request_root
    request_method = request_root.attrib['method']
    request_list = []
    for item in request_root:
        request_list.append(item.attrib)
    sorted_request_list = sorted(request_list, key=lambda k: k['flag'])

    print "sorted_request_list", sorted_request_list

    print(request_method)
    if request_method == 'inquery':
        print('go to inquery')
        request_result = inquery(root, sorted_request_list)
    elif request_method == 'remove':
        print("remove method")
        request_result = remove(root, sorted_request_list)            
    elif request_method == 'insert':
        print("insert method")
        request_result = insert(root, tree, sorted_request_list)
    else:
        print("error")
    return request_result

def handleClient(connection):                    # child process: reply, exit
    recv_buf = []
    global time_data, value, first_line
    while True:
        recv_b = recvall(connection)
        # print recv_b
        recv_str = recv_b.decode()
        if recv_str.startswith('control'):
            print 'one control record come'
            # parse_request(recv_str)
            pass
        else:
            recv_buf.append(recv_str)
            xml_sender, xml_date, xml_time, xml_value = single_xml2lst(recv_str)
            py_date = datetime.strptime(xml_date.encode() + ' ' + xml_time.encode(),  '%Y%m%d %H:%M')
            # print 'py_date : ', py_date
            if first_line == False:
                for i in reversed(range(100)):
                    pre_py_date = py_date - timedelta(minutes=i)
                    time_data.append(pre_py_date)
                    value.append(np.nan)
                    first_line = True
            time_data.append(py_date)
            value.append(xml_value.encode())

            if len(recv_buf) > 30:
                conn, cursor = conn_DB()
                lt2str = ''.join(recv_buf)
                # print lt2str
                xml_tuple_list = multi_xml2lst(lt2str)
                # print xml_tuple_list
                ins_DB(conn, cursor,xml_tuple_list)
                recv_buf = []
                print 'cycle finish'
                print "close database"
                conn.close()
    print 'cleaning'
    print 'finally close database'
    conn.close()
    # reply = parse_request(b_data.decode())
    # b_reply = reply.encode()
    # length = len(b_reply)
    # connection.sendall(str(length).encode() + b' ' + b_reply)
    # connection.close()
    # print(connection, " is closed")
    os._exit(0)

def launchServer():                                # listen until process killed
    sockobj = socket.socket(AF_INET, SOCK_STREAM)           # make a TCP socket object
    sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print "run launchserver"
    sockobj.bind((serverHost, eval(serverPort)))                   # bind it to server port number
    sockobj.listen(5)                                # allow 5 pending connects

    while True:                                  # wait for next connection,
        connection, address = sockobj.accept()   # pass to process for service
        print('Server connected by', address)
        print('at', now())
        # reapChildren()                           # clean up exited children now
        # childPid = os.fork()                     # copy this process

        # args must be a tuple...........
        
        handleclient = threading.Thread(name='handleclient', target=handleClient,args=(connection,))
        handleclient.start()
        # if childPid == 0:                        # if in child process: handle
        #     handleClient(connection)
        # else:                                    # else: go accept next connect
        #     activeChildren.append(childPid)      # add to active child pid list

def start_real_time_sim(root, time_data, value):
    print 'come to sim'
    sim_object = SimProcessing("Realtime Simulation on Server", root)
    time.sleep(2)
    sim_object.start(time_data, value)
        
def cre_ctrl_panel(root):
    print 'create table'
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

    button4 = Tkinter.Button(master=buttonRow, text='realtime simulation',
                             command=lambda : start_real_time_sim(root, time_data, value) )
    button4.pack(side=Tkinter.LEFT)
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

if __name__=='__main__':
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = "localhost"
        serverPort = "50000"
    
    # tree = ET.parse('../../SampleDATA/csvData/First.xml')
    # root = tree.getroot()
    
    time_data = []
    value = []
    first_line = False
    sock_processing = threading.Thread(name='sock_processing', target=launchServer)
    sock_processing.start()

    root = Tk()
    cre_ctrl_panel(root)

    # while True:
    #     time.sleep(1)
    #     print 'sim loop'
    #     print "used for simulation : ",time_data, value        
    #     sim_object.realtimePloter(time_data, value)

    # childPid = os.fork()
    # if childPid == 0:
    #     print 'socket processing'
    #     launchServer()
    # else:        
    #     print 'come to sim'
    #     while True:


        # 
        # while True:
        #     print 'in sim loop'
        #     time.sleep(1)
        #     print time_data, value
        #     sim_object.realtimePloter(time_data, value)
