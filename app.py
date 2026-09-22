# app.py
# Personal Finance & Expense Analyzer
#
# This is the main Flask application file.
# It handles all web routes, authentication, and API endpoints.

import os
import json
import bcrypt
from datetime import datetime, date
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)

# Import our custom utility modules
from database import get_db_connection, init_db
from utils.preprocessing import process_uploaded_file
from utils.analysis import (
    get_summary, get_monthly_expenses, get_category_expenses,
    get_recent_transactions, get_budget_status, get_income_expense_trend
)
from utils.anomaly_detection import detect_anomalies_for_user, get_unusual_transactions
from utils.prediction import get_all_predictions
from utils.savings_impact import calculate_savings_impact
from utils.recommendations import generate_recommendations
from utils.categorization import CATEGORY_KEYWORDS

# Create the Flask application
app = Flask(__name__)

# Secret key for session management — change this to a random string in production
app.secret_key = 'personalfinance_secret_key_2024_mmcoe'

# Folder where uploaded CSV/Excel files are temporarily stored
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):
    """
    Checks if the uploaded file has a valid extension.
    Returns True if extension is csv, xlsx, or xls.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(func):
    """
    A decorator that checks if the user is logged in.
    If not logged in, redirects to the login page.
    Usage: @login_required above any route that needs authentication.
    """
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def get_current_user():
    """
    Returns the current logged-in user's information from the database.
    Returns None if not logged in or user not found.
    """
    if 'user_id' not in session:
        return None

    connection = get_db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page — redirect to dashboard if logged in, else to login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET: Shows the login page.
    POST: Validates email/password and creates a session.
    """
    # If already logged in, go to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')

        # Look up user in database
        connection = get_db_connection()
        if connection is None:
            flash('Database connection failed. Please try again.', 'error')
            return render_template('login.html')

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        # Check if user exists and password is correct
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Store user info in session (this keeps them logged in)
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET: Shows the registration page.
    POST: Creates a new user account.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validate input
        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')

        # Hash the password before storing (never store plain text passwords)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user into database
        connection = get_db_connection()
        if connection is None:
            flash('Database connection failed. Please try again.', 'error')
            return render_template('register.html')

        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password.decode('utf-8'))
            )
            connection.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            if 'Duplicate entry' in str(e):
                flash('An account with this email already exists.', 'error')
            else:
                flash('Registration failed. Please try again.', 'error')
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================
# DASHBOARD ROUTE
# ============================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard page.
    Shows financial summary, charts, alerts, goals, and recent transactions.
    """
    user_id = session['user_id']
    user = get_current_user()

    # Get available months from user's transactions
    connection = get_db_connection()
    available_months = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT MONTH(date) as month, YEAR(date) as year, MONTHNAME(date) as month_name
            FROM transactions
            WHERE user_id = %s
            ORDER BY year DESC, month DESC
        """, (user_id,))
        available_months = cursor.fetchall()
        cursor.close()
        connection.close()

    # Allow user to pick month/year, or default to current month, or fallback to latest month with data
    today = date.today()
    req_month = request.args.get('month')
    req_year = request.args.get('year')

    if req_month and req_year:
        current_month = int(req_month)
        current_year = int(req_year)
    elif available_months:
        # If current system month has transactions, use it; otherwise use latest month with data
        has_current = any(m['month'] == today.month and m['year'] == today.year for m in available_months)
        if has_current:
            current_month = today.month
            current_year = today.year
        else:
            current_month = available_months[0]['month']
            current_year = available_months[0]['year']
    else:
        current_month = today.month
        current_year = today.year

    # Get financial summary for current month
    summary = get_summary(user_id, current_month, current_year)

    # Get category-wise spending for pie chart
    category_expenses = get_category_expenses(user_id, current_month, current_year)

    # Get last 6 months of spending for bar chart
    monthly_expenses = get_monthly_expenses(user_id, num_months=6)

    # Get budget status for current month
    budget_status = get_budget_status(user_id, current_month, current_year)

    # Get financial goals
    goals = get_goals(user_id)

    # Get last 10 transactions
    recent_transactions = get_recent_transactions(user_id, limit=10)

    # Run anomaly detection and get unusual transactions
    detect_anomalies_for_user(user_id)
    unusual_transactions = get_unusual_transactions(user_id, limit=5)

    # Generate alerts and recommendations
    recommendations = generate_recommendations(user_id, current_month, current_year)

    # Separate alerts (warnings) from general recommendations
    alerts = [r for r in recommendations if r['type'] in ('warning', 'danger')]

    return render_template(
        'dashboard.html',
        user=user,
        summary=summary,
        category_expenses=category_expenses,
        monthly_expenses=monthly_expenses,
        budget_status=budget_status,
        goals=goals,
        recent_transactions=recent_transactions,
        unusual_transactions=unusual_transactions,
        recommendations=recommendations,
        alerts=alerts,
        current_month=current_month,
        current_year=current_year,
        available_months=available_months
    )


