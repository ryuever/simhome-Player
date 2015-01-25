# fork_server.py
import os, time, sys, xml.etree.ElementTree as ET
from xml_operations import *
import json
from socket import *
import io
import socket

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
    print("received data's length : ", recv_len)
    amount_received = len(data)
    print('recv_len : ', recv_len)
    print('data: ', data)
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

def handleClient(connection):                    # child process: reply, exit
    b_data = recvall(connection)
    JSON_str = json.loads(b_data.decode())
    method = JSON_str['method']
    if method == 'get':
        print('invoke get_all')
        reply = get_all(root, JSON_str)
    elif method == 'remove':
        print("remove method")
        reply = remove(root, JSON_str)            
    elif method == 'insert':
        print("insert method")
        reply = insert(root, tree, JSON_str)
    else:
        print("error")
    b_reply = reply.encode()
    length = len(b_reply)
    connection.sendall(str(length).encode() + b' ' + b_reply)
    connection.close()
    print(connection, " is closed")
    os._exit(0)

def launchServer():                                # listen until process killed
    sockobj = socket.socket(AF_INET, SOCK_STREAM)           # make a TCP socket object
    sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockobj.bind((serverHost, eval(serverPort)))                   # bind it to server port number
    sockobj.listen(5)                                # allow 5 pending connects

    while True:                                  # wait for next connection,
        connection, address = sockobj.accept()   # pass to process for service
        print('Server connected by', address)
        print('at', now())
        reapChildren()                           # clean up exited children now
        childPid = os.fork()                     # copy this process
        if childPid == 0:                        # if in child process: handle
            handleClient(connection)
        else:                                    # else: go accept next connect
            activeChildren.append(childPid)      # add to active child pid list

if __name__=='__main__':
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = "localhost"
        serverPort = "50000"

    tree = ET.parse('../../SampleDATA/csvData/First.xml')
    root = tree.getroot()

    launchServer()
