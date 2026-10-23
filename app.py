# app.py - Personal Finance & Expense Analyzer
# Syllabus Mapping:
# - Om: Transactions (CRUD, search, filter, CSV upload, category totals)
# - Spandan: Budgets & Goals, User Auth/Sessions (OS & DBMS), Financial Advice
# - Kedar: Applied Statistics (Mean, Median, Std Dev), Z-Score Anomaly Detection, Linear Regression Prediction

import os, bcrypt, numpy as np
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash

from database import get_db_connection, init_db
from utils.categorization import categorize_transaction
from utils.expense_classifier import classify_expense_type
from utils.analysis import get_summary, get_category_expenses, get_monthly_expenses, get_recent_transactions, get_budget_status
from utils.prediction import get_all_predictions
from utils.anomaly_detection import detect_anomalies_for_user, get_unusual_transactions
from utils.recommendations import generate_recommendations
from utils.preprocessing import process_uploaded_file

app = Flask(__name__)
app.secret_key = 'finance_college_project_key_2026'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.context_processor
def inject_user():
    name = session.get('user_name', 'User')
    return {'first_name': name.split()[0] if name else 'User'}

def is_logged_in():
    return 'user_id' in session

# ----------------- AUTH (SPANDAN) -----------------
@app.route('/')
def index():
    return redirect(url_for('dashboard') if is_logged_in() else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pwd = request.form.get('password', '').strip()
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            conn.close()
            if user and bcrypt.checkpw(pwd.encode('utf-8'), user['password'].encode('utf-8')):
                session['user_id'], session['user_name'] = user['id'], user['name']
                return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        pwd = request.form.get('password', '').strip()
        if not name or not email or len(pwd) < 6:
            flash('All fields required (password min 6 chars).', 'error')
            return render_template('register.html')
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed))
                conn.commit()
                conn.close()
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception:
                flash('Email already registered.', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------- DASHBOARD -----------------
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    today = date.today()

    # 1. Fetch available months from database that actually have transactions
    conn = get_db_connection()
    available_months = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT MONTH(date) as month, YEAR(date) as year, MONTHNAME(date) as month_name
            FROM transactions WHERE user_id = %s ORDER BY year DESC, month DESC
        """, (uid,))
        available_months = cursor.fetchall()
        conn.close()

    # 2. Pick the month/year to display
    req_m = request.args.get('month')
    req_y = request.args.get('year')

    if req_m and req_y:
        m = int(req_m)
        y = int(req_y)
    elif available_months:
        # If current system month has transactions, show it; otherwise show the latest month with data!
        has_current = any(item['month'] == today.month and item['year'] == today.year for item in available_months)
        if has_current:
            m = today.month
            y = today.year
        else:
            m = available_months[0]['month']
            y = available_months[0]['year']
    else:
        m = today.month
        y = today.year

    return render_template('dashboard.html',
        summary=get_summary(uid, m, y),
        category_expenses=get_category_expenses(uid, m, y),
        monthly_expenses=get_monthly_expenses(uid, 6),
        recent_transactions=get_recent_transactions(uid, 8),
        budget_status=get_budget_status(uid, m, y),
        alerts=generate_recommendations(uid, m, y),
        current_month=m,
        current_year=y,
        available_months=available_months
    )

# ----------------- TRANSACTIONS (OM) -----------------
@app.route('/transactions')
def transactions():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    txn_type = request.args.get('type', '').strip()

    q = "SELECT * FROM transactions WHERE user_id = %s"
    params = [uid]
    if search: q += " AND description LIKE %s"; params.append(f"%{search}%")
    if category: q += " AND category = %s"; params.append(category)
    if txn_type: q += " AND type = %s"; params.append(txn_type)
    q += " ORDER BY date DESC, id DESC"

    conn = get_db_connection()
    txns = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(q, tuple(params))
        txns = cursor.fetchall()
        conn.close()

    return render_template('transactions.html', transactions=txns, filter_search=search,
                           filter_category=category, filter_type=txn_type, today_date=date.today().isoformat())

@app.route('/transactions/add', methods=['POST'])
def add_transaction():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    t_date = request.form.get('date') or date.today().isoformat()
    desc = request.form.get('description', '').strip()
    amt = float(request.form.get('amount') or 0)
    t_type = request.form.get('type', 'expense')
    cat = request.form.get('category') or categorize_transaction(desc)
    mode = request.form.get('payment_mode', 'UPI')
    exp_type = classify_expense_type(desc, amt, cat)

    if amt > 0:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, date, description, amount, type, category, expense_type, payment_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (uid, t_date, desc, amt, t_type, cat, exp_type, mode))
            conn.commit()
            conn.close()
            detect_anomalies_for_user(uid)
            flash('Transaction added successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if not is_logged_in(): return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, session['user_id']))
        conn.commit()
        conn.close()
        flash('Transaction deleted.', 'info')
    return redirect(url_for('transactions'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_logged_in(): return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Please choose a CSV or Excel file.', 'error')
            return redirect(url_for('upload'))

        filepath = os.path.join(UPLOAD_FOLDER, f"up_{session['user_id']}_{file.filename}")
        file.save(filepath)

        txns, count, skipped, errors = process_uploaded_file(filepath, session['user_id'])
        inserted = 0

        if txns:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                for t in txns:
                    try:
                        cursor.execute("""
                            INSERT INTO transactions (user_id, date, description, amount, type, category, expense_type, payment_mode)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (t['user_id'], str(t['date']), t['description'], t['amount'], t['type'], t['category'], t['expense_type'], t['payment_mode']))
                        inserted += 1
                    except Exception:
                        skipped += 1
                conn.commit()
                conn.close()
                detect_anomalies_for_user(session['user_id'])
                flash(f'{inserted} transactions imported successfully! ({skipped} rows skipped)', 'success')
        else:
            msg = errors[0] if errors else 'No valid transactions found in file.'
            flash(msg, 'warning')

        if os.path.exists(filepath): os.remove(filepath)
        return redirect(url_for('transactions'))
    return render_template('upload.html')

