import tkinter as tk
from tkinter import ttk, messagebox
import os
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from AllFunctions import (boil_to_pressure, offload_with_raising_pressure,
                          offload_const_pressure, boil_over_time, vent_trailer,
                          fill_trailer_const_pressure)

# Initialize REFPROP
os.environ['RPPREFIX']=r'C:\Program Files\REFPROP'
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum

# Constants
TRAILER_VOLUME = 32.0  # m^3
STATION_VOLUME = 13.33  # m^3
TRAILER_MASS_INITIAL = 2100  # kg
TRAILER_PRESSURE_INITIAL = 160000  # Pa
TIME_TRANSPORTATION = 1 * 24 * 3600  # 1 day in seconds
TRAILER_PRESSURE_FILL = 131000  # Pa
STATION_MAX_MASS = 800  # kg
STATION_MAX_PRESSURE = 400000  # Pa (3.0 barg)
STATION_VENT_PRESSURE = STATION_MAX_PRESSURE * 0.9  # 90% of max pressure
trailer_pressure_max = 1204514.0  # Pa (160 psig, 174.7 psia)
STATION_MAX_FILL_FRACTION = 0.95

# Function to run a study
def run_study(study_id, num_stations, station_mass_initial, station_pressure_initial):
    print(f"\nRunning Study {study_id}")
    total_mass_received = 0
    total_mass_vented = 0
    trailer_mass = TRAILER_MASS_INITIAL
    trailer_pressure = TRAILER_PRESSURE_INITIAL

    for station in range(num_stations):
        final_enthalpy, time_duration = boil_to_pressure(trailer_mass, trailer_pressure, station_pressure_initial)
        trailer_pressure = station_pressure_initial

        final_pressure, final_station_mass, final_trailer_mass = offload_with_raising_pressure(
            trailer_pressure, station_pressure_initial, trailer_mass,
            station_mass_initial, STATION_VOLUME, STATION_MAX_MASS, STATION_MAX_PRESSURE, trailer_pressure_max,
            TRAILER_VOLUME
        )

        if final_pressure > STATION_VENT_PRESSURE:
            final_station_mass, mass_vented_station, _, _ = vent_trailer(final_station_mass, final_pressure,
                                                                         STATION_VENT_PRESSURE)
            total_mass_vented += mass_vented_station
            final_pressure = STATION_VENT_PRESSURE

        station_max_mass = STATION_VOLUME * \
                           RP.REFPROPdll("PARAHYD", "PQ", "D", MASS_BASE_SI, 0, 0, final_pressure, 0, [1.0]).Output[
                               0] * STATION_MAX_FILL_FRACTION

        if final_station_mass < station_max_mass:
            mass_transfer, energy_added = offload_const_pressure(
                final_trailer_mass, final_station_mass, final_pressure,
                STATION_VOLUME, STATION_MAX_FILL_FRACTION
            )
            final_trailer_mass -= mass_transfer
            final_station_mass += mass_transfer

        mass_received = final_station_mass - station_mass_initial
        total_mass_received += mass_received
        trailer_mass = final_trailer_mass
        trailer_pressure = final_pressure

    pressure_after_transport, quality_after_transport = boil_over_time(trailer_mass, trailer_pressure,
                                                                       TIME_TRANSPORTATION)

    mass_after_vent, mass_vented_trailer, mass_liq_final, mass_gas_final = vent_trailer(trailer_mass,
                                                                                        pressure_after_transport,
                                                                                        TRAILER_PRESSURE_FILL)
    total_mass_vented += mass_vented_trailer

    mass_change, mass_liq_added, mass_gas_added = fill_trailer_const_pressure(mass_after_vent, TRAILER_MASS_INITIAL,
                                                                              TRAILER_PRESSURE_FILL, TRAILER_VOLUME)

    return total_mass_received, total_mass_vented

