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
TIME_TRANSPORTATION = 1 * 24 * 3600  # 1 day in seconds
station_pressure = 353312 # 2.5 atm
time_transportation = 1 * 24 * 3600  # 1 day in seconds
TRAILER_PRESSURE_FILL = 131000  # Pa
station_max_fill_fraction = 0.95
STATION_VENT_PRESSURE = 353312  # Pa (2.5 atm gauge)
trailer_pressure_max = 1204514.0  # Pa (160 psig, 174.7 psia)

def simulate_scenario():
    # Initial state
    trailer_mass = 1832  # kg
    print(f"Initial trailer mass: {trailer_mass:.2f} kg")

    # 1st Offload
    station_initial_mass = 146  # kg
    station_final_mass = 763  # kg
    station_vented = 27  # kg

    print("\n1st Offload:")
    mass_transferred, gas_vented, trailer_mass, station_mass, _ = offload_const_pressure(
        trailer_mass, station_initial_mass, TRAILER_PRESSURE_FILL, STATION_VOLUME, station_max_fill_fraction
    )
    
    print(f"Calculated mass transferred: {mass_transferred:.2f} kg")
    print(f"Calculated gas vented: {gas_vented:.2f} kg")
    print(f"Calculated station mass after offload: {station_mass:.2f} kg")
    print(f"Actual station mass after offload: {station_final_mass:.2f} kg")
    print(f"Difference: {abs(station_mass - station_final_mass):.2f} kg")
    print(f"Calculated trailer mass after offload: {trailer_mass:.2f} kg")

    # 2nd Offload
    station_initial_mass = 38  # kg
    station_final_mass = 752  # kg
    station_vented = 39  # kg

    print("\n2nd Offload:")
    mass_transferred, gas_vented, trailer_mass, station_mass, _ = offload_const_pressure(
        trailer_mass, station_initial_mass, TRAILER_PRESSURE_FILL, STATION_VOLUME, station_max_fill_fraction
    )
    
    print(f"Calculated mass transferred: {mass_transferred:.2f} kg")
    print(f"Calculated gas vented: {gas_vented:.2f} kg")
    print(f"Calculated station mass after offload: {station_mass:.2f} kg")
    print(f"Actual station mass after offload: {station_final_mass:.2f} kg")
    print(f"Difference: {abs(station_mass - station_final_mass):.2f} kg")
    print(f"Calculated trailer mass after offload: {trailer_mass:.2f} kg")

    # Trailer venting at plant
    vented_mass = 109  # kg
    print("\nTrailer Venting:")
    trailer_mass_after_vent, mass_vented, _, _ = vent_trailer(trailer_mass, station_pressure, TRAILER_PRESSURE_FILL)
    print(f"Calculated vented mass: {mass_vented:.2f} kg")
    print(f"Actual vented mass: {vented_mass:.2f} kg")
    print(f"Difference: {abs(mass_vented - vented_mass):.2f} kg")
    print(f"Calculated trailer mass after venting: {trailer_mass_after_vent:.2f} kg")

    # Trailer refill
    final_trailer_mass = 2014  # kg
    print("\nTrailer Refill:")
    change_mass, _, _ = fill_trailer_const_pressure(trailer_mass_after_vent, final_trailer_mass, TRAILER_PRESSURE_FILL, TRAILER_VOLUME)
    print(f"Calculated mass added: {change_mass:.2f} kg")
    print(f"Actual mass added: {final_trailer_mass - trailer_mass_after_vent:.2f} kg")
    print(f"Difference: {abs(change_mass - (final_trailer_mass - trailer_mass_after_vent)):.2f} kg")

if __name__ == "__main__":
    simulate_scenario()
