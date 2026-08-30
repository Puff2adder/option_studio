"""Options Strategy Learning Studio - Version 2.0."""

from __future__ import annotations

from math import exp
import secrets

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from challenge_bank import replication_challenges, strategy_design_challenges
from pricing import option_chain, price_lookup
from question_bank import QUESTIONS, generated_question, shuffled_choices
from replication import (
    calls_only_replication,
    parse_fractional_number,
    piecewise_target,
    replication_matches,
    replication_formula,
    replication_positions_table,
)
from strategy import (
    active_option_positions,
    break_even_points,
    component_costs,
    strategy_scenarios,
    terminal_cost,
)
from ui import concept, configure_page, hero, signed_money, success_box, why_it_matters


configure_page()


def rounded_strikes(spot: float) -> list[float]:
    raw = np.linspace(0.7 * spot, 1.3 * spot, 7)
    step = 5.0 if spot >= 40 else 2.5
    strikes = sorted({round(value / step) * step for value in raw})
    while len(strikes) < 7:
        strikes.append(strikes[-1] + step)
    return strikes[:7]


def random_market() -> dict[str, float]:
    st.session_state.market_seed = st.session_state.get("market_seed", 2301) + 1
    rng = np.random.default_rng(st.session_state.market_seed)
    spot = float(rng.choice(np.arange(60, 141, 5)))
    return {
        "spot_input": spot,
        "vol_input": int(rng.choice([18, 22, 26, 30, 34])),
        "rate_input": float(rng.choice([2.0, 3.0, 4.0, 5.0])),
        "div_input": float(rng.choice([0.0, 1.0, 2.0, 3.0])),
        "mat_input": float(rng.choice([0.25, 0.50, 0.75, 1.00])),
    }


if "market_seed" not in st.session_state:
    st.session_state.market_seed = 2300
for key, value in random_market().items():
    st.session_state.setdefault(key, value)
if st.session_state.get("market_unit_schema") != "percentage_points":
    if st.session_state["vol_input"] <= 1:
        st.session_state["vol_input"] *= 100
    if st.session_state["rate_input"] <= 1:
        st.session_state["rate_input"] *= 100
    if st.session_state["div_input"] <= 1:
        st.session_state["div_input"] *= 100
    st.session_state.market_unit_schema = "percentage_points"


st.sidebar.title("Options Strategy Studio")
st.sidebar.caption("Version 2.0 · European options · hypothetical data")
navigation = st.sidebar.radio(
    "Learning laboratory",
    [
        "Studio orientation",
        "1 · Create the market",
        "2 · Single positions",
        "3 · Strategy builder",
        "4 · Strategy design problems",
        "5 · Replication problem sets",
        "6 · Guided applications",
        "7 · Knowledge check",
    ],
)
st.sidebar.divider()
st.sidebar.subheader("Hypothetical market")
if st.sidebar.button("Generate a new market", width="stretch"):
    for key, value in random_market().items():
        st.session_state[key] = value
    st.session_state.pop("strategy_positions", None)
    st.session_state.pop("strategy_result", None)
    st.rerun()

spot = st.sidebar.number_input("Stock price today", min_value=10.0, max_value=500.0, step=5.0, key="spot_input")
volatility = st.sidebar.slider("Annual volatility (%)", 5, 80, step=1, key="vol_input") / 100.0
rate = st.sidebar.slider("Risk-free rate (%)", 0.0, 15.0, step=0.5, key="rate_input") / 100.0
dividend_yield = st.sidebar.slider("Dividend yield (%)", 0.0, 10.0, step=0.5, key="div_input") / 100.0
maturity = st.sidebar.select_slider("Years to expiration", options=[0.25, 0.50, 0.75, 1.00, 1.50, 2.00], key="mat_input")

strikes = rounded_strikes(float(spot))
chain = option_chain(float(spot), strikes, float(maturity), float(rate), float(volatility), float(dividend_yield))
prices = price_lookup(chain)
signature = (round(float(spot), 4), tuple(strikes), round(float(maturity), 4), round(float(rate), 5), round(float(volatility), 5), round(float(dividend_yield), 5))


def market_metrics():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stock price", f"${spot:,.2f}")
    c2.metric("Volatility", f"{volatility:.0%}")
    c3.metric("Expiration", f"{maturity:g} years")
    c4.metric("Strike range", f"{strikes[0]:g}–{strikes[-1]:g}")


