# Create Python class for a thermodynamic state

#import pandas as pd.... never mind, just use CoolProp for the fluid data
import CoolProp.CoolProp as CP  #must have CoolProp library installed

# def class fluid_props(subcooled_csv, saturated_csv, superheated_csv):
#     ''' This class is a pandas panel of three data frames that define the fluid properties. The inputs are the filenames of the .csv's that contain the fluid data. The saturated_csv can be one filename or a list of filenames (such as saturated data listed by pressure or by temperature) that will be combined into one dataframe'''
#     # how do I structure this pandas panel of three data frames?
    # idea: use MultiIndex to index the subcooled and superheated data frames by both pressure and temperature



class state(fluid,**kwargs):
    ''' This is a class that can be used to define a thermodynamic state for a given fluid. The user must enter the fluid string to select in CoolProp and then 2 independent named variables for the state to be properly defined. All variables are specific, in that they are valued per unit mass. Optional variables and their default units are:
        T = temperature, (deg C)
        p = pressure, (MPa)
        v = specific volume (m^3/kg)
        d = density (kg/m^3)
        u = internal energy (kJ/kg)
        h = enthalpy (kJ/kg)
        s = entropy (kJ/kg.K)
        x, Q = quality (real number between 0 and 1 inclusive)
    '''
    def __init__(self,fluid,**kwargs):
        self.fluid = fluid
        state_vars = ['T','P','D','V','U','H','S','X','Q']
        # note that 'x' and 'Q' both represent two-phase quality
        key1 = '', value1 = '', key2 = '', value2 = ''
        for key, value in kwargs.items():
            key.upper() #convert to uppercase
            if key in state_vars:
                if key == 'X': key = 'Q'  # for CoolProp
                if key == 'V': key = 'D', value = 1/value  # use denisty for CoolProp
                if key1 != '': key1 = key, value1 = value, continue
                if key2 != '': key2 = key, value2 = value, continue
        # set state properties
        self.T = CP.PropSI('T',key1,value1,key2,value2,fluid)
        self.p = CP.PropSI('P',key1,value1,key2,value2,fluid)
        self.v = 1 / CP.PropSI('D',key1,value1,key2,value2,fluid)
        self.d = CP.PropSI('D',key1,value1,key2,value2,fluid)
        self.u = CP.PropSI('U',key1,value1,key2,value2,fluid)
        self.h = CP.PropSI('H',key1,value1,key2,value2,fluid)
        self.s = CP.PropSI('S',key1,value1,key2,value2,fluid)
        self.x = CP.PropSI('Q',key1,value1,key2,value2,fluid)
        
class process(st_a,st_b):
    # create another class that defines values for a process: w, q, delta u, etc.
    # it should inherit the methods for class state

