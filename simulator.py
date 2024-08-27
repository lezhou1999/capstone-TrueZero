import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
import math
import tkinter as tk
from tkinter import messagebox
from AllFunctions import (boil_to_pressure, offload_with_raising_pressure,
                          offload_const_pressure, boil_over_time, vent_trailer,
                          fill_trailer_const_pressure)

# Initialize REFPROP
# os.environ['RPPREFIX'] = r'C:\coding'

os.environ['RPPREFIX']=r'C:\Program Files\REFPROP'
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum


# Function to run the simulation
def run_simulation():
    try:
        # Get values from user input
        trailer_volume = float(entry_trailer_volume.get())
        TRAILER_HEAT_LOAD = float(entry_heat_load.get())
        trailer_pressure_max = float(entry_trailer_pressure_max.get())
        station_pressure_max = float(entry_station_pressure_max.get())
        trailer_pressure_fill = float(entry_trailer_pressure_fill.get())
        station_pressure_initial = float(entry_station_pressure_initial.get())
        station_volume = float(entry_station_volume.get())
        station_max_fill_fraction = float(entry_station_max_fill_fraction.get())
        time_transportation = float(entry_time_transportation.get())
        offload_pressure = float(entry_offload_pressure.get())
        trailer_mass_max = float(entry_trailer_mass_max.get())
        station_mass_initial = float(entry_station_mass_initial.get())
        trailer_mass_initial = float(entry_trailer_mass_initial.get())
        trailer_pressure_initial = float(entry_trailer_pressure_initial.get())

        # Start simulation
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Starting H2 Trailer Cycle Simulation\n")

        # Step 1: Heat up to station pressure
        target_pressure = station_pressure_initial
        final_enthalpy, time_duration = boil_to_pressure(trailer_mass_initial, trailer_pressure_initial,
                                                         target_pressure)
        output_text.insert(tk.END,
                           f"\n1. Heating trailer to station pressure\nHeated to: Pressure = {target_pressure:.2f} Pa, Time taken = {time_duration:.2f} seconds\n")

        # Step 2: Offload with rising pressure up to 2.5 atm
        final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
            target_pressure, station_pressure_initial, trailer_mass_initial, station_mass_initial, station_volume,
            station_mass_initial * station_max_fill_fraction, offload_pressure, trailer_pressure_max, trailer_volume
        )
        output_text.insert(tk.END,
                           f"\n2. Offloading with rising pressure up to 2.5 atm\nAfter rising pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg\n")

        # Calculate station maximum mass
        station_max_mass = station_volume * \
                           RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, offload_pressure, 0, [1.0]).Output[
                               0] * station_max_fill_fraction

        # Step 3: Offload with constant pressure at 2.5 atm
        if final_station_mass < station_max_mass:
            mass_transfer, energy_added = offload_const_pressure(
                final_trailer_mass, final_station_mass, offload_pressure, station_volume, station_max_fill_fraction
            )
            final_trailer_mass -= mass_transfer
            final_station_mass += mass_transfer
            output_text.insert(tk.END,
                               f"\n3. Offloading with constant pressure at 2.5 atm\nAfter constant pressure offload: Station mass = {final_station_mass:.2f} kg, Trailer mass = {final_trailer_mass:.2f} kg\n")
        else:
            output_text.insert(tk.END, "\n3. Skipping constant pressure offload - station is already full\n")

        # Step 4: Delay boil over 1 day transportation
        pressure_after_transport, quality_final = boil_over_time(final_trailer_mass, final_pressure,
                                                                 time_transportation)
        output_text.insert(tk.END,
                           f"\n4. Boiling over 1 day transportation\nAfter transport: Pressure = {pressure_after_transport:.2f} Pa, Quality = {quality_final:.2f}\n")

        # Step 5: Venting before filling the trailer
        mass_after_vent, mass_vented, _, _ = vent_trailer(final_trailer_mass, pressure_after_transport,
                                                          trailer_pressure_fill)
        output_text.insert(tk.END,
                           f"\n5. Venting trailer before filling\nAfter venting: Mass vented = {mass_vented:.2f} kg, Pressure = {trailer_pressure_fill:.2f} Pa\n")

        # Step 6: Fill the trailer
        mass_change, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_after_vent, trailer_mass_max,
                                                                                  trailer_pressure_fill, trailer_volume)
        mass_after_fill = mass_after_vent + mass_change
        output_text.insert(tk.END,
                           f"\n6. Filling the trailer\nAfter filling: Mass = {mass_after_fill:.2f} kg, Pressure = {trailer_pressure_fill:.2f} Pa\n")

        output_text.insert(tk.END, "\nH2 Trailer Cycle Simulation Complete\n")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")


