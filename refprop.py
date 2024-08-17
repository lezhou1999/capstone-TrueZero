import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

# Initialize REFPROP
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum

# Constants
TANK_VOLUME = 32.0  # m^3
TRAILER_HEAT_LOAD = 40.7  # W
TRAILER_P_MAX = 1204514.0  # Pa (160 psig, 174.7 psia)

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
    mass_liquid_available = mass_trailer_initial - mass_gas_trailer_empty

    Q = 0
    r_liq = RP.REFPROPdll("PARAHYD", "QP", "D", MASS_BASE_SI, 0, 0, Q, pressure, [1.0])
    density_liq = r_liq.Output[0]
    mass_station_max = station_volume * density_liq * max_station_fill_fraction
    mass_transfer_needed = mass_station_max - mass_station_initial
    
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

# Example usage
if __name__ == "__main__":
    # Example parameters
    mass_initial = 1680.0  # kg
    pressure_initial = 202650  # Pa (2 atm absolute)
    pressure_final = 506625  # Pa (5 atm absolute)
    
    # Test boil_to_pressure
    final_enthalpy, time_duration = boil_to_pressure(mass_initial, pressure_initial, pressure_final)
    print(f"Boil to pressure: Final enthalpy = {final_enthalpy:.2f} J/kg, Time duration = {time_duration:.2f} seconds")
    
    # Test boil_over_time
    time_duration = 5 * 24 * 3600  # 5 days in seconds
    final_pressure = boil_over_time(mass_initial, pressure_initial, time_duration)
    print(f"Boil over time: Final pressure = {final_pressure:.2f} Pa")
    
    # Test vent_trailer
    mass_final, mass_vented, mass_liq_final, mass_gas_final = vent_trailer(mass_initial, pressure_final, pressure_initial)
    print(f"Vent trailer: Final mass = {mass_final:.2f} kg, Vented mass = {mass_vented:.2f} kg, mass_liq_final = {mass_liq_final:.2f} kg, mass_gas_final = {mass_gas_final:.2f} kg")
    
    # Test offload_varying_pressure
    P_initial_trailer = 31.7 * 6894.76 + 101325  # 31.7 psig converted to Pa absolute
    P_initial_station = 101325  # 1 atm
    m_initial_trailer = 1680  #  kg
    m_initial_station = 80  # kg
    V_station = 12  # cubic meters, example value

    final_pressure, final_station_mass, final_trailer_mass = offload_parahydrogen(
        P_initial_trailer, P_initial_station, m_initial_trailer, m_initial_station, V_station
    )

    print(f"\nFinal Results:")
    print(f"Final station pressure: {final_pressure:.1f} Pa")
    print(f"Final station mass: {final_station_mass:.2f} kg")
    print(f"Final trailer mass: {final_trailer_mass:.2f} kg")

    # Test offload_const_pressure
    # Assumptions:
    mass_station_initial = 80.0  # kg
    station_volume = 15.0  # m^3
    max_station_fill_fraction = 0.95
    offload_pressure = 253312  # Pa (2.5 atm absolute)
    
    mass_transfer, energy_added, u_trailer_final, u_station_final = offload_const_pressure(
        mass_initial, mass_station_initial, offload_pressure, station_volume, max_station_fill_fraction
    )
    print(f"Offload const pressure: Mass transferred = {mass_transfer:.2f} kg")
    print(f"Energy added to trailer = {energy_added:.2f} J")
    print(f"Final trailer enthalpy = {u_trailer_final:.2f} J/kg")
    print(f"Final station enthalpy = {u_station_final:.2f} J/kg")
        
    # Test fill_trailer_const_pressure
    mass_offload_final = 1680  # kg
    mass_offload_initial = 80
    change_mass, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_offload_initial, mass_offload_final, pressure_final)
    print(f"Fill trailer const pressure: Change in mass = {change_mass:.2f} kg")
    print(f"Mass of liquid added = {mass_liq_added:.2f} kg, Mass of gas added = {mass_gas_added:.2f} kg")