# Define study parameters
studies = [
    {"id": "1.1", "num_stations": 2, "starting_mass": 100, "pressure": 250000},
    {"id": "2.1", "num_stations": 2, "starting_mass": 100, "pressure": 300000},
    {"id": "3.1", "num_stations": 2, "starting_mass": 100, "pressure": 350000},
    {"id": "1.2", "num_stations": 3, "starting_mass": 200, "pressure": 250000},
    {"id": "2.2", "num_stations": 3, "starting_mass": 200, "pressure": 300000},
    {"id": "3.2", "num_stations": 3, "starting_mass": 200, "pressure": 350000},
    {"id": "1.3", "num_stations": 4, "starting_mass": 350, "pressure": 250000},
    {"id": "2.3", "num_stations": 4, "starting_mass": 350, "pressure": 300000},
    {"id": "3.3", "num_stations": 4, "starting_mass": 350, "pressure": 350000},
    {"id": "1.4", "num_stations": 5, "starting_mass": 440, "pressure": 250000},
    {"id": "2.4", "num_stations": 5, "starting_mass": 440, "pressure": 300000},
    {"id": "3.4", "num_stations": 5, "starting_mass": 440, "pressure": 350000},
    {"id": "1.5", "num_stations": 6, "starting_mass": 500, "pressure": 250000},
    {"id": "2.5", "num_stations": 6, "starting_mass": 500, "pressure": 300000},
    {"id": "3.5", "num_stations": 6, "starting_mass": 500, "pressure": 350000},
]

# Function to run a single study
def run_single_study():
    study_id = study_id_var.get()
    study = next((s for s in studies if s["id"] == study_id), None)
    if study:
        return run_study(study["id"], study["num_stations"], study["starting_mass"], study["pressure"])
    else:
        messagebox.showerror("Error", f"Study {study_id} not found.")
        return None

# Function to run all studies
def run_all_studies():
    results = {}
    for study in studies:
        mass_received, mass_vented = run_study(study["id"], study["num_stations"], study["starting_mass"],
                                               study["pressure"])
        results[study["id"]] = {
            "num_stations": study["num_stations"],
            "starting_mass": study["starting_mass"],
            "pressure": study["pressure"],
            "mass_received": mass_received,
            "mass_vented": mass_vented
        }
    return results

# GUI-related functions
def on_run_single_study():
    result = run_single_study()
    if result:
        mass_received, mass_vented = result
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Study {study_id_var.get()}:\n")
        output_text.insert(tk.END, f"  Total mass received: {mass_received:.2f} kg\n")
        output_text.insert(tk.END, f"  Total mass vented: {mass_vented:.2f} kg\n")

def on_run_all_studies():
    results = run_all_studies()
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\nFinal Results for All Studies:\n")
    for study_id, data in results.items():
        output_text.insert(tk.END, f"\nStudy {study_id}:\n")
        output_text.insert(tk.END, f"  Number of stations: {data['num_stations']}\n")
        output_text.insert(tk.END, f"  Starting mass: {data['starting_mass']} kg\n")
        output_text.insert(tk.END, f"  Pressure: {data['pressure']} Pa\n")
        output_text.insert(tk.END, f"  Total mass received: {data['mass_received']:.2f} kg\n")
        output_text.insert(tk.END, f"  Total mass vented: {data['mass_vented']:.2f} kg\n")

    max_received = max(results.items(), key=lambda x: x[1]['mass_received'])
    min_vented = min(results.items(), key=lambda x: x[1]['mass_vented'])

    output_text.insert(tk.END, "\nAnalysis:\n")
    output_text.insert(tk.END, f"Most efficient for mass received: Study {max_received[0]}\n")
    output_text.insert(tk.END, f"  Mass Received: {max_received[1]['mass_received']:.2f} kg\n")
    output_text.insert(tk.END, f"Least mass vented: Study {min_vented[0]}\n")
    output_text.insert(tk.END, f"  Mass Vented: {min_vented[1]['mass_vented']:.2f} kg\n")

# Create main window
root = tk.Tk()
root.title("H2 Trailer Cycle Study")

# Study selection
study_id_var = tk.StringVar()
tk.Label(root, text="Select Study ID:").grid(row=0, column=0, sticky="e")
study_id_dropdown = ttk.Combobox(root, textvariable=study_id_var)
study_id_dropdown['values'] = [study["id"] for study in studies]
study_id_dropdown.grid(row=0, column=1)
study_id_dropdown.current(0)  # Default to the first study ID

# Run single study button
run_single_button = ttk.Button(root, text="Run Single Study", command=on_run_single_study)
run_single_button.grid(row=1, column=0, columnspan=2, pady=10)

# Run all studies button
run_all_button = ttk.Button(root, text="Run All Studies", command=on_run_all_studies)
run_all_button.grid(row=2, column=0, columnspan=2, pady=10)

# Output text area
output_text = tk.Text(root, height=20, width=60)
output_text.grid(row=3, column=0, columnspan=2, pady=10)

# Start the application
root.mainloop()
