function result = offload_const_pressure(trailer_mass_initial, station_mass_initial, pressure, station_volume, station_max_fill_fraction, trailer_volume)
    % Calculate initial trailer state 
    density_trailer_initial = trailer_mass_initial / trailer_volume;
    e_trailer_initial = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'PD', 'E', 0, 0, 0, pressure, density_trailer_initial, 1.0);
    e_trailer_initial = e_trailer_initial.Output(1);  % Extracting the energy

    % Calculate initial station state (density and energy)
    density_station_initial = station_mass_initial / station_volume;
    e_station_initial = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'DP', 'E', 0, 0, 0, density_station_initial, pressure, 1.0);
    e_station_initial = e_station_initial.Output(1);

    % Calculate gas and liquid densities
    density_gas = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'QP', 'D', 0, 0, 0, 1, pressure, 1.0);
    density_gas = density_gas.Output(1);
    density_liq = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'QP', 'D', 0, 0, 0, 0, pressure, 1.0);
    density_liq = density_liq.Output(1);

    % Calculate mass of gas when trailer is empty and available liquid mass in trailer
    mass_gas_trailer_empty = trailer_volume * density_gas;
    mass_liquid_available = trailer_mass_initial - mass_gas_trailer_empty;

    % Calculate maximum mass that can be transferred to the station
    mass_station_max = station_volume * density_liq * station_max_fill_fraction;
    mass_transfer_needed = mass_station_max - station_mass_initial;

    % Determine the actual mass to transfer (minimum of available liquid or station capacity)
    mass_transfer = min(mass_transfer_needed, mass_liquid_available);

    % Calculate the volume of gas vented during the process
    volume_transfer = mass_transfer / density_liq;  % Volume transferred in liquid form
    gas_vented = (trailer_mass_initial - mass_transfer) / density_gas - trailer_volume;  % Gas vented from trailer

    % Calculate final masses in trailer and station
    mass_trailer_final = trailer_mass_initial - mass_transfer;
    mass_station_final = station_mass_initial + mass_transfer;

    % Calculate final energy states
    e_trailer_final = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'PD', 'E', 0, 0, 0, pressure, mass_trailer_final / trailer_volume, 1.0);
    e_trailer_final = e_trailer_final.Output(1);
    e_station_final = calllib('REFPROP', 'REFPROPdll', 'PARAHYD', 'PD', 'E', 0, 0, 0, pressure, mass_station_final / station_volume, 1.0);
    e_station_final = e_station_final.Output(1);

    % Calculate energy transferred during the offloading process
    energy_transferred = (e_trailer_final - e_trailer_initial) * mass_trailer_final;

    % Return results as a structure
    result.mass_transfer = mass_transfer;
    result.gas_vented = gas_vented;
    result.final_mass_trailer = mass_trailer_final;
    result.final_mass_station = mass_station_final;
    result.energy_transferred = energy_transferred;
end
