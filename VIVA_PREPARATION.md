# Personal Finance & Expense Analyzer — Viva & Presentation Guide

---

## 1. Project Tagline & Core Philosophy

> **"Don't just show users where their money went — show them where their current spending could lead."**

Most finance apps only show backward-looking history (pie charts of past expenses). Our system features a **6-Stage Analysis Pipeline** that forecasts month-end spending, detects overspending before it happens, calculates the impact on planned savings, and generates actionable daily spending recommendations.

---

## 2. The 6-Stage Analysis Pipeline (Viva Favorite)

Be ready to explain this flow on the whiteboard:

1. **Transaction Ingestion & Normalization (`preprocessing.py`):**
   - Ingests CSV/Excel statements from PhonePe, Paytm, Google Pay, or Banks.
   - Cleans currency symbols (₹, commas), parses various date formats, standardizes column headers.
2. **Expense Classification (`expense_classifier.py`):**
   - Classifies each expense into **Fixed** (Rent, EMI), **Recurring-Variable** (Electricity, Groceries), or **Variable** (Dining, Shopping).
3. **Category Spending Aggregation (`analysis.py`):**
   - Groups transactions by category and computes sums and counts using SQL `GROUP BY`.
4. **Future Spending Prediction (`prediction.py`):**
   - Uses **Linear Regression** (Ordinary Least Squares) on day-of-month vs. cumulative category spend to forecast total expenditure by day 30.
5. **Overspending Detection & Savings Impact (`savings_impact.py`):**
   - Compares predicted spend against category budgets: `Overspend = Predicted Spend - Budget`.
   - Projects reduction in planned savings: `Savings At Risk = Planned Savings - Total Overspend`.
6. **Rule-Based Recommendation (`recommendations.py`):**
   - Computes safe daily spending targets: `(Budget - Current Spend) / Remaining Days` to prevent budget overrun.

---

## 3. Academic Subject Mapping (Direct Viva Answers)

| Subject | Where it is demonstrated in the code | Viva Question & Answer |
|---|---|---|
| **DBMS / SQL** | `database/schema.sql`, `database.py`, `utils/analysis.py` | **Q:** Why use normalized tables? **A:** Eliminates redundancy. We use foreign keys with `ON DELETE CASCADE`, unique constraints (`user_id, month, year` on budgets), and aggregation queries (`SUM`, `GROUP BY`, `ORDER BY`). |
| **Data Structures & Algorithms** | `utils/preprocessing.py`, `utils/categorization.py` | **Q:** How is categorization optimized? **A:** Hash maps / dictionaries with O(1) average lookup for keyword-to-category mapping, list sorting for dates and day indexing. |
| **Statistics** | `utils/analysis.py`, `utils/anomaly_detection.py` | **Q:** How do you determine baseline spending? **A:** Mean, median, standard deviation, and Z-score calculation: \( z = \frac{x - \mu}{\sigma} \). If \( \|z\| > 2.0 \), it's flagged as an outlier. |
| **Machine Learning** | `utils/prediction.py`, `utils/anomaly_detection.py` | **Q:** Why Linear Regression and Isolation Forest? **A:** Linear regression learns cumulative spending trajectory over days. Isolation Forest is an unsupervised tree ensemble that isolates anomalies without requiring labeled fraud data. |
| **Web Technologies** | `app.py`, Jinja2 templates, Tailwind CSS | **Q:** Why server-side rendering with Flask? **A:** Fast, lightweight, easy session management, and zero npm build toolchain overhead for simple deployment. |

---

## 4. Top 10 Viva Questions & Winning Answers

### Q1: What is the Research Gap addressed by your project?
**Answer:** Existing commercial solutions focus primarily on recording past transactions and sending passive budget-exceeded alerts after the damage is done. Our system predicts overspending halfway through the month and translates that overspending into tangible savings loss, giving users an adjusted daily spending quota.

### Q2: How does Linear Regression forecast month-end spending?
**Answer:** For a specific category in the current month, we plot:
- Feature \( X \): Day of the month (e.g. Day 1, Day 4, Day 12).
- Target \( Y \): Cumulative expenditure up to that day.
We fit a linear model \( Y = mX + c \). We then query the model at \( X = 30 \) to predict projected expenditure at month-end.

