# -*- coding: utf-8 -*-
"""
#c ****************************************************************************************************************************
#c 
#c　シミュレーション実行時に複数のプログラム間で
#c 実行を同期させるためのオブジェクト
#c
#c ****************************************************************************************************************************
"""

#c プログラム名とバージョンの定義
__program__ = "syncObject"
__version__ = "0.0.1"


"""
#c ****************************************************************************************************************************
#c オブジェクトのインポート
#c ****************************************************************************************************************************
"""
from scipy.weave.accelerate_tools import Instance

import os
import threading
import socket
import SocketServer
import sys
import struct
import subprocess
from subprocess import check_call
"""
#c ****************************************************************************************************************************
#c
#c client program for synchronize
#c just send message
#c 
#c ****************************************************************************************************************************
"""
class SyncClient:
    def __init__(self, inProgramName, inMasterHostForSend, inMasterPortForSend, inMyPortForReceiveSync = -1):

        #c get hostname of myself and process id of myself
        self.pid = os.getpid()
        self.uname = os.uname()[1]
        
        #c set given programname 
        self.pgName = inProgramName
       
        #c set mutex
        self.mux = threading.RLock()
        
        #c set port for receive
        self.myPortForReceiveSync = inMyPortForReceiveSync
        self.myPortForReceiveCmd = -1
       
        #c set run mode
        self.slaveMode = False
        
        self.sendString = ""
        
        #c set send host and port
        self.masterHost = inMasterHostForSend
        self.doSend = False;
        self.masterPortForSend = 0;
        if(isinstance(inMasterPortForSend, int)):
            self.masterPortForSend = inMasterPortForSend
            self.doSend = True
        
        if(isinstance(inMasterPortForSend, str)):
            if(inMasterPortForSend.isdigit()):
                self.masterPortForSend = int(inMasterPortForSend)
                self.doSend = True
            else:
                self.doSend = False
        
        self.debug = True
        return
    
    #c **************************************************************
    #c set debug mode
    #c **************************************************************
    def setDebugMode(self, inDebug):
        self.debug = inDebug
        return
    
    #c **************************************************************
    #c set run mode and master port
    #c **************************************************************
    def setSlave(self, inMyPortForReceiveCmd):
        self.slaveMode = True
        self.myPortForReceiveCmd = inMyPortForReceiveCmd
    
    #c *************************************************************
    #c send regist message
    #c *************************************************************
    def regist(self,type=""):
        if(self.doSend == False):
            return
        try:
            sendString = ""
            sendString = "<command>"
            sendString = sendString + "<operation>register</operation>"
            sendString = sendString + "<programname>"+self.pgName+"</programname>"
            sendString = sendString + "<pid>" + str(self.pid) + "</pid>"
            sendString = sendString + "<port>" + str(self.myPortForReceiveSync) + "</port>"
            if(self.slaveMode):
                sendString = sendString + "<mode>slave</mode>"
                sendString = sendString + "<slavehost>" + str(self.uname) + "</slavehost>"
                sendString = sendString + "<cmdport>" + str(self.myPortForReceiveCmd) +"</cmdport>"
                if(len(type) > 0):
                    sendString = sendString + "<simtype>" + type + "</simtype>"
            sendString +="</command>"

            self.sendString = sendString
            
            with self.mux:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                l_onoff=1
                l_linger=0
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                            struct.pack('ii', l_onoff, l_linger))
                conn = sock.connect((self.masterHost, self.masterPortForSend))
                sock.send(sendString)
                sock.close()
            return 0
        except socket.error, e:
            print >>sys.stderr, "["+self.pgName+"] SyncClient.regist socket failed: %s" % (e)
            return -1
        return 0
    
    #c ******************************
    #c send synchronize message      
    #c ******************************
    def sendSyncMessage(self, inMessage, mode="client", time=""):
        if(self.doSend == False):
            return True
        try:
            sendString = "<command><operation>"+inMessage+"</operation><programname>"+self.pgName+"</programname>"
            if(mode == "slave"):
                sendString = sendString + "<runmode>slave</runmode>"
            if(inMessage == "next"):
                sendString = sendString + "<time>" + time + "</time>"
            sendString = sendString +"</command>"
            self.sendString = sendString
            with self.mux:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                conn = sock.connect((self.masterHost, self.masterPortForSend))
                sock.send(sendString)
                sock.close()  
            return True
        except socket.error, e:
            print >>sys.stderr, "["+self.pgName+"] SyncClient.sendsync socket failed: %s" % (e)
            return False
        return False 
