function [deltaLiq, deltaGas] = fillTrailer(mass_trailer_initial,mass_trailer_final,V_trailer,pressure)%,U_total)
%Constant Pressure Process

%% Initial State
%Calculate Initial Net Density
rho_intial = mass_trailer_initial/V_trailer;
%Calculate Initial Quality
x_initial = py.CoolProp.CoolProp.PropsSI('Q','D',rho_intial,'P',pressure,'Parahydrogen');
%u_initial = py.CoolProp.CoolProp.PropsSI('U','D',rho_intial,'P',pressure,'Parahydrogen');

%% Final State
%Calculate Final Net Density
rho_final = mass_trailer_final/V_trailer;
%Calculate Final Quality
x_final = py.CoolProp.CoolProp.PropsSI('Q','D',rho_final,'P',presssure,'Parahydrogen'); 
%u_final = py.CoolProp.CoolProp.PropsSI('U','D',rho_final,'P',pressure,'Parahydrogen');

%% Calculate change in liquid and gas masses
% mass_change = mass_final - mass_initial;
deltaLiq = mass_trailer_final*(1-x_final) - mass_trailer_initial*(1-x_initial);
deltaGas = mass_trailer_initial*(x_initial) - mass_trailer_final*(x_final);
end


