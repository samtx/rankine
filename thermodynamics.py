# Create Python class for a thermodynamic state

import pandas as pd

def class fluid_props(subcooled_csv, saturated_csv, superheated_csv):
    ''' This class is a pandas panel of three data frames that define the fluid properties. The inputs are the filenames of the .csv's that contain the fluid data. The saturated_csv can be one filename or a list of filenames (such as saturated data listed by pressure or by temperature) that will be combined into one dataframe'''
    # how do I structure this pandas panel of three data frames?
    # idea: use MultiIndex to index the subcooled and superheated data frames by both pressure and temperature

def class state(fluid_panel,**kwargs):
    ''' This is a class that can be used to define a thermodynamic state for a given fluid. The user must enter the pandas data panel object containing data frames for 2 independent named variables for the state to be properly defined. All variables are specific, in that they are valued per unit mass. Optional variables and their default units are:
        T = temperature, (deg C)
        p = pressure, (MPa)
        v = specific volume (m^3/kg)
        u = internal energy (kJ/kg)
        h = enthalpy (kJ/kg)
        s = entropy (kJ/kg.K)
        x = quality (real number between 0 and 1 inclusive)
                '''
    def __init__():
        #
    