"""
#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************
"""

"""     
#c ****************************************************************************************************************************
#c Receviver for synchronize
#c ****************************************************************************************************************************
"""
class SyncReceiver(object):
    def __init__(self):
        self.doExit = True
        return
    
    def startUp(self, inPgName, inMySelfListenPortForSync):
        self.doReveive = False
        self.debug = True
        self.mux = threading.RLock()
        
        if (inMySelfListenPortForSync == None):
            self.doReveive = False
            return

        self.myListenPortForSync = inMySelfListenPortForSync
        self.pgName = inPgName
        self.doExit = False

        self.serverSocketForReceiveCommand = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocketForReceiveCommand.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.serverSocketForReceiveCommand.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        try:
            self.serverSocketForReceiveCommand.bind(("0.0.0.0",self.myListenPortForSync))
        except:
            self.serverSocketForReceiveCommand.bind(("localhost",self.myListenPortForSync))

        self.doReveive = True
        return
    
    
    #c **************************************************************
    #c set debug mode
    #c **************************************************************
    def setDebugMode(self, inDebug):
        self.debug = inDebug
        return
        
    #c **************************************************************
    #c get Synchronize Message
    #c **************************************************************
    def listenForSync(self):
        if (self.doReveive == False):
            return
        while True:
            try:
                self.serverSocketForReceiveCommand.listen(100)
                #print  >>sys.stderr, "Wait for start"
                (clSock, clAddr) = self.serverSocketForReceiveCommand.accept()
                #print  >>sys.stderr,"["+ self.pgName +"] KickReceiver get message"
        
                msg = clSock.recv(1024).strip()
                clSock.close()
            except:
                break
            
            #print msg

            if (msg == "start"):
                if(self.debug):
                    print  >>sys.stderr, "["+ self.pgName +"] SyncReceiver get start message"
                break
            
            if (msg == "next"):
                if(self.debug):
                    print  >>sys.stderr, "["+ self.pgName +"] SyncReceiver get next message"
                break
            
            if (msg == "stop"):
                if(self.debug):
                    print  >>sys.stderr, "["+ self.pgName +"] SyncReceiver get stop message"
                self.doExit = True
                self.serverSocketForReceiveCommand.close()
                break
#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************


#c ****************************************************************************************************************************
#c Synchronizing Object including sender and receiver
#c ****************************************************************************************************************************
class SyncClientObject:
    def __init__(self, inProgramName, inMasterHost, inMasterPortForSendSync, inMySelfListenPortForSync, inMySelfListenPortForReceiveCmd = -1):
        
        self.syncClient = SyncClient(inProgramName, inMasterHost, str(inMasterPortForSendSync), inMySelfListenPortForSync)
        
        self.syncReceiver = SyncReceiver()
        self.syncReceiver.startUp(inProgramName, inMySelfListenPortForSync)        
        self.debug = True
        return
    
    #c *****************************
    #c
    #c *****************************
    def setDebugMode(self,inDebug):
        self.debug = inDebug
        self.syncClient.setDebugMode(inDebug)
        self.syncReceiver.setDebugMode(inDebug)
        return
    
    #c *****************************
    #c
    #c *****************************
    def regist(self, simType=""):
        self.syncClient.regist(simType)
        return
    
    #c *****************************
    #c
    #c *****************************
    def setSlave(self, inMyPortForReceiveCmd):
        self.syncClient.setSlave(inMyPortForReceiveCmd)
        return
    
    #c *****************************
    #c
    #c *****************************
    def listenForSync(self):
        if(self.debug):
            print >>sys.stderr, "[" + str(os.getpid()) +"] Listen for sync "
        self.syncReceiver.listenForSync()
        
    #c *****************************
    #c
    #c *****************************
    def sendSyncMessage(self, inMessage):
        return self.syncClient.sendSyncMessage(inMessage)

    #c *****************************
    #c
    #c *****************************
    def doExit(self):
        return self.syncReceiver.doExit
    
    #c *****************************
    #c
    #c *****************************
    def doNextStep(self, time):
        sendMsg = "next"
        ret = False
        while(ret == False):
            ret = self.syncClient.sendSyncMessage(sendMsg,"client", time)
        self.syncReceiver.listenForSync()
        return
    
    #c *****************************
    #c
    #c *****************************
    def doSendReady(self):
        self.syncClient.sendSyncMessage("ready")
        return
    
    #c *****************************
    #c
    #c *****************************
    def doSendEnd(self, mode="client"):
        self.syncClient.sendSyncMessage("end",mode)
        return
