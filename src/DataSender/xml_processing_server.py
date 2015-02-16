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
import dateutil.relativedelta
import numpy as np
from tk_calendar import *
from CalendarDialog import *

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

def db_inquery(start, end):
    print start, end
    conn, cursor = conn_DB("sim_player.db")
    res = duration_inquery(cursor, start, end)
    print "duration query result : ", res    
    datetime_list = []
    value_list = []
    for item in res:
        datetime_list.append(item[1])
        value_list.append(item[2].encode())
    print datetime_list, value_list
    
    sim_plotting(root, datetime_list, value_list)

def db_inquery2(start, end, connection):
    print start, end
    conn, cursor = conn_DB("sim_player.db")
    res = duration_inquery(cursor, start, end)
    print "duration query result : ", res    
    datetime_list = []
    value_list = []
    for item in res:
        datetime_list.append(item[1].strftime("%Y-%m-%d %H:%M"))
        value_list.append(item[2].encode())
    print datetime_list, value_list
    # response = "datetime_list=" + str(datetime_list) + ' ' + "value_list=" + str(value_list)
    response = str(datetime_list) + '=' +str(value_list)
    b_response = response.encode()
    b_response_len = len(b_response)
    connection.sendall(str(b_response_len).encode() + b' ' + b_response)    
    
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

def handleClient(connection):          # child process: reply, exit
    recv_buf = []
    global time_data, value, first_line
    while True:
        recv_b = recvall(connection)
        # print recv_b
        recv_str = recv_b.decode()
        if recv_str.startswith('control'):
            print 'one control record come'
            # parse_request(recv_str)
            regexpattern = '<|>| |"'
            splited_data = re.split(regexpattern, recv_str)
            request_method = splited_data[4]
            request_datetime_start_date = splited_data[12]
            request_datetime_start_time = splited_data[13]
            request_datetime_end_date = splited_data[16]
            request_datetime_end_time = splited_data[17]
            datetime_start = datetime.strptime(request_datetime_start_date + ' ' + request_datetime_start_time, "%Y-%m-%d %H:%M")
            datetime_end = datetime.strptime(request_datetime_end_date + ' ' + request_datetime_end_time, "%Y-%m-%d %H:%M")
            print datetime_start, datetime_end
            db_inquery2(datetime_start, datetime_end, connection)
            # db_query
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
                conn, cursor = conn_DB('sim_player.db')
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
    
    # 2 second for simulator initialization
    # time.sleep(2)
    sim_object.start(time_data, value)

def onclick(clicked_button, root, selected_date):
    cd = CalendarDialog(root)

    # cd is a datetime
    selected_date = cd.result.strftime("%Y-%m-%d")
    print "selected_date : ", selected_date
    clicked_button.config(text=selected_date)
    print cd.result

def sel(hr_select):
    selection = "Value = " + str(hr_select.get())
    print "selected date : ", selection

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
    
    db_inquery(datetime.strptime(datetime_start, "%Y-%m-%d %H:%M"), datetime.strptime(datetime_end, "%Y-%m-%d %H:%M"))
    
def cre_ctrl_panel(root):
    root.wm_title("Simulation Control Panel -- Server")
    root.minsize(width=666, height=666)
    buttonRow = Frame(root)

    cur = datetime.now()
    button1_timestamp = datetime.now() - timedelta(days=7)
    button2_timestamp = datetime.now() - dateutil.relativedelta.relativedelta(months=-1)
    button3_timestamp = datetime.now() - dateutil.relativedelta.relativedelta(months=-6)
    
    button1 = Tkinter.Button(master=buttonRow, text='recent one week',
                             command=lambda:db_inquery(button1_timestamp, cur))
    button1.grid(row=0, column=0)
    button2 = Tkinter.Button(master=buttonRow, text='last month',
                             command=lambda:db_inquery(button2_timestamp, cur))
    button2.grid(row=0, column=1)
    button3 = Tkinter.Button(master=buttonRow, text='last six monthes',
                             command=lambda:db_inquery(button3_timestamp, cur))
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

def fetch(ent1, ent2):
    start, end = ent1.get(), ent2.get()
    print start, end
    start_date = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(end, "%Y-%m-%d %H:%M")
    print start_date, end_date
    db_inquery(start_date, end_date)

if __name__=='__main__':
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = "localhost"
        serverPort = "50000"
    
    time_data = []
    value = []
    first_line = False
    sock_processing = threading.Thread(name='sock_processing', target=launchServer)
    sock_processing.start()

    root = Tk()
    cre_ctrl_panel(root)
