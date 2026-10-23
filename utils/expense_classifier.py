# expense_classifier.py - OM'S MODULE: Expense Classification (fixed/recurring/variable)

def classify_expense_type(desc, amount, category):
    """Classifies an expense into fixed, recurring_variable, or variable."""
    d = str(desc or '').lower()
    if any(k in d for k in ['rent', 'emi', 'loan', 'insurance', 'subscription', 'salary', 'stipend']):
        return 'fixed'
    if category in ['Bills', 'Health', 'Education']:
        return 'recurring_variable'
    return 'variable'
