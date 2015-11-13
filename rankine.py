# Model the Rankine Cycle

from __future__ import print_function
import thermodynamics as thermo  # custom thermo state class in thermodynamics.py
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
#import os           # for file system utilities
import sys
from prettytable import PrettyTable #for output formatting

######################################

def main():
    #Obtaining user-defined properties of Rankine cycle
    props = define_inputs()
    # begin computing processess for rankine cycle
    (cyc_props,p_list,s_list) = compute_cycle(props)
    # print output to screen
    print_output_to_screen(cyc_props,p_list,s_list)
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
        p_hi = 8.0
        p_lo = 0.008
        turb_eff = 0.80
        pump_eff = 0.75
    else:
        (p_hi,p_lo) = select_pressures()
        (turb_eff,pump_eff) = select_efficiencies()
    #create dictionary of properties
    props = {}
    props["fluid"] = fluid
    props["p_hi"] = p_hi
    props["p_lo"] = p_lo
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

def compute_cycle(props):
    fluid = props['fluid']
    p_hi = props['p_hi']*10**6
    p_lo = props['p_lo']*10**6
    turb_eff = props['turb_eff']
    pump_eff = props['pump_eff']

    # Define States
    state_list = []
    # State 1, saturated vapor at high pressure
    st_1 = thermo.State(fluid,'p',p_hi,'x',1.0,'1')
    state_list.append(st_1)
    print(st_1.s)

    # State 2s, two-phase at low pressure with same entropy as state 1
    st_2s = thermo.State(fluid,'p',p_lo,'s',st_1.s,'2s')
    state_list.append(st_2s)

    # State 2, two-phase at low pressure determined by turbine efficiency
    h2 = turb_eff * (st_2s.h - st_1.h) + st_1.h  # with an irreversible turbine
    st_2 = thermo.State(fluid,'p',p_lo,'h',h2,'2')
    if st_2.x > 1:
        print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency \nExiting...')
        sys.exit()
    state_list.append(st_2)

    # State 3, saturated liquid at low pressure
    st_3 = thermo.State(fluid,'p',p_lo,'x',0.0,'3')
    state_list.append(st_3)

    # States 4 and 4s, sub-cooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for isentropic pump operation
    wps = -st_3.v*(p_hi - p_lo)
    h4s = st_3.h - wps
    # find values for irreversible pump operation
    wp = 1/pump_eff * wps
    st_4s = thermo.State(fluid,'p',p_hi,'s',st_3.s,'4s')
    state_list.append(st_4s)
    st_4 = thermo.State(fluid,'p',p_hi,'h',st_3.h-wp,'4')
    state_list.append(st_4)
    # find State 4b, high pressure saturated liquid
    st_4b = thermo.State(fluid,'p',p_hi,'x',0.0,'4b')
    state_list.append(st_4b)

    # Define processes
    # Find work and heat for each process
    wt = st_1.h - st_2.h
    qb = st_1.h - st_4.h
    qc = st_3.h - st_2.h
    turb = thermo.Process(st_1,st_2,0,wt,"Turbine")
    cond = thermo.Process(st_2,st_3,qc,0,"Condenser")
    pump = thermo.Process(st_3,st_4,0,wp,"Pump")
    boil = thermo.Process(st_4,st_1,qb,0,"Boiler")
    process_list = [turb,cond,pump,boil]

    # Define cycle properties
    wnet = turb.work + pump.work
    qnet = boil.heat + cond.heat
    # Find thermal efficiency for cycle
    thermal_eff = wnet / boil.heat
    # Find back work ratio
    bwr = -pump.work / turb.work
    cyc_props = {}
    cyc_props['wnet'] = wnet
    cyc_props['qnet'] = qnet
    cyc_props['thermal_eff'] = thermal_eff
    cyc_props['bwr'] = bwr

    return (cyc_props, process_list, state_list)

