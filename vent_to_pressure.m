function [mass_final, quality_final] = vent_to_pressure(mass_initial, pressure_initial, pressure_final)
    % Function 3: Venting to a specified pressure
    %
    % Args:
    % mass_initial (float): Initial mass in kg
    % pressure_initial (float): Initial pressure in Pa
    % pressure_final (float): Final pressure in Pa
    %
    % Returns:
    % tuple: (mass_final, quality_final)
    

    
    density_initial = mass_initial / TANK_VOLUME;
    
    % Calculate initial entropy
    s_initial = CoolProp.PropsSI('S', 'D', density_initial, 'P', pressure_initial, 'ParaHydrogen');
    
    % Calculate new density and quality at final pressure with same entropy
    density_final = CoolProp.PropsSI('D', 'P', pressure_final, 'S', s_initial, 'ParaHydrogen');
    quality_final = CoolProp.PropsSI('Q', 'P', pressure_final, 'S', s_initial, 'ParaHydrogen');
    
    % Calculate final mass
    mass_final = density_final * TANK_VOLUME;
end
