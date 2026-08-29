"""Ungraded conceptual checks and generated practice questions."""

QUESTIONS = [
    {
        "question": "A manufacturer must buy copper in six months and is harmed by higher copper prices. Which position most directly preserves the benefit of lower prices while limiting the damage from higher prices?",
        "choices": ["Buy a call", "Sell a call", "Buy a put", "Sell the stock"],
        "answer": "Buy a call",
        "explanation": "A long call pays in the high-price states. The firm can still buy at the lower market price if copper falls.",
    },
    {
        "question": "Which statement best distinguishes payoff from profit for a long call?",
        "choices": ["Profit subtracts the premium; payoff does not", "Payoff subtracts the premium; profit does not", "They are always identical", "Profit is calculated only before expiration"],
        "answer": "Profit subtracts the premium; payoff does not",
        "explanation": "The terminal call payoff is max(S_T-K,0). Profit recognizes what was paid for that right.",
    },
    {
        "question": "An investor owns one share and sells one call. What happens above the strike?",
        "choices": ["Stock gains are offset by the short-call obligation", "The downside is eliminated", "Both positions expire worthless", "The investor gains twice as fast"],
        "answer": "Stock gains are offset by the short-call obligation",
        "explanation": "The stock adds slope +1 while the short call adds slope -1 above the strike, producing a flat payoff there.",
    },
    {
        "question": "In a calls-only replication, what does a short call at a strike do to the payoff slope above that strike?",
        "choices": ["Reduces the slope", "Raises the intercept everywhere", "Changes the slope below the strike", "Creates a discontinuous jump"],
        "answer": "Reduces the slope",
        "explanation": "A call has zero slope below its strike and positive slope above it. Shorting the call lowers the portfolio slope above the strike.",
    },
    {
        "question": "Why is the premium received from a short option not free income?",
        "choices": ["It compensates the writer for accepting an obligation", "It must always be returned the next day", "Short options have no terminal payoff", "Only long options can lose money"],
        "answer": "It compensates the writer for accepting an obligation",
        "explanation": "The writer receives cash today because unfavorable future states can require a payment or delivery obligation.",
    },
    {
        "question": "What does selling the higher-strike call in a call spread surrender?",
        "choices": ["Protection in the most extreme high-price states", "All protection immediately", "The premium on the lower-strike call", "The right to benefit from lower spot prices"],
        "answer": "Protection in the most extreme high-price states",
        "explanation": "The long lower-strike call protects first. Above the higher strike, the short call offsets additional gains from the long call.",
    },
]


def generated_question(spot, strike, premium, kind="call", side="long"):
    if kind == "call" and side == "long":
        break_even = strike + premium
        return {
            "prompt": f"A European call has strike {strike:g} and costs {premium:.2f}. At what expiration stock price does its simple profit first reach zero?",
            "answer": break_even,
            "explanation": f"For a long call, max(S_T-{strike:g},0)-{premium:.2f}=0, so the break-even price is {break_even:.2f}.",
        }
    if kind == "put" and side == "long":
        break_even = strike - premium
        return {
            "prompt": f"A European put has strike {strike:g} and costs {premium:.2f}. What is its simple-profit break-even stock price at expiration?",
            "answer": break_even,
            "explanation": f"For a long put, max({strike:g}-S_T,0)-{premium:.2f}=0, so break-even is {break_even:.2f}.",
        }
    raise ValueError("Unsupported generated-question type.")
