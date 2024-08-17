import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import math

# Initialize REFPROP
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum

def boil_to_pressure(mass_initial, pressure_initial, pressure_final):
    density = mass_initial / TANK_VOLUME
    
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "H;E", MASS_BASE_SI, 0, 0, pressure_initial, density, [1.0])
    h_initial, e_initial = r_initial.Output[0], r_initial.Output[1]
    
    r_final = RP.REFPROPdll("PARAHYD", "PD", "H;E", MASS_BASE_SI, 0, 0, pressure_final, density, [1.0])
    h_final, e_final = r_final.Output[0], r_final.Output[1]
    
    de = e_final - e_initial
    dt = de * mass_initial / TRAILER_HEAT_LOAD
    
    return h_final, dt

def boil_over_time(mass_initial, pressure_initial, time_duration):
    density = mass_initial / TANK_VOLUME
    
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure_initial, density, [1.0])
    e_initial = r_initial.Output[0]
    
    e_final = e_initial + (TRAILER_HEAT_LOAD * time_duration) / mass_initial
    
    r_final = RP.REFPROPdll("PARAHYD", "DE", "P", MASS_BASE_SI, 0, 0, density, e_final, [1.0])
    pressure_final = r_final.Output[0]
    
    return pressure_final

def vent_trailer(mass_initial, pressure_initial, pressure_final):
    density_initial = mass_initial / TANK_VOLUME
    
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "S", MASS_BASE_SI, 0, 0, pressure_initial, density_initial, [1.0])
    s_initial = r_initial.Output[0]
    
    r_final = RP.REFPROPdll("PARAHYD", "PS", "D;QMASS", MASS_BASE_SI, 0, 0, pressure_final, s_initial, [1.0])
    density_final, x_final = r_final.Output[0], r_final.Output[1]

    if x_final < 0 or x_final > 1:
        x_final = 1
    else:
        x_final = x_final

    total_mass_final = density_final * TANK_VOLUME
    mass_liq_final = (1 - x_final) * total_mass_final
    mass_gas_final = x_final * total_mass_final
    mass_vented = mass_initial - total_mass_final
    
    return total_mass_final, mass_vented, mass_liq_final, mass_gas_final

def offload_parahydrogen(P_initial_trailer, P_initial_station, m_initial_trailer, m_initial_station, V_station):
    P_gauge_limit = 253312  # 2.5 bar gauge converted to Pa absolute
    P_diff = 0.4 * 100000  # 0.4 bar gauge converted to Pa
    max_iterations = 1000
    
    P_trailer = P_initial_trailer
    P_station = P_initial_station
    m_trailer = m_initial_trailer
    m_station = m_initial_station
    
    for step in range(max_iterations):
        # Calculate densities
        Q = 0
        rho_trailer = RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, P_trailer, [1.0]).Output[0]
        rho_station = m_station / V_station
        
        # Calculate new pressure in station
        P_new_station = P_station + 1000  # Increase by 1 kPa each step
        
        # Calculate mass transfer
        Q = 0
        rho_new_station = RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, P_new_station, [1.0]).Output[0]
        m_transferred = V_station * (rho_new_station - rho_station)
        
        # Check stop conditions
        if m_transferred > m_trailer:
            print(f"Stop: Trailer empty at step {step}")
            break
        if P_new_station > P_gauge_limit:
            print(f"Stop: Station pressure limit reached at step {step}")
            break
        if m_station + m_transferred > RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, P_gauge_limit, [1.0]).Output[0] * TANK_VOLUME:
            print(f"Stop: Station mass limit reached at step {step}")
            break
        
        # Update values
        m_trailer -= m_transferred
        m_station += m_transferred
        P_station = P_new_station
        P_trailer = P_station + P_diff
        
        print(f"Step {step}")
        print(f"Pressure: {P_station:.1f}")
    
    print("Pressure Halt")
    print(f"station mass: {m_station:.12f}")
    print(f"station pressure: {P_station:.1f}")
    
    return P_station, m_station, m_trailer

