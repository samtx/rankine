# Model the Rankine Cycle with Geothermal Brine Heat Source

from __future__ import print_function
import thermodynamics as thermo  # custom thermo state class in thermodynamics.py
import sys
import CoolProp.CoolProp as CP
from numbers import Number
from print_rankine import print_output_to_screen

######################################

def main():

    # The list of pure and pseudo-pure fluids that CoolProp supports can
    # be found here:
    # http://www.coolprop.org/fluid_properties/PurePseudoPure.html#list-of-fluids
    
    #create dictionary of properties
    props = {}
    props["fluid"] = 'n-Butane'
    props["p_hi"] = 3.5  #MPa
    props["p_lo"] = 0.3 #MPa
    props["turb_eff"] = 0.8
    props["pump_eff"] = 0.75
    props['cool_eff'] = .25 #cooling efficiency
    props['superheat'] =  False # should we allow for superheating?
    props['in_kW'] = False # print results in kW instead of kJ/kg?
    props['cycle_mdot'] = 3.14   # mass flow rate of rankine cycle working fluid in kg/s

    # begin computing processess for rankine cycle
    rankine = compute_cycle(props)

    # compute plant efficiencies
    plant = compute_plant(rankine,props)

    # print output to screen
    print_output_to_screen(plant,props)

    return

def compute_cycle(props):
    fluid = props.get('fluid',None)
    p_hi = props.get('p_hi',None)
    p_lo = props.get('p_lo',None)
    if p_hi: p_hi = p_hi * 10**6  #convert MPa to Pa
    if p_lo: p_lo = p_lo * 10**6  #convert MPa to Pa
    t_hi = props.get('t_hi',None)
    t_lo = props.get('t_lo',None)
    if t_hi: t_hi += 273.15  #convert deg C to K
    if t_lo: t_lo += 273.15  #convert deg C to K
    turb_eff = props.get('turb_eff',1.0)
    pump_eff = props.get('pump_eff',1.0)
    superheat = props.get('superheat',False)
    mdot = props.get('cycle_mdot',1.0)
    units = props.get('units','si')

    # set dead state
    dead = thermo.State(name='Dead State',fluid=fluid)
    print('Fluid={}'.format(fluid))
    dead.fix('T',15+273.0, 'p', 101325.0)
    dead.ef = 0

    # initialize cycle
    cyc = thermo.Cycle(fluid,name='Rankine',mdot=mdot,dead=dead)

    # check to see if enough pressures and temperatures were entered
    if superheat and not(
        p_hi and
        isinstance(t_hi, Number)):
        print('\nERROR\nIf you are superheating the fluid, specify both a high pressure and high temperature for the cycle')
        sys.exit()
    # check to see if one high and one low value were entered
    elif not superheat:
        if not (p_hi or isinstance(t_hi,Number)):
            print('\nERROR\nYou must enter at least one high value (temperature or pressure) for the cycle')
            sys.exit()
        elif not (p_lo or isinstance(t_lo,Number)):
            print('\nERROR\nYou must enter one low value (temperature or pressure) for the cycle.')
            sys.exit()

    # use pressures instead of temperatures when accessing CoolProp. So we
    # want to find the saturation pressures for the given temperatures and
    # fluid.
    if t_hi and (not superheat):
        p_hi = CP.PropsSI('P','T',t_hi,'Q',0,fluid)
    elif (not t_hi) and (not superheat):
        t_hi = CP.PropsSI('T','P',p_hi,'Q',0,fluid)
    if t_lo:
        p_lo = CP.PropsSI('P','T',t_lo,'Q',0,fluid)
    else:
        t_lo = CP.PropsSI('T','P',p_lo,'Q',0,fluid)

    # Define States
    # State 1, saturated vapor at high temperature
    st1 = thermo.State(cycle=cyc,name='1')
    h_sat = CP.PropsSI('H','P',p_hi,'Q',1,fluid) #enthalpy at sat vapor
    if superheat:
        st1.fix('p',p_hi,'T',t_hi)
    else:
        st1.fix('p',p_hi,'x',1.0)
    # st1.flow_exergy()

    # State 2s, two-phase at low temperature with same entropy as state 1
    st2s = thermo.State(cycle=cyc,name='2s')
    st2s.fix('p', p_lo, 's', st1.s)
    # st2s.flow_exergy()

    # State 2, two-phase at low pressure determined by turbine efficiency
    st2 = thermo.State(cycle=cyc,name='2')
    # if turb_eff = 1, then just copy values from state 2s
    if turb_eff == 1:
        st2.fix('p',p_lo,'s',st2s.s)
    else:
        h2 = turb_eff * (st2s.h - st1.h) + st1.h  #with an irreversible turbine
        st2.fix('h',h2,'p',p_lo)
    # st2.flow_exergy()