# Create main window
root = tk.Tk()
root.title("H2 Trailer Cycle Simulation")

# Input fields for constants and initial conditions
tk.Label(root, text="Trailer Volume (m^3):").grid(row=0, column=0, sticky="e")
entry_trailer_volume = tk.Entry(root)
entry_trailer_volume.grid(row=0, column=1)
entry_trailer_volume.insert(0, "32.0")

tk.Label(root, text="Trailer Heat Load (W):").grid(row=1, column=0, sticky="e")
entry_heat_load = tk.Entry(root)
entry_heat_load.grid(row=1, column=1)
entry_heat_load.insert(0, "40.7")

tk.Label(root, text="Trailer Pressure Max (Pa):").grid(row=2, column=0, sticky="e")
entry_trailer_pressure_max = tk.Entry(root)
entry_trailer_pressure_max.grid(row=2, column=1)
entry_trailer_pressure_max.insert(0, "1204514.0")

tk.Label(root, text="Station Pressure Max (Pa):").grid(row=3, column=0, sticky="e")
entry_station_pressure_max = tk.Entry(root)
entry_station_pressure_max.grid(row=3, column=1)
entry_station_pressure_max.insert(0, "550000")

tk.Label(root, text="Trailer Pressure Fill (Pa):").grid(row=4, column=0, sticky="e")
entry_trailer_pressure_fill = tk.Entry(root)
entry_trailer_pressure_fill.grid(row=4, column=1)
entry_trailer_pressure_fill.insert(0, "131000")

tk.Label(root, text="Station Pressure Initial (Pa):").grid(row=5, column=0, sticky="e")
entry_station_pressure_initial = tk.Entry(root)
entry_station_pressure_initial.grid(row=5, column=1)
entry_station_pressure_initial.insert(0, "202650")

tk.Label(root, text="Station Volume (m^3):").grid(row=6, column=0, sticky="e")
entry_station_volume = tk.Entry(root)
entry_station_volume.grid(row=6, column=1)
entry_station_volume.insert(0, "13.33")

tk.Label(root, text="Station Max Fill Fraction:").grid(row=7, column=0, sticky="e")
entry_station_max_fill_fraction = tk.Entry(root)
entry_station_max_fill_fraction.grid(row=7, column=1)
entry_station_max_fill_fraction.insert(0, "0.95")

tk.Label(root, text="Time Transportation (s):").grid(row=8, column=0, sticky="e")
entry_time_transportation = tk.Entry(root)
entry_time_transportation.grid(row=8, column=1)
entry_time_transportation.insert(0, "86400")  # 1 day

tk.Label(root, text="Offload Pressure (Pa):").grid(row=9, column=0, sticky="e")
entry_offload_pressure = tk.Entry(root)
entry_offload_pressure.grid(row=9, column=1)
entry_offload_pressure.insert(0, "353312")

tk.Label(root, text="Trailer Mass Max (kg):").grid(row=10, column=0, sticky="e")
entry_trailer_mass_max = tk.Entry(root)
entry_trailer_mass_max.grid(row=10, column=1)
entry_trailer_mass_max.insert(0, "2100")

tk.Label(root, text="Station Mass Initial (kg):").grid(row=11, column=0, sticky="e")
entry_station_mass_initial = tk.Entry(root)
entry_station_mass_initial.grid(row=11, column=1)
entry_station_mass_initial.insert(0, "150")

tk.Label(root, text="Trailer Mass Initial (kg):").grid(row=12, column=0, sticky="e")
entry_trailer_mass_initial = tk.Entry(root)
entry_trailer_mass_initial.grid(row=12, column=1)
entry_trailer_mass_initial.insert(0, "2100")

tk.Label(root, text="Trailer Pressure Initial (Pa):").grid(row=13, column=0, sticky="e")
entry_trailer_pressure_initial = tk.Entry(root)
entry_trailer_pressure_initial.grid(row=13, column=1)
entry_trailer_pressure_initial.insert(0, "160000")

# Run Simulation button
run_button = tk.Button(root, text="Run Simulation", command=run_simulation)
run_button.grid(row=14, column=0, columnspan=2, pady=10)

# Output text area
output_text = tk.Text(root, height=15, width=80)
output_text.grid(row=15, column=0, columnspan=2, pady=10)

# Start the application
root.mainloop()
