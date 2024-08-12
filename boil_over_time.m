function pressure_final = boil_over_time(mass_initial, quality_initial, pressure_initial, time_duration)
    % Function 2: Boiling over a specified time duration
    %
    % Args:
    % mass_initial (float): Initial mass in kg
    % quality_initial (float): Initial quality (mass fraction of gas)
    % pressure_initial (float): Initial pressure in Pa
    % time_duration (float): Time duration in seconds
    %
    % Returns:
    % float: Final pressure in Pa
    


    
    density = mass_initial / TANK_VOLUME;
    
    % Calculate initial internal energy
    u_initial = CoolProp.PropsSI('U', 'D', density, 'P', pressure_initial, 'ParaHydrogen');
    
    % Calculate final internal energy
    u_final = u_initial + (HEAT_LOAD * time_duration) / mass_initial;
    
    % Find final pressure (assuming constant density)
    pressure_final = CoolProp.PropsSI('P', 'D', density, 'U', u_final, 'ParaHydrogen');
end