#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************

#c ****************************************************************************************************************************
#c
#c simulator management class
#c
#c ****************************************************************************************************************************

#c ****************************************************************************************************************************
#c port list manager
#c ****************************************************************************************************************************
class PortListmnager:
    def __init__(self):
        self.portList = {}
        self.hostPortList = {}
        #self.revInPortList = {}
        self.pgPidList = {}
        self.startport = 20001
        self.curPort = self.startport
        self.mux = threading.RLock()
        self.debug = True
        return
    
    #c **************************************************************
    #c set debug mode
    #c **************************************************************
    def setDebugMode(self, inDebug):
        self.debug = inDebug
        return
    
    #c **************************************************************
    #c set port
    #c **************************************************************
    def setPort(self, pgName, inSyncPort, inHost="localhost", inCmdListenPort=-1 ):
        if(isinstance(inSyncPort,int) == False):
            return
        if(isinstance(inCmdListenPort,int) == False):
            return
        with self.mux:
            #c if(self.portList.has_key(pgName)):

            
            self.portList[pgName] = inSyncPort
            self.hostPortList[pgName] = [inHost, inSyncPort, inCmdListenPort]
    
    #c **************************************************************
    #c
    #c **************************************************************
    def setCmdPort(self, pgName,  inCmdListenPort=-1 , syncPort = -1):
        if(isinstance(syncPort,int) == False):
            return
        if(isinstance(inCmdListenPort,int) == False):
            return
        with self.mux:
            if(inCmdListenPort < 0):
                return
            if(self.hostPortList.has_key(pgName)):
                wkHostPort = self.hostPortList[pgName]
                self.hostPortList[pgName] = [wkHostPort[0], wkHostPort[1], inCmdListenPort]
            else:
                self.hostPortList[pgName] = ["localhost", syncPort, inCmdListenPort]
                self.portList[pgName] = syncPort
            return

    #c **************************************************************
    #c
    #c **************************************************************
    def setHost(self, pgName, inHost = "localhost", cmdPort =-1, syncPort = -1):
        if(isinstance(cmdPort,int) == False):
            return
        if(isinstance(syncPort,int) == False):
            return
        with self.mux:
            if(self.hostPortList.has_key(pgName)):
                wkHostPort = self.hostPortList[pgName]
                self.hostPortList[pgName] = [inHost, wkHostPort[1], wkHostPort[2]]
            else:
                self.hostPortList[pgName] = [inHost, syncPort, cmdPort]
                self.portList[pgName] = syncPort
            return
        
    #c **************************************************************
    #c get port    
    #c **************************************************************
    def getPort(self, pgName, host = "localhost", mode="syncport", state="get"):
        with self.mux:
