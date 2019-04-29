# Model the Rankine Cycle with Geothermal Brine Heat Source

from __future__ import print_function
import matplotlib   # for pretty pictures
matplotlib.use('Agg') # to get matplotlib to save figures to a file instead of using X windows
import matplotlib.pyplot as plt
import sys
from prettytable import PrettyTable, MSWORD_FRIENDLY, PLAIN_COLUMNS #for output formatting
import CoolProp.CoolProp as CP
from numbers import Number

##############################################################################
# ------------------- Print output functions ---------------------------------
##############################################################################

def print_output_to_screen(plant,props):
    in_kW = props.get('in_kW',False)
    print_user_values(props)
    print('Rankine Cycle States and Processes    (Working Fluid: '+plant.rank.fluid+')')
    print('\nStates:')
    print_state_table(plant.rank,in_kW)
    print('\nProcess Energy:')
    print_process_table(plant.rank,in_kW)
    print('\nProcess Exergy:')
    print_exergy_table(plant.rank,in_kW)
    # create_plot(plant.rank, props)
    print('\nGeothermal Cycle States and Processes    (Brine: '+plant.geo.fluid+')')
    print_state_table(plant.geo,in_kW)
    if plant.geo.get_procs():
        # only print process table for brine if processes have been defined.
        print_process_table(plant.geo,in_kW)
        print_exergy_table(plant.geo,in_kW)
    print_plant_results(plant)
    return

def print_user_values(props):
    # print values to screen
    fluid = props.get('fluid',None)
    p_hi = props.get('p_hi',None)
    p_lo = props.get('p_lo',None)
    t_hi = props.get('t_hi',None)
    t_lo = props.get('t_lo',None)
    turb_eff = props.get('turb_eff',1.0)
    pump_eff = props.get('pump_eff',1.0)
    print('\nUser entered values\n-------------------')
    print('Working Fluid: '+fluid)
    if t_lo: print('Low Temperature:  {:>3.1f} deg C'.format(t_lo))
    if t_hi: print('High Temperature: {:>3.1f} deg C'.format(t_hi))
    if p_lo: print('Low Pressure:  {:>5.4f} MPa'.format(p_lo))
    if p_hi: print('High Pressure: {:>5.4f} MPa'.format(p_hi))
    print('Isentropic Turbine Efficiency: {:>2.1f}%'.format(props["turb_eff"]*100))
    print('Isentropic Pump Efficiency:    {:>2.1f}%'.format(props["pump_eff"]*100))
    print('Plant Cooling Efficiency:      {:>2.1f}%\n'.format(props["cool_eff"]*100))
    return

def print_state_table(cycle,in_kW=False):
    s_list = cycle.get_states()
    s_list.append(cycle.dead)
    if in_kW:
        headers = ['State','P(kPa)','T(deg C)','H(kW)','S(kW/K)','Ef(kW)','x']
    else:
        headers = ['State','P(kPa)','T(deg C)','h(kJ/kg)','s(kJ/kg.K)','ef(kJ/kg)','x']
    t = PrettyTable(headers)
    for item in headers[1:6]:
        t.align[item] = 'r'
    for item in headers[2:4]:
        t.float_format[item] = '4.2'
    t.float_format[headers[1]] = '5.0'
    t.float_format[headers[4]] = '6.5'
    t.float_format[headers[5]] = '4.2'
    t.float_format[headers[6]] = '0.2'
    t.padding_width = 1
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for item in s_list:
        #print('item.name = ',item.name)
        t.add_row([item.name[:6],
                   item.p/1000,
                   item.T-273,
                   item.h/1000 * mdot,
                   item.s/1000 * mdot,
                   item.ef/1000 * mdot,
                   item.x])
    print(t)
    return

def print_process_table(cycle,in_kW=False):
    p_list = cycle.get_procs()
    if in_kW:
        headers = ['Process','State','Q(kW)','W(kW)']
    else:
        headers = ['Process','State','Q(kJ/kg)','W(kJ/kg)']
    t = PrettyTable(headers)
    #t.set_style(MSWORD_FRIENDLY)
    for item in headers[2:]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for p in p_list:
        t.add_row([p.name[:7],p.inflow.name[:5]+' -> '+p.outflow.name[:5],
                   p.heat/1000 * mdot,
                   p.work/1000 * mdot])
    # add totals row
    t.add_row(['Net','',
               cycle.qnet/1000 * mdot,
               cycle.wnet/1000 * mdot])
    print(t)
    return

