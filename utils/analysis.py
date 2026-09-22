# analysis.py
# This file contains functions to get financial summaries using MySQL queries.

from database import get_db_connection

def get_summary(user_id, month=None, year=None):
    """
    Gets total income, expenses, and balance.
    Can filter by month and year if provided.
    """
    conn = get_db_connection()
    if not conn:
        return {}
        
    cursor = conn.cursor(dictionary=True)
    
    # Base query for totals
    query = """
        SELECT 
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expenses,
            SUM(CASE WHEN payment_mode IN ('UPI', 'Card', 'Bank Transfer') AND type='income' THEN amount 
                     WHEN payment_mode IN ('UPI', 'Card', 'Bank Transfer') AND type='expense' THEN -amount ELSE 0 END) as online_balance,
            SUM(CASE WHEN payment_mode = 'Cash' AND type='income' THEN amount 
                     WHEN payment_mode = 'Cash' AND type='expense' THEN -amount ELSE 0 END) as cash_balance
        FROM transactions 
        WHERE user_id = %s
    """
    params = [user_id]
    
    if month and year:
        query += " AND MONTH(date) = %s AND YEAR(date) = %s"
        params.extend([month, year])
        
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    
    conn.close()
    
    income = float(result['total_income'] or 0)
    expenses = float(result['total_expenses'] or 0)
    online_balance = float(result['online_balance'] or 0)
    cash_balance = float(result['cash_balance'] or 0)
    
    balance = income - expenses
    savings = balance
    savings_rate = (savings / income * 100) if income > 0 else 0.0
    
    return {
        'total_income': income,
        'total_expenses': expenses,
        'balance': balance,
        'online_balance': online_balance,
        'cash_balance': cash_balance,
        'savings': savings,
        'savings_rate': savings_rate
    }

def get_monthly_expenses(user_id, num_months=12):
    """
    Gets the total expenses for the last N months.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            MONTH(date) as month, 
            YEAR(date) as year, 
            MONTHNAME(date) as month_name, 
            SUM(amount) as total
        FROM transactions
        WHERE user_id = %s AND type = 'expense'
        GROUP BY year, month, month_name
        ORDER BY year DESC, month DESC
        LIMIT %s
    """
    cursor.execute(query, (user_id, num_months))
    results = cursor.fetchall()
    
    conn.close()
    
    # Reverse to show chronological order
    results.reverse()
    
    for row in results:
        row['total'] = float(row['total'] or 0)
        
    return results

def get_category_expenses(user_id, month=None, year=None):
    """
    Gets spending broken down by category.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            category, 
            SUM(amount) as total, 
            COUNT(*) as count
        FROM transactions
        WHERE user_id = %s AND type = 'expense'
    """
    params = [user_id]
    
    if month and year:
        query += " AND MONTH(date) = %s AND YEAR(date) = %s"
        params.extend([month, year])
        
    query += " GROUP BY category ORDER BY total DESC"
    
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    
    conn.close()
    
    for row in results:
        row['total'] = float(row['total'] or 0)
        
    return results

def get_recent_transactions(user_id, limit=10):
    """
    Gets the most recent transactions for the user.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT * FROM transactions
        WHERE user_id = %s
        ORDER BY date DESC, id DESC
        LIMIT %s
    """
    cursor.execute(query, (user_id, limit))
    results = cursor.fetchall()
    
    conn.close()
    
    # Convert amounts to float
    for row in results:
        row['amount'] = float(row['amount'])
        row['date'] = str(row['date']) # Convert date to string for easy JSON serializing if needed
        row['created_at'] = str(row['created_at'])
        
    return results

def get_budget_status(user_id, month, year):
    """
    Checks total expenses against the monthly budget.
    """
    conn = get_db_connection()
    if not conn:
        return {'budget': 0.0, 'spent': 0.0, 'remaining': 0.0, 'percentage_used': 0.0}
        
    cursor = conn.cursor(dictionary=True)
    
    # Get budget
    cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    budget_row = cursor.fetchone()
    budget = float(budget_row['amount']) if budget_row else 0.0
    
    # Get total spent
    cursor.execute("SELECT SUM(amount) as spent FROM transactions WHERE user_id = %s AND type = 'expense' AND MONTH(date) = %s AND YEAR(date) = %s", (user_id, month, year))
    spent_row = cursor.fetchone()
    spent = float(spent_row['spent']) if spent_row and spent_row['spent'] else 0.0
    
    conn.close()
    
    remaining = budget - spent
    percentage_used = (spent / budget * 100) if budget > 0 else 0.0
    
    return {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'percentage_used': percentage_used
    }

def get_income_expense_trend(user_id, num_months=6):
    """
    Gets income and expenses month-by-month for trend analysis.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            MONTH(date) as month, 
            YEAR(date) as year, 
            MONTHNAME(date) as month_name, 
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses
        FROM transactions
        WHERE user_id = %s
        GROUP BY year, month, month_name
        ORDER BY year DESC, month DESC
        LIMIT %s
    """
    cursor.execute(query, (user_id, num_months))
    results = cursor.fetchall()
    
    conn.close()
    
    # Reverse for chronological order
    results.reverse()
    
    for row in results:
        row['income'] = float(row['income'] or 0)
        row['expenses'] = float(row['expenses'] or 0)
        
    return results