#     #print('state 2 quality: ',st2.x)
#     if st2.x > 1 and (not superheat):
#         print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency \nExiting...')
#         sys.exit()

    # State 2b, saturated vapor at low pressure
    # --- if necessary: state 2 is superheated and we need the sat vapor state for graphing purposes
    h2b = CP.PropsSI('H','P',p_lo,'Q',1.0,fluid)  #sat vapor enthalpy
    if st2.h > h2b:
        # then state 2 is superheated. Find state 2b
        st2b = thermo.State(name='2b',cycle=cyc)
        st2b.fix('p',p_lo,'x',1.0)
        # st2b.flow_exergy() 
    
    # State 3, saturated liquid at low pressure
    st3 = thermo.State(name='3',cycle=cyc)
    st3.fix('p',p_lo,'x',0.0)
    # st3.flow_exergy()

    # States 4 and 4s, subcooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for irreversible pump operation
    # print('st3.v={:.4e}'.format(st3.v),'st3.d={:.2f}'.format(st3.d))
    wps = -st3.v * (st1.p - st3.p)
    wp = 1/pump_eff * wps
    st4s = thermo.State(name='4s', cycle=cyc)
    st4s.fix('s',st3.s,'p',p_hi)
    # st4s.flow_exergy()
    # State 4
    st4 = thermo.State(name='4', cycle=cyc)
    # if pump_eff = 1, then just copy values from state 4s
    if pump_eff == 1:
        st4.fix('h',st3.h-wps,'p',p_hi)
    else:
        st4.fix('h',st3.h-wp,'p',p_hi)
        #   it appears that CoolProp is pulling properties for Temperature and entropy
        #   for state 4 that are slightly lower than state 4s. These values should
        #   be higher than those at state 4s.
        #   Add logic to add a 0.1% increase in both values if they are lower.
        if st4.T < st4s.T:
            st4.T = st4s.T * 1.001  # add 0.1% increase
        st4.s = CP.PropsSI('S','P',p_hi,'H',st4.h,fluid)
        if st4.s < st4s.s:
            st4.s = st4s.s * 1.001  # add 0.1% increase
    # st4.flow_exergy()
    # find State 4b, high pressure saturated liquid
    st4b = thermo.State(name='4b', cycle=cyc)
    st4b.fix('p',p_hi,'x',0.0)
    # st4b.flow_exergy()

    # State 4c for graphing purposes. Sat vapor at p_hi
    if st1.x == 'super':
        st4c = thermo.State(name='4c', cycle=cyc)
        st4c.fix('p',p_hi,'x',1.0)
        # st4c.flow_exergy()
        print('st4c',st4c.ef)

    # Define processes
    # Find work and heat for each process
    turb = thermo.Process(cyc,st1, st2, 0, st1.h-st2.h, "Turbine")
    cond = thermo.Process(cyc,st2, st3, st3.h-st2.h, 0, "Condenser")
    pump = thermo.Process(cyc,st3, st4, 0, wp, "Pump")
    boil = thermo.Process(cyc,st4, st1, st1.h-st4.h, 0, "Boiler")

    # Calculate flow exergy values for each state in cycle
    cyc.flow_exergy()

    # calculate exergy values for each process
    # Boiler
    boil.ex_in = boil.delta_ef
    boil.ex_d = 0
    boil.ex_out = 0
    boil.ex_eff = 1
    boil.ex_bal = boil.ex_in - boil.ex_out - boil.delta_ef - boil.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += boil.ex_in
    cyc.ex_d += boil.ex_d
    cyc.ex_out += boil.ex_out
    cyc.delta_ef += boil.delta_ef

    # Turbine
    turb.ex_in = 0
    turb.ex_d = turb.cycle.dead.T * (turb.outflow.s - turb.inflow.s)
    turb.ex_out = turb.work
    turb.ex_eff = turb.ex_out / -turb.delta_ef
    turb.ex_bal = turb.ex_in - turb.ex_out - turb.delta_ef - turb.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += turb.ex_in
    cyc.ex_d += turb.ex_d
    cyc.ex_out += turb.ex_out
    cyc.delta_ef += turb.delta_ef

    # Condenser
    cond.ex_in = 0
    cond.ex_d = 0
    cond.ex_out = -cond.delta_ef
    cond.ex_eff = 1
    cond.ex_bal = cond.ex_in - cond.ex_out - cond.delta_ef - cond.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += cond.ex_in
    cyc.ex_d += cond.ex_d
    cyc.ex_out += cond.ex_out
    cyc.delta_ef += cond.delta_ef

    # Pump
    pump.ex_out = 0
    pump.ex_in = -pump.work
    pump.ex_d = pump.cycle.dead.T * (pump.outflow.s - pump.inflow.s)
    pump.ex_eff = pump.delta_ef / pump.ex_in
    pump.ex_bal = pump.ex_in - pump.ex_out - pump.delta_ef - pump.ex_d
    # add results to cycle exergy totals
    cyc.ex_in += pump.ex_in
    cyc.ex_d += pump.ex_d
    cyc.ex_out += pump.ex_out
    cyc.delta_ef += pump.delta_ef

    # Define cycle properties
    cyc.wnet = turb.work + pump.work
    cyc.qnet = boil.heat + cond.heat
    cyc.en_eff = cyc.wnet / boil.heat
    cyc.bwr = -pump.work / turb.work
    cyc.ex_eff = cyc.wnet / boil.delta_ef  # cycle exergetic eff

    print('PUMP WORK=',pump.work)

    return cyc

