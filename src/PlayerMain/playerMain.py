# -*- coding: utf-8 -*-
"""
#c ******************************
#c Player メインクラス
#c ******************************
"""

"""
#c imports
"""
import sys
from Synchronizer.SyncObject import *
from DataSender.oadrModokiClnt import *
from DataSender.wattXMLClnt import *

class simhomePlayerMain:
    def __init__(self, confXMLObj, syncObj, inDataFile, inIndex = 1):
        self.syncClientObject = syncObj
        self.confXMLObject = confXMLObj
        self.dataFile = inDataFile
        self.useXMLClnt = None
        self.genXMLClnt = None
        self.useOADRClnt = None
        self.genOADRClnt = None
        self.index = inIndex
        self.useXMLmux = threading.RLock()
        self.genXMLmux = threading.RLock()
        self.useOADRmux = threading.RLock()
        self.genOADRmux = threading.RLock()
        self.useDataQueue = []
        self.dataFD = None
        self.dataBuf = []
        return
    
    """
    #c **************************************
    #c
    #c **************************************
    """
    def setup(self):
        """
        #c セットアップの開始
        """
    
        #c パラメータチェック
        if((self.syncClientObject == None ) or (self.confXMLObject == None)):
            print >>sys.stderr,"object is not Set"
            return False
        
        try:
            """
            #c xml データ送信オブジェクト生成
            #c wattXMLClient(
                hgwId, 
                host, 
                myListenPort, 
                timeout, sleep_time = 10, inMuxSocket = None, inMaster = None):
            #c
            #c        
            """
        
            self.useXMLClnt = wattXMLClient(
                                        self.index, 
                                        self.confXMLObject.UseDataXMLSendHost,
                                        self.confXMLObject.UseDataXMLSendPort,
                                        self.confXMLObject.timeout)
        
            self.genXMLClnt = wattXMLClient(
                                        self.index,
                                        self.confXMLObject.GenDataXMLSendHost,
                                        self.confXMLObject.GenDataXMLSendPort,
                                        self.confXMLObject.timeout)
        
            """
            #c OADR情報送信オブジェクト設定
            """
            self.useOADRClnt = oadrModokiClnt(
                                          self.confXMLObject.UseDataOADRSendHost,
                                          self.confXMLObject.UseDataOADRSendPort,
                                          self.confXMLObject.timeout)
            self.genOADRClnt = oadrModokiClnt(
                                          self.confXMLObject.GenDataOADRSendHost,
                                          self.confXMLObject.GenDataOADRSendPort,
                                          self.confXMLObject.timeout)
            return True
        
        except Exception as e:
            # print >>sys.stderr, "Exception: [type:"+str(type(e))+"][args:"+str(e.args)+"][message:"+e.message+"][Exception itself:"+str(e)+"]"
            print >>sys.stderr, "Exception: "+str(e)
            return False
        
        return True
    """
    #c
    #c データ再生の開始
    #c
    """
    def playStart(self):
        
        """
        #c
        #c データ再生処理
        #c 行う動作
        #c 0-1. データファイル読み込み
        #c 0-2. データファイルの格納
        #c 1. データ送信ループ
        #c 1-1. 格納された領域からデータをひとつ取り出す。
        #c 1-2. データを解析し、データ送信情報を設定
        #c 1-2. 電力データを送信
        #c 1-3. OADR情報（消費電力量のデータ) を送信
        #c 1-4. 送信後の同期メッセージ送信と同期待ち
        #c 1-5. 次の送信データがあれば1-1へ。送信データがなければ、データ送信終了を上位ノードへ送信し、
        #c
        """
        
        """
        #c
        #c 0-1. データファイル読み込み
        #c 0-2. データファイルの格納 格納形式は [time,value,value...
        #c      ただし1行目は [DATE, date1, date2, ....
        #c      データ再生ができるためのデータ格納形式についても検討(合意取り)が必要
        #c      現状は、シミュレーション開始時刻をどのように設定するか？　要検討
        #c 
        """
        try:
            self.dataFD = open(self.dataFile,'r')
            wkLineBuf = self.dataFD.read().split('\r')
            wkBuf = []
            for line in wkLineBuf:
                if(("wh/m2") in line.lower()):
                    continue
                self.dataBuf.append(line.lower().split(','))
        except Exception as e:
            print "Exception "+str(e)
            return
        
        
        
        
        """
        #c データ送信後の同期
        #c 動作
        #c 1.マスターノードにシミュレーションの時刻を送信する。
        #c 2.同期待ちをする
        #c 3.同期メッセージを解析し、"end"であればデータ送信を中断する
        
        vCurrentTimeString = self.Vcurrent.strftime('[%Y-%m-%d/%H:%M:%S]')
            #print >>sys.stderr, "[" + self.programName +"] done ["+str(i-1)+"]"
            #send status
            if(self.syncClientObject != None):
                #print >>sys.stderr, "[" + self.programName +"] send next ["+str(i-1)+"]"
                self.syncClientObject.doNextStep(vCurrentTimeString)
                
                if(self.syncClientObject.doExit() == True):
                    #print >>sys.stderr, "[" + self.programName + "] Receive end message ["+str(i-1)+"]"
                    self.alive = False
                    break
        """
        return
    