"""Calls-only replication of continuous piecewise-linear terminal payouts."""

from fractions import Fraction

import numpy as np
import pandas as pd


def parse_fractional_number(value, label="Entry"):
    """Safely parse an integer, decimal, or simple fraction such as -60/55."""
    text = str(value).strip().replace(" ", "")
    if not text:
        raise ValueError(f"{label} is blank. Enter zero if the position is unused.")
    try:
        result = float(Fraction(text))
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"{label} must be a number or fraction such as 1.25, 60/55, or -60/55.") from None
    if not np.isfinite(result):
        raise ValueError(f"{label} must be finite.")
    return result


def replication_matches(maximum_dollar_error, tolerance=0.01):
    """Accept a replication when every tested payoff is within the stated dollar tolerance."""
    return abs(float(maximum_dollar_error)) <= float(tolerance) + 1e-12


def calls_only_replication(nodes, target_values):
    x, y = np.asarray(nodes, dtype=float), np.asarray(target_values, dtype=float)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Nodes and target values must have equal length and at least two points.")
    if abs(x[0]) > 1e-12 or np.any(np.diff(x) <= 0):
        raise ValueError("Nodes must start at zero and increase strictly.")
    slopes = np.diff(y) / np.diff(x)
    calls = [
        {"kind": "call", "strike": float(x[i]), "quantity": float(slopes[i] - slopes[i - 1])}
        for i in range(1, len(x) - 1)
    ]
    return {"bond_payoff": float(y[0]), "stock_quantity": float(slopes[0]),
            "call_positions": calls, "segment_slopes": slopes}


def piecewise_target(nodes, values, terminal_prices):
    x, y, s = np.asarray(nodes, dtype=float), np.asarray(values, dtype=float), np.asarray(terminal_prices, dtype=float)
    result = np.interp(s, x, y)
    left_slope = (y[1] - y[0]) / (x[1] - x[0])
    right_slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
    result = np.where(s < x[0], y[0] + left_slope * (s - x[0]), result)
    return np.where(s > x[-1], y[-1] + right_slope * (s - x[-1]), result)


def replication_formula(replication):
    terms = []
    bond, stock = float(replication["bond_payoff"]), float(replication["stock_quantity"])
    if abs(bond) > 1e-10:
        terms.append(f"{bond:.4g}")
    if abs(stock) > 1e-10:
        terms.append(f"{stock:.4g} S_T")
    for pos in replication["call_positions"]:
        qty = float(pos["quantity"])
        if abs(qty) > 1e-10:
            terms.append(f"{'+' if qty >= 0 else '-'} {abs(qty):.4g}(S_T - {float(pos['strike']):g})^+")
    return " ".join(terms) if terms else "0"


def replication_positions_table(replication):
    rows = [
        {"Instrument": "Riskless payoff at T", "Quantity": replication["bond_payoff"]},
        {"Instrument": "Stock", "Quantity": replication["stock_quantity"]},
    ]
    rows.extend({"Instrument": f"Call, K = {float(pos['strike']):g}", "Quantity": float(pos["quantity"])}
                for pos in replication["call_positions"])
    return pd.DataFrame(rows)