def print_exergy_table(cycle,in_kW):
    p_list = cycle.get_procs()
    if in_kW:
        headers = ['Proc','State','Ex.In(kW)','Ex.Out(kW)','Delt.Ef(kW)','Ex.D(kW)','Ex.Eff.','Ex.Bal']
    else:
        headers = ['Proc','State','Ex.In(kJ/kg)','Ex.Out(kJ/kg)','delt.ef(kJ/kg)','Ex.D(kJ/kg)','Ex.Eff.','Ex.Bal']
    t = PrettyTable(headers)
    #t.set_style(MSWORD_FRIENDLY)
    for item in headers[2:]:
        t.align[item] = 'r'
        t.float_format[item] = '5.1'
    if in_kW:
        mdot = cycle.mdot
    else:
        mdot = 1.0
    for p in p_list:
        t.add_row([p.name[:4],p.inflow.name[:5]+'->'+p.outflow.name[:5],
                   p.ex_in/1000 * mdot,
                   p.ex_out/1000 * mdot,
                   p.delta_ef/1000 * mdot,
                   p.ex_d/1000 * mdot,
                   '{:.1%}'.format(p.ex_eff),
                   p.ex_bal/1000 * mdot])
    # add totals row
    t.add_row(['Net','',
               cycle.ex_in/1000 * mdot,
               cycle.ex_out/1000 * mdot,
               cycle.delta_ef/1000 * mdot,
               cycle.ex_d/1000 * mdot,
               '{:.1%}'.format(cycle.ex_eff),
               'n/a'])
    print(t)
    return

def print_cycle_values(cycle):
    print('\nCycle Values \n------------ ')
    print('thermal efficiency = {:2.1f}%'.format(cycle.en_eff*100))
    print('back work ratio = {:.3f}'.format(cycle.bwr))
    return

