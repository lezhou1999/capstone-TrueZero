function [quality_final, time_duration] = boilToPressure(V_t,mass_initial,pressure_initial_t,pressure_final_t)
%Example Constants
% V_t = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W

%% Calculate Initial & Final States
rho = mass_initial/V_t; %density
%quality_initial = 0.5;
xf = py.CoolProp.CoolProp.PropsSI('Q','D',rho,'P',pressure_final_t,'Parahydrogen'); %final Quality
ui = py.CoolProp.CoolProp.PropsSI('U','D',rho,'P',pressure_initial_t,'Parahydrogen'); %initial Internal Energy
uf = py.CoolProp.CoolProp.PropsSI('U','D',rho,'P',pressure_final_t,'Parahydrogen'); %final Internal Energy
dU = mass_initial *(uf - ui); %change in internal energy
dt = dU/heat_load; %time Duration, using 40.7Watts for heat load

quality_final = xf;
time_duration = dt;
end