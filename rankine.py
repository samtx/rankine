# Model the Rankine Cycle

from __future__ import print_function
import thermodynamics as thermo  # custom thermo state class in thermodynamics.py
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
#import os           # for file system utilities
import sys
from prettytable import PrettyTable, MSWORD_FRIENDLY, PLAIN_COLUMNS #for output formatting
import CoolProp.CoolProp as CP

######################################

def main():

    fluid_list = ['Water']
    for fluid in fluid_list:
        #create dictionary of properties
        props = {}
        props["fluid"] = fluid
        props["p_hi"] = 8  #MPa
        props["p_lo"] = 0.008 #MPa
        props["t_hi"] = 120  # deg C
        props["t_lo"] = 25 # deg C
        props["turb_eff"] = 1
        props["pump_eff"] = 0.60

        # begin computing processess for rankine cycle
        rankine = compute_cycle(props)
        cyc_props = {}
        cyc_props['wnet'] = rankine.wnet
        cyc_props['qnet'] = rankine.qnet
        cyc_props['thermal_eff'] = rankine.thermal_eff
        cyc_props['bwr'] = rankine.bwr
        s_list = rankine.get_states()
        p_list = rankine.get_procs()

        # initialize geothermal cycle using defaults defined in object
        geotherm = thermo.Geotherm()

        # print output to screen
        print_output_to_screen(rankine,cyc_props,p_list,s_list,props,s_list[0].cycle.dead)

        # compute plant efficiencies
        plant = compute_plant(rankine,geotherm)

        # print plant results to screen
        print_plant_results(plant)

    return

