"""
Expected Value (EV) Based Trading Strategy for Kalshi
=====================================================

Implements an Expected Value based trading strategy for Kalshi prediction markets.
Based on the principle: Only trade when Expected Value (EV) > 0.

Core Principles:
1. Expected Value is King - Only trade when EV > 0
2. Kelly Criterion Position Sizing - Optimal bet sizing
3. Diversification across event types
4. Liquidity requirements - Only trade liquid contracts
5. Time decay awareness - Adjust strategies based on time to expiration
6. Immediate documentation - Document EVERY trade immediately
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

class EVBasedKalshiStrategy:
    """
    Expected Value (EV) Based Trading Strategy for Kalshi Prediction Markets
    """

    def __init__(self, min_ev: float = 0.01, max_risk_per_trade: float = 0.015,
                 max_event_type_exposure: float = 0.10, min_volume: int = 50):
        """
        Initialize the strategy.

        Args:
            min_ev: Minimum Expected Value to consider a trade (in cents, default 0.01 = $0.01)
            max_risk_per_trade: Maximum risk per trade as fraction of account (default 1.5%)
            max_event_type_exposure: Maximum exposure per event type (default 10%)
            min_volume: Minimum daily volume for consideration (default 50 contracts)
        """
        self.min_ev = min_ev  # Minimum EV in dollars
        self.max_risk_per_trade = max_risk_per_trade
        self.max_event_type_exposure = max_event_type_exposure
        self.min_volume = min_volume
        self.support_resistance_levels = {}  # Not used in Kalshi but kept for interface
        self.fibonacci_levels = {}  # Not used in Kalshi but kept for interface
        self.harmonic_patterns = []  # Not used in Kalshi but kept for interface
        self.trade_journal = []  # List of all trades for documentation
        self.event_type_exposure = {}  # Track current exposure by event type

    def calculate_ev(self, contract: Dict) -> Dict:
        """
        Calculate Expected Value (EV) for a Kalshi contract.

        Args:
            contract: Kalshi contract dictionary with 'price' and other fields

        Returns:
            Dictionary with EV analysis and recommendation
        """
        # Extract price (0-100 representing probability %)
        price = contract.get('price', 50)  # Default to 50 if not available
        
        # Convert price to probability
        probability_yes = price / 100.0
        probability_no = 1.0 - probability_yes
        
        # For a YES contract:
        # - If YES wins: profit = (100 - price) per contract
        # - If YES loses: loss = price per contract
        # For a NO contract (selling YES or buying NO):
        # - If NO wins (YES loses): profit = price per contract
        # - If NO loses (YES wins): loss = (100 - price) per contract
        
        # Calculate EV for buying YES
        ev_yes = (probability_yes * (100 - price)) - (probability_no * price)
        
        # Calculate EV for buying NO (equivalent to selling YES)
        ev_no = (probability_no * price) - (probability_yes * (100 - price))
        
        # The better option is the one with positive EV
        if ev_yes > ev_no:
            ev = ev_yes
            recommendation = 'BUY_YES'  # Buy YES contract
            direction = 'YES'
        else:
            ev = ev_no
            recommendation = 'BUY_NO'   # Buy NO contract (sell YES)
            direction = 'NO'
        
        # Convert EV from cents to dollars (assuming price in cents)
        ev_dollars = ev / 100.0
        
        return {
            'contract_id': contract.get('id', 'unknown'),
            'title': contract.get('title', 'Unknown Contract'),
            'price': price,
            'probability_yes': probability_yes,
            'probability_no': probability_no,
            'ev_cents': ev,  # EV in cents
            'ev_dollars': ev_dollars,  # EV in dollars
            'ev_yes_cents': ev_yes,
            'ev_no_cents': ev_no,
            'recommendation': recommendation,
            'direction': direction,
            'timestamp': datetime.now().isoformat()
        }

    def analyze_opportunities(self, kalshi_data: Dict) -> List[Dict]:
        """
        Analyze market data and identify profitable trading opportunities.

        Args:
            kalshi_data: Dictionary containing markets and contracts data from Kalshi API

        Returns:
            List of opportunity dictionaries sorted by EV descending
        """
        opportunities = []
        
        # Extract markets from data
        markets = kalshi_data.get('markets', [])
        
        for market in markets:
            # Skip markets with insufficient volume
            volume = market.get('volume', 0)
            if volume < self.min_volume:
                continue
                
            # Get contracts for this market
            contracts = market.get('contracts', [])
            
            for contract in contracts:
                # Calculate EV for this contract
                ev_analysis = self.calculate_ev(contract)
                
                # Only consider opportunities with positive EV above threshold
                if ev_analysis['ev_dollars'] >= self.min_ev:
                    # Add market and contract context
                    opportunity = {
                        'market_id': market.get('id'),
                        'market_title': market.get('title'),
                        'event_type': self._get_event_type(market.get('title', '')),
                        'volume': volume,
                        'liquidity': market.get('liquidity', 'unknown'),
                        'bid_ask_spread': market.get('bid_ask_spread', 0),
                        'time_to_expiration': market.get('time_to_expiration', 0),
                        **ev_analysis  # Include all EV analysis fields
                    }
                    opportunities.append(opportunity)
        
        # Sort by EV descending (best opportunities first)
        opportunities.sort(key=lambda x: x['ev_dollars'], reverse=True)
        
        return opportunities

    def _get_event_type(self, market_title: str) -> str:
        """Determine event type from market title."""
        title_lower = market_title.lower()
        
        if any(word in title_lower for word in ['fed', 'federal reserve', 'interest rate', 'powell']):
            return 'politics'
        elif any(word in title_lower for word in ['election', 'president', 'senate', 'house', 'governor', 'mayor']):
            return 'politics'
        elif any(word in title_lower for word in ['gdp', 'employment', 'jobs', 'unemployment', 'inflation', 'cpi', 'ppi', 'retail sales']):
            return 'economics'
        elif any(word in title_lower for word in ['weather', 'temperature', 'precipitation', 'snow', 'rain', 'hurricane']):
            return 'weather'
        elif any(word in title_lower for word in ['sports', 'super bowl', 'world series', 'oscars', 'emmys', 'grammys']):
            return 'entertainment'
        elif any(word in title_lower for word in ['bitcoin', 'ethereum', 'crypto', 'stock', 'market']):
            return 'finance'
        else:
            return 'other'

    def calculate_position_size(self, opportunity: Dict, bankroll: float,
                              current_exposure: Dict[str, float]) -> float:
        """
        Calculate optimal position size using Kelly Criterion or fixed fractional.

        Args:
            opportunity: Opportunity dictionary from analyze_opportunities
            bankroll: Available capital in account
            current_exposure: Current exposure by event type (event_type -> amount)

        Returns:
            Recommended position size in dollars
        """
        # Get EV in dollars
        ev_dollars = opportunity.get('ev_dollars', 0)
        
        if ev_dollars <= 0:
            return 0
        
        # Get probability and payout for Kelly calculation
        price = opportunity.get('price', 50)
        probability = price / 100.0 if opportunity['direction'] == 'YES' else (100 - price) / 100.0
        
        # For binary outcomes: 
        # If WIN: profit = payout_per_contract * quantity
        # If LOSS: loss = quantity (you lose your entire investment)
        # Actually for Kalshi: Each contract is worth $1 if correct, $0 if wrong
        # You buy at price/100 dollars per contract
        
        # Simplified: If you buy at price P (0-100), your cost is P/100 per contract
        # If correct, you get $1 per contract, profit = (1 - P/100)
        # If wrong, you get $0, loss = P/100
        
        cost_per_contract = price / 100.0
        profit_if_correct = 1.0 - cost_per_contract
        loss_if_wrong = cost_per_contract
        
        # Kelly Criterion: f* = (bp - q) / b
        # where b = net odds = profit_if_correct / loss_if_wrong
        # p = probability of winning
        # q = probability of losing = 1 - p
        
        if loss_if_wrong == 0:
            return 0  # Avoid division by zero
            
        b = profit_if_correct / loss_if_wrong
        p = probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Apply maximum risk per trade
        max_risk_amount = bankroll * self.max_risk_per_trade
        kelly_amount = bankroll * max(kelly_fraction, 0)  # Only positive Kelly
        
        # Take the smaller of Kelly amount and max risk amount
        position_size = min(kelly_amount, max_risk_amount)
        
        # Apply event type exposure limits
        event_type = opportunity.get('event_type', 'other')
        current_event_exposure = current_exposure.get(event_type, 0)
        max_event_exposure = bankroll * self.max_event_type_exposure
        remaining_event_exposure = max_event_exposure - current_event_exposure
        
        if remaining_event_exposure < 0:
            # Already over-exposed to this event type
            return 0
            
        position_size = min(position_size, remaining_event_exposure)
        
        # Ensure minimum viable position size (at least $1 for practical purposes)
        position_size = max(position_size, 1.0)
        
        return position_size

    def execute_trade(self, kalshi_client: Any, opportunity: Dict, 
                     amount: float) -> Dict:
        """
        Execute a trade on Kalshi.

        Args:
            kalshi_client: Kalshi API client instance
            opportunity: Opportunity dictionary from analyze_opportunities
            amount: Position size in dollars to invest

        Returns:
            Trade execution result dictionary
        """
        contract_id = opportunity.get('contract_id')
        direction = opportunity.get('direction')  # 'YES' or 'NO'
        price = opportunity.get('price', 50)
        
        # Calculate number of contracts to buy
        cost_per_contract = price / 100.0  # Dollars per contract
        if cost_per_contract == 0:
            return {'success': False, 'error': 'Invalid price'}
            
        quantity = int(amount / cost_per_contract)
        if quantity == 0:
            return {'success': False, 'error': 'Amount too small for single contract'}
        
        actual_cost = quantity * cost_per_contract
        
        # Execute trade via Kalshi API
        # This would be replaced with actual API call in production
        try:
            # Mock implementation - replace with actual Kalshi API call
            # For example: kalshi_client.buy_contract(contract_id, quantity, direction)
            # For now, we simulate the trade
            
            trade_result = {
                'success': True,
                'contract_id': contract_id,
                'quantity': quantity,
                'direction': direction,
                'entry_price': price,
                'entry_time': datetime.now().isoformat(),
                'cost': actual_cost,
                'potential_profit': quantity * (1.0 - cost_per_contract),  # If correct
                'potential_loss': quantity * cost_per_contract,  # If wrong
                'order_id': f"order_{int(time.time())}"
            }
            
            return trade_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'contract_id': contract_id,
                'quantity': quantity,
                'direction': direction,
                'amount': amount
            }

    def document_trade(self, trade: Dict, kalshi_client: Any = None) -> Dict:
        """
        Document a trade immediately in the journal (Kalshi rule: non-negotiable).

        Args:
            trade: Trade dictionary from execute_trade
            kalshi_client: Optional Kalshi client to fetch settlement data

        Returns:
            Updated trade dictionary with journal entry
        """
        # Add documentation fields
        trade['journal_entry'] = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': trade.get('order_id', f"trade_{int(time.time())}"),
            'contract_id': trade.get('contract_id'),
            'title': trade.get('title', 'Unknown Contract'),
            'market_type': trade.get('event_type', 'other'),
            'direction': trade.get('direction'),
            'quantity': trade.get('quantity'),
            'entry_price': trade.get('entry_price'),
            'cost': trade.get('cost'),
            'ev_analysis': {
                'ev_dollars': trade.get('ev_dollars'),
                'recommendation': trade.get('recommendation'),
                'probability_yes': trade.get('probability_yes')
            },
            'strategy': 'ev_based_kalshi',
            'risk_percentage': self.max_risk_per_trade,
            'lessons_learned': self._generate_lessons_learned(trade),
            'emotional_state': self._rate_emotional_state(trade)
        }
        
        # If we have a client and the trade is settled, add outcome
        if kalshi_client and trade.get('status') == 'settled':
            # In practice, we would fetch the actual settlement from Kalshi
            # For now, we'll leave outcome fields empty to be filled later
            trade['journal_entry']['outcome'] = 'pending_settlement'
        elif kalshi_client:
            # For open trades, mark as pending
            trade['journal_entry']['outcome'] = 'open'
        else:
            # No client provided, assume we'll update later
            trade['journal_entry']['outcome'] = 'unknown'
        
        # Add to journal
        self.trade_journal.append(trade['journal_entry'])
        
        # In a real system, this would be saved to a database or file
        # For now, we just keep it in memory and return it
        return trade

    def _generate_lessons_learned(self, trade: Dict) -> str:
        """Generate lessons learned from the trade."""
        ev = trade.get('ev_analysis', {}).get('ev_dollars', 0)
        direction = trade.get('direction', 'unknown')
        title = trade.get('title', 'unknown')
        market_type = trade.get('event_type', 'unknown')
        
        lessons = f"Traded {market_type} contract '{title}' {direction} with EV ${ev:.4f}. "
        
        if ev >= 0.05:  # 5 cents or more
            lessons += "High EV opportunity - excellent trade selection."
        elif ev >= 0.01:  # 1 cent or more
            lessons += "Positive EV trade - follow the model."
        elif ev >= 0:
            lessons += "Break-even EV - review if slippage affected outcome."
        else:
            lessons += "NEGATIVE EV - This should never happen! Review entry criteria."
        
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

    def update_exposure(self, event_type: str, amount: float):
        """Update current exposure for an event type."""
        if event_type not in self.event_type_exposure:
            self.event_type_exposure[event_type] = 0
        self.event_type_exposure[event_type] += amount

    def reduce_exposure(self, event_type: str, amount: float):
        """Reduce exposure for an event type (when position closes)."""
        if event_type in self.event_type_exposure:
            self.event_type_exposure[event_type] = max(0, 
                self.event_type_exposure[event_type] - amount)

    def get_current_exposure(self) -> Dict[str, float]:
        """Get current exposure by event type."""
        return self.event_type_exposure.copy()
