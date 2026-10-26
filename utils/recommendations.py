
from utils.analysis import get_summary, get_budget_status
from utils.anomaly_detection import get_unusual_transactions

def generate_recommendations(user_id, month, year):
    """Evaluates rules on savings rate, budget usage, and anomalies to give advice."""
    recs = []
    summary = get_summary(user_id, month, year)
    budget = get_budget_status(user_id, month, year)
    anomalies = get_unusual_transactions(user_id)

    rate = summary.get('savings_rate', 0)
    if rate < 20:
        recs.append({'type': 'warning', 'message': f"Savings rate is {rate:.1f}%. Recommended target is at least 20%."})
    elif rate >= 30:
        recs.append({'type': 'success', 'message': f"Great job! Your savings rate is strong at {rate:.1f}%."})

    pct = budget.get('percentage_used', 0)
    if pct > 100:
        recs.append({'type': 'warning', 'message': f"Monthly budget exceeded by ₹{budget['spent'] - budget['budget']:,.0f}!"})
    elif pct > 80:
        recs.append({'type': 'warning', 'message': f"You've used {pct:.1f}% of your monthly budget. Slow down spending."})

    if anomalies:
        recs.append({'type': 'warning', 'message': f"Detected {len(anomalies)} unusual transaction(s). Check the Transactions page."})

    return recs
