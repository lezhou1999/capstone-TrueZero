import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from AllFunctions import (boil_to_pressure, offload_with_raising_pressure, 
                          offload_const_pressure, boil_over_time, vent_trailer, 
                          fill_trailer_const_pressure)

# Initialize REFPROP
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum

# Constants
TRAILER_VOLUME = 32.0  # m^3
STATION_VOLUME = 13.33  # m^3
TRAILER_MASS_INITIAL = 2100  # kg
TRAILER_PRESSURE_INITIAL = 160000  # Pa
TIME_TRANSPORTATION = 1 * 24 * 3600  # 1 day in seconds
TRAILER_PRESSURE_FILL = 131000  # Pa
STATION_MAX_MASS = 800  # kg
STATION_MAX_PRESSURE = 400000  # Pa (3.0 barg)
STATION_VENT_PRESSURE = STATION_MAX_PRESSURE * 0.9  # 90% of max pressure
trailer_pressure_max = 1204514.0  # Pa (160 psig, 174.7 psia)
STATION_MAX_FILL_FRACTION = 0.95

def run_study(study_id, num_stations, station_mass_initial, station_pressure_initial):
    print(f"\nRunning Study {study_id}")
    print(f"Number of stations: {num_stations}")
    print(f"Initial station mass: {station_mass_initial} kg")
    print(f"Initial station pressure: {station_pressure_initial} Pa")
    print(f"Initial trailer mass: {TRAILER_MASS_INITIAL} kg")
    print(f"Initial trailer pressure: {TRAILER_PRESSURE_INITIAL} Pa")

    total_mass_received = 0
    total_mass_vented = 0
    trailer_mass = TRAILER_MASS_INITIAL
    trailer_pressure = TRAILER_PRESSURE_INITIAL

    for station in range(num_stations):
        print(f"\nOffloading to Station {station + 1}")
        print(f"Trailer mass before offload: {trailer_mass:.2f} kg")
        print(f"Trailer pressure before offload: {trailer_pressure:.2f} Pa")

        # Step 1: Heat up to station pressure
        print(f"Heating trailer from {trailer_pressure:.2f} Pa to {station_pressure_initial:.2f} Pa")
        final_enthalpy, time_duration = boil_to_pressure(trailer_mass, trailer_pressure, station_pressure_initial)
        print(f"Time to heat up: {time_duration:.2f} seconds")
        print(f"Final enthalpy after heating: {final_enthalpy:.2f} J/kg")

        # Update trailer pressure after heating
        trailer_pressure = station_pressure_initial
        print(f"Trailer pressure after heating: {trailer_pressure:.2f} Pa")

        # Step 2: Offload with rising pressure
        print("Starting offload with raising pressure")
        final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
            trailer_pressure, station_pressure_initial, trailer_mass, 
            station_mass_initial, STATION_VOLUME, STATION_MAX_MASS, STATION_MAX_PRESSURE, trailer_pressure_max, TRAILER_VOLUME 
        )
        print(f"After raising pressure offload:")
        print(f"  Final pressure: {final_pressure:.2f} Pa")
        print(f"  Final station mass: {final_station_mass:.2f} kg")
        print(f"  Final trailer mass: {final_trailer_mass:.2f} kg")
        
        if final_trailer_mass == trailer_mass:
            print("Warning: No mass was transferred during offload_with_raising_pressure")

        # Step 3: Vent station if pressure reached STATION_MAX_PRESSURE
        if final_pressure > STATION_VENT_PRESSURE:
            print(f"Station pressure {final_pressure:.2f} Pa reached max pressure. Venting station.")
            final_station_mass, mass_vented_station, _, _ = vent_trailer(final_station_mass, final_pressure, STATION_VENT_PRESSURE)
            total_mass_vented += mass_vented_station
            print(f"Vented {mass_vented_station:.2f} kg from station")
            print(f"Station mass after venting: {final_station_mass:.2f} kg")
            final_pressure = STATION_VENT_PRESSURE
            print(f"Station pressure after venting: {final_pressure:.2f} Pa")

        # Calculate station maximum mass
        station_max_mass = STATION_VOLUME * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, final_pressure, 0, [1.0]).Output[0] * STATION_MAX_FILL_FRACTION

        # Step 4: Offload with constant pressure (if station is not full)
        if final_station_mass < station_max_mass:
            print("Starting offload with constant pressure")
            mass_transfer, gas_vented, final_trailer_mass, final_station_mass, energy_added = offload_const_pressure(
                final_trailer_mass, final_station_mass, final_pressure, 
                STATION_VOLUME, STATION_MAX_FILL_FRACTION
            )
            print(f"Mass transferred during constant pressure: {mass_transfer:.2f} kg")
            print(f"Gas vented during constant pressure: {gas_vented:.2f} kg")
            print(f"Energy added during constant pressure: {energy_added:.2f} J")
            
            total_mass_vented += gas_vented
        else:
            print("Skipping constant pressure offload - station is already full")
        
        mass_received = final_station_mass - station_mass_initial
        total_mass_received += mass_received

        print(f"Total mass transferred to station: {mass_received:.2f} kg")
        print(f"Final station mass: {final_station_mass:.2f} kg")
        print(f"Trailer mass after offload: {final_trailer_mass:.2f} kg")
        
        # Update for next iteration
        trailer_mass = final_trailer_mass
        trailer_pressure = final_pressure

    # Step 5: Boil over during transportation
    print(f"\nSimulating boil-over during transportation")
    print(f"Initial trailer mass: {trailer_mass:.2f} kg")
    print(f"Initial trailer pressure: {trailer_pressure:.2f} Pa")
    pressure_after_transport, quality_after_transport = boil_over_time(trailer_mass, trailer_pressure, TIME_TRANSPORTATION)
    print(f"Pressure after transport: {pressure_after_transport:.2f} Pa")
    # print(f"Quality after transport: {quality_after_transport:.4f}")
    
    # Step 6: Vent trailer before filling
    print(f"\nVenting trailer from {pressure_after_transport:.2f} Pa to {TRAILER_PRESSURE_FILL} Pa")
    mass_after_vent, mass_vented_trailer, mass_liq_final, mass_gas_final = vent_trailer(trailer_mass, pressure_after_transport, TRAILER_PRESSURE_FILL)
    total_mass_vented += mass_vented_trailer
    print(f"Mass vented from trailer: {mass_vented_trailer:.2f} kg")
    print(f"Mass after venting: {mass_after_vent:.2f} kg")
    print(f"Liquid mass after venting: {mass_liq_final:.2f} kg")
    # print(f"Gas mass after venting: {mass_gas_final:.2f} kg")
    
    # Step 7: Fill the trailer
    print(f"\nFilling trailer from {mass_after_vent:.2f} kg to {TRAILER_MASS_INITIAL} kg")
    mass_change, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_after_vent, TRAILER_MASS_INITIAL, TRAILER_PRESSURE_FILL, TRAILER_VOLUME)
    print(f"Mass added to refill trailer: {mass_change:.2f} kg")
    print(f"Liquid mass added: {mass_liq_added:.2f} kg")
    print(f"Gas mass added: {mass_gas_added:.2f} kg")

    print(f"\nStudy {study_id} Results:")
    print(f"Total mass received by stations: {total_mass_received:.2f} kg")
    print(f"Total mass vented: {total_mass_vented:.2f} kg")
    print("----------------------------------------")

    return total_mass_received, total_mass_vented

