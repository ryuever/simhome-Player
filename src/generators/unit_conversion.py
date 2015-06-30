from __future__ import division

""" Unit Conversion """
# refer to http://www.pveducation.org/pvcdrom/appendices/units-and-conversions

def J2Watt():
    """
    Purpose : conversion from J/m**m to 
    """

# Solar Radiation Conversion
def Btu2J(btu):
    return btu * 1055



# from C degree to K degree


###########################################################
# Conversion between Joule and Watt
# 
# W = J / s = N * m / s = kg * m^2 / s^3
#
# J = kg * m^2 / s^2 = N * m = Pa * m^3
##########################################################



###########################################################
# Temporature
# 
# 
###########################################################
def f2c(f_temp):
    """
    Purpose : Convert Fahrenheit to Celsius
    Expects : fahrenheit (F)
    Return  : Celsius (C)
    """
    return (f_temp - 32)  * 5 / 9

def c2k(c_temp):
    """
    Purpose : Convert Celsius temperature to kelvin (Thermodynamic temperature)
    Expects : celsius temperature(C)
    Return  : Thermodynamic temperature (K)
    """
    return c_temp + 273.15

def f2k(f_temp):
    return (f_temp - 32)  * 5 / 9 + 273.15

###########################################################
# Gas
# gas constant(R) = 8.31447 J/(mol * K)
# 
###########################################################
R = 8.31447

def std_atm(atm_v):
    """
    Purpose : standard atmosphere(atm) to pascal(kpa)
    Expects : a number which means the times of standard atmosphere
    Description : 1 atm = 101.325 kilopascal   
    Return  : kilopascal value (kpa)
    """
    return atm_v * 101.325

if __name__ == "__main__":
    print(specific_gas_constant(0.0289))