# ----------------- BUDGET & GOALS (SPANDAN) -----------------
@app.route('/budget', methods=['GET', 'POST'])
def budget():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    today = date.today()
    m, y = today.month, today.year

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        conn = get_db_connection()
        if form_type == 'monthly' and conn:
            amt = float(request.form.get('amount', 0))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO budgets (user_id, month, year, amount) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE amount = %s", (uid, m, y, amt, amt))
            conn.commit(); conn.close()
            flash('Monthly budget saved!', 'success')
        elif form_type == 'category' and conn:
            cat = request.form.get('category')
            amt = float(request.form.get('budget_amount', 0))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO category_budgets (user_id, category, month, year, budget_amount) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE budget_amount = %s", (uid, cat, m, y, amt, amt))
            conn.commit(); conn.close()
            flash(f'Budget for {cat} saved!', 'success')
        return redirect(url_for('budget'))

    conn = get_db_connection()
    cat_budgets = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT cb.*, COALESCE(SUM(t.amount), 0) as spent FROM category_budgets cb
            LEFT JOIN transactions t ON (t.user_id = cb.user_id AND t.category = cb.category AND MONTH(t.date) = cb.month AND YEAR(t.date) = cb.year AND t.type = 'expense')
            WHERE cb.user_id = %s AND cb.month = %s AND cb.year = %s GROUP BY cb.id
        """, (uid, m, y))
        cat_budgets = cursor.fetchall()
        conn.close()

    for cb in cat_budgets:
        cb['spent'], cb['budget_amount'] = float(cb['spent']), float(cb['budget_amount'])
        cb['percentage'] = min(100, (cb['spent'] / cb['budget_amount'] * 100)) if cb['budget_amount'] > 0 else 0

    return render_template('budget.html', budget_status=get_budget_status(uid, m, y), category_budgets=cat_budgets, current_month=m, current_year=y)

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    if request.method == 'POST':
        name = request.form.get('goal_name', '').strip()
        tgt = float(request.form.get('target_amount') or 0)
        curr = float(request.form.get('current_amount') or 0)
        contrib = float(request.form.get('monthly_contribution') or 0)
        t_date = request.form.get('target_date') or None
        if name and tgt > 0:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO financial_goals (user_id, goal_name, target_amount, current_amount, monthly_contribution, target_date) VALUES (%s, %s, %s, %s, %s, %s)", (uid, name, tgt, curr, contrib, t_date))
                conn.commit(); conn.close()
                flash('Goal created successfully!', 'success')
        return redirect(url_for('goals'))

    conn = get_db_connection()
    goals_list = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM financial_goals WHERE user_id = %s ORDER BY id DESC", (uid,))
        goals_list = cursor.fetchall()
        conn.close()

    for g in goals_list:
        g['target_amount'], g['current_amount'] = float(g['target_amount']), float(g['current_amount'])
        g['monthly_contribution'] = float(g['monthly_contribution'] or 0)
        g['progress_percentage'] = min(100, (g['current_amount'] / g['target_amount'] * 100)) if g['target_amount'] > 0 else 0
        g['is_achieved'] = g['current_amount'] >= g['target_amount']
        rem = g['target_amount'] - g['current_amount']
        g['months_remaining'] = int(rem / g['monthly_contribution']) + 1 if rem > 0 and g['monthly_contribution'] > 0 else 0

    return render_template('goals.html', goals=goals_list)

@app.route('/goals/edit/<int:goal_id>', methods=['POST'])
def edit_goal(goal_id):
    if not is_logged_in(): return redirect(url_for('login'))
    curr = float(request.form.get('current_amount') or 0)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE financial_goals SET current_amount = %s WHERE id = %s AND user_id = %s", (curr, goal_id, session['user_id']))
        conn.commit(); conn.close()
        flash('Goal progress updated!', 'success')
    return redirect(url_for('goals'))

@app.route('/goals/delete/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    if not is_logged_in(): return redirect(url_for('login'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financial_goals WHERE id = %s AND user_id = %s", (goal_id, session['user_id']))
        conn.commit(); conn.close()
        flash('Goal deleted.', 'info')
    return redirect(url_for('goals'))

# ----------------- STATS & PREDICTIONS (KEDAR) -----------------
@app.route('/analysis')
def analysis():
    if not is_logged_in(): return redirect(url_for('login'))
    uid = session['user_id']
    m, y = date.today().month, date.today().year

    conn = get_db_connection()
    amounts, cat_budgets = [], {}
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT amount FROM transactions WHERE user_id = %s AND type = 'expense'", (uid,))
        amounts = [float(r['amount']) for r in cursor.fetchall()]
        cursor.execute("SELECT category, budget_amount FROM category_budgets WHERE user_id = %s AND month = %s AND year = %s", (uid, m, y))
        for r in cursor.fetchall(): cat_budgets[r['category']] = float(r['budget_amount'])
        conn.close()

    stats_metrics = {
        'count': len(amounts),
        'mean': float(np.mean(amounts)) if amounts else 0.0,
        'median': float(np.median(amounts)) if amounts else 0.0,
        'std_dev': float(np.std(amounts)) if amounts else 0.0
    }

    predictions = get_all_predictions(uid, m, y)
    for p in predictions: p['budget'] = cat_budgets.get(p['category'], 0.0)

    detect_anomalies_for_user(uid)
    return render_template('analysis.html',
        stats_metrics=stats_metrics,
        predictions=predictions,
        unusual_transactions=get_unusual_transactions(uid, 10),
        monthly_trend=get_monthly_expenses(uid, 12)
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