def offload_const_pressure(mass_trailer_initial, mass_station_initial, pressure, station_volume, max_station_fill_fraction):
    density_trailer_initial = mass_trailer_initial / TANK_VOLUME
    
    r_trailer_initial = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, density_trailer_initial, [1.0])
    e_trailer_initial = r_trailer_initial.Output[0]
    
    density_station_initial = mass_station_initial / station_volume
    r_station_initial = RP.REFPROPdll("PARAHYD", "DP", "E", MASS_BASE_SI, 0, 0, density_station_initial, pressure, [1.0])
    e_station_initial = r_station_initial.Output[0]
    
    Q = 1
    r_gas = RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, pressure, [1.0])
    density_gas = r_gas.Output[0]
    mass_gas_trailer_empty = TANK_VOLUME * density_gas
    mass_liquid_available = abs(mass_trailer_initial - mass_gas_trailer_empty)

    Q = 0
    r_liq = RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, pressure, [1.0])
    density_liq = r_liq.Output[0]
    mass_station_max = station_volume * density_liq * max_station_fill_fraction
    mass_transfer_needed = abs(mass_station_max - mass_station_initial)
    
    mass_transfer = min(mass_transfer_needed, mass_liquid_available)
    
    mass_trailer_final = mass_trailer_initial - mass_transfer
    mass_station_final = mass_station_initial + mass_transfer
    
    r_trailer_final = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, mass_trailer_final / TANK_VOLUME, [1.0])
    e_trailer_final = r_trailer_final.Output[0]
    
    r_station_final = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, mass_station_final / station_volume, [1.0])
    e_station_final = r_station_final.Output[0]
   
    energy_added = (e_trailer_final - e_trailer_initial) * mass_trailer_final
    
    return mass_transfer, energy_added, e_trailer_final, e_station_final

def fill_trailer_const_pressure(mass_initial, mass_final, pressure):
    density_initial = mass_initial / TANK_VOLUME
    density_final = mass_final / TANK_VOLUME
    
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "E;QMOLE", MASS_BASE_SI, 0, 0, pressure, density_initial, [1.0])
    e_initial, x_initial = r_initial.Output[0], r_initial.Output[1]

    if x_initial < 0 or x_initial > 1:
        x_initial = 1
    else:
        x_initial = x_initial

    r_final = RP.REFPROPdll("PARAHYD", "PD", "E;QMOLE", MASS_BASE_SI, 0, 0, pressure, density_final, [1.0])
    e_final, x_final = r_final.Output[0], r_final.Output[1]

    if x_final < 0 or x_final > 1:
        x_final = 1
    else:
        x_final = x_final
        
    change_mass = mass_final - mass_initial
    mass_liq_added = mass_final*(1-x_final) - mass_initial*(1-x_initial)
    mass_gas_added = mass_final*(x_final) - mass_initial*(x_initial)

    return change_mass, mass_liq_added, mass_gas_added

# Constants and initial conditions
TANK_VOLUME = 32.0  # m^3
TRAILER_HEAT_LOAD = 40.7  # W
TRAILER_P_MAX = 1204514.0  # Pa (160 psig, 174.7 psia)
STATION_P_MAX = TRAILER_P_MAX / 3  # Pa (1/2.5 of trailer max pressure)
PLANT_FILL_PRESSURE = 196570.5  # Pa (1.94 atm absolute)
STATION_INITIAL_PRESSURE = 202650  # Pa (2 atm absolute)
STATION_VOLUME = 12  # m^3
MAX_STATION_FILL_FRACTION = 0.95
TRANSPORT_TIME = 5 * 24 * 3600  # 5 days in seconds
OFFLOAD_PRESSURE = 253312  # Pa (2.5 atm absolute)
PRESSURE_DIFFERENCE = 40000  # Pa (0.4 bar)
MAX_MASS_TRAILER = 1680.0 # kg
mass_station_initial = 80.0  # kg (assuming some residual H2 in the trailer)
mass_trailer_initial = 50 #kg
pressure_trailer_initial = 354638 # for venting 3.5 atm

def check_and_vent(mass, pressure, max_pressure, volume, is_trailer=True):
    if pressure > max_pressure*0.95:
        target_pressure = max_pressure*0.9
        print(f"{'Trailer' if is_trailer else 'Station'} pressure exceeded. Venting to {target_pressure:.2f} Pa")
        mass_after_vent, mass_vented, _, _ = vent_trailer(mass, pressure, target_pressure)
        return mass_after_vent, target_pressure
    return mass, pressure

print("Starting H2 Trailer Cycle Simulation")