# ============================================================
# TRANSACTIONS ROUTES
# ============================================================

@app.route('/transactions')
@login_required
def transactions():
    """
    Shows all transactions with filter and search functionality.
    Filters are applied via GET query parameters.
    """
    user_id = session['user_id']

    # Get filter parameters from URL query string
    filter_date_from = request.args.get('date_from', '')
    filter_date_to = request.args.get('date_to', '')
    filter_category = request.args.get('category', '')
    filter_type = request.args.get('type', '')
    filter_payment_mode = request.args.get('payment_mode', '')
    filter_search = request.args.get('search', '')
    filter_amount_min = request.args.get('amount_min', '')
    filter_amount_max = request.args.get('amount_max', '')

    # Build SQL query with filters
    query = "SELECT * FROM transactions WHERE user_id = %s"
    params = [user_id]

    if filter_date_from:
        query += " AND date >= %s"
        params.append(filter_date_from)

    if filter_date_to:
        query += " AND date <= %s"
        params.append(filter_date_to)

    if filter_category:
        query += " AND category = %s"
        params.append(filter_category)

    if filter_type:
        query += " AND type = %s"
        params.append(filter_type)

    if filter_payment_mode:
        query += " AND payment_mode = %s"
        params.append(filter_payment_mode)

    if filter_search:
        query += " AND description LIKE %s"
        params.append(f'%{filter_search}%')

    if filter_amount_min:
        query += " AND amount >= %s"
        params.append(float(filter_amount_min))

    if filter_amount_max:
        query += " AND amount <= %s"
        params.append(float(filter_amount_max))

    query += " ORDER BY date DESC, created_at DESC"

    # Execute the query
    connection = get_db_connection()
    if connection is None:
        flash('Database error. Could not load transactions.', 'error')
        return render_template('transactions.html', transactions=[], categories=list(CATEGORY_KEYWORDS.keys()))

    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    all_transactions = cursor.fetchall()

    # Convert date objects to strings for display
    for txn in all_transactions:
        if hasattr(txn['date'], 'strftime'):
            txn['date'] = txn['date'].strftime('%Y-%m-%d')

    cursor.close()
    connection.close()

    # Get list of all categories for the filter dropdown
    categories = list(CATEGORY_KEYWORDS.keys())

    return render_template(
        'transactions.html',
        transactions=all_transactions,
        categories=categories,
        total_count=len(all_transactions),
        # Pass filter values back to template so form stays filled
        filter_date_from=filter_date_from,
        filter_date_to=filter_date_to,
        filter_category=filter_category,
        filter_type=filter_type,
        filter_payment_mode=filter_payment_mode,
        filter_search=filter_search,
        filter_amount_min=filter_amount_min,
        filter_amount_max=filter_amount_max
    )


