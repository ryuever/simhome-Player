from __future__ import division
from math import pi, sin, asin, exp, cos, acos, log, sqrt, pow, tan

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


def dof2md(year, dof):
    """
    Purpose : calculating the corresponding month, 
              day fromat from year and day number
    """
    if ((year % 4 == 0) and (year % 100 != 0 or year % 400 == 0 )):
        leap = 1
    else:
        leap = 0

    mon = 12
    while(dof <= month_days[leap][mon]):
        mon = mon - 1

    day = dof - month_days[leap][mon]
    print("month : {0}, day : {1}".format(mon, day))
    return [mon, day]

def deg2rad(degree):
    """ convert degree to radians"""
    return degree * pi / 180

def rad2deg(radian):
    """convert radian to degree"""
    return 180 * radian / pi

class Solar_Angle(object):
    def __init__(self, lat, lgt, dof):
        self.lat_degree = lat
        self.long_degree = lgt

        self.day_num = doy        # day of year, day number
        self.sol_time = 0          # True solar time
        
        self.sunrise               # local sunrise time
        self.sunset = 0            # local sunset time

        self.eq_time_rad = 0
        self.ele_rad = 0
        self.ele_sin = 0
        self.ele_cos = 0
        self.azim = 0               # azimuth angle in radians N=0, E=90, S=180, W=270
        self.declin = 0             # declination angle
        self.declin_sin = 0
        
        self.year = 2015        
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.timezone = 0
        self.interval = 0

        self.amass = 0
        self.hr_ang = 0             # hour angle -- hour of sun from solar noon
        
        self.diff_horz = 0          # 
        self.dir_norm = 0           #
        self.extra_irrad = 0        #

        self.local_time = 0
        self.day_ang = 0

    def eq_time(self, day_of_year):            
        """
        Purpose : Compute the equation of time
        Expects : Day of year from Jan 1
        return  : equation time in minutes
        """
        rad = deg2rad(360 *(day_of_year - 81) / 365)
        self.eq_time_rad = 9.87 * sin(rad * 2) - 7.53 * cos(rad) - 1.5 * sin(rad)

    def sol_time(self, std_time, day_of_year, std_meridian, longitude):
        """
        Purpose : Compute the solar time
        Explanation : The factor of 4 minutes comes from the fact that the Earth rotates
                      1 degree every 4 minutes.
        Return : local solar time in hours. 9.5 means 9:30
        """
        std_meridian_degree = 15 * std_meridian
        self.sol_time_hr = std_time + eq_time(day_of_year) / 60 + 4 * (longitude-std_meridian_degree) / 60

    def local_time(self, sol_time, day_of_year, std_meridian, longitude):
        """
        Purpose : Reverse of calculating locate time to solar time
        Return  : Local time in decimal hours
        """
        std_meridian_degree = 15 * std_meridian
        self.local_time = sol_time - eq_time(day_of_year) / 60 - 4 * (longitude-std_meridian_degree) / 60

    def hour_angle(self, sol_time):
        """
        Explanation : The Earth rotate 15 degree per hour
        Purpose : Compute the hour angle
        Return  : Reture a hour angle radians
        """
        self.hr_ang = -deg2rad(15 * (sol_time - 12))   # morning +, afternoon -

    def sin_declination(self, day_of_year):
        self.declin_sin = sin(deg2rad(23.45)) * sin(deg2rad(360 / 365 * (day_of_year - 81)))

    def declination(self, day_of_year):
        """
        Purpose : Compute the solar declination angle
        Expectes : Days of year from Jan 1
        Retrun : Declination angle in radians    
        """
        self.declin = asin(sin_declination(day_of_year))
    
    def sin_ele(self, day_of_year, latitude, sol_time):
        """
        Purpose : sine of elevation angle    
        """
        hr_ang = hour_angle(sol_time)
        decl = declination(day_of_year)
        lat_rad = deg2rad(latitude)
        self.ele_sin = sin(decl) * sin(lat_rad) + cos(decl) * cos(lat_rad) * cos(hr_ang)

    def elevation(self, day_of_year, latitude, sol_time):
        """
        Description : Also called altitude. It's the complement of zenith
        Purpose : Compute the elevation angle
        Return  : elevation angle in radians     
        """
        self.ele_rad = asin(sin_ele(day_of_year, latitude, sol_time))

    def zenith(self, day_of_year, latitude, sol_time):
        """
        Purpose : Compute the zenith angle. complement of elevation
        Return  : zenith angle in radians
        """
        hr_ang = hour_angle(sol_time)
        decl = declination(day_of_year)
        lat_rad = deg2rad(latitude)
        self.zen = acos(sin(decl) * sin(lat_rad) + cos(decl) * cos(lat_rad) * cos(hr_ang))    

    def azimuth(self, day_of_year, latitude, sol_time):
        """
        Purpose : Compute the azimuth angle
        Return  : azimuth angle in radians
        """
        hr_ang = hour_angle(sol_time)
        decl   = declination(day_of_year)
        lat_rad = deg2rad(latitude)
        alpha = deg2rad(90) - lat_rad + decl
        self.azim = acos((sin(decl) * cos(lat_rad) - cos(decl) * sin(lat_rad) * cos(hr_ang)) / cos(alpha))
    
    def cos_incident(self, latitude, slope, az, sol_time, day_of_year):
        """
        still in considered
        """
        hr_ang = hour_angle(sol_time)
        decl   = declination(day_of_year)
        lat_rad = deg2rad(latitude)
            
        sindecl = sin(decl)
        sinlat = sin(lat_rad)
        sinslope = sin(slope)
        sinaz = sin(az)
        sinhr = sin(hr_ang)

        cosdecl = cos(decl)
        coslat = cos(lat_rad)
        cosslope = cos(slope)
        cosaz = cos(az)
        coshr = cos(hr_ang)

        inc_cos = sindecl * sinlat * cosslope - \
                 sindecl * coslat * sinslope * cosaz + \
                 cosdecl * coslat * cosslope * coshr + \
                 cosdecl * sinlat * sinslope * cosaz * coshr + \
                 cosdecl * sinslope * sinaz * sinhr
        return inc_cos < 0.0 and 0.0 or inc_cos

    def day_ang(self, day_of_year):
        """
        Purpose : compute the day angle
        """
        self.day_ang = 2 * pi * (day_of_year -1) / 365

    def amass(self, zenith):
        """
        Purpose : Compute the air mass
        Expects : air mass in fraction
        """
        self.amass = 1 / cos(zenith)       

    def gb_radiation():
        """
        Purpose : Compute global radiation    
        """
        return 1.353 * pow(0.7, pow(1.5, 0.678)) * 1.1

    def dr_radiation():
        """
        Purpose : Compute direct radiation
        """
        return 1.353 * pow(0.7, pow(1.5, 0.678))

    def df_radiation():
        """
        Purpose : Compute diffuse radiation
        """
        pass

        ### refer to link http://www.macaulay.ac.uk/LADSS/documents/Calc_sr_ff.pdf ###
        ####### Beginning ########
    def atmos_trans(day_of_year):
        """
        Purpose : Compute atmospheric transmissivity    
        """
        return 0.64 + 0.12 * cos((day_of_year - 174) / 365 * 2 * pi)

    def daylight_period(latitude, declination):
        """
        Purpose : Compute daylight period per day
        Expects : declination angle in radians, latitude in angle
        Return  : daylight period
        """
        lat_rad = latitude * pi / 180
        dlt_pd  = 2 / (15 * pi / 180) * acos(-tan(lat_rad) * tan(declination))

    def tauthing(day_of_year, latitude, sol_time):
        sin_elevation = sin_ele(day_of_year, latitude, sol_time)
        at_trans = atmos_trans(day_of_year)    
        return pow(at_trans, 1/sin_elevation)

    def jp(day_of_year, latitude, sol_time):
        sin_elevation = sin_ele(day_of_year, latitude, sol_time)
        tau_thing = tauthing(day_of_year, latitude, sol_time)
        return 1367 * sin_elevation / pi / 2 * (1 + tau_thing)

    def js(day_of_year, latitude, sol_time):
        sin_elevation = sin_ele(day_of_year, latitude, sol_time)
        tau_thing = tauthing(day_of_year, latitude, sol_time)
        return 1367 * sin_elevation / pi * tau_thing

    def f_blue(day_of_year, latitude, sol_time):    
        tau_thing = tauthing(day_of_year, latitude, sol_time)
        return (1 - tau_thing) / (1 + tau_thing)

    def f_cloud(day_of_year, latitude, sol_time):
        return 0.4 * f_blue(day_of_year, latitude, sol_time)

    def cloud_por(sunshine_dur, day_len):
        return 1 - sunshine_dur / day_len

    def j0(day_of_year, latitude, sol_time, declination, longitude):
        js_val = js(day_of_year, latitude, sol_time)
        print("js_val is {0}".format(js_val))    
        jp_val = jp(day_of_year, latitude, sol_time)
        print("jp_val is {0}".format(jp_val))
        h0s = sunshine_duration(declination, latitude)
        h = day_length(declination, longitude)
        f_blue_val = f_blue(day_of_year, latitude, sol_time)
        f_cloud_val = f_cloud(day_of_year, latitude, sol_time)
        c = cloud_por(h0s, h)

        j0 = (h0s * js_val + h * jp_val * (f_blue_val * (1 - c) + f_cloud_val * c)) / h
        return j0

    def cal_rad2(j0, h):
        return max(0, j0 / 1000000 * h * 3600 * 2)
    ###### Ending #########

    # refer to "Estimate of the direct, diffuse and global solar radiations"
    # Beginning ####
    def day_length(self, declination, longitude):
        """
        Purpose : Compute day length
        Expects : declination in radians, longitude in degree
        Return  : day length in hours
        """
        lgd_rad = deg2rad(longitude)
        return 24 * (1 -  acos((tan(declination)) * tan(lgd_rad)) / pi)

    def sunshine_duration(self, declination, latitude):
        """
        Purpose : Compute the sunshine duration
        Expects : latitude in degree, declination in radians
        Return  : sunshine duration in hours
        """
        lat_rad = deg2rad(latitude)
        return 2 / 15 * acos(-tan(declination) * tan(lat_rad))

    def sun_set_rise_time(self, latitude, day_of_year):
        lat_rad = deg2rad(latitude)
        sin_lat = sin(lat_rad)
        cos_lat = cos(lat_rad)
        sin_decl = sin_declination(day_of_year)
        cos_decl = cos(declination(day_of_year))

        sunrise = 12 - 1 / deg2rad(15) * acos(- sin_lat * sin_decl / cos_lat * cos_decl)
        sunset  = 12 + 1 / deg2rad(15) * acos(- sin_lat * sin_decl / cos_lat * cos_decl)

        print("sunrise : {0}".format(sunrise))
        print("sunset : {0}".format(sunset))            


    def cal_radiation(self, latitude, day_of_year, sol_time):
        lat_rad = deg2rad(latitude)
        sin_lat_rad = sin(lat_rad)
        a_he = sin((360 / 365) * (day_of_year - 121))
        T1 = pow(0.89, lat_rad)
        T2 = (0.9 + 0.4 * a_he) * pow(0.63, lat_rad)
        elev = sin_ele(day_of_year, latitude, sol_time)
        T3 = 2.4 - 0.9 * sin_lat_rad + 0.1 * (2 + sin_lat_rad) * a_he - 0.2 * lat_rad - (1.22 + 0.14 * a_he) * (1 - elev)
        print("T1 is : {0}".format(T1))
        print("T2 is : {0}".format(T2))
        print("T3 is : {0}".format(T3))

        T = T1 + T2 + T3
        I_cons = 1367
    
        earth_sun_dis = 1 + 0.034 * cos(day_of_year - 2)
        I = I_cons * earth_sun_dis * exp(-T * 1 / (0.9 + 9.4 * elev / T1)) * elev

        a = 1.1
        b = log(T1 + T2) - 2.8 + 1.02 * (1 - elev) * (1 - elev)
        D = I_cons * earth_sun_dis * exp(-1 + log(elev)) + a - sqrt(a * a + b * b)
        
        print("I is : {0}".format(I))
        print("D is : {0}".format(D))
        