#             if(self.portList.has_key(pgName)):
                #retPort = self.portList[pgName]
            wkHostPortList = ["localhost", -1, -1]
            if((self.hostPortList.has_key(pgName) == False) or (state == "new")):
                # find yangest port
                wkPort = self.startport
                while 1:
                    if(self.revInPortList.has_key(wkPort)):
                        wkPort += 1
                        continue
                    else:
                        break              

                if(self.hostPortList.has_key(pgName)):
                    wk2HostPortList = self.hostPortList[pgName]
                else:
                    wk2HostPortList = [host,wkPort, -1]
                    
                wkHostPortList = [wk2HostPortList[0], wkPort, wk2HostPortList[2]]
                
                self.portList[pgName] = wkPort
                self.hostPortList[pgName] = wkHostPortList
                self.revInPortList[wkPort] = pgName

            wkHostPortList = self.hostPortList[pgName]
            
        retHostPort =  [wkHostPortList[0], wkHostPortList[1]]
        if(mode == "cmdport"):
            retHostPort =  [wkHostPortList[0], wkHostPortList[2]]
            
        return retHostPort
    
    #c **************************************************************
    #c release port
    #c **************************************************************
    def releasePort(self, pgName):
        with self.mux:
            if(self.portList.has_key(pgName)):
                removePort = self.portList[pgName]
                #self.revInPortList.pop(removePort)
                self.portList.pop(pgName)
                
            if(self.hostPortList.has_key(pgName)):
                self.hostPortList.pop(pgName)
        return
    
    #c **************************************************************
    #c get port list
    #c **************************************************************
    def getPortList(self):
        with self.mux:
#             return self.portList.values()
            return self.hostPortList.values()
        
    #c **************************************************************
    #c
    #c **************************************************************
    def getPortFromPgName(self, pgName):
        with self.mux:
            if(self.hostPortList.has_key(pgName)):
                return self.hostPortList[pgName]
            else:
                return ["unknown",-1,-1]
    #c **************************************************************
    #c
    #c **************************************************************     
    def getPgList(self):
        with self.mux:
            return self.hostPortList.keys()
        
#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************     
        
#c ****************************************************************************************************************************
#c program state manager
#c ****************************************************************************************************************************
class PgStateManager:
    def __init__(self):
        self.pgStateList = {}
        self.pgPidList = {}
        self.pidPgList = {}
        self.simTimeList = {}
        self.simTypeList = {}
        self.mux = threading.RLock()
        #self.pgNum = 0
        self.debug = True
        return
    
    #c **************************************************************
    #c set debug mode
    #c **************************************************************
    def setDebugMode(self, inDebug):
        with self.mux:
            self.debug = inDebug
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
#     def setRunPgNum(self, inPgNum):
#         with self.mux:
#             self.pgNum = inPgNum
#         return
    
    #c **************************************************************
    #c kill all programs registerd
    #c **************************************************************
    def killAll(self, test = False):
        with self.mux:
            pidList = self.pidPgList.keys()
            for pid in pidList:
                killString = "kill -9 " +str(pid) + " "
                if(test):
                    print killString
                else:
                    process = subprocess.Popen(killString, shell=True, cwd="/")
                
        return
    
    #c **************************************************************
    #c check if same program name exists
    #c **************************************************************
    def chkExists(self, pgName):
        with self.mux:
            if(self.pgStateList.has_key(pgName)):
                return True
            else:
                return False
            
    #c **************************************************************
    #c get program runnning state
    #c **************************************************************
    def getPgState(self, pgName):
        with self.mux:
            if(self.pgStateList.has_key(pgName) ==  False):
                return "unknown"
            else:
                return self.pgStateList[pgName]

    #c **************************************************************
    #c register / update  program state
    #c **************************************************************
    def register(self, pgName, state, pid=-1):
        with self.mux:
            upDate = False
            if(self.pgStateList.has_key(pgName) ==  False):
                upDate = True
            else:
                
                if(self.pgStateList[pgName] != "end"):
                    upDate = True
                    
            if(upDate):
                self.pgStateList[pgName] = state
                self.pgPidList[pgName] = pid
                if(pid > 0):
                    self.pidPgList[pid] = pgName
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
    def setState(self, pgName, state):
        with self.mux:
            if(self.pgStateList.has_key(pgName)):
                self.pgStateList[pgName] = state
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
    def getPGNameFromPid(self, pid):
        with self.mux:
            if(self.pidPgList.has_key(pid)):
                return self.pidPgList[pid]
            else:
                return None
            
    #c **************************************************************
    #c
    #c **************************************************************          
    def remove(self, pgName):
        with self.mux:
            if(self.pgStateList.has_key(pgName)):
                self.pgStateList.pop(pgName)
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
    def getPgNum(self):
        with self.mux:
            return len(self.pgStateList)
    
    #c **************************************************************
    #c
    #c **************************************************************
    def chkAllpgStateisSame(self,state):
        with self.mux:
            pgList = self.pgStateList.keys()
            #stateList = self.pgStateList.values()
            beforeState = None
            allSameState = True
            #for eachState in stateList:
