import os
from utilities import *
from datetime import datetime
import csv
# import SimObject

wind_direction = sim_enum('wind_direction', 'E', 'W', 'S', 'N')

class Climate(object):    
    def __init__(self, file_path):
        self.object_name = 'climate'
        self.module_name = 'climate'
        # check file extension(csv)
        # file = raw_input("please enter a file name : ")
        # file_name, file_extension = os.path.splitext(file)
        if file_path.endswith('.csv'):
            if os.path.isfile(file_path):
                pass
            else:
                print("File {0} not found".format(file_path))
        else:
            print("please input a file name with extension : .csv")

        self.pressure = 101.325    # kpa
        self.sea_press = 101.325   # sea level pressure            
        self.temp = 30             # temperature
        self.ws = 18               # wind speed m/s
        self.w_d = wind_direction.E               # wind direction
        self.rh = 50               # percentage
        
        self.d_time = []
        self.d_pressure = []
        self.d_temp = []
        self.d_sea_press = []
        self.d_ws = []
        self.d_w_direction = []
        self.d_r_huminity = []

        csv_reader_obj = CSVReader(file_path)
        csv_reader_obj.record_process(self)
        gl_obj.append(self)

    def show_info(self):
        for ele in self.d_time:
            print(ele)
        
class CSVReader(object):
    def __init__(self, file_path):
        self.data_city = ''
        self.lat_degress = 0
        self.lat_minutes = 0
        self.long_degrees = 0
        self.long_minutes = 0
        self.file_path = file_path
        
    def record_process(self, obj):
        line_number = 1
        with open(self.file_path, 'rb') as climate_file:
            climate_data = csv.reader(climate_file)
            for row in climate_data:
                if line_number == 1:
                    col_0_list = row[0].split('\x9a', 1)
                    # print(col_0_list)
                    self.download_time = datetime.strptime(col_0_list[1], '%Y/%m/%d %H:%M:%S')
                if line_number == 3:
                    self.data_city = row[1]
                if line_number > 6:
                    print(row)
                    obj.d_time.append(datetime.strptime(row[0], '%Y/%m/%d %H:%M:%S'))
                    obj.d_pressure.append(float(row[1].replace(',', '')) / 10)
                    obj.d_temp.append(float(row[2]))
                    obj.d_sea_press.append(float(row[3].replace(',', '')))
                    obj.d_ws.append(float(row[4]))
                    obj.d_w_direction.append(row[5])
                    obj.d_r_huminity.append(float(row[6]))
                line_number += 1
                                        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = "localhost"
        serverPort = "50000"

    gl_obj = []
    temp = Climate('kanazawa.csv')
    temp.show_info()        
    print(gl_obj[0].d_temp)
