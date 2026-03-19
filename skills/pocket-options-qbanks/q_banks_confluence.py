"""
Q Banks Confluence Strategy for Pocket Options
==============================================

Implements the Q Banks confluence trading methodology for binary options trading.
Based on the teachings of 8-figure trader Q Banks from Wall Street Academy.

Core Principles:
1. Support/Resistance from WICKS (not candle bodies)
2. Wait for RETEST before entry (no retest, no entry)
3. Require 2-3 confirmations (confluence score >= 70)
4. Use LIMIT orders for precision (1 pip from level)
5. Risk management: max 1-2% per trade
6. Document EVERY trade immediately
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# We assume BinaryOptionsTools v2 is available in the environment
# In practice, this would be imported from the installed package
# For now, we'll define a mock structure that will be replaced by the actual tool

class QBanksConfluenceStrategy:
    """
    Q Banks Confluence Trading Strategy for Pocket Options
    """

    def __init__(self, min_confluence: int = 70, risk_percentage: float = 0.015):
        """
        Initialize the strategy.

        Args:
            min_confluence: Minimum confluence score to take a trade (0-100)
            risk_percentage: Percentage of account to risk per trade (default 1.5%)
        """
        self.min_confluence = min_confluence
        self.risk_percentage = risk_percentage
        self.support_resistance_levels = {}  # asset -> list of levels
        self.fibonacci_levels = {}  # asset -> fib levels
        self.harmonic_patterns = []  # detected harmonic patterns
        self.trade_journal = []  # list of all trades for documentation

    def calculate_confluence(self, asset: str, candle: Dict, 
                           historical_candles: List[Dict]) -> Tuple[int, Dict]:
        """
        Calculate confluence score (0-100) for the current candle.

        Args:
            asset: Trading symbol (e.g., 'EURUSD_otc')
            candle: Current candle data
            historical_candles: List of historical candles

        Returns:
            Tuple of (confluence_score, details_dict)
        """
        # Initialize factor scores
        factors = {
            'sr_alignment': 0,      # Support/Resistance alignment (max 30)
            'fib_alignment': 0,     # Fibonacci level alignment (max 25)
            'candle_pattern': 0,    # Candle pattern (max 20)
            'trend_line': 0,        # Trend line alignment (max 15)
            'volume': 0             # Volume confirmation (max 10)
        }
        
        details = {}
        current_price = candle['close']

        # 1. Support/Resistance Alignment (30 points max)
        sr_score, sr_details = self._check_sr_alignment(asset, candle, historical_candles)
        factors['sr_alignment'] = min(30, sr_score)
        details['sr'] = sr_details

        # 2. Fibonacci Alignment (25 points max)
        if asset in self.fibonacci_levels:
            fib_score, fib_details = self._check_fib_alignment(asset, candle)
            factors['fib_alignment'] = min(25, fib_score)
            details['fib'] = fib_details

        # 3. Candle Pattern (20 points max)
        pattern_score, pattern_details = self._check_candle_pattern(candle, historical_candles)
        factors['candle_pattern'] = min(20, pattern_score)
        details['pattern'] = pattern_details

        # 4. Trend Line (15 points max)
        trend_score, trend_details = self._check_trend_line(asset, candle, historical_candles)
        factors['trend_line'] = min(15, trend_score)
        details['trend'] = trend_details

        # 5. Volume (10 points max)
        volume_score, volume_details = self._check_volume(candle, historical_candles)
        factors['volume'] = min(10, volume_score)
        details['volume'] = volume_details

        # Calculate total score
        total_score = sum(factors.values())

        return total_score, {
            'factors': factors,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }

    def _check_sr_alignment(self, asset: str, candle: Dict, 
                           historical_candles: List[Dict]) -> Tuple[int, Dict]:
        """Check alignment with support/resistance levels from wicks."""
        if asset not in self.support_resistance_levels:
            return 0, {'levels': [], 'aligned': False}

        levels = self.support_resistance_levels[asset]
        current_price = candle['close']
        tolerance = 0.0005  # 5 pips for 5-digit pricing

        aligned_levels = []
        for level in levels:
            level_price = level['level']
            level_type = level['type']  # 'support' or 'resistance'
            touch_count = level['touch_count']

            # Check if price is near this level (within tolerance)
            if abs(current_price - level_price) < tolerance:
                # Check if this is a retest (not first touch)
                is_retest = self._is_retest(asset, level_price, historical_candles)
                
                if is_retest:
                    # Score based on touch count (more touches = stronger level)
                    # Cap at 30 points for S/R alignment
                    score = min(30, touch_count * 5)
                    aligned_levels.append({
                        'level': level_price,
                        'type': level_type,
                        'touch_count': touch_count,
                        'is_retest': True,
                        'score': score
                    })

        if not aligned_levels:
            return 0, {'levels': [], 'aligned': False}

        # Take the highest score from aligned levels
        best_level = max(aligned_levels, key=lambda x: x['score'])
        return best_level['score'], {
            'levels': aligned_levels,
            'aligned': True,
            'best_level': best_level
        }

    def _is_retest(self, asset: str, level_price: float, 
                  historical_candles: List[Dict]) -> bool:
        """Check if the level has been tested before (retest)."""
        tolerance = 0.0005
        touch_count = 0

        # Look at last 50 candles for touches
        for candle in historical_candles[-50:]:
            # Check for wick touching the level
            high = candle['high']
            low = candle['low']
            
            # Upper wick touching level (resistance retest)
            if abs(high - level_price) < tolerance:
                touch_count += 1
            
            # Lower wick touching level (support retest)
            if abs(low - level_price) < tolerance:
                touch_count += 1

        # Must have been touched at least twice before to be considered a retest
        return touch_count >= 2

    def _check_fib_alignment(self, asset: str, candle: Dict) -> Tuple[int, Dict]:
        """Check alignment with Fibonacci levels."""
        if asset not in self.fibonacci_levels:
            return 0, {'levels': [], 'aligned': False}

        fib_data = self.fibonacci_levels[asset]
        current_price = candle['close']
        tolerance = 0.001  # 1 pip tolerance for fib levels

        aligned_fibs = []
        for level_name, level_price in fib_data['levels'].items():
            if abs(current_price - level_price) < tolerance:
                aligned_fibs.append({
                    'name': level_name,
                    'price': level_price
                })

        if not aligned_fibs:
            return 0, {'levels': [], 'aligned': False}

        # Key levels get more points
        key_levels = {'61.8', '78.6', '88.6'}
        has_key_level = any(f['name'] in key_levels for f in aligned_fibs)

        if has_key_level:
            return 25, {
                'levels': aligned_fibs,
                'aligned': True,
                'key_level': True
            }
        else:
            return 15, {
                'levels': aligned_fibs,
                'aligned': True,
                'key_level': False
            }

    def _check_candle_pattern(self, candle: Dict, 
                            historical_candles: List[Dict]) -> Tuple[int, Dict]:
        """Check for bullish/bearish candle patterns."""
        score = 0
        pattern_type = 'none'
        confirmation = []

        # Need at least 2 candles to form a pattern
        if len(historical_candles) < 1:
            return score, {'pattern': pattern_type, 'confirmation': confirmation, 'score': 0}

        prev_candle = historical_candles[-1]
        curr_candle = candle

        # Calculate body and wicks
        body = abs(curr_candle['close'] - curr_candle['open'])
        upper_wick = curr_candle['high'] - max(curr_candle['open'], curr_candle['close'])
        lower_wick = min(curr_candle['open'], curr_candle['close']) - curr_candle['low']

        # Bullish Engulfing
        if (curr_candle['close'] > curr_candle['open'] and  # current bullish
            prev_candle['close'] < prev_candle['open'] and  # previous bearish
            curr_candle['close'] > prev_candle['open'] and  # current close > prev open
            curr_candle['open'] < prev_candle['close']):    # current open < prev close
            score = 18
            pattern_type = 'bullish_engulfing'
            confirmation.append('Bullish engulfing pattern detected')

        # Bearish Engulfing
        elif (curr_candle['close'] < curr_candle['open'] and  # current bearish
              prev_candle['close'] > prev_candle['open'] and  # previous bullish
              curr_candle['close'] < prev_candle['open'] and  # current close < prev open
              curr_candle['open'] > prev_candle['close']):    # current open > prev close
            score = 18
            pattern_type = 'bearish_engulfing'
            confirmation.append('Bearish engulfing pattern detected')

        # Hammer (bullish reversal)
        elif lower_wick > body * 2 and upper_wick < body * 0.5:
            score = 15
            pattern_type = 'hammer'
            confirmation.append('Hammer pattern detected (bullish reversal)')

        # Shooting Star (bearish reversal)
        elif upper_wick > body * 2 and lower_wick < body * 0.5:
            score = 15
            pattern_type = 'shooting_star'
            confirmation.append('Shooting star pattern detected (bearish reversal)')

        # Doji (indecision)
        elif body < (upper_wick + lower_wick) * 0.1:
            score = 10
            pattern_type = 'doji'
            confirmation.append('Doji pattern detected (market indecision)')

        # Spinning Top
        elif body < (upper_wick + lower_wick) * 0.3:
            score = 5
            pattern_type = 'spinning_top'
            confirmation.append('Spinning top detected')

        return score, {
            'pattern': pattern_type,
            'confirmation': confirmation,
            'score': score
        }

    def _check_trend_line(self, asset: str, candle: Dict, 
                         historical_candles: List[Dict]) -> Tuple[int, Dict]:
        """Check alignment with trend lines."""
        # Simplified trend line check - in practice, this would be more sophisticated
        if len(historical_candles) < 10:
            return 0, {'aligned': False, 'reason': 'Insufficient data'}

        # Calculate simple trend based on last 10 candles
        recent_closes = [c['close'] for c in historical_candles[-10:]]
        if len(recent_closes) < 2:
            return 0, {'aligned': False, 'reason': 'Not enough closes'}

        # Check if trending up or down
        first_half = sum(recent_closes[:5]) / 5
        second_half = sum(recent_closes[5:]) / 5
        
        if second_half > first_half * 1.001:  # Uptrend
            trend = 'up'
            strength = min(15, int((second_half - first_half) / first_half * 1000))
        elif second_half < first_half * 0.999:  # Downtrend
            trend = 'down'
            strength = min(15, int((first_half - second_half) / first_half * 1000))
        else:
            trend = 'sideways'
            strength = 0

        # Check if current price aligns with trend
        current_price = candle['close']
        if trend == 'up' and current_price > recent_closes[-1]:
            return strength, {'aligned': True, 'trend': trend, 'strength': strength}
        elif trend == 'down' and current_price < recent_closes[-1]:
            return strength, {'aligned': True, 'trend': trend, 'strength': strength}
        else:
            return 0, {'aligned': False, 'trend': trend, 'reason': 'Price not aligned with trend'}

    def _check_volume(self, candle: Dict, 
                     historical_candles: List[Dict]) -> Tuple[int, Dict]:
        """Check volume characteristics."""
        if 'volume' not in candle or len(historical_candles) < 10:
            return 5, {'reason': 'No volume data', 'score': 5}  # Neutral score

        current_volume = candle['volume']
        recent_volumes = [c.get('volume', 0) for c in historical_candles[-10:]]
        avg_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0

        if avg_volume == 0:
            return 5, {'reason': 'Zero average volume', 'score': 5}

        volume_ratio = current_volume / avg_volume

        if volume_ratio > 2.0:
            return 10, {
                'aligned': True,
                'reason': 'Very high volume',
                'ratio': volume_ratio,
                'score': 10
            }
        elif volume_ratio > 1.5:
            return 8, {
                'aligned': True,
                'reason': 'High volume',
                'ratio': volume_ratio,
                'score': 8
            }
        elif volume_ratio > 0.5:
            return 5, {
                'aligned': True,
                'reason': 'Normal volume',
                'ratio': volume_ratio,
                'score': 5
            }
        else:
            return 3, {
                'aligned': False,
                'reason': 'Low volume',
                'ratio': volume_ratio,
                'score': 3
            }

    def analyze_signal(self, asset: str, candle: Dict, 
                      historical_candles: List[Dict]) -> Optional[Dict]:
        """
        Analyze market data and generate a trading signal if conditions are met.

        Returns:
            Dict with signal details or None if no signal
        """
        # Calculate confluence score
        confluence_score, details = self.calculate_confluence(asset, candle, historical_candles)

        # Check if we have sufficient confluence
        if confluence_score < self.min_confluence:
            return None

        # Determine trade direction based on S/R level and price action
        sr_details = details.get('details', {}).get('sr', {})
        best_level = sr_details.get('best_level', {})

        if not best_level:
            return None

        level_price = best_level.get('level', 0)
        level_type = best_level.get('type', 'support')
        current_price = candle['close']

        # Determine direction
        if level_type == 'support' and current_price > level_price:
            # Price is above support - bullish bias
            direction = 'call'
            trade_bias = 'bullish'
        elif level_type == 'resistance' and current_price < level_price:
            # Price is below resistance - bearish bias
            direction = 'put'
            trade_bias = 'bearish'
        else:
            # Price is not aligned with the level bias
            return None

        # Calculate entry, stop loss, and take profit
        # For binary options, we use fixed durations instead of SL/TP
        # But we still need to calculate the expected move for confirmation

        # Calculate position size based on risk management
        # This would typically be done by the risk management agent
        # For now, we'll return a fixed amount that will be adjusted by risk management

        signal = {
            'asset': asset,
            'direction': direction,  # 'call' or 'put'
            'entry_price': current_price,
            'confluence_score': confluence_score,
            'trade_bias': trade_bias,
            'level_info': best_level,
            'signal_details': details,
            'timestamp': datetime.now().isoformat(),
            'strategy': 'q_banks_confluence',
            'min_confluence': self.min_confluence,
            'risk_percentage': self.risk_percentage
        }

        return signal

    def update_support_resistance(self, asset: str, candles: List[Dict]):
        """
        Update support and resistance levels based on recent candle data.
        This should be called periodically to refresh S/R levels.

        Args:
            asset: Trading symbol
            candles: List of recent candles (at least 50-100 recommended)
        """
        if asset not in self.support_resistance_levels:
            self.support_resistance_levels[asset] = []

        levels = self.support_resistance_levels[asset]
        new_levels = []

        # Process candles to find significant wicks
        for candle in candles:
            high = candle['high']
            low = candle['low']
            open_price = candle['open']
            close_price = candle['close']
            body = abs(close_price - open_price)

            # Check for significant upper wick (potential resistance)
            upper_wick = high - max(open_price, close_price)
            if upper_wick > body * 0.5:  # Significant wick
                new_levels.append({
                    'level': high,
                    'type': 'resistance',
                    'timestamp': candle.get('timestamp', time.time())
                })

            # Check for significant lower wick (potential support)
            lower_wick = min(open_price, close_price) - low
            if lower_wick > body * 0.5:  # Significant wick
                new_levels.append({
                    'level': low,
                    'type': 'support',
                    'timestamp': candle.get('timestamp', time.time())
                })

        # Merge new levels with existing ones (group nearby levels)
        all_levels = levels + new_levels
        merged_levels = self._merge_nearby_levels(all_levels, tolerance=0.001)

        # Update levels with touch counts (simplified)
        # In practice, we would track touches over time
        for level in merged_levels:
            level['touch_count'] = level.get('touch_count', 0) + 1

        self.support_resistance_levels[asset] = merged_levels

    def _merge_nearby_levels(self, levels: List[Dict], 
                           tolerance: float = 0.001) -> List[Dict]:
        """Merge levels that are within tolerance of each other."""
        if not levels:
            return []

        # Sort by level price
        sorted_levels = sorted(levels, key=lambda x: x['level'])
        merged = []
        current_group = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            if abs(level['level'] - current_group[-1]['level']) < tolerance:
                current_group.append(level)
            else:
                # Merge current group
                merged_level = {
                    'level': sum(l['level'] for l in current_group) / len(current_group),
                    'type': current_group[0]['type'],  # Assume same type in group
                    'timestamp': max(l['timestamp'] for l in current_group),
                    'touch_count': sum(l.get('touch_count', 0) for l in current_group)
                }
                merged.append(merged_level)
                current_group = [level]

        # Don't forget the last group
        if current_group:
            merged_level = {
                'level': sum(l['level'] for l in current_group) / len(current_group),
                'type': current_group[0]['type'],
                'timestamp': max(l['timestamp'] for l in current_group),
                'touch_count': sum(l.get('touch_count', 0) for l in current_group)
            }
            merged.append(merged_level)

        return merged

    def update_fibonacci_levels(self, asset: str, candles: List[Dict]):
        """
        Update Fibonacci levels based on recent swing high/low.

        Args:
            asset: Trading symbol
            candles: List of recent candles
        """
        if len(candles) < 20:
            return

        # Find swing high and low
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]

        swing_high = max(highs)
        swing_low = min(lows)

        # Calculate Fibonacci levels
        diff = swing_high - swing_low
        if diff <= 0:
            return

        self.fibonacci_levels[asset] = {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'levels': {
                '0.0': swing_high,
                '23.6': swing_high - (diff * 0.236),
                '38.2': swing_high - (diff * 0.382),
                '50.0': swing_high - (diff * 0.5),
                '61.8': swing_high - (diff * 0.618),  # Golden ratio
                '78.6': swing_high - (diff * 0.786),
                '88.6': swing_high - (diff * 0.886),
                '100.0': swing_low
            },
            'projections': {
                '-27.0': swing_high + (diff * 0.27),  # Q Banks favorite
                '161.8': swing_low - (diff * 1.618)
            },
            'timestamp': time.time()
        }

    def document_trade(self, trade: Dict) -> Dict:
        """
        Document a trade immediately in the journal (Q Banks rule: non-negotiable).

        Args:
            trade: Trade dictionary to document

        Returns:
            Updated trade dictionary with journal entry
        """
        # Add documentation fields
        trade['journal_entry'] = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': trade.get('trade_id', f"trade_{int(time.time())}"),
            'asset': trade.get('asset'),
            'direction': trade.get('direction'),
            'entry_price': trade.get('entry_price'),
            'confluence_score': trade.get('confluence_score'),
            'signal_details': trade.get('signal_details'),
            'strategy': trade.get('strategy'),
            'risk_percentage': self.risk_percentage,
            'lessons_learned': self._generate_lessons_learned(trade),
            'emotional_state': self._rate_emotional_state(trade)
        }

        # Add to journal
        self.trade_journal.append(trade['journal_entry'])

        # In a real system, this would be saved to a database or file
        # For now, we just keep it in memory and return it
        return trade

    def _generate_lessons_learned(self, trade: Dict) -> str:
        """Generate lessons learned from the trade."""
        confluence = trade.get('confluence_score', 0)
        direction = trade.get('direction', 'unknown')
        asset = trade.get('asset', 'unknown')

        lessons = f"Traded {asset} {direction} with {confluence} confluence. "
        
        if confluence >= 80:
            lessons += "High confluence setup - good trade execution."
        elif confluence >= 70:
            lessons += "Acceptable confluence setup - follow plan."
        else:
            lessons += "Low confluence - avoid similar setups in future."

        return lessons

    def _rate_emotional_state(self, trade: Dict) -> Dict:
        """Rate emotional state during the trade (for journaling)."""
        # In a real system, this would be filled by the trader
        # For now, we return ideal emotional state
        return {
            'fear': 1,      # 0-10 scale (lower is better)
            'confidence': 8, # 0-10 scale (higher is better)
            'discipline': 9, # 0-10 scale (higher is better)
            'patience': 8    # 0-10 scale (higher is better)
        }

    def get_journal(self) -> List[Dict]:
        """Get the trade journal."""
        return self.trade_journal

    def clear_journal(self):
        """Clear the trade journal."""
        self.trade_journal = []
