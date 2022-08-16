#!/usr/bin/env python3

from marilib.tools import units as unit

from marilib.aircraft_model.airplane import viewer as show

from marilib.aircraft_data.aircraft_description import Aircraft

from marilib.processes import assembly as run, initialization as init

from datetime import datetime as dt

import matplotlib.pyplot as plt

import pandas as pd
import pickle

def saveDraw_view (f_name, ac_for_print, win_t, plot_t):
    show.draw_3d_view(ac_for_print, win_t, plot_t)
    #plt.show()
    plt.savefig("./_results/" + f_name + ".png")
    plt.show()
    #print("great")
    return
def v_input(question, input_type):
    input_para = False
    while type(input_para) is not input_type:
        try:
            input_para = input_type(input(question))
        except ValueError:
            print("please enter a ", input_type)
    return input_para

#==============================
# Define list of cases to be input for design
#==============================
# 0:n_engine, 1:n_pax_ref, 2:design_range(NM), 3:cruise_mach, 4:process
schedule = [
            #[4, 500, 7000, 0.7, '1'] #no result
            #[4, 500, 7000, 0.78, '1'], #no result
            #[4, 500, 8000, 0.7, '1'], #no result
            #[4, 500, 8000, 0.8, '1'], #no result
            #[4, 500, 8000, 0.85, '1'], #no result
            #[4, 500, 8000, 0.78, '1'], #no result
            #[4, 600, 6000, 0.7, '1'], #no result
            #[4, 600, 6000, 0.78, '1'], #no result
            #[4, 600, 7000, 0.7, '1'], #no result
            #[4, 600, 7000, 0.8, '1'], #no result
            #[4, 600, 7000, 0.85, '1'], #Climb to cross over altitude is not possible
            #[4, 600, 7000, 0.78, '1'], #no result
            #[4, 100, 5000, 0.7, '1'], #Climb to top of climb is not possible
            #[4, 100, 4000, 0.7, '1'], #Climb to top of climb is not possible
            #[4, 100, 6000, 0.7, '1'], #Climb to top of climb is not possible, no result
            #[4, 150, 6000, 0.8, '1'], #no result
            #[2, 250, 4000, 0.8, '2'], #failed case
            #[4, 100, 7000, 0.8, '2'],
            #[4, 300, 7000, 0.8, '2'],
            #[4, 400, 7000, 0.8, '2']
            #[4, 100, 3000, 0.8, '2'],
            #[4, 150, 3000, 0.8, '2'],
            #[4, 250, 3000, 0.8, '2'],
            #[4, 300, 3000, 0.8, '2'],
            #[4, 400, 3000, 0.8, '2'],
            #[4, 500, 3000, 0.8, '2'],
            #[4, 600, 3000, 0.8, '2'],
            #[4, 300, 4000, 0.8, '2'],
            #[4, 300, 5000, 0.8, '2'],
            #[4, 300, 6000, 0.8, '2'],
            #[4, 300, 7000, 0.8, '2']
            ]

failed_cases=[]