def compute_cycle(props):
    fluid = props['fluid']
    p_hi = props['p_hi']*10**6
    p_lo = props['p_lo']*10**6
    t_hi = props['t_hi'] + 273.15
    t_lo = props['t_lo'] + 273.15
    turb_eff = props['turb_eff']
    pump_eff = props['pump_eff']

    # set dead state
    dead = thermo.State(None,'Dead State',fluid)
    dead.T = 15+273  #K
    dead.p = 101325.0  #Pa
    dead.h = CP.PropsSI('H','T',dead.T,'P',dead.p,dead.fluid)
    dead.s = CP.PropsSI('S','T',dead.T,'P',dead.p,dead.fluid)

    # initialize cycle
    cyc = thermo.Cycle(fluid,name='Rankine',mdot=0.43,dead=dead)

    # use pressures instead of temperatures when accessing CoolProp. So we
    # want to find the saturation pressures for the given temperatures and
    # fluid.
    if t_hi:
        p_hi = CP.PropsSI('P','T',t_hi,'Q',0,fluid)
    if t_lo:
        p_lo = CP.PropsSI('P','T',t_lo,'Q',0,fluid)

    # Define States
    # State 1, saturated vapor at high temperature
    st1 = thermo.State(cyc,'1')
    st1.T = t_hi
    st1.p = p_hi
    st1.x = 1
    st1.h = CP.PropsSI('H','P',p_hi,'Q',1,fluid)
    st1.s = CP.PropsSI('S','P',p_hi,'Q',1,fluid)
    st1.flow_exergy()

    # State 2s, two-phase at low temperature with same entropy as state 1
    st2s = thermo.State(cyc,'2s')
    st2s.T = CP.PropsSI('T','P',p_lo,'S',st1.s,fluid)
    st2s.p = p_lo
    st2s.s = st1.s
    sf = CP.PropsSI('S','P',p_lo,'Q',0,fluid)
    sg = CP.PropsSI('S','P',p_lo,'Q',1,fluid)
    st2s.x = (st2s.s - sf) / (sg - sf)
    hf = CP.PropsSI('H','P',p_lo,'Q',0,fluid)
    hg = CP.PropsSI('H','P',p_lo,'Q',1,fluid)
    st2s.h = st2s.x * (hg - hf) + hf
    st2s.flow_exergy()

    # State 2, two-phase at low pressure determined by turbine efficiency
    st2 = thermo.State(cyc,'2')
    st2.h = turb_eff * (st2s.h - st1.h) + st1.h  #with an irreversible turbine
    st2.x = (st2.h - hf) / (hg - hf)
    st2.s = st2.x * (sg - sf) + sf
    st2.p = p_lo
    st2.T = CP.PropsSI('T','P',p_lo,'S',st2.s,fluid)
    st2.flow_exergy()

    print('state 2 quality: ',st2.x)
    if st2.x > 1:
        print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency \nExiting...')
        sys.exit()

    # State 3, saturated liquid at low pressure
    st3 = thermo.State(cyc,'3')
    st3.T = t_lo
    st3.p = p_lo
    st3.x = 0
    st3.s = CP.PropsSI('S','P',p_lo,'Q',st3.x,fluid)
    st3.h = CP.PropsSI('H','P',p_lo,'Q',st3.x,fluid)
    st3.flow_exergy()

    # States 4 and 4s, subcooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for irreversible pump operation
    wp = 1/pump_eff * (-st3.v)*(st1.p - st3.p)
    st4s = thermo.State(cyc,'4s')
    st4s.s = st3.s
    st4s.p = p_hi
    st4s.T = CP.PropsSI('T','P',p_hi,'S',st4s.s,fluid)
    st4s.h = CP.PropsSI('H','P',p_hi,'S',st4s.s,fluid)
    st4s.x = 'subcooled'
    st4s.flow_exergy()


    # State 4
    st4 = thermo.State(cyc,'4')
    st4.h = st3.h - wp
    st4.T = CP.PropsSI('T','H',st4.h,'P',p_hi,fluid)
    st4.s = CP.PropsSI('S','H',st4.h,'P',p_hi,fluid)
    st4.p = p_hi
    st4.x = 'subcooled'
    st4.flow_exergy()
    # find State 4b, high pressure saturated liquid
    st4b = thermo.State(cyc,'4b')
    st4b.p = p_hi
    st4b.T = t_hi
    st4b.x = 0
    st4b.h = CP.PropsSI('H','P',p_hi,'Q',st4b.x,fluid)
    st4b.s = CP.PropsSI('S','P',p_hi,'Q',st4b.x,fluid)
    st4b.flow_exergy()

    # Define processes
    # Find work and heat for each process
    turb = thermo.Process(cyc,st1, st2, 0, st1.h-st2.h, "Turbine")
    cond = thermo.Process(cyc,st2, st3, st3.h-st2.h, 0, "Condenser")
    pump = thermo.Process(cyc,st3, st4, 0, wp, "Pump")
    boil = thermo.Process(cyc,st4, st1, st1.h-st4.h, 0, "Boiler")

    # calculate exergy values for each process
    # Boiler
    boil.ex_in = boil.delta_ef
    boil.ex_d = 0
    boil.ex_out = 0
    boil.ex_eff = 1
    # add results to cycle exergy totals
    cyc.ex_in += boil.ex_in
    cyc.ex_d += boil.ex_d
    cyc.ex_out += boil.ex_out
    cyc.delta_ef += boil.delta_ef

    # Turbine
    turb.ex_in = 0
    turb.ex_d = turb.cycle.dead.T * (turb.out.s - turb.in_.s)
    turb.ex_out = turb.work
    turb.ex_eff = turb.ex_out / -turb.delta_ef
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
    # add results to cycle exergy totals
    cyc.ex_in += cond.ex_in
    cyc.ex_d += cond.ex_d
    cyc.ex_out += cond.ex_out
    cyc.delta_ef += cond.delta_ef

    # Pump
    pump.ex_out = 0
    pump.ex_in = -pump.work
    pump.ex_d = pump.cycle.dead.T * (pump.out.s - pump.in_.s)
    pump.ex_eff = pump.delta_ef / pump.ex_in
    # add results to cycle exergy totals
    cyc.ex_in += pump.ex_in
    cyc.ex_d += pump.ex_d
    cyc.ex_out += pump.ex_out
    cyc.delta_ef += pump.delta_ef

    # Define cycle properties
    cyc.wnet = cyc.mdot * (turb.work + pump.work)
    cyc.qnet = cyc.mdot * (boil.heat + cond.heat)
    cyc.en_eff = cyc.wnet / boil.heat
    cyc.thermal_eff = cyc.en_eff
    cyc.bwr = -pump.work / turb.work
    cyc.ex_eff = cyc.ex_out / cyc.ex_in  # cycle exergetic eff

    return cyc

