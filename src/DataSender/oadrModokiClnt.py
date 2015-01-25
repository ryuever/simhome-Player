#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
from datetime import datetime

__program__ = "oadrModokiClnt"
__version__ = "0.0.1"

from optparse import OptionParser
import datetime
import socket
import struct
import sys
import time
import threading
import Queue
from lxml import etree
from multiprocessing import *
import os
import requests

OADR_UPD_REPORT = 'oadr:oadrUpdateReport'

# define of name space
OADR_ei_schemaVersion='2.0b'
OADR_xsi_schemaLocation='http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd'
OADR_xmlns_emix='http://docs.oasis-open.org/ns/emix/2011/06'
OADR_xmlns_power='http://docs.oasis-open.org/ns/emix/2011/06/power'
OADR_xmlns_scale='http://docs.oasis-open.org/ns/emix/2011/06/siscale'
OADR_xmlns_ei='http://docs.oasis-open.org/ns/energyinterop/201110'
OADR_xmlns_pyld='http://docs.oasis-open.org/ns/energyinterop/201110/payloads'
OADR_xmlns_oadr='http://openadr.org/oadr-2.0b/2012/07'
OADR_xmlns_gml='http://www.opengis.net/gml/3.2'
OADR_xmlns_xsi='http://www.w3.org/2001/XMLSchema-instance'
OADR_xmlns_atom='http://www.w3.org/2005/Atom'
OADR_xmlns_xcal='urn:ietf:params:xml:ns:icalendar-2.0'
OADR_xmlns_strm='urn:ietf:params:xml:ns:icalendar-2.0:stream'

nameSpace_20B_nsMap = { # If you see an 2.0a variable used here, that means that the namespace is the same
    'ver'     : OADR_ei_schemaVersion,
    'xsiloc' : OADR_xsi_schemaLocation,
    'oadr'   : OADR_xmlns_oadr,
    'pyld'   : OADR_xmlns_pyld,
    'ei'     : OADR_xmlns_ei,
    'emix'   : OADR_xmlns_emix,
    'xcal'   : OADR_xmlns_xcal,
    'strm'   : OADR_xmlns_strm,
    'scale'  : OADR_xmlns_scale,
    'power'  : OADR_xmlns_power,
    'atom'   : OADR_xmlns_atom,
    'gml'    : OADR_xmlns_gml,
    'xsi'    : OADR_xmlns_xsi
}

nameSpace_20B_elmMap = {
    'ver'     : 'ei:schemaVersion',
    'xsiloc' : 'xsi:schemaLocation',
    'oadr'   : 'xmlns:oadr',
    'pyld'   : 'xmlns:pyld',
    'ei'     : 'xmlns:ei',
    'emix'   : 'xmlns:emix',
    'xcal'   : 'xmlns:xcal',
    'strm'   : 'xmlns:strm',
    'scale'  : 'xmlns:scale',
    'power'  : 'xmlns:power',
    'atom'   : 'xmlns:atom',
    'gml'    : 'xmlns:gml',
    'xsi'    : 'xmlns:xsi'                     
}

nameSpace_20B_elmMap_XML = {
    'oadr'   : 'xmlns:oadr'
}

nsOADRMap  = {
    'oadr'   : 'xmlns:oadr'
}

# def tcpSend(host, port, timeout, data):
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.settimeout(timeout)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind(('localhost', 1034))
#         conn = sock.connect((host, port))
#         sock.send(data)
#         sock.close()
#         return 0
#     except socket.error, e:
#         print >>sys.stderr, "%s: socket failed: %s" % \
#             (__program__, e)
#         return -1

