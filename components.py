# Components

# Model the Rankine Cycle with Geothermal Brine Heat Source

from __future__ import print_function
from thermodynamics import State  # custom thermo state class in thermodynamics.py
import CoolProp.CoolProp as CP

######################################

class Component():
    inflow = State()  # input state
    outflow = State()  # output state
    constant = []         # constant values

class ConnectFlow(Component):
    # Set inflow states to outflow states
    pass

# class Valve(Component):
#     name = 'Valve'
#     constant.append('h')  # constant enthalpy

class Pump(Component):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name','Pump')
        self.eff = kwargs.get('eff',1.0)
        self.fluid = kwargs.get('fluid','Water')
        self.p_hi = kwargs.get('p_hi',None)
        self.p_lo = kwargs.get('p_lo',None)
        self.T_hi = kwargs.get('T_hi',None)
        self.work = kwargs.get('work',None)
        self.heat = 0.0
        self.cycle = kwargs.get('cycle',None)
        self.inflow = kwargs.get('inflow',None)
        self.outflow = kwargs.get('outflow',None)
        self.delta_ef = 0
        
         # add process to cycle's process list
        if self.cycle:
            self.cycle.add_proc(self)

        # default these exergy process values to zero. Compute them ad-hoc
        # and then add them to the object attributes.
        self.ex_d = 0      # exergy destroyed
        self.ex_in = 0     # exergy input
        self.ex_out = 0    # exergy output
        self.ex_eff = 1.0  # exergetic efficiency
        self.ex_bal = 0    # exergy balance = ex_in - ex_out - delta_ef - ex_d = 0
        return

    def compute(self):
        if not self.inflow:
            # then assume inflow is sat liquid
            self.inflow = State(name='inflow', fluid=self.fluid)
            self.inflow.fix('p',self.p_lo,'x',0.0)
            
        if not self.outflow:
            self.outflow = State(name='outflow', fluid=self.fluid)
            self.outflow.p = self.p_hi
            
        # Get intrev work 
        work_intrev = -self.inflow.v * (self.outflow.p - self.inflow.p)
        self.work = 1/self.eff * work_intrev
        
        self.outflow.fix('p',self.p_hi,'h',self.inflow.h-self.work)

        # change in flow exergy
        if self.cycle:
            self.delta_ef = (self.outflow.h - self.inflow.h) - self.cycle.dead.T * (self.outflow.s - self.inflow.s)
    
class Turbine(Component):
    def __init__(self, eff=1.0, name='Turbine', **kwargs):
        self.name = name
        self.eff = eff
        self.fluid = kwargs.get('fluid','Water')
        self.p_hi = kwargs.get('p_hi',None)
        self.p_lo = kwargs.get('p_lo',None)
        self.T_hi = kwargs.get('T_hi',None)
        self.work = kwargs.get('work',None)
        self.heat = 0.0
        self.cycle = kwargs.get('cycle',None)
        self.inflow = kwargs.get('inflow',None)
        self.outflow = kwargs.get('outflow',None)
        self.delta_ef = 0
        
         # add process to cycle's process list
        if self.cycle:
            self.cycle.add_proc(self)

        # default these exergy process values to zero. Compute them ad-hoc
        # and then add them to the object attributes.
        self.ex_d = 0      # exergy destroyed
        self.ex_in = 0     # exergy input
        self.ex_out = 0    # exergy output
        self.ex_eff = 1.0  # exergetic efficiency
        self.ex_bal = 0    # exergy balance = ex_in - ex_out - delta_ef - ex_d = 0
        return

    def compute(self):
        if not self.inflow:
            self.inflow = State(name='inflow', fluid=self.fluid)
            if not self.T_hi:
                # then assume inflow is sat vapor
                self.inflow.fix('p',self.p_hi,'x',1.0)
            else:
                self.inflow.fix('p',self.p_hi,'T',self.T_hi)
        
        if not self.outflow:
            self.outflow = State(name='outflow', fluid=self.fluid)
            self.outflow.p = self.p_lo

        isen = State(name='isen_2s', fluid=self.fluid, s=self.inflow.s)
        h_in = self.inflow.h
        s_in = self.inflow.s
        if self.outflow.p:
            p_out = self.outflow.p
        else:
            p_out = self.p_lo
        isen.fix('s',s_in,'p',p_out)
        # compute exit enthalpy and state
        h_out = self.eff * (isen.h - h_in) + h_in  #with an irreversible turbine
        self.outflow.fix('h',h_out,'p',p_out)
        # compute work per unit mass
        self.work = h_in - h_out
        # change in flow exergy
        if self.cycle:
            self.delta_ef = (self.outflow.h - self.inflow.h) - self.cycle.dead.T * (self.outflow.s - self.inflow.s)
        
