from __future__ import division
from unit_conversion import *
from math import pi, pow
from utilities import *
import csv

Turbine_Model = sim_enum('Turbine_Model', 'GENERIC_IND_SMALL', 'GENERIC_SYNCH_SMALL')

class WindTurbine(object):    
    def __init__(self, ):
        # used to find wadj
        self.roughness_l = .055;     # European wind atlas def for terrain roughness, values range from 0.0002 to 1.6
	self.ref_height = 10;	     # height wind data was measured (Most meteorological data taken at 5-15 m)
        
        # used to find air density
        self.Ridealgas = 8.31447;   
        self.Molar = 0.0289644;      # average molar mass of dry air is 28.97 g/mol (0.0289kg/mol) 
        self.std_air_dens = 1.2754;  # dry air density at std pressure and temp in kg/m^3
        self.air_press = 1013.25     # standard atmosphere(hpa)
        self.temp = 25               # temperature (C)
        self.air_density = 1.2754    # kg/m^3

        self.avg_ws = 8              # avarage wind speed
        self.Turbine_Model = 1

        self.w_power = 0             # watt
        
        if self.Turbine_Model == Turbine_Model.GENERIC_IND_SMALL or Turbine_Model.GENERIC_SYNCH_SMALL:
            """ Creates generic 5 kW wind turbine, Fortis Montana 5 kW wind turbine """
            self.blade_diam = 5       # in m
            self.turbine_height = 16  # in m
            self.q = 0                # number of gearbox stages, no gear box
            self.Rated_VA = 6315      # calculate from P & Q
            self.Max_P = 5800
            self.Max_Q = 2500
            self.Rated_V = 600
            self.pf = 0.95
            # self.CP_Data = GENERAL_SMALL
            self.cut_in_ws = 2.5	  # lowest wind speed 
            self.cut_out_ws = 25	  # highest wind speed 
            self.Cp_max = 0.302	  # rotor specifications for power curve
            self.ws_maxcp = 7	  # |
            self.Cp_rated = self.Cp_max-.05 # |
            self.ws_rated = 17	  # |
            if self.Turbine_Model == Turbine_Model.GENERIC_IND_SMALL:
                # self.Gen_type = INDUCTION
                self.Rst = 0.12				
                self.Xst = 0.17					
                self.Rr = 0.12				
                self.Xr = 0.15			
                self.Rc = 999999
                self.Xm = 9.0	
            elif self.Turbine_Model == Turbine_Model.GENERIC_SYNCH_SMALL:
                # self.Gen_type = SYNCHRONOUS
                self.Rs = 0.05
                self.Xs = 0.200
                self.Rg = 0.000
                self.Xg = 0.000

    def specific_gas_constant(self):
        """
        Purpose : compute specific gas constant (J/mol * K)
        Expects : molar mass (kg / mol)
        Return  : specific gas constant (J / Kg * K)
        """
        return self.Ridealgas / self.molar

    def air_dens(self):
        """
        Purpose : compute air density
        Expects : pressure (kpa),
                  molar mass (kg / mol),
                  temperature (F)
        Return  : air density    
        """
        pressure = self.air_press * 100      # for temporary use
        # pressure = self.a_press * 100        # from hpa to pa
        pressure = self.
        speGasCons = specific_gas_constant()
        # k_temp = f2c(f_temp)            # from Fahrenheit to kelvin
        k_temp = c2k(self.temp)
    
        self.air_density = pressure / (speGasCons * k_temp)
        return self.air_density
    
    def wind_power(self):
        """
        Purpose : compute wind power
        """
        self.w_power = 1/2 * self.air_dens() * pi * pow(self.blade_diam/2, 2) * pow(self.avg_ws, 3)
        return self.w_power
    
if __name__ == "__main__":
    wtb = WindTurbine()
    print(wtb.wind_power()
