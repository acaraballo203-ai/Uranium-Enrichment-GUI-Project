"""
burnup_calc.py
--------------
The math for the "Energy from fuel (burnup)" section of the app.

Like enrichment_calc.py, this file has no GUI code in it, so we can
test it on its own (see test_burnup_calc.py).

Key idea: SPECIFIC POWER
    Specific power = reactor thermal power / mass of heavy metal in the core
    Units: kW per kg of heavy metal (kW/kgHM), which is the same number
    as MW per ton of heavy metal (MW/tHM).

    It tells you how hard each kilogram of fuel is being "worked".
    Multiply it by the number of days and you get burnup:

        burnup (MWd/tHM) = specific power (MW/tHM) * days

For uranium fuel, kgU and kgHM are the same thing (uranium IS the heavy
metal), so the product mass from section 1 can be used directly.
"""


# Preset reactor settings for the dropdown.
# These are TYPICAL starting values, not exact numbers for any one plant.
# The user can always change them (just like the cost inputs).
#   specific_power  - kW/kgHM (= MW/tHM)
#   efficiency      - % of thermal energy turned into electricity
#   max_burnup      - typical discharge burnup in GWd/tHM
#   capacity_factor - % of the time the plant runs at full power
#                     (outages and maintenance make it less than 100 %)
PRESETS = {
    "PWR (pressurized water)": {
        "specific_power": 38.0,
        "efficiency": 33.0,
        "max_burnup": 50.0,
        "capacity_factor": 90.0,
    },
    "BWR (boiling water)": {
        "specific_power": 25.0,
        "efficiency": 34.0,
        "max_burnup": 50.0,
        "capacity_factor": 90.0,
    },
    "Molten salt": {
        "specific_power": 30.0,
        "efficiency": 44.0,
        "max_burnup": 100.0,
        "capacity_factor": 85.0,
    },
    "Custom": None,  # None means "leave the boxes for the user to fill in"
}


def burnup_mwd_per_t(specific_power, days):
    """
    Burnup in MWd/tHM (megawatt-days per ton of heavy metal).

    specific_power is in kW/kgHM, which is the same as MW/tHM,
    so we can just multiply by days.
    """
    return specific_power * days


def fuel_life_days(max_burnup_gwd_per_t, specific_power):
    """
    How many full-power days the fuel can run before it reaches
    its maximum (discharge) burnup.

    Check your answer: PWR preset (50 GWd/t, 38 kW/kg) should give
    about 1,316 days, which is roughly 3.6 years.
    """
    if specific_power <= 0:
        raise ValueError("Specific Power must be greater than 0.")
    else: 
        days = (max_burnup_gwd_per_t * 1000) / specific_power

    return days


def fuel_life_years(full_power_days, capacity_factor_percent):
    """
    Turn full-power days into real calendar YEARS.

    A plant is not at full power every day (refueling outages,
    maintenance), so the fuel takes longer on the calendar than
    the full-power days suggest.


    Check your answer: 1,315.79 full-power days at 90 % should give
    about 4.00 years.
    """

    if capacity_factor_percent <= 0:
        raise ValueError("Capacity factor must be greater than 0.")

    capacity_factor_percentage = capacity_factor_percent / 100.0

    calendar_years = (full_power_days) / (capacity_factor_percentage * 365.25) 

    return calendar_years


def calendar_days(full_power_days, capacity_factor_percent):
    """
    How many real calendar days it takes to run a number of
    full-power days (same idea as fuel_life_years, but in days).

    Example: 365 full-power days at 90 % takes 365 / 0.90 = 405.6 days.
    """
    if capacity_factor_percent <= 0:
        raise ValueError("Capacity factor must be greater than 0.")
    return full_power_days / (capacity_factor_percent / 100.0)


def max_electricity_mwh(electric_power_mw, calendar_days):
    """
    The MOST electricity the fuel could have made if the plant ran at
    full power on every single calendar day (no outages at all).
    The pie chart compares this with the electricity really made.

    YOUR TURN!  Right now this returns None, and the pie chart shows
    "(not built yet)".

    Hints:
      * energy = power * time
      * electric_power_mw is in MW, calendar_days is in days,
        and we want the answer in MWh
      * how many hours are in one day?

    Check your answer: 12.54 MWe for 405.56 calendar days should give
    about 122,057 MWh.
    """

    max_elec_generated = electric_power_mw * calendar_days * 24

    return max_elec_generated


def calculate_all(fuel_mass_kg, specific_power, efficiency_percent, days,
                  max_burnup_gwd_per_t, capacity_factor_percent=90.0):
    """
    Run every burnup calculation and return the results in a dictionary.

    fuel_mass_kg         - kg of heavy metal (the product mass from section 1)
    specific_power       - kW/kgHM
    efficiency_percent   - thermal-to-electric efficiency, in %
    days                 - full-power operating days
    max_burnup_gwd_per_t - typical discharge burnup, GWd/tHM
    capacity_factor_percent - % of the time at full power (default 90)
    """
    # ---- check the inputs make sense ----
    if fuel_mass_kg <= 0:
        raise ValueError("Product mass (section 1) must be greater than 0.")
    if specific_power <= 0:
        raise ValueError("Specific power must be greater than 0.")
    if not (0 < efficiency_percent <= 100):
        raise ValueError("Efficiency must be between 0 and 100 %.")
    if days < 0:
        raise ValueError("Operating days cannot be negative.")
    if max_burnup_gwd_per_t <= 0:
        raise ValueError("Max burnup must be greater than 0.")
    if not (0 < capacity_factor_percent <= 100):
        raise ValueError("Capacity factor must be between 0 and 100 %.")

    fuel_mass_t = fuel_mass_kg / 1000.0          # kg -> metric tons
    efficiency = efficiency_percent / 100.0      # 33 % -> 0.33

    # Thermal power of this much fuel: MW/t * t = MW (thermal)
    thermal_power_mw = specific_power * fuel_mass_t

    # Burnup reached after this many days
    burnup_mwd = burnup_mwd_per_t(specific_power, days)
    burnup_gwd = burnup_mwd / 1000.0

    # Total energy. MWd * 24 hours = MWh
    thermal_energy_mwh = burnup_mwd * fuel_mass_t * 24
    electric_energy_mwh = thermal_energy_mwh * efficiency

    # Fuel life, first in full-power days, then in calendar years
    life_days = fuel_life_days(max_burnup_gwd_per_t, specific_power)

    return {
        "thermal_power": thermal_power_mw,
        "electric_power": thermal_power_mw * efficiency,
        "burnup": burnup_gwd,
        "thermal_energy": thermal_energy_mwh,
        "electric_energy": electric_energy_mwh,
        "fuel_life": life_days,
        "fuel_life_years": fuel_life_years(life_days, capacity_factor_percent),
        # Calendar days needed for the operating days the user typed in
        # (used by the pie chart)
        "calendar_days": calendar_days(days, capacity_factor_percent),
        # Electricity it could have made running every calendar day
        # (used by the "made vs possible" pie chart)
        "max_electricity": max_electricity_mwh(
            thermal_power_mw * efficiency,
            calendar_days(days, capacity_factor_percent)),
        # True if the user ran the fuel longer than it is meant to last
        "over_max_burnup": burnup_gwd > max_burnup_gwd_per_t,
    }
