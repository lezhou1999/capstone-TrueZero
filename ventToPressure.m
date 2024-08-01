function [quality_final, mass_final] = ventToPressure(mass_initial,pressure_initial_t,pressure_final_t)
%treat As Constant Entropy Process
%example Constants
% V_s = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% quality_initial = 0.5;

rho = mass_initial/V_s; %density
si = py.CoolProp.CoolProp.PropsSI('S','D',rho,'P',pressure_initial_t,'Parahydrogen'); %initial Entropy
rho_f = py.CoolProp.CoolProp.PropsSI('D','P',pressure_final_t,'S',si,'Parahydrogen'); %final Density
xf = py.CoolProp.CoolProp.PropsSI('Q','P',pressure_final_t,'S',si,'Parahydrogen'); %final Quality
mass_f = rho_f * V_s; %final Mixture Mass
mass_l = (1-xf) * mass_final; %mass Of Remaining Liquid
v = V_s/mass_final; %specific Volume of Final Mixure
vl = (1-xf)*v; %final Liquid Specfic Volume
V_liquid = vl * mass_l; %final Liquid Volume
V_gas = V_s - V_liquid;
%Not sure what outputs are needed. Code must be adjusted after speaking with Greg

quality_final = xf;
mass_final = mass_f;