### Ending ###
if __name__ == "__main__":
    "Testing of equation of time"
    print("eot : {0}".format(eq_time(27)))     # -12.7648055069
    print("eot : {0}".format(eq_time(105)))    # -0.240124057807
    
    "Testing of solar time"
    print("solar_time : {0}".format(sol_time(10.0, 27, 9, 136.554242)))   # 9.89
    print("solar_time : {0}".format(sol_time(10.0, 68, 9, 136.554242)))   # 9.91

    "Testing of solar time"
    print("local_time : {0}".format(local_time(9.89, 27, 9, 136.554242)))   # 9.99913062511
    print("local_time : {0}".format(local_time(9.91, 68, 9, 136.554242)))   # 9.99439801261

    "Testing of hour angle"
    solar_time_1 = sol_time(10.0, 27, 9, 136.554242)
    print("hour angle : {0}".format(hour_angle(solar_time_1)))   # -31.636
    
    "Testing of declination angle"
    print("declation angle : {0}".format(declination(80)))      # Mar 22 equinox
    print("declation angle : {0}".format(declination(171)))      # Jun 21 solstice
    print("declation angle : {0}".format(declination(263)))     # Sep 23 equinox
    print("declation angle : {0}".format(declination(352)))     # Dec 22 solstice        

    "Testing of azimuth angle"
    solar_time_2 = sol_time(12.0, 27, 9, 136.554242)
    print("azimuth : {0}".format(rad2deg(azimuth(27, 36.44, solar_time_2))))
    print("elevation : {0}".format(rad2deg(elevation(27, 36.44, solar_time_2))))
    print("zenith : {0}".format(rad2deg(zenith(27, 36.44, solar_time_2))))
    
    "Testing of cos_incident"
    az = azimuth(27, 36.44, solar_time_2)
    print("cos_incident : {0}".format(rad2deg(acos(cos_incident(36.44, 33.86, az, solar_time_2,  27)))))

    zen = zenith(27, 36.44, solar_time_2)    
    print("air mass : {0}".format(amass(zen)))
    
    dof2md(2015, 38)

    print("atmos trans is {0}".format(atmos_trans(27)))
    print("atmos trans is {0}".format(atmos_trans(120)))

    print("day length is {0}".format(day_length(declination(80), 134)))
    print("sunshine duration is {0}".format(day_length(declination(80), 36)))

    sun_set_rise_time(36, 80)
    
    print("j0 is {0}".format(j0(27, 36, solar_time_1, declination(27), 135.44)))

    day_len = day_length(declination(27), 135.44)
    j0_val = j0(27, 36, solar_time_1, declination(27), 135.44)
    print("radiation is {0}".format(cal_rad2(j0_val, day_len)))

    cal_radiation(36.44, 27, solar_time_1)
