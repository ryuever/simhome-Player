from __future__ import division
from math import pi, sin, asin, cos, acos, tan, radians, degrees, exp
import itertools
import matplotlib.pyplot as plt

def seq(start, end, step):
    """
    Purpose : support for float step in a range-like function
    """
    assert(step != 0)
    sample_count = abs(end - start) / step
    return itertools.islice(itertools.count(start, step), sample_count)

# http://www.greenrhinoenergy.com/solar/radiation/tiltedsurface.php
albedo = {'untilted_field': 0.26,
          'lawn': 0.205,
          'old_snow': 0.58,
          'naked_ground': 0.17,
          'asphalt': 0.15,
          'weather_beaten_concrete': 0.3,
          'fresh_snow': 0.85}

days_thru_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]   # ignore leap year
month_days = [[0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
              [0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335 ]]

def doy2md(year, doy):
    """
    Purpose : calculating the corresponding month, 
              day fromat from year and day number
    """
    if ((year % 4 == 0) and (year % 100 != 0 or year % 400 == 0 )):
        leap = 1
    else:
        leap = 0

    mon = 12
    while(doy <= month_days[leap][mon]):
        mon = mon - 1

    day = doy - month_days[leap][mon]
    print("month : {0}, day : {1}".format(mon, day))
    return [mon, day]

def md2doy(year, month, day):
    if ((year % 4 == 0) and (year % 100 != 0 or year % 400 == 0 )):
        leap = 1
    else:
        leap = 0

    selected_month_days = month_days[leap]
    doy = selected_month_days[month] + day
    return doy
    
def lat2deg(degree, minute, second):
    return degree + minute / 60 + second * (60 * 60)

def lgt2deg(degree, minute, second):
    return degree + minute / 60 + second * (60 * 60)

class SolarAngle(object):
    def __init__(self, lat, lgt, std_meridian, doy = 0, local_time=12, altitude=0, G_sc=1367):
        self.lat_deg = lat         # value in decimal
        self.lgt_deg = lgt         # value in decimal
        self.doy = doy             # day of year, day number
        self.std_meridian = std_meridian   # time zone
        self.local_time = local_time       # local time in hour, 9.5 means 9:30

        self.altitude = altitude
        self.G_sc = G_sc           # solar constant
        
    def eq_time(self, doy):
        """
        Purpose : Compute the equation of time
        Expects : Day of year from Jan 1
        return  : equation time in minutes
        """
        rad = radians(360 *(doy - 81) / 365)
        return 9.87 * sin(rad * 2) - 7.53 * cos(rad) - 1.5 * sin(rad)        

    def sol_time(self, localtime=0, doy = 0):
        """
        Purpose : Compute the solar time
        Explanation : The factor of 4 minutes comes from the fact that the Earth rotates
                      1 degree every 4 minutes.
        Return : local solar time in hours. 9.5 means 9:30
        """
        loc_time = localtime if localtime != 0 else self.localtime
        std_meridian_degree = 15 * self.std_meridian
        solar_time = loc_time + self.eq_time(doy) / 60 + 4 * (self.lgt_deg - std_meridian_degree) / 60
        return solar_time

    def diff_std_sol_time(self, doy):
        std_meridian_degree = 15 * self.std_meridian
        return self.eq_time(doy) / 60 + 4 * (self.lgt_deg - std_meridian_degree) / 60
    
    def local_time(self, sol_time = 0, doy = 0):
        """
        Purpose : Computing the locate time or standard time from solar time
        Return  : Local time in decimal hours
        equation : local_time = solar_time - equation_time - 4*(meridian - longitude)         
        """
        std_meridian_degree = 15 * self.std_meridian
        solar_time = sol_time if sol_time != 0 else self.sol_time
        local_time = solar_time - self.eq_time(doy) / 60 - 4 * (self.lgt_deg - std_meridian_degree) / 60
        return local_time

    def declination_sin(self, doy=0):
        doy = doy if doy != 0 else self.doy
        return sin(radians(23.45)) * sin(radians(360 / 365 * (doy - 81)))

    def declination(self, doy = 0):
        """
        Purpose : Compute the solar declination angle
        Expectes : Days of year from Jan 1
        Retrun : Declination angle in degrees
        """
        doy = doy if doy != 0 else self.doy
        return 23.45 * sin(radians(360 * (284 + doy) / 365))

    def elevation_sin(self, localtime, doy):
        """
        Purpose : sine of elevation angle    
        """
        hour_angle = radians((localtime - 12) * 15)
        decl   = radians(self.declination(doy))
        lat_rad = radians(self.lat_deg)
        return sin(decl) * sin(lat_rad) + cos(decl) * cos(lat_rad) * cos(hour_angle)
    
    def elevation(self, localtime=0, doy = 0):
        """
        Description : Also called altitude. It's the complement of zenith
        Purpose : Compute the elevation angle
        Return  : elevation angle in radians     
        """
        doy = doy if doy != 0 else self.doy
        loc_time = localtime if localtime != 0 else self.localtime        
        return asin(self.elevation_sin(loc_time, doy))

    def zenith_cos(self, localtime=0, doy = 0):
        """
        Purpose : Compute the zenith angle. complement of elevation
        Return  : zenith angle in radians
        """
        doy = doy if doy != 0 else self.doy
        loc_time = localtime

        hour_angle = radians((loc_time - 12) * 15)
        decl = radians(self.declination(doy))
        lat_rad = radians(self.lat_deg)
        return sin(decl) * sin(lat_rad) + cos(decl) * cos(lat_rad) * cos(hour_angle)

    def zenith_cos_daily(self, doy=0):
        ze_cos_daily = []
        for i in seq(0.5, 25, 1):
            value = self.zenith_cos(i, doy)
            # ze_cos_daily.append(float("{0:.2f}".format(value)))
            ze_cos_daily.append(round(value, 2))
        return ze_cos_daily
    
    def zenith(self, localtime=0, doy = 0):
        return acos(self.zenith_cos(localtime, doy))

    def zenith_daily(self, doy):
        ze_daily = []
        for i in (0.5, 24, 1):
            ze_daily.append(acos(self.zenith_cos(i, doy)))
        return ze_daily    
        
    def azimuth(self, localtime, doy):
        """
        selected
        """
        ze = self.zenith(localtime, doy)
        decl_rad = radians(self.declination(doy))
        lat_rad = radians(self.lat_deg)
        hour_angle = radians((localtime-12) * 15)

        if hour_angle > 0:        
            az = abs(acos((cos(ze) * sin(lat_rad) - sin(decl_rad)) / (sin(ze) * cos(lat_rad))))
        else:
            az = -abs(acos((cos(ze) * sin(lat_rad) - sin(decl_rad)) / (sin(ze) * cos(lat_rad))))
            
        return az

    def azimuth_v4(self, localtime, doy):
        """
        Purpose : Compute the azimuth angle
        Return  : azimuth angle in radians
        """
        hour_angle = radians((localtime - 12) * 15)
        decl   = radians(self.declination(doy))
        alpha = cos(self.elevation(localtime, doy))
        return asin(cos(decl) * sin(hour_angle) / alpha)

    def azimuth_v2(self, localtime, doy):
        """
        Purpose : Compute the azimuth angle
        Return  : azimuth angle in radians
        """
        hour_angle = radians((localtime - 12) * 15)
        decl   = radians(self.declination(doy))
        lat_rad = radians(self.lat_deg)
        alpha = cos(self.elevation(localtime, doy))
        return acos((sin(decl) * cos(lat_rad) - cos(decl) * sin(lat_rad) * cos(hour_angle)) / alpha)

    def azimuth_v3(self, localtime, doy):
        """
        Purpose : Compute the azimuth angle
        Return  : azimuth angle in radians
        """
        hour_angle = radians((localtime - 12) * 15)
        decl   = radians(self.declination(doy))
        lat_rad = radians(self.lat_deg)
        ze = self.zenith(localtime, doy)
        return acos((sin(decl) * cos(lat_rad) - cos(decl) * sin(lat_rad) * cos(hour_angle)) / sin(ze))

    def cos_incidence(self, localtime, doy, slope_deg):
        """
        selected
        """
        a_coeff = radians(self.lat_deg - slope_deg)
        decl_rad = radians(self.declination(doy))
        hour_angle = radians((localtime-12) * 15)        
        # print("a_coeff", degrees(a_coeff), "decl_rad", degrees(decl_rad), "hour_angle", degrees(hour_angle))
        return cos(a_coeff) * cos(decl_rad) * cos(hour_angle) + sin(a_coeff) * sin(decl_rad)

    def incidence_cos_daily(self, doy, slope_deg):
        inc_cos_daily = []
        for i in seq(0.5, 25, 1):
            a_coeff = radians(self.lat_deg - slope_deg)
            decl_rad = radians(self.declination(doy))
            hour_angle = radians((i - 12) * 15)
            value = cos(a_coeff) * cos(decl_rad) * cos(hour_angle) + sin(a_coeff) * sin(decl_rad)
            inc_cos_daily.append(round(value,2))
        return inc_cos_daily

    def hr_ang(self, localtime,doy):
        """
        Explanation : The Earth rotate 15 degree per hour
        Purpose : Compute the hour angle
        Return  : Reture a hour angle in degrees
        """
        solar_time = self.sol_time(localtime, doy)
        return 15 * (solar_time - 12)   # morning +, afternoon -

    def sunset_hour_angle(self, doy):
        decl = radians(self.declination(doy))
        print("decl ", decl)
        lat = radians(self.lat_deg)
        return acos(-tan(decl) * tan(lat))    
    
    def hourly_radiation_ratio(self, localtime, doy):
        W = radians(self.hr_ang(localtime, doy))
        Ws = self.sunset_hour_angle(doy)
        Ws_deg = degrees(Ws)
        # customized
        # a = 0.109 + 0.4016 * sin(deg2rad(Ws_deg - 60))
        # b = 0.2160 - 0.1010 * sin(deg2rad(Ws_deg - 40))        
        a = 0.409 + 0.5016 * sin(radians(Ws_deg - 60))
        b = 0.6609 - 0.4767 * sin(radians(Ws_deg - 60))

        print(a, b, "W", W, degrees(W), "Ws", Ws, degrees(Ws))
        r = pi / 24 * (a + b * cos(W)) * ((cos(W) - cos(Ws)) / (sin(Ws) - pi/180 * Ws_deg * cos(Ws)))
        return r

    # def hourly_radiation_ratio_daily(self, doy):
    #     ratio = []
    #     for i in range(6, 19):
    #         value = self.hourly_radiation_ratio(i, doy)
    #         ratio.append(round(value,4))
    #     return ratio
    
    def hourly_radiation_ratio_daily(self, doy):
        ratio = []
        for i in range(6, 19):
            value = self.hourly_radiation_ratio(i, doy)
            ratio.append(round(value,4))
        return ratio

    def five_mins_radiation_ratio_daily(self, doy):
        modeled_ratios = []

        ratio = self.hourly_radiation_ratio(5.917, doy)
        modeled_ratios.append(ratio)
        
        for i in range(6, 19):
            for j in seq(0,1,1/12):
                modeled_ratio = self.hourly_radiation_ratio(i+j, doy)
                if modeled_ratio <= 0:
                    modeled_ratio = 0
                modeled_ratios.append(modeled_ratio)
        # for i in range(0, 13):
        # sum = []
        # for i in range(13):
        #     sum.append(modeled_ratios[(i+1)*12 - 1] - modeled_ratios[])
        
        five_diff = []
        for i in range(1, len(modeled_ratios)):
            five_diff.append(abs(modeled_ratios[i] - modeled_ratios[i-1]))

        five_diff_sum = []
        for i in range(13):
            five_diff_sum.append(0)
        for i in range(13):
            five_diff_sum[i] = (reduce(lambda x, y: (x + y), five_diff[12 *i:(i+1)*12 - 1]))

        five_diff_cor = []
        for i in range(len(five_diff)):
            if five_diff_sum[int(i/12)] != 0:                
                five_diff_cor.append(five_diff[i] / five_diff_sum[int(i/12)])
            else:
                five_diff_cor.append(0)
        return five_diff, modeled_ratios, five_diff_cor
    
    def cal_extraterrestrial_radiation_normal(self, doy):
        """
        Extraterrestrial radiation incident on the plane normal to the radiation on the
        nth day of the year
        """
        G_on = self.G_sc * (1 + 0.033 * cos(360 * doy / 365))
        return G_on

    def cal_extraterrestrial_radiation_normal_daily(self, doy):
        hourly_ratios = self.hourly_radiation_ratio_daily(doy)
        G_on = self.cal_extraterrestrial_radiation_horizontal_total_daily(doy)
        hourly_extra_radiation = []
        for i in range(6, 19):
            hourly_extra_radiation.append(round(G_on * hourly_ratios[i-6] / 10000, 2))
        return hourly_extra_radiation
    
    def cal_extraterrestrial_radiation_horizontal_between_timestamp(self, w1, w2, doy):
        """
        hourly radiation from localtime to (localtime + 1)
        """
        lat_rad = radians(self.lat_deg)
        decl_rad = radians(self.declination(doy))
        w1 = (w1 - 12) * 15
        w2 = (w2 -12) * 15

        w1_r = radians(w1)
        w2_r = radians(w2)
        
        I_coeff = cos(lat_rad) * cos(decl_rad) * (sin(w2_r) - sin(w1_r)) + \
                  pi *(w2 - w1) / 180 * sin(lat_rad) * sin(decl_rad)

        I_o = 12 * 3600 * 1367 / pi * I_coeff        
        return I_o

    def cal_diff_from_beam(self, beam, doy, start_time, end_time):
        diff = 0
        I = self.cal_extraterrestrial_radiation_horizontal_between_timestamp(start_time, end_time,doy)
    
        power = I / ((end_time - start_time) * 3600)
        r = 0
        r_c = 0
        if I < 0:
            diff = 0
        else:
            r = beam / power
            if r <= 0.22:
                r_c = 1.0 - 0.09 * r
            elif 0.22 < r <= 0.80:
                r_c = 0.9511 - 0.1604 * r_c + 4.388 * pow(r, 2) - 16.638 * pow(r, 3) + 12.336 * pow(r, 4)
            elif 0.8 < r < 1:                
                r_c = 0.165
            else:                
                r_c = 0
            diff = beam * r_c

        print("r, r_c ", r, r_c, "beam", beam, "power", power)
        return round(diff, 2)
    def cal_r_b_daily(self,slope_deg, doy):
        t = list(seq(0, 24, 1/12))        
        for i in range(len(t)):
            cos_inc = self.cos_incidence(t[i], doy, slope_deg)
            ze_cos = self.zenith_cos(t[i], doy)
            r_b = cos_inc / ze_cos
            if r_b < 0:
                r_b = 1.2
            print("cos_inc, ze_cos, r_b", round(cos_inc, 2), round(ze_cos, 2), round(r_b, 2), t[i])
    def cal_incident_radiation(self, beam, start_time, end_time, albedo, slope_deg, doy):        
        local_time = start_time
        cos_inc = self.cos_incidence(local_time, doy, slope_deg)        
        ze_cos = self.zenith_cos(local_time, doy)
        
        # power_beam, power_diff, power, radiation = obj_03.cal_diff_beam_v2(doy, rh)
        
        diff = self.cal_diff_from_beam(beam, doy, start_time, end_time)
        if diff > 0:
            R_b_item = round(cos_inc / ze_cos, 2)
            if R_b_item < 1:
                R_b_item = 1.2
            glb_radiation = beam + diff
            print("R_b_item : ", R_b_item, "cos_inc", cos_inc, "ze_cos", ze_cos)
            # I_ti = beam * R_b_item + diff + glb_radiation * albedo * ((1-cos(radians(slope_deg)))/2)
            I_ti = beam + beam * albedo * ((1-cos(radians(slope_deg)))/2)
        else:
            I_ti = 0
        
        return I_ti
        
    def cal_extraterrestrial_radiation_horizontal_five_min_daily(self, doy):
        """
        hourly radiation from localtime to (localtime + 1)
        """
        I_s = []
        for i in range(6, 19):
            for j in seq(0,1,1/12):
                w1 = i + j
                w2 = i + j + 1/12
                value = self.cal_extraterrestrial_radiation_horizontal_between_timestamp(w1, w2, doy)
                I_s.append(round(value / 10000,2)) 
        return I_s
    
    def cal_extraterrestrial_radiation_horizontal_total_daily(self, doy):
        lat_rad = radians(self.lat_deg)
        decl_rad = radians(self.declination(doy))
        ws = self.sunset_hour_angle(doy)
        ws_d = degrees(ws)
        
        H_coeff = cos(lat_rad) * cos(decl_rad) * sin(ws) + \
                  pi * ws_d / 180 * sin(lat_rad) * sin(decl_rad)

        H_o = 24 * 3600 * 1367 / pi * H_coeff        
        return H_o
    
    def cal_atmospheric_transmittance_beam_daily(self, doy):
        """
        The atmospheric transmittance for beam radiation
        """
        at_ratio_beam = []
        cos_ze_daily = self.zenith_cos_daily(doy)
        for i in range(len(cos_ze_daily)):
            a = 0.4237 - 0.00821 * pow((6 - self.altitude), 2)
            b = 0.5055 + 0.00595 * pow((6.5 - 0.27), 2)
            k = 0.2711 + 0.01858 * pow((2.5 - 0.27) ,2)
            # print("a", a, "b", b, "k", k)
            ratio = a + b * exp((-k) / cos_ze_daily[i])
            at_ratio_beam.append(ratio)        
        return at_ratio_beam

    def cal_atmospheric_transmittance_diffuse_daily(self, doy):
        """
        The atmospheric transmittance for beam radiation
        """
        at_ratio_diffuse = []
        at_ratio_beam = self.cal_atmospheric_transmittance_beam_daily(doy)
        for i in range(len(at_ratio_beam)):
            ratio = 0.271 - 0.294 * at_ratio_beam[i]
            at_ratio_diffuse.append(ratio)
        return at_ratio_diffuse
    
    def cal_beam_diffuse_horizontal_daily(self, doy):
        cos_ze_daily = self.zenith_cos_daily(doy)
        at_ratio_beam_daily = self.cal_atmospheric_transmittance_beam_daily(doy)
        at_ratio_diffuse_daily = self.cal_atmospheric_transmittance_diffuse_daily(doy)
        G_on = self.cal_extraterrestrial_radiation_normal(doy)
        G_cb_daily = []
        G_cd_daily = []
        G_c_total_hourly = 0
        G_c_total_daily = []

        G_c_total_radiation_daily = []
        for i in range(6, 18):
            "beam / diffuse radiation for clear day on horizontal surface "
            G_c_total_radiation_hourly = 0
            G_cb = G_on * at_ratio_beam_daily[i] * cos_ze_daily[i]
            G_cd = G_on * at_ratio_diffuse_daily[i] * cos_ze_daily[i]
            G_cb_daily.append(G_cb)
            G_cd_daily.append(G_cd)
            
            G_c_total_hourly = G_cb + G_cd
            G_c_total_daily.append(G_c_total_hourly)

            G_c_total_radiation_hourly = G_c_total_hourly * 3600
            G_c_total_radiation_daily.append(G_c_total_radiation_hourly)

        return G_cb_daily, G_cd_daily

    def cal_diff_beam_v2(self, doy, rh):
        ze_cos_daily = self.zenith_cos_daily(doy)

        if (rh <= 40):
            ratio = 0.69
        elif(40 <rh <= 45):
            ratio = 0.67
        elif(45 < rh <= 55):
            ratio = 0.57
        elif (55 < rh <= 65):
            ratio = 0.47
        elif (65 < rh <= 75):
            ratio = 0.41
        elif (75 < rh <= 80):
            ratio = 0.3
        else:
            ratio = 0.2            

        # if rh < 10:
        #     ratio = 0.85
        # elif rh < 20:
        #     ratio = 0.8            
        # elif rh < 30:
        #     ratio = 0.75        
        # elif rh <= 40:
        #     ratio = 0.69
        # elif(40 <rh <= 45):
        #     ratio = 0.67
        # elif(45 < rh <= 55):
        #     ratio = 0.57
        # elif (55 < rh <= 60):
        #     ratio = 0.47
        # elif 60 < rh <= 65:
        #     ratio = 0.3
        # elif 65 < rh <= 75:
        #     ratio = 0.2
        # elif 75 < rh < 85:
        #     ratio = 0.15            
        # else:
        #     ratio = 0.12
            
        power_v2 = []
        radiation_v2 = []
        G_bh_list = []
        G_dh_list = []
        # print("ze_cos", ze_cos_daily)
        # for i in range(6, 18):
        #     # print(ze_cos_daily[i])
        #     am = 1 / ze_cos_daily[i]
        #     # G_bh = 1367 * pow(ratio, am) * ze_cos_daily[i]
        #     # G_dh = 0.3 * (1 - pow(ratio, am)) * 1367 * ze_cos_daily[i]

        #     G_bh = 1367 * pow(ratio, am)
        #     G_dh = 0.3 * (1 - pow(ratio, am)) * 1367

        #     power_v2.append(G_bh + G_dh)
        #     radiation_v2.append(round((G_bh + G_dh) * 3600 / 10000, 2))
        #     G_bh_list.append(round(G_bh * 3600 / 10000, 2))
        #     G_dh_list.append(round(G_dh * 3600 / 10000, 2))

        power_diff = []
        power_beam = []
        for i in range(6, 18):
            # print(ze_cos_daily[i])
            am = 1 / ze_cos_daily[i]
            # G_bh = 1367 * pow(ratio, am) * ze_cos_daily[i]
            # G_dh = 0.3 * (1 - pow(ratio, am)) * 1367 * ze_cos_daily[i]

            # G_bh = 1367 * pow(ratio, am)
            # G_dh = 0.3 * (1 - pow(ratio, am)) * 1367
                
            if doy in [60, 62, 66, 67, 68, 74, 78]:
                if doy in [60,62, 66, 67, 68, 78]:
                    G_bh = 1367 * pow(ratio, am) * ze_cos_daily[i] / 3
                    G_dh = 0.3 * (1 - pow(ratio, am)) * 1367 * ze_cos_daily[i] / 3
                else :
                    G_bh = 1367 * pow(ratio, am) / 3
                    G_dh = 0.3 * (1 - pow(ratio, am)) * 1367 / 3
            else:
                G_bh = 1367 * pow(ratio, am)
                G_dh = 0.3 * (1 - pow(ratio, am)) * 1367

            if doy in [65]:
                G_bh = 1367 * pow(ratio, am) * ze_cos_daily[i]
                G_dh = 0.3 * (1 - pow(ratio, am)) * 1367 * ze_cos_daily[i]

            power_v2.append(G_bh + G_dh)
            power_diff.append(G_dh)
            power_beam.append(G_bh)
            radiation_v2.append(round((G_bh + G_dh) * 3600 / 10000, 2))
            G_bh_list.append(round(G_bh * 3600 / 10000, 2))
            G_dh_list.append(round(G_dh * 3600 / 10000, 2))

        if doy in [60, 62, 66, 67, 68, 74, 78]:
            print("--------------------------------------------")
            print("doy" , doy , ze_cos_daily[6:18])
            print("--------------------------------------------")
            
        print(doy - 59, ": ",  G_bh_list, G_dh_list)
        return power_beam, power_diff, power_v2, radiation_v2
    
    def radiation_every_five_mins(self, doy, rh):
        five_diff, modeled_ratios, five_diff_cor = self.five_mins_radiation_ratio_daily(doy)
        power_beam, power_diff, power, radiation = self.cal_diff_beam_v2(doy, rh)
        radiation_every_five = []
        power.append(0)

        print("radiation sum ", radiation)


        v = []

        for i in range(13):
            v.append(reduce(lambda x, y: (x + y), five_diff_cor[12 *i:(i+1)*12 - 1]))

            
        print("v : ", v)
        print("power_____________________________________________x", power)
        print("five_diff_cor", five_diff_cor)
        for i in range(len(five_diff_cor)):
            print("i", i)
            # radiation_every_five.append(round(five_diff_cor[i] * radiation[int(i/12)], 2))
            radiation_every_five.append(round(five_diff_cor[i] * power[int(i/12)] * 3600, 2))
        return radiation_every_five

    def radiation_every_five_mins_given_hourly_radiation(self, doy, radiation):
        five_diff, modeled_ratios, five_diff_cor = self.five_mins_radiation_ratio_daily(doy)
        radiation_every_five = []
        for i in range(len(five_diff_cor)):
            print("i", i)
            # radiation_every_five.append(round(five_diff_cor[i] * radiation[int(i/12)], 2))
            print("xxxxxxxxxxxxxxxxxxxx", radiation[int(i/12)], "xxxxxxxxxxxxxxxxxxxxxxxx")
            radiation_every_five.append(round(five_diff_cor[i] * radiation[int(i/12)], 2))
        return radiation_every_five        

    def power_every_five_mins(self, doy, rh):
        radiation_every_five = self.radiation_every_five_mins(doy, rh)

        power_every_five = []
        for i in range(len(radiation_every_five)):            
            power_every_five.append(round(radiation_every_five[i] / 300, 2))
        return power_every_five
    
    def cal_inclined_radiation(self, doy, rh, slope_deg):
        cos_incidence = self.incidence_cos_daily(doy, slope_deg)
        ze_cos_daily = self.zenith_cos_daily(doy)
        R_b = []
        power_beam, power_diff, power, radiation = obj_03.cal_diff_beam_v2(doy, rh)
        I_ti_daily = []
        for i in range(6, 18):
            R_b_item = round(cos_incidence[i] / ze_cos_daily[i], 2)
            R_b.append(R_b_item)
            I_ti = power_beam[i-6] * R_b_item + power_diff[i-6] + power[i-6] * 0.2 * ((1-cos(radians(slope_deg)))/2)
            I_ti_daily.append(I_ti)
        return I_ti_daily
        
if __name__ == "__main__":
    obj_v_az = SolarAngle(43, 100, 9)
    print("obj_v_az azimuth", obj_v_az.azimuth(16, 77),
          degrees(obj_v_az.azimuth(16, 77)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v2(16, 77),
          degrees(obj_v_az.azimuth_v2(16, 77)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v3(16, 77),
          degrees(obj_v_az.azimuth_v3(16, 77)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v4(16, 77),
          degrees(obj_v_az.azimuth_v4(16, 77)))   # verify azimuth p 41    

    print("obj_v_az azimuth", obj_v_az.azimuth(9.5, 44),
          degrees(obj_v_az.azimuth(9.5, 44)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v2(9.5, 44),
          degrees(obj_v_az.azimuth_v2(9.5, 44)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v3(9.5, 44),
          degrees(obj_v_az.azimuth_v3(9.5, 44)))   # verify azimuth p 41
    print("obj_v_az azimuth", obj_v_az.azimuth_v4(9.5, 44),
          degrees(obj_v_az.azimuth_v4(9.5, 44)))   # verify azimuth p 41
    
    print("obj_v_az declination", obj_v_az.declination(77)) # verify declination p 41

    obj_v_inc = SolarAngle(40, 100, 9)
    print("cos_incidence", obj_v_inc.cos_incidence(9.5, 47, 30))     # p50
    print("zenith_daily ", obj_v_inc.zenith_cos_daily(47))
    print("incidence ", obj_v_inc.incidence_cos_daily(47, 30))

    obj_ratio = SolarAngle(36.44, 136.554242, 9)
    print("hourly radiation ratio daily ", obj_ratio.hourly_radiation_ratio_daily(89))

    obj_p61 = SolarAngle(43, 136, 9)
    # print(round(obj_p61.cal_extraterrestrial_radiation_horizontal_hourly(10, 105) / pow(10, 6), 2), "MJ/m^2")
    print(round(obj_p61.cal_extraterrestrial_radiation_horizontal_total_daily(105)/pow(10, 6),2), "MJ/m^2")

    obj_p112 = SolarAngle(40, 136, 9)
    beam, diffuse = obj_p112.cal_beam_diffuse_horizontal_daily(51)
    print(beam, diffuse)

    coeff = [1, 2, 1.5, 1.3, 1.2, 1.1, 1, 1.1, 1.3, 2, 2.2, 2.5, 0]
    # obj_0330 = SolarAngle(36.03, 140.08, 9)
    # hr_ratio = obj_0330.hourly_radiation_ratio_daily(89)
    # extra_radiation_0330 = obj_0330.cal_extraterrestrial_radiation_horizontal_total_daily(89)
    # modeled_radiation_0330 = []
    # for i in range(len(hr_ratio)):
    #     modeled_radiation_0330.append(round(extra_radiation_0330 * hr_ratio[i] / 10000 * 0.76 , 2))
    # print(modeled_radiation_0330)
    # real_diff_0330 = [4, 26, 46, 61, 68, 72, 74, 70, 68, 65, 60, 39, 13]
    # real_beam_0330= [6,104,194,235,266,280,284,286,274,246,177,124, 32]
    # real_total_0330 = []
    # for i in range(len(real_diff_0330)):
    #     real_total_0330.append(real_beam_0330[i] + real_diff_0330[i])
    # fig, ax = plt.subplots()
    # # ax.plot(range(6, 19), modeled_radiation_0330, 'g^', color="red", label = "modeled")
    # ax.plot(range(6, 19), real_total_0330, 'g^', color="green", label = "measured")
    # v2_power_0330, v2_radiation_0330 = obj_0330.cal_diff_beam_v2(89)
    # v2_radiation_0330.append(0)
    # ax.plot(range(6, 19), v2_radiation_0330, 'g^', color="blue", label = "v2")

    # ax.legend()
    # ax.set_title("20150330")
    # ax.set_ylim([0, 500])
    # # G_cb_daily, G_cd_daily = obj_0330.cal_beam_diffuse_horizontal_daily(89)
    # # G_c_total_daily = []
    # # for i in range(len(G_cb_daily)):
    # #     G_c_total_daily.append(G_cb_daily[i] + G_cd_daily[i])
    # # print(len(G_c_total_daily), G_c_total_daily)
    # # G_cb_daily.append(0)

    # print("-----------------------------------------------------------------")
    # obj_0327 = SolarAngle(36.03, 140.08, 9)
    # hr_ratio_0327 = obj_0327.hourly_radiation_ratio_daily(86)
    # extra_radiation_0327 = obj_0327.cal_extraterrestrial_radiation_horizontal_total_daily(86)    
    # modeled_radiation_0327 = []
    # for i in range(len(hr_ratio)):
    #     modeled_radiation_0327.append(round(extra_radiation_0327 * hr_ratio_0327[i] * 0.9 / 10000 , 2))
    # print(modeled_radiation_0327)
    # real_diff_0327 = [3, 17, 26, 31, 34, 36, 39, 40, 41, 38, 29, 23,9]
    # real_beam_0327 = [20,192,281,319,338,348,346,341,325,310,299,233,102]
    # real_total_0327 = []
    # for i in range(len(real_diff_0327)):
    #     real_total_0327.append(real_beam_0327[i] + real_diff_0327[i])
    # fig, ax = plt.subplots()
    # # ax.plot(range(6, 19), modeled_radiation_0327, 'g^', color="red", label = "modeled")
    # ax.plot(range(6, 19), real_total_0327, 'g^', color="green", label = "measured")
    # v2_power_0327, v2_radiation_0327 = obj_0327.cal_diff_beam_v2(86)
    # v2_radiation_0327.append(0)
    # ax.plot(range(6, 19), v2_radiation_0327, 'g^', color="blue", label = "v2")

    # ax.legend()
    # ax.set_title("20150327")
    # ax.set_ylim([0, 500])
    # print("0327 ratio", hr_ratio_0327)
    # print("0327", extra_radiation_0327, modeled_radiation_0327, real_total_0327)
    # print("83", obj_0327.declination(83))
    # print("171", obj_0327.declination(171))
    # print("-----------------------------------------------------------------")
    
    # obj_0331 = SolarAngle(36.03, 140.08, 9)
    # hr_ratio = obj_0331.hourly_radiation_ratio_daily(90)
    # extra_radiation_0331 = obj_0331.cal_extraterrestrial_radiation_horizontal_total_daily(90)
    # modeled_radiation_0331 = []
    # for i in range(len(hr_ratio)):
    #     modeled_radiation_0331.append(round(extra_radiation_0331 * hr_ratio[i] / 10000 * 0.82, 2))
    # print(modeled_radiation_0331)
    # real_diff_0331 = [4, 28, 51, 67, 75, 75, 60, 59, 63, 54, 46, 34, 12 ]
    # real_beam_0331 = [ 6, 98,186,228,258,274,308,307,285,274,243,173, 19]
    # real_total_0331 = []
    # for i in range(len(real_diff_0331)):
    #     real_total_0331.append(real_beam_0331[i] + real_diff_0331[i])
    # fig, ax = plt.subplots()
    # # ax.plot(range(6, 19), modeled_radiation_0331, 'g^', color="red", label = "modeled")
    # ax.plot(range(6, 19), real_total_0331, 'g^', color="green", label = "measured")
    # v2_power_0331, v2_radiation_0331 = obj_0331.cal_diff_beam_v2(90)
    # v2_radiation_0331.append(0)
    # ax.plot(range(6, 19), v2_radiation_0331, 'g^', color="blue", label = "v2")
    # ax.legend()
    # ax.set_title("20150331")
    # ax.set_ylim([0, 500])

    rh = [66, 18, 50, 46, 14, 33, 71, 71, 81, 24, 16, 17, 16, 25,
          52, 53, 41, 35, 70, 65, 22, 37, 18, 18, 17, 16, 9,17, 33, 22, 35]

    beam_03 = [1,3122,0,1669,2402,431,5,22,0,1670,2599,2807,2820,955,218,339,2299,865,0,39,1214,1861,1179,3504,3195,3363,3454,1599,1216,2508,2659]

    diff_03 =   [350,343,401,588,490,1084,650,532,420,572,464,415,445,991,710,932,608,1005,310,852,835,857,776,334,479,373,366,1003,703,666,628]

    obj_03 =  SolarAngle(36.03, 140.08, 9)

    beam_03_daily = [[0,0,0,0,1,0,0,0,0,0,0,0,0],
                     [0,104,251,300,324,339,337,336,319,306,284,193,29],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,1,4,191,268,263,274,256,192,186,34],
                     [0,75,234,293,318,325,331,333,209,119,163,0,2],
                     [0,6,10,4,3,45,131,5,52,69,21,83,2],
                     [0,0,0,1,0,0,0,0,0,1,3,0,0],
                     [0,0,0,0,0,0,0,7,10,5,0,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,108,252,323,349,333,264,0,10,21,1,0,9],
                     [0,148,275,323,346,342,352,251,268,143,67,61,23],
                     [0,108,229,259,315,329,335,326,310,254,246,90,6],
                     [1,132,250,301,322,330,324,309,290,201,218,128,14],
                     [0,51,123,141,80,76,30,5,102,146,108,79,14],
                     [0,21,58,10,0,0,0,4,0,24,38,53,10],
                     [0,0,0,3,17,81,90,135,13,0,0,0,0],
                     [0,46,138,200,245,285,311,311,254,248,205,48,8],
                     [0,0,47,197,233,162,67,69,41,47,2,0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0,0],
                     [0,0,0,0,0,0,0,1,18,19,0,0,1],
                     [0,0,0,1,3,81,137,73,281,270,219,129,20],
                     [0,35,125,182,208,226,235,226,227,190,141,59,7],
                     [1,78,184,239,246,275,70,77,9,0,0,0,0],
                     [17,188,284,327,345,354,354,350,339,329,304,225,88],
                     [19,188,279,310,324,332,321,329,266,278,273,206,70],
                     [17,180,273,316,337,343,345,348,335,313,279,211,66],
                     [20,192,281,319,338,348,346,341,325,310,299,233,102],
                     [6,33,24,9,19,106,142,225,298,261,220,193,63],
                     [7,116,209,246,278,282,73,2,1,2,0,0,0],
                     [6,104,194,235,266,280,284,286,274,246,177,124,32],
                     [6,98,186,228,258,274,308,307,285,274,243,173,19]]
    diff_03_daily = [[0,3,24,44,87,45,38,34,36,18,11,10,0],
                     [0,7,20,28,34,37,42,42,43,37,28,20,5],
                     [0,4,9,23,63,67,73,41,43,35,27,15,1],
                     [0,1,8,47,110,96,73,71,59,55,45,19,4],
                     [0,9,23,30,35,40,42,41,98,89,56,24,3],
                     [0,15,47,76,119,135,142,141,158,123,81,42,5],
                     [0,7,21,57,73,75,73,82,90,74,68,26,4],
                     [0,2,11,19,40,45,34,101,136,85,43,13,3],
                     [0,10,30,42,31,60,67,62,60,35,16,6,1],
                     [0,10,23,23,24,36,79,73,120,102,63,16,3],
                     [0,10,20,25,27,33,34,57,75,80,68,28,7],
                     [0,13,28,38,39,41,43,46,48,47,39,28,5],
                     [0,12,25,31,37,40,45,50,54,65,47,32,7],
                     [0,16,48,75,115,152,153,123,112,86,63,40,8],
                     [0,22,62,82,63,45,60,62,68,107,81,49,9],
                     [0,15,41,84,130,157,162,126,115,75,19,7,1],
                     [1,21,49,67,71,64,54,53,67,61,52,37,11],
                     [1,20,58,68,76,120,159,157,131,118,65,25,7],
                     [0,3,9,25,49,85,53,29,16,16,9,11,5],
                     [1,12,18,48,52,104,115,146,164,118,49,20,5],
                     [0,5,18,73,93,134,151,136,68,57,51,38,11],
                     [1,25,55,75,90,98,101,103,92,87,72,46,12],
                     [2,23,45,57,70,74,130,150,110,58,30,23,4],
                     [2,15,24,28,31,33,36,37,37,33,28,21,9],
                     [2,15,25,34,42,45,54,55,63,59,45,29,11],
                     [2,17,27,32,34,38,40,39,39,38,33,25,9],
                     [3,17,26,31,34,36,39,40,41,38,29,23,9],
                     [5,37,73,92,137,165,158,107,66,61,58,33,11],
                     [3,26,45,55,60,68,140,103,81,81,21,16,4],
                     [4,26,46,61,68,72,74,70,68,65,60,39,13],
                     [4,28,51,67,75,75,60,59,63,54,46,34,12]]
    count = 0
    inner_count = 0
    for i in range(0, 31):
        # power_beam, power_diff, power, radiation = obj_03.cal_diff_beam_v2(60 + i, rh[i])
        radiation = obj_03.cal_extraterrestrial_radiation_normal_daily(60 + i)
        real_radiation = []
        beam = beam_03_daily[i]
        diff = diff_03_daily[i]
        
        for j in range(0, 13):
            real_radiation.append(beam[j] + diff[j])

        if count % 6 == 0:
            f, ax = plt.subplots(2,3)
            inner_count = 0
        print(int(inner_count / 3), inner_count % 3)
        x = int(inner_count / 3)
        y = inner_count % 3

        # print("radiation", len(radiation))        
        # radiation.append(0)
        # print("real_radiation", len(real_radiation))
        
        ax[x,y].plot(range(6,19), radiation, 'g^', label="modeled", color="red")
        ax[x,y].set_title("2015-03-" + str(i + 1))

        ax[x,y].plot(range(6, 19), real_radiation, 'g^', label="measured")
        # ax[x,y].legend()
        count += 1
        inner_count += 1
        # for j in range(0, 13):
        #     real_radiation.append(beam[j] + diff[j])
        # fig, ax = plt.subplots()
        # ax.plot(range(6, 19), real_radiation, 'g^', color="green", label = "measured")
        # radiation.append(0)
        # ax.plot(range(6, 19), radiation, 'g^', color="blue", label = "v2")
        # ax.legend()
        # ax.set_title("2015-03-" + str(i + 1))
        # ax.set_ylim([0, 500])
        print("Rb", obj_03.cal_inclined_radiation(60+i, rh[i], 30))

    # test for hourly ratio
    obj_test_ratio = SolarAngle(36.03, 140.08, 9)
    print("ratio daily", obj_test_ratio.hourly_radiation_ratio_daily(80))

    five_diff, modeled_ratios, five_diff_cor = obj_test_ratio.five_mins_radiation_ratio_daily(89)
    print("modeled_ratio", modeled_ratios)
    print("ratio five mins", five_diff)
    print("cor", len(five_diff_cor), five_diff_cor)

    radiation_every_five = obj_test_ratio.radiation_every_five_mins(89, 22)
    print(radiation_every_five)

    power_every_five = obj_test_ratio.power_every_five_mins(89, 22)
    print("power every five", power_every_five, len(power_every_five))

    power_beam, power_diff, power, radiation = obj_03.cal_diff_beam_v2(89, 22)
    print("0330 : radiation", radiation, "power", power)

    # calculate total daily radiation first
    H_0330_total = SolarAngle(36.03, 140.08, 9)
    H = H_0330_total.cal_extraterrestrial_radiation_horizontal_total_daily(89)  # 
    r_0330 = H_0330_total.hourly_radiation_ratio_daily(89)
    radiation = []
    for i in range(len(r_0330)):
        radiation.append(round(H * r_0330[i] / 10000, 2))    # unit in 0.01 MJ/m^2
    every_five_mins_radiation = H_0330_total.radiation_every_five_mins_given_hourly_radiation(89, radiation)
    print("total : H", H, "ratio", r_0330, "radiation", radiation)
    print("every five minuts", every_five_mins_radiation)
    for i in range(len(five_diff_cor)):
        if i % 12 == 0:
            print("_____________________________")
        print(round(five_diff_cor[i], 4))

    print("new method for five minus ", H_0330_total.cal_extraterrestrial_radiation_horizontal_five_min_daily(89))

    print("H_0329 ", H_0330_total.cal_extraterrestrial_radiation_horizontal_five_min_daily(88))
    print("H_0326 ", H_0330_total.cal_extraterrestrial_radiation_horizontal_five_min_daily(85))
    print("H_0325 ", H_0330_total.cal_extraterrestrial_radiation_horizontal_five_min_daily(84))

    H_0327_total = SolarAngle(36.03, 140.08, 9)
    I_o_0327 = []
    for i in range(6, 18):
        temp = H_0327_total.cal_extraterrestrial_radiation_horizontal_between_timestamp(i, i+1, 89 )
        I_o_0327.append(round(temp /10000, 2))

    
    
    # print("I_o_0327",  I_o_0327)
    # haha = beam_03_daily[29]
    # print(diff_rad(haha[1:], I_o_0327))

    H_0327_total = SolarAngle(43, 140.08, 9)
    print(degrees(H_0327_total.sunset_hour_angle(75)))
    print(H_0327_total.cal_extraterrestrial_radiation_horizontal_total_daily(105))

    H_0326 = SolarAngle(36.03, 140.08, 9)

    count = 0
    tt = list(seq(0, 24, 1/12))

    I_daily = []
    i = 0
    for i in range(len(tt) - 1):        
        I = H_0326.cal_extraterrestrial_radiation_horizontal_between_timestamp(tt[i], tt[i+1], 86)
        if I<0:
            print(i)
        I_daily.append(round(I / 300, 2))
    print(I_daily, len(I_daily))
    ws = H_0326.sunset_hour_angle(86)
    sunrise = degrees(ws) / (2 * 15)
    print("sunrise", sunrise)

    H_0326.cal_r_b_daily(30, 86)
    
    # plt.show()
    
