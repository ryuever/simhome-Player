from __future__ import division
import sys
from time import sleep
from socket import *
import xml.etree.ElementTree as ET
from multiprocessing import Process, Manager, Queue
import datetime
from datetime import timedelta, datetime, time
# from testRatio import *
# from unit_conversion import *
import unit_conversion
from math import exp
# from ClimateReader import *

import Tkinter
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange, MinuteLocator

import threading
from SolarAngle import *
from wind_4k import *
import struct
from utilities import *
import os

def recvall(connection, meglen):
    data = ''
    while len(data) < meglen:
        packet = connection.recv(meglen - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_climate_data(sockobj,q):
    # global first, sim_timestamp, modeled_power
    global first, temp_0520, ws_0520, ratio_0520
    while True:
        print("loop")
        # q.put(recvall(sockobj))
        raw_msglen = recvall(sockobj, 4)
        print("raw_msglen", raw_msglen)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        recv_data = recvall(sockobj, msglen)
        t_data ='<root>' + recv_data.decode() + '</root>'
        print("t_data ", t_data)
        root = ET.fromstring(t_data)
        print(recv_data)
        real_data = {}
        for item in root:                        
            real_data = dict(
                timestamp = item.find('timestamp').text,
                temp = float(item.find("temperature").text),
                radiation = float(item.find("radiation").text),
                measured_pow = float(item.find("measured_pow").text),
                ws = float(item.find('windspeed').text))
            
            # print(real_data)

        tmp_sim_timestamp = real_data['timestamp']
        t = datetime.strptime(tmp_sim_timestamp, '%Y/%m/%d %H:%M:%S')
        tmp_modeled_power = obj_sim.generated_power_point(real_data['temp'], real_data['ws'], real_data['radiation'], t)
        # reg_rad = obj_sim.reg(real_data["temp"], real_data["ws"], tmp_modeled_power)
        tmp_modeled_wind = cal_available_power(4.4, real_data['ws'])

        reg_rad = obj_sim.reg(real_data["temp"], real_data["ws"], real_data["measured_pow"])
        tmp_modeled_power2 = obj_sim.generated_power_point(real_data['temp'], real_data['ws'], reg_rad, t)
                
        if t > datetime.strptime("2015/05/22 06:00:00", '%Y/%m/%d %H:%M:%S') and t < datetime.strptime("2015/05/20 14:00:00", '%Y/%m/%d %H:%M:%S'):
            temp_0520.append(real_data["temp"])
            ws_0520.append(real_data["ws"])
            ratio_0520.append(tmp_modeled_power / real_data["measured_pow"])
    
        # filename = str(t.year) + str(t.month) + str(t.day) + ".csv"

        
        if time(16,0,0) <= t.time() or t.time() <= time(8,0,0):
            tmp_total_power = tmp_modeled_power2 + tmp_modeled_wind            
        else:
            tmp_total_power = tmp_modeled_power + tmp_modeled_wind
        
        print("t.time", t.time())
        # if time(6,0,0) <= t.time() and t.time() <= time(20,0,0):            
        #     # if os.path.isfile("filename"):
        #     with open(filename, 'a') as the_file:
        #         # the_file.write("{0}, {1}, {2}, {3}, {4}\n".format(tmp_sim_timestamp, tmp_modeled_power, real_data["measured_pow"], real_data["radiation"], reg_rad))
        #         the_file.write("{0}, {1}, {2}, {3}, {4}\n".format(tmp_sim_timestamp, round(tmp_modeled_power2, 2), real_data["measured_pow"], tmp_modeled_wind, tmp_total_power))

        
        # with open(filename, 'a') as the_file:
        #     # the_file.write("{0}, {1}, {2}, {3}, {4}\n".format(tmp_sim_timestamp, tmp_modeled_power, real_data["measured_pow"], real_data["radiation"], reg_rad))
        #     the_file.write("{0}, {1}, {2}, {3}, {4}, {5}\n".format(tmp_sim_timestamp, round(tmp_modeled_power2, 2), real_data["measured_pow"], round(real_data['ws'],2), round(tmp_modeled_wind,2), round(tmp_total_power, 2)))
            
        # print(list(temp_0520), list(ws_0520), list(ratio_0520))
        if first == True:
            first = False
            # mutex.acquire()
            for i in reversed(range(288)):
                # print("begining 3")
                sim_timestamp.append(t - timedelta(minutes=i*5))
                modeled_power.append(tmp_modeled_power)
                # measured_pow.append(real_data['measured_pow'])
                measured_pow.append(0)
                measured_radiation.append(0)
                measured_ws.append(0)
                measured_temp.append(0)
                modeled_wind.append(0)
                total_power.append(0)
                # mutex.release()
            # print("initialized modeled power", modeled_power)
            # print("initialized sim timestamp", sim_timestamp)
        else:
            mutex.acquire()

            modeled_wind.append(tmp_modeled_wind)

            measured_pow.append(real_data['measured_pow'])

            if time(16,0,0) <= t.time() or t.time() <= time(8,0,0):
                measured_radiation.append(reg_rad)
                modeled_power.append(tmp_modeled_power2)
            else:
                modeled_power.append(tmp_modeled_power)
                measured_radiation.append(real_data['radiation'])
            total_power.append(tmp_total_power)
            measured_ws.append(real_data['ws'])
            measured_temp.append(real_data['temp'])

            print("appended timestamp : ", tmp_sim_timestamp)
            sim_timestamp.append(datetime.strptime(tmp_sim_timestamp, '%Y/%m/%d %H:%M:%S'))
            mutex.release()
            # print("out 4")            

# def simulation(ax, fig, line, canvas, mutex, sim_timestamp, modeled_power):
def simulation(ax, fig, line, line2, line3, line4, line5, line6, line7, canvas):
    # global sim_timestamp, modeled_power
    ax[0, 0].grid(True)
    ax[0, 0].set_title('realtime simulation for generated power')
    ax[0, 0].set_ylabel('generated power(W)')

    ax[1, 0].grid(True)
    ax[1, 0].set_title('realtime simulation for measured wind power')
    ax[1, 0].set_ylabel('modeled wind power(W)')

    ax[2, 0].grid(True)
    ax[2, 0].set_title('realtime simulation for modeled total power')
    ax[2, 0].set_ylabel('modeled total power(W)')
        
    ax[0, 1].grid(True)
    ax[0, 1].set_title('realtime simulation for wind speed')
    ax[0, 1].set_ylabel('wind speed(m/s)')

    ax[1, 1].grid(True)
    ax[1, 1].set_title('realtime simulation for measured temperature')
    ax[1, 1].set_ylabel('measured temperature($^\circ$C)')

    ax[2, 1].grid(True)
    ax[2, 1].set_title('realtime simulation for measured radiation')
    ax[2, 1].set_ylabel('measured radiation($kW/m^2$)')

    mutex.acquire()
    # print("[-288]", (sim_timestamp[-288:], modeled_power[-288:]))
    line[0].set_data(sim_timestamp[-288:], modeled_power[-288:])
    line2[0].set_data(sim_timestamp[-288:], measured_pow[-288:])
    line3[0].set_data(sim_timestamp[-288:], measured_radiation[-288:])

    line4[0].set_data(sim_timestamp[-288:], measured_ws[-288:])
    line5[0].set_data(sim_timestamp[-288:], measured_temp[-288:])
    line6[0].set_data(sim_timestamp[-288:], modeled_wind[-288:])
    line7[0].set_data(sim_timestamp[-288:], total_power[-288:])

    len_value = len(sim_timestamp)

    m_left_index = len_value - 288
    m_right_index = len_value - 1

    # print("left ", m_left_index, m_right_index, len(sim_timestamp), len(modeled_power))
    # print("left value", sim_timestamp[m_left_index], sim_timestamp[m_right_index])
    ax[0, 0].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 3000])
    ax[0, 0].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_00_loc = MinuteLocator(interval=5)
    ax[0, 0].xaxis.set_minor_locator(ax_00_loc)
    # ax[0, 0].xaxis.grid(True, which='minor')

    ax[1, 0].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 4000])
    ax[1, 0].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_10_loc = MinuteLocator(interval=5)
    ax[1, 0].xaxis.set_minor_locator(ax_10_loc)
    # ax[1, 0].xaxis.grid(True, which='minor')    

    ax[2, 0].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 6000])
    ax[2, 0].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_20_loc = MinuteLocator(interval=5)
    ax[2, 0].xaxis.set_minor_locator(ax_20_loc)
    # ax[2, 0].xaxis.grid(True, which='minor')    

    ax[0, 1].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 30])
    ax[0, 1].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_01_loc = MinuteLocator(interval=5)
    ax[0, 1].xaxis.set_minor_locator(ax_01_loc)
    # ax[0, 1].xaxis.grid(True, which='minor')    

    ax[1, 1].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 50])
    ax[1, 1].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_11_loc = MinuteLocator(interval=5)
    ax[1, 1].xaxis.set_minor_locator(ax_11_loc)
    # ax[1, 1].xaxis.grid(True, which='minor')

    ax[2, 1].axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 3000])
    ax[2, 1].xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax_21_loc = MinuteLocator(interval=5)
    ax[2, 1].xaxis.set_minor_locator(ax_21_loc)
    # ax[2, 1].xaxis.grid(True, which='minor')    

    m_left_date = sim_timestamp[m_left_index].date()
    m_right_date = sim_timestamp[m_right_index].date()
    # mutex.release()
    # print("out 5")
    
    list_x_label = []
    if m_left_date == m_right_date:
        ax[0,0].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        ax[1,0].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        ax[2,0].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        ax[0,1].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        ax[1,1].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
        ax[2,1].set_xlabel(m_left_date.strftime("%Y-%m-%d"))
    else:
        diff_days = m_right_date - m_left_date
        int_diff_days = diff_days.days + 1
        for i in range(int_diff_days):
            date_str = (m_left_date + timedelta(days=i)).strftime("%Y-%m-%d")
            list_x_label.append(date_str)
        ax[0, 0].set_xlabel("   ".join(list_x_label))
        ax[1, 0].set_xlabel("   ".join(list_x_label))
        ax[2, 0].set_xlabel("   ".join(list_x_label))
        ax[0, 1].set_xlabel("   ".join(list_x_label))
        ax[1, 1].set_xlabel("   ".join(list_x_label))
        ax[2, 1].set_xlabel("   ".join(list_x_label))
        
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.subplots_adjust(bottom=0.2)
    canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
    # print("sim_timestamp, modeled_power", list(sim_timestamp), len(modeled_power), len(measured_pow), len(measured_temp), len(measured_ws), len(sim_timestamp))
    canvas.show()    
    # canvas2.show()
    mutex.release()
    
    # print(sim_timestamp[-10:])
    root.after(300, simulation,ax, fig, line, line2,line3, line4, line5, line6, line7, canvas)
            