"""
#c **********************************************
#c client of oadr sender
#c this object sends messages that is OADR formatted.
#c
#c **********************************************
"""
"""
#c **********************************************
#c Object initializer
#c when initalize object, yuse specifies these infomations
#c parameters
#c  host         : hostname that I send OADR messages to.
#c  myListenPort : port no that I send OADR messages to.
#c  timeout      : timeout time that I send OADR messages to.
#c  inQueue      : data queue that stores data that I send as OADR messages to.
#c  inSocketMux  : mutex for access to queue that stores data that I send as OADR messages to.
#c  sleep_time   : sleep time when I failed to send OADR messages
#c  inMaster     : master object that this Object users
#c  debug        : swuitch this object send debun ngessage to.
#c **********************************************
"""
class oadrModokiClnt():
    def __init__(self, 
                 hostNameSendTo, 
                 portNoSendTo, 
                 timeout, 
                 inQueue = None, 
                 inSocketMux = None , 
                 sleep_time = 10, 
                 inMaster=None, 
                 debug = True):

        self.debug = debug
        self.sq = 0

        self.host = hostNameSendTo
        self.port = int(portNoSendTo)
        if timeout != None:
            self.timeout = int(timeout)
        else:
            self.timeout = -1

        # set queue
        self.wattQueue = inQueue
        self.queue = []
        
        # set mutex lock 
        self.queueMux = inSocketMux
        self.socketMux = threading.RLock()
        self.hostName = socket.gethostname()
        self.pid = os.getpid()
        self.sleep_time = sleep_time
        self.master = inMaster
        self.errsq = 0
        self.terminate = False
        #self.oadrWattHourIntervalTime = datetime.datetime(0,0,0,0,5,0,0)
        self.oadrWattHourIntervalTime = 5.0
        self.wattHourCalcBaseTime = datetime.datetime.now()
        self.oadrWattHourCalcBaseTime = datetime.datetime.now()
        self.privData = {}
        self.sendData = {}
        self.wkWattHour = {}
        
    """    
    #c ******************************************
    #c set watthour data collect interval time
    #c ******************************************   
    """
    def setOadrWattHourIntervalTime(self, inMinutes):
        wkMinute = 0
        try:
            wkMinute = int(str(inMinutes))
        except:
            return False
        
        if(wkMinute < 0):
            return False
        
        #self.oadrWattHourIntervalTime = datetime.datetime(0,0,0,0,wkMinute,0,0)
        self.oadrWattHourIntervalTime = wkMinute
        return
    
    """    
    #c ******************************************
    #c set watthour base time
    #c ******************************************    
    """
    def setWattHourCalcBaseTime(self, inTime):
        self.wattHourCalcBaseTime = inTime
        return
    
    """
    #c ******************************************
    #c convert watt data to watthour data
    #c ******************************************
    #c Input watt data
    #c data contains
    #c [0]: epmID (sequence nuber, cyclic, max value is 255)
    #c [1]: wattage (consume/generate watt at time)
    #c [2]: record time (current time at queuing)
    #c [3]: house name (name inside of simulator program)
    #c [4]: process id (id of simulator program)
    #c [5]: sequence number of client
    #c [6]: hgwID
    #c [7]: retry count(not used)
    #c ******************************************
    #c ******************************************
    #c output wattsHourData contains following info
    #c data [0]: wattHour every (Specified) min,
    #c data [1]: start time (dtstart->datetime),  "%Y-%m-%dT%H:%M:%SZ" Foremat is YYYY-mm-ddTHH:MM:SSZ"
    #c data [2]: end time,
    #c data [3]: duration (interval->duration->duration),
    #c data [4]: house name
    #c data [5]: process id (oaDrReportPayload->rID),
    #c data [6]: hgwID
    #c data [7]: seqNo
    #c data [8]: retry count(not used)
    #c ******************************************
    """
    def makeWattHourData(self):
        """
        手順
        1. キューからデータを取り出す。
        
        2. 電力量の計算。
        2-1. 前回データの時間を抽出
        2-2. 取り出した前回データの時間と今回データの時間の時間差を算出
        2-3. 算出した時間と今回データの電力、前回データの電力を元に電力量を計算
             （時間は前回時間と今回時間の差、電力は前回データと今回データの平均）
        2-4. 前回データの時間を今回データの時間で更新
        2-5. 送信データ用の電力量に今回算出した電力量を加算
        
        3. データ送信の判定。
        3-1. 前回データ送信時間と今回データの時間の時間差(送信時間差分)を計算
        3-2. 基準時刻がない場合はデータの時刻を基準時刻に設定
        3-3. 送信時間差分が設定した時間以上になったら以下の動作をしてデータ作成
        3-4. 今回データの時刻をデータ送信時間とする
        
        4. 作成したデータを送信キューにキューイング
        """
        
        """
        #c 1. キューからデータを取り出す。
        """        
        with self.queueMux:
            if(len(self.wattQueue) < 1):
                return

        currentData = None
        with self.queueMux:
            try:
                currentData = self.wattQueue.pop(0)
            except:
                return

        if(currentData == None):
            return

        """
        #c 2. 電力量の計算。
        """
        """
        #c 2-0. 前回データの抽出。
        #c      前回データは、house name(3番目のデータ)とprocess id(4) とhgwID(6番目のデータ)を連結した文字列
        #c      もしなかった場合は、今のデータを前回データと設定してリターン
        """
        keyData = str(currentData[3])+"_"+str(currentData[4])+"_"+str(currentData[6])
        if(self.privData.has_key(keyData)):
            privData = self.privData[keyData]
        else:
            """
            #c 今のデータを前回データと設定
            #c 同時に送信用のデータを設定
            """
            self.privData[keyData] = currentData
            self.wkWattHour[keyData] = 0.0
            return
        
        """
        #c 2-1. 前回データの電力と時間を抽出
        """
        currentWatt = currentData[1]
        prevWatt = privData[1]

        currentTime = currentData[2]
        prevTime = privData[2]
        
        """
        #c 2-2. 取り出した前回データの時間と今回データの時間の時間差を算出
        #c     データの形式は文字列("%Y-%m-%dT%H:%M:%SZ" Foremat is YYYY-mm-ddTHH:MM:SSZ")
        #c     これはOpenADRのフォーマット形式と同じ
        """
        #c データ形式の変換
        currentTimeDateTimeStr = str(currentTime).upper().split('T')
        currentTimeDateStr = currentTimeDateTimeStr[0].split('-')
        currentTimeTimeStr = currentTimeDateTimeStr[1].split(':')
        
        
        privTimeDateTimeStr = str(prevTime).upper().split('T')
        privTimeDateStr = privTimeDateTimeStr[0].split('-')
        privTimeTimeStr = privTimeDateTimeStr[1].split(':')
        
        
        currentDateTime = datetime.datetime(
                                     int(str(currentTimeDateStr[0])),
                                     int(str(currentTimeDateStr[1])),
                                     int(str(currentTimeDateStr[2])),
                                     int(str(currentTimeTimeStr[0])),
                                     int(str(currentTimeTimeStr[1])),
                                     int(str(currentTimeTimeStr[2])),0)
                                     
        privDateTime = datetime.datetime(
                                   int(str(privTimeDateStr[0])),
                                   int(str(privTimeDateStr[1])),
                                   int(str(privTimeDateStr[2])),
                                   int(str(privTimeTimeStr[0])),
                                   int(str(privTimeTimeStr[1])),
                                   int(str(privTimeTimeStr[2])),0)
                                   

        
        dateTimeDiff = currentDateTime - privDateTime
        """
        #c 2-3. 算出した時間と今回データの電力、前回データの電力を元に電力量を計算
        #c     （時間は前回時間と今回時間の差、電力は前回データと今回データの平均）
        """
        avgWatt = (float(str(currentWatt))+float(str(prevWatt)))/2.0
        wkWattHour = (float(str(dateTimeDiff.seconds)) * avgWatt)/3600.0
        """
        #c 2-5. 送信データ用の電力量に今回算出した電力量を加算
        """
        self.wkWattHour[keyData] += wkWattHour
        
        
            
        """
        #c 2-4. 前回データの時間を今回データの時間で更新
        """
        self.privData[keyData] = currentData

        """
        #c 3. データ送信の判定。
        """
        """
        #c 3-1. 前回データ送信時間と今回データの時間の時間差(送信時間差分)を計算
        """
        privSendTime = self.sendData[keyData] 
        
        """
        #c 3-2. 基準時刻がない場合はデータの時刻を基準時刻に設定
        #c      -> 送信用データ作成時に同時に作成。ここでは処理しない。
        """
        sendTimeDiff = currentDateTime - privSendTime
        
        """
        #c 3-3. 時間差の判定
        """
        if(sendTimeDiff.total_seconds() >= (self.oadrWattHourIntervalTime) * 60):
            """
            #c 3-3. 送信時間差分が設定した時間以上になったら以下の動作をしてデータ作成
            #c      設定単位は分単位,小数点以下は四捨五入
            """
            # sendTimeDiff をそのまま格納
            #diffStr = str(float(sendTimeDiff.minutes())+0.5).split(".")[0]
            """
            #c 送信データの設定
            #c 3-4. 今回データの時刻をデータ送信時間とする
            """
            wkSendData = [
                          self.wkWattHour[keyData],
                          self.privData[keyData][2],
                          currentData[2], 
                          sendTimeDiff, 
                          currentData[3], 
                          currentData[4], 
                          currentData[6],
                          currentData[5],
                          0]
            """
            #c 4-1. 作成したデータを送信キューにキューイング(ただし今は無効化)
            """
            #self.queue.append(wkSendData)
            """
            #c 4-2. 作成したデータを送信
            """
            self.oadrModokiSingleSend(wkSendData)
            """
            #c 5. 次の送信に備え、データを初期化
            """
            """
            #c 今のデータを前回データと設定
            #c 同時に送信用のデータを設定
            """
            self.privData[keyData] = currentData
            self.wkWattHour[keyData] = 0.0
            return
        return
    """
    #c ******************************************
    #c oadrModokiSingeSend
    #c send singel OADR message to energy manager.
    #c the message contains 1 data.
    #c parameters
    #c  wattsHourData : 
    #c    watt Hour . energy consumption durong some times.
    #C    this is an array of 8 Datas.
    #c ******************************************
    # wattsHourData contains following info
    # data [0]: wattHour every 5 min,
    # data [1]: start time (dtstart->datetime),  "%Y-%m-%dT%H:%M:%SZ" Foremat is YYYY-mm-ddTHH:MM:SSZ
    # data [2]: end time,
    # data [3]: duration (interval->duration->duration), class type is datetime.datetime
    # data [4]: house name
    # data [5]: process id (oaDrReportPayload->rID),
    # data [6]: hgwID
    # data [7]: seqNo
    # data [8]: retry count(not used)
    #C **********************************************
    """
    def oadrModokiSingleSend(self, wattsHourData):
        
        #c *******************
        #c make payload data
        #c *******************
        #c dammy vender ID (hostname + processID)
        venderModokiID = str(self.hostName) + "_" + str(wattsHourData[5])
        
        #c home gaeway ID 
        hgwIDWK = venderModokiID + "_" + hex(wattsHourData[6])

        #c sender name
        senderString = hgwIDWK + "_" + wattsHourData[4]
        """
        #c *******************
        #c make root data and set vender ID
        #c 送信するデータの大枠の部分のXMLデータを作成し、VenderIDを設定する
        #c *******************
        """
        xmlData = self.generateOADRXMLRoot(venderModokiID)
        
        """
        #c *******************
        #c make report data
        #c レポートデータの作成。
        #c *******************
        
        """
        
        oadrIntervals = self.generateOADRIntervalsRootXML()
        timeInterval = wattsHourData[3]
        minInterval = int(timeInterval.seconds)
        stringInterval = "P" + str(minInterval / 60) + "M"
       
        oadrEiInterval = self.generateOADREachIntervalXML(stringInterval, wattsHourData[7])
        xmlWattData = self.generateOADRReportPayloadData(hgwIDWK, wattsHourData[0])
       
        #c integrate all xml data to singel xml data area 
        oadrEiInterval.append(xmlWattData)
        oadrIntervals.append(oadrEiInterval)
        
        """
        #c *****************************
        #c レポートデータの外側の作成。このプログラムではレポートデータの中にはデータはひとつだけ含まれる
        #c ***************************
        """
        oadrReport = self.generateOADRReportXML(wattsHourData[1], senderString, wattsHourData[7], datetime.datetime.today(),stringInterval)
        oadrReport.append(oadrIntervals)
        
        
        
        #c make interval data (unit is minutes)
        xmlData.append(oadrReport)
        #c *********************
        #c make xml string from xml data to send to server
        #c *********************
        xmlOutdata = etree.tostring(xmlData, pretty_print=True)
        #print >>sys.stderr,xmlOutdata
        url = "http://" + str(self.host) + ":" + str(self.port) + "/"
        sending = True  
        while sending:
            try:  
                reqRes = requests.post(url, xmlOutdata)
                sending = False
                
            except requests.exceptions.ConnectionError as e:
                if (e.args[0][0] == 111):
                    if (self.debug):
                        print >> sys.stderr, "connection refused"
                    sending = False
                continue
            
            except Exception as e:
                if (self.debug):
                    wkTm = datetime.datetime.now()
                    wkTmStr = wkTm.strftime("%H:%M:%S:%f")
                    print >> sys.stderr, 'oadrModokiSingleSend error [Time:' + wkTmStr + '][type:' + str(type(e)) + '] [args:' + str(e.args) + '] [message:' + e.message + '] [e itself' + str(e) + ']'
                    print >> sys.stderr, "%s : oadrModokiMultiSend(%s:%d): failed time[%s]" % (__program__, self.host, self.port, wkTmStr)
                continue
            
        return True
    """
    #c *****************************************************
    #c Send single OADR messages in some times
    #c *****************************************************
    """
    def oadrModokiMultiSend(self):
        if(self.socketMux == None):
            return
        
        self.makeWattHourData()
        if(self.queue == None):
            return
        
        with self.socketMux:
            if(self.terminate):
                if(self.master != None):
                    self.master.alive = False
                return
                
