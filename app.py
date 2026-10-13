"""
app.py
------
The Tkinter window for the uranium enrichment calculator.

Run it with:
    py app.py

This file only builds the window and reads/writes the boxes.
All of the actual math is in enrichment_calc.py (section 1)
and burnup_calc.py (section 2).
"""

import tkinter as tk
from tkinter import ttk, messagebox

import enrichment_calc as calc
import burnup_calc as burn


# Each input row: (label text, default value).
# The order here is the order they appear in the window.
INPUT_FIELDS = [
    ("Product mass (kgU)", "1000"),
    ("Product assay (% U-235)", "4.95"),
    ("Feed assay (% U-235)", "0.711"),
    ("Tails assay (% U-235)", "0.25"),
    ("Energy to run 1 kg SWU of enrichment process (kWh)", "0"),
    ("Feed cost ($/kgU [U_3O_8])", "0"),
    ("SWU cost ($/SWU)", "0"),
    ("Conversion cost ($/kgU [UF_6])", "0"),
]

# Each output row: (label text, key in the results dictionary, unit/format).
OUTPUT_FIELDS = [
    ("Feed uranium needed", "feed_mass", "kgU"),
    ("Tails (depleted U)", "tails_mass", "kgU"),
    ("Separative work", "swu", "SWU"),
    ("Energy of Separative work Required", "energy_required", "kWh"),
    ("Feed cost", "feed_cost", "$"),
    ("Conversion cost", "conversion_cost", "$"),
    ("Enrichment (SWU) cost", "enrichment_cost", "$"),
    ("TOTAL COST", "total_cost", "$"),
]


# ---------- Section 2: energy from the fuel (burnup) ----------

# Each burnup input row: (label text, key in a PRESETS entry).
# "days" is not part of a preset, so its key is None.
BURNUP_INPUT_FIELDS = [
    ("Specific power (kW/kgHM)", "specific_power"),
    ("Thermal-to-electric efficiency (%)", "efficiency"),
    ("Max (discharge) burnup (GWd/tHM)", "max_burnup"),
    ("Capacity factor (%)", "capacity_factor"),
    ("Full-power operating days", None),
]

# Each burnup output row: (label text, key in the results dictionary, unit).
BURNUP_OUTPUT_FIELDS = [
    ("Thermal power of this fuel", "thermal_power", "MWt"),
    ("Electric power of this fuel", "electric_power", "MWe"),
    ("Burnup reached", "burnup", "GWd/tHM"),
    ("Thermal energy made", "thermal_energy", "MWh"),
    ("Electricity made", "electric_energy", "MWh"),
    ("Fuel life at max burnup", "fuel_life", "full-power days"),
    ("Fuel life (calendar)", "fuel_life_years", "years"),
]