#             pgCount = len(pgList)
#             if(pgCount < self.pgNum):
#                 allSameState = False
#             else:
            pgCount = 0
            for pgName in pgList:
                pgCount += 1
                eachState = self.pgStateList[pgName]
                    
                if(beforeState == None):
                    beforeState = eachState
                    continue
                    
                if(eachState == "none"):
                    continue
                
                if(beforeState != eachState):
                    allSameState = False
                    continue

                
        return allSameState

    #c **************************************************************
    #c
    #c **************************************************************
    def resetState(self):
        with self.mux:
            pgList = self.pgStateList.keys()
            i=0
            for key in pgList:
                self.pgStateList[key] = str(i)
                i += 1
        return
    
    #c **************************************************************          
    #c set time information         
    #c **************************************************************       
    def setTime(self,pgName, time):
        with self.mux:
            if(self.pgStateList.has_key(pgName)):
                self.simTimeList[pgName] = time
        return
    
    #c **************************************************************
    #c reset time information
    #c **************************************************************
    def resetTime(self):
        with self.mux:
            pgList = self.pgStateList.keys()
            for key in pgList:
                self.simTimeList[key] = "-1:-1:-1"
        return

    #c **************************************************************
    #c
    #c **************************************************************
    def setSimType(self,pgName, type="default"):
        with self.mux:
            if(self.pgStateList.has_key(pgName)):
                self.simTypeList[pgName]=type
        return

#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************

#c ****************************************************************************************************************************
#c Synchronize manager
#c ****************************************************************************************************************************
class SyncManager:
    #c ***************************************** 
    #c initalize. set portlistmanager
    #c ****************************************
