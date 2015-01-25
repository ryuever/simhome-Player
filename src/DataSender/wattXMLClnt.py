#!/usr/bin/env python
#
# Copyright (c) 2011 Takashi OKADA (tk.okada55@gmail.com)
# All rights reserved.
# modified by h-fujita at 2014 for send xml format data
#
#
#from tarfile import TUREAD


__program__ = "wattXMLClnt"
__version__ = "0.0.1"

#from optparse import OptionParser
import datetime
import socket
#import struct
import sys
import time
import threading
#import Queue
import os
from lxml import etree
import random

def tcpSend(host, port, timeout, data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        #sock.bind(('localhost', 1034))
        #conn = sock.connect((host, port))
        sock.connect((host, port))
        sock.send(data)
        sock.close()
        return 0
    except socket.error, e:
        print >>sys.stderr, "%s: socket failed: %s" % \
            (__program__, e)
        return -1

# ***************************************************************************
# clnt of watt information send
# ***************************************************************************
class wattXMLClient():
    def __init__(self, hgwId, host, myListenPort, timeout, sleep_time = 10, inMuxSocket = None, inMaster = None):
        # home gateway ID (0xe000 - 0xffff)
        if hgwId > (int(0xffff) - int(0xe000)) or hgwId < 0:
            print >>sys.stderr, "%s %s : __init__ : invalid home gateway ID" \
                ": %d" % (__program__, self.__class__.__name__, hgwId)
            return None
        self.hgwId = int(0xe000) + int(hgwId)

        self.sq = 0

        self.host = host
        self.port = int(myListenPort)
        if timeout != None:
            self.timeout = int(timeout)
        else:
            self.timeout = -1

        self.muxSocket = inMuxSocket;
        self.wk_Queue = []
        self.sleep_time = sleep_time
        self.sqNum = 0
        self.master = inMaster
        self.retryCounter = 0
        self.terminate = False
        self.debug = True

    def packedWattXMLMultiSend(self, wk_Queue):
        if(self.muxSocket == None):
            return
        
        #sendQueNum =0
        i = 0
        if(self.terminate):
            #doFinal = True
            self.master.alive = False

            print >>sys.stderr," do terminate"
            return
            
        with self.muxSocket:
            sendQueNum = len(wk_Queue)
            if (sendQueNum < 1):
                return
        
        wkQList = []
       
        #doFinal = False
        #finalWattData = []
        with self.muxSocket:
            while (i < sendQueNum):
                i += 1
                try:
                    wattsData = wk_Queue.pop(0)
                    if wattsData[0] == "-1":
                        #doFinal = True
                        self.master.alive = False
                        #finalWattData = wattsData
                        
                    
                    wkQList.append(wattsData)
                    continue
                    
                except:
                    continue

        # get watt data
        # data contains
        # [0]: epmID (sequence nuber, cyclic, max value is 255)
        # [1]: wattage (consume/generate watt at time)
        # [2]: record time (current time at queuing)
        # [3]: house name (name inside of simulator program)
        # [4]: process id (id of simulator program
        # [5]: sequence number of client
        # [6]: hgwID
        # [7]: retry count(not used)

        time.sleep(self.sleep_time)

        xmlRootData = self.generateXMLDataRoot()
        xmlDataData = self.generateXMLDataDataVoid()
        i = 0
        while (i < sendQueNum):  
            eachWattData = wkQList[i]
            if (eachWattData[0] == "-1"):
                i += 1
                continue
            
            senderString = self.getSenderString(eachWattData[3], eachWattData[0], str(eachWattData[6]),str(eachWattData[4]))
            xmlWattData = self.generateXMLRawDataWithSender(senderString, eachWattData[0], eachWattData[1], eachWattData[5], eachWattData[2])
            self.sqNum += 1
            if(self.sqNum > 65535):
                self.sqNum = 0  
            xmlDataData.append(xmlWattData)
            i += 1
                
        xmlRootData.append(xmlDataData)
        
        xmlOutdata = etree.tostring(xmlRootData,pretty_print=True)
        #sys.stderr.write("["+str(self.sqNum )+"]")
        #print " send[%s]" % (xmlOutdata)
        dataSending = True
        while dataSending:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                if self.timeout >= 0:
                    sock.settimeout(self.timeout)
                else:
                    print "timeout:", socket.getdefaulttimeout()

                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((self.host, self.port))
                sock.sendall(xmlOutdata)
                sock.close()
                dataSending = False
                continue
#         except Exception as e:
#             print str(type(e))
#             
#         except Exception as e:
#             print 'type:' +str(type(e))
#             print 'args:' + str(e.args)
#             print 'message:' + e.message
#             print 'e itself' + str(e)
#             return
        
        
            except socket.timeout, e:
                sock.close()
                if(self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print "%s %s (%s) : wattXMLMultiSend : socket.timeout!: [%s] house [%s] time[%s]" % (__program__, self.__class__.__name__,str(os.getpid()), e, wattsData[3], wkTmStr)
            
                #time.sleep(self.sleep_time)
                time.sleep(random.random()/10)
#                 wattsData[len(wattsData)-1] +=1
#                 with self.muxSocket:
#                     i = 0
#                     while (i < sendQueNum):        
#                         wk_Queue.insert(wk_Queue.__len__()-1,wkQList[i])
#                         i += 1
#                     if(doFinal == True):
#                         wk_Queue.append(finalWattData)
# 
#                 for i in range(0,10):
#                     time.sleep(self.sleep_time)
#                 if(self.master != None):
#                     self.master.alive = True
#                 return
                continue
            
            except socket.error, e:
            
                sock.close()
                if(e.errno == 111):
                    #c connection refuse
                    #c not send data
                    dataSending = False
                    continue
                if(self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print >>sys.stderr, "%s : wattXMLMultiSend(%s:%d): socket failed:%s Time[%s]" % (__program__, self.host, self.port, e, wkTmStr)
                    #time.sleep(self.sleep_time)
                    time.sleep(random.random()/10)
#             with self.muxSocket:
#                 if(e.errno == 111):
#                     self.retryCounter +=1
#                 if(self.retryCounter < 3):
#                     i = 0
#                     while (i < sendQueNum):        
#                         wk_Queue.insert(wk_Queue.__len__()-1,wkQList[i])
#                         i += 1
#                 else:
#                     self.retryCounter= 0
#                 if(doFinal == True):
#                     wk_Queue.append(finalWattData)
#                                         
#             for i in range(0,10):
#                 time.sleep(self.sleep_time)
#             if(self.master != None):
#                 self.master.alive = True
#             return
            
            except Exception as e: 
                sock.close()
                time.sleep(self.sleep_time)
                if(self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print 'wattXMLMultiSend error [Time:' + wkTmStr + '][type:' +str(type(e)) + '] [args:' + str(e.args) + '] [message:' + e.message + '] [e itself' + str(e) + ']'
                    print >>sys.stderr, "%s : wattXMLMultiSend(%s:%d): socket failed time[%s]" % (__program__, self.host, self.port, wkTmStr)
                

#             with self.muxSocket:
#                 i = 0
#                 while (i < sendQueNum):        
#                     wk_Queue.insert(wk_Queue.__len__()-1,wkQList[i])
#                     i += 1
#                 if(doFinal == True):
#                     wk_Queue.append(finalWattData)  
#             for i in range(0,10):
#                 time.sleep(self.sleep_time)
#             if(self.master != None):
#                 self.master.alive = True
#             return
        
        
        return
# send each data type

    def wattXMLSingleSend(self, wattsData):
    # get watt data
    # data contains
    # [0]: epmID (sequence nuber, cyclic, max value is 255)
    # [1]: wattage (consume/generate watt at time)
    # [2]: record time (current time at queuing)
    # [3]: house name (name inside of simulator program)
    # [4]: process id (id of simulator program)
    # [5]: sequence number of client
    # [6]: hgwID
    # [7]: retry count(not used)
        dataSending = True
        while dataSending:
            try:
                #time.sleep(self.sleep_time)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.timeout >= 0:
                    sock.settimeout(self.timeout)
                else:
                    print "timeout:", socket.getdefaulttimeout()
                
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((self.host, self.port))
                xmlRootData = self.generateXMLDataRoot()
                xmlDataData = self.generateXMLDataDataVoid()
                senderString = self.getSenderString(wattsData[3], wattsData[0], str(wattsData[6]),str(wattsData[4]))
                xmlWattData = self.generateXMLRawDataWithSender(senderString, wattsData[0], wattsData[1], wattsData[5], wattsData[2])
                self.sqNum += 1
                if (self.sqNum > 65535):
                    self.sqNum = 0
                xmlDataData.append(xmlWattData)
                xmlRootData.append(xmlDataData)
                #print  >>sys.stderr," send[%s]" % (wattsData[0])
                xmlOutdata = etree.tostring(xmlRootData, pretty_print=True)
                #sys.stderr.write("[" + str(self.sqNum) + "]")
                sock.sendall(xmlOutdata) #time.sleep(self.sleep_time)
                sock.close()
                dataSending = False
                #return True

            except socket.timeout as e:
                sock.close()
                if (self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print >> sys.stderr, "%s %s : wattXMLSingleSend : socket.timeout!: [%s] house [%s] time[%s]" % (__program__, self.__class__.__name__, e, wattsData[3], wkTmStr)
                time.sleep(random.random()/10)
                #return False
            
            except socket.error as e:
                sock.close()
                if(e.errno == 111):
                    #c connection refuse
                    #c not send data
                    dataSending = False
                    return False

                if (self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print >> sys.stderr, "%s : wattXMLSingleSend(%s:%d): socket failed:%s rime[%s]" % (__program__, self.host, self.port, e, wkTmStr)
                time.sleep(random.random()/10)
                continue
                #return False
        
            except Exception as e:
                sock.close()
                if (self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print 'wattXMLSingleSend error [Time:' + wkTmStr + '][type:' + type(e) + '] [args:' + str(e.args) + '] [message:' + e.message + '] [e itself' + str(e) + ']'
                    print >> sys.stderr, "%s : wattXMLSingleSend(%s:%d): socket failed" % (__program__, self.host, self.port)
                    continue
                time.sleep(random.random()/10)
        return True

    def wattXMLMultiSend(self, wk_Queue):
        if(self.muxSocket == None):
            return
        
        #wkSendQueNum =0
        if(self.alive == False):
            return
        
        with self.muxSocket:
            wkSendQueNum = len(wk_Queue)
            if (wkSendQueNum < 1):
#             self.muxSocket.release()
                return
        
        
        while len(wk_Queue) >0:
        
        
            with self.muxSocket:
                try:
                    wattsData = wk_Queue.pop(0)
                except:
#                     for i in range(0,100):
#                         time.sleep(self.sleep_time)
                    return
            if wattsData[0] == "-1":
                time.sleep(self.sleep_time * 10)
                self.master.alive = False
                return
            
            sendResult = self.wattXMLSingleSend(wattsData)
              
            if(sendResult == False):
                time.sleep(self.sleep_time)
                wattsData[len(wattsData) - 1] += 1
                if (wattsData[len(wattsData) - 1] < 10):
                    with self.muxSocket:
                        wk_Queue.insert(wk_Queue.__len__() - 1, wattsData)
                #for i in range(0, 10):
                time.sleep(self.sleep_time*10)
            

        return

    def generateXMLDataRoot(self):
        xmlOutdata = etree.Element("root")
        return xmlOutdata
    
    def getSenderString(self, houseName, epmID, hgwID, pid):
        setString = socket.gethostname()
        setString += "_"
        setString += pid
        setString += "_"
        setString += hex(int(hgwID))
        setString += "_"
        setString += houseName
#         setString += "_"
#         setString += str(int(epmID))
        return setString

    def generateXMLDataData(self, houseName, epmID):
        xmlOutdata = etree.Element("data")
        
        setString = self.getSenderString(houseName, epmID)
        
        xmlOutdata.set("sender",setString)
        return xmlOutdata
    
    def generateXMLDataDataVoid(self):
        xmlOutdata = etree.Element("data")
        return xmlOutdata

    def generateXMLRawData(self, epmId, wattage, seqNo, tm):   
        # wattage (0 - 65535)
        if wattage < 0:
            watt = 0
        elif wattage > 65535:
            watt = wattage
            while (watt > 65535):
                watt -= 65535
        else:
            watt = wattage

        # MF: missing flag 0:mesured other:missed
#         if missedFlag == 0:
#             mf = missedFlag
#         else:
#             mf = 1
         
        data = etree.Element("value")
        data.set("date",str(tm))
        data.set("time",str(seqNo))
        data.set("type", " ")
        data.set("info","["+str(int(epmId)) +"]")
        data.text= str(watt)
        
#         self.sq +=1
#         if(self.sq >65535):
#             self.sq = 0
        
        return data


# ***************************************************************************
# clnt oc sml send thread
# ***************************************************************************

    def generateXMLRawDataWithSender(self, sender, epmId, wattage, seqNo, tm):   
        # wattage (0 - 65535)
        if wattage < 0:
            watt = 0
        elif wattage > 65535:
            watt = wattage
            while (watt > 65535):
                watt -= 65535
        else:
            watt = wattage
       
        # modify time
        
        wkDate = tm.strftime("%Y-%m-%dT%H:%M:%SZ")
        sectime = tm.strftime("%H:%M:%S")
        
        data = etree.Element("value")
        data.set("sender",str(sender))
        data.set("date",wkDate)
        data.set("time",sectime)
        data.set("msec",str(tm.microsecond))
        data.set("seqno",str(seqNo))
        data.set("type", " ")
        data.set("info","["+str(int(epmId)) +"]")
        data.text= str(watt)
        
#         self.sq +=1
#         if(self.sq >65535):
#             self.sq = 0
        
        return data


# ***************************************************************************
# clnt oc sml send thread
# ***************************************************************************

class xmlSendThread(threading.Thread):

    def __init__(self, xc, queue, inMux, sleep_time):
        #threading.Thread.__init__(self)
        threading.Thread.__init__(self)
        self.xc = xc
        self.queue = queue
        self.mux = inMux
        self.sleep_time = sleep_time
        self.alive = True
        
    def run(self):
        while self.alive:
            if(self.queue.empty()):
                time.sleep(self.sleep_time)


"""
#c **********************************************
#c Thread Object initializer
#c when initalize object, use specifies these infomations
#c parameters
#c  index        :
#c  uSrvHost     : hostname that I send wattXML messages to.
#c  uSrvPort     : port no that I send wattXML messages to.
#c  uSrvTimeout
#c
#c
"""
class wattXMLClientThread(threading.Thread):
    def __init__(self, 
                 index, 
                 uSrvHost, 
                 uSrvPort, 
                 uSrvTimeout,  
                 inMuxSocket, 
                 queue, 
                 sleep_time):
        self.stop = threading.Event()
        threading.Thread.__init__(self)
        #self.master = master
        self.sleep_time = sleep_time
        self.uc = wattXMLClient(index, uSrvHost, uSrvPort, uSrvTimeout,  self.sleep_time, inMuxSocket, self)
        self.alive = True
#         self.queue = queue
        self.mux_Socket_H = inMuxSocket
        self.wk_Queue = queue
        self.threaded = False
        return
    
    def send(self,wattsData):
        if(self.threaded):
            return
        rval = False
        while(rval == False):
            rval = self.uc.wattXMLSingleSend(wattsData)
            if(rval == False):
                #for i in range(0, 10):
                time.sleep(self.sleep_time*10)
        
        return

    def run(self):
        self.threaded = True
        while self.alive:
            #send = 0
            time.sleep(self.sleep_time)
            # rval = self.uc.wattXMLMultiSend(self.wk_Queue) 
            #rval = self.uc.packedWattXMLMultiSend(self.wk_Queue)
            self.uc.packedWattXMLMultiSend(self.wk_Queue)
        endstr =  "terminate wattXMLClnt Thread [" + str(os.getpid()) + "]"
        print >>sys.stderr,endstr
        return

    def terminate(self):
        self.alive = False
        self.uc.terminate = True
#         if self.process is not None:
#             self.process.terminate()
#         self.uc.terminate = True
#         self.stop.set()
""" just send & receive the messages """