# ============================================================
# UPLOAD ROUTE
# ============================================================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    GET: Shows the upload page.
    POST: Processes the uploaded CSV/Excel file and inserts transactions into DB.
    """
    if request.method == 'POST':
        # Check if file was included in the request
        if 'file' not in request.files:
            flash('No file was uploaded. Please select a file.', 'error')
            return redirect(url_for('upload'))

        uploaded_file = request.files['file']
        source = request.form.get('source', 'Generic CSV')

        # Check if user selected a file
        if uploaded_file.filename == '':
            flash('No file selected. Please choose a CSV or Excel file.', 'error')
            return redirect(url_for('upload'))

        # Check if file type is allowed
        if not allowed_file(uploaded_file.filename):
            flash('Invalid file type. Please upload a CSV or Excel (.xlsx/.xls) file.', 'error')
            return redirect(url_for('upload'))

        # Save the file temporarily
        safe_filename = f"upload_{session['user_id']}_{int(datetime.now().timestamp())}.{uploaded_file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        uploaded_file.save(filepath)

        try:
            # Process the file using our preprocessing utility
            transactions_list, success_count, skip_count, error_messages = process_uploaded_file(
                filepath, session['user_id'], source
            )

            if not transactions_list and success_count == 0:
                flash(f'No valid transactions found in the file. {skip_count} rows were skipped.', 'warning')
                return redirect(url_for('upload'))

            # Insert valid transactions into the database
            connection = get_db_connection()
            if connection is None:
                flash('Database error. Could not save transactions.', 'error')
                return redirect(url_for('upload'))

            cursor = connection.cursor()
            insert_query = """
                INSERT INTO transactions
                (user_id, date, description, amount, type, category, expense_type, payment_mode, source, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            inserted = 0
            for txn in transactions_list:
                try:
                    cursor.execute(insert_query, (
                        txn['user_id'],
                        txn['date'],
                        txn['description'],
                        txn['amount'],
                        txn['type'],
                        txn['category'],
                        txn['expense_type'],
                        txn['payment_mode'],
                        txn['source'],
                        txn['notes']
                    ))
                    inserted += 1
                except Exception:
                    skip_count += 1  # Count DB errors as skips too

            connection.commit()
            cursor.close()
            connection.close()

            # Show result message to user
            if inserted > 0:
                flash(f'{inserted} transactions imported successfully.', 'success')
            if skip_count > 0:
                flash(f'{skip_count} invalid rows were skipped.', 'warning')

            # Run anomaly detection after new data is imported
            detect_anomalies_for_user(session['user_id'])

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        finally:
            # Delete the temporary file after processing
            if os.path.exists(filepath):
                os.remove(filepath)

        return redirect(url_for('transactions'))

    return render_template('upload.html')


# ============================================================
# BUDGET ROUTES
# ============================================================

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    """
    GET: Shows the budget management page.
    POST: Saves or updates the monthly budget.
    """
    user_id = session['user_id']
    today = date.today()
    current_month = int(request.args.get('month', today.month))
    current_year = int(request.args.get('year', today.year))

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'monthly')

        if form_type == 'monthly':
            # Set overall monthly budget
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))
            amount = float(request.form.get('amount', 0))

            if amount <= 0:
                flash('Budget amount must be greater than zero.', 'error')
            else:
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    # Use INSERT ... ON DUPLICATE KEY UPDATE to handle existing budgets
                    cursor.execute("""
                        INSERT INTO budgets (user_id, month, year, amount)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE amount = %s
                    """, (user_id, month, year, amount, amount))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    flash('Monthly budget saved successfully!', 'success')

        elif form_type == 'category':
            # Set per-category budget
            category = request.form.get('category')
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))
            budget_amount = float(request.form.get('budget_amount', 0))

            if budget_amount <= 0:
                flash('Category budget must be greater than zero.', 'error')
            else:
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("""
                        INSERT INTO category_budgets (user_id, category, month, year, budget_amount)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE budget_amount = %s
                    """, (user_id, category, month, year, budget_amount, budget_amount))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    flash(f'Budget for {category} saved!', 'success')

        return redirect(url_for('budget', month=current_month, year=current_year))

    # --- GET request: load budget data ---

    # Get overall budget status
    budget_status = get_budget_status(user_id, current_month, current_year)

    # Get category expenses and category budgets
    category_expenses = get_category_expenses(user_id, current_month, current_year)

    # Get all category budgets for current month
    connection = get_db_connection()
    category_budgets = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT cb.*, 
                   COALESCE(SUM(t.amount), 0) as spent
            FROM category_budgets cb
            LEFT JOIN transactions t ON (
                t.user_id = cb.user_id
                AND t.category = cb.category
                AND MONTH(t.date) = cb.month
                AND YEAR(t.date) = cb.year
                AND t.type = 'expense'
            )
            WHERE cb.user_id = %s AND cb.month = %s AND cb.year = %s
            GROUP BY cb.id
        """, (user_id, current_month, current_year))
        category_budgets = cursor.fetchall()
        cursor.close()
        connection.close()

    # Calculate percentage used for each category budget
    for cat_budget in category_budgets:
        if cat_budget['budget_amount'] > 0:
            cat_budget['percentage'] = min(100, (cat_budget['spent'] / cat_budget['budget_amount']) * 100)
        else:
            cat_budget['percentage'] = 0

    categories = list(CATEGORY_KEYWORDS.keys())

    return render_template(
        'budget.html',
        budget_status=budget_status,
        category_budgets=category_budgets,
        category_expenses=category_expenses,
        categories=categories,
        current_month=current_month,
        current_year=current_year
    )


@app.route('/budget/category/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_category_budget(budget_id):
    """Deletes a category budget entry."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM category_budgets WHERE id = %s AND user_id = %s",
            (budget_id, session['user_id'])
        )
        connection.commit()
        cursor.close()
        connection.close()
        flash('Category budget deleted.', 'info')
    return redirect(url_for('budget'))


