"""
Simple tests for burnup_calc.py.

Run them from this folder with:
    py -m unittest
"""

import unittest

import burnup_calc as burn


class TestBurnupCalc(unittest.TestCase):

    def test_burnup_is_power_times_days(self):
        # 38 kW/kg for 1000 days = 38,000 MWd/t
        self.assertAlmostEqual(burn.burnup_mwd_per_t(38, 1000), 38000)

    def test_energy_for_one_ton(self):
        # 1000 kg (1 t) at 40 kW/kg for 100 days at 33 % efficiency
        results = burn.calculate_all(1000, 40, 33, 100, 50)
        self.assertAlmostEqual(results["thermal_power"], 40)    # MW thermal
        self.assertAlmostEqual(results["burnup"], 4)            # GWd/t
        # 40 MW * 100 days * 24 h = 96,000 MWh thermal
        self.assertAlmostEqual(results["thermal_energy"], 96000)
        self.assertAlmostEqual(results["electric_energy"], 96000 * 0.33)

    def test_over_max_burnup_flag(self):
        # 40 kW/kg for 2000 days = 80 GWd/t, more than the 50 GWd/t max
        results = burn.calculate_all(1000, 40, 33, 2000, 50)
        self.assertTrue(results["over_max_burnup"])

    def test_bad_efficiency_raises(self):
        with self.assertRaises(ValueError):
            burn.calculate_all(1000, 40, 150, 100, 50)

    def test_every_preset_has_numbers(self):
        for name, preset in burn.PRESETS.items():
            if preset is None:  # "Custom" has no numbers on purpose
                continue
            for key in ("specific_power", "efficiency", "max_burnup",
                        "capacity_factor"):
                self.assertGreater(preset[key], 0, name + " " + key)

    # Un-comment this test once you write fuel_life_days()!
    def test_fuel_life_days(self):
        days = burn.fuel_life_days(50, 38)
        self.assertAlmostEqual(days, 1315.79, places=2)

    # Un-comment this test once you write fuel_life_years()!
    def test_fuel_life_years(self):
        years = burn.fuel_life_years(1315.79, 90)
        self.assertAlmostEqual(years, 4.00, places=2)

    def test_calendar_days(self):
        # 365 full-power days at 90 % takes 365 / 0.9 = 405.56 calendar days
        self.assertAlmostEqual(burn.calendar_days(365, 90), 405.56, places=2)

    # Un-comment this test once you write max_electricity_mwh()!
    def test_max_electricity(self):
       mwh = burn.max_electricity_mwh(12.54, 405.56)
       self.assertAlmostEqual(mwh, 122057.3, places=1)


if __name__ == "__main__":
    unittest.main()
