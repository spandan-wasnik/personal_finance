# prediction.py - KEDAR'S MODULE: Linear Regression Spending Prediction (Y = mX + c)
import datetime
from sklearn.linear_model import LinearRegression
from database import get_db_connection

def predict_category_spend(user_id, category, month, year):
    """Fits Linear Regression on daily cumulative spending and projects Day 30 spend."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DAY(date) as day_num, amount FROM transactions
        WHERE user_id = %s AND category = %s AND type = 'expense' AND MONTH(date) = %s AND YEAR(date) = %s
        ORDER BY day_num ASC
    """, (user_id, category, month, year))
    results = cursor.fetchall()
    conn.close()

    if len(results) < 3: return None  # Need at least 3 points for a line

    daily = {}
    for r in results:
        daily[r['day_num']] = daily.get(r['day_num'], 0) + float(r['amount'])

    days = sorted(daily.keys())
    X, Y = [], []
    cum = 0
    for d in days:
        cum += daily[d]
        X.append([d])
        Y.append(cum)

    # ML: Fit Y = mX + c
    model = LinearRegression().fit(X, Y)
    predicted = max(float(model.predict([[30]])[0]), Y[-1])

    return {
        'category': category,
        'current_spend': Y[-1],
        'predicted_month_end': round(predicted, 2)
    }

def get_all_predictions(user_id, month, year):
    """Predicts month-end spend for all active categories."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM transactions WHERE user_id = %s AND type = 'expense' AND MONTH(date) = %s AND YEAR(date) = %s", (user_id, month, year))
    cats = [r['category'] for r in cursor.fetchall()]
    conn.close()

    preds = []
    for c in cats:
        p = predict_category_spend(user_id, c, month, year)
        if p: preds.append(p)
    return preds