# ============================================================
# GOALS ROUTES
# ============================================================

def get_goals(user_id):
    """Helper function to get all financial goals for a user."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM financial_goals WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    goals = cursor.fetchall()
    cursor.close()
    connection.close()

    # Calculate progress and months remaining for each goal
    for goal in goals:
        if goal['target_amount'] > 0:
            goal['progress_percentage'] = min(100, (goal['current_amount'] / goal['target_amount']) * 100)
        else:
            goal['progress_percentage'] = 0

        remaining = goal['target_amount'] - goal['current_amount']
        if remaining > 0 and goal['monthly_contribution'] > 0:
            goal['months_remaining'] = int(remaining / goal['monthly_contribution']) + 1
        else:
            goal['months_remaining'] = 0

        goal['is_achieved'] = goal['current_amount'] >= goal['target_amount']

    return goals


@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    """
    GET: Shows the financial goals page.
    POST: Adds a new financial goal.
    """
    user_id = session['user_id']

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'add')

        if form_type == 'add':
            goal_name = (request.form.get('goal_name') or request.form.get('name') or '').strip()
            target_amount = float(request.form.get('target_amount') or 0)
            current_amount = float(request.form.get('current_amount') or 0)
            monthly_contribution = float(request.form.get('monthly_contribution') or 0)
            target_date = request.form.get('target_date') or None

            if not goal_name or target_amount <= 0:
                flash('Goal name and target amount are required.', 'error')
            else:
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("""
                        INSERT INTO financial_goals
                        (user_id, goal_name, target_amount, current_amount, monthly_contribution, target_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, goal_name, target_amount, current_amount, monthly_contribution, target_date))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    flash(f'Goal "{goal_name}" added successfully!', 'success')

        return redirect(url_for('goals'))

    user_goals = get_goals(user_id)
    return render_template('goals.html', goals=user_goals)


@app.route('/goals/edit/<int:goal_id>', methods=['POST'])
@login_required
def edit_goal(goal_id):
    """Updates an existing financial goal."""
    user_id = session['user_id']
    goal_name = (request.form.get('goal_name') or request.form.get('name') or '').strip()
    target_amount = float(request.form.get('target_amount') or 0)
    current_amount = float(request.form.get('current_amount') or 0)
    monthly_contribution = float(request.form.get('monthly_contribution') or 0)
    target_date = request.form.get('target_date') or None

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE financial_goals
            SET goal_name=%s, target_amount=%s, current_amount=%s, monthly_contribution=%s, target_date=%s
            WHERE id=%s AND user_id=%s
        """, (goal_name, target_amount, current_amount, monthly_contribution, target_date or None, goal_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Goal updated successfully!', 'success')

    return redirect(url_for('goals'))


@app.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """Deletes a financial goal."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM financial_goals WHERE id = %s AND user_id = %s",
            (goal_id, session['user_id'])
        )
        connection.commit()
        cursor.close()
        connection.close()
        flash('Goal deleted.', 'info')
    return redirect(url_for('goals'))


# ============================================================
# ANALYSIS ROUTE
# ============================================================

