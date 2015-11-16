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
    #Obtaining user-defined properties of Rankine cycle
    props = define_inputs()
<<<<<<< HEAD

    # begin computing processess for rankine cycle
    (cyc_props,p_list,s_list) = compute_cycle(props)

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

    # ----- PUT THIS INTO A SEPARATE FUNCTION LATER -----

    # print values to screen
    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+props["fluid"])
    #print('Low Pressure:  {:>3.3f} MPa'.format(props["p_lo"]))
    #print('High Pressure: {:>3.3f} MPa'.format(props["p_hi"]))
    print('Low Temperature:  {:>3.0f} deg C'.format(props["t_lo"]))
    print('High Temperature: {:>3.0f} deg C'.format(props["t_hi"]))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%\n'.format(props["pump_eff"]*100))

    t = PrettyTable(['State','Enthalpy (kJ/kg)','Entropy (kJ/kg.K)','Quality'])
    t.align['Enthalpy (kJ/kg)'] = 'r'
    t.align['Entropy (kJ/kg.K)']= 'r'
    t.float_format['Enthalpy (kJ/kg)'] = '4.2'
    t.float_format['Entropy (kJ/kg.K)'] = '6.5'
    t.float_format['Quality'] = '0.2'
    t.padding_width = 1
    t.add_row([st_1.name,st_1.h/1000,st_1.s/1000,'Sat Vapor'])
    t.add_row([st_2s.name,st_2s.h/1000,st_2s.s/1000,st_2s.x])
    t.add_row([st_2.name,st_2.h/1000,st_2.s/1000,st_2.x])
    t.add_row([st_3.name,st_3.h/1000,st_3.s/1000,'Sat Liquid'])
    t.add_row([st_4s.name,st_4s.h/1000,st_4s.s/1000,'Sub-Cooled Liq'])
    t.add_row([st_4.name,st_4.h/1000,st_4.s/1000,'Sub-Cooled Liq'])
    print(t,'\n')

    t = PrettyTable(['Process','States','Heat (kJ/kg)','Work (kJ/kg)'])
    t.align['Heat (kJ/kg)'] = 'r'
    t.align['Work (kJ/kg)'] = 'r'
    t.float_format['Heat (kJ/kg)'] = '5.1'
    t.float_format['Work (kJ/kg)'] = '5.1'
    for p in p_list:
        t.add_row([p.name,p.state_in.name+' -> '+p.state_out.name,p.heat/1000,p.work/1000])
    t.add_row(['Net','',cyc_props["qnet"]/1000,cyc_props["wnet"]/1000])
    print(t)

    print('\nOther Values \n------------ ')
    print('v3 = {:.4e} m^3/kg'.format(st_3.v))
    print('thermal efficiency = {:2.1f}%'.format(cyc_props["thermal_eff"]*100))
    print('back work ratio = {:.3f}'.format(cyc_props["bwr"]))

    # get temperature values for T-s plot
#     T1 =  h2o_sat[h2o_sat['P']==p_hi]['T'].values()[0]
#     T2 =  h2o_sat[h2o_sat['P']==p_lo]['T'].values()[0] # come back to this
#     T2s = T2  # come back to this
#     T3 = T2s
#     T4s = T3 + 5 # temporary until I can interpolate to find real T4
#     T4b = T1
#     T4 = T4b * (s4 - s4s)/(s4b - s4s) + T4s
=======
>>>>>>> master

    # begin computing processess for rankine cycle
    rankine = compute_cycle(props)
    cyc_props = {}
    cyc_props['wnet'] = rankine.wnet
    cyc_props['qnet'] = rankine.qnet
    cyc_props['thermal_eff'] = rankine.thermal_eff
    cyc_props['bwr'] = rankine.bwr
    s_list = rankine.get_states()
    p_list = rankine.get_procs()

#     initialize geothermal cycle using defaults
    geotherm = thermo.Geotherm()

    # print output to screen
    print_output_to_screen(cyc_props,p_list,s_list,props,s_list[0].cycle.dead)

    # compute plant efficiencies
    plant = compute_plant(rankine,geotherm)

    # print plant results to screen
    print_plant_results(plant)

    return

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
<<<<<<< HEAD
        p_hi = 8.0
        p_lo = 0.008
        t_hi = 90
        t_lo = 20
        turb_eff = 1
        pump_eff = 0.75
=======
        p_hi = 3.9
        p_lo = 1.0
        turb_eff = 0.85
        pump_eff = 0.6
>>>>>>> master
    else:
        (t_hi,t_lo) = select_temps()
        #(p_hi,p_lo) = select_pressures()
        (turb_eff,pump_eff) = select_efficiencies()
    #create dictionary of properties
    props = {}
    props["fluid"] = fluid
    #props["p_hi"] = p_hi
    #props["p_lo"] = p_lo
    props['t_hi'] = t_hi
    props['t_lo'] = t_lo
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

def select_temps():
    t_lo = enter_temp('low')
    t_hi = enter_temp('high')
    return t_hi,t_lo

def enter_temp(which_t):
    while True:
        t = raw_input("Enter the desired " + which_t + " temperature in degrees Celcius: ")
        should_quit(t)
        t,loop_again = try_float(t)
        if loop_again: continue  # must be a positive real number
        return t

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

