function [heat_added, liq_recieved] = offloadConstP(mass_trailer_initial,mass_station_initial,pressure,V_station,V_trailer,max_station_fill_frac)
%example Constants
% V_s = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% quality_initial = 0.5;

%% Calculate Maximum Liquid That Trailer Can Offload
rho_trailer_initial = mass_trailer_initial/V_trailer; %trailer Initial Density
u_trailer_intial = py.CoolProp.CoolProp.PropsSI('U','D',rho_trailer_initial,'P',pressure,'Parahydrogen');
%xi = py.CoolProp.CoolProp.PropsSI('Q','D',rho_trailer_initial,'P',presure,'Parahydrogen');%initial Quality (Trailer)
%mass_gas_initial = xi * mass_trailer_initial; %initial Gas Mass, WHY DO WE NEED THIS
%Using x = 1, calculate gas density
rho_gas = py.CoolProp.CoolProp.PropsSI('D','P',pressure,'Q',1,'Parahydrogen');
%Mass of gas in trailer if empty of liquid 
mass_gas_empty = V_trailer * rho_gas;
%Available Liquid to be Offloaded
mass_liquid_available = mass_trailer_initial - mass_gas_empty; %add if statement for if the mass is negative to assume zero. 

%% Calculate How Much Mass Required to Fill Station
rho_liq = py.CoolProp.CoolProp.PropsSI('D','P',pressure,'Q',0,'Parahydrogen');
mass_station_max = V_station * rho_liq * max_station_fill_frac;
mass_transfer_needed = mass_station_max - mass_station_initial;

%% Use Smaller Quantity for Results
if mass_liquid_available < mass_transfer_needed
    mass_trailer_final = mass_gas_empty;
    mass_station_final = mass_station_initial + mass_liquid_available;
    %How to get volume of liquid now in station?? Leftover VOlume is Gas,
    %find its mass, calculate gas left at station???
    u_trailer_final = py.CoolProp.CoolProp.PropsSI('U','Q',1,'P',pressure,'Parahydrogen');
else
    mass_trailer_final = mass_trailer_initial - mass_transfer_needed;
    mass_station_final = mass_station_initial + mass_transfer_needed;
    rho_t_final = mass_trailer_final/V_trailer;
    u_trailer_final = py.CoolProp.CoolProp.PropsSI('U','D',rho_t_final,'P',pressure,'Parahydrogen');
end

%% Calculate Heat Added to Trailer

Q = (u_trailer_final - u_trailer_intial) * mass_trailer_final;

%% Output Results
heat_added = Q;
liq_recieved = mass_station_final - mass_station_initial;
end
 %add trailer mass and trailer pressure for all functions and if station is
 %involved do station mass and station pressure