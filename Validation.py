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
TRAILER_PRESSURE_FILL = 131000  # Pa
station_max_fill_fraction = 0.95
STATION_MAX_MASS = 870 * station_max_fill_fraction   # kg
STATION_VENT_PRESSURE = 353312  # Pa (2.5 atm gauge)
station_max_fill_fraction = 0.95
trailer_pressure_max = 1204514.0  # Pa (160 psig, 174.7 psia)


def validate_offload(trailer_mass, station_mass_initial, station_pressure_initial):
    # Step 1 & 2: Offload with rising pressure and constant pressure
    print("Starting Offload with rising pressure")
    final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
        station_pressure_initial, station_pressure_initial, trailer_mass, 
        station_mass_initial, STATION_VOLUME,  STATION_MAX_MASS, STATION_VENT_PRESSURE, trailer_pressure_max, TRAILER_VOLUME
    )
    print(f"After rising pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")
    print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
    print(f"Final station mass: {final_station_mass:.2f} kg")
    print(f"Final trailer pressure: {final_pressure:.2f} Pa")
    print(f"Final station pressure: {final_pressure:.2f} Pa")

    # Calculate station maximum mass
    # station_max_mass = STATION_VOLUME * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, STATION_VENT_PRESSURE, 0, [1.0]).Output[0] * station_max_fill_fraction

    if final_station_mass < STATION_MAX_MASS:
        print(f"{final_station_mass:.2f} kg < {STATION_MAX_MASS:.2f} kg")
        print("\n3. Offloading with constant pressure at 2.5 atm")
        mass_transferred, mass_vented_station, station_liq_mass, station_gas_mass, trailer_liq_mass = offload_const_pressure(
            final_trailer_mass, final_station_mass, STATION_VENT_PRESSURE, 
            STATION_VOLUME, station_max_fill_fraction, TRAILER_VOLUME
        )
        final_trailer_mass -= mass_transferred
        final_station_mass += mass_transferred
        print(f"After constant pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")
        print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
        print(f"Final station mass: {final_station_mass:.2f} kg")
        print(f"Final trailer pressure: {STATION_VENT_PRESSURE:.2f} Pa")
        print(f"Final station pressure: {STATION_VENT_PRESSURE:.2f} Pa")
    else:
        mass_transferred=0
        mass_vented_station=0
        print("\n3. Skipping constant pressure offload - station is already full")
        print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
        print(f"Final station mass: {final_station_mass:.2f} kg")
        print(f"Final trailer pressure: {final_pressure:.2f} Pa")
        print(f"Final station pressure: {final_pressure:.2f} Pa")
    
    return final_station_mass, final_trailer_mass, mass_vented_station

def main():
    # Initial conditions
    trailer_mass_initial = 1832  # kg
    
    # 1st Offload
    station_mass_1 = 146  # kg
    station_pressure_1 = 202650  # Pa (assuming 2atm absolute)
    final_station_mass_1, trailer_mass_after_1, vented_1 = validate_offload(trailer_mass_initial, station_mass_1, station_pressure_1)
    
    print("1st Offload:")
    print(f"  Station mass increase: {final_station_mass_1 - station_mass_1:.2f} kg (Expected: 617 kg)")
    print(f"  Mass vented: {vented_1:.2f} kg (Expected: 27 kg)")
    
    # 2nd Offload
    station_mass_2 = 38  # kg
    station_pressure_2 = 202650  # Pa (assuming 2atm absolute)
    # final_station_mass_2, trailer_mass_after_2, vented_2 = validate_offload(trailer_mass_after_1, station_mass_2, station_pressure_2)
    
    # print("\n2nd Offload:")
    # print(f"  Station mass increase: {final_station_mass_2 - station_mass_2:.2f} kg (Expected: 714 kg)")
    # print(f"  Mass vented: {vented_2:.2f} kg (Expected: 39 kg)")
    
    # # Trailer venting at plant
    # _, mass_vented_trailer, _, _ = vent_trailer(trailer_mass_after_2, 160000, TRAILER_PRESSURE_FILL)
    # print(f"\nTrailer venting at plant: {mass_vented_trailer:.2f} kg (Expected: 109 kg)")
    
    # # Trailer refill
    # mass_change, _, _ = fill_trailer_const_pressure(trailer_mass_after_2 - mass_vented_trailer, 2014, TRAILER_PRESSURE_FILL, TRAILER_VOLUME)
    # print(f"\nTrailer refill: {mass_change:.2f} kg (Expected: {2014 - (trailer_mass_after_2 - mass_vented_trailer):.2f} kg)")

if __name__ == "__main__":
    main()


    # Make a table showing the results. how much left the trailer and how much recieved at the station and the difference lost mass