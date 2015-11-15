# Create Python class for a thermodynamic state

import CoolProp.CoolProp as CP  #must have CoolProp library installed

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
        return prop,value

    # need to add kinetic and potential energy values
    def flow_exergy(self):
        if self.cycle:
            return self.h-self.cycle.dead.h - self.cycle.dead.T*(self.s-self.cycle.dead.s)
        else:       # then the state in question is the dead state. Don't find flow exergy
            return 0


    # flow exergy
    @property
    def ef(self):
        return self._ef

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
        self._ef = self.flow_exergy()
        self._vel = velocity
        self._z = z     #height

        # add state to cycle's state list if not dead state
        if self.cycle:
            self.cycle.add_state(self)
            

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

    def calc_exergy(self,state_in=None,state_out=None,env_vars=[]):
        pass
#         '''Calculate the exergy in, exergy out, and exergy destroyed for each process'''
#         # if heat = 0
#         if self.heat == 0:
#             if self.
#         # find difference in flow exergy
#         (state_in.ef - state_out.ef)



        pass
#         ''' Calculate the exergy in, exergy out, and exergy destruction of the process'''
#         To = env_vars["To"] # environment temperature in Kelvin
#         po = env_vars["po"] # environment pressure in Pa

    def exergy_destroyed(self):
        return self.cycle.dead.T*(self.state_out.s-self.state_in.s) # exergy destroyed

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

    # change in flow exergy
    @property
    def delta_ef(self):
        return self._delta_ef

#     @property
#     def ex_d(self):
#         return self._ex_d

#     @property
#     def intrev(self):
#         return self._intrev

    @property
    def cycle(self):
        return self._cycle

    def __repr__(self):
        return self.name

    def __init__(self,cycle,state_in,state_out,heat=0,work=0,name="",intrev=False):
        self._cycle = cycle # this should be an object of class Cycle
        self._heat = heat
        self._work = work
        self._state_in = state_in  # these are objects of class State
        self._state_out = state_out
        self.name = name

        exergy = self.calc_exergy()
        # change in flow exergy
        self._delta_ef = (self.out.h - self.in_.h) - self.cycle.dead.T * (self.out.s - self.in_.s)
        # default these exergy process values to zero. Compute them ad-hoc
        # and then add them to the object attributes.
        self.ex_d = 0      # exergy destroyed
        self.ex_in = 0     # exergy input
        self.ex_out = 0    # exergy output
        self.ex_eff = 1.0  # exergetic efficiency

        # is the process internally reversible?
        self.intrev = intrev  # True/False

        # add process to cycle's process list
        if self.cycle:
            self._cycle.add_proc(self)
 

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

    @property
    def prop_hi(self):
        # return the dictionary
        return self._cyc_prop_hi

    @property
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

    def add_state(self,state):
        self._state_list.append(state)

    def get_states(self):
        return self._state_list

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
        mdot = 1
        for key, value in kwargs.iteritems():
            if key.lower() == 'p_hi':
                p_hi = value
            elif key.lower() == 'p_lo':
                p_lo = value
            elif key.lower() == 't_hi':
                T_hi = value
            elif key.lower() == 't_lo':
                T_lo = value
            elif key.lower() == 'dead':
                dead = value
            elif key.lower() == 'name':
                name = value
            elif key.lower() == 'mdot':
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
            dead = State(None,fluid,'T',15+273,'P',101325,'Dead State')
        self._dead = dead
        # set cycle name
        self.name = name
        # initialize process list
        self._proc_list = []
        # initialize state list
        self._state_list = []
        # set mass flow rate
        self._mdot = mdot # in kg/s

class Geotherm(object):
    '''This class describes the geothermal heating cycle of the power plant'''
    
    @property
    def 
    
    def __init__(self,**kwargs):
        ''' Create an instance of a geothermal heating cycle object
        arguments: 
            brine (optional) = which fluid to use for the brine in the geothermal plant
            mdot (optional) = mass flow rate of brine fluid        
            name (optional) = string used to describe the geothermal cycle
            t_ground (optional) = underground temperature that brine will be raised
            p_ground (optional) = underground pressure of brine
            to before entering the steam generator of the organic Rankine cycle.'''

        # get optional arguments from kwargs
        
        # default brine fluid is 20% NaCl solution with water. 
        # See http://www.coolprop.org/v4/FluidInformation.html for more 
        # information on available brines
        self._brine = kwargs.pop('brine','MNA-20')  
        # default mass flow rate is 1 kg/s
        self._mdot = kwargs.pop('mdot',1)
        # default name is 'Geothermal'
        self._name = kwargs.pop('name','Geothermal')

        # initialize process list
        self._proc_list = []
        # initialize state list
        self._state_list = []
        
        # create initial brine state
        # default ground temperature is 120 deg C
        t = kwargs.pop('t_ground',120)
        # default ground pressure is 0.5 MPa (5 bar)
        p = kwargs.pop('p_ground',0.5)
        g1 = State(self,brine,'T',t+273,'P',p*10**6,'Brine In')
        
        
        
class Plant(object):
    '''This class describes the whole geothermal power plant, including both
    the geothermal heat source and the organic Rankine cycle power generation '''
    
    def __init__(self,cycle,geotherm,**kwargs):
        ''' Create an instance of a geothermal Plant object
        arguments: 
            cycle (required) = an instance of object Cycle for the organic Rankine cycle used in the plant
            brine (optional) = which fluid to use for the brine in the geothermal plant
            mdot (optional) = mass flow rate of brine fluid
            
            
            '''
        self._cycle = cycle






