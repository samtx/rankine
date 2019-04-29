"""
Run tests by entering

    $ pytest

on the command line.
"""

import pytest
from .. import rankine
from ..print_rankine import print_output_to_screen

def test_print_rankine_butane():
    props = {}
    props["fluid"] = 'n-Butane'
    props["p_hi"] = 3.5  #MPa
    props["p_lo"] = 0.3 #MPa
    # props["t_hi"] =  148 # deg C
    props["turb_eff"] = 0.8
    props["pump_eff"] = 0.75
    props['cool_eff'] = 0.25 #cooling efficiency
    props['in_kW'] = False # print results in kW instead of kJ/kg?
    props['cycle_mdot'] = 3.14   # mass flow rate of rankine cycle working fluid in kg/s
    props['superheat'] =  False # should we allow for superheating?
    # begin computing processess for rankine cycle
    cyc = rankine.compute_cycle(props)
    # compute plant efficiencies
    plant = rankine.compute_plant(cyc,props)
    # print output to screen
    print_output_to_screen(plant,props)
    assert cyc.en_eff == pytest.approx(0.14709, abs=1e-4)
