
from database import get_db_connection
from utils.prediction import get_all_predictions


class SavingsImpactAnalyzer:
    """
    Encapsulates savings calculations, budget impact, and risk analysis.
    """
    def __init__(self, user_id):
        self.user_id = user_id

    def compute_impact(self, month, year):
        """Calculates overspending impact and savings at risk."""
        return calculate_savings_impact(self.user_id, month, year)


def calculate_savings_impact(user_id, month, year):
    """
    Calculates:
    - Planned savings (income - overall budget)
    - Projected overspend across all categories
    - Savings at risk (what's left of savings after overspend)
    """
    conn = get_db_connection()
    if not conn:
        return {}
        
    cursor = conn.cursor(dictionary=True)
    
    # 1. DBMS: Get Monthly Income
    cursor.execute("""
        SELECT SUM(amount) as income 
        FROM transactions 
        WHERE user_id = %s AND type = 'income' AND MONTH(date) = %s AND YEAR(date) = %s
    """, (user_id, month, year))
    income_row = cursor.fetchone()
    monthly_income = float(income_row['income']) if income_row and income_row['income'] else 0.0
    
    # 2. DBMS: Get Overall Budget limit
    cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    budget_row = cursor.fetchone()
    overall_budget = float(budget_row['amount']) if budget_row else 0.0
    
    # 3. DBMS & DSA: Get Category Budgets into a fast lookup dictionary
    cursor.execute("SELECT category, budget_amount FROM category_budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    cat_budgets = {row['category']: float(row['budget_amount']) for row in cursor.fetchall()}
    
    conn.close()
    
    # 4. Fetch ML predictions from Kedar's module
    predictions = get_all_predictions(user_id, month, year)
    
    # Basic math
    planned_savings = monthly_income - overall_budget
    total_overspend = 0.0
    overspending_categories = []
    
    # 5. Check which categories are projected to cross their budget
    for pred in predictions:
        cat = pred['category']
        predicted_spend = pred['predicted_month_end']
        
        if cat in cat_budgets:
            cat_budget = cat_budgets[cat]
            if predicted_spend > cat_budget:
                overspend = predicted_spend - cat_budget
                total_overspend += overspend
                overspending_categories.append({
                    'category': cat,
                    'budget': cat_budget,
                    'predicted': predicted_spend,
                    'overspend': overspend
                })
                
    # STATS: Calculate remaining savings
    savings_at_risk = planned_savings - total_overspend
    
    return {
        'monthly_income': monthly_income,
        'overall_budget': overall_budget,
        'planned_savings': planned_savings,
        'total_overspend': total_overspend,
        'savings_at_risk': savings_at_risk,
        'overspending_categories': overspending_categories
    }


def calculate_goal_acceleration_plan(user_id, target_amount, current_amount, monthly_contribution):
    """
    Computes baseline vs. accelerated timeline for a financial goal by identifying
    practical cuts from discretionary spending categories (e.g. Entertainment, Shopping, Food).
    """
    import math
    rem = max(0.0, float(target_amount) - float(current_amount))
    contrib = max(0.0, float(monthly_contribution or 0))

    if rem <= 0:
        return {
            'is_achieved': True,
            'remaining_amount': 0,
            'baseline_months': 0,
            'accelerated_months': 0,
            'months_saved': 0,
            'total_monthly_cuts': 0,
            'category_cuts': []
        }

    baseline_months = math.ceil(rem / contrib) if contrib > 0 else 0

    # 1. Fetch user's historical discretionary spending
    user_category_spends = {}
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT category, 
                       SUM(amount) as total_spent, 
                       COUNT(DISTINCT CONCAT(YEAR(date), '-', MONTH(date))) as month_count
                FROM transactions 
                WHERE user_id = %s AND type = 'expense'
                  AND category IN ('Entertainment', 'Shopping', 'Food', 'Travel', 'Other')
                GROUP BY category
            """, (user_id,))
            rows = cursor.fetchall()
            for r in rows:
                m_cnt = max(1, r.get('month_count') or 1)
                user_category_spends[r['category']] = float(r.get('total_spent') or 0) / m_cnt
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    # 2. Benchmarks and cut percentages
    benchmarks = {
        'Entertainment': {'default_spend': 2000.0, 'pct': 0.30, 'tip': 'Reduce cinema outings & extra streaming subscriptions'},
        'Shopping': {'default_spend': 3000.0, 'pct': 0.25, 'tip': 'Trim non-essential online retail and impulse shopping'},
        'Food': {'default_spend': 3500.0, 'pct': 0.20, 'tip': 'Cut 2 restaurant dinners or food delivery orders per month'},
        'Travel': {'default_spend': 1500.0, 'pct': 0.20, 'tip': 'Postpone non-essential weekend leisure trips'},
        'Other': {'default_spend': 1000.0, 'pct': 0.15, 'tip': 'Optimize miscellaneous cash and online spending'}
    }

    category_cuts = []
    total_cuts = 0.0

    # If user has recorded transactions in discretionary categories, use them
    if user_category_spends:
        for cat in ['Entertainment', 'Shopping', 'Food', 'Travel', 'Other']:
            spend = user_category_spends.get(cat, 0.0)
            if spend >= 100:
                cfg = benchmarks.get(cat, {'pct': 0.20, 'tip': f'Cut discretionary expenses in {cat}'})
                pct = cfg['pct']
                cut = round((spend * pct) / 50) * 50
                cut = max(50.0, cut)
                if cut < spend:
                    category_cuts.append({
                        'category': cat,
                        'current_monthly': round(spend),
                        'cut_amount': round(cut),
                        'cut_percent': int(pct * 100),
                        'tip': cfg['tip']
                    })
                    total_cuts += cut

    # If user has no transactions in discretionary categories yet, use smart baselines
    if not category_cuts:
        for cat in ['Entertainment', 'Shopping', 'Food']:
            cfg = benchmarks[cat]
            spend = cfg['default_spend']
            cut = round(spend * cfg['pct'])
            category_cuts.append({
                'category': cat,
                'current_monthly': round(spend),
                'cut_amount': round(cut),
                'cut_percent': int(cfg['pct'] * 100),
                'tip': cfg['tip']
            })
            total_cuts += cut

    accelerated_contrib = contrib + total_cuts
    accelerated_months = math.ceil(rem / accelerated_contrib) if accelerated_contrib > 0 else 0
    months_saved = max(0, baseline_months - accelerated_months) if baseline_months > 0 else 0

    return {
        'is_achieved': False,
        'remaining_amount': rem,
        'baseline_months': baseline_months,
        'baseline_contribution': contrib,
        'accelerated_months': accelerated_months,
        'accelerated_contribution': accelerated_contrib,
        'months_saved': months_saved,
        'total_monthly_cuts': total_cuts,
        'category_cuts': category_cuts
    }
