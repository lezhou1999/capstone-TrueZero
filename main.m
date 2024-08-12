while true
    % Display menu
    fprintf('Select an operation:\n');
    fprintf('1. Boil to a specified pressure\n');
    fprintf('2. Boil over a specified time duration\n');
    fprintf('3. Vent to a specified pressure\n');
    fprintf('4. Exit\n');
    
    choice = input('Enter your choice (1-4): ');
    
    switch choice
        case 1
            % Boil to a specified pressure
            mass_initial = input('Enter initial mass (kg): ');
            quality_initial = input('Enter initial quality (fraction): ');
            pressure_initial = input('Enter initial pressure (Pa): ');
            pressure_final = input('Enter final pressure (Pa): ');
            
            [quality_final, time_duration] = boil_to_pressure(mass_initial, quality_initial, pressure_initial, pressure_final, TANK_VOLUME, HEAT_LOAD);
            fprintf('Boiling to pressure: Final quality = %.4f, Time duration = %.2f seconds\n', quality_final, time_duration);
            
        case 2
            % Boil over a specified time duration
            mass_initial = input('Enter initial mass (kg): ');
            quality_initial = input('Enter initial quality (fraction): ');
            pressure_initial = input('Enter initial pressure (Pa): ');
            time_duration = input('Enter time duration (seconds): ');
            
            final_pressure = boil_over_time(mass_initial, quality_initial, pressure_initial, time_duration, TANK_VOLUME, HEAT_LOAD);
            fprintf('Boiling over time: Final pressure = %.2f Pa\n', final_pressure);
            
        case 3
            % Vent to a specified pressure
            mass_initial = input('Enter initial mass (kg): ');
            pressure_initial = input('Enter initial pressure (Pa): ');
            pressure_final = input('Enter final pressure (Pa): ');
            
            [mass_final, quality_final] = vent_to_pressure(mass_initial, pressure_initial, pressure_final, TANK_VOLUME);
            fprintf('Venting: Final mass = %.2f kg, Final quality = %.4f\n', mass_final, quality_final);
            
        case 4
            % Exit the program
            fprintf('Exiting the program.\n');
            break;
            
        otherwise
            fprintf('Invalid choice. Please try again.\n');
    end
end