def compute_plant(rank,props):
    ''' Compute and return plantplo object from rankine cycle and geothermal cycle objects '''
    cool_eff = props.get('cool_eff',1.0) # cooling efficiency
    units = props.get('units','si')
    # initialize geothermal cycle using defaults defined in object
    fluid = u'Salt Water, 20% salinity'
    # set brine dead state
    dead = thermo.State(cycle=None,name='Br.Dead',fluid=fluid)
    # dead.fix('T',298.0,'p',101325.0)
    dead.h = 61.05 * 1000 # J/kg
    dead.s = 0.2205 * 1000 # J/kg.K
    dead.T = 15 + 273 # K
    dead.p = 101325 # Pa
    dead.ef = 0
    geo = thermo.Geotherm(fluid=fluid,dead=dead)

    #   Find the mass flow rate of the brine based on cooling efficiency and
    #   the heat gained by the boiler in the Rankine cycle.
    # first, get the heat from the boiler process
    heat = 0.0
    for p in rank.get_procs():
        if 'boil' in p.name.lower():
            heat = p.heat
    # create initial brine state
    g1 = thermo.State(cycle=geo,name='Br.In')
    g1.s = 1.492 * 1000 # J/kg.K
    g1.h = 491.6 * 1000 # J/kg
    g1.T = 120 + 273.15 # K
    g1.p = 5 * 10**5    # bars to Pa
    g1.flow_exergy()
    geo.inflow = g1
    # set brine mass flow rate
    geo.mdot = (rank.mdot * heat) / (cool_eff * (geo.inflow.h - geo.dead.h))

    # initialize plant object using rankine and geothermal cycles
    plant = thermo.Plant(rank,geo)
    # set cooling efficiency
    plant.cool_eff = cool_eff
    #   Calculate plant energetic efficiency
    q_avail = geo.mdot * (geo.inflow.h - geo.dead.h)
    plant.en_eff = (rank.mdot * rank.wnet) / q_avail
    # calculate plant exergetic efficiency
    plant.ex_eff = (rank.mdot * rank.wnet) / (geo.mdot * geo.inflow.ef)

    return plant

def interactive():
    import input_rankine
    input_rankine.main()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Calculate the properties of a Rankine power cycle')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='interactively create and evaluate a Rankine power cycle')
    args = parser.parse_args(sys.argv[1:])
    print(args)
    if args.interactive:
        interactive()
    else:
        main()
    # print(args.accumulate(args.integers))