#     def __init__(self, inPortListManager):
#         self.portListManager = inPortListManager
#         return
    def __init__(self):
        self.portListManager = PortListmnager()
        self.pgStateManager = PgStateManager()
        self.mux = threading.RLock()
        self.debug = True
    
    
    #c **************************************************************
    #c set debug mode
    #c **************************************************************
    def setDebugMode(self, inDebug):
        self.debug = inDebug
        self.portListManager.setDebugMode(inDebug)
        self.pgStateManager.setDebugMode(inDebug)
        return
    
    #c **************************************************************
    #c send message to all managed cprogram
    #c senf same message
    #c **************************************************************
    def sendMsg(self,msg,mode="toclient"):
        ret = 0
        with self.mux:            
            pgList = self.portListManager.getPgList()
            #portlist = self.portListManager.getPortList()
            pgNum = 0
            for pgName in pgList:
                pgNum = pgNum + 1
                #c ***************************
                #c send message
                #c ***************************
                
                pgState = self.pgStateManager.getPgState(pgName)
                if((pgState == "end") or (pgState == "unknown")):
                    continue
                    
                port = self.portListManager.getPortFromPgName(pgName)
                success = False
                
                #tmpDbg = self.debug
                
                while(success == False):
                    try:
                        #if(self.debug):
                        #    print "pgnum["+str(pgNum)+"] send message  to [" + pgName +"]"
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.2)
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                     l_onoff=1
#                     l_linger=0
#                     sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
#                             struct.pack('ii', l_onoff, l_linger))
                        hostPort=(port[0],port[1])
                        if(mode == "toslave"):
                            hostPort = (port[0], port[2])
                        conn = sock.connect(hostPort)
                        sock.send(msg)
                        sock.close()
                        success = True
                    except socket.error, e:
                        print >>sys.stderr, "socket failed: %s" % (e)
                        if(e.errno == 111):
                            #c can not connect
                            success = True
                                
                    #c ***************************
                    #c reset time
                    #c ***************************
                    self.pgStateManager.setTime(pgName, "-1:-1:-1")
                ret = 0
        return ret
    
    #c **************************************************************
    #c reset time
    #c **************************************************************
    def resetTime(self):
        with self.mux:
            self.pgStateManager.resetTime()
        return
    
    #c **************************************************************
    #c set time
    #c **************************************************************
    def setTime(self, pgName, time):
        with self.mux:
            self.pgStateManager.setTime(pgName, time)
        return
    
    #c **************************************************************
    #c reset state
    #c **************************************************************
    def resetState(self):
        with self.mux:
            self.pgStateManager.resetState()
        return       

    #c **************************************************************
    #c
    #c **************************************************************
    def getPort(self, pgName, host, mode , state):
        return self.portListManager.getPort(pgName, host, mode, state)

    #c **************************************************************
    #c register client program
    #c **************************************************************
    def chkExists(self, pgName):
        with self.mux:
            return self.pgStateManager.chkExists(pgName)
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
    def register(self, pgName, state, pid=-1, clAddr = "localhost", cmdPort = -1, syncPort = -1):
        with self.mux:
            self.pgStateManager.register(pgName, state, pid)
            self.portListManager.setHost(pgName, clAddr, cmdPort, syncPort)
            #self.portListManager.setCmdPort(pgName, cmdPort)
        return
    #c **************************************************************
    #c
    #c **************************************************************
    def setState(self, pgName, state):
        with self.mux:
            self.pgStateManager.setState(pgName, state)
            
    #c **************************************************************
    #c
    #c **************************************************************
    def chkDoReady(self, pgName):
        return self.chkDoSameState(pgName, "ready")
    
    #c **************************************************************
    #c
    #c **************************************************************   
    def chkDoNext(self, pgName, time):
        stateName = "next|" + time
        return self.chkDoSameState(pgName, stateName)
    
    #c **************************************************************
    #c
    #c **************************************************************
    def chkReady(self):
        with self.mux:
            return self.pgStateManager.chkAllpgStateisSame("ready")
    
    #c **************************************************************
    #c
    #c **************************************************************
#     def setRunPgNum(self, pgNum):
#         with self.mux:
#             self.pgStateManager.setRunPgNum(pgNum)
#             return
        
    #c **************************************************************
    #c
    #c **************************************************************        
    def chkDoSameState(self,pgName,state): 
        ret = False
        with self.mux:
            self.pgStateManager.register(pgName, state)
            ret = self.pgStateManager.chkAllpgStateisSame(state)
#             if(self.pgStateManager.chkAllpgStateisSame(state)):
#                 ret = True
#             else:
#                 ret = False
            
        return ret
    
    #c **************************************************************
    #c
    #c **************************************************************
    def release(self, pgName):
        with self.mux:
            self.pgStateManager.remove(pgName)
            self.portListManager.releasePort(pgName)
            
        return self.pgStateManager.getPgNum()
    
    #c **************************************************************
    #c
    #c **************************************************************
    def setSimType(self,pgName,type="default"):
        with self.mux:
            self.pgStateManager.setSimType(pgName, type)
        return
    
    #c **************************************************************
    #c
    #c **************************************************************
    def killAll(self):
        with self.mux:
            self.pgStateManager.killAll()
        return

#c ****************************************************************************************************************************
#c end of class
#c ****************************************************************************************************************************
        
