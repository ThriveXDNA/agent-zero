# Q Banks Confluence Strategy for Pocket Options

This skill implements the Q Banks confluence trading methodology adapted for binary options.

## Core Principles

1. **Support/Resistance from Wicks**
   - ALWAYS draw S/R from wicks, not candle bodies
   - Market ALWAYS retests wicks
   - Wait for retest before entry

2. **Fibonacci Retracements**
   - PRZ levels: 38.2%, 61.8%, 78.6%, 88.6%
   - Key level: 61.8% (golden ratio)
   - Projections: -27% for targets

3. **Confluence Required**
   - Minimum 70/100 confluence score
   - Weighted: S/R (30%), Fibs (25%), Candle patterns (20%), Trend lines (15%), Volume (10%)
   - Multiple confirmations before entry

4. **Risk Management**
   - 1-2% risk per trade maximum
   - Daily loss limit: 5%
   - IMMEDIATE documentation after every trade

5. **Entry Rules**
   - Only at S/R levels
   - Price must retest level
   - 2-3 confirmations required
   - Use limit orders for precision

## Implementation

This skill provides the following functions:

- `calculate_confluence(asset, candle, historical_candles)`: Returns confluence score and details
- `analyze_signal(asset, candle, historical_candles)`: Returns trading signal if confluence >= 70
- `execute_trade(tool, signal)`: Executes the trade using the provided tool
- `document_trade(trade)`: Immediately documents the trade in the journal

## References

- Q Banks Confluence Methodology (from 8-figure trader)
- BinaryOptionsTools v2 for Pocket Options API
- Risk management: 1-2% per trade, daily loss limit 5%

## Usage

Load this skill in the Agent Zero trading system to enable Pocket Options trading with Q Banks methodology.
