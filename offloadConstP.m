function [heat_added, liq_recieved] = offloadConstP(mass_t_initial,mass_s_initial,presure,V_s,V_t,max_s_fill_frac)
%example Constants
% V_s = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% quality_initial = 0.5;

%% Calculate Maximum Liquid That Trailer Can Offload
rho_t_initial = mass_t_initial/V_t; %trailer Initial Density
xi = py.CoolProp.CoolProp.PropsSI('Q','D',rho_t_initial,'P',presure,'Parahydrogen');%initial Quality (Trailer)
mass_gas_initial = xi * mass_t_initial; %initial Gas Mass, WHY DO WE NEED THIS
%Using x = 1, calculate gas density
rho_gas = py.CoolProp.CoolProp.PropsSI('D','P',pressure,'Q',1,'Parahydrogen');
%Mass of gas in trailer if empty of liquid 
mass_gas_empty = V_t * rho_gas;
%Available Liquid to be Offloaded
mass_liquid_available = mass_t_initial - mass_gas_empty;

%% Calculate How Much Mass Required to Fill Station
rho_liq = py.CoolProp.CoolProp.PropsSI('D','P',pressure,'Q',0,'Parahydrogen');
mass_s_max = V_s * rho_liq * max_s_fill_frac;
mass_s_refuel = mass_s_max - mass_s_initial;

%% Use Smaller Quantity for Results
if mass_liquid_available < mass_s_refuel
    mass_t_final = mass_gas_empty;
    mass_s_final = mass_s_initial + mass_liquid_available;
    %How to get volume of liquid now in station?? Leftover VOlume is Gas,
    %find its mass, calculate gas left at station???
    u_t_final = py.CoolProp.CoolProp.PropsSI('U','Q',1,'P',pressure,'Parahydrogen');
else
    mass_t_final = mass_t_initial - mass_s_refuel;
    mass_s_final = mass_s_initial + mass_s_refuel;
    rho_t_final = mass_t_final/V_t;
    u_t_final = py.CoolProp.CoolProp.PropsSI('U','D',rho_t_final,'P',pressure,'Parahydrogen');
end

%% Calculate Heat Added to Trailer
u_t_intial = py.CoolProp.CoolProp.PropsSI('U','D',rho_t_intial,'P',pressure,'Parahydrogen');
Q = (u_t_final - u_t_intial) * mass_t_final;

%% Output Results
heat_added = Q;
liq_recieved = mass_s_final - mass_s_initial;