class SolarPVSim(object):
    def __init__(self, V_max = 43.4, Voc_max = 53, Voc_temp_coeff = -0.147, module_Tcoeff = -0.336, 
                 module_acoeff = -2.81, module_bcoeff = -0.0455, module_dTcoeff = 0.0,
                 soiling_factor = 0, derating_factor = 0,efficiency = 0, Pmax_temp_coeff = 0,
                 size = 1.5, panel_type_v = "single_crystal_silicon"):
        """
        The following items should be provided by manufacture, or used the default value of
        GEPVp-200-M
            V_max          : max power voltage - Volts
            Voc_max        : max open circuit voltage(voc) - Volts        
            module_Tcoeff  : temperature coefficient - itemed as temperature coefficient pMax.
            Voc_temp_coeff : open circuit temperature coefficient
        
        The emperical coefficiency :
            module_acoeff   : Empirically-determined coefficient establishing the upper limit
                              for module temperature at low wind speeds and high solar irradiance
            module_bcoeff   : Empirically-determined coefficient establishing the rate at which
                              module temperature drops as wind speed increases
            module_dTcoeff  : Temperature difference between the cell and the module back
                              surface at an irradiance level of 1000 W/m2.
            soiling_factor  : soiling of array factor - reprensenting dirt on array
            derating_factor : manufacturing variations 5% reduction of energy transferring
            efficiency      : depending on solar panel type

        size : size of solar panel (m^2)
        """
        self.V_max = V_max
        self.Voc_max = Voc_max
        self.Voc_temp_coeff = Voc_temp_coeff
        self.module_Tcoeff = module_Tcoeff
        
        self.module_acoeff = module_acoeff
        self.module_bcoeff = module_bcoeff        
        self.module_dTcoeff = module_dTcoeff
        
        if soiling_factor <= 0 or soiling_factor > 1.0:
            self.soiling_factor = 0.95
            print("Invalid soiling factor specified, defaulting to 95%")
        else:
            self.soiling_factor = soiling_factor

        if derating_factor <= 0 or derating_factor > 1.0:
            self.derating_factor = 0.95
            print("Invalid derating factor specified, defaulting to 95%")
        else:
            self.derating_factor = derating_factor
            
        print("derating factor : ", self.derating_factor)
        
        if panel_type_v == "single_crystal_silicon":
            self.efficiency = 0.2 if efficiency == 0 else efficiency
        elif panel_type_v == "multi_crystal_silicon":
            self.efficiency = 0.15 if efficiency == 0 else efficiency
        elif panel_type_v == "amorphous_silicon":
            self.efficiency = 0.07 if efficiency == 0 else efficiency
        elif panel_type_v == "thin_film_ga_as":
            self.efficiency = 0.3 if efficiency == 0 else efficiency
        elif panel_type_v == "concentrator":
            self.efficiency = 0.15 if efficiency == 0 else efficiency
        else:
            self.efficiency = 0.1 if efficiency == 0 else efficiency

        self.size = size

        # self.init_climate()
        # module type : Glass/cell/polymer sheet; Mount : Insulated back

    def generated_power_point(self, temp, wind, power, timestamp):

        VA_Outs = []
        Tambient = temp
        # insolwmsq = power * 0.95

        doy = md2doy(timestamp.year, timestamp.month, timestamp.day)
        
        start_time = timestamp.hour + timestamp.minute / 60
        end_time_date = timestamp + timedelta(minutes=5)
        # end_time = start_time + 1/12
        end_time = end_time_date.hour + end_time_date.minute / 60

        from math import degrees
        # insolwmsq = power * obj_solar_angle.cos_incidence(start_time, doy, 30) * 0.95
        # if timestamp.hour > 13:
        #     # power = obj_solar_angle.cal_incident_radiation(power, start_time, end_time, 0.2, 30, doy)
        #     # insolwmsq = power * obj_solar_angle.elevation_sin(start_time, doy) * 0.95
        #     # insolwmsq = power * obj_solar_angle.zenith_cos(start_time, doy) * 0.95
        #     tm = cos(2 * pi * (timestamp.hour + timestamp.minute / 60 - 12) / 25)
        #     print("------------------tm----------", tm, timestamp.hour, timestamp.minute)
        #     insolwmsq = power * tm * 0.95
        #     # insolwmsq = power * obj_solar_angle.cos_incidence(start_time, doy, 30) * obj_solar_angle.elevation_sin(start_time, doy)  * 0.95 
        # else:
        #     # insolwmsq = glb_radiation * 0.95
        #     insolwmsq = 0.95 * power

                #----------------------------------------------------#
        # if timestamp.hour == 6:            
        #     power = power - 190

        insolwmsq = 0.95 * power 
        windspeed = wind                       # m/s        
        
        a = self.module_acoeff
        b = self.module_bcoeff
        # print("a", a, "b", b)
        # Calculate the "back" temperature of the array
        Tback = (insolwmsq * exp(a + b * windspeed)) + Tambient
        Tcell = Tback + insolwmsq/1000.0*self.module_dTcoeff;
        # Conversion from Celsius to Fahrenheit
        Tmodule = unit_conversion.c2f(Tback)   # from C to F
        tempcorr = 1.0 + self.module_Tcoeff * (Tcell - 25.0)/100
        efficiency = 0.2
        
        # print("derating_factor : ", self.derating_factor)

        if Tambient < 19.2:
            P_Out = insolwmsq * self.derating_factor * 12.8 * efficiency * tempcorr * 1.05
        elif Tambient < 22.8:
            P_Out = insolwmsq * self.derating_factor * 12.8 * efficiency * tempcorr * 1
        else:
            P_Out = insolwmsq * self.derating_factor * 12.8 * efficiency * tempcorr * 0.97
            

        #----------------------------------------------------#
        # if timestamp.hour < 7 or timestamp.hour > 17:
        #     P_Out = 0
        #----------------------------------------------------#
        # if timestamp.hour == 6:
        #     print("hlfasdjfkafajkfjklafjakf")
        #     P_Out = P_Out - 430
        
        VA_Out = P_Out
        # print("VA_Out : ", VA_Out)
        
        Voc = self.Voc_max * (1 + self.Voc_temp_coeff * (Tmodule - 77) / 100)
        V_Out = self.V_max * (Voc/self.Voc_max)
        # print("V_Out", V_Out)
        # I_Out = (VA_Out / V_Out)
        VA_Outs.append(round(VA_Out,2))

        p_dco = 2700
        v_dco = 380
        # v_dco = 302
        # p_so = 20.7
        p_so = 20.7
    
        c_o = 0
        c_1 = 0
        c_2 = 0
        c_3 = 0

        p_max = 2500

        C1 = p_dco*(1+c_1*(V_Out-v_dco));
        C2 = p_so*(1+c_2*(V_Out-v_dco));
        C3 = c_o*(1+c_3*(V_Out-v_dco));
        ac = ((p_max/(C1-C2))-C3*(C1-C2))*(P_Out-C2)+C3*(P_Out-C2)*(P_Out-C2)

        # p_dco = 2694
        # v_dco = 250
        # # v_dco = 302
        # # p_so = 20.7
        # p_so = 90
    
        # c_o = -1.545e-5
        # c_1 = 6.525e-5;
        # c_2 = 2.836e-3;
        # c_3 = -3.058e-4;

        # p_max = 2500

        # C1 = p_dco*(1+c_1*(V_Out-v_dco));
        # C2 = p_so*(1+c_2*(V_Out-v_dco));
        # C3 = c_o*(1+c_3*(V_Out-v_dco));
        # ac = ((p_max/(C1-C2))-C3*(C1-C2))*(P_Out-C2)+C3*(P_Out-C2)*(P_Out-C2)
        
        if P_Out == 0:
            ac = 0
        # print(timestamp, "glb_raidation", glb_radiation , "ac", ac)
        print(timestamp, "power", power , "ac", ac)    
        # return ac
        return P_Out
    def reg(self, temp, wind, power):
        Tambient = temp
        # insolwmsq = power[i] * 0.95
        windspeed = wind                    # m/s
        efficiency = 0.2
        a = self.module_acoeff
        b = self.module_bcoeff
        
        z = power * 100/ (self.derating_factor * 12.56 * efficiency)
        m = exp(a + b * windspeed)
        x = self.module_Tcoeff * (m + self.module_dTcoeff / 1000)
        y = 100 + self.module_Tcoeff * (Tambient - 25) / 1000
        # x = (m*self.module_Tcoeff / 1000 + self.module_dTcoeff / 1000000)
        # y = (1 + (self.module_Tcoeff * Tambient)/ 1000)

        value = (-y + sqrt(pow(y, 2)  + 4 * x * z)) / (2 * x)
        # print("power", power[i], "x", x , "y", y, "z", z, value)
        # values.append(round(value,2))
        return value
    
    def regression_from_power(self, temp, wind, power):
        """
        # from measured power data 
        """
        Tambients = []
        winds = []
        efficiency = 0.2
        for i in range(13):
            for j in range(1, 13):
                Tambients.append(temp[i] + (temp[i+1] - temp[i]) / 12 * j)
                winds.append(wind[i] + (wind[i+1] - wind[i]) / 12 * j)                
        print("len", len(Tambients))
        a = self.module_acoeff
        b = self.module_bcoeff

        values = []
        for i in range(len(power)):
            Tambient = Tambients[i]
            # insolwmsq = power[i] * 0.95
            windspeed = winds[i]                       # m/s

            z = power[i] * 100/ (self.derating_factor * 12.56 * efficiency)
            m = exp(a + b * windspeed)
            x = self.module_Tcoeff * (m + self.module_dTcoeff / 1000)
            y = 100 + self.module_Tcoeff * (Tambient - 25) / 1000
            # x = (m*self.module_Tcoeff / 1000 + self.module_dTcoeff / 1000000)
            # y = (1 + (self.module_Tcoeff * Tambient)/ 1000)

            value = (-y + sqrt(pow(y, 2)  + 4 * x * z)) / (2 * x)
            print("power", power[i], "x", x , "y", y, "z", z, value)
            values.append(round(value,2))        
        return values            
