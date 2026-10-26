
from database import get_db_connection

def get_summary(user_id, month=None, year=None):
    """Calculates income, expenses, balance, cash, online balance and savings rate."""
    conn = get_db_connection()
    if not conn: return {}
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expenses,
            SUM(CASE WHEN payment_mode IN ('UPI','Card','Bank Transfer') AND type='income' THEN amount 
                     WHEN payment_mode IN ('UPI','Card','Bank Transfer') AND type='expense' THEN -amount ELSE 0 END) as online_balance,
            SUM(CASE WHEN payment_mode='Cash' AND type='income' THEN amount 
                     WHEN payment_mode='Cash' AND type='expense' THEN -amount ELSE 0 END) as cash_balance
        FROM transactions WHERE user_id = %s
    """
    params = [user_id]
    if month and year:
        query += " AND MONTH(date) = %s AND YEAR(date) = %s"
        params.extend([month, year])
    cursor.execute(query, tuple(params))
    res = cursor.fetchone() or {}
    conn.close()

    inc = float(res.get('total_income') or 0)
    exp = float(res.get('total_expenses') or 0)
    bal = inc - exp
    return {
        'total_income': inc,
        'total_expenses': exp,
        'balance': bal,
        'online_balance': float(res.get('online_balance') or 0),
        'cash_balance': float(res.get('cash_balance') or 0),
        'savings': bal,
        'savings_rate': (bal / inc * 100) if inc > 0 else 0.0
    }

def get_category_expenses(user_id, month=None, year=None):
    """Gets total spending grouped by category."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    q = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE user_id = %s AND type = 'expense'"
    p = [user_id]
    if month and year:
        q += " AND MONTH(date) = %s AND YEAR(date) = %s"
        p.extend([month, year])
    q += " GROUP BY category ORDER BY total DESC"
    cursor.execute(q, tuple(p))
    rows = cursor.fetchall()
    conn.close()
    for r in rows: r['total'] = float(r['total'] or 0)
    return rows

def get_monthly_expenses(user_id, num_months=6):
    """Gets total spending per month for bar charts."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT MONTH(date) as month, YEAR(date) as year, MONTHNAME(date) as month_name, SUM(amount) as total
        FROM transactions WHERE user_id = %s AND type = 'expense'
        GROUP BY year, month, month_name ORDER BY year DESC, month DESC LIMIT %s
    """, (user_id, num_months))
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    for r in rows: r['total'] = float(r['total'] or 0)
    return rows

def get_recent_transactions(user_id, limit=8):
    """Gets last N transactions."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC, id DESC LIMIT %s", (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    for r in rows:
        r['amount'] = float(r['amount'])
        r['date'] = str(r['date'])
    return rows

def get_budget_status(user_id, month, year):
    
    conn = get_db_connection()
    if not conn: return {'budget': 0.0, 'spent': 0.0, 'remaining': 0.0, 'percentage_used': 0.0}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s AND year = %s", (user_id, month, year))
    b_row = cursor.fetchone()
    budget = float(b_row['amount']) if b_row else 0.0

    cursor.execute("SELECT SUM(amount) as spent FROM transactions WHERE user_id = %s AND type = 'expense' AND MONTH(date) = %s AND YEAR(date) = %s", (user_id, month, year))
    s_row = cursor.fetchone()
    spent = float(s_row['spent']) if s_row and s_row['spent'] else 0.0
    conn.close()

    rem = budget - spent
    pct = (spent / budget * 100) if budget > 0 else 0.0
    return {'budget': budget, 'spent': spent, 'remaining': rem, 'percentage_used': pct}
