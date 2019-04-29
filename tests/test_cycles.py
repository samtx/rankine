
from pytest import approx
from ..cycles import ideal_rankine, rankine_superheated, rankine_reheated

def test_ideal_rankine_butane():
    fluid = 'n-Butane'
    p_hi = 3.5  # MPa
    p_lo = 0.3  # MPa
    turb_eff = 0.8
    pump_eff = 0.75
    cycle = ideal_rankine(p_hi=p_hi, p_lo=p_lo, 
        turb_eff=turb_eff, pump_eff=pump_eff,
        fluid=fluid)
    assert cycle.en_eff == approx(0.14709, abs=1e-4)

def test_ideal_rankine_water():
    fluid = 'Water'
    p_hi = 8.0  # MPa
    p_lo = 0.020  # MPa
    cycle = ideal_rankine(p_hi=p_hi, p_lo=p_lo, 
        fluid=fluid)
    assert cycle.en_eff == approx(0.345, abs=1e-3)
    assert cycle.bwr == approx(0.0093, abs=1e-3)
    assert cycle.wnet == approx(861.8e3, rel=1e-3)

def test_rankine_superheat():
    fluid = 'Water'
    p_hi = 4.0   # MPa
    p_lo = 0.010 # MPa
    T_hi = 400   # deg C
    cycle = rankine_superheated(p_hi=p_hi, p_lo=p_lo, T_hi=T_hi, 
        fluid=fluid)
    assert cycle.en_eff == approx(0.353, abs=1e-3)
    assert cycle.wnet == approx(1065.5e3, rel=1e-3)

def test_rankine_superheat_2():
    fluid = 'Water'
    p_hi = 3.0   # MPa
    p_lo = 0.050 # MPa
    T_hi = 400   # deg C
    cycle = rankine_superheated(p_hi=p_hi, p_lo=p_lo, T_hi=T_hi, 
        fluid=fluid)
    assert cycle.en_eff == approx(0.284, abs=1e-3)
    assert cycle.wnet == approx(820.45e3, rel=1e-3)

def test_rankine_reheat():
    fluid = 'Water'
    p_hi = 4.0    # MPa
    p_mid = 0.400 # MPa
    p_lo = 0.010  # MPa
    T_hi = 400    # deg C
    T_mid = 400   # deg C
    cycle = rankine_reheated(
        p_hi=p_hi, T_hi=T_hi,
        p_mid=p_mid, T_mid=T_mid,
        p_lo=p_lo,  
        fluid=fluid)
    assert cycle.en_eff == approx(0.359, abs=1e-3)
    # assert cycle.wnet == approx(1293.1e3, rel=1e-3)

def test_rankine_reheat_2():
    # https://youtu.be/dr4ez5saGmw?t=2169
    fluid = 'Water'
    p_hi = 8.0    # MPa
    p_mid = 1.00 # MPa
    p_lo = 0.020  # MPa
    T_hi = 440    # deg C
    T_mid = 440   # deg C
    cycle = rankine_reheated(
        p_hi=p_hi, T_hi=T_hi,
        p_mid=p_mid, T_mid=T_mid,
        p_lo=p_lo,  
        fluid=fluid)
    assert cycle.en_eff == approx(0.373, abs=1e-3)
    assert cycle.bwr == approx(0.006, abs=1e-3)
    assert cycle.wnet == approx(1336.7e3, rel=1e-3)