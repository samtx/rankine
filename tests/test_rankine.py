"""
Run tests by entering

    $ pytest

on the command line.
"""

import pytest
from .. import rankine

def test_rankine_butane():
    props = {}
    props["fluid"] = 'n-Butane'
    props["p_hi"] = 3.5  #MPa
    props["p_lo"] = 0.3 #MPa
    # props["t_hi"] =  148 # deg C
    props["turb_eff"] = 0.8
    props["pump_eff"] = 0.75
    props['superheat'] =  False # should we allow for superheating?
    # begin computing processess for rankine cycle
    cyc = rankine.compute_cycle(props)
    assert cyc.en_eff == pytest.approx(0.14709, abs=1e-4)

def test_rankine_water():
    # https://youtu.be/nOiPWVIoSHQ?t=449
    props = {}
    props["fluid"] = 'Water'
    props["p_hi"] = 8.0  # MPa
    props["p_lo"] = 0.020 # MPa
    # begin computing processess for rankine cycle
    cyc = rankine.compute_cycle(props)
    assert cyc.en_eff == pytest.approx(0.345, abs=1e-3)
    assert cyc.bwr == pytest.approx(0.0093, abs=1e-3)
    assert cyc.wnet == pytest.approx(861.8e3, rel=0.001)
    
def test_rankine_water_superheat():
    props = {}
    props["fluid"] = 'Water'
    props["p_hi"] = 4.0   # MPa
    props["p_lo"] = 0.010 # MPa
    props['t_hi'] = 400   # deg C
    props["turb_eff"] = 1.0
    props["pump_eff"] = 1.0
    props['superheat'] =  True # should we allow for superheating?
    # begin computing processess for rankine cycle
    cyc = rankine.compute_cycle(props)
    assert cyc.en_eff == pytest.approx(0.353, abs=1e-3)
    assert cyc.wnet == pytest.approx(1065.5e3, rel=0.001)

def test_rankine_water_superheat_2():
    props = {}
    props["fluid"] = 'Water'
    props["p_hi"] = 3.0   # MPa
    props["p_lo"] = 0.050 # MPa
    props['t_hi'] = 400   # deg C
    props["mdot"] = 25.0  # kg/s
    props['superheat'] =  True # should we allow for superheating?
    # begin computing processess for rankine cycle
    cyc = rankine.compute_cycle(props)
    assert cyc.en_eff == pytest.approx(0.284, abs=1e-3)
    assert cyc.wnet == pytest.approx(820.45e3, rel=0.001)
