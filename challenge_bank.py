"""Problem banks for payoff design and calls-only replication.

The student-facing prompts deliberately avoid named-strategy menus.  Each
problem begins with an economic belief, exposure, or contract and asks the
student to construct the required payoff from signed component positions.
"""

from __future__ import annotations

import numpy as np


def _option(kind: str, strike: float, quantity: float) -> dict[str, float | str]:
    return {"kind": kind, "strike": float(strike), "quantity": float(quantity)}


def strategy_design_challenges(spot: float, strikes: list[float]) -> list[dict]:
    """Return open-construction problems and one representative exact payoff."""
    if len(strikes) < 7:
        raise ValueError("At least seven strikes are required for the challenge bank.")
    outer_low, low = float(strikes[1]), float(strikes[2])
    middle = float(strikes[len(strikes) // 2])
    high, outer_high = float(strikes[-3]), float(strikes[-2])

    return [
        {
            "id": "earnings_jump",
            "title": "An earnings announcement could move the stock sharply",
            "difficulty": "Foundation",
            "setting": (
                f"The stock is near ${spot:.2f}. An investor believes an imminent earnings announcement "
                "will cause a large move up or down. A price close to its current level at expiration is "
                "viewed as unlikely. Construct a position using calls and puts that expresses this belief."
            ),
            "payoff_goal": (
                f"The terminal payoff should be smallest near ${middle:g} and should rise as the stock "
                "moves far above or far below that level."
            ),
            "questions": [
                "Which option benefits from a large upward move?",
                "Which option benefits from a large downward move?",
                "What happens to profit if the stock finishes close to the common strike?",
            ],
            "tips": [
                "Begin with zero stock and zero riskless payoff. Concentrate on one call and one put.",
                f"Use the same strike, K = {middle:g}, so both rights are centered on the current stock price.",
                "Both option quantities should be positive: the investor is buying two rights, not accepting obligations.",
            ],
            "solution": {
                "stock": 0.0,
                "bond": 0.0,
                "positions": [_option("call", middle, 1.0), _option("put", middle, 1.0)],
            },
            "interpretation": (
                "The investor pays two premiums and therefore loses money if the anticipated move does not occur. "
                "Large moves in either direction can overcome that initial cost."
            ),
        },
        {
            "id": "wide_event_window",
            "title": "Only a move outside a wide range is considered meaningful",
            "difficulty": "Foundation",
            "setting": (
                f"A regulatory decision is expected soon. The stock currently trades near ${spot:.2f}. "
                f"The investor wants exposure only if the price finishes below ${low:g} or above ${high:g}; "
                "moves inside that range are considered economically unimportant."
            ),
            "payoff_goal": (
                f"Create zero payoff between ${low:g} and ${high:g}, with payoff increasing as the stock "
                "moves farther into either tail."
            ),
            "questions": [
                "Which strike should begin downside participation?",
                "Which strike should begin upside participation?",
                "Why must both chosen options be purchased rather than written?",
            ],
            "tips": [
                "Use one put to respond below the lower boundary and one call to respond above the upper boundary.",
                f"The relevant strikes are {low:g} and {high:g}.",
                "Leave the stock and riskless payoff at zero and enter +1 for each option right.",
            ],
            "solution": {
                "stock": 0.0,
                "bond": 0.0,
                "positions": [_option("put", low, 1.0), _option("call", high, 1.0)],
            },
            "interpretation": (
                "Moving the strikes apart lowers the range in which either option pays, but it also changes the "
                "premiums and the size of the move required before the position becomes profitable."
            ),
        },
        {
            "id": "portfolio_floor_cap",
            "title": "Protect a portfolio while financing part of the insurance",
            "difficulty": "Intermediate",
            "setting": (
                f"An investor owns one unit of a stock currently worth ${spot:.2f}. The investor wants a terminal "
                f"floor of ${low:g}, but is willing to give up stock value above ${high:g} to help pay for the protection."
            ),
            "payoff_goal": (
                f"The combined terminal value should be flat below ${low:g}, follow the stock between "
                f"${low:g} and ${high:g}, and be flat again above ${high:g}."
            ),
            "questions": [
                "Which existing position creates slope +1 in the middle region?",
                "Which purchased right removes downside slope below the floor?",
                "Which written obligation removes upside slope above the cap?",
            ],
            "tips": [
                "Start with the one unit of stock already owned.",
                f"Buy downside protection at {low:g} and sell an upside right at {high:g}.",
                "The option quantities are +1 for the put and -1 for the call.",
            ],
            "solution": {
                "stock": 1.0,
                "bond": 0.0,
                "positions": [_option("put", low, 1.0), _option("call", high, -1.0)],
            },
            "interpretation": (
                "The investor has exchanged some favorable high-price states for cheaper downside protection. "
                "The written call is an obligation, not free premium income."
            ),
        },
        {
            "id": "moderate_upside",
            "title": "Benefit from a moderate increase, but not from an extreme increase",
            "difficulty": "Intermediate",
            "setting": (
                f"An investor expects the stock to rise above ${low:g}, but sees little additional economic value "
                f"in gains beyond ${high:g}. The investor wants no terminal payoff if the stock remains below ${low:g}."
            ),
            "payoff_goal": (
                f"The payoff should be zero below ${low:g}, rise one-for-one between ${low:g} and ${high:g}, "
                f"and remain constant above ${high:g}."
            ),
            "questions": [
                "Which option starts the positive slope?",
                "Which option removes that slope at the upper boundary?",
                "What upside is surrendered in exchange for the premium received?",
            ],
            "tips": [
                f"Buy a call at the lower boundary, K = {low:g}.",
                f"A written call at K = {high:g} removes the slope above the upper boundary.",
                "Use quantities +1 and -1, with no stock or bond position.",
            ],
            "solution": {
                "stock": 0.0,
                "bond": 0.0,
                "positions": [_option("call", low, 1.0), _option("call", high, -1.0)],
            },
            "interpretation": (
                "The higher-strike written call reduces the initial cost because the investor gives another party "
                "the right to the most extreme upside states."
            ),
        },
        {
            "id": "bounded_two_tail",
            "title": "Seek exposure to a large move while limiting the terminal payoff",
            "difficulty": "Advanced",
            "setting": (
                "A biotechnology event could move the stock substantially in either direction. The investor wants "
                "two-tail exposure but has a fixed payoff target and is willing to surrender additional gains after "
                "the stock moves beyond outer boundaries."
            ),
            "payoff_goal": (
                f"Payoff should be zero between ${low:g} and ${high:g}, rise in either tail, and stop rising "
                f"below ${outer_low:g} or above ${outer_high:g}."
            ),
            "questions": [
                "Which two purchased options begin the tail payoffs?",
                "Which two written options stop the payoff from increasing farther out?",
                "How does selling the outer options change both cost and extreme-state protection?",
            ],
            "tips": [
                f"Begin with a long put at {low:g} and a long call at {high:g}.",
                f"Use a written put at {outer_low:g} and a written call at {outer_high:g} to flatten the outer tails.",
                "All four option quantities have magnitude one; purchased rights are positive and written obligations are negative.",
            ],
            "solution": {
                "stock": 0.0,
                "bond": 0.0,
                "positions": [
                    _option("put", low, 1.0),
                    _option("put", outer_low, -1.0),
                    _option("call", high, 1.0),
                    _option("call", outer_high, -1.0),
                ],
            },
            "interpretation": (
                "The outer written options lower the initial premium but cap the payoff in the most extreme states. "
                "This is a direct exchange of tail protection for a lower cost today."
            ),
        },
        {
            "id": "range_belief_obligations",
            "title": "Express a belief that the stock will remain inside a range",
            "difficulty": "Advanced",
            "setting": (
                f"An investor believes the stock will remain between ${low:g} and ${high:g} through expiration. "
                "The investor wants to receive premium today and accepts that the belief may be wrong."
            ),
            "payoff_goal": (
                f"The option payoff should be zero inside ${low:g}–${high:g} and negative outside the range. "
                "The profit line should include the premiums received today."
            ),
            "questions": [
                "Which option obligations create losses below and above the range?",
                "Why can the payoff be zero while profit is positive inside the range?",
                "Which tail creates potentially unlimited loss?",
            ],
            "tips": [
                "Receiving premium means the option quantities must be negative.",
                f"Write a put at {low:g} and a call at {high:g}.",
                "The written call creates unbounded loss as the terminal stock price rises; inspect the graph beyond the displayed range.",
            ],
            "solution": {
                "stock": 0.0,
                "bond": 0.0,
                "positions": [_option("put", low, -1.0), _option("call", high, -1.0)],
            },
            "interpretation": (
                "Premium is compensation for accepting obligations. A quiet outcome produces the premium income, "
                "but a sufficiently large move can create losses far greater than the amount received."
            ),
        },
    ]


def replication_challenges(spot: float, strikes: list[float], nodes: np.ndarray) -> list[dict]:
    """Return economically motivated continuous piecewise-linear payouts."""
    if len(strikes) < 7:
        raise ValueError("At least seven strikes are required for the challenge bank.")
    x = np.asarray(nodes, dtype=float)
    low = float(strikes[2])
    middle = float(strikes[len(strikes) // 2])
    high = float(strikes[-3])

    guarantee = float(spot)
    acquisition = np.where(
        x < low,
        guarantee / low * x,
        np.where(x <= high, guarantee, guarantee + 0.5 * (x - high)),
    )
    debt_face = middle
    conversion_ratio = 0.75
    convertible_face = conversion_ratio * middle
    protected_principal = 0.80 * spot
    participation = 0.60
    earnout_base = 0.30 * spot
    earnout_share = 2.0 / 3.0
    salary = 0.25 * spot

    return [
        {
            "id": "acquisition_collar",
            "title": "Stock-financed acquisition collar",
            "difficulty": "Intermediate",
            "story": (
                f"Target shareholders participate in the acquirer's stock below ${low:g}, receive ${guarantee:g} "
                f"from ${low:g} through ${high:g}, and regain 50% participation above ${high:g}."
            ),
            "decision": "Replicate the negotiated consideration and determine its no-arbitrage value today.",
            "values": acquisition,
            "interpretation": (
                "The flat interval protects the negotiated dollar value. Below and above the collar, target "
                "shareholders again bear part of the acquirer's stock-price risk."
            ),
        },
        {
            "id": "risky_debt",
            "title": "Simplified risky corporate debt",
            "difficulty": "Foundation",
            "story": (
                f"A firm owes ${debt_face:g} at maturity. Debtholders receive the promised amount when firm asset "
                "value is sufficient, but receive the remaining asset value in default."
            ),
            "decision": "Replicate min(V_T, face value) using the firm's assets and calls, then value the debt.",
            "values": np.minimum(x, debt_face),
            "interpretation": (
                "Risky debt is the firm's asset value with the most favorable states transferred to equity once "
                "asset value exceeds the promised payment."
            ),
        },
        {
            "id": "convertible_note",
            "title": "A simplified convertible note",
            "difficulty": "Intermediate",
            "story": (
                f"The investor is promised ${convertible_face:.2f} at maturity but may instead receive "
                f"{conversion_ratio:g} shares. Conversion becomes attractive when the stock exceeds ${middle:g}."
            ),
            "decision": "Replicate the better of the promised payment and the conversion value, then value the note.",
            "values": np.maximum(convertible_face, conversion_ratio * x),
            "interpretation": (
                "The note combines a riskless promised payment with an option to participate in sufficiently high "
                "stock-price outcomes."
            ),
        },
        {
            "id": "protected_participation",
            "title": "Capital protection with partial upside participation",
            "difficulty": "Foundation",
            "story": (
                f"A structured investment promises ${protected_principal:.2f} at maturity and adds "
                f"{participation:.0%} of stock gains above ${middle:g}."
            ),
            "decision": "Construct the protected payoff and calculate what the promise should cost today.",
            "values": protected_principal + participation * np.maximum(x - middle, 0.0),
            "interpretation": (
                "Capital protection comes from the riskless payoff. Upside participation is purchased separately "
                "through calls and is therefore less than one-for-one."
            ),
        },
        {
            "id": "capped_earnout",
            "title": "Capped acquisition earnout",
            "difficulty": "Intermediate",
            "story": (
                f"A seller receives ${earnout_base:.2f} for certain, plus {earnout_share:.0%} of performance above "
                f"${low:g}. The additional payment stops increasing after performance reaches ${high:g}."
            ),
            "decision": "Replicate the base payment and capped earnout, then compute its value today.",
            "values": (
                earnout_base
                + earnout_share * np.maximum(x - low, 0.0)
                - earnout_share * np.maximum(x - high, 0.0)
            ),
            "interpretation": (
                "The base payment establishes value in every state. The first call creates performance sensitivity, "
                "and the written higher-strike call caps the seller's additional consideration."
            ),
        },
        {
            "id": "executive_compensation",
            "title": "Salary, stock ownership, and performance incentives",
            "difficulty": "Advanced",
            "story": (
                f"An executive receives a fixed terminal payment of ${salary:.2f}, 0.25 shares, and additional "
                f"option-based incentives once the stock exceeds ${middle:g}."
            ),
            "decision": "Infer the fractional stock and call positions from the payout slopes and value the package.",
            "values": salary + 0.25 * x + 1.50 * np.maximum(x - middle, 0.0),
            "interpretation": (
                "Stock ownership creates sensitivity in every state. The option grant makes compensation much more "
                "sensitive to performance above the strike."
            ),
        },
        {
            "id": "procurement_band",
            "title": "Procurement protection with a premium budget",
            "difficulty": "Intermediate",
            "story": (
                f"A manufacturer wants a cost offset when an input price rises above ${low:g}, but will surrender "
                f"additional protection once the price exceeds ${high:g} to reduce the premium."
            ),
            "decision": "Replicate the terminal cost offset and determine the no-arbitrage premium today.",
            "values": np.maximum(x - low, 0.0) - np.maximum(x - high, 0.0),
            "interpretation": (
                "The higher-strike written call finances part of the purchased protection by returning the most "
                "extreme high-price states to the option writer."
            ),
        },
        {
            "id": "revenue_floor",
            "title": "Revenue shortfall guarantee",
            "difficulty": "Advanced",
            "story": (
                f"A producer receives a payment equal to any shortfall below ${middle:g}. The payment is zero when "
                "the market price finishes at or above the guaranteed level."
            ),
            "decision": "Use only a riskless payoff, the underlying, and calls to reproduce the shortfall payment.",
            "values": np.maximum(middle - x, 0.0),
            "interpretation": (
                "Although the contract looks like downside insurance, it can be decomposed using a riskless promise, "
                "a short underlying position, and a call. This is a calls-only form of payoff parity."
            ),
        },
    ]