@app.route('/analysis')
@login_required
def analysis():
    """
    Shows the deep analysis page with charts, predictions, and anomaly detection.
    """
    user_id = session['user_id']
    # Get available months from user's transactions
    connection = get_db_connection()
    available_months = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT MONTH(date) as month, YEAR(date) as year, MONTHNAME(date) as month_name
            FROM transactions
            WHERE user_id = %s
            ORDER BY year DESC, month DESC
        """, (user_id,))
        available_months = cursor.fetchall()
        cursor.close()
        connection.close()

    today = date.today()
    req_month = request.args.get('month')
    req_year = request.args.get('year')

    if req_month and req_year:
        selected_month = int(req_month)
        selected_year = int(req_year)
    elif available_months:
        has_current = any(m['month'] == today.month and m['year'] == today.year for m in available_months)
        if has_current:
            selected_month = today.month
            selected_year = today.year
        else:
            selected_month = available_months[0]['month']
            selected_year = available_months[0]['year']
    else:
        selected_month = today.month
        selected_year = today.year

    # Get all analysis data
    income_expense_trend = get_income_expense_trend(user_id, num_months=12)
    category_expenses = get_category_expenses(user_id, selected_month, selected_year)
    summary = get_summary(user_id, selected_month, selected_year)

    # Get spending predictions
    predictions = get_all_predictions(user_id, selected_month, selected_year)

    # Get category budgets for comparison with predictions
    connection = get_db_connection()
    category_budget_map = {}
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT category, budget_amount FROM category_budgets
            WHERE user_id = %s AND month = %s AND year = %s
        """, (user_id, selected_month, selected_year))
        for row in cursor.fetchall():
            category_budget_map[row['category']] = float(row['budget_amount'] or 0)
        cursor.close()
        connection.close()

    # Add budget info and status to each prediction
    for pred in predictions:
        cat = pred['category']
        pred['budget'] = float(category_budget_map.get(cat, 0.0))
        if pred['budget'] > 0:
            if pred['predicted_month_end'] > pred['budget'] * 1.0:
                pred['status'] = 'exceed'
            elif pred['predicted_month_end'] > pred['budget'] * 0.8:
                pred['status'] = 'close'
            else:
                pred['status'] = 'on_track'
        else:
            pred['status'] = 'no_budget'

    # Get unusual transactions
    unusual_transactions = get_unusual_transactions(user_id, limit=20)

    # Get savings impact analysis
    savings_impact = calculate_savings_impact(user_id, selected_month, selected_year)

    return render_template(
        'analysis.html',
        income_expense_trend=income_expense_trend,
        category_expenses=category_expenses,
        summary=summary,
        predictions=predictions,
        unusual_transactions=unusual_transactions,
        savings_impact=savings_impact,
        selected_month=selected_month,
        selected_year=selected_year,
        available_months=available_months
    )


# ============================================================
# SETTINGS ROUTE
# ============================================================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Profile and account settings page."""
    user_id = session['user_id']
    user = get_current_user()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()

            if not name or not email:
                flash('Name and email are required.', 'error')
            else:
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute(
                            "UPDATE users SET name=%s, email=%s WHERE id=%s",
                            (name, email, user_id)
                        )
                        connection.commit()
                        session['user_name'] = name  # Update session too
                        flash('Profile updated successfully!', 'success')
                    except Exception as e:
                        if 'Duplicate entry' in str(e):
                            flash('This email is already used by another account.', 'error')
                        else:
                            flash('Update failed. Please try again.', 'error')
                    finally:
                        cursor.close()
                        connection.close()

        elif form_type == 'password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'error')
            else:
                # Verify current password first
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
                    db_user = cursor.fetchone()
                    cursor.close()

                    if db_user and bcrypt.checkpw(current_password.encode('utf-8'), db_user['password'].encode('utf-8')):
                        new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                        cursor2 = connection.cursor()
                        cursor2.execute(
                            "UPDATE users SET password=%s WHERE id=%s",
                            (new_hashed.decode('utf-8'), user_id)
                        )
                        connection.commit()
                        cursor2.close()
                        flash('Password changed successfully!', 'success')
                    else:
                        flash('Current password is incorrect.', 'error')
                    connection.close()

        elif form_type == 'delete':
            # Delete the account and all its data
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                connection.commit()
                cursor.close()
                connection.close()
                session.clear()
                flash('Your account has been deleted.', 'info')
                return redirect(url_for('login'))

        return redirect(url_for('settings'))

    return render_template('settings.html', user=user)


