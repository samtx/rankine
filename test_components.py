"""
Run tests by entering

    $ pytest

on the command line.
"""

import pytest
from components import Turbine, Condenser, Pump, Boiler
from thermodynamics import State

def test_turbine_butane():
    fluid = 'n-Butane'
    p_hi = 3.5  # MPa
    p_lo = 0.3  # MPa
    turb_eff = 0.8
    turb = Turbine(eff=turb_eff, p_hi=p_hi*1e6, p_lo=p_lo*1e6, fluid=fluid)
    turb.compute()
    assert turb.work == pytest.approx(74.562095e3)

def test_turbine_water():
    fluid = 'Water'
    p_hi = 2     # MPa
    p_lo = 0.010  # MPa
    turb_eff = 1.0
    turb = Turbine(eff=turb_eff, p_hi=p_hi*1e6, p_lo=p_lo*1e6, fluid=fluid)
    turb.compute()
    assert turb.work == pytest.approx(792e3, abs=1e3)

def test_turbine_superheat_nonintrev():
    fluid = 'Water'
    p_hi = 3.8     # MPa
    p_lo = 0.010  # MPa
    t_hi = 380    # deg C
    turb_eff = 0.86
    turb = Turbine(eff=turb_eff, T_hi=t_hi+273.15, p_hi=p_hi*1e6, p_lo=p_lo*1e6, fluid=fluid)
    turb.compute()
    assert turb.work == pytest.approx(894.1e3, abs=1e3)

def test_condenser():
    fluid = 'Water'
    p = 10 # kPa
    inflow = State(fluid=fluid)
    inflow.fix('p',p*1e3, 'h', 2007.5e3)
    cond = Condenser(p=p*1e3, inflow=inflow, fluid=fluid)
    cond.compute()
    assert cond.heat == pytest.approx(-1815.7e3, abs=1e3)

def test_pump_nonintrev():
    fluid = 'n-Butane'
    p_hi = 3.5    # MPa
    p_lo = 0.300  # MPa
    eff = 0.75
    pump = Pump(eff=eff, p_hi=p_hi*1e6, p_lo=p_lo*1e6, fluid=fluid)
    pump.compute()
    assert pump.work == pytest.approx(-7555.526867)

def test_pump_water():
    fluid = 'Water'
    p_hi = 2.0    # MPa
    p_lo = 0.010  # MPa
    eff = 1.0
    pump = Pump(eff=eff, p_hi=p_hi*1e6, p_lo=p_lo*1e6, fluid=fluid)
    pump.compute()
    assert pump.work == pytest.approx(-2.0e3, rel=0.01)

def test_pump_inflow_state():
    fluid = 'Water'
    p_in = 100 # kPa
    T_in = 30  # deg C
    p_out = 5  # MPa
    inflow = State(fluid=fluid)
    inflow.fix('p',p_in*1e3,'T',T_in+273.15)
    pump = Pump(p_hi=p_out*1e6, inflow=inflow, fluid=fluid)
    pump.compute()
    assert pump.work == pytest.approx(-4.92e3, rel=0.01)

def test_boiler():
    fluid = 'Water'
    p = 2 # MPa
    inflow = State(fluid=fluid)
    inflow.fix('p',p*1e6, 'h', 193.8e3)
    boil = Boiler(p=p*1e6, inflow=inflow, fluid=fluid)
    boil.compute()
    assert boil.heat == pytest.approx(2605.7e3, rel=0.001)

def test_boiler_superheated():
    fluid = 'Water'
    p = 4 # MPa
    T_hi = 400 # deg C
    inflow = State(fluid=fluid)
    inflow.fix('p',p*1e6, 'h', 195.8e3)
    boil = Boiler(p=p*1e6, T_hi=T_hi+273.15, inflow=inflow, fluid=fluid)
    boil.compute()
    assert boil.heat == pytest.approx(3017.8e3, rel=0.001)
