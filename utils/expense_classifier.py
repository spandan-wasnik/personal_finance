# expense_classifier.py
# This file classifies expenses into fixed, recurring_variable, or variable.

def classify_expense_type(description, amount, category):
    """
    Classifies an expense into one of three types based on keywords and category:
    - fixed: Same amount every month (rent, EMI, etc.)
    - recurring_variable: Happens monthly but amount varies (electricity, groceries)
    - variable: Discretionary spending (dining out, shopping, etc.)
    """
    desc_lower = ""
    if description:
        desc_lower = description.lower()
        
    fixed_keywords = ['rent', 'emi', 'loan', 'insurance', 'subscription', 'salary', 'stipend']
    recurring_categories = ['Bills', 'Health', 'Education']
    variable_categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Travel', 'Other']
    
    # First, check for fixed expenses based on keywords
    for keyword in fixed_keywords:
        if keyword in desc_lower:
            return 'fixed'
            
    # Then check by category
    if category in recurring_categories:
        return 'recurring_variable'
    elif category in variable_categories:
        return 'variable'
        
    # Default to variable if not caught by above rules
    return 'variable'
