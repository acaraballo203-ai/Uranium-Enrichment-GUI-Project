# Uranium-Enrichment-GUI-Project

Create a Python Based GUI that allows users to input uranium enrichment info to calculate uranium needed, swu, energy required, and/or cost required. Additional features will include energy production and fuel life expency.

A beginner-friendly Python + Tkinter app. Type in how much enriched uranium
you want and at what enrichment, plus your own unit costs, and it calculates:

- feed (natural) uranium needed
- tails (depleted uranium) left over
- separative work (SWU)
- feed, conversion, enrichment and total cost

Costs are whatever you type in; the app does not look up market prices.

## Run it

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

## The formulas

Assays are in % U-235 (x = assay / 100 inside the formulas).

- Feed: `F = P * (xp - xt) / (xf - xt)`
- Tails: `T = F - P`
- Value function: `V(x) = (2x - 1) * ln(x / (1 - x))`
- SWU: `SWU = P*V(xp) + T*V(xt) - F*V(xf)`
- Total cost: `F * (feed $/kgU + conversion $/kgU) + SWU * ($/SWU)`

## Coming later

Energy production and fuel life expectancy.
