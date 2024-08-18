function [quality_final, mass_final, delta_gas, delta_liq] = ventToPressure(V_t,mass_initial,pressure_initial_t,pressure_final_t)
%treat As Constant Entropy Process
%example Constants
% V_t = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% quality_initial = 0.5;

%% Intial State (Pre-Venting)
rho_intial = mass_initial/V_t; %density
si = py.CoolProp.CoolProp.PropsSI('S','D',rho_intial,'P',pressure_initial_t,'Parahydrogen'); %initial Entropy
xi = py.CoolProp.CoolProp.PropsSI('Q','D',rho_intial,'P',pressure_initial_t,'Parahydrogen'); %initial Quality
mass_liquid_initial = (1-xi) * mass_initial;
mass_gas_initial = mass_intial - mass_liquid_initial;
% v_tot_initial = V_t/mass_intial;
% v_gas_initial = xi * (V_t/mass_initial);
% v_liquid_intial = (1-xi) * (V_t/mass_initial);
% volume_gas_initial = v_gas_initial * mass_gas_initial;
% volume_liquid_initial = v_liquid_intial * mass_liquid_initial;

%% Final State (Post Venting)
rho_f = py.CoolProp.CoolProp.PropsSI('D','P',pressure_final_t,'S',si,'Parahydrogen'); %final Density
xf = py.CoolProp.CoolProp.PropsSI('Q','P',pressure_final_t,'S',si,'Parahydrogen'); %final Quality
mass_f = rho_f * V_t; %final Mixture Mass
mass_liquid_final = (1-xf) * mass_f; %mass Of Remaining Liquid
mass_gas_final = xf * mass_f; %mass of Remaining Gas
% v_gas_final = V_t/mass_gas_final;
% v_liquid_final = V_t/mass_liquid_final;
% volume_gas_final = v_gas_final *

% v_tot_final = V_t/mass_f; %specific Volume of Final Mixure
% vl = (1-xf)*v; %final Liquid Specfic Volume
% V_liquid = vl * mass_liquid_final; %final Liquid Volume, rest of volume in tank is gas volume.
% V_gas = V_t - V_liquid;
%Not sure what outputs are needed. Code must be adjusted after speaking with Greg

%% Results
quality_final = xf;
mass_final = mass_f;
delta_gas = mass_gas_initial - mass_gas_final;
delta_liq = mass_liquid_initial - mass_liquid_final;
end