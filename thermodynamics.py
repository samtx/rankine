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
#         # convert MPa to Pa for CoolProp
#         elif prop == 'P':
#             value = value * 10**6
        # convert kJ to J for CoopProp
#         elif prop in ['H','U','S']:
#             value = value * 10
        return prop,value

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

#     @property
#     def phase(self):
#         return self._phase

    @property
    def name(self):
        return self._name

    @property
    def cycle(self):
        return self._cycle

    def __str__():
        return self._name

    def __repr__(self):
        return self.name

    def __init__(
        self,
        cycle,fluid,
        prop1,value1,prop2,value2,
        name="",
        velocity=0,z=0):

        self._cycle = cycle  # should be an object of class cycle

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

#         # determine phase of fluid and add description
#         if self.x == 1:
#             phase = 'Sat Vapor'
#         elif self.x == 0:
#             phase = 'Sat Liquid'
#         elif self.p < CP.PropsSI('P','P',self.p,'Q',0,fluid):
#             phase = 'Sub-Cooled Liq'
#         elif self.p > CP.PropsSI('P','P',self.p,'Q',1,fluid):
#             phase = 'Superheated'
#         else:
#             phase = ""
#         self._phase = phase



class Process(object):
    '''A class that defines values for a process based on a
    state in and a state out. '''

    @property
    def heat(self):
        return self._heat

    @property
    def work(self):
        return self._work

    @property
    def state_in(self):
        return self._state_in

    @property
    def in_(self):
        return self._state_in

    @property
    def state_out(self):
        return self._state_out

    @property
    def out(self):
        return self._state_out

    @property
    def ex_in(self):
        return self._ex_in

    @property
    def ex_out(self):
        return self._ex_out

    @property
    def ex_d(self):
        return self._ex_d

    @property
    def cycle(self):
        return self._cycle

    def __repr__(self):
        return self.name

    def __init__(self,cycle,state_in,state_out,heat=0,work=0,name=""):
        self._cycle = cycle # this should be an object of class Cycle
        self._heat = heat
        self._work = work
        self._state_in = state_in  # these are objects of class State
        self._state_out = state_out
        self.name = name
        self._ex_in = state_in.ef       # flow exergy in
        self._ex_out = state_out.ef     # flow exergy out
        self._ex_d = cycle.dead.T*(self.state_out.s-self.state_in.s) # exergy destroyed


class Cycle(object):
     '''A class that defines values for a thermodynamic power cycle
     keyword arguments:
         p_hi = high pressure of cycle in MPa
         p_lo = low pressure of cycle in MPa
         T_hi = high temperature of cycle in Celcius
         T_lo = low temperature of cycle in Celcius
         dead = object of class State that represents the dead state pressure and temperature
         name = string to represent the cycle
         mdot = mass flow rate in kg/s

     note: the user must enter at least one "high" value and one "low" value for either temperature, pressure, or mixed.
     Entering the dead state is optional but will default to T = 15 degC, P = 0.101325 MPa (1 atm) for the given fluid'''

    @propety
    def prop_hi(self):
        # return the dictionary
        return self._cyc_prop_hi

    @propety
    def prop_lo(self):
        # return the dictionary
        return self._cyc_prop_lo

    @property
    def fluid(self):
        return self._fluid

    @property
    def dead(self):
        #return dead state
        return self._dead

    def __repr__(self):
        return self.name

    def add_proc(self,process):
        self._proc_list.append(process)

    def get_procs(self):
        return self._proc_list
    
    @property
    def mdot(self):
        return self._mdot

    def __init__(self,fluid,**kwargs):
        # unpack keyword arguments
        p_hi = None
        p_lo = None
        T_hi = None
        T_lo = None
        dead = None
        name = ""
        mdot = None
        for key, value in kwargs.iteritems():
            if key.lower() = 'p_hi':
                p_hi = value
            elif key.lower() = 'p_lo':
                p_lo = value
            elif key.lower() = 't_hi'
                T_hi = value
            elif key.lower() = 't_lo'
                T_lo = value
            elif key.lower() = 'dead'
                dead = value
            elif key.lower() = 'name'
                name = value
            elif key.lower() = 'mdot'
                mdot = value
        # check to see if at least one high and one low value are entered
        if not((p_hi or T_hi) and (p_lo or T_lo)):
            raise ValueError('Must enter one of each group (p_hi or T_h) and (p_lo and T_lo)')
        # set low and high cycle properties
        # high property
        if T_hi:
            cyc_prop_hi = {'T':T_hi + 273.15} # temperature must be saved in K
        elif p_hi:
            cyc_prop_hi = {'P':p_hi*10**6}  # pressure must be saved in Pa
        # low property
        if T_lo:
            cyc_prop_lo = {'T':T_lo + 273.15} # temperature must be saved in K
        elif p_lo:
            cyc_prop_lo = {'P':p_lo*10**6}  # pressure must be saved in Pa
        self._cyc_prop_hi = cyc_prop_hi
        self._cyc_prop_lo = cyc_prop_lo
        # set fluid property
        self._fluid = fluid
        # set dead state
        if not dead:
            dead = State(None,fluid,'T',15+273.15,'P',101325,'Dead State')
        self._dead = dead
        # set cycle name
        self.name = name
        # initialize process list
        self._proc_list = []
        # set mass flow rate
        self._mdot = mdot # in kg/s











