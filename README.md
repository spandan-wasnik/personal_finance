# Personal Finance & Expense Analyzer

> **A web-based personal finance tracking and analysis system built as a B.Tech semester project.**

---

## Project Description

Managing personal finances is challenging when transaction data is spread across multiple UPI apps, bank accounts, and cash payments. This application consolidates all your financial data in one place and provides intelligent analysis to help you understand your spending habits and protect your savings.

**The core idea:** *Don't just show users where their money went — show them where their current spending could lead.*

---

## Problem Statement

People use multiple payment platforms (Paytm, PhonePe, Google Pay, bank accounts, cash) and their transaction data is scattered across these sources. This makes it difficult to:
- Understand overall spending habits
- Track savings progress
- Detect unusually high expenses
- Predict future spending and take action early

---

## Objectives

1. Import transaction data from CSV/Excel files (PhonePe, Paytm, Google Pay, Bank)
2. Categorize transactions automatically using keyword-based rules
3. Analyze income, expenses, and savings
4. Track monthly budgets with per-category limits
5. Set and monitor financial goals
6. Predict future spending using Linear Regression
7. Detect unusual transactions using Isolation Forest
8. Calculate how overspending impacts planned savings
9. Generate rule-based financial recommendations
10. Visualize all data through an interactive dashboard

---

## Features

- **Transaction Upload** — CSV/Excel import from PhonePe, Paytm, Google Pay, or generic bank statements
- **Manual Entry** — Add individual transactions with category, payment mode, and notes
- **Auto Categorization** — Keyword-based categorization (Food, Transport, Shopping, Entertainment, Bills, Education, Health, Travel)
- **Expense Classification** — Fixed / Recurring-Variable / Variable expense types
- **Dashboard** — Income, Expenses, Balance, Savings cards with charts
- **Budget Management** — Monthly and per-category budget limits with progress bars
- **Financial Goals** — Goal tracking with estimated months-to-completion
- **Spending Prediction** — Linear Regression to predict month-end spending per category
- **Overspending Detection** — Alerts when predicted spending will exceed budget
- **Savings Impact** — Shows how overspending reduces planned savings
- **Anomaly Detection** — Isolation Forest (Z-score fallback) to flag unusual transactions
- **Smart Recommendations** — Rule-based suggestions to protect savings
- **Search & Filter** — Filter transactions by date, category, type, payment mode, amount

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x + Flask |
| Database | MySQL |
| Data Processing | Pandas, NumPy |
| Machine Learning | scikit-learn (Linear Regression, Isolation Forest) |
| Frontend | HTML, Tailwind CSS (CDN) |
| Charts | Chart.js (CDN) |
| Authentication | Flask Sessions + bcrypt |
| File Parsing | Pandas read_csv / read_excel |

---

## System Architecture

```
User Browser
     │
     ▼
Flask Application (app.py)
     │
     ├── Auth Routes (login, register, logout)
     ├── Page Routes (dashboard, transactions, budget, goals, analysis)
     ├── Upload Route (CSV/Excel processing)
     └── API Routes (/api/*)
          │
          ├── database.py ─── MySQL Database
          └── utils/
               ├── preprocessing.py     (CSV/Excel parsing)
               ├── categorization.py    (Keyword → Category)
               ├── expense_classifier.py (Fixed/Recurring/Variable)
               ├── analysis.py          (Financial calculations)
               ├── prediction.py        (Linear Regression)
               ├── anomaly_detection.py (Isolation Forest)
               ├── savings_impact.py    (Overspend → Savings loss)
               └── recommendations.py  (Rule-based suggestions)
```

---

## Database Structure

| Table | Purpose |
|---|---|
| `users` | Login credentials |
| `transactions` | All income/expense records |
| `budgets` | Monthly overall budget |
| `category_budgets` | Per-category spending limits |
| `financial_goals` | Savings goals with progress |

---

## Installation

### Prerequisites
- Python 3.9 or higher
- MySQL Server (XAMPP/WAMP or standalone)
- pip

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/personal-finance-analyzer.git
cd personal-finance-analyzer
```

### Step 2: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set up MySQL database
1. Open MySQL (via XAMPP phpMyAdmin or MySQL Workbench)
2. Run the schema file:
```sql
source database/schema.sql
```
Or from command line:
```bash
mysql -u root -p < database/schema.sql
```

### Step 4: Configure database connection
Open `database.py` and update:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Change this
    'database': 'personal_finance',
    'port': 3306
}
```

### Step 5: Run the application
```bash
python app.py
```

### Step 6: Open in browser
Visit: [http://localhost:5000](http://localhost:5000)

---

## How to Use

1. **Register** — Create an account at `/register`
2. **Upload Transactions** — Go to Upload page, select your CSV/Excel file and source app
3. **Or enter manually** — Use the Transactions page to add individual transactions
4. **Set Budget** — Go to Budget page, set your monthly budget and per-category limits
5. **View Dashboard** — See your financial summary, charts, and alerts
6. **Set Goals** — Add financial goals on the Goals page
7. **View Analysis** — Deep analysis, predictions, and anomaly detection on Analysis page

---

## Sample Data

Sample CSV files are provided in the `sample_data/` folder:
- `sample_transactions.csv` — Generic format
- `sample_phonePe.csv` — PhonePe format
- `sample_paytm.csv` — Paytm format

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/summary` | Financial summary (income, expenses, balance) |
| GET | `/api/transactions` | All transactions (JSON) |
| POST | `/api/transactions` | Add new transaction |
| PUT | `/api/transactions/<id>` | Update transaction |
| DELETE | `/api/transactions/<id>` | Delete transaction |
| GET | `/api/category-expenses` | Spending by category |
| GET | `/api/monthly-expenses` | Month-by-month expenses |
| GET | `/api/predictions` | Spending predictions |
| GET | `/api/alerts` | Active alerts and recommendations |

---

## Academic Concepts Demonstrated

| Subject | Implementation |
|---|---|
| Python | All backend code, utility modules |
| DBMS / SQL | MySQL, 5 tables, GROUP BY, JOIN, WHERE, ORDER BY |
| Data Structures | Lists, Dictionaries, Sorting, Searching, Filtering |
| Statistics | Mean, Median, Std Dev, Z-score for anomaly detection |
| Machine Learning | Linear Regression (prediction), Isolation Forest (anomaly) |
| OOP | Classes in utility modules |
| Pandas / NumPy | CSV parsing, data cleaning, numerical calculations |
| HTML / CSS | 9 Jinja2 templates with Tailwind CSS |
| APIs | Flask RESTful JSON endpoints |

---

## Screenshots

*(Add screenshots of your running application here)*

---

## Future Scope

- Mobile application (Flutter/React Native)
- Bank API integration for automatic data sync
- SMS/email parsing for transaction extraction
- Advanced ML models for better spending prediction
- Personalized AI financial recommendations
- Investment tracking (stocks, mutual funds, FD)
- Credit score analysis
- Multiple currency support
- Voice-based expense entry
- Family/shared expense tracking

---

## License

This project is created for personal finance management and expense analysis.