def print_output_to_screen(cycle,cyc_props,p_list,s_list,props,dead):
    #print_user_values(props)
    print_state_table(cycle)
    #print_process_table(cyc_props,p_list)
    #print_exergy_table(p_list)
    #print_cycle_values(cyc_props)
    #create_plot(p_list,s_list)
    return

def print_user_values(props):
    # print values to screen
    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+props["fluid"])
    print('Low Temperature:  {:>3.0f} deg C'.format(props["t_lo"]))
    print('High Temperature: {:>3.0f} deg C'.format(props["t_hi"]))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%\n'.format(props["pump_eff"]*100))
    return

def print_state_table(cycle):
    s_list = cycle.get_states()
    s_list.append(cycle.dead)
    headers = ['State','Press (kPa)','Temp (deg C)','Enthalpy (kJ/kg)','Entropy (kJ/kg.K)','Flow Exergy (kJ/kg)','Quality']
    t = PrettyTable(headers)
    for item in headers[1:6]:
        t.align[item] = 'r'
    for item in headers[2:4]:
        t.float_format[item] = '4.2'
    t.float_format[headers[1]] = '6.5'
    t.float_format[headers[4]] = '6.5'
    t.float_format[headers[5]] = '4.2'
    t.float_format[headers[6]] = '0.2'
    t.padding_width = 1
    for item in s_list:
        t.add_row([item.name,item.p/1000,item.T-273,item.h/1000,item.s/1000,item.ef/1000,item.x])
    print(t,'\n')
    return

def print_process_table(cyc_props,p_list):
    headers = ['Process','States','Heat (kJ/kg)','Work (kJ/kg)']
    t = PrettyTable(headers)
    #t.set_style(MSWORD_FRIENDLY)
    for item in headers[2:]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    for p in p_list:
        t.add_row([p.name,p.state_in.name+' -> '+p.state_out.name,p.heat/1000,p.work/1000])
    t.add_row(['Net','cycle',cyc_props["qnet"]/1000,cyc_props["wnet"]/1000])
    print(t, '\n')
    return

def print_exergy_table(p_list):
    headers = ['Process','States','Exergy In (kJ/kg)','Exergy Out (kJ/kg)','Delta Ef (kJ/kg)','Exergy Dest. (kJ/kg)','Exergetic Eff.']
    t = PrettyTable(headers)
    #t.set_style(PLAIN_COLUMNS)
    for item in headers[2:6]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    ex_totals = [0,0,0,0]
    for p in p_list:
        row = [p.name,p.state_in.name+' -> '+p.state_out.name,p.ex_in/1000,p.ex_out/1000,p.delta_ef/1000,p.ex_d/1000,'{:.1%}'.format(p.ex_eff)]
        t.add_row(row)
        # calculate exergy totals
        idx = 0
        for i in row[2:6]:
            ex_totals[idx] += i
            idx += 1
    # print net exergy row
    row = ['Net','']
    for i in ex_totals:
        row.append(i)
    # cycle exergetic efficiency
    cyc_ex_eff = ex_totals[1]/ex_totals[0]  # (total ex_out)/(total ex_in)
    row.append('{:.1%}'.format(cyc_ex_eff))
    t.add_row(row)
    print(t, '\n')
    return