# Step 1: Vent trailer at the plant
print("\n1. Venting trailer at the plant")
mass_after_vent, mass_vented, mass_liq_after_vent, mass_gas_after_vent = vent_trailer(mass_trailer_initial, pressure_trailer_initial, 101325)  
print(f"After venting: Mass = {mass_after_vent:.2f} kg, Pressure = 101325 Pa")

# Step 2: Fill trailer at the plant
print("\n2. Filling trailer at the plant")
mass_change, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_after_vent, MAX_MASS_TRAILER, PLANT_FILL_PRESSURE)
mass_after_fill = mass_after_vent + mass_change
print(f"After filling: Mass = {mass_after_fill:.2f} kg, Pressure = {PLANT_FILL_PRESSURE} Pa")

# Check and vent if necessary after filling
mass_after_fill, pressure_after_fill = check_and_vent(mass_after_fill, PLANT_FILL_PRESSURE, TRAILER_P_MAX, TANK_VOLUME)

# Step 3: Transport (boil over time)
print("\n3. Transporting trailer (boil over time)")
pressure_after_transport = boil_over_time(mass_after_fill, pressure_after_fill, TRANSPORT_TIME)
print(f"After transport: Pressure = {pressure_after_transport:.2f} Pa")

# Check and vent if necessary after transport
mass_after_transport, pressure_after_transport = check_and_vent(mass_after_fill, pressure_after_transport, TRAILER_P_MAX, TANK_VOLUME)

# Step 4: Boil to pressure before offloading
print("\n4. Boiling to pressure before offloading")
target_pressure = min(STATION_INITIAL_PRESSURE + PRESSURE_DIFFERENCE, TRAILER_P_MAX)
if pressure_after_transport < target_pressure:
    final_enthalpy, time_duration = boil_to_pressure(mass_after_transport, pressure_after_transport, target_pressure)
    print(f"Boiled to: Pressure = {target_pressure} Pa, Time taken = {time_duration:.2f} seconds")
    pressure_before_offload = target_pressure
else:
    print("No boiling necessary, pressure already above target pressure")
    pressure_before_offload = pressure_after_transport

# Step 5: Offload at station
print("\n5. Offloading at station")
# First, offload with rising pressure up to 2.5 atm
final_pressure, final_station_mass, final_trailer_mass = offload_parahydrogen(
    pressure_before_offload, STATION_INITIAL_PRESSURE, mass_after_transport, mass_station_initial, STATION_VOLUME
)
print(f"After rising pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")

# Check and vent station if necessary
final_station_mass, station_pressure = check_and_vent(final_station_mass, final_pressure, STATION_P_MAX, STATION_VOLUME, is_trailer=False)

# Then, offload with constant pressure at 2.5 atm
mass_transfer, energy_added, u_trailer_final, u_station_final = offload_const_pressure(
    final_trailer_mass, final_station_mass, OFFLOAD_PRESSURE, STATION_VOLUME, MAX_STATION_FILL_FRACTION
)
final_trailer_mass -= mass_transfer
final_station_mass += mass_transfer
print(f"After constant pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg")

# Final check and vent for both trailer and station
final_trailer_mass, trailer_final_pressure = check_and_vent(final_trailer_mass, OFFLOAD_PRESSURE, TRAILER_P_MAX, TANK_VOLUME)
final_station_mass, station_final_pressure = check_and_vent(final_station_mass, OFFLOAD_PRESSURE, STATION_P_MAX, STATION_VOLUME, is_trailer=False)

# Step 6: Final venting of trailer (if necessary)
if trailer_final_pressure > 101325:
    print("\n6. Final venting of trailer")
    mass_after_final_vent, mass_final_vented, _, _ = vent_trailer(final_trailer_mass, trailer_final_pressure, 101325)
    print(f"After final venting: Trailer mass = {mass_after_final_vent:.2f} kg, Pressure = 101325 Pa")
else:
    print("\n6. No final venting needed")
    mass_after_final_vent = final_trailer_mass

print("\nH2 Trailer Cycle Simulation Complete")
print(f"Final trailer mass: {mass_after_final_vent:.2f} kg")
print(f"Final station mass: {final_station_mass:.2f} kg")
print(f"Final trailer pressure: {trailer_final_pressure:.2f} Pa")
print(f"Final station pressure: {station_final_pressure:.2f} Pa")