from __future__ import division
import sys
import time
from socket import *
import xml.etree.ElementTree as ET
from multiprocessing import Process, Manager, Queue
from datetime import timedelta
# from testRatio import *
# from unit_conversion import *
import unit_conversion
from math import exp
# from ClimateReader import *
from datetime import datetime
import Tkinter
import itertools
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import threading

from SolarAngle import *

# def ac_output(V_In, VA_In):
#     C1 = p_dco*(1+c_1*(V_In-v_dco));
#     C2 = p_so*(1+c_2*(V_In-v_dco));
#     C3 = c_o*(1+c_3*(V_In-v_dco));
#     VA_Out = ((p_max/(C1-C2))-C3*(C1-C2))*(VA_In-C2)+C3*(VA_In-C2)*(VA_In-C2)
#     return VA_Out

def seq(start, end, step):
    """
    Purpose : support for float step in a range-like function
    """
    assert(step != 0)
    sample_count = abs(end - start) / step
    return itertools.islice(itertools.count(start, step), sample_count)

def recvall(connection):
    recv_data = connection.recv(1024)             # till eof when socket closed

    for i in range(len(recv_data)):
        if recv_data[i] == ' ':
            break
    
    recv_len = recv_data[:i]
    data = b'' + recv_data[i+1:]
    amount_received = len(data)
    amount_expected = eval(recv_len)
    
    while amount_received < amount_expected:
        more = connection.recv(1024)
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (amount_expected, amount_received))
        data += more
        amount_received += len(more)
    return data

def recv_climate_data(sockobj,q):
    # global first, sim_timestamp, modeled_power
    global first
    while True:
        print("loop")
        # q.put(recvall(sockobj))
        recv_data = recvall(sockobj)
        # print(recv_data.decode())
        t_data ='<root>' + recv_data.decode() + '</root>'
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
        if first == True:
            first = False
            # mutex.acquire()
            for i in reversed(range(100)):
                print("begining 3")
                sim_timestamp.append(t - timedelta(minutes=i*5))
                modeled_power.append(tmp_modeled_power)
                # measured_pow.append(real_data['measured_pow'])
                measured_pow.append(0)
                # mutex.release()
            # print("initialized modeled power", modeled_power)
            # print("initialized sim timestamp", sim_timestamp)
        else:
            # mutex.acquire()
            modeled_power.append(tmp_modeled_power)
            measured_pow.append(real_data['measured_pow'])
            print("appended timestamp : ", tmp_sim_timestamp)
            sim_timestamp.append(datetime.strptime(tmp_sim_timestamp, '%Y/%m/%d %H:%M:%S'))
            # mutex.release()
            # print("out 4")            

