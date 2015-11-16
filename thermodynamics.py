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

    def flow_exergy(self):
        self.ef = self.h-self.cycle.dead.h - self.cycle.dead.T*(self.s-self.cycle.dead.s)
        return

    def __str__():
        return self._name

    def __repr__(self):
        return self.name

    def __init__(self,cycle,name=""):

        self.cycle = cycle  # should be an object of class cycle

        self.fluid = cycle.fluid

        # note that 'x' and 'Q' both represent two-phase quality
        # set property name if specified
        self.name = name # 1, 2, 2s, 3, 4, 4s, 4b, etc.

        # add state to cycle's state list if not dead state
        if self.cycle:
            self.cycle.add_state(self)

        # set state properties
        self.T = None
        self.p = None
        self.d = None
        self.v = 1 / self.d
        self.u = None
        self.h = None
        self.s = None
        self.ef = 0
        self.x = None
        return

class Process(object):
    '''A class that defines values for a process based on a
    state in and a state out. '''

    def exergy_destroyed(self):
        return self.cycle.dead.T*(self.state_out.s-self.state_in.s) # exergy destroyed

    def __repr__(self):
        return self.name

    def __init__(self,cycle,state_in,state_out,heat=0,work=0,name="",intrev=False):
        self.cycle = cycle # this should be an object of class Cycle
        self.heat = heat
        self.work = work
        self.in_ = state_in  # these are objects of class State
        self.out = state_out
        self.name = name

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

        return

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

    def __repr__(self):
        return self.name

    def add_proc(self,process):
        self.proc_list.append(process)

    def get_procs(self):
        return self.proc_list

    def add_state(self,state):
        self.state_list.append(state)

    def get_states(self):
        return self.state_list

    def compute_cycle_results(self):
        ''' Compute and store rankine cycle
          wnet        = net work output
          qnet        = net heat input
          thermal_eff = thermal efficiency
          bwr         = back work ratio
          ex_eff      = exergetic efficiency
          '''
        return

    def __init__(self,fluid,**kwargs):
        # unpack keyword arguments
        dead = kwargs.pop('dead',None)
        name = kwargs.pop('name',"")
        mdot = kwargs.pop('mdot',1)  #default is 1 kg/s

        # set fluid property
        self.fluid = fluid
        # set dead state
        if not dead:
            dead = State(None,fluid,'Dead State')
            dead.T = 15+273  #K
            dead.p = 101325  #Pa
            dead.h = CP.Props('H','T',dead.T,'P',dead.P,dead.fluid)
            dead.s = CP.Props('S','T',dead.T,'P',dead.P,dead.fluid)
        self.dead = dead
        # set cycle name
        self.name = name
        # initialize process list
        self.proc_list = []
        # initialize state list
        self.state_list = []
        # set mass flow rate
        self.mdot = mdot # in kg/s

        # initialize cycle results
        self.wnet = None
        self.qnet = None
        self.en_eff = None
        self.ex_eff = 0
        self.bwr = None

        return

class Geotherm(object):
    '''This class describes the geothermal heating cycle of the power plant'''

    # should probably make this a subclass of Cycle later, and make a new
    # class called Rankine a subclass of Cycle also.

    def add_proc(self,process):
        self.proc_list.append(process)

    def get_procs(self):
        return self.proc_list

    def add_state(self,state):
        self.state_list.append(state)

    def get_states(self):
        return self.state_list

    def __init__(self,**kwargs):
        ''' Create an instance of a geothermal heating cycle object
        arguments:
            brine (optional) = which fluid to use for the brine in the geothermal plant
            mdot (optional) = mass flow rate of brine fluid
            name (optional) = string used to describe the geothermal cycle
            t_ground (optional) = underground temperature that brine will be raised
            p_ground (optional) = underground pressure of brine
            dead (optional) = dead state of brine
            to before entering the steam generator of the organic Rankine cycle.'''

        # get optional arguments from kwargs

        # default brine fluid is 20% NaCl solution with water.
        # See http://www.coolprop.org/fluid_properties/Incompressibles.html for more
        # information on available brines
        self.brine = "INCOMP::" + kwargs.pop('brine','ZM[.01]')  # ZM -> Zitrec M, Ethylene Glycol
        # use MNA for sodium chloride aqueous mix
        # default mass flow rate is 1 kg/s
        self.mdot = kwargs.pop('mdot',1)
        # default name is 'Geothermal'
        self.name = kwargs.pop('name','Geothermal')

        # initialize process list
        self.proc_list = []
        # initialize state list
        self.state_list = []

        # find brine dead state
        self.dead = kwargs.pop('dead',None)
        if not self.dead:
            dead = State(None,self.brine,'Brine Dead State')
            dead.h = 61.05 * 1000 # J/kg
            dead.s = 0.2205 * 1000 # J/kg.K
            dead.T = 15 + 273 # K
            self.dead = dead

        # create initial brine state
        g1 = State(self,self.brine,'Brine In')
        g1.s = 1.492 * 1000 # J/kg.K
        g1.h = 491.6 * 1000 # J/kg
        g1.T = 120 + 273.15 # K
        g1.flow_exergy()

        # state in
        self.in_ = g1

        #state out
        self.out = None  # default

        return

class Plant(object):
    '''This class describes the whole geothermal power plant, including both
    the geothermal heat source and the organic Rankine cycle power generation '''

    def calc_plant_effs(self):
        '''Once the geothermal and rankine cycles have been defined for the
        plant, calcuate the overall plant energetic and exergetic
        efficiencies'''
        # calculate plant energetic efficiency
        q_avail = self.geo.mdot * (self.geo.in_.h - self.geo.dead.h)
        en_eff = self.rank.wnet / q_avail
        # calculate plant exergetic efficiency
        ex_eff = self.rank.wnet / (self.geo.mdot * self.geo.in_.ef)
        return (en_eff, ex_eff)

    def __init__(self,rankine,geotherm):
        ''' Create an instance of a geothermal Plant object
        arguments:
            rankine (required) = an instance of object Cycle/Rankine for the organic Rankine cycle used in the plant
            geotherm (required) = the geothermal cycle used in the plant
            '''
        self.rank = rankine
        self.geo = geotherm

        # calculate and store plant efficiencies
        (en_eff, ex_eff) = self.calc_plant_effs()
        self.en_eff = en_eff   # plant energetic efficiency
        self.ex_eff = ex_eff   # plant exergetic efficiency
        return
