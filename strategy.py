"""Portfolio cost, terminal payoff, and profit calculations."""

from math import exp

import numpy as np
import pandas as pd


def active_option_positions(position_table):
    active = []
    for _, row in position_table.iterrows():
        strike = float(row["Strike"])
        for column, kind in (("Calls", "call"), ("Puts", "put")):
            quantity = float(row[column])
            if abs(quantity) > 1e-12:
                active.append({"kind": kind, "strike": strike, "quantity": quantity})
    return active


def component_costs(spot, rate, maturity, stock_quantity, bond_payoff, positions, prices, multiplier=1.0):
    rows = []
    if abs(stock_quantity) > 1e-12:
        rows.append({"Component": "Stock", "Quantity": stock_quantity, "Unit price": spot,
                     "Signed cost": stock_quantity * spot})
    if abs(bond_payoff) > 1e-12:
        bond_price = exp(-rate * maturity)
        rows.append({"Component": "Riskless payoff at T", "Quantity": bond_payoff,
                     "Unit price": bond_price, "Signed cost": bond_payoff * bond_price})
    for pos in positions:
        kind, strike, quantity = str(pos["kind"]), float(pos["strike"]), float(pos["quantity"])
        unit_price = prices[strike][kind]
        rows.append({"Component": f"{strike:g} {kind}", "Quantity": quantity,
                     "Unit price": unit_price, "Signed cost": quantity * multiplier * unit_price})
    if not rows:
        rows.append({"Component": "No positions", "Quantity": 0.0, "Unit price": 0.0, "Signed cost": 0.0})
    return pd.DataFrame(rows)


def strategy_scenarios(terminal_prices, stock_quantity, bond_payoff, positions, net_initial_cost,
                       multiplier=1.0, financed_cost=None):
    terminal_prices = np.asarray(terminal_prices, dtype=float)
    data = {"Stock price at expiration": terminal_prices}
    total = np.zeros_like(terminal_prices)
    if abs(stock_quantity) > 1e-12:
        values = stock_quantity * terminal_prices
        data[f"Stock ({stock_quantity:g})"] = values
        total += values
    if abs(bond_payoff) > 1e-12:
        values = np.full_like(terminal_prices, bond_payoff)
        data[f"Riskless payoff ({bond_payoff:g})"] = values
        total += values
    for pos in positions:
        kind, strike, quantity = str(pos["kind"]), float(pos["strike"]), float(pos["quantity"])
        intrinsic = np.maximum(terminal_prices - strike, 0.0) if kind == "call" else np.maximum(strike - terminal_prices, 0.0)
        values = quantity * multiplier * intrinsic
        data[f"{quantity:g} x {strike:g} {kind}"] = values
        total += values
    data["Total payoff"] = total
    data["Profit"] = total - net_initial_cost
    if financed_cost is not None:
        data["Profit incl. financing"] = total - financed_cost
    return pd.DataFrame(data)


def break_even_points(terminal_prices, profit):
    roots = []
    x, y = np.asarray(terminal_prices, dtype=float), np.asarray(profit, dtype=float)
    for i in range(len(x) - 1):
        if abs(y[i]) < 1e-10:
            roots.append(float(x[i]))
        if y[i] * y[i + 1] < 0:
            roots.append(float(x[i] - y[i] * (x[i + 1] - x[i]) / (y[i + 1] - y[i])))
    if abs(y[-1]) < 1e-10:
        roots.append(float(x[-1]))
    return [root for i, root in enumerate(roots) if i == 0 or abs(root - roots[i - 1]) > 1e-5]


def terminal_cost(net_initial_cost, rate, maturity):
    return net_initial_cost * exp(rate * maturity)