def print_cycle_values(cyc_props):
    print('\nCycle Values \n------------ ')
    print('thermal efficiency = {:2.1f}%'.format(cyc_props["thermal_eff"]*100))
    print('back work ratio = {:.3f}'.format(cyc_props["bwr"]))
    return

def create_plot(p_list,s_list):
    # unpack states
    st_1 = s_list[0]
    st_2s = s_list[1]
    st_2 = s_list[2]
    st_3 = s_list[3]
    st_4s = s_list[4]
    st_4 = s_list[5]
    st_4b = s_list[6]

    # unpack processes
    turb = p_list[0]
    cond = p_list[1]
    pump = p_list[2]
    boil = p_list[3]

#    (spts,tpts) = get_sat_dome(cyc.fluid)

    # note: use h4, s4 to fix the state to find T4
    T_pts = [st_1.T, st_2s.T, st_2.T, st_2s.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
    s_pts = [st_1.s, st_2s.s, st_2.s, st_2s.s, st_3.s, st_4s.s, st_4b.s, st_1.s]

    s_dash_12 = [st_1.s, st_2.s]
    T_dash_12 = [st_1.T, st_2.T]
    s_dash_34 = [st_3.s, st_4.s]
    T_dash_34 = [st_3.T, st_4.T]

    # Draw T-s plot
    plt.clf()
#     plt.plot(s_pts,T_pts,'b',sfsat_pts,Tsat_pts,'g--',sgsat_pts,Tsat_pts,'g--')
    plt.plot(s_dash_12,T_dash_12,'b--',s_dash_34,T_dash_34,'b--')
    plt.annotate("1.", xy = (s_pts[1],T_pts[1]) , xytext = (s_pts[1] + 2,T_pts[1]+25 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
    plt.annotate("2.", xy = (s_pts[2],T_pts[2]) , xytext = (s_pts[2] + 2,T_pts[2]+25 ), arrowprops=dict(facecolor = 'blue', shrink=0.05),)
    plt.annotate("3.", xy = (s_pts[0],T_pts[0]) , xytext = (s_pts[0] + 2,T_pts[0]+25 ), arrowprops=dict(facecolor = 'red', shrink=0.05),)
    plt.annotate("4.", xy = (s_pts[4],T_pts[4]) , xytext = (s_pts[4] + 2,T_pts[4]+25 ), arrowprops=dict(facecolor = 'blue', shrink=0.05),)
    plt.suptitle("Rankine Cycle T-s Diagram")
    plt.xlabel("Entropy (kJ/kg.K)")
    plt.ylabel("Temperature (deg C)")
    # Save plot
    filename = 'ts_plot.png'
    plt.savefig(filename) # save figure to directory
    return

def compute_plant(rank,geo):
    ''' Compute and return plant object from rankine cycle and geothermal cycle objects '''
    plant = thermo.Plant(rank,geo)
    return plant

def print_plant_results(plant):
    print('\nPlant Efficiencies \n------------ ')
#     headers = ['Working Fluid','Plant Energetic Eff.','Plant Exergetic Eff.','Cycle Energetic Eff.','Cycle Exergetic Eff.']
#     t = PrettyTable(headers)
#     for item in headers[1:]:
#         t.align[item] = 'r'
#         #t.float_format[item] = '0.2'
    effs = [plant.en_eff,plant.ex_eff,plant.rank.en_eff,plant.rank.ex_eff]
#     row = [plant.rank.fluid]
#     row.append(effs)
#     #for e in effs:
#     #    row.append('{:.2}'.format(e))
#     t.add_row(row)
#     print(t, '\n')
    print('plant en eff=',plant.en_eff)
    print('plant ex eff=',plant.ex_eff)
    print('cycle en eff=',plant.rank.en_eff)
    print('cycle ex eff=',plant.rank.ex_eff)
    return

def get_sat_dome(fluid):
    pass
#     smin = ?
#     smax = ?
#     step = ?
#     quality = 0
#     tpts = []
#     spts = []
#     crit_pt = thermo.State(None,fluid, critical) point?asdlkfjasd;lkf100 #something
#     for s in range(s_min:step:s_max):
#         if s > crit_pt.s:
#             quality = 1
#         T = CP.PropsSI('T','S',s,'Q',quality,fluid)
#         spts.append(s)
#         tpts.append(T-273) # save in celcius
#     return spts,tpts






##############################################################################
# ----------------------- User Input Functions -------------------------------
##############################################################################

def should_quit(string):
    exit_cmds = ['quit','exit','q','x','e','stop']
    if (string.lower() in exit_cmds):
        sys.exit() # gracefully exit program

def try_float(string):
    loop_again = False
    try:
        number = float(string)
    except ValueError:
        print('Please enter a number or Q to quit')
        number = ""
        loop_again = True
    return number,loop_again

def define_inputs():
    fluid = select_fluid()
    if fluid == 'eg_mode':
        # use example mode
        fluid = 'Water'
        p_hi = 3.9  # MPa
        p_lo = 1.0  # MPa
        t_hi = 120  # deg C
        t_lo = 25   # deg C
        turb_eff = 0.85
        pump_eff = 0.6
    else:
        (p_hi,p_lo) = select_pressures()
        (turb_eff,pump_eff) = select_efficiencies()
    #create dictionary of properties
    props = {}
    props["fluid"] = fluid
    props["p_hi"] = p_hi
    props["p_lo"] = p_lo
    props["t_hi"] = t_hi
    props["t_lo"] = t_lo
    props["turb_eff"] = turb_eff
    props["pump_eff"] = pump_eff
    return props

def select_fluid():
    while True:
        print("Select a working fluid from the following options: ")
        fluid_list = ["Water","Ethane","n-Propane","R22","R134a","R236EA","CarbonDioxide","n-Pentane","IsoButene"]
        for i in range(9):
            print(" {}. {}".format(i+1,fluid_list[i]) )
        fluid = raw_input(": ")
        should_quit(fluid)
        if fluid == '0':  #example problem
            fluid = 'eg_mode'
            break
        elif fluid.isdigit() and fluid not in range(0,len(fluid_list)):
            fluid = fluid_list[int(fluid)-1] #use num to pick fluid string
            break
        elif fluid in fluid_list: # if they just typed it exactly, case-sensitive
            break
        else: print("Invalid input: Please Select Again. Enter Q to quit.\n")
    return fluid

def select_pressures():
    p_hi = enter_pressure('high')
    p_lo = enter_pressure('low')
    return p_hi,p_lo

def enter_pressure(which_p):
    if which_p == 'high': machine = 'boiler'
    if which_p == 'low': machine = 'condenser'
    while True:
        p = raw_input("Enter the desired " + which_p + " pressure (" + machine + " pressure) in MPa: ")
        should_quit(p)
        p,loop_again = try_float(p)
        if loop_again: continue  # must be a positive real number
        if p < 0:
            print("Can't have a negative pressure.")
            continue
        return p

def select_efficiencies():
    turb_eff = enter_efficiencies('turbine')
    pump_eff = enter_efficiencies('pump')
    return turb_eff,pump_eff

def enter_efficiencies(which_eff):
    while True:
        eff = raw_input("Enter the " + which_eff + " efficiency in %. Default is 100%: ").strip('%')
        should_quit(eff)
        if eff == "":
            eff = 1.0  # default if nothing is entered
            break
        (eff,loop_again) = try_float(eff)
        if loop_again: continue
        if eff == 0:
            print("Can't have 0% " + which_eff + " efficiency")
            continue
        if eff < 0:
            print("Can't have negative " + which_eff + " efficiency")
            continue
        elif eff > 100:
            print("Can't have over 100% " + which_eff + " efficiency")
            continue
        elif eff > 1.0:
            eff = eff/100 # convert to decimal if entered in percent
        break
    return eff

if __name__ == '__main__':
    main()