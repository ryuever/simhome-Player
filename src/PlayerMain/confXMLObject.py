# -*- coding: utf-8 -*-

import sys
import codecs
from optparse import OptionParser
from Synchronizer.SyncObject import *
from DataSender.oadrModokiClnt import *
from DataSender.wattXMLClnt import *
from xml.etree.ElementTree import fromstring

"""
#c XML Parser
"""
class ConfXMLObject:
    """
    #c 初期化
    """
    def __init__(self):
        """
        #c 変数の初期化
        """
        self.confXMLBuf = ""
        self.elem = None
        self.targetElem = None
        self.xmlStatus = False
        self.GenDataXMLSendHost = ""
        self.GenDataXMLSendPort = 0
        self.GenDataOADRSendHost = ""
        self.GenDataOADRSendPort = 0
        
        self.UseDataXMLSendHost = ""
        self.UseDataXMLSendPort = 0
        self.UseDataOADRSendHost = ""
        self.UseDataOADRSendPort = 0
        
        self.timeout = 60
        """
        #c 定数の設定
        """
        self.Use_SrvHost = "Use_SrvHost" 
        self.Use_SrvPort = "Use_SrvPort" 
        self.Gen_SrvHost = "Gen_SrvHost" 
        self.Gen_SrvPort = "Gen_SrvPort" 
        self.SrvTimeout = "SrvTimeout" 
        self.oadr_Srv_Gen_Host = "oadr_Srv_Gen_Host" 
        self.oadr_Srv_Gen_Port = "oadr_Srv_Gen_Port" 
        self.oadr_Srv_Use_Host = "oadr_Srv_Use_Host" 
        self.oadr_Srv_Use_Port = "oadr_Srv_Use_Port" 
        return

    """
    #c
    #c ファイルの読み込み
    #c
    """
    def read(self, inFileName):

        try:
            """
            #c ファイルの読み込み
            """
            self.confXMLBuf = open(inFileName).read()
            

            
        except Exception as e:
            """
            #c 例外発生時の処理。
            #c オブジェクトを無効の状態にしておく
            """
            print "Exception "+str(e)
            self.confXMLBuf = ""
            self.elem = None
            self.xmlStatus = False
            return False
        
        return True
    
    def parseXML(self, XMLBuf = None):
        if(XMLBuf == None):
            XMLBuf = self.confXMLBuf
            
        try:
            """
            #c 読み込んだデータの解析
            """
            self.elem = fromstring(self.confXMLBuf)
            
            self.targetElem = self.elem.find('Generic')
            
            """
            #c 要素の抽出
            """
            attribDic = self.targetElem.attrib
        
            if(attribDic.has_key(self.Gen_SrvHost)):
                self.GenDataXMLSendHost = str(attribDic[self.Gen_SrvHost])
                
            if(attribDic.has_key(self.Gen_SrvPort)):
                self.GenDataXMLSendPort = int(str(attribDic[self.Gen_SrvPort]))
                
            if(attribDic.has_key(self.oadr_Srv_Gen_Host)):
                self.GenDataOADRSendHost = str(attribDic[self.oadr_Srv_Gen_Host])
                
            if(attribDic.has_key(self.oadr_Srv_Gen_Port)):
                self.GenDataOADRSendPort = int(str(attribDic[self.oadr_Srv_Gen_Port]))
        
            if(attribDic.has_key(self.Use_SrvHost)):
                self.UseDataXMLSendHost = str(attribDic[self.Use_SrvHost])
                
            if(attribDic.has_key(self.Use_SrvPort)):
                self.UseDataXMLSendPort = int(str(attribDic[self.Use_SrvPort]))
                
            if(attribDic.has_key(self.oadr_Srv_Use_Host)):
                self.UseDataOADRSendHost = str(attribDic[self.oadr_Srv_Use_Host])
            
            if(attribDic.has_key(self.oadr_Srv_Use_Port)):
                self.UseDataOADRSendPort = int(str(attribDic[self.oadr_Srv_Use_Port]))

            if(attribDic.has_key(self.SrvTimeout)):
                self.timeout = int(str(attribDic[self.SrvTimeout]))

            return True
            
        except Exception as e:
            """
            #c 例外発生時の処理。
            #c オブジェクトを無効の状態にしておく
            """
            print "Exception "+str(e)
            self.confXMLBuf = ""
            self.elem = None
            self.xmlStatus = False
            return False
        
        return True
