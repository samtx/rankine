# Model the Rankine Cycle

import thermodynamics as thermo  # custom thermo state class in thermodynamics.py
import pandas as pd # for data analysis tools like dataframes
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
import os           # for file system utilities
import sys
from prettytable import PrettyTable #for output formatting
from __future__ import print_function
######################################

def main():
    #Obtaining user-defined properties of Rankine cycle
    props = define_inputs()

    # begin computing processess for rankine cycle
    compute_cycle(props)


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
    if fluid = 'eg_mode':
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
        print "Select a working fluid from the following options: "
        fluid_list = ["Water","Ethane","Propane","R22","R134a","R236ea","Carbon Dioxide","Pentane","Isobutene"]
        for i in range(9):
            print(" {}. {}".format(i+1,fluid_list[i]) )
        fluid = raw_input(": ")
        should_quit(fluid)
        if userinput.isdigit(): userinput = int(userinput) #convert to integer if possible
        if userinput == 0: fluid = 'eg_mode',break #example problem
        else: print "Invalid input: Please Select Again. Enter Q to quit.\n"
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
    turb_eff = enter_efficiencies('turbine'):
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
    p_hi = props['p_hi']
    p_lo = props['p_lo']
    turb_eff = props['turb_eff']
    pump_eff = props['pump_eff']

    # State 1, saturated vapor at high pressure
    # assume that this isn't a superheated rankine cycle, so state 2 is saturated vapor at pressure p_hi
    st_1 = thermo.State(fluid,p=p_hi,x=1,name='1')

    # State 2s, two-phase at low pressure with same entropy as state 1
    st_2s = thermo.State(fluid,p=p_lo,s=st_1.entropy(),name='2s')

    # State 2, two-phase at low pressure determined by turbine efficiency
    h2 = turb_eff * (st_2s.enthalpy() - st_1.enthalpy()) + st_1.enthalpy()  # with an irreversible turbine
    st_2 = thermo.State(fluid,p=p_lo,h=h2,name='2')
    if st_2.quality() > 1:
        print('Fluid is superheated after leaving turbine. Please enter a higher turbine efficiency \nExiting...')
        sys.exit()

    # State 3, saturated liquid at low pressure
    st_3 = thermo.State(fluid,p=p_lo,x=0,name='3')

    # States 4 and 4s, sub-cooled liquid at high pressure
    # assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
    # find values for isentropic pump operation

    wps = -st_3.volume()*(p_hi - p_lo)*(10**3) # convert MPa to kPa
    h4s = h3 - wps
    # find values for irreversible pump operation
    wp = 1/pump_eff * (h3 - h4s)
    h4 = h3 - wp
    st_4s = thermo.State(fluid,p=p_hi,s=st_3.entropy(),name='4s')
    st_4 = thermo.State(fluid,p=p_hi,h=h4,name='4')
    # find State 4b, high pressure saturated liquid
    st_4b = thermo.State(fluid,p=p_hi,x=0,name='4b')

    # Find work and heat for each process
    wt = h1 - h2
    qb = h1 - h4
    qc = h3 - h2

    # Define processes
    turb = thermo.Process(heat=0,work=wt,st_1,st_2,name="Turbine")
    cond = thermo.Process(heat=qc,work=0,st_2,st_3,name="Condenser")
    pump = thermo.Process(heat=0,work=wp,st_3,st_4,name="Pump")
    boil = thermo.Process(heat=qb,work=0,st_4,st_1,name="Boiler")

    # Define cycle 
    wnet = wt + wp
    qnet = qb + qc


    # Find thermal efficiency for cycle
    thermal_eff = wnet / qb

    # Find back work ratio
    bwr = -wp / wt

    # print values to screen

def print_output(state_list,props):

    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+fluid)
    print('Low Pressure:  {:>3.3f} MPa'.format(p_lo))
    print('High Pressure: {:>3.3f} MPa'.format(p_hi))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(turb_eff*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%\n'.format(pump_eff*100))

    t = PrettyTable(['State','Enthalpy (kJ/kg)','Entropy (kJ/kg.K)','Quality'])
    t.align['Enthalpy (kJ/kg)'] = 'r'
    t.align['Entropy (kJ/kg.K)']= 'r'
    t.float_format['Enthalpy (kJ/kg)'] = '4.2'
    t.float_format['Entropy (kJ/kg.K)'] = '6.5'
    t.float_format['Quality'] = '0.2'
    t.padding_width = 1
    t.add_row(['1',h1,s1,'Sat Vapor'])
    t.add_row(['2s',h2s,s2s,x2s])
    t.add_row(['2',h2,s2,x2])
    t.add_row(['3',h3,s3,'Sat Liquid'])
    t.add_row(['4s',h4s,s4s,'Sub-Cooled Liq'])
    t.add_row(['4',h4,s4,'Sub-Cooled Liq'])
    print t,'\n'

    t = PrettyTable(['Process','Heat (kJ/kg)','Work (kJ/kg)'])
    t.align['Heat (kJ/kg)'] = 'r'
    t.align['Work (kJ/kg)'] = 'r'
    t.float_format['Heat (kJ/kg)'] = '5.1'
    t.float_format['Work (kJ/kg)'] = '5.1'
    t.add_row(['1 - 2',0,wt])
    t.add_row(['2 - 3',qc,0])
    t.add_row(['3 - 4',0,wp])
    t.add_row(['4 - 1',qb,0])
    t.add_row(['Net',qb+qc,wt+wp])
    print t

    print('\nOther Values \n------------ ')
    print('v3 = {:.4e} m^3/kg'.format(v3))
    print('thermal efficiency = {:2.1f}%'.format(thermal_eff*100))
    print('back work ratio = {:.3f}'.format(bwr))

    # get temperature values for T-s plot
    T1 =  h2o_sat[h2o_sat['P']==p_hi]['T'].values[0]
    T2 =  h2o_sat[h2o_sat['P']==p_lo]['T'].values[0] # come back to this
    T2s = T2  # come back to this
    T3 = T2s
    T4s = T3 + 5 # temporary until I can interpolate to find real T4
    T4b = T1
    T4 = T4b * (s4 - s4s)/(s4b - s4s) + T4s

    # note: use h4, s4 to fix the state to find T4
    T_pts = [T1, T2s, T2, T2s, T3, T4s, T4b, T1] # solid lines
    s_pts = [s1, s2s, s2, s2s, s3, s4s, s4b, s1]

    s_dash_12 = [s1, s2]
    T_dash_12 = [T1, T2]
    s_dash_34 = [s3, s4]
    T_dash_34 = [T3, T4]

    # for i in s_pts: #round to two decimal places
    #   s_pts(i) = float('{:.2f}'.format(i))
    #print T_pts
    #print s_pts

    # draw saturated dome. Get values from sat table
    Tsat_pts = h2o_sat['T'].tolist()
    sfsat_pts = h2o_sat['sf'].tolist()
    sgsat_pts = h2o_sat['sg'].tolist()
    # sort the lists
    #Tsat_pts =

    # Draw T-s plot
    plt.clf()
    plt.plot(s_pts,T_pts,'b',sfsat_pts,Tsat_pts,'g--',sgsat_pts,Tsat_pts,'g--')
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

if __name__ == '__main__':
  main()
