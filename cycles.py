
from .components import Boiler, Turbine, Condenser, Pump, connect_flow
from .thermodynamics import Cycle, State

def ideal_rankine(**kwargs):
    fluid = kwargs.get('fluid','Water')
    p_hi = kwargs.get('p_hi',None) * 1e6  # MPa
    p_lo = kwargs.get('p_lo',None) * 1e6 # MPa
    turb_eff = kwargs.get('turb_eff',1.0)   
    pump_eff = kwargs.get('pump_eff',1.0)
    T_0 = kwargs.get('T_0', 25) + 273.15 # deg C
    p_0 = kwargs.get('p_0', 101.3) * 1e3 # kPa

    # Convert

    dead = State(p=p_0, T=T_0, fluid=fluid)

    cycle = Cycle(fluid=fluid, dead=dead)

    turb = Turbine(p_hi=p_hi, p_lo=p_lo, eff=turb_eff, fluid=fluid, cycle=cycle)
    turb.compute()
    
    cond = Condenser(inflow=turb.outflow, p=p_lo, fluid=fluid, cycle=cycle)
    cond.compute()
    
    pump = Pump(inflow=cond.outflow, p_hi=p_hi, eff=pump_eff, fluid=fluid, cycle=cycle)
    pump.compute()  
    
    boil = Boiler(inflow=pump.outflow, outflow=turb.inflow, fluid=fluid, cycle=cycle)
    boil.compute()

    cycle.flow_exergy()

    # Define cycle properties
    cycle.wnet = turb.work + pump.work
    cycle.qnet = boil.heat + cond.heat
    cycle.en_eff = cycle.wnet / boil.heat
    cycle.bwr = -pump.work / turb.work
    cycle.ex_eff = cycle.wnet / boil.delta_ef  # cycle exergetic eff

    return cycle    


def rankine_superheated(**kwargs):
    fluid = kwargs.get('fluid','Water')
    p_hi = kwargs.get('p_hi',None) * 1e6  # MPa
    p_lo = kwargs.get('p_lo',None) * 1e6 # MPa
    T_hi = kwargs.get('T_hi',None) + 273.15 # deg C
    turb_eff = kwargs.get('turb_eff',1.0)   
    pump_eff = kwargs.get('pump_eff',1.0)
    T_0 = kwargs.get('T_0', 25) + 273.15 # deg C
    p_0 = kwargs.get('p_0', 101.3) * 1e3 # kPa

    # Convert

    dead = State(p=p_0, T=T_0, fluid=fluid)

    cycle = Cycle(fluid=fluid, dead=dead)

    turb = Turbine(p_hi=p_hi, p_lo=p_lo, T_hi=T_hi, eff=turb_eff, fluid=fluid, cycle=cycle)
    turb.compute()
    
    cond = Condenser(inflow=turb.outflow, p=p_lo, fluid=fluid, cycle=cycle)
    cond.compute()
    
    pump = Pump(inflow=cond.outflow, p_hi=p_hi, eff=pump_eff, fluid=fluid, cycle=cycle)
    pump.compute()  
    
    boil = Boiler(inflow=pump.outflow, outflow=turb.inflow, fluid=fluid, cycle=cycle)
    boil.compute()

    cycle.flow_exergy()

    # Define cycle properties
    cycle.wnet = turb.work + pump.work
    cycle.qnet = boil.heat + cond.heat
    cycle.en_eff = cycle.wnet / boil.heat
    cycle.bwr = -pump.work / turb.work
    cycle.ex_eff = cycle.wnet / boil.delta_ef  # cycle exergetic eff

    return cycle    
