import CoolProp.CoolProp as CP

# Constants
TANK_VOLUME = 32.0  # m^3
HEAT_LOAD = 40.7  # W
P_MAX = 1204514.0  # Pa (160 psig, 174.7 psia)

def boil_to_pressure(mass_initial, quality_initial, pressure_initial, pressure_final):
    """
    Function 1: Boiling up to a certain pressure
    
    Args:
    mass_initial (float): Initial mass in kg
    quality_initial (float): Initial quality (mass fraction of gas)
    pressure_initial (float): Initial pressure in Pa
    pressure_final (float): Final pressure in Pa
    
    Returns:
    tuple: (quality_final, time_duration)
    """
    density = mass_initial / TANK_VOLUME
    
    # Calculate final quality
    quality_final = CP.PropsSI('Q', 'D', density, 'P', pressure_final, 'ParaHydrogen')
    
    # Calculate energy change
    u_initial = CP.PropsSI('U', 'D', density, 'P', pressure_initial, 'ParaHydrogen')
    u_final = CP.PropsSI('U', 'D', density, 'P', pressure_final, 'ParaHydrogen')
    du = u_final - u_initial
    
    # Calculate time duration
    time_duration = (du * mass_initial) / HEAT_LOAD
    
    return quality_final, time_duration

def boil_over_time(mass_initial, quality_initial, pressure_initial, time_duration):
    """
    Function 2: Boiling over a specified time duration
    
    Args:
    mass_initial (float): Initial mass in kg
    quality_initial (float): Initial quality (mass fraction of gas)
    pressure_initial (float): Initial pressure in Pa
    time_duration (float): Time duration in seconds
    
    Returns:
    float: Final pressure in Pa
    """
    density = mass_initial / TANK_VOLUME
    
    # Calculate initial internal energy
    u_initial = CP.PropsSI('U', 'D', density, 'P', pressure_initial, 'ParaHydrogen')
    
    # Calculate final internal energy
    u_final = u_initial + (HEAT_LOAD * time_duration) / mass_initial
    
    # Find final pressure (assuming constant density)
    pressure_final = CP.PropsSI('P', 'D', density, 'U', u_final, 'ParaHydrogen')
    
    return pressure_final

def vent_to_pressure(mass_initial, pressure_initial, pressure_final):
    """
    Function 3: Venting to a specified pressure
    
    Args:
    mass_initial (float): Initial mass in kg
    pressure_initial (float): Initial pressure in Pa
    pressure_final (float): Final pressure in Pa
    
    Returns:
    tuple: (mass_final, quality_final)
    """
    density_initial = mass_initial / TANK_VOLUME
    
    # Calculate initial entropy
    s_initial = CP.PropsSI('S', 'D', density_initial, 'P', pressure_initial, 'ParaHydrogen')
    
    # Calculate new density and quality at final pressure with same entropy
    density_final = CP.PropsSI('D', 'P', pressure_final, 'S', s_initial, 'ParaHydrogen')
    quality_final = CP.PropsSI('Q', 'P', pressure_final, 'S', s_initial, 'ParaHydrogen')
    
    # Calculate final mass
    mass_final = density_final * TANK_VOLUME
    
    return mass_final, quality_final

# Example usage
if __name__ == "__main__":
    # Example for boiling up to pressure
    mass_initial = 1680.0  # kg
    quality_initial = 0.5  # Assuming 50% gas initially
    pressure_initial = 202650  # Pa (2 atm absolute)
    pressure_final = 506625  # Pa (5 atm absolute)
    
    quality_final, time_duration = boil_to_pressure(mass_initial, quality_initial, pressure_initial, pressure_final)
    print(f"Boiling to pressure: Final quality = {quality_final:.4f}, Time duration = {time_duration:.2f} seconds")
    
    # Example for boiling over time
    time_duration = 5 * 24 * 3600  # 5 days in seconds
    final_pressure = boil_over_time(mass_initial, quality_initial, pressure_initial, time_duration)
    print(f"Boiling over time: Final pressure = {final_pressure:.2f} Pa")
    
    # Example for venting
    mass_final, quality_final = vent_to_pressure(mass_initial, pressure_final, pressure_initial)
    print(f"Venting: Final mass = {mass_final:.2f} kg, Final quality = {quality_final:.4f}")