# ============================================================
# JSON API ENDPOINTS
# ============================================================

@app.route('/api/summary')
@login_required
def api_summary():
    """Returns financial summary as JSON."""
    user_id = session['user_id']
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    summary = get_summary(user_id, month, year)
    return jsonify(summary)


@app.route('/api/transactions', methods=['GET'])
@login_required
def api_get_transactions():
    """Returns all transactions as JSON."""
    user_id = session['user_id']
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC",
        (user_id,)
    )
    transactions_list = cursor.fetchall()
    cursor.close()
    connection.close()

    # Convert date objects to strings
    for txn in transactions_list:
        if hasattr(txn['date'], 'isoformat'):
            txn['date'] = txn['date'].isoformat()
        if hasattr(txn.get('created_at'), 'isoformat'):
            txn['created_at'] = txn['created_at'].isoformat()

    return jsonify(transactions_list)


@app.route('/api/transactions', methods=['POST'])
@login_required
def api_add_transaction():
    """Adds a new transaction via JSON POST."""
    user_id = session['user_id']
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate required fields
    required = ['date', 'amount', 'type']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Get category from categorization if not provided
    from utils.categorization import categorize_transaction
    from utils.expense_classifier import classify_expense_type

    description = data.get('description', '')
    category = data.get('category') or categorize_transaction(description)
    expense_type = classify_expense_type(description, float(data['amount']), category)

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO transactions
        (user_id, date, description, amount, type, category, expense_type, payment_mode, source, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        data['date'],
        description,
        float(data['amount']),
        data['type'],
        category,
        expense_type,
        data.get('payment_mode', 'Other'),
        'Manual',
        data.get('notes', '')
    ))
    connection.commit()
    new_id = cursor.lastrowid
    cursor.close()
    connection.close()

    # Re-run anomaly detection after adding new data
    detect_anomalies_for_user(user_id)

    return jsonify({'success': True, 'id': new_id}), 201


@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@login_required
def api_update_transaction(transaction_id):
    """Updates an existing transaction."""
    user_id = session['user_id']
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE transactions
        SET date=%s, description=%s, amount=%s, type=%s, category=%s, payment_mode=%s, notes=%s
        WHERE id=%s AND user_id=%s
    """, (
        data.get('date'),
        data.get('description', ''),
        float(data.get('amount', 0)),
        data.get('type'),
        data.get('category', 'Other'),
        data.get('payment_mode', 'Other'),
        data.get('notes', ''),
        transaction_id,
        user_id
    ))
    connection.commit()
    cursor.close()
    connection.close()

    detect_anomalies_for_user(user_id)
    return jsonify({'success': True})


@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def api_delete_transaction(transaction_id):
    """Deletes a transaction."""
    user_id = session['user_id']
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM transactions WHERE id = %s AND user_id = %s",
        (transaction_id, user_id)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'success': True})


@app.route('/api/category-expenses')
@login_required
def api_category_expenses():
    """Returns category-wise expenses as JSON."""
    user_id = session['user_id']
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    data = get_category_expenses(user_id, month, year)
    return jsonify(data)


@app.route('/api/monthly-expenses')
@login_required
def api_monthly_expenses():
    """Returns month-by-month expenses as JSON."""
    user_id = session['user_id']
    num_months = int(request.args.get('months', 12))
    data = get_monthly_expenses(user_id, num_months)
    return jsonify(data)


@app.route('/api/predictions')
@login_required
def api_predictions():
    """Returns spending predictions as JSON."""
    user_id = session['user_id']
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    predictions = get_all_predictions(user_id, month, year)
    return jsonify(predictions)


@app.route('/api/alerts')
@login_required
def api_alerts():
    """Returns current alerts and recommendations as JSON."""
    user_id = session['user_id']
    today = date.today()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    recommendations = generate_recommendations(user_id, month, year)
    return jsonify(recommendations)


# ============================================================
# RUN THE APPLICATION
# ============================================================

if __name__ == '__main__':
    # Initialize the database tables when starting the app
    print("Initializing database...")
    init_db()
    print("Starting Flask development server...")
    print("Open http://localhost:5000 in your browser")
    # debug=True shows error details during development
    app.run(debug=True, host='0.0.0.0', port=5000)
