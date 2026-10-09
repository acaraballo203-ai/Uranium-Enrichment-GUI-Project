"""
enrichment_calc.py
------------------
All of the math for the uranium enrichment calculator lives here.

Keeping the math separate from the GUI (app.py) means:
  * we can test the math on its own (see test_enrichment_calc.py)
  * the GUI code stays short and only worries about buttons and boxes

Assays (enrichment levels) are written as PERCENT U-235 in this file,
for example 4.95 for 4.95 % enriched fuel and 0.711 for natural uranium.
"""

import math


def value_function(assay_percent):
    """
    The "value function" V(x) used in the standard SWU formula.

        V(x) = (2x - 1) * ln( x / (1 - x) )

    x is the assay as a FRACTION (0.04 instead of 4 %), so we convert first.
    """
    x = assay_percent / 100.0
    return (2 * x - 1) * math.log(x / (1 - x))


def check_assays(product_assay, feed_assay, tails_assay):
    """
    Make sure the three assays make physical sense.
    Raises ValueError with a friendly message if something is wrong.
    """
    for name, value in [("Product", product_assay),
                        ("Feed", feed_assay),
                        ("Tails", tails_assay)]:
        if not (0 < value < 100):
            raise ValueError(name + " assay must be between 0 and 100 %.")

    # Enrichment only works if: tails < feed < product
    if not (tails_assay < feed_assay < product_assay):
        raise ValueError("Assays must satisfy: tails < feed < product.")


def feed_needed(product_mass, product_assay, feed_assay, tails_assay):
    """
    Mass of feed (natural) uranium needed, in the same units as product_mass.

    Comes from a U-235 mass balance:
        F = P * (xp - xt) / (xf - xt)
    """
    check_assays(product_assay, feed_assay, tails_assay)
    return product_mass * (product_assay - tails_assay) / (feed_assay - tails_assay)


def tails_mass(product_mass, product_assay, feed_assay, tails_assay):
    """Mass of depleted uranium (tails) left over: T = F - P."""
    return feed_needed(product_mass, product_assay, feed_assay, tails_assay) - product_mass


def swu_needed(product_mass, product_assay, feed_assay, tails_assay):
    """
    Separative Work Units (SWU) needed, using the standard formula:

        SWU = P*V(xp) + T*V(xt) - F*V(xf)

    If product_mass is in kgU, the answer is in kg-SWU (usually just called SWU).
    """
    feed = feed_needed(product_mass, product_assay, feed_assay, tails_assay)
    tails = feed - product_mass
    return (product_mass * value_function(product_assay)
            + tails * value_function(tails_assay)
            - feed * value_function(feed_assay))


def calculate_all(product_mass, product_assay, feed_assay, tails_assay, energy_required,
                  feed_cost_per_kg, swu_cost, conversion_cost_per_kg):
    """
    Run every calculation at once and return the results in a dictionary.

    Costs are whatever the user types in (not market prices):
      feed_cost_per_kg        - $ per kg of natural uranium (U3O8) feed
      swu_cost                - $ per SWU
      conversion_cost_per_kg  - $ per kg of feed converted (to UF6)
    """
    if product_mass <= 0:
        raise ValueError("Product mass must be greater than 0.")
    for cost in (feed_cost_per_kg, swu_cost, conversion_cost_per_kg):
        if cost < 0:
            raise ValueError("Costs cannot be negative.")

    if energy_required < 0:
        raise ValueError("Energy of enrichment process cannot be negative.")

    feed = feed_needed(product_mass, product_assay, feed_assay, tails_assay)
    swu = swu_needed(product_mass, product_assay, feed_assay, tails_assay)

    energy_enrichment = swu * energy_required
    feed_cost = feed * feed_cost_per_kg
    conversion_cost = feed * conversion_cost_per_kg
    enrichment_cost = swu * swu_cost

    return {
        "feed_mass": feed,
        "tails_mass": feed - product_mass,
        "swu": swu,
        "energy_required": energy_enrichment,
        "feed_cost": feed_cost,
        "conversion_cost": conversion_cost,
        "enrichment_cost": enrichment_cost,
        "total_cost": feed_cost + conversion_cost + enrichment_cost,
    }