if __name__ == "__main__":
    if len(sys.argv) == 3:
        serverHost = sys.argv[1]
        serverPort = sys.argv[2]
    else:
        serverHost = 'localhost'
        serverPort = '50000'

    obj_sim = SolarPVSim()
    obj_solar_angle = SolarAngle(36.03, 140.08, 9)    
    manager = Manager()
    
    # sim_timestamp = manager.list()
    # modeled_power = manager.list()
    # mutex = thread.allocate_lock()
    mutex = threading.Lock()
    q = Queue()
    print("in 1")
    # mutex.acquire()
    # sim_timestamp = []    
    # modeled_power = []

    sim_timestamp = manager.list()
    modeled_power = manager.list()
    measured_pow = manager.list()

    measured_radiation = manager.list()
    measured_ws = manager.list()
    measured_temp = manager.list()
    modeled_wind = manager.list()
    total_power = manager.list()
    
    temp_0520 = manager.list()
    ws_0520 = manager.list()
    ratio_0520 = manager.list()

    # mutex.release()
    
    print("out 1")
    first = True
    
    sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
    print("serverHost : ",serverHost)
    print("port : ", serverPort)
    sockobj.connect((serverHost, eval(serverPort)))   # connect to server machine + port
    
    # recv_cli_data = Process(name='start connection to receive data from server', target=recv_climate_data, args=(sockobj,q))
    recv_cli_data = threading.Thread(name='start connection to receive data from server', target=recv_climate_data, args=(sockobj,q))
    recv_cli_data.start()

    root = Tkinter.Tk()
    fig, ax = plt.subplots(3, 2)

    # fig2, ax2 = plt.subplots(1)
    
    sleep(1)
    # print("len(modeled_power), len(sim_timestamp)", len(modeled_power), len(sim_timestamp), modeled_power, sim_timestamp)
    # with mutex :
        # mutex.acquire()
    mutex.acquire()
    line = ax[0, 0].plot(sim_timestamp, modeled_power, label="modeled power")
    line2 = ax[0, 0].plot(sim_timestamp, measured_pow, label="measured power")
    line6 = ax[1, 0].plot(sim_timestamp, modeled_wind, label="modeled wind power")
    line7 = ax[2, 0].plot(sim_timestamp, total_power, label="modeled total power")

    line4 = ax[0, 1].plot(sim_timestamp, measured_ws, label="measured wind speed")
    line5 = ax[1, 1].plot(sim_timestamp, measured_temp, label="measured temperature")
    line3 = ax[2, 1].plot(sim_timestamp, measured_radiation, label="measured radiation")

    ax[0, 0].legend()
    ax[0, 1].legend()
    ax[1, 0].legend()
    ax[1, 1].legend()
    ax[2, 0].legend()
    ax[2, 1].legend()
    mutex.release()
        # mutex.release()
    canvas = FigureCanvasTkAgg(fig, master=root)
    # canvas2 = FigureCanvasTkAgg(fig2, master=root)

    root.after(300,simulation, ax, fig, line, line2, line3, line4, line5, line6,line7, canvas)
    # root.after(1000,simulation, ax, fig, line, canvas)

    root.mainloop()
    print("not reach")
