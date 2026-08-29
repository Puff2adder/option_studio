# Options Strategy Learning Studio

An ungraded, student-facing Streamlit laboratory for European call and put options.

## Version 1 capabilities

- Generates a hypothetical stock, volatility, rates, maturity, strikes, and Black-Scholes option chain.
- Separates option payoff from profit.
- Builds multi-leg strategies using stock, a riskless terminal payoff, calls, and puts.
- Shows signed component costs, terminal scenario tables, payoff diagrams, profit diagrams, and break-even points.
- Reverse-engineers continuous piecewise-linear target payouts using a bond, stock, and calls.
- Accepts exact fractional replication entries such as `60/55`; rounded attempts are accepted when every payoff is within one cent of the target.
- Labels available strikes on replication graphs and highlights strikes where the target slope changes.
- Includes guided managerial applications and ungraded knowledge checks.

## Run locally

Double-click `Launch Options Strategy Learning Studio.cmd`, or run:

```text
python -m streamlit run app.py --server.port 8769
```

Then open `http://localhost:8769`.

## Deploy

Upload the project files to a GitHub repository. In Streamlit Community Cloud, select the repository,
the `main` branch, and `app.py` as the main file path. Python 3.13 is recommended because that is the
local test environment.

All prices and scenarios are hypothetical and intended for education, not investment advice.
