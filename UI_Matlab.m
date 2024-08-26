function create_gui()
    % Create the first UI figure
    create_trailer_ui();
end

function create_trailer_ui()
    % Create the UI figure
    fig = uifigure('Name', 'Input For Study 1.1', 'Position', [100, 100, 500, 450]);

    % Create input fields for trailer parameters
    uilabel(fig, 'Position', [20, 400, 150, 22], 'Text', 'Trailer Volume (m^3):');
    trailerVolumeField = uieditfield(fig, 'numeric', 'Position', [200, 400, 250, 22], 'Value', 32.0);

    uilabel(fig, 'Position', [20, 360, 150, 22], 'Text', 'Trailer Heat Load (W):');
    trailerHeatLoadField = uieditfield(fig, 'numeric', 'Position', [200, 360, 250, 22], 'Value', 40.7);

    uilabel(fig, 'Position', [20, 320, 150, 22], 'Text', 'Trailer Pressure Max (Pa):');
    trailerPressureMaxField = uieditfield(fig, 'numeric', 'Position', [200, 320, 250, 22], 'Value', 1204514.0);

    uilabel(fig, 'Position', [20, 280, 150, 22], 'Text', 'Trailer Pressure Fill (Pa):');
    trailerPressureFillField = uieditfield(fig, 'numeric', 'Position', [200, 280, 250, 22], 'Value', 131000.0);

    uilabel(fig, 'Position', [20, 240, 150, 22], 'Text', 'Trailer Pressure Initial (Pa):');
    trailerPressureInitialField = uieditfield(fig, 'numeric', 'Position', [200, 240, 250, 22], 'Value', 160000.0);

    uilabel(fig, 'Position', [20, 200, 150, 22], 'Text', 'Trailer Mass Initial (kg):');
    trailerMassInitialField = uieditfield(fig, 'numeric', 'Position', [200, 200, 250, 22], 'Value', 2100.0);

    uilabel(fig, 'Position', [20, 160, 150, 22], 'Text', 'Trailer Mass Max (kg):');
    trailerMassMaxField = uieditfield(fig, 'numeric', 'Position', [200, 160, 250, 22], 'Value', 2100.0);

    % Create a button to proceed to the next screen
    uibutton(fig, 'Position', [200, 50, 100, 30], 'Text', 'Next', ...
        'ButtonPushedFcn', @(btn, event) create_station_ui(trailerVolumeField.Value, ...
                                                           trailerHeatLoadField.Value, ...
                                                           trailerPressureMaxField.Value, ...
                                                           trailerPressureFillField.Value, ...
                                                           trailerPressureInitialField.Value, ...
                                                           trailerMassInitialField.Value, ...
                                                           trailerMassMaxField.Value));
end

function create_station_ui(trailerVolume, trailerHeatLoad, trailerPressureMax, trailerPressureFill, trailerPressureInitial, trailerMassInitial, trailerMassMax)
    % Create the UI figure
    fig = uifigure('Name', 'Input For Study 1.2', 'Position', [100, 100, 500, 450]);

    % Create input fields for station parameters
    uilabel(fig, 'Position', [20, 360, 150, 22], 'Text', 'Station Pressure Max (Pa):');
    stationPressureMaxField = uieditfield(fig, 'numeric', 'Position', [200, 360, 250, 22], 'Value', 550000);

    uilabel(fig, 'Position', [20, 320, 150, 22], 'Text', 'Station Pressure Initial (Pa):');
    stationPressureInitialField = uieditfield(fig, 'numeric', 'Position', [200, 320, 250, 22], 'Value', 202650);

    uilabel(fig, 'Position', [20, 280, 150, 22], 'Text', 'Station Volume (m^3):');
    stationVolumeField = uieditfield(fig, 'numeric', 'Position', [200, 280, 250, 22], 'Value', 13.33);

    uilabel(fig, 'Position', [20, 240, 150, 22], 'Text', 'Station Mass Initial (kg):');
    stationMassInitialField = uieditfield(fig, 'numeric', 'Position', [200, 240, 250, 22], 'Value', 150.0);

    uilabel(fig, 'Position', [20, 200, 150, 22], 'Text', 'Station Max Fill Fraction:');
    stationMaxFillFractionField = uieditfield(fig, 'numeric', 'Position', [200, 200, 250, 22], 'Value', 0.95);

    uilabel(fig, 'Position', [20, 160, 150, 22], 'Text', 'Offload Pressure (Pa):');
    offloadPressureField = uieditfield(fig, 'numeric', 'Position', [200, 160, 250, 22], 'Value', 353312);

    % Create a button to proceed to the next screen
    uibutton(fig, 'Position', [200, 50, 100, 30], 'Text', 'Next', ...
        'ButtonPushedFcn', @(btn, event) create_other_ui(trailerVolume, trailerHeatLoad, ...
                                                         trailerPressureMax, trailerPressureFill, ...
                                                         trailerPressureInitial, trailerMassInitial, ...
                                                         trailerMassMax, stationPressureMaxField.Value, ...
                                                         stationPressureInitialField.Value, stationVolumeField.Value, ...
                                                         stationMassInitialField.Value, stationMaxFillFractionField.Value, ...
                                                         offloadPressureField.Value));
end

function create_other_ui(trailerVolume, trailerHeatLoad, trailerPressureMax, trailerPressureFill, trailerPressureInitial, ...
                         trailerMassInitial, trailerMassMax, stationPressureMax, stationPressureInitial, ...
                         stationVolume, stationMassInitial, stationMaxFillFraction, offloadPressure)
    % Create the UI figure
    fig = uifigure('Name', 'Input For Study 1.3', 'Position', [100, 100, 500, 450]);

    % Create input fields for time and transportation parameters
    uilabel(fig, 'Position', [20, 360, 150, 22], 'Text', 'Time Transportation (s):');
    timeTransportationField = uieditfield(fig, 'numeric', 'Position', [200, 360, 250, 22], ...
                                          'Value', 1 * 24 * 3600);

    % Create a button to finish and display the waiting message
    uibutton(fig, 'Position', [200, 50, 100, 30], 'Text', 'Finish', ...
        'ButtonPushedFcn', @(btn, event) display_waiting_message(trailerMassInitial, stationMassInitial, ...
                                                                 offloadPressure, stationVolume, trailerVolume, ...
                                                                 stationMaxFillFraction, trailerPressureInitial, ...
                                                                 timeTransportationField.Value));
end

function display_waiting_message(trailerMassInitial, stationMassInitial, pressure, stationVolume, trailerVolume, maxStationFillFrac, trailerPressureInitial, timeTransportation)
    % Create the UI figure
    fig = uifigure('Name', 'Results', 'Position', [100, 100, 500, 450]);

    % Display the "waiting calculations" message
    uilabel(fig, 'Position', [50, 140, 400, 22], 'Text', 'Waiting calculations...', 'HorizontalAlignment', 'center');

    % Pause briefly to simulate waiting
    pause(2);

    % Call the offloadConstP function
    [heat_added, liq_recieved] = offloadConstP(trailerMassInitial, stationMassInitial, ...
                                               pressure, stationVolume, trailerVolume, maxStationFillFrac);

    % Update the label with the results
    uilabel(fig, 'Position', [50, 100, 400, 22], 'Text', sprintf('Heat Added: %.2f J', heat_added), 'HorizontalAlignment', 'center');
    uilabel(fig, 'Position', [50, 60, 400, 22], 'Text', sprintf('Liquid Received: %.2f kg', liq_recieved), 'HorizontalAlignment', 'center');
end
