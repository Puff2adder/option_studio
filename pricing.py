"""Black-Scholes pricing utilities for the Options Strategy Learning Studio."""

from __future__ import annotations

from math import exp, log, sqrt
from statistics import NormalDist

import pandas as pd

N = NormalDist().cdf


def black_scholes_prices(spot, strike, maturity, rate, volatility, dividend_yield=0.0):
    """Return European call and put prices with continuous compounding."""
    if spot <= 0 or strike <= 0:
        raise ValueError("Spot and strike must be positive.")
    if maturity < 0 or volatility < 0:
        raise ValueError("Maturity and volatility cannot be negative.")
    if maturity == 0:
        return max(spot - strike, 0.0), max(strike - spot, 0.0)
    if volatility == 0:
        stock_pv = spot * exp(-dividend_yield * maturity)
        strike_pv = strike * exp(-rate * maturity)
        return max(stock_pv - strike_pv, 0.0), max(strike_pv - stock_pv, 0.0)
    scale = volatility * sqrt(maturity)
    d1 = (log(spot / strike) + (rate - dividend_yield + 0.5 * volatility**2) * maturity) / scale
    d2 = d1 - scale
    call = spot * exp(-dividend_yield * maturity) * N(d1) - strike * exp(-rate * maturity) * N(d2)
    put = strike * exp(-rate * maturity) * N(-d2) - spot * exp(-dividend_yield * maturity) * N(-d1)
    return call, put


def option_chain(spot, strikes, maturity, rate, volatility, dividend_yield=0.0):
    rows = []
    for strike in sorted(strikes):
        call, put = black_scholes_prices(spot, strike, maturity, rate, volatility, dividend_yield)
        parity_error = call - put - spot * exp(-dividend_yield * maturity) + strike * exp(-rate * maturity)
        rows.append({
            "Strike": float(strike),
            "Moneyness": strike / spot,
            "Call price": call,
            "Put price": put,
            "Parity error": parity_error,
        })
    return pd.DataFrame(rows)


def price_lookup(chain):
    return {
        float(row["Strike"]): {"call": float(row["Call price"]), "put": float(row["Put price"])}
        for _, row in chain.iterrows()
    }
