# recommendations.py
# Generates personalized financial advice based on rules.

from utils.analysis import get_summary, get_budget_status
from utils.savings_impact import calculate_savings_impact
from utils.anomaly_detection import get_unusual_transactions
import datetime

def generate_recommendations(user_id, month, year):
    """
    Creates a list of recommendation messages by applying financial rules.
    """
    recs = []
    
    # Get data needed for rules
    summary = get_summary(user_id, month, year)
    savings_impact = calculate_savings_impact(user_id, month, year)
    budget_status = get_budget_status(user_id, month, year)
    unusual_txs = get_unusual_transactions(user_id)
    
    # Rule 1, 2, 3: Savings Rate
    if 'savings_rate' in summary:
        rate = summary['savings_rate']
        if rate < 20:
            recs.append({
                'type': 'warning',
                'message': f"Your savings rate is {rate:.1f}%. Financial experts recommend saving at least 20% of income. Consider reducing non-essential spending."
            })
        elif 20 <= rate < 30:
            recs.append({
                'type': 'info',
                'message': f"Good job! Your savings rate is {rate:.1f}%. Try to push it above 30% for better financial security."
            })
        else:
            recs.append({
                'type': 'success',
                'message': f"Excellent! Your savings rate is {rate:.1f}%. Keep it up!"
            })
            
    # Rule 4: Predicted Overspending
    if 'overspending_categories' in savings_impact:
        for cat_info in savings_impact['overspending_categories']:
            if cat_info['overspend'] > 0:
                recs.append({
                    'type': 'warning',
                    'message': f"You are projected to overspend on {cat_info['category']} by ₹{cat_info['overspend']:,.0f} this month. Consider reducing {cat_info['category']} spending."
                })
                
    # Rule 5, 6: Overall Budget
    if 'percentage_used' in budget_status:
        pct = budget_status['percentage_used']
        
        today = datetime.date.today()
        # Check if we are currently in the requested month
        if today.month == month and today.year == year:
            if pct > 100:
                amount_exceeded = budget_status['spent'] - budget_status['budget']
                recs.append({
                    'type': 'warning',
                    'message': f"You have exceeded your monthly budget by ₹{amount_exceeded:,.0f}."
                })
            elif pct > 80:
                recs.append({
                    'type': 'warning',
                    'message': f"You have used {pct:.1f}% of your monthly budget. Slow down spending to avoid exceeding your budget."
                })
                
            # Rule 8: Daily Target
            remaining_days = 30 - today.day
            if remaining_days > 0 and budget_status['remaining'] > 0:
                daily_target = budget_status['remaining'] / remaining_days
                recs.append({
                    'type': 'info',
                    'message': f"To stay within budget, try to spend no more than ₹{daily_target:,.0f} per day for the rest of this month."
                })
                
    # Rule 7: Unusual Transactions
    if unusual_txs:
        count = len(unusual_txs)
        recs.append({
            'type': 'warning',
            'message': f"We detected {count} unusual transaction(s). Review them in the Transactions page."
        })
        
    return recs

def generate_category_recommendation(category, budget, predicted, current_spend, days_elapsed):
    """
    Provides a specific recommendation for a single category to get back on track.
    """
    if days_elapsed >= 30:
        return "Month is over."
        
    normal_target = budget / 30.0
    
    remaining_budget = budget - current_spend
    remaining_days = 30 - days_elapsed
    
    # If already exceeded budget
    if remaining_budget <= 0:
        return f"You have already exceeded your {category} budget."
        
    safe_target = remaining_budget / remaining_days
    
    return f"You're spending faster than planned on {category}. Your normal target is ₹{normal_target:.0f}/day. Try spending ₹{safe_target:.0f}/day to stay within budget."
