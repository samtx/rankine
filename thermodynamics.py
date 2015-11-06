# Create Python class for a thermodynamic state

#import pandas as pd.... never mind, just use CoolProp for the fluid data
import CoolProp.CoolProp as CP  #must have CoolProp library installed

# def class fluid_props(subcooled_csv, saturated_csv, superheated_csv):
#     ''' This class is a pandas panel of three data frames that define the fluid properties. The inputs are the filenames of the .csv's that contain the fluid data. The saturated_csv can be one filename or a list of filenames (such as saturated data listed by pressure or by temperature) that will be combined into one dataframe'''
#     # how do I structure this pandas panel of three data frames?
    # idea: use MultiIndex to index the subcooled and superheated data frames by both pressure and temperature



class State(object):
    ''' This is a class that can be used to define a thermodynamic state for a given fluid. The user must enter the fluid string to select in CoolProp and then 2 independent named variables for the state to be properly defined. All variables are specific, in that they are valued per unit mass. Optional variables and their default units are:
        T = temperature, (deg C)
        p = pressure, (MPa)
        v = specific volume (m^3/kg)
        d = density (kg/m^3)
        u = internal energy (kJ/kg)
        h = enthalpy (kJ/kg)
        s = entropy (kJ/kg.K)
        x, Q = quality (real number between 0 and 1 inclusive)
        velocity = velocity (m/s) for kinetic energy
        z = relative height (m) for potential energy
    '''
    def CP_convert(self,prop,value):
        ''' make necessary conversions for CoolProp functions '''
        #convert to uppercase
        prop = prop.upper()
        # use Q for quality but will accept x
        if prop == 'X':
            prop = 'Q'
        # use denisty for CoolProp
        elif prop == 'V':
            prop = 'D'
            value = 1/value
        # convert MPa to Pa for CoolProp
        elif prop == 'P':
            value = value * 10**6
        return prop,value

    def __init__(self,fluid,prop1,value1,prop2,value2,name="",velocity=0,z=0):
        self._fluid = fluid
        # note that 'x' and 'Q' both represent two-phase quality
        # set property name if specified
        self._name = name # 1, 2, 2s, 3, 4, 4s, 4b, etc.
        # make necessary conversions for CoolProp functions
        (prop1, value1) = self.CP_convert(prop1,value1)
        (prop2, value2) = self.CP_convert(prop2,value2)

        # set state properties
        # note that pairs h, T aren't yet supported by CoolProp
        #print(key1 + str(value1) + key2 + str(value2) + fluid)
#         try:
#             self._T = CP.PropsSI('T',key1,value1,key2,value2,fluid)
#         except:
#             print('Oops. Something happened when calling CoolProp for state ' + self.name)
        self._T = CP.PropsSI('T',prop1,value1,prop2,value2,fluid)
        self._p = CP.PropsSI('P',prop1,value1,prop2,value2,fluid)
        rho = CP.PropsSI('D',prop1,value1,prop2,value2,fluid)
        self._d = rho
        self._v = 1 / rho
        self._u = CP.PropsSI('U',prop1,value1,prop2,value2,fluid)
        self._h = CP.PropsSI('H',prop1,value1,prop2,value2,fluid)
        self._s = CP.PropsSI('S',prop1,value1,prop2,value2,fluid)
        self._x = CP.PropsSI('Q',prop1,value1,prop2,value2,fluid)
        self._vel = velocity
        self._z = z     #height

    @property
    def T(self):
        return self._T

    @property
    def p(self):
        return self._p

    @property
    def v(self):
        return self._v

    @property
    def d(self):
        return self._d

    @property
    def u(self):
        return self._u

    @property
    def h(self):
        return self._h

    @property
    def s(self):
        return self._s

    @property
    def x(self):
        return self._x

    @property
    def vel(self):
        return self._vel

    @property
    def z(self):
        return self._z

    @property
    def name(self):
        return self._name

    def __str__():
        return self._name

class Process(object):
    '''A class that defines values for a process based on a
    state in and a state out. '''

    def __init__(self,state_in,state_out,heat=0,work=0,name=""):
        self.heat = heat
        self.work = work
        self._in = state_in  # these are of class State
        self._out = state_out
        self.name = name

# class Cycle(Process):
#     '''A class that defines values for a thermodynamic power cycle'''

#     def __init__(self,)







