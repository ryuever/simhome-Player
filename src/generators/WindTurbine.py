import csv
from unit_conversion import *
from math import pi, pow
from utilities import *

generator_mode = sim_enum('generator_mode', 'UNKNOWN', 'CONSTANT_V', 'CONSTANT_PQ', 'CONSTANT_PF', 'SUPPLY_DRIVEN')

class WindTurbine(object):    
    def __init__(self,roughness_l = 0.055, ref_height = 10, max_vrotor = 1.2
                 , avg_ws = 8, std_air_dens = 1.2754, std_air_temp = 0, std_air_press = 10000
                 , gen_mode, gen_status, blade_diam, cut_in_ws, cut_out_ws, Cp_max, Cp_rated
                 , ws_maxcp, ws_rated):
        # air density, temperature, pressure
        Ridealgas = 8.31447;
        Molar = 0.0289644;     # average molar mass of dry air is 28.97 g/mol (0.0289kg/mol) 

        if TurbineModel == GENERIC_IND_LARGE || GENERIC_SYNCH_LARGE:
            blade_diam = 82.5
            turbine_height = 90
            q = 3
            pf = 0.95
            Rated_VA = 1635000
            Max_P = 1500000
            Max_Q = 650000
            Rated_V = 600
            pf = 0.95
            CP_Data = GENERAL_LARGE
            cut_in_ws = 4               # lowest wind speed 
            cut_out_ws = 25             # highest wind speed 
            Cp_max = 0.302              # rotor specifications for power curve
            ws_maxcp = 7	
            Cp_rated = Cp_max-.05
            ws_rated = 12.5	
            if Turbine_Model == GENERIC_IND_LARGE :
                Gen_type = INDUCTION
                Rst = 0.12					
                Xst = 0.17					
                Rr = 0.12				
                Xr = 0.15			
                Rc = 999999
                Xm = 9.0	
            elif Turbine_Model == GENERIC_SYNCH_LARGE:
                Gen_type = SYNCHRONOUS
                Rs = 0.05
                Xs = 0.200
                Rg = 0.000
                Xg = 0.000
        if TurbineModel == GENERIC_IND_MID || GENERIC_SYNCH_MID:
            """ Creates generic 100kW wind turbine, northwind 100 """
            blade_diam = 23.2
            turbine_height = 30
            q = 0                        # number of gearbox stages, no gear box 
            Rated_VA = 156604
            Max_P = 150000
            Max_Q = 45000
            Rated_V = 480  
            pf = 0.9                     # lag and lead of 0.9
            CP_Data = GENERAL_MID
            cut_in_ws = 3.5              # lowest wind speed in m/s
            cut_out_ws = 25              # highest wind speed in m/s
            Cp_max = 0.302               # rotor specifications for power curve
            ws_maxcp = 7			
            Cp_rated = Cp_max-.05
            ws_rated = 14.5              # in m/s
            if Turbine_Model == GENERIC_IND_MID:
                """need to check the machine parameters"""        
                gen_type = INDUCTION
                Rst = 0.12					
                Xst = 0.17
                Rr = 0.12				
                Xr = 0.15			
                Rc = 999999
                Xm = 9.0
            elif Turbine_Model == GENERIC_SYNCH_MID:
                Gen_type = SYNCHRONOUS
                Rs = 0.05
                Xs = 0.200
                Rg = 0.000
                Xg = 0.000
        
        if Turbine_Model == GENERIC_IND_SMALL || GENERIC_SYNCH_SMALL:
            """ Creates generic 5 kW wind turbine, Fortis Montana 5 kW wind turbine """
            blade_diam = 5       # in m
            turbine_height = 16  # in m
            q = 0                # number of gearbox stages, no gear box
            Rated_VA = 6315      # calculate from P & Q
            Max_P = 5800
            Max_Q = 2500
            Rated_V = 600
            pf = 0.95
            CP_Data = GENERAL_SMALL
            cut_in_ws = 2.5	  # lowest wind speed 
            cut_out_ws = 25	  # highest wind speed 
            Cp_max = 0.302	  # rotor specifications for power curve
            ws_maxcp = 7	  # |
            Cp_rated = Cp_max-.05 # |
            ws_rated = 17	  # |
            if Turbine_Model == GENERIC_IND_SMALL:
                Gen_type = INDUCTION
                Rst = 0.12				
                Xst = 0.17					
                Rr = 0.12				
                Xr = 0.15			
                Rc = 999999
                Xm = 9.0	
            elif Turbine_Model == GENERIC_SYNCH_SMALL:
                Gen_type = SYNCHRONOUS
                Rs = 0.05
                Xs = 0.200
                Rg = 0.000
                Xg = 0.000
            if Turbin_Model == VESTAS_V82:
            """ Include manufacturer's data - cases can be added to call other wind turbines """
            turbine_height = 78
            blade_diam = 82
            Rated_VA = 1808000
            Rated_V = 600
            Max_P = 1650000
            Max_Q = 740000
            pf = 0.91                  # Can range between 0.65-1.00 depending on controllers and Pout.
            CP_Data = MANUF_TABLE		
            cut_in_ws = 3.5
            cut_out_ws = 20
            q = 2
            Gen_type = SYNCHRONOUS     # V82 actually uses a DFIG, but will use synch representation for now
            Rs = 0.025                 # Estimated values for synch representation.
            Xs = 0.200
            Rg = 0.000
            Xg = 0.000
        if TurbineModel == GE_25MW:
            turbine_height = 100
            blade_diam = 100
            Rated_VA = 2727000
            Rated_V = 690
            Max_P = 2500000
            Max_Q = 1090000
            pf = 0.95                  # ranges between -0.9 -> 0.9;
            q = 3
            CP_Data = GENERAL_LARGE
            cut_in_ws = 3.5
            cut_out_ws = 25
            Cp_max = 0.28
            Cp_rated = 0.275
            ws_maxcp = 8.2
            ws_rated = 12.5
            Gen_type = SYNCHRONOUS
            Rs = 0.035
            Xs = 0.200
            Rg = 0.000
            Xg = 0.000            
        if TurbineModel == BERGEY_10kW:
            turbine_height = 24
            blade_diam = 7
            Rated_VA = 10000
            Rated_V = 360
            Max_P = 15000
            Max_Q = 4000
            pf = 0.95                  # ranges between -0.9 -> 0.9;
            q = 0
            CP_Data = GENERAL_SMALL
            cut_in_ws = 2
            cut_out_ws = 20
            Cp_max = 0.28
            Cp_rated = 0.275
            ws_maxcp = 8.2
            ws_rated = 12.5
            Gen_type = SYNCHRONOUS
            Rs = 0.05
            Xs = 0.200
            Rg = 0.000
            Xg = 0.000
        if TurbineModel == USER_DEFINED:
            CP_Data = USER_SPECIFY
            Gen_type = USER_TYPE
            Rs = 0.2
            Xs = 0.2
            Rg = 0.1
            Xg = 0

def air_dens(self, a_press, molar, f_temp):
    """
    Purpose : compute air density
    Expects : pressure (kpa),
              molar mass (kg / mol),
              temperature (F)
    Return  : air density    
    """
    pressure = a_press * 100        # converted to pa
    speGasCons = specific_gas_constant(molar)
    # k_temp = f2c(f_temp)            # from Fahrenheit to kelvin
    k_temp = c2k(f_temp)

    air_density = pressure / speGasCons * k_temp
    return air_density

def wind_power(self, air_dens, blade_diam, ws):
    """
    Purpose : compute wind power
    """
    return air_dens / 1000 * pi * pow(blade_diam/2, 2) * pow(ws, 3)


ad = air_dens(10.04,0.02897 ,18.1)
wp = wind_power(ad, 16, 4.3)

print(ad)
print(wp)