for s in schedule:
    try:

        #======================================================================================================
        # Initialization
        #======================================================================================================
        propulsive_architecture = 1 # 1:turbofan, 2:partial turboelectric

        number_of_engine = s[0]
        aircraft = Aircraft(propulsive_architecture)

        n_pax_ref = s[1]
        design_range = unit.m_NM(s[2])
        cruise_mach = s[3]
        design_choice = s[4]
        #------------------------------------------------------------------------------------------------------
        run.aircraft_initialize(aircraft, n_pax_ref, design_range, cruise_mach, propulsive_architecture, number_of_engine)

        print("-------------------------------------------")
        print("Initialization : done")

        #Use MDA or MDF
        if design_choice!="2":  #full MDA
            #======================================================================================================
            # Modify initial values here
            #======================================================================================================

            aircraft.turbofan_engine.reference_thrust = -(-aircraft.turbofan_engine.reference_thrust//100000) * 100000
            aircraft.wing.area = -(-aircraft.wing.area//100) * 100
            title = "MDA " + str(number_of_engine) + "engine," + str(n_pax_ref) + "pax," + str(unit.NM_m(design_range)) + "|Mach" + str(cruise_mach)
            print(title)
            print(f'reference thrust: {aircraft.turbofan_engine.reference_thrust} N')
            print(f'reference wing area: {aircraft.wing.area}')
            #======================================================================================================
            # MDA process
            #======================================================================================================

            # Initialization of HTP and VTP areas, compulsory with mda3
            #------------------------------------------------------------------------------------------------------
            run.eval_mda0(aircraft)

            # Full MDA process
            #------------------------------------------------------------------------------------------------------
            run.eval_mda3(aircraft)

            print("-------------------------------------------")
            print("Sequence : done")

        else:   #MDF
            #======================================================================================================
            # Design process
            #======================================================================================================
            title = "MDF " + str(number_of_engine) + "engine," + str(n_pax_ref) + "pax," + str(unit.NM_m(design_range)) + "|Mach" + str(cruise_mach)

            #------------------------------------------------------------------------------------------------------
            print(title)
            print(f'Reference thrust = {aircraft.turbofan_engine.reference_thrust} N')
            print(f'Reference wing area = {aircraft.wing.area} m2')

            t_lowBnd = (aircraft.turbofan_engine.reference_thrust//100000)*100000
            t_UpBnd = (-(-aircraft.turbofan_engine.reference_thrust//100000) + 3)*100000
            a_lowBnd = (aircraft.wing.area//100)*100
            a_upBnd = (-(-aircraft.wing.area//100) + 3)*100

            thrust_bnd = (t_lowBnd,t_UpBnd)
            area_bnd = (a_lowBnd,a_upBnd)
            search_domain = (thrust_bnd,area_bnd)
            print(f'thrust_bnd: {thrust_bnd}')
            print(f'area_bnd: {area_bnd}')

            # Perform MDF optimization
            #------------------------------------------------------------------------------------------------------
            criterion = "MTOW"

            run.mdf_process(aircraft,search_domain,criterion)
            #run.plot_mdf_process(aircraft,search_domain,criterion)
            print("-------------------------------------------")
            print("Optimization : done")

        aircraft.name = title

        #======================================================================================================
        # Print some results
        #======================================================================================================

        aircraft_data = Aircraft.get_data_dict(aircraft)
        suffix_time = dt.now().strftime("%Y%m%d%H%M%S")
        file_name1 = "./_airplane-data/ac-d_" + suffix_time
        with open(file_name1+".dict", 'wb') as handle:
            pickle.dump(aircraft_data, handle)

        line = "Turbofan (1) or Partial turboelectric (2): " + "%.0f"%propulsive_architecture
        if design_choice=="2":
            line += "\nUsing MDF process: (thrust = " + str(thrust_bnd) + ") (area = " + str(area_bnd) + ")"
        else:
            line += "\nUsing full MDA process"
        line += "\nEvaluation mission cash op cost = " + "%.0f"%aircraft.economics.cash_operating_cost + " $"
        line += "\nNumber of passengers = " + "%.0f"%aircraft.cabin.n_pax_ref + " int"
        line += "\nDesign range = " + "%.0f"%unit.NM_m(aircraft.design_driver.design_range) + " NM"
        line += "\nCruise Mach number = " + "%.2f"%aircraft.design_driver.cruise_mach + " Mach"
        line += "\n-------------------------------------------"
        line += "\nReference thrust turbofan = " + "%.0f"%aircraft.turbofan_engine.reference_thrust + " N"
        line += "\nReference thrust effective = " + "%.0f"%aircraft.propulsion.reference_thrust_effective + " N"
        line += "\nTurbofan mass = " + "%.0f"%aircraft.turbofan_nacelle.mass + " kg"
        line += "\nCruise SFC = " + "%.4f"%(aircraft.propulsion.sfc_cruise_ref*36000) + " kg/daN/h"
        line += "\nCruise LoD = " + "%.4f"%(aircraft.aerodynamics.cruise_lod_max) + " no_dim"
        line += "\n-------------------------------------------"
        line += "\nWing area = " + "%.2f"%aircraft.wing.area + " m2"
        line += "\nWing span = " + "%.2f"%aircraft.wing.span + " m"
        line += "\n-------------------------------------------"
        line += "\nWing position = " + "%.2f"%aircraft.wing.x_root + " m"
        line += "\nHTP area = " + "%.2f"%aircraft.horizontal_tail.area + " m2"
        line += "\nVTP area = " + "%.2f"%aircraft.vertical_tail.area + " m2"
        line += "\n-------------------------------------------"
        line += "\nFuselage length = " + "%.2f"%aircraft.fuselage.length + " m"
        line += "\nFuselage width = " + "%.2f"%aircraft.fuselage.width + " m"
        line += "\n-------------------------------------------"
        line += "\nMTOW = " + "%.2f"%aircraft.weights.mtow + " kg"
        line += "\nMLW = " + "%.2f"%aircraft.weights.mlw + " kg"
        line += "\nOWE = " + "%.2f"%aircraft.weights.owe + " kg"
        line += "\nMWE = " + "%.2f"%aircraft.weights.mwe + " kg"
        line += "\n-------------------------------------------"
        line += "\nDesign range = " + "%.0f"%unit.NM_m(aircraft.design_driver.design_range) + " NM"
        line += "\nEffective nominal range = " + "%.0f"%unit.NM_m(aircraft.nominal_mission.range)+" NM"
        line += "\n"
        line += "\nTake off field length required = "+"%.0f"%aircraft.low_speed.req_tofl+" m"
        line += "\nTake off field length effective = "+"%.0f"%aircraft.low_speed.eff_tofl+" m"
        line += "\n"
        line += "\nApproach speed required= "+"%.1f"%unit.kt_mps(aircraft.low_speed.req_app_speed)+" kt"
        line += "\nApproach speed effective = "+"%.1f"%unit.kt_mps(aircraft.low_speed.eff_app_speed)+" kt"
        line += "\n"
        line += "\nOne engine ceiling path required = " + "%.1f"%(aircraft.low_speed.req_oei_path*100) + " %"
        line += "\nOne engine ceiling path effective = " + "%.1f"%(aircraft.low_speed.eff_oei_path*100) + " %"
        line += "\n"
        line += "\nClimb speed required in MCL rating = " + "%.1f"%unit.ftpmin_mps(aircraft.high_speed.req_vz_climb)+" ft/min"
        line += "\nClimb speed effective in MCL rating = " + "%.1f"%unit.ftpmin_mps(aircraft.high_speed.eff_vz_climb)+" ft/min"
        line += "\n"
        line += "\nClimb speed required in MCR rating = " + "%.1f"%unit.ftpmin_mps(aircraft.high_speed.req_vz_cruise)+" ft/min"
        line += "\nClimb speed effective in MCR rating = " + "%.1f"%unit.ftpmin_mps(aircraft.high_speed.eff_vz_cruise)+" ft/min"
        line += "\n"
        line += "\nTime to climb required = " + "%.1f"%unit.min_s(aircraft.high_speed.req_ttc)+" min"
        line += "\nTime to climb effective = " + "%.1f"%unit.min_s(aircraft.high_speed.eff_ttc)+" min"
        line += "\n-------------------------------------------"
        line += "\nEvaluation mission range = " + "%.0f"%unit.NM_m(aircraft.cost_mission.range) + " NM"
        line += "\nEvaluation mission block fuel = " + "%.0f"%aircraft.cost_mission.block_fuel + " kg"
        line += "\nEvaluation mission cash op cost = " + "%.0f"%aircraft.economics.cash_operating_cost + " $"
        line += "\nCO2 metric = " + "%.4f"%(aircraft.environmental_impact.CO2_metric*1000) +" kg/km/m0.48"

        file_name = "study-airplane_results_" + suffix_time
        with open("./_results/"+file_name+".txt",'w') as f:
            f.write(line)
        #print(line)

        # airplane 3D view
        #------------------------------------------------------------------------------------------------------
        print("-------------------------------------------")
        print("3 view drawing : launched")
        saveDraw_view(file_name, aircraft, file_name, title) #calling the show 3d view function in MARILib
    except:
        failed_cases.append(s)
print(f'Failed cases: {failed_cases}')
