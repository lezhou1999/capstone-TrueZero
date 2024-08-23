function [mass_trailer_final, mass_vented, mass_liquid_final, mass_gas_final] = ventToPressure(V_trailer,mass_trailer_initial,pressure_trailer_initial,pressure_trailer_final)
%treat As Constant Entropy Process
%example Constants
% V_t = 32; %m^3
% mass_initial=1680; %kg
% pressure_final_t = 506625; %kPa
% pressure_inital_t = 202650; %kPa
% heat_load = 40.7; %W
% quality_initial = 0.5;

%% Intial State (Pre-Venting)
rho_intial = mass_trailer_initial/V_trailer; %density
si = py.CoolProp.CoolProp.PropsSI('S','D',rho_intial,'P',pressure_trailer_initial,'Parahydrogen'); %initial Entropy
%xi = py.CoolProp.CoolProp.PropsSI('Q','D',rho_intial,'P',pressure_trailer_initial,'Parahydrogen'); %initial Quality
%mass_liquid_initial = (1-xi) * mass_trailer_initial;
%mass_gas_initial = mass_intial_trailer - mass_liquid_initial;

%% Final State (Post Venting)
%rho_f = py.CoolProp.CoolProp.PropsSI('D','P',pressure_trailer_final,'S',si,'Parahydrogen'); %final Density
xf = py.CoolProp.CoolProp.PropsSI('Q','P',pressure_trailer_final,'S',si,'Parahydrogen'); %final Quality
%mass_f = rho_f * V_trailer; %final Mixture Mass
mass_liquid_final = (1-xf) * mass_trailer_initial; %mass Of Remaining Liquid, why do we re-use initial mass here?? (Greg's Instructions), Can calculate final mass with final mixture density and trailer volume. 
rho_liquid = py.CoolProp.CoolProp.PropsSI('D','P',pressure_trailer_final,'Q',0,'Parahydrogen');
liquid_volume = mass_liquid_final/rho_liquid;
gas_volume = V_trailer-liquid_volume;
rho_gas = py.CoolProp.CoolProp.PropsSI('D','P',pressure_trailer_final,'Q',1,'Parahydrogen');

%% Results
mass_gas_final = gas_volume * rho_gas;
mass_trailer_final = mass_gas_final + mass_liquid_final;
mass_vented = mass_trailer_initial - mass_trailer_final;
end

