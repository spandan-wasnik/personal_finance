# savings_impact.py
# SPANDAN'S MODULE: Savings Impact & Risk Analysis
#
# Hey bro, this file calculates how much of your future savings is in danger!
# If the ML model says you're gonna overspend on Food by ₹2,000,
# that ₹2,000 comes directly out of your planned savings.
#
# Syllabus Mapping from Work Distribution Sheet:
# - Assigned to: Spandan
# - DBMS: Fetching monthly income, overall budget, and category budgets
# - DSA: Dictionary lookup for category budgets O(1), list filtering of overspending categories
# - PS OOP: SavingsImpactAnalyzer class
# - Statistics: Planned savings = income - budget; Savings at risk = planned savings - total overspend

from database import get_db_connection
from utils.prediction import get_all_predictions


class SavingsImpactAnalyzer:
    """
    PS OOP Class by Spandan:
    Encapsulates savings calculations, budget impact, and risk analysis.
    """
    def __init__(self, user_id):
        self.user_id = user_id

    def compute_impact(self, month, year):
        """Calculates overspending impact and savings at risk."""
        return calculate_savings_impact(self.user_id, month, year)


def calculate_savings_impact(user_id, month, year):
    """
    SPANDAN'S PART:
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
