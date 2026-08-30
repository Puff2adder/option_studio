"""Ungraded conceptual checks and generated practice questions."""

import hashlib
import random

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
    {
        "question": "An investor expects a very large stock-price move after an announcement but does not know the direction. What payoff behavior should the investor seek?",
        "choices": ["Low near the current price and rising in both tails", "Increasing only when the stock rises", "Constant in every state", "High near the current price and falling in both tails"],
        "answer": "Low near the current price and rising in both tails",
        "explanation": "The economic belief concerns magnitude rather than direction. The desired payoff should therefore respond to both large upward and large downward moves.",
    },
    {
        "question": "A target payout's slope changes from 0.25 to 1.00 at strike K. What call quantity creates that slope change?",
        "choices": ["Buy 0.75 calls", "Sell 0.75 calls", "Buy 1.25 calls", "Sell 0.25 calls"],
        "answer": "Buy 0.75 calls",
        "explanation": "A call adds slope only above its strike. The required quantity is the change in slope: 1.00 - 0.25 = +0.75.",
    },
    {
        "question": "Why can a replicated payout be valued by adding the signed market values of its stock, bond, and call positions?",
        "choices": ["Identical future cash flows must have the same value today", "Option premiums are always forecasts", "Risk-neutral probabilities equal physical probabilities", "Every replication has zero cost"],
        "answer": "Identical future cash flows must have the same value today",
        "explanation": "This is the Law of One Price. A different price for two identical state-by-state payouts would create an arbitrage opportunity.",
    },
    {
        "question": "In a calls-only replication, which component establishes a nonzero payout level when the underlying price is zero?",
        "choices": ["The riskless terminal payoff", "A call with a positive strike", "The stock position", "Volatility"],
        "answer": "The riskless terminal payoff",
        "explanation": "Stock and positive-strike calls pay zero when the underlying price is zero. The bond sets the vertical level of the payout.",
    },
    {
        "question": "A long put has strike $100 and costs $7. If the stock finishes at $80, what are the put's payoff and simple profit per share?",
        "choices": ["Payoff $20; profit $13", "Payoff $13; profit $20", "Payoff $20; profit $27", "Payoff $0; profit -$7"],
        "answer": "Payoff $20; profit $13",
        "explanation": "The payoff is max(100-80,0)=$20. Subtracting the $7 premium gives a simple profit of $13 per share.",
    },
    {
        "question": "A payoff diagram has slope +1 below strike K and slope 0 above K. Which call position creates the change in slope at K?",
        "choices": ["Sell one call at K", "Buy one call at K", "Buy one share at K", "Lend K dollars at expiration"],
        "answer": "Sell one call at K",
        "explanation": "The slope falls by one at K. A short call contributes a slope change of -1 above its strike.",
    },
    {
        "question": "A firm wants a terminal procurement payout that is zero below $90 and then rises dollar-for-dollar above $90. Which single option creates that payoff?",
        "choices": ["A long call with strike $90", "A long put with strike $90", "A short call with strike $90", "A short put with strike $90"],
        "answer": "A long call with strike $90",
        "explanation": "A long call pays max(S_T-90,0), matching a zero payout below $90 and slope +1 above $90.",
    },
    {
        "question": "An investor buys a call and a put with the same strike and expiration. Which statement describes the position's terminal payoff?",
        "choices": ["It rises with the absolute distance between the stock price and the strike", "It is positive only when the stock rises", "It is constant at every stock price", "It is largest when the stock finishes exactly at the strike"],
        "answer": "It rises with the absolute distance between the stock price and the strike",
        "explanation": "At expiration, the combined payoff is max(S_T-K,0)+max(K-S_T,0)=|S_T-K|. The premium affects profit, not this payoff shape.",
    },
    {
        "question": "Two portfolios have identical cash flows at expiration in every possible stock-price state. Under the Law of One Price, what must be true today?",
        "choices": ["They must have the same value today", "They must have the same expected return", "They must use the same securities", "They must both have zero value"],
        "answer": "They must have the same value today",
        "explanation": "Identical state-by-state cash flows must carry the same current value in an arbitrage-free market, even if the portfolios use different components.",
    },
    {
        "question": "A company owns stock and buys a put below the current stock price. What risk does the put primarily transfer?",
        "choices": ["Losses below the put strike", "All variation above the put strike", "The initial stock purchase cost", "The obligation to sell a call"],
        "answer": "Losses below the put strike",
        "explanation": "Below the strike, gains on the put offset further declines in the stock. The company retains upside unless another position limits it.",
    },
    {
        "question": "A replicated payout requires 0.40 shares and -0.25 calls at strike K. How should the negative call quantity be interpreted?",
        "choices": ["Write one-quarter of a call per unit of the payout", "Buy one-quarter of a call per unit of the payout", "Ignore the call because fractional positions are invalid", "Borrow one-quarter of the strike price"],
        "answer": "Write one-quarter of a call per unit of the payout",
        "explanation": "A negative option quantity is a short position. Fractional quantities are valid when expressing a payoff per unit or when contracts can be scaled across a larger exposure.",
    },
]


def shuffled_choices(question, shuffle_seed):
    """Return a stable shuffled order for one question and one session seed."""
    material = f"{shuffle_seed}|{question['question']}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    choices = list(question["choices"])
    random.Random(derived_seed).shuffle(choices)
    return choices


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