### Q3: How does the Anomaly Detection work?
**Answer:** We employ **Isolation Forest** from `scikit-learn`. Unlike distance-based algorithms, Isolation Forest constructs an ensemble of isolation trees. Anomalies (such as an unusual ₹4,500 restaurant charge when normal meals are ₹300) have distinct attribute values and require fewer splits to be isolated near the root of the trees. If historical records are fewer than 5, we gracefully fall back to the **Z-score** statistical metric.

### Q4: Why did you not use a Large Language Model (LLM) or Deep Learning?
**Answer:** For tabular financial arithmetic and budget predictions, Deep Learning is over-parameterized, lacks explainability, and introduces high compute/API costs. Linear Regression and statistical rules are deterministic, interpretable, run in milliseconds locally, and produce 100% reliable calculations without hallucinations.

### Q5: How do you handle different CSV formats from PhonePe, Paytm, and Google Pay?
**Answer:** Through our preprocessing and column-mapping abstraction layer in `utils/preprocessing.py`. It inspects the header names:
- PhonePe uses `Transaction Details`
- Paytm uses `Activity`
- Google Pay uses `Time`
It maps them to a standard schema (`date`, `description`, `amount`, `type`, `category`, `payment_mode`), cleans currency strings and dates, and normalizes rows before inserting them into MySQL.

### Q6: How is user security maintained?
**Answer:** Passwords are never stored in plain text; they are salted and hashed using `bcrypt`. SQL queries use parameterized placeholders (`%s`) to prevent SQL Injection attacks. Session authentication is enforced via a `@login_required` decorator.

### Q7: What is the difference between Online Balance and Cash Balance?
**Answer:** Cash transactions represent physical currency, whereas Online Balance tracks digital payments (UPI, Debit/Credit Cards, Net Banking). In our SQL query, we aggregate cash and online inflows minus outflows separately, preventing discrepancies between digital account balances and physical cash on hand.

### Q8: What happens if a user uploads a statement with 1,000 transactions?
**Answer:** Pandas handles data parsing in vectorized memory buffers. Valid rows are batched and inserted via MySQL parameterized execution, and the user receives a summary showing how many records were inserted and how many invalid rows were skipped.

### Q9: Can the user edit or re-categorize a transaction?
**Answer:** Yes. The transaction table provides an Edit modal where the user can modify description, amount, category, or payment mode. The API endpoint `PUT /api/transactions/<id>` updates MySQL and triggers recalculation of anomalies.

### Q10: What are the future enhancements?
**Answer:** Account Aggregator API integration for automated bank statement synchronization, receipt OCR scanning, and SMS/push-notification parse engines for real-time tracking.

---

## 5. Demonstration Flow for the Evaluator

1. **Sign in:** Log in with your registered account.
2. **Dashboard Overview:**
   - Highlight the top KPI cards: Total Income, Total Expenses, Current Balance, Total Savings, Online Balance, and Cash Balance.
   - Point out the active **Alert Banner** (flags savings rate warnings or unusual transactions).
   - Show the interactive **Period Selector** (switch between months with live chart updates).
3. **Category Spending & 6-Month Trend:**
   - Show the doughnut chart of category breakdown and the bar chart of monthly expenses.
4. **Transactions Page:**
   - Filter by Type (Income/Expense), Category (Food, Transport, etc.), or search by keyword.
   - Click "Add Transaction" to demonstrate manual entry.
5. **Upload Statements:**
   - Demonstrate the upload page and show the supported formats (PhonePe, Paytm, GPay, Generic).
6. **Budget Management:**
   - Show the circular gauge for overall budget and the category-wise budget progress bars.
7. **Deep Analysis & AI Predictions:**
   - Show the Income vs. Expenses comparative line chart.
   - Show the **AI Insights & Predictions** table (Linear Regression month-end spend vs. Budget status: On Track / Close / Will Exceed).
   - Show the **Unusual Activity** table (Isolation Forest outlier detection).
8. **Settings:**
   - Demonstrate profile update and security options.
