import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

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
m_station_max = 870.0 * station_max_fill_fraction  # 95% of full mass


def boil_to_pressure(mass_initial, pressure_initial, pressure_final):
    density = mass_initial / trailer_volume
    
    # Calculate initial and final states
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "H;E", MASS_BASE_SI, 0, 0, pressure_initial, density, [1.0])
    h_initial, e_initial = r_initial.Output[0], r_initial.Output[1]
    
    r_final = RP.REFPROPdll("PARAHYD", "PD", "H;E", MASS_BASE_SI, 0, 0, pressure_final, density, [1.0])
    h_final, e_final = r_final.Output[0], r_final.Output[1]
    
    # Calculate energy change and time duration
    de = e_final - e_initial
    dt = de * mass_initial / TRAILER_HEAT_LOAD
    
    return h_final, dt

def boil_over_time(mass_initial, pressure_initial, time_duration):
    density = mass_initial / trailer_volume
    
    # Calculate initial state
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure_initial, density, [1.0])
    e_initial = r_initial.Output[0]
    
    # Calculate final internal energy
    e_final = e_initial + (TRAILER_HEAT_LOAD * time_duration) / mass_initial
    
    # Find final pressure 
    r_final = RP.REFPROPdll("PARAHYD", "DE", "P;QMASS", MASS_BASE_SI, 0, 0, density, e_final, [1.0])
    pressure_final, quality_final= r_final.Output[0], r_final.Output[1]
    
    return pressure_final, quality_final

def vent_trailer(mass_initial, pressure_initial, pressure_final):
    # print(pressure_final)
    density_initial = mass_initial / trailer_volume
    
    # Calculate initial entropy
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "S", MASS_BASE_SI, 0, 0, pressure_initial, density_initial, [1.0])
    s_initial = r_initial.Output[0]
    
    # Calculate new density at final pressure, with same entropy
    r_final = RP.REFPROPdll("PARAHYD", "PS", "D;QMASS", MASS_BASE_SI, 0, 0, pressure_final, s_initial, [1.0])
    density_final, x_final = r_final.Output[0], r_final.Output[1]

    # print(x_final, density_initial, density_final)
    if x_final < 0 or x_final > 1:
        x_final = 1
        print("Caution Quality is constrained!")
    else:
        x_final = x_final
    
    # Calculate liquid final values
    mass_final = trailer_volume*density_final
    mass_liq_final = (1 - x_final) * mass_final #why are we using the initial mass here?
    r1 = RP.REFPROPdll("PARAHYD", "P;QMASS", "D", MASS_BASE_SI, 0, 0, pressure_final, 0, [1.0])
    vol_liq = mass_liq_final/r1.Output[0]
    
    # Calculate gas final values
    vol_gas = trailer_volume - vol_liq
    r2 = RP.REFPROPdll("PARAHYD", "P;QMASS", "D", MASS_BASE_SI, 0, 0, pressure_final, 1, [1.0])
    mass_gas_final = vol_gas*r2.Output[0]
    
    # Calculate mass vented
    #mass_trailer_final = mass_gas_final + mass_liq_final
    mass_vented = mass_initial - mass_final
    
    return mass_final, mass_vented, mass_liq_final, mass_gas_final

