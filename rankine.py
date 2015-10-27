# Sam Rankine Cycle

import numpy as np  # for some numerical methods
import pandas as pd # for data analysis tools like dataframes
import math         # duh
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt

# Given properties

# these pressures must exist in the saturation table
# ... later add function to create new record of interpolated data in between
# pressure points if the user selects a pressure that isn't in the saturation table
p_lo = 0.008 # low pressure, in MPa (condenser pressure)
p_hi = 8.0 # high pressure, in MPa (boiler pressure)

# read in table values
h2o_psat = pd.read_csv('H2O_PresSat.csv')
h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
#print h2o_psat
h2o_tsat = pd.read_csv('H2O_TempSat.csv')
h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
#print h2o_tsat
# merge the psat and tsat tables into one saturated table
h2o_sat = pd.concat([h2o_psat,h2o_tsat], axis=0, join='outer', join_axes=None, ignore_index=True,
                    keys=None, levels=None, names=None, verify_integrity=False)

h2o_sat = h2o_sat.sort('P')
h2o_comp = pd.read_csv('H2O_Compressed.csv')
h2o_comp = h2o_comp.dropna(axis=1) #remove last NaN column
#print h2o_comp

# begin computing processess for rankine cycle


# State 1, saturated vapor at high pressure
# assume that this isn't a superheated rankine cycle, so state 2 is saturated vapor at pressure p_hi
s1 = h2o_sat[h2o_sat['P']==p_hi]['sg'].values[0]
h1 = h2o_sat[h2o_sat['P']==p_hi]['hg'].values[0]

# State 2, two-phase at low pressure
s2 = s1  # ideal rankine cycle
# find h_3 from s_2 and p_lo. first get the quality x_3
sf =  h2o_sat[h2o_sat['P']==p_lo]['sf'].values[0]
sg =  h2o_sat[h2o_sat['P']==p_lo]['sg'].values[0]
x2 = (s2 - sf)/(sg - sf) # quality at state 3
hf =  h2o_sat[h2o_sat['P']==p_lo]['hf'].values[0]
hg =  h2o_sat[h2o_sat['P']==p_lo]['hg'].values[0]
h2 = x2 * (hg - hf) + hf

# State 3, saturated liquid at low pressure
s3 =  h2o_sat[h2o_sat['P']==p_lo]['sf'].values[0]
h3 =  h2o_sat[h2o_sat['P']==p_lo]['hf'].values[0]

# State 4, sub-cooled liquid at high pressure
s4 = s3 # ideal rankine cycle
# assuming incompressible isentropic pump operation, let W/m = v*dp with v4 = v3
v3 = h2o_sat[h2o_sat['P']==p_lo]['vf'].values[0]
wp = v3*(p_hi - p_lo)*(10**3) # convert MPa to kPa
h4 = h3 + wp

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
print('h1 = {:.2f}'.format(h1))
print('h2 = {:.2f}'.format(h2))
print('h3 = {:.2f}'.format(h3))
print('v3 = {:.2f}'.format(v3))
print('h4 = {:.2f}'.format(h4))
print('wt = {:.2f}'.format(wt))
print('wp = {:.2f}'.format(wp))
print('qb = {:.2f}'.format(qb))
print('qc = {:.2f}'.format(qc))
print('eta = {:.2f}'.format(eta))
print('bwr = {:.2f}'.format(bwr))

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
plt.plot(s_pts,T_pts,'b',sfsat_pts,Tsat_pts,'g--',sgsat_pts,Tsat_pts,'g--')
#plt.plot(s_pts,T_pts,'b',ssat_pts,Tsat_pts,'g--')
plt.suptitle("Rankine Cycle T-s Diagram")
plt.xlabel("Entropy (kJ/kg.K)")
plt.ylabel("Temperature (deg C)")
plt.savefig("graph.png") # save figure to directory
