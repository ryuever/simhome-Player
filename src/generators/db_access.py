from __future__ import division
import MySQLdb
from datetime import datetime, timedelta
import time
import sys
import socket
# from socket import *
from multiprocessing import Manager, Process
from ctypes import c_char_p

class ClimateRecordAccess(object):    
    def access_db(self,cli_data):
        myDB = MySQLdb.connect(host="150.65.230.155",port=3306,user="dc_server",passwd="dc_server!",db="dc_server_db")
        handler = myDB.cursor()

        end_time_dt = datetime.strptime("2015-03-26 00:00:00", '%Y-%m-%d %H:%M:%S')
        temp_item_avg = 25
        radiation_item_avg = 0
        ws_item_avg = 1
        measured_pow_avg = 0

        while True:
            time.sleep(0.3)
            temp_time = end_time_dt
    
            start_time_dt = temp_time
            start_time = datetime.strftime(start_time_dt, "%Y/%m/%d %H:%M:%S")

            end_time_dt = temp_time + timedelta(minutes = 5)    
            end_time = datetime.strftime(end_time_dt, "%Y/%m/%d %H:%M:%S")

            """ temperature data """
            temp_sql = 'select * from t_device_value where device_id = "000E7BED7B10001101"\
            and property = "MeasuredTemp" and get_date > "{0}" and  get_date< "{1}";'.format(start_time, end_time)
            # temp_sql = 'select * from t_experiment_value where device_id = "000E7BED7B10001101"\
            # and property = "MeasuredTemp" and get_date > "{0}" and get_date<"{1}" and gateway_id="iHouse_gateway"\
            # and experiment_id="ihouseproject";'.format(start_time, end_time)
            # print(temp_sql)    
            handler.execute(temp_sql)
            temp_results = handler.fetchall()    
            # print(results)
            # for table t_experiment_value
            # if temp_results != ():
            #     count = 0
            #     item_sum = 0
            #     for item in temp_results:
            #         # print(item)
            #         if item[5] != "" and item[5] != " ":
            #             item_sum += int(item[5], 16)
            #             count += 1
            #     item_avg = item_sum / count
            #     timestamp = item[4] - timedelta(minutes=(item[4].minute - int(item[4].minute / 5) * 5), seconds=item[4].second)
            #     print("timestamp : ", timestamp, "value : ", round(item_avg,2))
            if temp_results != ():
                temp_count = 0
                temp_item_sum = 0
                for temp_item in temp_results:
                    # print(temp_item)
                    if temp_item[4] != "" and temp_item[4] != " ":
                        temp_item_sum += int(temp_item[4], 16)
                        temp_count += 1
                if temp_count == 0:
                    temp_item_avg = 0
                else:
                    temp_item_avg = round(temp_item_sum / (temp_count * 10), 2)
        
                temp_timestamp = temp_item[3] - \
                                 timedelta(minutes=(temp_item[3].minute - int(temp_item[3].minute / 5) * 5), seconds=temp_item[3].second)
        
                print("temp_timestamp : ", temp_timestamp, "value : ", round(temp_item_avg,2))

            """ radiation data """
            radiation_sql = 'select * from t_device_value where device_id = "000E7BEB7B10000d01" and property="Sunshine" \
            and gateway_id="iHouse_sspf_gateway" and get_date > "{0}" and  get_date< "{1}";'.format(start_time, end_time)            
            handler.execute(radiation_sql)
            radiation_results = handler.fetchall()    
            if radiation_results != ():
                radiation_count = 0
                radiation_item_sum = 0
                for radiation_item in radiation_results:
                    # print(radiation_item)
                    if radiation_item[4] != "" and radiation_item[4] != " ":
                        radiation_item_sum += int(radiation_item[4], 16)
                        radiation_count += 1
                if radiation_count == 0:
                    radiation_item_avg = 0
                else:
                    radiation_item_avg = round(radiation_item_sum / radiation_count, 2)
        
                radiation_timestamp = radiation_item[3] - \
                                      timedelta(minutes=(radiation_item[3].minute - int(radiation_item[3].minute / 5) * 5),\
                                                seconds=radiation_item[3].second)
        
                # print("radiation_timestamp : ", radiation_timestamp, "value : ", round(radiation_item_avg,2))

            """ measured power data """
            measured_pow_sql = 'select * from t_device_value where device_id = "000E7B997110028703" and property="InstantPower" \
            and gateway_id="iHouse_sspf_gateway" and get_date > "{0}" and  get_date< "{1}";'.format(start_time, end_time)            
            handler.execute(measured_pow_sql)
            measured_pow_results = handler.fetchall()    
            if measured_pow_results != ():
                measured_pow_count = 0
                measured_pow_sum = 0
                for measured_pow in measured_pow_results:
                    # print(measured_pow)
                    if measured_pow[4] != "" and measured_pow[4] != " " and not measured_pow[4].startswith('f') :
                        measured_pow_sum = measured_pow_sum + int(measured_pow[4], 16)
                        measured_pow_count = measured_pow_count + 1
                if measured_pow_count == 0:
                    measured_pow_avg = 0
                else:
                    measured_pow_avg = round(measured_pow_sum / measured_pow_count, 2)
        
                measured_pow_timestamp = measured_pow[3] - \
                                     timedelta(minutes=(measured_pow[3].minute - int(measured_pow[3].minute / 5) * 5),\
                                                seconds=measured_pow[3].second)
        
                print("measured pow : ", measured_pow_timestamp, "value : ", round(measured_pow_avg,2))
                
            """   wind speed data """
            # ws_sql = 'select * from t_device_value where device_id = "000E7B087C10001f01" and \
            # property = "WindSpeed" and get_date > "{0}" and  get_date< "{1}";'.format(start_time, end_time)
            ws_sql = 'select * from t_experiment_value where device_id = "000E7B087C10001f01" and property = "WindSpeed"\
            and get_date > "{0}" and get_date<"{1}" and gateway_id="iHouse_gateway" and experiment_id="ihouseproject";'.format(start_time, end_time)
            # print(ws_sql)    
            handler.execute(ws_sql)
            ws_results = handler.fetchall()
            if ws_results != ():
                ws_count = 0
                ws_item_sum = 0
                for ws_item in ws_results:
                    # print(ws_item)
                    if ws_item[5] != "" and ws_item[5] != " ":
                        ws_item_sum += float(ws_item[5])
                        ws_count += 1
                if ws_count == 0:
                    ws_item_avg = 0
                else:
                    ws_item_avg = round(ws_item_sum / ws_count, 2)                        
                ws_timestamp = ws_item[4] - \
                               timedelta(minutes=(ws_item[4].minute - int(ws_item[4].minute / 5) * 5), seconds=ws_item[4].second)
                print("ws_timestamp : ", ws_timestamp, "value : ", round(ws_item_avg,2))
            cli_data.value = '<climate><timestamp>' + datetime.strftime(start_time_dt, "%Y/%m/%d %H:%M:%S") + '</timestamp>' \
                             + '<temperature>' + str(temp_item_avg) + '</temperature>' \
                             + '<radiation>' + str(radiation_item_avg) + '</radiation>'\
                             + '<measured_pow>' + str(measured_pow_avg) + '</measured_pow>'\
                             + '<windspeed>' + str(ws_item_avg) + '</windspeed>' + '</climate>'            

def send_climate_data(connection, ):
    while True:
        time.sleep(0.3)
        data = cli_data.value
        xml_text = data.encode()
        xml_len  = len(data)        
        connection.sendall("\n" + str(xml_len).encode() + b' ' +xml_text)    

if __name__ == "__main__":
    climate_obj = ClimateRecordAccess()

    manager = Manager()    
    cli_data = manager.Value(c_char_p, "")
    process = Process(target=climate_obj.access_db, args=(cli_data, ))
    process.start()
    
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = 'localhost'
        serverPort = '50000'
    
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # make a TCP socket object
    sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print "run launchserver"
    sockobj.bind((serverHost, eval(serverPort)))                   # bind it to server port number
    sockobj.listen(5)                                # allow 5 pending connects

    while True:                                  # wait for next connection,
        connection, address = sockobj.accept()   # pass to process for service
        print('Server connected by', address)
        handleclient = Process(name='handleclient', target=send_climate_data, args=(connection,))
        # handleclient = Process(name='handleclient', target=user.init) 
        handleclient.start()
