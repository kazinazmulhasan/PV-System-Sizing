"""Stand-alone PV system sizing for a household at Debidwar, Cumilla (23.6004 N, 90.9881 E)."""
import csv
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# Design assumptions
ETA_CABLE, ETA_REG, ETA_BAT, ETA_INV = 0.95, 0.95, 0.80, 0.95
V_DC = 48            # system voltage (V)
V_MODULE = 12        # module voltage (V)
P_MODULE = 50        # module rating (Wp)
A_MODULE = 0.4       # module area (m^2)
AUTONOMY_DAYS = 5
DEPTH_OF_DISCHARGE = 0.7
ETA_TOTAL_ROUNDED = 0.69  # product of the four efficiencies, rounded as in the report


def read_csv(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def main():
    loads = read_csv("loads.csv")
    daily_kwh = sum(int(r["amount"]) * float(r["power_w"]) * float(r["hours_per_day"]) for r in loads) / 1000

    irr = read_csv("irradiation.csv")
    worst = min(irr, key=lambda r: float(r["daily_kwh_m2"]))
    psh = float(worst["daily_kwh_m2"])

    p_pv = daily_kwh / ETA_TOTAL_ROUNDED          # kWh/day
    p_peak = round(p_pv / psh, 2)                 # kWp (rounded as in the report)
    n_series = V_DC // V_MODULE
    n_parallel_min = math.ceil(p_peak * 1000 / (P_MODULE * n_series))
    n_parallel = round(n_parallel_min, -1)        # design choice in the report: 69 -> 70 strings (small margin)
    n_modules = n_series * n_parallel
    area = n_modules * A_MODULE

    c_batt = AUTONOMY_DAYS * daily_kwh * 1000 * ETA_CABLE / (V_DC * DEPTH_OF_DISCHARGE)

    i_in = p_peak * 1000 / V_DC
    p_out = 950 + 180 + 400 + 900 + 1000 + 276 + 2200   # W, dishwasher and washing machine not simultaneous
    i_out = p_out / V_DC

    print(f"Daily load             : {daily_kwh:.2f} kWh/day")
    print(f"Worst month            : {worst['month']} (PSH = {psh:.2f} h/day)")
    print(f"Required PV energy     : {p_pv:.2f} kWh/day")
    print(f"Installed peak power   : {p_peak:.2f} kWp")
    print(f"Modules in series      : {n_series}")
    print(f"Strings in parallel    : {n_parallel}")
    print(f"Total modules          : {n_modules}")
    print(f"Required area          : {area:.0f} m^2")
    print(f"Battery capacity       : {c_batt:.0f} Ah @ {V_DC} V")
    print(f"Regulator input current: {i_in:.2f} A")
    print(f"Inverter output power  : {p_out/1000:.3f} kW ({i_out:.0f} A)")


if __name__ == "__main__":
    main()
