# Q Banks Confluence Strategy for Forex

This skill implements the Q Banks confluence trading methodology for Forex trading.

## Core Principles

1. **Support/Resistance from Wicks**
   - ALWAYS draw S/R from wicks, not candle bodies
   - Market ALWAYS retests wicks
   - Wait for retest before entry

2. **Fibonacci Retracements and Projections**
   - PRZ levels: 38.2%, 61.8%, 78.6%, 88.6%
   - Key level: 61.8% (golden ratio)
   - Projections: -27% for targets (Q Banks favorite)

3. **Harmonic Patterns**
   - Focus on Bat, Gartley, Butterfly, Crab patterns
   - Require specific Fibonacci ratios
   - Look for completion at support/resistance levels

4. **Confluence Required**
   - Minimum 70/100 confluence score
   - Weighted: S/R (30%), Fibs (25%), Candle patterns (20%), Trend lines (15%), Volume (10%)
   - Multiple confirmations before entry

5. **Timeframe Hierarchy**
   - Master ONE pair (e.g., EURUSD) - NO pair-hopping
   - Daily: Major S/R levels (3-5 levels)
   - H4: Intermediate levels (1-3 between daily zones)
   - H1: Entry timeframe and candle patterns
   - M15/M5: Timing and confirmation
   - M1: Precision entry (limit orders)

6. **Entry Rules**
   - Only at S/R levels (from wicks)
   - Price must retest level before entry
   - Require 2-3 confirmations (confluence score >= 70)
   - Use LIMIT orders 1 pip from level for precision
   - Never enter without confluence
   - Never chase price

7. **Risk Management**
   - 1-2% risk per trade maximum
   - Daily loss limit: 5%
   - Stop loss: Below support (for longs) or above resistance (for shorts)
   - Take profit: Next logical level or Fibonacci projection
   - IMMEDIATE documentation after every trade

## Implementation

This skill provides the following functions:

- `calculate_confluence(pair, candle, historical_candles)`: Returns confluence score and details
- `analyze_signal(pair, candle, historical_candles)`: Returns trading signal if confluence >= 70
- `execute_trade(forex_tool, signal)`: Executes the trade using the provided tool
- `document_trade(trade)`: Immediately documents the trade in the journal

## References

- Q Banks Confluence Methodology (from 8-figure trader)
- MetaTrader5 API for Forex trading
- Risk management: 1-2% per trade, daily loss limit 5%

## Usage

Load this skill in the Agent Zero trading system to enable Forex trading with Q Banks methodology.