# def simulation(ax, fig, line, canvas, mutex, sim_timestamp, modeled_power):
def simulation(ax, fig, line, line2, canvas):
    # global sim_timestamp, modeled_power
    ax.grid(True)
    ax.set_title('realtime simulation for wind power')
    ax.set_ylabel('wind power(wh)')

    # mutex.acquire()
    # print("[-100]", (sim_timestamp[-100:], modeled_power[-100:]))
    line[0].set_data(sim_timestamp[-100:], modeled_power[-100:])
    line2[0].set_data(sim_timestamp[-100:], measured_pow[-100:])
    len_value = len(sim_timestamp)

    m_left_index = len_value - 100
    m_right_index = len_value - 1

    # print("left ", m_left_index, m_right_index, len(sim_timestamp), len(modeled_power))
    # print("left value", sim_timestamp[m_left_index], sim_timestamp[m_right_index])
    ax.axis([sim_timestamp[m_left_index], sim_timestamp[m_right_index], 0, 3000])
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    
    m_left_date = sim_timestamp[m_left_index].date()
    m_right_date = sim_timestamp[m_right_index].date()
    # mutex.release()
    # print("out 5")
    
    list_x_label = []
    if m_left_date == m_right_date:
        ax.set_xlabel(m_left_date.strftime("%Y-%m-%d"))
    else:
        diff_days = m_right_date - m_left_date
        int_diff_days = diff_days.days + 1
        for i in range(int_diff_days):
            date_str = (m_left_date + timedelta(days=i)).strftime("%Y-%m-%d")
            list_x_label.append(date_str)
        ax.set_xlabel("   ".join(list_x_label))

    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.subplots_adjust(bottom=0.2)
    canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
    # print("sim_timestamp, modeled_power", list(sim_timestamp))
    canvas.show()
    # print(sim_timestamp[-10:])
    root.after(500, simulation,ax, fig, line, line2, canvas)
            
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
        end_time = timestamp + timedelta(minutes=5)
        doy = md2doy(timestamp.year, timestamp.month, timestamp.day)
        start_time = timestamp.hour + timestamp.minute / 60
        end_time = start_time + 1/12
        glb_radiation  = obj_solar_angle.cal_incident_radiation(power, start_time, end_time, 0.2, 30, doy)
        
        # insolwmsq = glb_radiation * 0.95
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
        P_Out = insolwmsq * self.derating_factor * 12.8 * efficiency * tempcorr
        
        VA_Out = P_Out
        # print("VA_Out : ", VA_Out)
        
        Voc = self.Voc_max * (1 + self.Voc_temp_coeff * (Tmodule - 77) / 100)
        V_Out = self.V_max * (Voc/self.Voc_max)
        # print("V_Out", V_Out)
        # I_Out = (VA_Out / V_Out)
        VA_Outs.append(round(VA_Out,2))

        p_dco = 2694
        v_dco = 250
        # v_dco = 302
        # p_so = 20.7
        p_so = 90
    
        c_o = -1.545e-5
        c_1 = 6.525e-5;
        c_2 = 2.836e-3;
        c_3 = -3.058e-4;

        p_max = 2500

        C1 = p_dco*(1+c_1*(V_Out-v_dco));
        C2 = p_so*(1+c_2*(V_Out-v_dco));
        C3 = c_o*(1+c_3*(V_Out-v_dco));
        ac = ((p_max/(C1-C2))-C3*(C1-C2))*(P_Out-C2)+C3*(P_Out-C2)*(P_Out-C2)

        if P_Out == 0:
            ac = 0
        # print(timestamp, "glb_raidation", glb_radiation , "ac", ac)
        print(timestamp, "power", power , "ac", ac)    
        return ac
        
    def generated_power(self, temp, wind, power):
        Tambients = temp
        winds = wind
        
        VA_Outs = []
        for i in range(len(Tambients)):
            Tambient = Tambients[i]
            insolwmsq = power[i] * 0.95
            windspeed = winds[i]                       # m/s

            a = self.module_acoeff
            b = self.module_bcoeff
            print("a", a, "b", b)
            # Calculate the "back" temperature of the array
            Tback = (insolwmsq * exp(a + b * windspeed)) + Tambient
            Tcell = Tback + insolwmsq/1000.0*self.module_dTcoeff;
            # Conversion from Celsius to Fahrenheit
            Tmodule = unit_conversion.c2f(Tback)   # from C to F
            Ftempcorr = 1.0 + self.module_Tcoeff * (Tcell - 25.0)/100
            efficiency = 0.2

            print("derating_factor : ", self.derating_factor)
            P_Out = insolwmsq * self.derating_factor * 12.8 * efficiency * Ftempcorr
        
            VA_Out = P_Out
            print("VA_Out : ", VA_Out)
            
            Voc = self.Voc_max * (1 + self.Voc_temp_coeff * (Tmodule - 77) / 100)
            V_Out = self.V_max * (Voc/self.Voc_max)
            print("V_Out", V_Out)
            I_Out = (VA_Out / V_Out)
            VA_Outs.append(round(VA_Out,2))
            print(power[i], VA_Out)
            
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
    # mutex.release()
    print("out 1")
    first = True
    
    sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
    print("serverHost : ",serverHost)
    print("port : ", serverPort)
    sockobj.connect((serverHost, eval(serverPort)))   # connect to server machine + port
    
    recv_cli_data = Process(name='start connection to receive data from server', target=recv_climate_data, args=(sockobj,q))
    recv_cli_data.start()

    root = Tkinter.Tk()
    fig, ax = plt.subplots()

    time.sleep(2)
    # print("len(modeled_power), len(sim_timestamp)", len(modeled_power), len(sim_timestamp), modeled_power, sim_timestamp)
    print("in 2")
    # with mutex :
        # mutex.acquire()
    print("begining 2")
    line = ax.plot(sim_timestamp, modeled_power)
    line2 = ax.plot(sim_timestamp, measured_pow)
        # mutex.release()
    print("out 2")
    canvas = FigureCanvasTkAgg(fig, master=root)

    root.after(500,simulation, ax, fig, line, line2, canvas)
    # root.after(1000,simulation, ax, fig, line, canvas)

    root.mainloop()
    print("not reach")