# Sam Rankine Cycle

# Here is another comment!!!

import numpy as np  # for some numerical methods
import pandas as pd # for data analysis tools like dataframes
import math         # duh
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
import os           # for file system utilities
import sys
from prettytable import PrettyTable #for output formatting
######################################
#Obtaining user input
done = 0
eg_mode = False
while not done:
  print "Select a working fluid from the following options: "
  print " 1. H20\n 2. Ethane\n 3. Propane\n 4. R22\n 5. R134a\n 6. R236ea\n 7. CO2\n 8. Pentane\n 9. Isobutene"
  userinput = raw_input(": ")
  # gracefully exit
  exit_cmds = ['quit','exit','q','x','e','stop']
  if (userinput.lower() in exit_cmds):
    sys.exit() # exit
  elif userinput.isdigit():
    userinput = int(userinput)
  if userinput == 0:
    # Example problem
    eg_mode = True
    # read in table values
    h2o_psat = pd.read_csv('H2O_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('H2O_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
    p_lo = 0.008
    p_hi = 8.0
    turb_eff = .80
    pump_eff = .75
  elif userinput == 1:
    # read in table values
    h2o_psat = pd.read_csv('H2O_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('H2O_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  # until we get csv tables loaded for the other organic fluids, don't crash the program if they are selected
  elif userinput in range(2,10):
    print("Sorry, we don't have that data loaded yet. Please enter 1 for H2O\n'")
    continue
  elif userinput == 2:
    h2o_psat = pd.read_csv('Ethane_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('Ethane_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 3:
    # read in table values
    h2o_psat = pd.read_csv('H20_PressSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('H2O_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 4:
    h2o_psat = pd.read_csv('Ethane_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('Ethane_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 5:
    # read in table values
    h2o_psat = pd.read_csv('R22_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('R22_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 6:
    h2o_psat = pd.read_csv('R134a_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('R134a_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 7:
    # read in table values
    h2o_psat = pd.read_csv('CO2_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('CO2_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 8:
    h2o_psat = pd.read_csv('Pentane_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('Pentane_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  elif userinput == 9:
    # read in table values
    h2o_psat = pd.read_csv('Isobutane_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('Isobutane_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
  else:
    print "Invalid input: Please Select Again. Enter q to quit.\n"

# Given properties

# these pressures must exist in the saturation table
# ... later add function to create new record of interpolated data in between
# pressure points if the user selects a pressure that isn't in the saturation table
if not eg_mode:
  p_lo = input("Enter the desired low pressure(condenser pressure) in MPa: ") #0.008 # low pressure, in MPa (condenser pressure)
  p_hi = input("Enter the desired high pressure(boiler pressure) in MPa: ")   #8.0 # high pressure, in MPa (boiler pressure)

# Isentropic efficiencies of pump and turbine in decimal notation. Default is 1.0 for 100% efficiency
if not eg_mode:
  turb_eff = input("Enter the turbine efficiency in decimal--Default to 1.0: ")

  pump_eff = input("Enter the pump efficiency in decimal--Default to 1.0: ")

# read in table values
##h2o_psat = pd.read_csv('H2O_PresSat.csv')
##h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
#print h2o_psat
##h2o_tsat = pd.read_csv('H2O_TempSat.csv')
##h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
#print h2o_tsat
# merge the psat and tsat tables into one saturated table
h2o_sat = pd.concat([h2o_psat,h2o_tsat], axis=0, join='outer', join_axes=None, ignore_index=True,
                    keys=None, levels=None, names=None, verify_integrity=False)

h2o_sat = h2o_sat.sort('P')

## Will we have compressed tables for everthing?? We will have to address this based upon what Colton finds
h2o_comp = pd.read_csv('H2O_Compressed.csv')
h2o_comp = h2o_comp.dropna(axis=1) #remove last NaN column
#print h2o_comp

# begin computing processess for rankine cycle


# State 1, saturated vapor at high pressure
# assume that this isn't a superheated rankine cycle, so state 2 is saturated vapor at pressure p_hi
s1 = h2o_sat[h2o_sat['P']==p_hi]['sg'].values[0]
h1 = h2o_sat[h2o_sat['P']==p_hi]['hg'].values[0]

# State 2, two-phase at low pressure
sf =  h2o_sat[h2o_sat['P']==p_lo]['sf'].values[0]
sg =  h2o_sat[h2o_sat['P']==p_lo]['sg'].values[0]
hf =  h2o_sat[h2o_sat['P']==p_lo]['hf'].values[0]
hg =  h2o_sat[h2o_sat['P']==p_lo]['hg'].values[0]
# find values for isentropic turbine operation
# find h_2s from s_1 and p_lo. first get the quality x_2s
s2s = s1
x2s = (s2s - sf)/(sg - sf) # quality at state 2s
h2s = x2s * (hg - hf) + hf  # using an internally reversible turbine
# !!! put check here to make sure state isn't superheated !!!
# find values for irreversible turbine operation
h2 = turb_eff * (h2s - h1) + h1  # with an irreversible turbine
x2 = (h2 - hf)/(hg - hf) # quality at state 2
s2 = x2 * (sg - sf) + sf # entropy at state 2

# State 3, saturated liquid at low pressure
s3 =  h2o_sat[h2o_sat['P']==p_lo]['sf'].values[0]
h3 =  h2o_sat[h2o_sat['P']==p_lo]['hf'].values[0]

# State 4, sub-cooled liquid at high pressure
# assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
v3 = h2o_sat[h2o_sat['P']==p_lo]['vf'].values[0]
# find values for isentropic pump operation
s4s = s3 # ideal rankine cycle
wps = -v3*(p_hi - p_lo)*(10**3) # convert MPa to kPa
h4s = h3 - wps
# find values for irreversible pump operation
wp = 1/pump_eff * (h4s - h3)
h4 = h3 + wp
# !!! find entropy s4 somehow !!!
s4 = s4s + 0.01  # temporary until I figure this out


# find State 4b, high pressure saturated liquid
s4b = h2o_sat[h2o_sat['P']==p_hi]['sf'].values[0]

# Find work and heat for each process
wt = h1 - h2
qb = h1 - h4
wnet = wt - wp
qnet = wnet
qc = qnet - qb

# Find thermal efficiency for cycle
thermal_eff = wnet / qb

# Find back work ratio
bwr = wp / wt

# print values to screen
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
t.add_row(['Net',qb-qc,wt-wp])
print t

print('\nOther Values \n------------ ')
print('v3 = {:.6f}'.format(v3))
print('thermal efficiency = {:.3f}'.format(thermal_eff))
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