def create_plot(cycle, props):
    p_list = cycle.get_states()
    s_list = cycle.get_states()
    superheat = s_list[3].name
    fluid = cycle.fluid

    #Check to see if the system is superheated
    if superheat == '2b':

      st_1 = s_list[0]
      st_2s = s_list[1]
      st_2 = s_list[2]
      st_2b= s_list[3]
      st_3 = s_list[4]
      st_4s = s_list[5]
      st_4 = s_list[6]
      st_4b = s_list[7]
      T_pts = [st_1.T, st_2s.T, st_2.T, st_2b.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
      s_pts = [st_1.s, st_2s.s, st_2.s, st_2b.s, st_3.s, st_4s.s, st_4b.s, st_1.s]
    else:
      st_1 = s_list[0]
      st_2s = s_list[1]
      st_2 = s_list[2]
      st_3 = s_list[3]
      st_4s = s_list[4]
      st_4 = s_list[5]
      st_4b = s_list[6]
      T_pts = [st_1.T, st_2s.T, st_2.T, st_3.T, st_4s.T, st_4b.T, st_1.T] # solid lines
      s_pts = [st_1.s, st_2s.s, st_2.s, st_3.s, st_4s.s, st_4b.s, st_1.s]

    # unpack processes
    turb = p_list[0]
    cond = p_list[1]
    pump = p_list[2]
    boil = p_list[3]
    #get the points to plot the saturation dome

    (dspts,dtpts) = get_sat_dome(cycle)


    s_dash_12 = [st_1.s, st_2.s]
    T_dash_12 = [st_1.T, st_2.T]
    s_dash_34 = [st_3.s, st_4.s]
    T_dash_34 = [st_3.T, st_4.T]
    #s_super

    # Draw T-s plot
    plt.clf()
    plt.plot(s_pts,T_pts, 'b')
    plt.plot(s_dash_12,T_dash_12,'g--',s_dash_34,T_dash_34,'g--')
    #PropsPlot(cycle.fluid,'Ts',units="KSI")
    #plotting the vapor dome...hopefully
    plt.plot(dspts,dtpts, 'r--')
    #appropriate point labels for the plot
    if superheat == '2b':
      #points for a superheated fluid
      plt.annotate("1.", xy = (s_pts[0],T_pts[0]) , xytext = (s_pts[0] + 2,T_pts[0]+20 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("2s.", xy = (s_pts[1],T_pts[1]) , xytext = (s_pts[1] + 2,T_pts[1]+25 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
      plt.annotate("2.", xy = (s_pts[2],T_pts[2]) , xytext = (s_pts[2] + 2,T_pts[2]+25 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("3.", xy = (s_pts[4],T_pts[4]) , xytext = (s_pts[4] - 800,T_pts[4] ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("4./4s.", xy =  (s_pts[5],T_pts[5]) , xytext = (s_pts[5] + 2,T_pts[5]+30 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      #plt.annotate("2B", xy =  (s_pts[3],T_pts[3]) , xytext = (s_pts[3] + 2,T_pts[3]+30 ), arrowprops=dict(facecolor = 'red', shrink=0.05),)
    else:
    #points for no superheated fluid
      plt.annotate("1.", xy = (s_pts[0],T_pts[0]) , xytext = (s_pts[0] + 2,T_pts[0]+20 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("2s.", xy = (s_pts[1],T_pts[1]) , xytext = (s_pts[1] + 2,T_pts[1]+25 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
      plt.annotate("2.", xy = (s_pts[2],T_pts[2]) , xytext = (s_pts[2] + 2,T_pts[2]+25 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("3.", xy = (s_pts[3],T_pts[3]) , xytext = (s_pts[3] - 800,T_pts[3] ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      plt.annotate("4./4s.", xy =  (s_pts[4],T_pts[4]) , xytext = (s_pts[4] + 2,T_pts[4]+30 ), arrowprops=dict(facecolor = 'magenta', shrink=0.05),)
      #plt.annotate("b.", xy =  (s_pts[5],T_pts[5]) , xytext = (s_pts[5] + 2,T_pts[5]+30 ), arrowprops=dict(facecolor = 'red', shrink=0.05),)

    #plt.annotate("4b.", xy = (s_dash_34[1],T_dash_34[1]) , xytext = (s_dash_34[1] + 500, T_dash_34[1] + 2 ), arrowprops=dict(facecolor = 'black', shrink=0.05),)
    title_txt = 'Rankine Cycle T-S Diagram: ' + fluid
    #print (title_txt)
    plt.suptitle(title_txt)
    plt.xlabel("Entropy (J/kg.K)")
    plt.ylabel("Temperature (deg K)")
    # Save plot
    filename = 'ts_plot.png'
    plt.savefig(filename) # save figure to directory
    return

def print_plant_results(plant):
    print('Plant Results \n------------------ ')
    print('Rankine Cycle mass flow rate  =   {:>3.2f} kg/s'.format(plant.rank.mdot))
    print('Geo. Brine mass flow rate     =   {:>3.2f} kg/s'.format(plant.geo.mdot))
    print('Plant thermal (energetic) eff = {:>6.1f}%'.format(plant.en_eff*100))
    print('Plant exergetic efficiency    = {:>6.1f}%'.format(plant.ex_eff*100))
    print('Plant cooling eff. (user specified) = {:>6.1f}%'.format(plant.cool_eff*100))
    print('Rankine cycle thermal eff     = {:>6.1f}%'.format(plant.rank.en_eff*100))
    print('Rankine cycle exergetic eff   = {:>6.1f}%'.format(plant.rank.ex_eff*100))
    print('Rankine cycle back work ratio =  {:>6.2f}%'.format(plant.rank.bwr*100))
    return


def get_sat_dome(cycle):
    fluid = cycle.fluid
    slist = cycle.get_states()
    # find min temp to use for dome
    t_state_min = 300  # default room temp in K
    #print('slist:',slist)
    for state in slist[:-1]:
        #print('state.T:',state.T)
        t_state_min = min([state.T,t_state_min])
    t_fluid_min = CP.PropsSI('TMIN',fluid)
    #print('t_fluid_min:',t_fluid_min)
    #print('t_state_min:',t_state_min)
    tmin = max([t_fluid_min,t_state_min-10]) # add 10 deg cushion
    tcrit = CP.PropsSI('TCRIT',fluid)  # critical temp for fluid
    #print('tcrit=',tcrit,' pcrit=',pcrit,' scrit=',scrit)
    liq_pts = []
    vap_pts = []
    tpts = []
    spts = []

    # for temps from tmin to tmax, find entropy at both sat liq and sat vap.
    t = tmin  # initial temp for dome
    dt = 1.0
    #print('tmin:',tmin)
    while t < tcrit:
        s = CP.PropsSI('S','T',t,'Q',0,fluid)
        liq_pts.append((s,t))
        s = CP.PropsSI('S','T',t,'Q',1,fluid)
        vap_pts.append((s,t))
        t += dt
    # now, unravel the liq_pts and vap_pts tuples to make the spts and tpts lists
    for item in liq_pts:
        spts.append(item[0])
        tpts.append(item[1])
    for item in vap_pts[::-1]:
        spts.append(item[0])
        tpts.append(item[1])
    return spts, tpts