def compute_cycle(props):
    fluid = props['fluid']
    #p_hi = props['p_hi']*10**6
    #p_lo = props['p_lo']*10**6
    t_hi = props['t_hi'] + 273.15
    t_lo = props['t_lo'] + 273.15
    turb_eff = props['turb_eff']
    pump_eff = props['pump_eff']

    # initialize cycle
    cyc = thermo.Cycle(fluid,p_hi=p_hi,p_lo=p_lo,name='Rankine',mdot=0.43)

    # Define States
    # State 1, saturated vapor at high pressure
    st_1 = thermo.State(cyc,fluid,'p',p_hi,'Q',1,'1')

    # State 2s, two-phase at low pressure with same entropy as state 1
    st_2s = thermo.State(cyc,fluid,cyc.prop_lo.keys()[0],cyc.prop_lo.values()[0],'s',st_1.s,'2s')

    # State 2, two-phase at low pressure determined by turbine efficiency
    h2 = turb_eff * (st_2s.h - st_1.h) + st_1.h  # with an irreversible turbine
    st_2 = thermo.State(cyc,fluid,'P',st_2s.p,'h',h2,'2')
    if st_2.x > 1:
        print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency. \nExiting...')
        sys.exit()

    # State 3, saturated liquid at low pressure
    st_3 = thermo.State(cyc,fluid,cyc.prop_lo.keys()[0],cyc.prop_lo.values()[0],'x',0.0,'3')

    # States 4 and 4s, sub-cooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for irreversible pump operation
    wp = 1/pump_eff * (-st_3.v)*(st_1.p - st_2.p)
    st_4s = thermo.State(cyc,fluid,cyc.prop_hi.keys()[0],cyc.prop_hi.values()[0],'s',st_3.s,'4s')
    st_4 = thermo.State(cyc,fluid,'P',st_1.p,'h',st_3.h-wp,'4')
    # find State 4b, high pressure saturated liquid
    st_4b = thermo.State(cyc,fluid,cyc.prop_hi.keys()[0],cyc.prop_hi.values()[0],'x',0.0,'4b')

    # Define processes
    # Find work and heat for each process
    turb = thermo.Process(cyc,st_1, st_2, 0, st_1.h-st_2.h, "Turbine")
    cond = thermo.Process(cyc,st_2, st_3, st_3.h-st_2.h, 0, "Condenser")
    pump = thermo.Process(cyc,st_3, st_4, 0, wp, "Pump")
    boil = thermo.Process(cyc,st_4, st_1, st_1.h-st_4.h, 0, "Boiler")

    # calculate exergy values for each process
    # Boiler
    boil.ex_in = boil.delta_ef
    boil.ex_d = 0
    boil.ex_out = 0
    boil.ex_eff = 1
    # Turbine
    turb.ex_in = 0
    turb.ex_d = turb.cycle.dead.T * (turb.out.s - turb.in_.s)
    turb.ex_out = turb.work
    turb.ex_eff = turb.ex_out / -turb.delta_ef
    # Condenser
    cond.ex_in = 0
    cond.ex_d = 0
    cond.ex_out = -cond.delta_ef
    cond.ex_eff = 1
    # Pump
    pump.ex_out = 0
    pump.ex_in = -pump.work
    pump.ex_d = pump.cycle.dead.T * (pump.out.s - pump.in_.s)
    pump.ex_eff = pump.delta_ef / pump.ex_in

    # Define cycle properties
    cyc.wnet = cyc.mdot * (turb.work + pump.work)
    cyc.qnet = cyc.mdot * (boil.heat + cond.heat)
    cyc.en_eff = cyc.wnet / boil.heat
    cyc.thermal_eff = cyc.en_eff
    cyc.bwr = -pump.work / turb.work

    return cyc

def print_output_to_screen(cyc_props,p_list,s_list,props,dead):
    print_user_values(props)
    print_state_table(s_list,dead)
    print_process_table(cyc_props,p_list)
    print_exergy_table(p_list)
    print_cycle_values(cyc_props)
    create_plot(p_list,s_list)
    return

def print_user_values(props):
    # print values to screen
    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+props["fluid"])
    print('Low Pressure:  {:>3.3f} MPa'.format(props["p_lo"]))
    print('High Pressure: {:>3.3f} MPa'.format(props["p_hi"]))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%\n'.format(props["pump_eff"]*100))
    return

def print_state_table(s_list,dead):
    headers = ['State','Press (MPa)','Temp (deg C)','Enthalpy (kJ/kg)','Entropy (kJ/kg.K)','Flow Exergy (kJ/kg)','Quality']
    t = PrettyTable(headers)
    for item in headers[1:6]:
        t.align[item] = 'r'
    for item in headers[2:4]:
        t.float_format[item] = '4.2'
    t.float_format[headers[1]] = '4.3'
    t.float_format[headers[4]] = '6.5'
    t.float_format[headers[5]] = '4.2'
    t.float_format[headers[6]] = '0.2'
    t.padding_width = 1
    s_list.append(dead)
    for item in s_list:
        print(item.name)
        t.add_row([item.name,item.p/1000000,item.T-273,item.h/1000,item.s/1000,item.ef/1000,item.x])
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

if __name__ == '__main__':
    main()
