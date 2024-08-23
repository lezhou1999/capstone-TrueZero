function [quality_final, pressure_final] = boilOverTime(V_trailer,mass_trailer_initial,pressure_trailer_initial,time_duration)
%Example Constants
% V_t = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% time_duration = 5*24*3600;

%% Calculate Initial & Final Conditions
rho = mass_trailer_initial/V_trailer; %density
%quality_initial = 0.5;
ui = py.CoolProp.CoolProp.PropsSI('U','D',rho,'P',pressure_trailer_initial,'Parahydrogen'); %initial Internal Energy
uf = ui + (heat_load * time_duration)/mass_trailer_initial; %final Internal Energy
%Constant density assumed
pressure_final_t = py.CoolProp.CoolProp.PropsSI('P','D',rho,'U',uf,'Parahydrogen'); %final Pressure
xf = py.CoolProp.CoolProp.PropsSI('Q','D',rho,'U',uf,'Parahydrogen'); %final Quality


quality_final = xf;
pressure_final = pressure_final_t;
end