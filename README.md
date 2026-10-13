# Uranium-Enrichment-GUI-Project

Create a Python Based GUI that allows users to input uranium enrichment info to calculate uranium needed, swu, energy required, and/or cost required. Additional features will include energy production and fuel life expency.

A beginner-friendly Python + Tkinter app. Type in how much enriched uranium
you want and at what enrichment, plus your own unit costs, and it calculates:

- feed (natural) uranium needed
- tails (depleted uranium) left over
- separative work (SWU)
- feed, conversion, enrichment and total cost

A second section underneath (with its own button) works out how much energy
that enriched uranium makes in a reactor, using **burnup**:

- pick a reactor type (PWR, BWR, molten salt, or custom)
- thermal and electric power, burnup reached, thermal and electric energy
- fuel life at max burnup, in full-power days and calendar years

Both sections also draw graphs (made with Matplotlib, embedded in the window):

- section 1: a bar graph of the energy needed to enrich the uranium
- section 2: a bar graph of enrichment energy (in) vs electricity and heat
  made (out), a pie of full-power days vs outage days, and a pie of how the
  reactor's heat splits into electricity and waste heat

Costs are whatever you type in; the app does not look up market prices.

## Run it

Install Matplotlib once (Tkinter comes with Python, Matplotlib does not):

```
py -m pip install -r requirements.txt
```

Then start the app:

```
py app.py
```

## Run the tests

```
py -m unittest
```

## Files

| File | What it does |
| --- | --- |
| `app.py` | The window: input boxes, buttons, result labels |
| `enrichment_calc.py` | All of the math (feed, SWU, cost) |
| `test_enrichment_calc.py` | Simple checks that the math is right |
| `burnup_calc.py` | The energy / burnup math and reactor presets |
| `test_burnup_calc.py` | Simple checks for the burnup math |
| `graphs.py` | Draws the graphs with Matplotlib |
| `requirements.txt` | Extra library to install (Matplotlib) |

## The formulas

Assays are in % U-235 (x = assay / 100 inside the formulas).

- Feed: `F = P * (xp - xt) / (xf - xt)`
- Tails: `T = F - P`
- Value function: `V(x) = (2x - 1) * ln(x / (1 - x))`
- SWU: `SWU = P*V(xp) + T*V(xt) - F*V(xf)`
- Total cost: `F * (feed $/kgU + conversion $/kgU) + SWU * ($/SWU)`

### Burnup (section 2)

Fuel mass M is the product mass from section 1 (kgU = kgHM for uranium fuel).

- Thermal power: `P_th (MW) = specific power (kW/kgHM) * M (t)`
- Burnup: `B (MWd/tHM) = specific power * days`
- Thermal energy: `E_th (MWh) = B * M (t) * 24`
- Electric energy: `E_e = E_th * efficiency`
- Fuel life: `days = max burnup (GWd/t) * 1000 / specific power`
- Fuel life in years: `years = days / capacity factor / 365.25`
- Calendar days (pie chart): `calendar days = full-power days / capacity factor`

Preset values are typical ballpark numbers, not data for one specific plant.

## Coming later

Ideas welcome!
