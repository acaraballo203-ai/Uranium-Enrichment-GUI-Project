"""
graphs.py
---------
The graphs for the app, drawn with Matplotlib.

Tkinter has no built-in charts, so we use Matplotlib (the most common
Python plotting library) and "embed" its drawings inside the Tkinter
window. Install it once with:
    py -m pip install matplotlib

How embedding works, in three steps:
  1. Make a Matplotlib Figure (the blank sheet of paper).
  2. Wrap it in a FigureCanvasTkAgg, which turns the Figure into a
     Tkinter widget that can be placed with .grid() like any Label.
  3. Whenever the numbers change, clear the Figure, draw again, and
     call canvas.draw() so the window shows the new picture.

Like the *_calc.py files, nothing here does any physics. These functions
only take numbers that were already calculated and draw them.
"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# One color per thing, used the same way in every graph,
# so "electricity" is always blue, "enrichment" is always orange, etc.
ENRICHMENT_COLOR = "#eb6834"   # orange
ELECTRIC_COLOR = "#2a78d6"     # blue
THERMAL_COLOR = "#1baf7a"      # green-blue (aqua)
GRAY = "#b8b6ae"               # for "nothing useful": outages, waste heat
TEXT_GRAY = "#52514e"


def make_canvas(parent, width_inches, height_inches):
    """
    Make an empty Figure inside a Tkinter frame.

    Returns (figure, canvas).
      * figure is what we draw on
      * canvas.get_tk_widget() is the Tkinter widget you .grid() into place
    """
    # dpi = dots per inch, so 100 dpi * 4 inches = 400 pixels wide
    figure = Figure(figsize=(width_inches, height_inches), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=parent)
    return figure, canvas


def show_message(figure, canvas, message):
    """Wipe the figure and write a short message in the middle instead."""
    figure.clear()
    figure.text(0.5, 0.5, message, ha="center", va="center",
                color=TEXT_GRAY, wrap=True)
    canvas.draw()


def tidy_axes(ax):
    """Small style tweaks so the bar charts look clean."""
    ax.spines["top"].set_visible(False)      # hide the box's top line
    ax.spines["right"].set_visible(False)    # and its right line
    ax.yaxis.grid(True, color="#e1e0d9")     # light horizontal grid lines
    ax.set_axisbelow(True)                   # grid behind the bars
    # Write axis numbers as 1,000,000 instead of 1e6
    ax.ticklabel_format(axis="y", style="plain")
    ax.yaxis.set_major_formatter("{x:,.0f}")


# ---------------- Section 1: enrichment ----------------

def draw_enrichment_energy(figure, canvas, energy_mwh):
    """
    Graph 1: one bar showing the energy needed to enrich the uranium.
    energy_mwh is in MWh (the app turns the kWh result into MWh first,
    so it matches the units in section 2).
    """
    if energy_mwh <= 0:
        show_message(figure, canvas,
                     "Enter the kWh per SWU in the inputs\n"
                     "to see the enrichment energy.")
        return

    figure.clear()
    ax = figure.add_subplot()   # one set of axes filling the figure

    bars = ax.bar(["Enrichment"], [energy_mwh],
                  color=ENRICHMENT_COLOR, width=0.5)
    # bar_label writes each bar's value on top of it
    ax.bar_label(bars, labels=["{:,.1f} MWh".format(energy_mwh)], padding=3)

    ax.set_title("Energy to enrich the uranium")
    ax.set_ylabel("Energy (MWh)")
    ax.set_ylim(0, energy_mwh * 1.2)   # leave room above for the label
    tidy_axes(ax)

    figure.tight_layout()   # stop labels from being cut off at the edges
    canvas.draw()


# ---------------- Section 2: burnup ----------------

def draw_energy_comparison(ax, enrichment_mwh, electric_mwh, thermal_mwh):
    """
    Graph 2: bars comparing the energy put IN to enrich the fuel
    with the energy the reactor gets OUT of it.
    """
    names = ["Enrichment\n(energy in)", "Electricity\nmade", "Thermal\nenergy made"]
    values = [enrichment_mwh, electric_mwh, thermal_mwh]
    colors = [ENRICHMENT_COLOR, ELECTRIC_COLOR, THERMAL_COLOR]

    bars = ax.bar(names, values, color=colors, width=0.6)
    ax.bar_label(bars, labels=["{:,.0f}".format(v) for v in values],
                 padding=3, fontsize=8)

    # The enrichment bar is usually tiny next to the reactor bars,
    # so the title spells out how many times bigger the output is.
    if enrichment_mwh > 0:
        ratio = electric_mwh / enrichment_mwh
        ax.set_title("Electricity out is {:,.0f}x the enrichment energy in"
                     .format(ratio), fontsize=10)
    else:
        ax.set_title("Energy in vs energy out\n(enter kWh per SWU in section 1)",
                     fontsize=10)

    ax.set_ylabel("Energy (MWh)")
    ax.set_ylim(0, max(values) * 1.15)
    ax.tick_params(axis="x", labelsize=8)
    tidy_axes(ax)


def draw_pie(ax, values, names, colors, unit, title):
    """
    One pie chart. Each slice is labeled with its name, its amount and
    its percent, so you never have to guess from the color alone.
    """
    # Skip any slice that is 0 (for example no outages at 100 % capacity),
    # otherwise its label would sit on top of the other one.
    slices = [(v, n, c) for v, n, c in zip(values, names, colors) if v > 0]
    values = [v for v, n, c in slices]
    names = [n for v, n, c in slices]
    colors = [c for v, n, c in slices]

    total = sum(values)
    labels = []
    for name, value in zip(names, values):
        percent = 100 * value / total
        labels.append("{}\n{:,.0f} {} ({:.0f}%)".format(name, value, unit, percent))

    ax.pie(values, labels=labels, colors=colors, startangle=0,
           counterclock=False,
           # a thin white edge between the slices
           wedgeprops={"edgecolor": "white", "linewidth": 2},
           textprops={"fontsize": 8})
    ax.set_title(title, fontsize=10)


def draw_burnup_graphs(figure, canvas, enrichment_mwh, electric_mwh,
                       thermal_mwh, full_power_days, calendar_days,
                       max_electric_mwh):
    """
    Draw all four section 2 pictures side by side in one figure:
      1st: bar graph, enrichment energy vs reactor energy
      2nd: pie, full-power days vs outage days
      3rd: pie, thermal energy split into electricity vs waste heat
      4th: pie, electricity made vs electricity lost to outages

    Why two pies instead of one?  Days and MWh are different units,
    so they cannot be slices of the same pie.
    """
    if full_power_days <= 0:
        show_message(figure, canvas,
                     "Enter more than 0 full-power operating days to see the graphs.")
        return

    figure.clear()
    # 1 row, 4 columns.  The bar graph gets a bit more room than each pie.
    grid = figure.add_gridspec(1, 4, width_ratios=[1.3, 1, 1, 1])
    bar_ax = figure.add_subplot(grid[0, 0])
    days_ax = figure.add_subplot(grid[0, 1])
    heat_ax = figure.add_subplot(grid[0, 2])
    made_ax = figure.add_subplot(grid[0, 3])

    draw_energy_comparison(bar_ax, enrichment_mwh, electric_mwh, thermal_mwh)

    # Calendar days = full-power days + days the plant was down or at low power
    outage_days = calendar_days - full_power_days
    draw_pie(days_ax,
             values=[full_power_days, outage_days],
             names=["Full power", "Outages"],
             colors=[THERMAL_COLOR, GRAY],
             unit="days",
             title="{:,.0f} calendar days".format(calendar_days))

    # All the reactor's heat either becomes electricity or is waste heat
    waste_heat = thermal_mwh - electric_mwh
    draw_pie(heat_ax,
             values=[electric_mwh, waste_heat],
             names=["Electricity", "Waste heat"],
             colors=[ELECTRIC_COLOR, GRAY],
             unit="MWh",
             title="Where the {:,.0f} MWh\nof heat goes".format(thermal_mwh))

    # Electricity made vs the most it could have made in the calendar days.
    # max_electric_mwh is None until max_electricity_mwh() is written.
    if max_electric_mwh is None:
        made_ax.axis("off")   # hide the empty axes box
        made_ax.text(0.5, 0.5, "Made vs possible:\n(not built yet)",
                     ha="center", va="center", color=TEXT_GRAY,
                     transform=made_ax.transAxes)
    else:
        # Whatever wasn't made was lost while the plant was down
        lost = max_electric_mwh - electric_mwh
        draw_pie(made_ax,
                 values=[electric_mwh, lost],
                 names=["Made", "Lost to outages"],
                 colors=[ELECTRIC_COLOR, GRAY],
                 unit="MWh",
                 title="Electricity made vs\n{:,.0f} MWh possible".format(
                     max_electric_mwh))

    figure.tight_layout()
    canvas.draw()