#         with self.socketMux:
        qLen = len(self.queue) 
        if (qLen < 1):
            return

        while (qLen > 0):
            qLen = qLen -1
        
            # get data from queue
            try:
                with self.socketMux:
                    wattsHourData = self.queue.pop(0)
            except:
                for i in range(0,100):
                    time.sleep(self.sleep_time) 
                break
            
            if wattsHourData[0] == "-1":
                time.sleep(self.sleep_time * 10)
                if(self.master != None):
                    self.master.alive = False
                break
            
            self.oadrModokiSingleSend(wattsHourData)        

        return
    
    """
    #c ****************************************************************
    #c Make OADR message
    #c ****************************************************************
    """
    """
    #c *********************
    #c Make root element
    #c *********************
    """
    def generateOADRXMLRoot(self, inVenID):
        
        #(OADR_OADRUPDATEREPORT         , "oadr:oadrUpdateReport")
        rootData = etree.Element("{%s}oadrUpdateReport" % nameSpace_20B_elmMap['oadr'], nsmap=nameSpace_20B_elmMap)
        
        #(OADR_REQUESTID                , "pyld:requestID")
        rootRequestID = etree.Element( "{%s}requestID" % nameSpace_20B_elmMap['pyld'], nsmap=nameSpace_20B_elmMap)
        rootRequestID.text = "String" 
        rootData.append(rootRequestID)

        #(OADR_VENID                    , "ei:venID");
        venID = etree.Element("{%s}venID" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        venID.text = str(inVenID)
        rootData.append(venID)
        
        return rootData
 
    """
    #c ************************
    #c make report element
    #c ************************
    #c ************************
    #c 以下の部分をつくる
    

    <oadr:oadrReport>
        <xcal:dtstart>
            <xcal:date-time>2001-12-17T09:30:47Z</xcal:date-time>
        </xcal:dtstart>
        <xcal:duration>
            <xcal:duration>P10M</xcal:duration>
        </xcal:duration>
        <strm:intervals>
            <ei:interval>
                <xcal:duration>
                    <xcal:duration>P5M</xcal:duration>
                </xcal:duration>
                <xcal:uid>
                    <xcal:text>0</xcal:text>
                </xcal:uid>
                <oadr:oadrReportPayload>
                    <ei:rID>123</ei:rID>
                    <ei:confidence>95</ei:confidence>
                    <ei:accuracy>0.2</ei:accuracy>
                    <ei:payloadFloat>
                        <ei:value>3.14159E0</ei:value>
                    </ei:payloadFloat>
                    <oadr:oadrDataQuality>Quality Good - Non Specific</oadr:oadrDataQuality>
                </oadr:oadrReportPayload>
                <oadr:oadrReportPayload>
                    <ei:rID>124</ei:rID>
                    <ei:confidence>100</ei:confidence>
                    <ei:accuracy>0</ei:accuracy>
                    <ei:payloadFloat>
                        <ei:value>20</ei:value>
                    </ei:payloadFloat>
                    <oadr:oadrDataQuality>Quality Good - Non Specific</oadr:oadrDataQuality>
                </oadr:oadrReportPayload>
            </ei:interval>
            <ei:interval>
                <xcal:duration>
                    <xcal:duration>P5M</xcal:duration>
                </xcal:duration>
                <xcal:uid>
                    <xcal:text>1</xcal:text>
                </xcal:uid>
                <oadr:oadrReportPayload>
                    <ei:rID>123</ei:rID>
                    <ei:confidence>95</ei:confidence>
                    <ei:accuracy>0.2</ei:accuracy>
                    <ei:payloadFloat>
                        <ei:value>4.15E0</ei:value>
                    </ei:payloadFloat>
                    <oadr:oadrDataQuality>Quality Good - Non Specific</oadr:oadrDataQuality>
                </oadr:oadrReportPayload>
                <oadr:oadrReportPayload>
                    <ei:rID>124</ei:rID>
                    <ei:confidence>100</ei:confidence>
                    <ei:accuracy>0</ei:accuracy>
                    <ei:payloadFloat>
                        <ei:value>21</ei:value>
                    </ei:payloadFloat>
                    <oadr:oadrDataQuality>Quality Good - Non Specific</oadr:oadrDataQuality>
                </oadr:oadrReportPayload>
            </ei:interval>
        </strm:intervals>
        <ei:eiReportID>RP_54321</ei:eiReportID>
        <ei:reportRequestID>RR_65432</ei:reportRequestID>
        <ei:reportSpecifierID>RS_12345</ei:reportSpecifierID>
        <ei:reportName>HISTORY_USAGE</ei:reportName>
        <ei:createdDateTime>2001-12-17T09:30:47Z</ei:createdDateTime>
    </oadr:oadrReport>

    #c ************************
    """
    def generateOADRReportXML(self, 
                              dtstart_datetime, 
                              sender, 
                              seqNo, 
                              dateData = datetime.datetime.today(),
                              totalDuration="P5M"):
        reqIDString = sender+"_"+str(seqNo)
        """
        #c *************************
        #c (OADR_OADRREPORT               , "oadr:oadrReport")
        #c  <oadr:oadrReport>
        #c    ......
        #c  </oadr:oadrReport>
        #c *************************
        """
        oadrReport = etree.Element("{%s}oadrReport" % nameSpace_20B_elmMap['oadr'], nsmap=nameSpace_20B_elmMap)
        
        """
        #c *************************
        #c (OADR_DTSTART                  , "xcal:dtstart")
        #c <xcal:dtstart>
        #c     ....
        #c </xcal:dtstart>
        #c *************************
        """
        oadrDtStart = etree.Element("{%s}dtstart" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        
        """
        #c ***********************************
        #c (OADR_DATETIME                 , "xcal:date-time")
        #c <xcal:date-time> </xcal:date-time>
        #c ***********************************
        """
        oadrDateTime = etree.Element("{%s}date-time" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        """
        #c ***********************************
        #c record today data(deta send)
        #c wkDate = today.strftime("%Y-%m-%dT%H:%M:%SZ")
        #c ***********************************
        #c *********************************** c#
        #c Use Parameter dtstart_datetime      c#
        #c *********************************** c#
        """
        wkDate = dtstart_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        oadrDateTime.text = str(wkDate)
        
        oadrDtStart.append(oadrDateTime)
        oadrReport.append(oadrDtStart)
        
        
        """
        #c **********************************
        #c (OADR_DURATION                 , "xcal:duration")
        #c **********************************
        """
        oadrOutDuration = etree.Element("{%s}duration" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)

        """
        #c **********************************
        #c (OADR_DURATION                 , "xcal:duration")
        #c **********************************
        #c *************************************** c#
        #c  Use Parameter totalDuration            c#
        #c *************************************** c#
        """
        oadrInDuration = etree.Element("{%s}duration" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        oadrInDuration.text = totalDuration
        
        oadrOutDuration.append(oadrInDuration)
        oadrReport.append(oadrOutDuration)
        #(OADR_DURATION                 , "xcal:duration")
        """
        #c **********************************
        #c (OADR_EIREPORTID                , "ei:eiReportID")
        #c **********************************
        """
        eiReportID = etree.Element("{%s}eiReportID" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        eiReportID.text = reqIDString
        oadrReport.append(eiReportID)
        """
        #c **********************************
        #c (OADR_REPORTREQUESTID        , "ei:reportRequestID")
        #c **********************************
        """
        reportRequestID = etree.Element("{%s}reportRequestID" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        reportRequestID.text = reqIDString
        oadrReport.append(reportRequestID)
        
        """
        #c **********************************
        #c (OADR_REPORTSPECIFIERID        , "ei:reportSpecifierID")
        #c **********************************
        """
        reportSpecifierID = etree.Element("{%s}reportSpecifierID" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        reportSpecifierID.text = reqIDString
        oadrReport.append(reportSpecifierID)
        
        """
        #c **********************************
        #c (OADR_REPORTNAME                , "ei:reportName")
        #c **********************************
        """
        reportName = etree.Element("{%s}reportName" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        reportName.text = "Wattage"
        oadrReport.append(reportName)
        """
        #c ***********************************
        #c (OADR_CREATEDDATETIME        , "ei:createdDateTime")
        #c ***********************************
        #c *********************************** c#
        #c Use Parameter ddateData             c#
        #c *********************************** c#
        """
        createdDateTime = etree.Element("{%s}createdDateTime" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        createdDateTime.text = dateData.strftime("%Y-%m-%dT%H:%M:%SZ")
        oadrReport.append(createdDateTime)

        """
        #c ***********************************
        #c end
        #c ***********************************
        """
        return oadrReport
    """
    #c *******************************************************
    #c make Interval section
    #c *******************************************************
    """
    def generateOADRIntervalsRootXML(self):
        """
        #c ***********************************
        #c (OADR_INTERVALS                , "strm:intervals")
        #c ***********************************
        """
        oadrIntervals = etree.Element("{%s}intervals" % nameSpace_20B_elmMap['strm'], nsmap=nameSpace_20B_elmMap)
        return oadrIntervals
    
    """    
    #c *******************************************************
    #c make each interval data
    #c Parameter:
    #c     interval : time interval (string. example is "P5M")
    #c     uid      : user id       (int. example is "1")
    #c *******************************************************
    """
    def generateOADREachIntervalXML(self, interval, uid=os.getpid()):
        """
        #c **************************************************
        #c (OADR_INTERVAL                 , "ei:interval")
        #c **************************************************
        """
        oadrEiInterval = etree.Element("{%s}interval" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        
        """
        #c **************************************************
        #c (OADR_DURATION                 , "xcal:duration")
        #c **************************************************
        """
        oadrIntervalOutDuration = etree.Element("{%s}duration" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        """
        #c **************************************************
        #c (OADR_DURATION                 , "xcal:duration")
        #c **************************************************
        #c *********************************************** c#
        #c Use Parameter interval                          c#
        #c *********************************************** c#
        """
        oadrIntervalInDuration = etree.Element("{%s}duration" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        oadrIntervalInDuration.text = interval
        oadrIntervalOutDuration.append(oadrIntervalInDuration)
        oadrEiInterval.append(oadrIntervalOutDuration)
        
        """
        #c **************************************************
        #c (OADR_UID                      , "xcal:uid")
        #c **************************************************
        #c *********************************************** c#
        #c Use Parameter uid                               c#
        #c *********************************************** c#
        """
        oadrdUid01 = etree.Element("{%s}uid" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        oadrUidIntext = etree.Element("{%s}text" % nameSpace_20B_elmMap['xcal'], nsmap=nameSpace_20B_elmMap)
        oadrUidIntext.text = str(uid)
        oadrdUid01.append(oadrUidIntext)
        oadrEiInterval.append(oadrdUid01) 
        
        return oadrEiInterval
    """
    #c ***************************************************************
    #c make payload data
    #c (inside of <oadr:oadrReportPayload/>)
    #c Parameters:
    #c     inRID         : rid      (int. example is "1")
    #c     wattHourValue : wattHour (float. example is "12.345")
    #c ***************************************************************
    """
    def generateOADRReportPayloadData(self, inRID, wattHourValue):  
        """
        #c ***********************************************************
        #c (OADR_OADRREPORTPAYLOAD        , "oadr:oadrReportPayload")
        #c ***********************************************************
        """
        oadrReportPayload = etree.Element("{%s}oadrReportPayload" % nameSpace_20B_elmMap['oadr'], nsmap=nameSpace_20B_elmMap)
        
        """
        #c ************************************************************
        #c (OADR_RID                        , "ei:rID")
        #c ************************************************************
        #c ********************************************************* c#
        #c Use Parameter inRID                                       c#
        #c ********************************************************* c#
        """
        rID = etree.Element("{%s}rID" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        rID.text = str(inRID)
        oadrReportPayload.append(rID)
        
        """
        #c ************************************************************
        #c (OADR_CONFIDENCE                , "ei:confidence")
        #c ************************************************************
        """
        confidence = etree.Element( "{%s}confidence" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        confidence.text = "95"
        oadrReportPayload.append(confidence)
        
        """
        #c ************************************************************
        #c (OADR_ACCURACY                , "ei:accuracy")
        #c ************************************************************
        """
        accuracy = etree.Element("{%s}accuracy" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        accuracy.text = "0.2"
        oadrReportPayload.append(accuracy)
        
        """
        #c ************************************************************
        #c (OADR_PAYLOADFLOAT            , "ei:payloadFloat")
        #c ************************************************************
        """
        payloadFloat = etree.Element("{%s}payloadFloat" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        
        """
        #c ************************************************************
        #c (OADR_OADRVALUE                , "ei:value")
        #c ************************************************************
        #c ********************************************************* c#
        #c Use Parameter wattHourValue                               c#
        #c ********************************************************* c#
        """
        payloadValue = etree.Element("{%s}value" % nameSpace_20B_elmMap['ei'], nsmap=nameSpace_20B_elmMap)
        payloadValue.text = str(wattHourValue)
        payloadFloat.append(payloadValue)
        oadrReportPayload.append(payloadFloat)
        
        """
        #c **************************************************************
        #c (OADR_OADRDATAQUALITY        , "oadr:oadrDataQuality")
        #c **************************************************************
        """
        oadrDataQuality = etree.Element("{%s}oadrDataQuality" % nameSpace_20B_elmMap['oadr'], nsmap=nameSpace_20B_elmMap)
        oadrDataQuality.text = "Good"
        oadrReportPayload.append(oadrDataQuality)
        return oadrReportPayload

"""   
# ***********************************************************************        
# **********************************************
# client of OADR sv
# **********************************************
# ***************************************************************************
# clnt oc sml send thread
# ***************************************************************************
"""

"""
#c **********************************************
#c Thread Object initializer
#c when initalize object, use specifies these infomations
#c parameters
#c  uSrvHost     : hostname that I send OADR messages to.
#c  uSrvPort     : port no that I send OADR messages to.
#c  uSrvtimeout  : timeout time that I send OADR messages to.
#c  inSocketMux  : mutex for access to queue that stores data that I send as OADR messages to.
#c  inQueue      : data queue that stores data that I send as OADR messages to.
#c  sleep_time   : sleep time when I failed to send OADR messages
#c  debug        : switch this object send debug message to.
#c **********************************************
#c Data Format of inQueue 
#c  wattsHourData : 
#c    watt Hour . energy consumption durong some times.
#c    this is an array of 8 Datas.
#c ******************************************
#c wattsHourData contains following info
#c data [0]: wattHour every 5 min,
#c data [1]: start time (dtstart->datetime),  "%Y-%m-%dT%H:%M:%SZ" Foremat is YYYY-mm-ddTHH:MM:SSZ
#c data [2]: end time,
#c data [3]: duration (interval->duration->duration), T5M
#c data [4]: house name
#c data [5]: process id (oaDrReportPayload->rID),
#c data [6]: hgwID
#c data [7]: seqNo
#c data [8]: retry count(not used, but reserved)
#c **********************************************
"""
class oadrModokiClntThread(threading.Thread):

    def __init__(self, 
                 uSrvHost, 
                 uSrvPort, 
                 uSrvTimeout, 
                 inSocketMux, 
                 inQueue , 
                 sleep_time, 
                 debug=True):
        self.stop = threading.Event()
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.myOadrModokiClient  = oadrModokiClnt(uSrvHost, uSrvPort, uSrvTimeout, inQueue, inSocketMux, sleep_time, self)
        self.alive = True
        self.debug = debug
        self.threaded = False
        return
    
    def send(self, wattsHourData):
        if(self.threaded):
            return
        rval = False
        while(rval == False):
            rval = self.myOadrModokiClient.oadrModokiSingleSend(wattsHourData)
            if(rval == False):
                for i in range(0, 10):
                    time.sleep(self.sleep_time)
                    
        return


    def run(self):
        self.threaded = True
        while self.alive:
            send = 0
            time.sleep(self.sleep_time)
            self.myOadrModokiClient.oadrModokiMultiSend()
        
        endStr = "Terminate oadrModokiClnt["+ str(os.getpid()) +"]"
        if(self.debug):
            print >>sys.stderr, endStr
        return

    def terminate(self):
        self.alive = False
        self.myOadrModokiClient.terminate = True

