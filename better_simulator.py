import tkinter as tk
from tkinter import messagebox
import CoolProp.CoolProp as CP


def calculate_density():
    try:
        pressure = float(entry_pressure.get())
        quality = float(entry_quality.get())
        if not (0 <= quality <= 1):
            raise ValueError("Quality should be between 0 and 1.")
        density = CP.PropsSI('D', 'P', pressure, 'Q', quality, 'parahydrogen')
        result_label.config(text=f"Density: {density:.2f} kg/m^3")
    except ValueError as ve:
        messagebox.showerror("Input Error", f"Input should be between 0 and 1!\n{ve}")
    except Exception as e:
        messagebox.showerror("Calculation Error", f"Error in calculation: {e}")


def setup_ui(root):
    root.title("Density Calculator")

    # Layout using grid
    label_pressure = tk.Label(root, text="Pressure (Pa)")
    label_pressure.grid(row=0, column=0)

    global entry_pressure
    entry_pressure = tk.Entry(root)
    entry_pressure.grid(row=0, column=1)

    label_quality = tk.Label(root, text="Quality (0-1)")
    label_quality.grid(row=1, column=0)

    global entry_quality
    entry_quality = tk.Entry(root)
    entry_quality.grid(row=1, column=1)

    calculate_button = tk.Button(root, text="Calculate", command=calculate_density)
    calculate_button.grid(row=2, columnspan=2)

    global result_label
    result_label = tk.Label(root, text="Result will appear here.")
    result_label.grid(row=3, columnspan=2)


def main():
    root = tk.Tk()
    setup_ui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
