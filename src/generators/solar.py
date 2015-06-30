# para_list =[
#     ['generator_mode', 'UNKNOWN', 'CONSTANT_V', 'CONSTANT_PQ', 'CONSTANT_PF', 'SUPPLY_DRIVEN'],
#     ['generator_status', 'OFFLINE', 'ONLINE'],
#     ['panel type', 'SINGLE_CRYSTAL_SILICON', 'MULTI_CRYSTAL_SILICON', 'THIN_FILM_GA_AS', 'CONCENTRATOR']
# ]

# for item in para_list[0:1]:
#     # generator_mode = sim_enum(item)
#     item[0] = sim_enum(item)
# # map(sim_enum(para_list_ele), para_list)

# def sim_enum(para_list_ele):
#     name = para_list_ele[0]
#     para_list_items = para_list_ele[1:]
#     enum_list = list(enumerate(para_list_items))
#     enum_dict = {name : value for value, name in enum_list}
#     return type(name, (object,), enum_dict)



from utilities import *

class Solar(object):
    def __init__(self, lat, lgt, tilt):
        self.sol_con = 1367          # solar constant uses 1367 W/sq m
        
        self.latitude = lat
        self.longitude = lgt
        self.tilt = tilt


    




generator_mode = sim_enum('generator_mode', 'UNKNOWN', 'CONSTANT_V', 'CONSTANT_PQ', 'CONSTANT_PF', 'SUPPLY_DRIVEN')
generator_status = sim_enum('generator_status', 'ONLINE', 'OFFLINE')
panel_type = sim_enum('panel_type', 'SINGLE_CRYSTAL_SILICON','MULTI_CRYSTAL_SILICON', 'AMORPHOUS_SILICON','THIN_FILM_GA_AS', 'CONCENTRATOR')
power_type = sim_enum('power_type', 'AC', 'DC')
intallation_type = sim_enum('installation_type', 'ROOF_MOUNTED', 'GROUND_MOUNTED')
SOLAR_TILT_MODEL = sim_enum('solar_tilt_model', 'DEFAULT', 'SOLPOS', 'PLAYERVALUE')
SOLAR_POWER_MODEL = sim_enum('solar_power_model', 'DEFAULT', 'FLATPLATE')

# In [4]: SOLAR_TILT_MODEL.DEFAULT
# Out[4]: 0
#
# In [5]: SOLAR_TILT_MODEL.SOLPOS
# Out[5]: 1

# CNOTATION = 
print(generator_mode.CONSTANT_V)
print(power_type.AC)
print(power_type.DC)

class CNOTATION(object):
    I = 'i'
    J = 'j'
    A = 'd'
    R = 'r'
# CNOTATION = type('CNOTATION', (object,), dict(I='i', J='j', A='d', R='r'))
# typedef enum {I='i',J='j',A='d', R='r'} CNOTATION; /**< complex number notation to use */
print("start")
from sets import Set
def getter_setter_gen(name, type_):
    def getter(self):
        return getattr(self, "_" + name)
    def setter(self, value):
        if not isinstance(value, type_):
            raise TypeError("%s attribute must be set to an instance of %s" % (name, type_))
        print('name is {0} : {1}'.format("_" + name, value))
        setattr(self, "_" + name, value)
    return property(getter, setter)

def getter_setter_set(name, container):
    def getter(self):
        return getattr(self, "_"+name)
    def setter(self, value):
        if value not in container:
            raise TypeError("value is limited to {0}".format(container))
        setattr(self, "_" + name, value)
    return property(getter, setter)

def auto_attr_check(cls):
    new_dct = {}
    for key, value in cls.__dict__.items():
        if isinstance(value, type):
            print('type is {0} : {1}'.format(type, value))
            value = getter_setter_gen(key, value)
            print(value)
        else:
            value = getter_setter_set(key, value)
        new_dct[key] = value
    print(new_dct)
    # Creates a new class, using the modified dictionary as the class dict:
    return type(cls)(cls.__name__, cls.__bases__, new_dct)

@auto_attr_check
class complex(object):
    r = float  # real part
    i = float  # imaginary part
    f = Set(['i', 'j', 'd', 'r'])

complex_instance = complex()
complex_instance.r = 1.3
complex_instance.f = 'j'
print(complex_instance.f)
print("end")
class Solar(object):
    def __init__(self):
        self.NOCT = 118.4  #degF
        self.Tcell = 21.0   #degC
	self.Tambient = 25.0  #degC
	self.Tamb = 77 	#degF
	self.wind_speed = 0.0 
	self.Insolation = 0 
	self.Rinternal = 0.05 
	self.prevTemp = 15.0 	# Start at a reasonable ambient temp (degC) - default temp is 59 degF = 15 degC
	self.currTemp = 15.0 	# Start at a reasonable ambient temp (degC)
	self.prevTime = 0 
	self.Rated_Insolation = 92.902  #W/Sf for 1000 W/m2
        self.V_Max = complex (27.1,0)  # max.power voltage (Vmp) from GE solar cell performance charatcetristics
	self.Voc_Max = complex(34,0)  #taken from GEPVp-200-M-Module performance characteristics
	self.Voc = complex (34,0)   #taken from GEPVp-200-M-Module performance characteristics
	self.P_Out = 0.0 

	self.area = 323  #sq f , 30m2
    
	# Defaults for flagging
	self.efficiency = 0 
	self.Pmax_temp_coeff = 0.0 
	self.Voc_temp_coeff  = 0.0 

	self.pSolarD = NULL 
	self.pSolarH = NULL 
	self.pSolarG = NULL 
	self.pAlbedo = NULL 
	self.pWindSpeed = NULL 

	self.module_acoeff = -2.81 		#Coefficients from Sandia database - represents 
	self.module_bcoeff = -0.0455 	#glass/cell/polymer sheet insulated back, raised structure mounting
	self.module_dTcoeff = 0.0 		
	self.module_Tcoeff = -0.5 		#%/C - default from SAM - appears to be a monocrystalline or polycrystalline silicon

	self.shading_factor = 1 					#By default, no shading
	self.tilt_angle = 45 					#45-deg angle by default
	self.orientation_azimuth = 180.0 		#Equator facing, by default - for LIUJORDAN model
	self.orientation_azimuth_corrected = 0 	#By default, still zero
	self.fix_angle_lat = false 				#By default, tilt angle fix not enabled (because ideal insolation, by default)

	self.soiling_factor = 0.95 				#Soiling assumed to block 5% solar irradiance
	self.derating_factor = 0.95 				#Manufacturing variations expected to remove 5% of energy

	self.orientation_type = DEFAULT 	#Default = ideal tracking
	self.solar_model_tilt = solar_model_tilt.LIUJORDAN # "Classic" tilt model - from Duffie and Beckman (same as ETP inputs)
	self.solar_power_model = BASEEFFICIENT #Use older power output calculation model - unsure where it came from

	# Null out the function pointers
	self.calc_solar_radiation = NULL
        return 1  # return 1 on success, 0 on failure
    def init_climate():
        if self.solar_model_tilt != SOLAR_TILT_MODEL.PLAYERVALUE:
            if weather != null:
                print("solarpanel: no climate data found, using static data");
                
        