def print_output_to_screen(cyc_props,p_list,s_list):
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
    print('Low Pressure:  {:>3.3f} MPa'.format(props["p_lo"]))
    print('High Pressure: {:>3.3f} MPa'.format(props["p_hi"]))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%\n'.format(props["pump_eff"]*100))

    t = PrettyTable(['State','Enthalpy (kJ/kg)','Entropy (kJ/kg.K)','Quality'])
    t.align['Enthalpy (kJ/kg)'] = 'r'
    t.align['Entropy (kJ/kg.K)']= 'r'
    t.float_format['Enthalpy (kJ/kg)'] = '4.2'
    t.float_format['Entropy (kJ/kg.K)'] = '6.5'
    t.float_format['Quality'] = '0.2'
    t.padding_width = 1
    t.add_row(['1',st_1.h/1000,st_1.s/1000,'Sat Vapor'])
    t.add_row(['2s',st_2s.h/1000,st_2s.s/1000,st_2s.x])
    t.add_row(['2',st_2.h/1000,st_2.s/1000,st_2.x])
    t.add_row(['3',st_3.h/1000,st_3.s/1000,'Sat Liquid'])
    t.add_row(['4s',st_4s.h/1000,st_4s.s/1000,'Sub-Cooled Liq'])
    t.add_row(['4',st_4.h/1000,st_4.s/1000,'Sub-Cooled Liq'])
    print(t,'\n')

    t = PrettyTable(['Process','Heat (kJ/kg)','Work (kJ/kg)'])
    t.align['Heat (kJ/kg)'] = 'r'
    t.align['Work (kJ/kg)'] = 'r'
    t.float_format['Heat (kJ/kg)'] = '5.1'
    t.float_format['Work (kJ/kg)'] = '5.1'
    t.add_row(['1 - 2',0,turb.work/1000])
    t.add_row(['2 - 3',cond.heat/1000,0])
    t.add_row(['3 - 4',0,pump.work/1000])
    t.add_row(['4 - 1',boil.heat/1000,0])
    t.add_row(['Net',cyc_props["qnet"]/1000,cyc_props["wnet"]/1000])
    print(t)

    print('\nOther Values \n------------ ')
    print('v3 = {:.4e} m^3/kg'.format(st_3.v))
    print('thermal efficiency = {:2.1f}%'.format(cyc_props["thermal_eff"]*100))
    print('back work ratio = {:.3f}'.format(cyc_props["bwr"]))

    # get temperature values for T-s plot
#     T1 =  h2o_sat[h2o_sat['P']==p_hi]['T'].values[0]
#     T2 =  h2o_sat[h2o_sat['P']==p_lo]['T'].values[0] # come back to this
#     T2s = T2  # come back to this
#     T3 = T2s
#     T4s = T3 + 5 # temporary until I can interpolate to find real T4
#     T4b = T1
#     T4 = T4b * (s4 - s4s)/(s4b - s4s) + T4s

    # note: use h4, s4 to fix the state to find T4
    T_pts = [st_1.T, st_2s.T, st_2.T, st_2s.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
    s_pts = [st_1.s, st_2s.s, st_2.s, st_2s.s, st_3.s, st_4s.s, st_4b.s, st_1.s]

    s_dash_12 = [st_1.s, st_2.s]
    T_dash_12 = [st_1.T, st_2.T]
    s_dash_34 = [st_3.s, st_4.s]
    T_dash_34 = [st_3.T, st_4.T]

    # for i in s_pts: #round to two decimal places
    #   s_pts(i) = float('{:.2f}'.format(i))
    #print T_pts
    #print s_pts

#     # draw saturated dome. Get values from sat table
#     step = 5
#     for step


#     Tsat_pts = h2o_sat['T'].tolist()
#     sfsat_pts = h2o_sat['sf'].tolist()
#     sgsat_pts = h2o_sat['sg'].tolist()
#     # sort the lists
    #Tsat_pts =

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
    # if os.access(filename,os.F_OK):  # check if a ts_plot.png already exists
    #   if not os.access(filename,os.W_OK): # check to see if it is not writable
    #     os.fchmod(filename,stat.S_IWOTH) # if not writable, then make it writable
    plt.savefig(filename) # save figure to directory
    return

if __name__ == '__main__':
  main()