class EnrichmentApp:
    def __init__(self, root):
        self.root = root
        root.title("Uranium Enrichment Calculator")
        root.resizable(False, False)

        # A frame with some padding holds everything else.
        main = ttk.Frame(root, padding=15)
        main.grid(row=0, column=0)

        # ---------- Inputs ----------
        inputs_box = ttk.LabelFrame(main, text="Inputs", padding=10)
        inputs_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # We keep every Entry box in a dictionary so we can read it later.
        self.entries = {}
        for row, (label_text, default) in enumerate(INPUT_FIELDS):
            ttk.Label(inputs_box, text=label_text).grid(
                row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(inputs_box, width=12, justify="right")
            entry.insert(0, default)  # put the default value in the box
            entry.grid(row=row, column=1, pady=3, padx=(10, 0))
            self.entries[label_text] = entry

        # ---------- Buttons ----------
        buttons = ttk.Frame(inputs_box)
        buttons.grid(row=len(INPUT_FIELDS), column=0, columnspan=2, pady=(10, 0))
        ttk.Button(buttons, text="Calculate", command=self.calculate).grid(
            row=0, column=0, padx=5)
        ttk.Button(buttons, text="Clear results", command=self.clear).grid(
            row=0, column=1, padx=5)

        # Pressing Enter anywhere also runs the calculation.
        root.bind("<Return>", lambda event: self.calculate())

        # ---------- Results ----------
        results_box = ttk.LabelFrame(main, text="Results", padding=10)
        results_box.grid(row=0, column=1, sticky="nsew")

        # A StringVar is a Tkinter variable: when we change it,
        # the Label showing it updates automatically.
        self.result_vars = {}
        for row, (label_text, key, unit) in enumerate(OUTPUT_FIELDS):
            ttk.Label(results_box, text=label_text).grid(
                row=row, column=0, sticky="w", pady=3)
            var = tk.StringVar(value="-")
            ttk.Label(results_box, textvariable=var, width=18, anchor="e").grid(
                row=row, column=1, pady=3, padx=(10, 0))
            self.result_vars[key] = var

        # ---------- Section 2: Energy from fuel (burnup) ----------
        self.build_burnup_section(main)

    def build_burnup_section(self, main):
        """
        Build the second section underneath the first one.
        It has its own Calculate button, so it never changes section 1.
        """
        # row=1 puts it under section 1; columnspan=2 makes it full width.
        burnup_box = ttk.LabelFrame(
            main, text="Energy from this fuel (burnup)", padding=10)
        burnup_box.grid(row=1, column=0, columnspan=2,
                        sticky="nsew", pady=(15, 0))

        # Left side: inputs.  Right side: results.
        inputs = ttk.Frame(burnup_box)
        inputs.grid(row=0, column=0, sticky="nw", padx=(0, 20))
        results = ttk.Frame(burnup_box)
        results.grid(row=0, column=1, sticky="nw")

        # --- Reactor type dropdown ---
        # A Combobox is Tkinter's drop-down list.
        # state="readonly" means you can pick from the list but not type in it.
        ttk.Label(inputs, text="Reactor type").grid(
            row=0, column=0, sticky="w", pady=3)
        self.reactor_choice = ttk.Combobox(
            inputs, values=list(burn.PRESETS.keys()),
            state="readonly", width=24)
        self.reactor_choice.grid(row=0, column=1, pady=3, padx=(10, 0))
        # When the user picks something, run self.apply_preset
        self.reactor_choice.bind("<<ComboboxSelected>>",
                                 lambda event: self.apply_preset())

        # --- Number boxes ---
        self.burnup_entries = {}
        for row, (label_text, preset_key) in enumerate(BURNUP_INPUT_FIELDS, start=1):
            ttk.Label(inputs, text=label_text).grid(
                row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(inputs, width=12, justify="right")
            entry.grid(row=row, column=1, pady=3, padx=(10, 0), sticky="e")
            self.burnup_entries[label_text] = entry
        self.burnup_entries["Full-power operating days"].insert(0, "365")

        # A small reminder of where the fuel mass comes from.
        ttk.Label(inputs, text="Fuel mass = Product mass from section 1",
                  foreground="gray").grid(
            row=len(BURNUP_INPUT_FIELDS) + 1, column=0, columnspan=2,
            sticky="w", pady=(6, 0))

        # --- Buttons ---
        buttons = ttk.Frame(inputs)
        buttons.grid(row=len(BURNUP_INPUT_FIELDS) + 2, column=0,
                     columnspan=2, pady=(10, 0))
        ttk.Button(buttons, text="Calculate energy",
                   command=self.calculate_burnup).grid(row=0, column=0, padx=5)
        ttk.Button(buttons, text="Clear results",
                   command=self.clear_burnup).grid(row=0, column=1, padx=5)

        # --- Results ---
        self.burnup_vars = {}
        for row, (label_text, key, unit) in enumerate(BURNUP_OUTPUT_FIELDS):
            ttk.Label(results, text=label_text).grid(
                row=row, column=0, sticky="w", pady=3)
            var = tk.StringVar(value="-")
            ttk.Label(results, textvariable=var, width=26, anchor="e").grid(
                row=row, column=1, pady=3, padx=(10, 0))
            self.burnup_vars[key] = var

        # A warning line that only shows text when burnup is too high.
        self.burnup_warning = tk.StringVar(value="")
        ttk.Label(results, textvariable=self.burnup_warning,
                  foreground="red", wraplength=300).grid(
            row=len(BURNUP_OUTPUT_FIELDS), column=0, columnspan=2,
            sticky="w", pady=(6, 0))

        # Start with the PWR preset picked and its numbers filled in.
        self.reactor_choice.current(0)
        self.apply_preset()

    def apply_preset(self):
        """Fill the boxes with the numbers for the chosen reactor type."""
        preset = burn.PRESETS[self.reactor_choice.get()]

        for label_text, preset_key in BURNUP_INPUT_FIELDS:
            if preset_key is None:
                continue  # operating days are always up to the user
            entry = self.burnup_entries[label_text]
            if preset is None:
                # "Custom": unlock the box and leave the old number to edit
                entry.state(["!readonly"])
            else:
                # A real preset: put its number in and lock the box
                entry.state(["!readonly"])     # must unlock before changing it
                entry.delete(0, tk.END)
                entry.insert(0, str(preset[preset_key]))
                entry.state(["readonly"])

    def read_burnup_number(self, label_text):
        """Same as read_number, but for the section 2 boxes."""
        text = self.burnup_entries[label_text].get().strip().replace(",", "")
        try:
            return float(text)
        except ValueError:
            raise ValueError('"' + label_text + '" must be a number.')

    def calculate_burnup(self):
        """Called when the section 2 Calculate energy button is pressed."""
        try:
            results = burn.calculate_all(
                # Fuel mass comes straight from section 1's Product mass box.
                fuel_mass_kg=self.read_number("Product mass (kgU)"),
                specific_power=self.read_burnup_number("Specific power (kW/kgHM)"),
                efficiency_percent=self.read_burnup_number("Thermal-to-electric efficiency (%)"),
                days=self.read_burnup_number("Full-power operating days"),
                max_burnup_gwd_per_t=self.read_burnup_number("Max (discharge) burnup (GWd/tHM)"),
                capacity_factor_percent=self.read_burnup_number("Capacity factor (%)"),
            )
        except ValueError as error:
            messagebox.showerror("Check your inputs", str(error))
            return

        for label_text, key, unit in BURNUP_OUTPUT_FIELDS:
            value = results[key]
            if value is None:
                # fuel_life_years() returns None until you write it
                self.burnup_vars[key].set("(not built yet)")
            else:
                self.burnup_vars[key].set("{:,.2f} {}".format(value, unit))

        if results["over_max_burnup"]:
            self.burnup_warning.set(
                "Warning: this is past the max burnup for this fuel. "
                "Real fuel would have been taken out before this.")
        else:
            self.burnup_warning.set("")

    def clear_burnup(self):
        """Reset every section 2 result back to a dash."""
        for var in self.burnup_vars.values():
            var.set("-")
        self.burnup_warning.set("")

    def read_number(self, label_text):
        """Read one input box and turn its text into a number."""
        text = self.entries[label_text].get().strip().replace(",", "")
        try:
            return float(text)
        except ValueError:
            raise ValueError('"' + label_text + '" must be a number.')

    def calculate(self):
        """Called when the Calculate button is pressed."""
        try:
            results = calc.calculate_all(
                product_mass=self.read_number("Product mass (kgU)"),
                product_assay=self.read_number("Product assay (% U-235)"),
                feed_assay=self.read_number("Feed assay (% U-235)"),
                tails_assay=self.read_number("Tails assay (% U-235)"),
                energy_required=self.read_number("Energy to run 1 kg SWU of enrichment process (kWh)"),
                feed_cost_per_kg=self.read_number("Feed cost ($/kgU [U_3O_8])"),
                swu_cost=self.read_number("SWU cost ($/SWU)"),
                conversion_cost_per_kg=self.read_number("Conversion cost ($/kgU [UF_6])"),
            )
        except ValueError as error:
            # Show the problem in a pop-up instead of crashing.
            messagebox.showerror("Check your inputs", str(error))
            return

        # Put each result in its label, formatted nicely.
        for label_text, key, unit in OUTPUT_FIELDS:
            value = results[key]
            if unit == "$":
                self.result_vars[key].set("${:,.2f}".format(value))
            else:
                self.result_vars[key].set("{:,.2f} {}".format(value, unit))

    def clear(self):
        """Reset every result back to a dash."""
        for var in self.result_vars.values():
            var.set("-")


# This block only runs when you start this file directly (py app.py).
if __name__ == "__main__":
    root = tk.Tk()
    EnrichmentApp(root)
    root.mainloop()
