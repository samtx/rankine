
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

def rankine_reheated(**kwargs):
    fluid = kwargs.get('fluid','Water')
    p_hi = kwargs.get('p_hi',None) * 1e6 # MPa
    p_mid = kwargs.get('p_mid',None) * 1e6 # MPa
    p_lo = kwargs.get('p_lo',None) * 1e6 # MPa
    T_hi = kwargs.get('T_hi',None) + 273.15 # deg C
    T_mid = kwargs.get('T_mid',None) + 273.15 # deg C
    hp_turb_eff = kwargs.get('hp_turb_eff',1.0)   
    lp_turb_eff = kwargs.get('lp_turb_eff',1.0)   
    pump_eff = kwargs.get('pump_eff',1.0)
    T_0 = kwargs.get('T_0', 25) + 273.15 # deg C
    p_0 = kwargs.get('p_0', 101.3) * 1e3 # kPa

    dead = State(p=p_0, T=T_0, fluid=fluid)
    cycle = Cycle(fluid=fluid, dead=dead)

    # high pressure turbine
    hp_turb = Turbine(p_hi=p_hi, p_lo=p_mid, T_hi=T_hi, eff=hp_turb_eff, name='HP Turb', fluid=fluid, cycle=cycle)
    hp_turb.compute()
    lp_boil = Boiler(inflow=hp_turb.outflow, p=p_mid, T_hi=T_mid, name='LP Boil', fluid=fluid, cycle=cycle)
    lp_boil.compute()
    lp_turb = Turbine(p_hi=p_mid, p_lo=p_lo, T_hi=T_mid, eff=lp_turb_eff, name='LP Turb', fluid=fluid, cycle=cycle)
    lp_turb.compute()
    cond = Condenser(inflow=lp_turb.outflow, p=p_lo, fluid=fluid, cycle=cycle)
    cond.compute()
    pump = Pump(inflow=cond.outflow, p_hi=p_hi, eff=pump_eff, fluid=fluid, cycle=cycle)
    pump.compute()  
    hp_boil = Boiler(inflow=pump.outflow, outflow=hp_turb.inflow, name='HP Boil', fluid=fluid, cycle=cycle)
    hp_boil.compute()
    cycle.flow_exergy()

    # Define cycle properties
    cycle.wnet = hp_turb.work + lp_turb.work + pump.work
    cycle.qnet = hp_boil.heat +lp_boil.heat + cond.heat
    cycle.en_eff = cycle.wnet / (hp_boil.heat +lp_boil.heat)
    cycle.bwr = -pump.work / (hp_turb.work + lp_turb.work)
    cycle.ex_eff = cycle.wnet / (hp_boil.delta_ef + lp_boil.delta_ef)  # cycle exergetic eff

    return cycle   
    
    
