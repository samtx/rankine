# Sam Rankine Cycle

import numpy as np
import pandas as pd
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Given properties

# number of time steps desired per process
step = 25

# these pressures must exist in the saturation table
# ... later add function to create new record of interpolated data in between
# pressure points if the user selects a pressure that isn't in the saturation table
p_low = 0.1 # low pressure, in MPa (condenser pressure)
p_hi = 10 # high pressure, in MPa (boiler pressure)

h2o_psat = pd.read_csv('H2O_PresSat.csv')
h2o_psat = h2o_psat.dropna(axis=1) #remove last NaN column
#print h2o_psat
h2o_tsat = pd.read_csv('H2O_TempSat.csv')
h2o_tsat = h2o_tsat.dropna(axis=1) #remove last NaN column
#print h2o_tsat
# merge the psat and tsat tables into one saturated table
h2o_sat = pd.concat([h2o_psat,h2o_tsat], axis=0, join='outer', join_axes=None, ignore_index=True,
                    keys=None, levels=None, names=None, verify_integrity=False)
#print h2o_sat
#sort by pressure
h2o_sat = h2o_sat.sort('P')
#print 'sorted...'
#print h2o_sat
h2o_comp = pd.read_csv('H2O_Compressed.csv')
h2o_comp = h2o_comp.dropna(axis=1) #remove last NaN column
#print h2o_comp

# begin computing processess for rankine cycle
fig = plt.figure(1)
plt.figure(1).suptitle("Rankine Cycle T-s Diagram \n Blue = adiabatic \n Green = isentropic")
plt.xlabel("Entropy (kJ/kg.K)")
plt.ylabel("Temperature (deg C)")

# create numpy arrays to save data from modeling
TT = np.zeros(step*4)
PP = np.zeros(step*4)
vv = np.zeros(step*4)
uu = np.zeros(step*4)
hh = np.zeros(step*4)
ss = np.zeros(step*4)
xx = np.zeros(step*4)

# process 2-3, isentropic turbine expansion with work output
# assume that this isn't a superheated rankine cycle, so state 2 is saturated vapor at pressure p_hi
s_o = h2o_sat[h2o_sat['P']==p_hi]['sg'].values[0] # this is the original entropy value
print s_o
#now interpolate down the saturation table and save the values for h, u, P, T, v
#for idx, row in h2o_sat.iterrows():
#    h2o_sat.ix[idx, grop] = 0
# save figure to directory
fig.savefig("graph.png")