def offload_with_raising_pressure(P_initial_trailer, P_initial_station, m_initial_trailer, m_initial_station, V_station, m_station_max, P_station_max, P_trailer_max, V_trailer):
    # Constants
    # V_trailer = 32  # m^3
    # P_trailer_max = 1204514.0  # Pa (160 psig, 174.7 psia)
    # P_station_max = 351325  # Pa (2.5 barg, converted to Pa abs)
    # m_station_max = 870.0 * station_max_fill_fraction  # 95% of full mass
    # m_station_max = 800
    # P_station_max = 400000

    dP = 1000  # Pa
    max_steps = 1000
    
    P_max = min(P_station_max, P_trailer_max)
    P = P_initial_trailer
    
    # print(f"Initial conditions:")
    # print(f"  Trailer pressure: {P_initial_trailer:.2f} Pa")
    # print(f"  Station pressure: {P_initial_station:.2f} Pa")
    # print(f"  Trailer mass: {m_initial_trailer:.2f} kg")
    # print(f"  Station mass: {m_initial_station:.2f} kg")
    # print(f"  Station volume: {V_station:.2f} m³")
    # print(f"  Station max fill fraction: {station_max_fill_fraction:.2f}")
    
    # Calculate full and empty masses
    m_trailer_empty = V_trailer * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P, 1, [1.0]).Output[0]
    m_trailer_full = V_trailer * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P, 0, [1.0]).Output[0]
    m_station_empty = V_station * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P, 1, [1.0]).Output[0]
    m_station_full = V_station * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P, 0, [1.0]).Output[0]
    
    # print(f"Calculated masses:")
    # print(f"  Trailer empty mass: {m_trailer_empty:.2f} kg")
    # print(f"  Trailer full mass: {m_trailer_full:.2f} kg")
    # print(f"  Station empty mass: {m_station_empty:.2f} kg")
    # print(f"  Station full mass: {m_station_full:.2f} kg")
    
    # Check input validity
    if m_initial_trailer <= m_trailer_empty:
        print(f"Trailer is empty! Initial mass ({m_initial_trailer:.2f} kg) <= Empty mass ({m_trailer_empty:.2f} kg)")
        return P, m_initial_station, m_initial_trailer
    elif m_initial_trailer > m_trailer_full:
        print(f"Trailer mass ({m_initial_trailer:.2f} kg) exceeds calculated full mass ({m_trailer_full:.2f} kg) at new pressure. Proceeding with transfer.")
    elif m_initial_station < m_station_empty:
        print(f"Station is less than empty! Initial mass ({m_initial_station:.2f} kg) < Empty mass ({m_station_empty:.2f} kg)")
        return P, m_initial_station, m_initial_trailer
    elif m_initial_station > m_station_full:
        print(f"Station is overfull! Initial mass ({m_initial_station:.2f} kg) > Full mass ({m_station_full:.2f} kg)")
        return P, m_initial_station, m_initial_trailer
    
    # Initialize
    m_trailer = m_initial_trailer
    m_station = m_initial_station
    m_combined = m_station + m_trailer
    V_combined = V_station + V_trailer
    rho_combined = m_combined / V_combined
    
    # Calculate initial energies and entropies
    u_combined = RP.REFPROPdll("PARAHYD", "PD", "U", MASS_BASE_SI, 0, 0, P, rho_combined, [1.0]).Output[0]
    s_station = RP.REFPROPdll("PARAHYD", "PD", "S", MASS_BASE_SI, 0, 0, P, m_station / V_station, [1.0]).Output[0]
    
    Q_total = 0
    m_transferred = 0
    
    # Stepwise pressure increase
    for step in range(max_steps):
        P2 = P + dP
        print(f"\nStep {step}")
        print(f"Pressure: {P:.1f} Pa")
        
        # Calculate new energies
        u2_combined = RP.REFPROPdll("PARAHYD", "PD", "U", MASS_BASE_SI, 0, 0, P2, rho_combined, [1.0]).Output[0]
        Q_step = (u2_combined - u_combined) * m_combined
        
        # Calculate new station properties
        rho_shrunk_station = RP.REFPROPdll("PARAHYD", "PS", "D", MASS_BASE_SI, 0, 0, P2, s_station, [1.0]).Output[0]
        V_shrunk_station = m_station / rho_shrunk_station
        
        # Calculate mass transfer
        rho2_L = RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P2, 0, [1.0]).Output[0]
        m_transfer = (V_station - V_shrunk_station) * rho2_L
        
        print(f"Mass Transferring: {m_transfer:.2f} kg")
        m2_trailer = m_trailer - m_transfer
        m2_station = m_station + m_transfer
        
        m2_trailer_min = V_trailer * RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, P2, 1, [1.0]).Output[0]
        
        # print(f"Updated masses:")
        # print(f"  Trailer: {m2_trailer:.2f} kg")
        # print(f"  Station: {m2_station:.2f} kg")
        # print(f"  Minimum trailer mass: {m2_trailer_min:.2f} kg")
        # print(f"  Maximum station mass: {m_station_max:.2f} kg")
        
        # Check stop conditions
        if P2 >= P_max:
            print("Pressure Halt")
            break
        elif m2_station >= m_station_max:
            print(f"Station Full with {m2_station:.2f} kg")
            break
        elif m2_trailer < m2_trailer_min:
            print(f"Trailer Empty with {m2_trailer:.2f} kg")
            break
        
        # Update values for next step
        P = P2
        u_combined = u2_combined
        Q_total += Q_step
        m_station = m2_station
        m_trailer = m2_trailer
        s_station = RP.REFPROPdll("PARAHYD", "PD", "S", MASS_BASE_SI, 0, 0, P, m_station / V_station, [1.0]).Output[0]
        m_transferred += m_transfer
        
        if step + 1 >= max_steps:
            print("Step Limit Reached")
    
    # print(f"\nFinal results:")
    # print(f"Station mass: {m_station:.12f} kg")
    # print(f"Transferred mass: {m_transferred:.2f} kg")
    # print(f"Station pressure: {P:.1f} Pa")
    # print(f"Max pressure: {P_max:.1f} Pa")
    # print(f"Max station mass: {m_station_max:.2f} kg")
    # print(f"Min trailer mass: {m2_trailer_min:.2f} kg")
    
    return P, m_station, m_trailer

