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
STATION_VENT_PRESSURE = 400000  # Pa (3.0 barg)

def run_study(num_stations, station_mass_initial, station_pressure_initial):
    total_mass_received = 0
    total_mass_vented = 0
    trailer_mass = TRAILER_MASS_INITIAL
    trailer_pressure = TRAILER_PRESSURE_INITIAL

    for station in range(num_stations):
        # Step 1: Heat up to station pressure
        _, time_duration = boil_to_pressure(trailer_mass, trailer_pressure, station_pressure_initial)
        
        # Step 2 & 3: Offload with rising pressure and constant pressure
        final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
            station_pressure_initial, station_pressure_initial, trailer_mass, 
            station_mass_initial, STATION_VOLUME, STATION_MAX_MASS / STATION_VOLUME
        )
        
        mass_transfer, _ = offload_const_pressure(
            final_trailer_mass, final_station_mass, final_pressure, 
            STATION_VOLUME, STATION_MAX_MASS / STATION_VOLUME
        )
        
        final_trailer_mass -= mass_transfer
        final_station_mass += mass_transfer
        
        total_mass_received += (final_station_mass - station_mass_initial)
        
        # Update for next iteration
        trailer_mass = final_trailer_mass
        trailer_pressure = final_pressure
        
        # Vent station if pressure is too high
        if final_pressure > STATION_VENT_PRESSURE:
            _, mass_vented_station, _, _ = vent_trailer(final_station_mass, final_pressure, STATION_VENT_PRESSURE)
            total_mass_vented += mass_vented_station

    # Step 4: Boil over during transportation
    pressure_after_transport, _ = boil_over_time(trailer_mass, trailer_pressure, TIME_TRANSPORTATION)
    
    # Step 5: Vent trailer before filling
    mass_after_vent, mass_vented_trailer, _, _ = vent_trailer(trailer_mass, pressure_after_transport, TRAILER_PRESSURE_FILL)
    total_mass_vented += mass_vented_trailer
    
    # Step 6: Fill the trailer
    mass_change, _, _ = fill_trailer_const_pressure(mass_after_vent, TRAILER_MASS_INITIAL, TRAILER_PRESSURE_FILL, TRAILER_VOLUME)
    
    return total_mass_received, total_mass_vented

# Define study parameters
studies = [
    {"num_stations": 2, "starting_mass": 100},
    {"num_stations": 3, "starting_mass": 200},
    {"num_stations": 4, "starting_mass": 350},
    {"num_stations": 5, "starting_mass": 440},
    {"num_stations": 6, "starting_mass": 500}
]

pressures = [250000, 300000, 350000]  # 1.5 barg, 2.0 barg, 2.5 barg

# Run the parametric study
results = {}

for pressure in pressures:
    for study in studies:
        study_key = f"Study {pressures.index(pressure) + 1}.{study['num_stations'] - 1}"
        mass_received, mass_vented = run_study(study['num_stations'], study['starting_mass'], pressure)
        results[study_key] = {
            "num_stations": study['num_stations'],
            "starting_mass": study['starting_mass'],
            "pressure": pressure,
            "mass_received": mass_received,
            "mass_vented": mass_vented
        }

# Print results
print("Parametric Study Results:")
print("-------------------------")
for study_key, result in results.items():
    print(f"{study_key}:")
    print(f"  Number of Stations: {result['num_stations']}")
    print(f"  Starting Mass: {result['starting_mass']} kg")
    print(f"  Initial Pressure: {result['pressure'] / 1e5:.2f} bar")
    print(f"  Total Mass Received: {result['mass_received']:.2f} kg")
    print(f"  Total Mass Vented: {result['mass_vented']:.2f} kg")
    print()

# Analysis
max_received = max(results.items(), key=lambda x: x[1]['mass_received'])
min_vented = min(results.items(), key=lambda x: x[1]['mass_vented'])

print("Analysis:")
print(f"Most efficient for mass received: {max_received[0]}")
print(f"  Mass Received: {max_received[1]['mass_received']:.2f} kg")
print(f"Least mass vented: {min_vented[0]}")
print(f"  Mass Vented: {min_vented[1]['mass_vented']:.2f} kg")