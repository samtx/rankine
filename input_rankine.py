# Rankine cycle program with user input

from __future__ import print_function
import rankine

def main():


return



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
    props = {}
    select_fluid(props)
    select_pressures(props)
    select_temperatures(props)
    select_efficiencies(props)
    select_other_options(props)
    return props

def select_fluid(props):
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
    props["fluid"] = fluid
    return

def select_pressures():
    props["p_hi"] = enter_pressure('high')
    props["p_lo"] = enter_pressure('low')
    return

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

def select_temperatures():
    props["t_hi"] = enter_temperature('high')
    props["t_lo"] = enter_temperature('low')
    return

def enter_temperature(which_t):
    if which_t == 'high': machine = 'boiler'
    if which_t == 'low': machine = 'condenser'
    while True:
        p = raw_input("Enter the desired " + which_t + " temperature (" + machine + " temp) in deg C: ")
        should_quit(p)
        p,loop_again = try_float(p)
        if loop_again: continue  # must be a positive real number
        if p < 0:
            print("Can't have a negative temperature.")
            continue
        return p

def select_efficiencies():
    props["turb_eff"] = enter_efficiencies('turbine')
    props["pump_eff"] = enter_efficiencies('pump')
    props["cool_eff"] = enter_efficiencies('plant cooling')
    return

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


def select_other_options():
    props["superheat"] = enter_tf("Allow the turbine to accept superheated vapor?")
    props["in_kW"] = enter_tf('Print results tables in kW instead of kJ/kg?')
    props['cycle_mdot'] = enter_cycle_mdot()
    return

def enter_tf(string):
    while True:
        p = raw_input(string)
        should_quit(p)
        (ans,loop_again) = is_true(p)
        if not loop_again:
            return ans

def is_true(string):
    loop_again = True
    true_cmds = ['yes','y','true']
    false_cmds = ['no','n','false']
    if (string.lower() in true_cmds):
        loop_again = False
        answer = True
    elif (string.lower() in false_cmds):
        loop_again = False
        answer = False
    return (answer,loop_again)

def enter_cycle_mdot():
    while True:
        p = raw_input('Enter the mass flow rate in kg/s of the working fluid in the Rankine cycle: ')
        (p,loop_again) = try_float(p)
        if loop_again: continue
    return


def enter_temperature(which_t):
    if which_t == 'high': machine = 'boiler'
    if which_t == 'low': machine = 'condenser'
    while True:
        p = raw_input("Enter the desired " + which_t + " temperature (" + machine + " temp) in deg C: ")
        should_quit(p)
        p,loop_again = try_float(p)
        if loop_again: continue  # must be a positive real number
        if p < 0:
            print("Can't have a negative temperature.")
            continue
        return p


if __name__ == '__main__':
    main()