def offload_const_pressure(trailer_mass_initial, station_mass_initial, pressure, station_volume, station_max_fill_fraction):
    # Calculate initial trailer state
    density_trailer_initial = trailer_mass_initial / trailer_volume
    e_trailer_initial = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, density_trailer_initial, [1.0]).Output[0]
    
    # Calculate initial station state
    density_station_initial = station_mass_initial / station_volume
    e_station_initial = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, density_station_initial, [1.0]).Output[0]
    
    # Calculate gas and liquid densities
    density_gas = RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, pressure, 1, [1.0]).Output[0]
    density_liq = RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, pressure, 0, [1.0]).Output[0]
    
    # Calculate mass of gas when trailer is empty and liquid available
    mass_gas_trailer_empty = trailer_volume * density_gas
    mass_liquid_available = trailer_mass_initial - mass_gas_trailer_empty
    
    # Calculate station max mass and mass transfer needed
    station_mass_max = station_volume * density_liq * station_max_fill_fraction
    mass_transfer_needed = min(station_mass_max - station_mass_initial, mass_liquid_available)
    
    # Calculate volume transferred and gas vented
    vol_transferred = mass_transfer_needed / density_liq
    gas_vented = vol_transferred * density_gas
    
    # Calculate final states
    trailer_mass_final = trailer_mass_initial - mass_transfer_needed
    station_mass_final = station_mass_initial + mass_transfer_needed - gas_vented
    
    # Calculate energy transferred
    e_trailer_final = RP.REFPROPdll("PARAHYD", "PD", "E", MASS_BASE_SI, 0, 0, pressure, trailer_mass_final / trailer_volume, [1.0]).Output[0]
    energy_transferred = (e_trailer_final - e_trailer_initial) * trailer_mass_final
    
    return mass_transfer_needed, gas_vented, trailer_mass_final, station_mass_final, energy_transferred

def fill_trailer_const_pressure(mass_initial, mass_final, pressure, trailer_volume):
    density_initial = mass_initial / trailer_volume
    density_final = mass_final / trailer_volume
    
    # Initial state
    r_initial = RP.REFPROPdll("PARAHYD", "PD", "E;QMOLE", MASS_BASE_SI, 0, 0, pressure, density_initial, [1.0])
    e_initial, x_initial = r_initial.Output[0], r_initial.Output[1]
    
    # print(x_initial, density_initial, density_final)
    if x_initial < 0 or x_initial > 1:
        x_initial = 1
        print("Caution Quality is constrained!")
    else:
        x_initial = x_initial

    # Final state
    r_final = RP.REFPROPdll("PARAHYD", "PD", "E;QMOLE", MASS_BASE_SI, 0, 0, pressure, density_final, [1.0])
    e_final, x_final = r_final.Output[0], r_final.Output[1]
    
    # print(x_final)
    if x_final < 0 or x_final > 1:
        x_final = 1
        
        print("Caution Quality is constrained!")
    else:
        x_final = x_final
        
    change_mass = mass_final - mass_initial
    mass_liq_added = mass_final*(1-x_final) - mass_initial*(1-x_initial)
    mass_gas_added = mass_initial*(x_initial) - mass_final*(x_final)

    return change_mass, mass_liq_added, mass_gas_added