# Define study parameters
studies = [
    {"id": "1.1", "num_stations": 2, "starting_mass": 100, "pressure": 250000},
    {"id": "2.1", "num_stations": 2, "starting_mass": 100, "pressure": 300000},
    {"id": "3.1", "num_stations": 2, "starting_mass": 100, "pressure": 350000},
    {"id": "1.2", "num_stations": 3, "starting_mass": 200, "pressure": 250000},
    {"id": "2.2", "num_stations": 3, "starting_mass": 200, "pressure": 300000},
    {"id": "3.2", "num_stations": 3, "starting_mass": 200, "pressure": 350000},
    {"id": "1.3", "num_stations": 4, "starting_mass": 350, "pressure": 250000},
    {"id": "2.3", "num_stations": 4, "starting_mass": 350, "pressure": 300000},
    {"id": "3.3", "num_stations": 4, "starting_mass": 350, "pressure": 350000},
    {"id": "1.4", "num_stations": 5, "starting_mass": 440, "pressure": 250000},
    {"id": "2.4", "num_stations": 5, "starting_mass": 440, "pressure": 300000},
    {"id": "3.4", "num_stations": 5, "starting_mass": 440, "pressure": 350000},
    {"id": "1.5", "num_stations": 6, "starting_mass": 500, "pressure": 250000},
    {"id": "2.5", "num_stations": 6, "starting_mass": 500, "pressure": 300000},
    {"id": "3.5", "num_stations": 6, "starting_mass": 500, "pressure": 350000},
]

# Function to run a single study
def run_single_study(study_id):
    study = next((s for s in studies if s["id"] == study_id), None)
    if study:
        return run_study(study["id"], study["num_stations"], study["starting_mass"], study["pressure"])
    else:
        print(f"Study {study_id} not found.")
        return None

# Function to run all studies
def run_all_studies():
    results = {}
    for study in studies:
        mass_received, mass_vented = run_study(study["id"], study["num_stations"], study["starting_mass"], study["pressure"])
        results[study["id"]] = {
            "num_stations": study["num_stations"],
            "starting_mass": study["starting_mass"],
            "pressure": study["pressure"],
            "mass_received": mass_received,
            "mass_vented": mass_vented
        }
    return results

# Analysis function
def analyze_results(results):
    print("\nFinal Results for All Studies:")
    for study_id, data in results.items():
        print(f"\nStudy {study_id}:")
        print(f"  Number of stations: {data['num_stations']}")
        print(f"  Starting mass: {data['starting_mass']} kg")
        print(f"  Pressure: {data['pressure']} Pa")
        print(f"  Total mass received: {data['mass_received']:.2f} kg")
        print(f"  Total mass vented: {data['mass_vented']:.2f} kg")

    print("\nAnalysis:")
    max_received = max(results.items(), key=lambda x: x[1]['mass_received'])
    min_vented = min(results.items(), key=lambda x: x[1]['mass_vented'])

    print(f"Most efficient for mass received: Study {max_received[0]}")
    print(f"  Mass Received: {max_received[1]['mass_received']:.2f} kg")
    print(f"Least mass vented: Study {min_vented[0]}")
    print(f"  Mass Vented: {min_vented[1]['mass_vented']:.2f} kg")

# Main execution
if __name__ == "__main__":
    while True:
        print("\nParametric Study Options:")
        print("1. Run a single study")
        print("2. Run all studies")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            study_id = input("Enter the study ID (e.g., 1.1, 2.3, etc.): ")
            run_single_study(study_id)
        elif choice == '2':
            results = run_all_studies()
            analyze_results(results)
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