class HeatExchanger(Component):
    name = 'Heat Exchanger'
#     constant.append('p')  # constant pressure

class Boiler(HeatExchanger):
    def __init__(self, **kwargs):
        self.name =  kwargs.get('name','Boiler')
        self.fluid = kwargs.get('fluid','Water')
        self.p = kwargs.get('p',None)
        self.T_hi = kwargs.get('T_hi',None)
        self.T_lo = kwargs.get('T_lo',None)
        self.work = 0.0
        self.heat = kwargs.get('heat',None)
        self.cycle = kwargs.get('cycle',None)
        self.inflow = kwargs.get('inflow',None)
        self.outflow = kwargs.get('outflow',None)
        self.delta_ef = 0
        
         # add process to cycle's process list
        if self.cycle:
            self.cycle.add_proc(self)

        # default these exergy process values to zero. Compute them ad-hoc
        # and then add them to the object attributes.
        self.ex_d = 0      # exergy destroyed
        self.ex_in = 0     # exergy input
        self.ex_out = 0    # exergy output
        self.ex_eff = 1.0  # exergetic efficiency
        self.ex_bal = 0    # exergy balance = ex_in - ex_out - delta_ef - ex_d = 0
        return

    def compute(self):
        if not self.inflow:
            self.inflow = State(name='inflow', fluid=self.fluid)
            if not self.T_lo:
                # then assume inflow is sat liquid
                self.inflow.fix('p',self.p,'x',0.0)
            else:
                self.inflow.fix('p',self.p,'T',self.T_lo)
        
        if not self.outflow:
            self.outflow = State(name='outflow', fluid=self.fluid)
            if not self.T_hi:
                # assume outflow is sat vapor
                self.outflow.fix('x',1.0,'p',self.p)
            else:
                self.outflow.fix('T',self.T_hi,'p',self.p)

        # compute exit enthalpy and state
        print(self.outflow.h)
        print(self.inflow.h)
        self.heat = self.outflow.h - self.inflow.h
    
        # change in flow exergy
        if self.cycle:
            self.delta_ef = (self.outflow.h - self.inflow.h) - self.cycle.dead.T * (self.outflow.s - self.inflow.s)

class Condenser(HeatExchanger):
    def __init__(self, **kwargs):
        self.name =  kwargs.get('name','Condenser')
        self.fluid = kwargs.get('fluid','Water')
        self.p = kwargs.get('p',None)
        self.T_hi = kwargs.get('T_hi',None)
        self.T_lo = kwargs.get('T_lo',None)
        self.work = 0.0
        self.heat = kwargs.get('heat',None)
        self.cycle = kwargs.get('cycle',None)
        self.inflow = kwargs.get('inflow',None)
        self.outflow = kwargs.get('outflow',None)
        self.delta_ef = 0
        
         # add process to cycle's process list
        if self.cycle:
            self.cycle.add_proc(self)

        # default these exergy process values to zero. Compute them ad-hoc
        # and then add them to the object attributes.
        self.ex_d = 0      # exergy destroyed
        self.ex_in = 0     # exergy input
        self.ex_out = 0    # exergy output
        self.ex_eff = 1.0  # exergetic efficiency
        self.ex_bal = 0    # exergy balance = ex_in - ex_out - delta_ef - ex_d = 0
        return

    def compute(self):
        # get isentropic state
        
        if not self.inflow:
            self.inflow = State(name='inflow', fluid=self.fluid)
            if not self.T_hi:
                # then assume inflow is sat vapor
                self.inflow.fix('p',self.p,'x',1.0)
            else:
                self.inflow.fix('p',self.p,'T',self.T_hi)
        
        if not self.outflow:
            self.outflow = State(name='outflow', fluid=self.fluid)
            # assume outflow is sat liquid
            self.outflow.fix('x',0.0,'p',self.p)

        # # compute exit enthalpy and state
        # self.outflow.fix('x',0.0,'p',self.p)
        # compute work per unit mass
        self.heat = self.outflow.h - self.inflow.h
    
        # change in flow exergy
        if self.cycle:
            self.delta_ef = (self.outflow.h - self.inflow.h) - self.cycle.dead.T * (self.outflow.s - self.inflow.s)
    


class Evaporator(HeatExchanger):
    name = 'Evaporator'
