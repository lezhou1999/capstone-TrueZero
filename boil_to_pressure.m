function [quality_final, time_duration] = boil_to_pressure(mass_initial, quality_initial, pressure_initial, pressure_final)
    % Function 1: Boiling up to a certain pressure
    %
    % Args:
    % mass_initial (float): Initial mass in kg
    % quality_initial (float): Initial quality (mass fraction of gas)
    % pressure_initial (float): Initial pressure in Pa
    % pressure_final (float): Final pressure in Pa
    %
    % Returns:
    % tuple: (quality_final, time_duration)

    % Constants
    TANK_VOLUME = 32.0;  % m^3
    HEAT_LOAD = 40.7;  %
    P_MAX = 1204514.0;  % Pa (160 psig, 174.7 psia)
    
    
    density = mass_initial / TANK_VOLUME;
    
    % Calculate final quality
    quality_final = CoolProp.PropsSI('Q', 'D', density, 'P', pressure_final, 'ParaHydrogen');
    
    % Calculate energy change
    u_initial = CoolProp.PropsSI('U', 'D', density, 'P', pressure_initial, 'ParaHydrogen');
    u_final = CoolProp.PropsSI('U', 'D', density, 'P', pressure_final, 'ParaHydrogen');
    du = u_final - u_initial;
    
    % Calculate time duration
    time_duration = (du * mass_initial) / HEAT_LOAD;
end
