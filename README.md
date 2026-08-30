# Options Strategy Learning Studio

An ungraded, student-facing Streamlit laboratory for European call and put options.

## Version 2 capabilities

- Generates a hypothetical stock, volatility, rates, maturity, strikes, and Black-Scholes option chain.
- Separates option payoff from profit.
- Builds multi-leg strategies using stock, a riskless terminal payoff, calls, and puts.
- Shows signed component costs, terminal scenario tables, payoff diagrams, profit diagrams, and break-even points.
- Provides six attempt-first economic design problems without asking students to choose a named strategy.
- Checks a student's constructed payoff against the required shape while still allowing payoff-equivalent portfolios.
- Unlocks progressive economic and slope tips only after the student checks an attempt.
- Reverse-engineers continuous piecewise-linear target payouts using a bond, stock, and calls.
- Includes eight replication problem sets drawn from acquisitions, corporate securities, compensation, procurement, revenue protection, and structured investments.
- Accepts exact fractional replication entries such as `60/55`; rounded attempts are accepted when every payoff is within one cent of the target.
- Labels available strikes on replication graphs and highlights strikes where the target slope changes.
- Requires a separate Law of One Price valuation after a target payout is matched and checks the student's value before revealing component arithmetic.
- Includes guided managerial applications and ungraded knowledge checks.

## Run locally

Double-click `Launch Options Strategy Learning Studio.cmd`, or run:

```text
python -m streamlit run app.py --server.port 8770
```

Then open `http://localhost:8770`.

## Deploy

Upload the project files to a GitHub repository. In Streamlit Community Cloud, select the repository,
the `main` branch, and `app.py` as the main file path. Python 3.13 is recommended because that is the
local test environment.

All prices and scenarios are hypothetical and intended for education, not investment advice.
