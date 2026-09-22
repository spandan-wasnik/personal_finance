# savings_impact.py
# Calculates how predicted overspending affects planned savings.

from database import get_db_connection
from utils.prediction import get_all_predictions

def calculate_savings_impact(user_id, month, year):
    """
    Calculates the impact of predicted overspending on user savings.
    """
    conn = get_db_connection()
    if not conn:
        return {}
        
    cursor = conn.cursor(dictionary=True)
    
    # 1. Get Monthly Income
    cursor.execute("""
        SELECT SUM(amount) as income 
        FROM transactions 
        WHERE user_id = %s AND type = 'income' AND MONTH(date) = %s AND YEAR(date) = %s
    """, (user_id, month, year))
    income_row = cursor.fetchone()
    monthly_income = float(income_row['income']) if income_row and income_row['income'] else 0.0
    
    # 2. Get Overall Budget
    cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    budget_row = cursor.fetchone()
    overall_budget = float(budget_row['amount']) if budget_row else 0.0
    
    # 3. Get Category Budgets
    cursor.execute("SELECT category, budget_amount FROM category_budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    cat_budgets = {row['category']: float(row['budget_amount']) for row in cursor.fetchall()}
    
    conn.close()
    
    # 4. Get Predictions
    predictions = get_all_predictions(user_id, month, year)
    
    planned_savings = monthly_income - overall_budget
    total_overspend = 0.0
    overspending_categories = []
    
    # 5. Calculate Overspend per category
    for pred in predictions:
        cat = pred['category']
        predicted_spend = pred['predicted_month_end']
        
        # If there is a budget for this category
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
                
    savings_at_risk = planned_savings - total_overspend
    
    return {
        'monthly_income': monthly_income,
        'overall_budget': overall_budget,
        'planned_savings': planned_savings,
        'total_overspend': total_overspend,
        'savings_at_risk': savings_at_risk,
        'overspending_categories': overspending_categories
    }