def strategy_chart(frame: pd.DataFrame, active_strikes: list[float], include_components=False):
    x = frame["Stock price at expiration"]
    fig = go.Figure()
    if include_components:
        excluded = {"Stock price at expiration", "Total payoff", "Profit", "Profit incl. financing"}
        for column in [c for c in frame.columns if c not in excluded]:
            fig.add_trace(go.Scatter(x=x, y=frame[column], mode="lines", name=column, opacity=0.35,
                                     line=dict(width=1.4)))
    fig.add_trace(go.Scatter(x=x, y=frame["Total payoff"], mode="lines", name="Total payoff",
                             line=dict(color="#17365d", width=4)))
    fig.add_trace(go.Scatter(x=x, y=frame["Profit"], mode="lines", name="Profit",
                             line=dict(color="#c94f45", width=3, dash="dash")))
    fig.add_hline(y=0, line_color="#7b8794", line_width=1)
    for strike in sorted(set(active_strikes)):
        fig.add_vline(x=strike, line_color="#d9a441", line_dash="dot", opacity=0.6)
    fig.update_layout(
        height=470,
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title="Stock price at expiration, S_T",
        yaxis_title="Dollars",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def mark_replication_strikes(fig: go.Figure, available_strikes, kink_strikes):
    """Put every available strike on the x-axis and emphasize payoff kinks."""
    strike_ticks = sorted({float(value) for value in available_strikes})
    fig.update_xaxes(
        tickmode="array",
        tickvals=strike_ticks,
        ticktext=[f"{value:g}" for value in strike_ticks],
        tickangle=0,
    )
    for strike_value in sorted({float(value) for value in kink_strikes}):
        fig.add_vline(
            x=strike_value,
            line_color="#d9a441",
            line_dash="dot",
            opacity=0.75,
            annotation_text=f"K = {strike_value:g}",
            annotation_position="top",
        )
    return fig


def empty_position_table():
    return pd.DataFrame({"Strike": strikes, "Calls": np.zeros(len(strikes)), "Puts": np.zeros(len(strikes))})


def ensure_strategy_state():
    if st.session_state.get("strategy_signature") != signature:
        st.session_state.strategy_signature = signature
        st.session_state.strategy_positions = empty_position_table()
        st.session_state.strategy_stock = 0.0
        st.session_state.strategy_bond = 0.0
        st.session_state.strategy_result = None
        st.session_state.strategy_editor_nonce = st.session_state.get("strategy_editor_nonce", 0) + 1


def reset_strategy():
    st.session_state.strategy_stock = 0.0
    st.session_state.strategy_bond = 0.0
    st.session_state.strategy_positions = empty_position_table()
    st.session_state.strategy_result = None
    st.session_state.strategy_editor_nonce = st.session_state.get("strategy_editor_nonce", 0) + 1


if navigation == "Studio orientation":
    st.title("Options Strategy Learning Studio")
    hero("Design the payoff before trying to price it", "Build intuition from component tables, payoff diagrams, profit diagrams, and calls-only replication.")
    market_metrics()
    st.subheader("The organizing question")
    st.markdown("### What payoff do we want, and how can options create it?")
    left, right = st.columns([1.15, 1])
    with left:
        concept("The learning sequence", "Exposure → bad outcome → favorable outcome to preserve → option design → component table → diagram → interpretation.")
        st.markdown(
            """
            1. Create a hypothetical but internally consistent option market.
            2. Separate **payoff** from **profit** for individual positions.
            3. Mesh stock, a riskless bond, calls, and puts into a strategy.
            4. Solve economic design problems without beginning from a named strategy.
            5. Reverse-engineer target payouts and value them using the Law of One Price.
            6. Apply the ideas to operating risks, portfolios, and corporate contracts.
            """
        )
    with right:
        st.info("This is an ungraded practice laboratory. Try a position, inspect the table, explain the shape, and reset as often as useful.")
        st.markdown("**Sign convention**")
        st.markdown("Positive quantity = long or purchased position. Negative quantity = short or sold position.")
        st.markdown("**Version 2 profit convention**")
        st.markdown("Profit equals terminal payoff minus initial net cost. Financing can be displayed as an optional extension.")
    why_it_matters("Executives rarely want to eliminate every uncertain outcome. Options allow them to reshape exposure by transferring selected states of the world.")
    st.subheader("A critical distinction")
    st.write("Payoff describes what the position delivers at expiration. Profit also recognizes what the position cost—or received—today.")

elif navigation == "1 · Create the market":
    st.title("1. Create the option market")
    hero("One stock, one maturity, several strikes", "The prices below are generated from the Black-Scholes model using the hypothetical inputs in the sidebar.")
    market_metrics()
    st.subheader("European option prices")
    display_chain = chain.copy()
    display_chain["Moneyness"] = display_chain["Moneyness"].map(lambda x: f"{x:.2f}× spot")
    st.dataframe(display_chain, width="stretch", hide_index=True,
                 column_config={"Strike": st.column_config.NumberColumn(format="$%.2f"),
                                "Call price": st.column_config.NumberColumn(format="$%.4f"),
                                "Put price": st.column_config.NumberColumn(format="$%.4f"),
                                "Parity error": st.column_config.NumberColumn(format="%.2e")})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=chain["Strike"], y=chain["Call price"], mode="lines+markers", name="Calls", line=dict(color="#2e74b5", width=3)))
    fig.add_trace(go.Scatter(x=chain["Strike"], y=chain["Put price"], mode="lines+markers", name="Puts", line=dict(color="#c94f45", width=3)))
    fig.add_vline(x=spot, line_dash="dot", line_color="#d9a441", annotation_text="Stock price")
    fig.update_layout(template="plotly_white", height=390, xaxis_title="Strike", yaxis_title="Black-Scholes price",
                      margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch", key="market_option_chain_chart")
    concept("Model assumptions", "European exercise; no arbitrage; continuously compounded risk-free and dividend rates; constant volatility; frictionless trading; lognormal stock prices.")
    st.subheader("Pause and predict")
    st.markdown("- If volatility rises, what happens to both call and put prices?\n- As the strike rises, why do calls generally become cheaper while puts become more expensive?\n- Why is a tiny parity error reassuring?")
    why_it_matters("The option chain gives every component a consistent price today. The strategy laboratory can therefore add component costs without mixing incompatible assumptions.")

elif navigation == "2 · Single positions":
    st.title("2. Explore a single option position")
    hero("Start with one contract", "Change the right, obligation, strike, or direction and watch payoff separate from profit.")
    c1, c2, c3 = st.columns(3)
    kind = c1.selectbox("Instrument", ["Call", "Put"])
    side = c2.selectbox("Position", ["Long", "Short"])
    strike = c3.selectbox("Strike", strikes, index=len(strikes) // 2)
    quantity = 1.0 if side == "Long" else -1.0
    premium = prices[float(strike)][kind.lower()]
    initial_cost = quantity * premium
    positions = [{"kind": kind.lower(), "strike": float(strike), "quantity": quantity}]
    grid = np.linspace(max(0.0, 0.35 * spot), 1.65 * spot, 261)
    scenarios = strategy_scenarios(grid, 0.0, 0.0, positions, initial_cost)
    m1, m2, m3 = st.columns(3)
    m1.metric("Premium per option", f"${premium:,.2f}")
    m2.metric("Initial signed cost", signed_money(initial_cost))
    be = break_even_points(grid, scenarios["Profit"].to_numpy())
    m3.metric("Break-even", ", ".join(f"${x:,.2f}" for x in be) if be else "None in range")
    st.plotly_chart(
        strategy_chart(scenarios, [strike]),
        width="stretch",
        key="single_position_payoff_profit_chart",
    )
    table_prices = sorted(set([max(0, strike - 20), strike - 10, strike, strike + 10, strike + 20]))
    table = strategy_scenarios(np.array(table_prices), 0.0, 0.0, positions, initial_cost)
    st.dataframe(table.round(2), width="stretch", hide_index=True)
    if kind == "Call":
        concept("The kink", f"The call changes slope at K = {strike:g}. The long position owns the right to buy; the short position accepts the corresponding obligation.")
    else:
        concept("Downside insurance", f"The put responds below K = {strike:g}. The long position owns the right to sell; the short position accepts the obligation to buy or settle.")
    why_it_matters("A premium does not change the payoff shape. It shifts the profit line vertically, which is why payoff and profit must never be used interchangeably.")

elif navigation == "3 · Strategy builder":
    ensure_strategy_state()
    st.title("3. General strategy builder")
    hero("Build any strategy from its components", "Do not begin with a strategy name. Enter signed positions, calculate their cost, read the component table, and then interpret the diagram.")
    concept(
        "What to do",
        "1. Enter shares of stock and the face value of the riskless payoff. "
        "2. Enter call and put quantities beside the desired strikes. "
        "3. Select Calculate strategy. Positive quantities are long; negative quantities are short.",
    )
    reset_col, note_col = st.columns([0.28, 0.72])
    reset_col.button("Reset everything to zero", on_click=reset_strategy, width="stretch")
    note_col.caption("Every entry begins at zero. Fractional quantities are allowed; for example, 1.25 or 0.8333.")
    q1, q2 = st.columns(2)
    stock_quantity = q1.number_input("Shares / units of stock", step=0.25, key="strategy_stock")
    bond_payoff = q2.number_input("Face value of riskless bonds at expiration", step=5.0, key="strategy_bond",
                                  help="Enter the total riskless dollar payoff at T. Its current cost is discounted at the risk-free rate.")
    st.markdown("### Calls and puts by strike")
    edited = st.data_editor(
        st.session_state.strategy_positions,
        width="stretch",
        hide_index=True,
        disabled=["Strike"],
        key=f"strategy_editor_{hash(signature)}_{st.session_state.strategy_editor_nonce}",
        column_config={"Strike": st.column_config.NumberColumn(format="$%.2f"),
                       "Calls": st.column_config.NumberColumn(step=0.25, format="%.4g"),
                       "Puts": st.column_config.NumberColumn(step=0.25, format="%.4g")},
    )
    st.session_state.strategy_positions = edited
    with st.expander("Optional contract scaling"):
        multiplier = st.number_input("Units controlled by each option quantity", min_value=1.0, max_value=1000.0,
                                     value=1.0, step=1.0,
                                     help="Leave at 1 for per-share analysis. Use 100 for standard equity-option contract scaling.")
    include_financing = st.checkbox("Also show profit after carrying the initial net cost to expiration", value=False)
    show_components = st.checkbox("Show component lines on the graph", value=False)
    if st.button("Calculate strategy", type="primary", width="stretch"):
        st.session_state.strategy_result = {
            "stock": float(stock_quantity), "bond": float(bond_payoff), "multiplier": float(multiplier),
            "positions": edited.copy(), "financing": include_financing,
        }
    result = st.session_state.get("strategy_result")
    if result:
        positions = active_option_positions(result["positions"])
        costs = component_costs(spot, rate, maturity, result["stock"], result["bond"], positions, prices, result["multiplier"])
        net_cost = float(costs["Signed cost"].sum())
        financed = terminal_cost(net_cost, rate, maturity) if result["financing"] else None
        grid = np.linspace(max(0.0, 0.3 * spot), 1.7 * spot, 321)
        scenarios = strategy_scenarios(grid, result["stock"], result["bond"], positions, net_cost,
                                       result["multiplier"], financed)
        st.subheader("A. Establish the strategy's net cost")
        cost_view = costs.copy()
        total_row = pd.DataFrame([{"Component": "TOTAL NET COST", "Quantity": np.nan, "Unit price": np.nan, "Signed cost": net_cost}])
        st.dataframe(pd.concat([cost_view, total_row], ignore_index=True), width="stretch", hide_index=True,
                     column_config={"Quantity": st.column_config.NumberColumn(format="%.4g"),
                                    "Unit price": st.column_config.NumberColumn(format="$%.4f"),
                                    "Signed cost": st.column_config.NumberColumn(format="$%.2f")})
        a, b, c = st.columns(3)
        a.metric("Net initial cost", signed_money(net_cost))
        roots = break_even_points(grid, scenarios["Profit"].to_numpy())
        b.metric("Break-even price(s)", ", ".join(f"${x:.2f}" for x in roots) if roots else "None in range")
        c.metric("Active option legs", str(len(positions)))
        st.subheader("B. Table first")
        sample_prices = np.linspace(max(0.0, 0.4 * spot), 1.6 * spot, 13)
        sample = strategy_scenarios(sample_prices, result["stock"], result["bond"], positions, net_cost,
                                    result["multiplier"], financed)
        st.dataframe(sample.round(2), width="stretch", hide_index=True)
        st.subheader("C. Diagram second")
        st.plotly_chart(
            strategy_chart(scenarios, [float(p["strike"]) for p in positions], show_components),
            width="stretch",
            key="strategy_builder_payoff_profit_chart",
        )
        concept("Read the shape through slopes", "Stock contributes slope everywhere. A call changes slope above its strike. A put changes slope below its strike. The riskless bond changes the level, not the slope.")
        why_it_matters("The net cost tells us what the engineered payoff costs today. The terminal table shows exactly which component creates each region of the diagram.")
    else:
        st.info("All positions are currently zero. Enter any signed combination of stock, bonds, calls, and puts, then select **Calculate strategy**.")

elif navigation == "4 · Strategy design problems":
    st.title("4. Strategy design problems")
    hero(
        "Begin with a belief or decision—not a strategy name",
        "Construct signed stock, bond, call, and put positions. Then inspect both terminal payoff and profit.",
    )
    challenges = strategy_design_challenges(float(spot), strikes)
    challenge_index = st.selectbox(
        "Choose a problem",
        range(len(challenges)),
        format_func=lambda i: f"{challenges[i]['difficulty']} · {challenges[i]['title']}",
    )
    challenge = challenges[challenge_index]
    challenge_id = f"{challenge['id']}_{hash(signature)}"
    st.subheader(challenge["title"])
    st.write(challenge["setting"])
    concept("Required payoff behavior", challenge["payoff_goal"])
    st.markdown("**Questions to answer before entering positions**")
    for question in challenge["questions"]:
        st.markdown(f"- {question}")

    st.subheader("Construct and test your position")
    st.caption(
        "Positive quantities purchase rights or assets. Negative quantities write options, short assets, "
        "or borrow through a negative riskless payoff. No strategy-name menu is provided."
    )
    nonce_key = f"design_nonce_{challenge_id}"
    st.session_state.setdefault(nonce_key, 0)
    checked_key = f"design_checked_{challenge_id}"
    revealed_key = f"design_revealed_{challenge_id}"
    reset_col, instruction_col = st.columns([0.28, 0.72])
    if reset_col.button("Reset this attempt", key=f"design_reset_{challenge_id}", width="stretch"):
        st.session_state[nonce_key] += 1
        st.session_state.pop(checked_key, None)
        st.session_state.pop(revealed_key, None)
        st.rerun()
    instruction_col.caption("Try more than once. Feedback and slope tips appear only after you check an attempt.")
    nonce = st.session_state[nonce_key]
    q1, q2 = st.columns(2)
    design_stock = q1.number_input(
        "Shares / units of stock",
        step=0.25,
        value=0.0,
        key=f"design_stock_{challenge_id}_{nonce}",
    )
    design_bond = q2.number_input(
        "Face value of riskless payoff at expiration",
        step=5.0,
        value=0.0,
        key=f"design_bond_{challenge_id}_{nonce}",
    )
    design_table = st.data_editor(
        empty_position_table(),
        width="stretch",
        hide_index=True,
        disabled=["Strike"],
        key=f"design_editor_{challenge_id}_{nonce}",
        column_config={
            "Strike": st.column_config.NumberColumn(format="$%.2f"),
            "Calls": st.column_config.NumberColumn(step=0.25, format="%.5g"),
            "Puts": st.column_config.NumberColumn(step=0.25, format="%.5g"),
        },
    )
    if st.button("Check this design", type="primary", width="stretch", key=f"design_check_{challenge_id}_{nonce}"):
        st.session_state[checked_key] = nonce
    design_checked = st.session_state.get(checked_key) == nonce

    design_positions = active_option_positions(design_table)
    design_costs = component_costs(
        spot, rate, maturity, float(design_stock), float(design_bond), design_positions, prices
    )
    design_net_cost = float(design_costs["Signed cost"].sum())
    design_grid = np.linspace(max(0.0, 0.25 * spot), 1.75 * spot, 401)
    design_scenarios = strategy_scenarios(
        design_grid, float(design_stock), float(design_bond), design_positions, design_net_cost
    )
    solution_spec = challenge["solution"]
    target_scenarios = strategy_scenarios(
        design_grid,
        float(solution_spec["stock"]),
        float(solution_spec["bond"]),
        solution_spec["positions"],
        0.0,
    )
    design_error = float(
        np.max(
            np.abs(
                design_scenarios["Total payoff"].to_numpy()
                - target_scenarios["Total payoff"].to_numpy()
            )
        )
    )

    if design_checked:
        a, b, c = st.columns(3)
        a.metric("Net initial cost", signed_money(design_net_cost))
        design_profit = design_scenarios["Profit"].to_numpy()
        if np.all(np.abs(design_profit) < 1e-10):
            break_even_label = "Every price (zero position)"
        else:
            roots = break_even_points(design_grid, design_profit)
            break_even_label = ", ".join(f"${value:.2f}" for value in roots) if roots else "None in range"
        b.metric("Break-even price(s)", break_even_label)
        c.metric("Maximum payoff-shape difference", f"${design_error:.4f}")
        if replication_matches(design_error):
            st.success("Your positions create the required terminal payoff shape.")
        else:
            st.warning("The payoff does not yet match the required behavior. Compare the slope in each price region.")

        st.markdown("### A. Component cost and profit")
        design_cost_view = design_costs.copy()
        design_total_row = pd.DataFrame(
            [{"Component": "TOTAL NET COST", "Quantity": np.nan, "Unit price": np.nan, "Signed cost": design_net_cost}]
        )
        st.dataframe(
            pd.concat([design_cost_view, design_total_row], ignore_index=True),
            width="stretch",
            hide_index=True,
            column_config={
                "Quantity": st.column_config.NumberColumn(format="%.5g"),
                "Unit price": st.column_config.NumberColumn(format="$%.4f"),
                "Signed cost": st.column_config.NumberColumn(format="$%.2f"),
            },
        )
        st.plotly_chart(
            strategy_chart(design_scenarios, [float(position["strike"]) for position in design_positions], True),
            width="stretch",
            key="strategy_design_attempt_chart",
        )

        st.markdown("### B. Compare your payoff with the required shape")
        comparison_fig = go.Figure()
        comparison_fig.add_trace(
            go.Scatter(
                x=design_grid,
                y=target_scenarios["Total payoff"],
                mode="lines",
                name="Required payoff shape",
                line=dict(color="#c94f45", width=5),
            )
        )
        comparison_fig.add_trace(
            go.Scatter(
                x=design_grid,
                y=design_scenarios["Total payoff"],
                mode="lines",
                name="Your payoff",
                line=dict(color="#17365d", width=3, dash="dash"),
            )
        )
        comparison_fig.update_layout(
            template="plotly_white",
            height=420,
            xaxis_title="Stock price at expiration, S_T",
            yaxis_title="Terminal payoff",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(comparison_fig, width="stretch", key="strategy_design_comparison_chart")
        sample_prices = np.linspace(max(0.0, 0.50 * spot), 1.50 * spot, 9)
        sample_attempt = strategy_scenarios(
            sample_prices, float(design_stock), float(design_bond), design_positions, design_net_cost
        )
        st.dataframe(sample_attempt.round(2), width="stretch", hide_index=True)

        st.markdown("### C. Progressive tips")
        for tip_number, tip in enumerate(challenge["tips"], start=1):
            with st.expander(f"Tip {tip_number}"):
                st.write(tip)
        if st.button("Reveal one exact construction", key=f"design_reveal_{challenge_id}_{nonce}"):
            st.session_state[revealed_key] = nonce
        if st.session_state.get(revealed_key) == nonce:
            solution_costs = component_costs(
                spot,
                rate,
                maturity,
                float(solution_spec["stock"]),
                float(solution_spec["bond"]),
                solution_spec["positions"],
                prices,
            )
            solution_cost = float(solution_costs["Signed cost"].sum())
            solution_scenarios = strategy_scenarios(
                design_grid,
                float(solution_spec["stock"]),
                float(solution_spec["bond"]),
                solution_spec["positions"],
                solution_cost,
            )
            st.dataframe(solution_costs, width="stretch", hide_index=True)
            st.metric("Initial cost of this exact construction", signed_money(solution_cost))
            st.plotly_chart(
                strategy_chart(
                    solution_scenarios,
                    [float(position["strike"]) for position in solution_spec["positions"]],
                    True,
                ),
                width="stretch",
                key="strategy_design_solution_chart",
            )
            success_box("Economic interpretation", challenge["interpretation"])
    else:
        st.info("Enter a position and select **Check this design** before opening any tips or solutions.")

    why_it_matters(
        "A general calculator becomes a learning tool when the student must translate a belief or decision into "
        "rights, obligations, slopes, costs, and retained risks."
    )

elif navigation == "5 · Replication problem sets":
    st.title("5. Calls-only replication problem sets")
    hero(
        "Reverse-engineer and value an economically motivated payout",
        "Match levels and slopes first. After the payoff is correct, use component prices and the Law of One Price.",
    )
    high_node = max(strikes[-1] + (strikes[-1] - strikes[-2]), round(1.55 * spot, 2))
    nodes = np.array([0.0] + strikes + [high_node], dtype=float)
    replication_bank = replication_challenges(float(spot), strikes, nodes)
    replication_options = list(range(len(replication_bank) + 1))
    replication_index = st.selectbox(
        "Choose a replication problem",
        replication_options,
        format_func=lambda i: (
            f"{replication_bank[i]['difficulty']} · {replication_bank[i]['title']}"
            if i < len(replication_bank)
            else "Open laboratory · Custom piecewise-linear payout"
        ),
    )
    is_custom_replication = replication_index == len(replication_bank)
    if is_custom_replication:
        replication_problem = {
            "id": "custom_piecewise",
            "title": "Custom piecewise-linear payout",
            "story": (
                "Edit the target payout at the nodes. The laboratory draws straight lines between nodes and "
                "continues the final slope beyond the last node."
            ),
            "decision": "Create any continuous target, replicate it, and determine its no-arbitrage value.",
            "values": nodes.copy(),
            "interpretation": "Every continuous piecewise-linear payout can be decomposed into a level, an initial slope, and slope changes at calls' strikes.",
        }
    else:
        replication_problem = replication_bank[replication_index]
    preset = replication_problem["id"]
    values = np.asarray(replication_problem["values"], dtype=float)
    st.subheader(replication_problem["title"])
    concept("Economic setting", replication_problem["story"])
    st.markdown(f"**Your task:** {replication_problem['decision']}")
    st.markdown(
        "Before entering positions, identify the payout level at zero, the leftmost slope, every strike where "
        "the slope changes, and the size of each change."
    )
    if is_custom_replication:
        values = nodes.copy()
    target_input = pd.DataFrame({"Stock price node": nodes, "Target payout": values})
    target_columns = {"Stock price node": st.column_config.NumberColumn(format="$%.2f"),
                      "Target payout": st.column_config.NumberColumn(format="$%.2f", step=0.50)}
    if is_custom_replication:
        edited_target = st.data_editor(target_input, width="stretch", hide_index=True,
                                       disabled=["Stock price node"], key=f"target_{preset}_{hash(signature)}",
                                       column_config=target_columns)
    else:
        edited_target = target_input
        st.dataframe(edited_target, width="stretch", hide_index=True, column_config=target_columns)
    target_values = edited_target["Target payout"].to_numpy(dtype=float)
    replication = calls_only_replication(nodes, target_values)
    active_calls = [p for p in replication["call_positions"] if abs(float(p["quantity"])) > 1e-9]
    grid = np.linspace(0, 1.7 * spot, 401)
    target_curve = piecewise_target(nodes, target_values, grid)
    target_fig = go.Figure()
    target_fig.add_trace(go.Scatter(x=grid, y=target_curve, mode="lines", name="Target payout",
                                    line=dict(color="#c94f45", width=4)))
    target_fig.update_layout(template="plotly_white", height=350, xaxis_title="Stock price at expiration, S_T",
                             yaxis_title="Target payout", margin=dict(l=20, r=20, t=25, b=20))
    mark_replication_strikes(target_fig, strikes, [pos["strike"] for pos in active_calls])
    st.plotly_chart(target_fig, width="stretch", key="replication_target_chart")
    st.caption("Every available strike is labeled on the horizontal axis. Gold dotted lines identify strikes where the target slope changes.")

    st.subheader("Your attempted replication")
    st.write(
        "Enter a riskless terminal payoff, a stock quantity, and call quantities. Leave unused strikes at zero. "
        "You may enter decimals or exact fractions—for example, `60/55` or `-60/55`."
    )
    target_signature = tuple(np.round(target_values, 6))
    attempt_id = f"{preset}_{hash(signature)}_{hash(target_signature)}"
    a1, a2 = st.columns(2)
    attempt_bond_text = a1.text_input(
        "Attempt: face value of riskless bonds at T", value="0",
        key=f"attempt_bond_fraction_{attempt_id}", help="Examples: 0, 25, -10, or 100/3",
    )
    attempt_stock_text = a2.text_input(
        "Attempt: shares / units of stock", value="0",
        key=f"attempt_stock_fraction_{attempt_id}", help="Examples: 1.25, 60/55, or -3/4",
    )
    attempt_input = pd.DataFrame({"Strike": strikes, "Call quantity": ["0"] * len(strikes)})
    attempt_editor = st.data_editor(
        attempt_input, width="stretch", hide_index=True, disabled=["Strike"],
        key=f"attempt_calls_fraction_{attempt_id}",
        column_config={"Strike": st.column_config.NumberColumn(format="$%.2f"),
                       "Call quantity": st.column_config.TextColumn(
                           help="Enter a decimal or fraction, such as 0.5 or -60/55."
                       )},
    )
    if st.button("Check my attempted replication", type="primary", width="stretch", key=f"check_{attempt_id}"):
        st.session_state.replication_attempt_checked = attempt_id
    attempted = st.session_state.get("replication_attempt_checked") == attempt_id

    entry_error = None
    try:
        attempt_bond = parse_fractional_number(attempt_bond_text, "Riskless bond payoff")
        attempt_stock = parse_fractional_number(attempt_stock_text, "Stock quantity")
        parsed_calls = [
            parse_fractional_number(row["Call quantity"], f"Call quantity at strike {float(row['Strike']):g}")
            for _, row in attempt_editor.iterrows()
        ]
    except ValueError as exc:
        entry_error = str(exc)

    if attempted and entry_error:
        st.error(entry_error)
        st.info("Correct the entry and select **Check my attempted replication** again.")

    if attempted and not entry_error:
        attempt_positions = [
            {"kind": "call", "strike": float(row["Strike"]), "quantity": float(quantity)}
            for (_, row), quantity in zip(attempt_editor.iterrows(), parsed_calls) if abs(float(quantity)) > 1e-10
        ]
        attempt_scenarios = strategy_scenarios(grid, float(attempt_stock), float(attempt_bond),
                                               attempt_positions, 0.0)
        attempt_error = attempt_scenarios["Total payoff"].to_numpy() - target_curve
        max_attempt_error = float(np.max(np.abs(attempt_error)))
        st.metric("Maximum difference between your payout and the target", f"${max_attempt_error:.6f}")
        checking_tolerance = 0.01
        replication_correct = replication_matches(max_attempt_error, checking_tolerance)
        if replication_correct:
            if max_attempt_error < 1e-8:
                st.success("Exact replication. Your portfolio matches the target at every tested stock price.")
            else:
                st.success(
                    "Replication correct to the nearest cent. The small displayed difference comes from rounding "
                    "decimal quantities; enter fractions if you want the exact mathematical match."
                )
        else:
            st.warning("The attempted payout differs from the target by more than $0.01. Compare slopes one interval at a time.")
        attempt_fig = go.Figure()
        attempt_fig.add_trace(go.Scatter(x=grid, y=target_curve, mode="lines", name="Target",
                                         line=dict(color="#c94f45", width=4)))
        attempt_fig.add_trace(go.Scatter(x=grid, y=attempt_scenarios["Total payoff"], mode="lines",
                                         name="Your attempt", line=dict(color="#17365d", width=3, dash="dash")))
        attempt_fig.update_layout(template="plotly_white", height=390, xaxis_title="Stock price at expiration, S_T",
                                  yaxis_title="Payout", margin=dict(l=20, r=20, t=25, b=20),
                                  legend=dict(orientation="h", y=1.08))
        mark_replication_strikes(attempt_fig, strikes, [pos["strike"] for pos in active_calls])
        st.plotly_chart(attempt_fig, width="stretch", key="replication_attempt_chart")

        if replication_correct:
            st.subheader("Law of One Price valuation")
            st.write(
                "Because your portfolio reproduces the target payout in every state, the target must have the same "
                "value as the stock, bond, and calls used in your replication. Use the market prices below to "
                "calculate that value before revealing the component arithmetic."
            )
            valuation_rows = [
                {"Tradable component": "Stock", "Unit price today": float(spot)},
                {
                    "Tradable component": "$1 riskless payoff at T",
                    "Unit price today": float(exp(-rate * maturity)),
                },
            ]
            valuation_rows.extend(
                {
                    "Tradable component": f"Call, K = {float(strike_value):g}",
                    "Unit price today": float(prices[float(strike_value)]["call"]),
                }
                for strike_value in strikes
            )
            st.dataframe(
                pd.DataFrame(valuation_rows),
                width="stretch",
                hide_index=True,
                column_config={"Unit price today": st.column_config.NumberColumn(format="$%.4f")},
            )
            attempt_costs = component_costs(
                spot,
                rate,
                maturity,
                float(attempt_stock),
                float(attempt_bond),
                attempt_positions,
                prices,
            )
            attempt_value = float(attempt_costs["Signed cost"].sum())
            student_value = st.number_input(
                "Your no-arbitrage value today",
                value=0.0,
                step=0.50,
                key=f"student_value_{attempt_id}",
            )
            valuation_checked_key = f"valuation_checked_{attempt_id}"
            if st.button("Check my valuation", type="primary", key=f"check_value_{attempt_id}"):
                st.session_state[valuation_checked_key] = True
            if st.session_state.get(valuation_checked_key):
                valuation_error = abs(float(student_value) - attempt_value)
                if valuation_error <= 0.02:
                    st.success(
                        f"Correct. The target payout is worth {signed_money(attempt_value)} today by the Law of One Price."
                    )
                else:
                    st.warning(
                        "Not yet. Multiply every signed quantity by its unit price today, including discounting "
                        "the riskless terminal payoff, and then add the signed component costs."
                    )
                with st.expander("Valuation tip · Keep quantities and signs visible"):
                    st.write(
                        "Long stock and purchased calls have positive signed costs. Short stock and written calls "
                        "have negative signed costs. A terminal bond payoff B costs B exp(-rT) today."
                    )
                if st.button("Reveal the component valuation arithmetic", key=f"reveal_value_{attempt_id}"):
                    st.session_state[f"valuation_revealed_{attempt_id}"] = True
                if st.session_state.get(f"valuation_revealed_{attempt_id}"):
                    st.dataframe(
                        attempt_costs,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "Quantity": st.column_config.NumberColumn(format="%.5g"),
                            "Unit price": st.column_config.NumberColumn(format="$%.4f"),
                            "Signed cost": st.column_config.NumberColumn(format="$%.4f"),
                        },
                    )
                    st.metric("Sum of signed component costs", signed_money(attempt_value))

        st.subheader("Guided slope hints")
        with st.expander("Hint 1 · What is the leftmost slope?"):
            first_slope = float(replication["segment_slopes"][0])
            st.write(
                f"From S_T = {nodes[0]:g} to {nodes[1]:g}, the payout changes from "
                f"{target_values[0]:.2f} to {target_values[1]:.2f}. "
                f"The slope is ({target_values[1]:.2f} - {target_values[0]:.2f}) / "
                f"({nodes[1]:g} - {nodes[0]:g}) = **{first_slope:.5f}**. "
                f"Begin with **{first_slope:.5f} shares**."
            )
        for hint_number, pos in enumerate(active_calls, start=2):
            strike_value = float(pos["strike"])
            node_index = int(np.where(np.isclose(nodes, strike_value))[0][0])
            slope_before = float(replication["segment_slopes"][node_index - 1])
            slope_after = float(replication["segment_slopes"][node_index])
            change = slope_after - slope_before
            action = "buy" if change > 0 else "sell"
            with st.expander(f"Hint {hint_number} · What happens at S_T = {strike_value:g}?"):
                st.write(
                    f"The slope changes from **{slope_before:.5f}** to **{slope_after:.5f}**. "
                    f"The change is **{change:+.5f}**. Therefore {action} **{abs(change):.5f} calls** "
                    f"with strike **{strike_value:g}**."
                )

        if st.button("Reveal the complete calls-only solution", key=f"reveal_{attempt_id}"):
            st.session_state.replication_solution_revealed = attempt_id
        if st.session_state.get("replication_solution_revealed") == attempt_id:
            rep_costs = component_costs(spot, rate, maturity, replication["stock_quantity"],
                                        replication["bond_payoff"], active_calls, prices)
            rep_cost = float(rep_costs["Signed cost"].sum())
            rep_scenarios = strategy_scenarios(grid, replication["stock_quantity"],
                                               replication["bond_payoff"], active_calls, rep_cost)
            solution_error = rep_scenarios["Total payoff"].to_numpy() - target_curve
            st.subheader("Complete calls-only solution")
            st.code("X_T = " + replication_formula(replication), language=None)
            c1, c2, c3 = st.columns(3)
            c1.metric("Current replication cost", signed_money(rep_cost))
            c2.metric("Maximum payout error", f"${np.max(np.abs(solution_error)):.8f}")
            c3.metric("Nonzero call positions", str(len(active_calls)))
            solution_table = replication_positions_table(replication)
            solution_table = solution_table[solution_table["Quantity"].abs() > 1e-10]
            st.dataframe(solution_table, width="stretch", hide_index=True,
                         column_config={"Quantity": st.column_config.NumberColumn(format="%.5f")})
            solution_fig = go.Figure()
            solution_fig.add_trace(go.Scatter(x=grid, y=target_curve, mode="lines", name="Target payout",
                                               line=dict(color="#c94f45", width=5)))
            solution_fig.add_trace(go.Scatter(x=grid, y=rep_scenarios["Total payoff"], mode="lines",
                                               name="Calls-only replication",
                                               line=dict(color="#17365d", width=2, dash="dash")))
            solution_fig.update_layout(template="plotly_white", height=430,
                                       xaxis_title="Stock price at expiration, S_T", yaxis_title="Payout",
                                       margin=dict(l=20, r=20, t=30, b=20),
                                       legend=dict(orientation="h", y=1.08))
            mark_replication_strikes(solution_fig, strikes, [pos["strike"] for pos in active_calls])
            st.plotly_chart(solution_fig, width="stretch", key="replication_solution_chart")
            success_box(
                "Replication and economic meaning",
                "The target and replication lie on top of one another. Each call quantity equals the change in "
                f"slope at its strike. {replication_problem['interpretation']}",
            )
    elif not attempted:
        st.info("Try the replication before opening any hints. Select **Check my attempted replication** when ready.")

    why_it_matters("This turns a contract diagram into a portfolio. Begin with the stock slope, use calls to change the slope at each boundary, and use the riskless bond to establish the vertical level.")
    st.caption("Version 2 exactly handles continuous piecewise-linear payouts. A discontinuous digital payoff requires an approximation with tightly spaced call positions.")

elif navigation == "6 · Guided applications":
    case_low, case_high = strikes[2], strikes[-3]
    middle = len(strikes) // 2
    nearby = chain.iloc[max(0, middle - 1): min(len(chain), middle + 2)].copy()
    menu_columns = {
        "Strike": st.column_config.NumberColumn(format="$%.2f"),
        "Call price": st.column_config.NumberColumn(format="$%.4f"),
        "Put price": st.column_config.NumberColumn(format="$%.4f"),
    }
    st.title("6. Guided applications")
    hero("Choose a contract from prices and protection", "Each case supplies hypothetical option prices. Recommend a strike by explaining when protection begins, what favorable outcome remains, and what the premium costs.")
    tabs = st.tabs(["Input-cost insurance", "Portfolio protection", "Premium and obligation", "Merger payout"])
    with tabs[0]:
        st.subheader("A manufacturer needs an input later")
        st.write(f"The input costs ${spot:.2f} today and must be purchased at expiration. Higher prices are harmful; lower prices are favorable.")
        st.dataframe(nearby[["Strike", "Call price"]], width="stretch", hide_index=True,
                     column_config=menu_columns)
        st.markdown(
            "1. Which call strike would you recommend, and why?  \n"
            "2. At what input price does protection begin?  \n"
            "3. Would management pay more for an earlier cap, or accept a higher strike for a lower premium?"
        )
        with st.expander("Reveal the contract-choice logic"):
            st.write(
                "Buy a call. A lower strike begins protection sooner but normally costs more. An at-the-money or "
                "slightly out-of-the-money call is often considered, but the best strike depends on the maximum "
                "tolerable input cost and the premium budget—not on a strategy name. Selling a still higher-strike "
                "call reduces the premium but gives up protection above that second strike."
            )
    with tabs[1]:
        st.subheader("An investor wants a floor but would like to preserve upside")
        st.write(f"The portfolio is currently worth ${spot:.2f} per unit. The investor must choose how far below today's value the floor should begin.")
        st.dataframe(nearby[["Strike", "Put price"]], width="stretch", hide_index=True,
                     column_config=menu_columns)
        st.markdown(
            "1. Which put strike would you recommend?  \n"
            "2. What approximate floor does that strike establish before premium?  \n"
            "3. Is the stronger protection from the higher-strike put worth its larger premium?"
        )
        with st.expander("Reveal the contract-choice logic"):
            st.write(
                "Buy a put. A higher put strike creates a higher floor but is generally more expensive. A strike at "
                "or modestly below the current stock price is common when meaningful downside protection is desired. "
                "The recommendation should state both the protected level and the premium trade-off."
            )
    with tabs[2]:
        st.subheader("A client wants to earn option premium")
        st.write("The client must choose the obligation before focusing on the premium received.")
        st.dataframe(nearby[["Strike", "Call price", "Put price"]], width="stretch", hide_index=True,
                     column_config=menu_columns)
        st.markdown(
            "1. If the client owns the stock, at which call strike would the client genuinely be willing to sell away upside?  \n"
            "2. If the client wants to acquire the stock after a decline, which put strike represents an acceptable purchase price?  \n"
            "3. How does the quoted premium compensate for each obligation?"
        )
        with st.expander("Reveal the obligation logic"):
            st.write(
                "A covered-call strike should reflect the price above which the owner is willing to surrender further "
                "upside. A short-put strike should reflect a price at which the writer is genuinely willing and able to "
                "buy. An out-of-the-money contract usually pays less premium but postpones the obligation. A naked call "
                "has no offsetting stock and can lose without bound."
            )
    with tabs[3]:
        st.subheader("A stock-financed acquisition needs a negotiated payout")
        initial_slope = spot / case_low
        merger_prices = chain[chain["Strike"].isin([case_low, case_high])][["Strike", "Call price"]]
        st.write(
            f"The target payout rises from zero to {spot:.2f} as the acquirer's stock rises from 0 to {case_low:g}. "
            f"It remains fixed at {spot:.2f} from {case_low:g} through {case_high:g}. Above {case_high:g}, "
            f"the required payout slope is explicitly **0.50**."
        )
        st.dataframe(merger_prices, width="stretch", hide_index=True, column_config=menu_columns)
        st.markdown(
            f"1. What stock quantity creates the leftmost slope of {spot:g}/{case_low:g}?  \n"
            f"2. How many {case_low:g} calls must be sold to make the slope zero?  \n"
            f"3. How many {case_high:g} calls must be bought to make the slope 0.50 above {case_high:g}?  \n"
            "4. Use the quoted prices to calculate today's value of the complete payout."
        )
        with st.expander("Reveal the calls-only construction method"):
            st.write(
                f"Start with **{initial_slope:.5f} shares**. At {case_low:g}, the slope must fall from "
                f"{initial_slope:.5f} to zero, so sell **{initial_slope:.5f} calls with strike {case_low:g}**. "
                f"At {case_high:g}, the slope must rise from zero to 0.50, so buy **0.50000 calls with strike "
                f"{case_high:g}**. No riskless bond is needed because the payout begins at zero."
            )
    why_it_matters("Strategy names are secondary. The durable skill is translating a business exposure into signed component payoffs and then explaining who bears each state of the world.")

else:
    st.title("7. Knowledge check and question generator")
    hero("Practice without grades", "Choose an answer, inspect the explanation, and generate a numerical question from the current market.")
    st.session_state.setdefault("knowledge_shuffle_seed", secrets.randbits(63))
    question_col, shuffle_col = st.columns([0.72, 0.28])
    q_index = question_col.selectbox(
        "Conceptual question",
        range(len(QUESTIONS)),
        format_func=lambda i: f"Question {i + 1} of {len(QUESTIONS)}",
    )
    if shuffle_col.button("Reshuffle answers", width="stretch"):
        st.session_state.knowledge_shuffle_seed = secrets.randbits(63)
        st.rerun()
    q = QUESTIONS[q_index]
    shuffled = shuffled_choices(q, st.session_state.knowledge_shuffle_seed)
    st.markdown(f"### {q['question']}")
    choice = st.radio(
        "Select one answer",
        shuffled,
        key=f"choice_{q_index}_{st.session_state.knowledge_shuffle_seed}",
        index=None,
    )
    if st.button("Check my reasoning", type="primary"):
        if choice is None:
            st.warning("Select an answer before checking your reasoning.")
        elif choice == q["answer"]:
            st.success("Correct. " + q["explanation"])
        else:
            st.error("Not yet. " + q["explanation"])
            st.write(f"**Best answer:** {q['answer']}")
    st.divider()
    st.subheader("Generated numerical practice")
    mid_strike = float(strikes[len(strikes) // 2])
    instrument = st.selectbox("Generate for", ["Long call", "Long put"])
    kind = "call" if instrument == "Long call" else "put"
    premium = prices[mid_strike][kind]
    generated = generated_question(spot, mid_strike, premium, kind=kind, side="long")
    st.write(generated["prompt"])
    response = st.number_input("Your break-even stock price", min_value=0.0, step=0.5)
    if st.button("Check numerical answer"):
        if abs(response - generated["answer"]) <= 0.02:
            st.success("Correct. " + generated["explanation"])
        else:
            st.warning("Revisit payoff minus premium. " + generated["explanation"])
    why_it_matters("A correct number is only the beginning. Always connect the number to the right or obligation, the bad state being transferred, and the favorable state being preserved.")


st.sidebar.divider()
st.sidebar.caption("Educational use only. Prices are hypothetical Black-Scholes values, not market quotations or investment advice.")
