#onefullcycle.py
import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from AllFunctions import (boil_to_pressure, offload_with_raising_pressure, 
                          offload_const_pressure, boil_over_time, vent_trailer, 
                          fill_trailer_const_pressure)

# Initialize REFPROP
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum

# Constants and initial conditions
trailer_volume = 32.0  # m^3
TRAILER_HEAT_LOAD = 40.7  # W
trailer_pressure_max = 1204514.0  # Pa (160 psig, 174.7 psia)
station_pressure_max = 550000  # Pa 4.5bar
trailer_pressure_fill = 131000  # Pa 4psi gauge
station_pressure_initial = 202650  # Pa (2 atm absolute)
station_volume = 13.33  # m^3
station_max_fill_fraction = 0.95
time_transportation = 1 * 24 * 3600  # 1 day in seconds
offload_pressure = 353312  # Pa (2.5 atm gauge)
trailer_mass_max = 2100 # kg
station_mass_initial = 150  # kg (assuming some residual H2 in the trailer)
trailer_mass_initial = 2100 #kg
trailer_pressure_initial = 160000 # 

print("Starting H2 Trailer Cycle Simulation")

# Step 1: Heat up to station pressure
print("\n1. Heating trailer to station pressure")
target_pressure = station_pressure_initial
final_enthalpy, time_duration = boil_to_pressure(trailer_mass_initial, trailer_pressure_initial, target_pressure)
print(f"Heated to: Pressure = {target_pressure:.2f} Pa, Time taken = {time_duration:.2f} seconds")
print(f"Final trailer mass: {trailer_mass_initial:.2f} kg")
print(f"Final station mass: {station_mass_initial:.2f} kg")
print(f"Final trailer pressure: {target_pressure:.2f} Pa")
print(f"Final station pressure: {station_pressure_initial:.2f} Pa")

# Step 2: Offload with rising pressure up to 2.5 atm
print("\n2. Offloading with rising pressure up to 2.5 atm")
final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
    target_pressure, station_pressure_initial, trailer_mass_initial, station_mass_initial, station_volume, station_max_fill_fraction
)
print(f"After rising pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")
print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {final_pressure:.2f} Pa")
print(f"Final station pressure: {final_pressure:.2f} Pa")

# Calculate station maximum mass
station_max_mass = station_volume * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, offload_pressure, 0, [1.0]).Output[0] * station_max_fill_fraction

# Step 3: Offload with constant pressure at 2.5 atm (if station is not full)
if final_station_mass < station_max_mass:
    print("\n3. Offloading with constant pressure at 2.5 atm")
    mass_transfer, energy_added = offload_const_pressure(
        final_trailer_mass, final_station_mass, offload_pressure, station_volume, station_max_fill_fraction
    )
    final_trailer_mass -= mass_transfer
    final_station_mass += mass_transfer
    print(f"After constant pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")
    print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
    print(f"Final station mass: {final_station_mass:.2f} kg")
    print(f"Final trailer pressure: {offload_pressure:.2f} Pa")
    print(f"Final station pressure: {offload_pressure:.2f} Pa")
else:
    print("\n3. Skipping constant pressure offload - station is already full")
    print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
    print(f"Final station mass: {final_station_mass:.2f} kg")
    print(f"Final trailer pressure: {final_pressure:.2f} Pa")
    print(f"Final station pressure: {final_pressure:.2f} Pa")

# Step 4: Delay boil over 1 day transportation
print("\n4. Boiling over 1 day transportation")
pressure_after_transport, quality_final = boil_over_time(final_trailer_mass, final_pressure, time_transportation)
print(f"After transport: Pressure = {pressure_after_transport:.2f} Pa, Quality = {quality_final:.2f}")
print(f"Final trailer mass: {final_trailer_mass:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {pressure_after_transport:.2f} Pa")
print(f"Final station pressure: {final_pressure:.2f} Pa")

# Step 5: Venting before filling the trailer
print("\n5. Venting trailer before filling")
mass_after_vent, mass_vented, _, _ = vent_trailer(final_trailer_mass, pressure_after_transport, trailer_pressure_fill)  
print(f"After venting: Mass vented = {mass_vented:.2f} kg, Pressure = {trailer_pressure_fill:.2f} Pa")
print(f"Final trailer mass: {mass_after_vent:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {trailer_pressure_fill:.2f} Pa")
print(f"Final station pressure: {final_pressure:.2f} Pa")

# Step 6: Fill the trailer
print("\n6. Filling the trailer")
mass_change, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_after_vent, trailer_mass_max, trailer_pressure_fill, trailer_volume)
mass_after_fill = mass_after_vent + mass_change
print(f"After filling: Mass = {mass_after_fill:.2f} kg, Pressure = {trailer_pressure_fill:.2f} Pa")
print(f"Final trailer mass: {mass_after_fill:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {trailer_pressure_fill:.2f} Pa")
print(f"Final station pressure: {final_pressure:.2f} Pa")

print("\nH2 Trailer Cycle Simulation Complete")
print(f"Mass received at station: {final_station_mass - station_mass_initial:.2f} kg")
print(f"Mass lost (venting): {mass_vented:.2f} kg")
print(f"Final trailer mass: {mass_after_fill:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {trailer_pressure_fill:.2f} Pa")
print(f"Final station pressure: {final_pressure:.2f} Pa")