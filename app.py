"""
app.py
------
The Tkinter window for the uranium enrichment calculator.

Run it with:
    py app.py

This file only builds the window and reads/writes the boxes.
All of the actual math is in enrichment_calc.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import enrichment_calc as calc


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
