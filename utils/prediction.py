# prediction.py
# Uses machine learning to predict month-end expenses based on spending so far.

from sklearn.linear_model import LinearRegression
import numpy as np
from database import get_db_connection
import datetime

def predict_category_spend(user_id, category, month, year):
    """
    Uses Linear Regression to predict how much will be spent in a category by month-end.
    """
    conn = get_db_connection()
    if not conn:
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    # Get all expenses for this user, category, month, year
    query = """
        SELECT DAY(date) as day_num, amount
        FROM transactions
        WHERE user_id = %s AND category = %s AND type = 'expense' 
          AND MONTH(date) = %s AND YEAR(date) = %s
        ORDER BY day_num ASC
    """
    cursor.execute(query, (user_id, category, month, year))
    results = cursor.fetchall()
    conn.close()
    
    # We need at least 3 data points to make a reasonable prediction
    if len(results) < 3:
        return None
        
    # Calculate cumulative sum day by day
    # We will build a list of (day, cumulative_amount)
    daily_spend = {}
    for row in results:
        day = row['day_num']
        daily_spend[day] = daily_spend.get(day, 0) + float(row['amount'])
        
    # Sort days
    days = sorted(daily_spend.keys())
    
    X = []
    Y = []
    cumulative = 0
    
    for day in days:
        cumulative += daily_spend[day]
        X.append([day])  # sklearn expects 2D array for features
        Y.append(cumulative)
        
    # Fit the Linear Regression model
    model = LinearRegression()
    model.fit(X, Y)
    
    # Predict for day 30
    predicted_end = model.predict([[30]])[0]
    
    # Ensure prediction is not less than current spend
    current_spend = Y[-1]
    if predicted_end < current_spend:
        predicted_end = current_spend
        
    # Current day of month calculation
    today = datetime.date.today()
    if today.month == month and today.year == year:
        days_elapsed = today.day
    else:
        days_elapsed = 30 # For past months
        
    return {
        'category': category,
        'days_elapsed': days_elapsed,
        'current_spend': current_spend,
        'predicted_month_end': float(predicted_end),
        'model_used': 'Linear Regression'
    }

def get_all_predictions(user_id, month, year):
    """
    Gets predictions for all categories for the given month and year.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    # Find which categories have expenses this month
    query = """
        SELECT DISTINCT category
        FROM transactions
        WHERE user_id = %s AND type = 'expense' 
          AND MONTH(date) = %s AND YEAR(date) = %s
    """
    cursor.execute(query, (user_id, month, year))
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    
    predictions = []
    for cat in categories:
        pred = predict_category_spend(user_id, cat, month, year)
        if pred:
            predictions.append(pred)
            
    return predictions
