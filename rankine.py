# Sam Rankine Cycle

# Here is another comment!!!

import numpy as np  # for some numerical methods
import pandas as pd # for data analysis tools like dataframes
import math         # duh
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
######################################
#Obtaining user input
done = 0
while not done:
  print "Select a working fluid from the following options: "
  print "1. H20" "\n" "2. Ethane" "\n" "3. Propane" "\n" "4. R22" "\n" "5. R134a" "\n" "6. R236ea" "\n" "7. CO2" "\n" "8. Pentane" "\n" "9. Isobutene"
  userinput = int(input(": "))

  if userinput == 1:
    # read in table values
    h2o_psat = pd.read_csv('H2O_PresSat.csv')
    h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
    h2o_tsat = pd.read_csv('H2O_TempSat.csv')
    h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
    done = 1
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
    print "Invalid input: Please Select Again"

# Given properties

# these pressures must exist in the saturation table
# ... later add function to create new record of interpolated data in between
# pressure points if the user selects a pressure that isn't in the saturation table
p_lo = input("Enter the desired low pressure(condenser pressure) in MPa: ") #0.008 # low pressure, in MPa (condenser pressure)
p_hi = input("Enter the desired high pressure(boiler pressure) in MPa: ")   #8.0 # high pressure, in MPa (boiler pressure)

# Isentropic efficiencies of pump and turbine in decimal notation. Default is 1.0 for 100% efficiency
print "Enter the turbine efficiency in decimal--Default to 1.0"
turb_eff = input(":") #.70  # turbine efficency
print "Enter the pump efficiency in decimal--Default to 1.0"
pump_eff = input(":") #.70  # pump efficiency

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
wps = v3*(p_hi - p_lo)*(10**3) # convert MPa to kPa
h4s = h3 + wps
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
eta = wnet / qb

# Find back work ratio
bwr = wp / wt

# print values to screen
print(' h1 = {:.2f}    s1 = {:.4f}'.format(h1,s1))
print('h2s = {:.2f}   s2s = {:.4f}'.format(h2s,s2s))
print(' h2 = {:.2f}    s2 = {:.4f}'.format(h2,s2))
print(' h3 = {:.2f}    s3 = {:.4f}'.format(h3,s3))
print('h4s = {:.2f}   s4s = {:.4f}'.format(h4s,s4s))
print(' h4 = {:.2f}    s4 = {:.4f}'.format(h4,s4))

print('x2s = {:.2f}'.format(x2s))
print(' x2 = {:.2f}'.format(x2))

print('v3 = {:.2f}'.format(v3))

print('wt = {:.2f}'.format(wt))
print('wp = {:.2f}'.format(wp))
print('qb = {:.2f}'.format(qb))
print('qc = {:.2f}'.format(qc))
print('eta = {:.3f}'.format(eta))
print('bwr = {:.3f}'.format(bwr))

# get temperature values for T-s plot
T1 =  h2o_sat[h2o_sat['P']==p_hi]['T'].values[0]
T2 =  h2o_sat[h2o_sat['P']==p_lo]['T'].values[0]
T3 = T2
T4 = T3 + 5 # temporary until I can interpolate to find real T3
# note: use h4, s4 to fix the state to find T4
T_pts = [T1, T2, T3, T4, T1, T1]
s_pts = [s1, s2, s3, s4, s4b, s1]
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
plt.plot(s_pts,T_pts,'b',sfsat_pts,Tsat_pts,'r--',sgsat_pts,Tsat_pts,'g--')
#plt.plot(s_pts,T_pts,'b',ssat_pts,Tsat_pts,'g--')
plt.suptitle("Rankine Cycle T-s Diagram")
plt.xlabel("Entropy (kJ/kg.K)")
plt.ylabel("Temperature (deg C)")
plt.savefig("graph.png") # save figure to directory
