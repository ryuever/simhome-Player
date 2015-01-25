import sys,io, os
from socket import *                # portable socket interface plus constants

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
    data = b'' + recv_data[i + 1:]

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

# if len(sys.argv) > 1:       
#     serverHost = sys.argv[1]                # server from cmd line arg 1
#     if len(sys.argv) > 2:                   # text from cmd line args 2..n
#         message = (x.encode() for x in sys.argv[2:])  

sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
print("serverHost : ",serverHost)
print("port : ", serverPort)
sockobj.connect((serverHost, eval(serverPort)))   # connect to server machine + port
# text = input()
text = '{"method":"get", "sender":"", "date":"", "time":"", "type":""}'
# text = '{"method":"insert", "sender":"First", "date":"20140701", "time":"00:01:00", "type":"int", "text":"200"}'
btext = text.encode()
length = len(btext)

# insert a b' ' as a indicator to split length and data
sockobj.sendall(str(length).encode() + b' ' + btext)


# for single clients
recv_data = recvall(sockobj)
print('Client received:\n')
print(recv_data.decode())
sockobj.close()                             # close socket to send eof to server        

# # for multi-clients
# recv_data = recvall(sockobj)
# export_file = "process{}.txt".format(eval(indicator))
# fp = open(export_file, "w")
# print('Client received:\n')
# print(recv_data.decode())
# fp.write(recv_data.decode())
# sockobj.close()                             # close socket to send eof to server        
