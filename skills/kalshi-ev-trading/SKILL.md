# Expected Value (EV) Based Trading Strategy for Kalshi

This skill implements an Expected Value based trading strategy for Kalshi prediction markets.

## Core Principles

1. **Expected Value is King**
   - Only trade contracts with positive Expected Value (EV > 0)
   - EV = (Probability of Win × Profit if Win) - (Probability of Loss × Loss if Loss)
   - For Kalshi: Probability = Price/100, Profit if Win = (100 - Price), Loss if Loss = Price

2. **Kelly Criterion Position Sizing**
   - Optimal bet size = (bp - q) / b where b = net odds, p = win probability, q = loss probability
   - For Kalshi: Simplified to bet size proportional to EV
   - Maximum risk per trade: 1-2% of account

3. **Diversification**
   - Spread risk across different event types (politics, economics, weather, etc.)
   - Maximum 5-10% exposure per event type
   - Avoid high correlation between positions

4. **Liquidity Requirements**
   - Only trade contracts with sufficient volume and tight bid-ask spreads
   - Minimum daily volume threshold for consideration
   - Prefer contracts with spread < 5 points

5. **Time Decay Awareness**
   - Understand how prices change as expiration approaches
   - Adjust strategies based on time to expiration
   - Be aware of accelerated movement near expiration

6. **Immediate Documentation**
   - Document EVERY trade immediately (within 60 seconds)
   - Record EV analysis, reasoning, emotional state, outcome
   - This is where real learning happens

## Implementation

This skill provides the following functions:

- `calculate_ev(contract)`: Returns Expected Value and recommendation
- `analyze_opportunities(kalshi_tool)`: Returns list of profitable opportunities
- `calculate_position_size(opportunity, bankroll, exposure)`: Returns optimal position size
- `execute_trade(kalshi_tool, opportunity, amount)`: Executes the trade
- `document_trade(trade)`: Immediately documents the trade in the journal

## References

- Kalshi Official API Documentation
- Expected Value Theory
- Kelly Criterion for position sizing
- Risk management: 1-2% per trade, daily loss limit 5%

## Usage

Load this skill in the Agent Zero trading system to enable Kalshi trading with EV-based strategy.
