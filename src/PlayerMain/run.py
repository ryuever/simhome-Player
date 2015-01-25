# -*- coding: utf-8 -*-
"""
#c *****************************
#c simhome player main
#c *****************************
"""
"""
#c imports
"""
import sys
import codecs
from optparse import OptionParser
from Synchronizer.SyncObject import *
from DataSender.oadrModokiClnt import *
from DataSender.wattXMLClnt import *
from confXMLObject import *
from playerMain import  *
from xml.etree.ElementTree import fromstring

__program__ = "simhomePlayer"
__version__ = "0.0.1"

"""
#c main routine
"""

if __name__ == '__main__':
    """
    #c read arguments 
    """
    """
    #c options parsing
    #c パラメータの設定
    """
    usage = "usage: %s \n" \
             "\t-c <configuration_file>     : config for simhome player\n" \
             "\t-d <data_file>              : data file of simulation play (csv format)\n" \
             "\t-x <nodename>               : master node for synchronize\n" \
             "\t-y <nodeport>               : master node port for synchronize\n" \
             "\t-p <selfport>               : myself port for get synchronize message\n" \
             "\t-z <pgname>                 : program name of myself\n" \
             % (__program__)
    
    parser = OptionParser(usage, version = "version: %s" % __version__)
    
    parser.add_option("-c", "--conf", default="", type="string", dest="conf",
            help="specify the configuration file name for %s." % __program__)
    
    parser.add_option("-d", "--data", default="", type="string", dest="datafile",
            help="specify the configuration file name for %s." % __program__)
    
    # c 2014-10-08 h-fujita
    parser.add_option("-x", "--masterhost", default=None, type="string",
            dest="master_node", help="specify the master node for synchronize")
    
    parser.add_option("-y", "--masterport", default=None, type="int",
            dest="master_port", help="specify the port of master node for synchronize")

    parser.add_option("-p", "--selfsyncport", default=None, type="int",
            dest="port_num", help="secify the self port for synchroneze")
    
    parser.add_option("-z", "--programname", default=None, type="string",
            dest="program_name", help="secify the program name of myself")
    
    (options, args) = parser.parse_args()
    
    """
    #c
    #c check the configuration file
    #c 設定ファイルとデータファイルの設定
    #c
    """
    if not os.path.isfile(options.conf):
        print >>sys.stderr, "%s: main: config does not exist: %s" % \
                (__program__, options.conf)
        print usage
        sys.exit()
        
    if not os.path.isfile(options.datafile):
        print >>sys.stderr, "%s: main: data file does not exist: %s" % \
                (__program__, options.datafile)
        print usage
        sys.exit()
        
    
    """
    #c データ送信先のホストとノードの解析
    """    
    masterNode = options.master_node
    masterNodePort = options.master_port
    listenPort = options.port_num
    programName = "simhomePlayer_"+str(os.getpid())
    if(options.program_name != None):
        programName = options.program_name
    

    if((masterNodePort == None ) or (listenPort == None)):
        print >>sys.stderr, "%s: main: parentPort or listenPort is not specified:" % (__program__)
        print usage
        sys.exit(-1)
        
    if((masterNodePort < 1) or (listenPort < 1)):
        print >>sys.stderr, "%s: main: invalid parentPort or listenPort is specified:" % (__program__)
        print usage
        sys.exit(-1)
    
    """
    #c
    #c XMLデータの読み込み
    #c
    """
    confXMLObject = ConfXMLObject()
    confXMLObject.read(options.conf)
    confXMLObject.parseXML()
    
    syncClientObject = None
    syncClientObject = SyncClientObject(programName, masterNode, masterNodePort, listenPort)
    syncClientObject.regist()
    #syncClientObject.listenForSync()
    if(syncClientObject.doExit()):
        print >>sys.stderr, "[" + programName +"] send end "
        syncClientObject.sendSyncMessage("end")
        sys.exit(-1)    
    
    """
    #c play player
    """
    simPlayer = simhomePlayerMain(confXMLObject, syncClientObject, options.datafile)
    
    if(simPlayer.setup() == False):
        print >>sys.stderr, "[" + programName +"] could not start because of setup error "
        sys.exit(-1)
    

    simPlayer.playStart()
    


"""
#c end of program
"""