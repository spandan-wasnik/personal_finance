# preprocessing.py
# This file handles reading and cleaning CSV/Excel files from payment apps.

import pandas as pd
import datetime
import math
from utils.categorization import categorize_transaction
from utils.expense_classifier import classify_expense_type

# Mapping of standard column names for different apps
COLUMN_MAPPINGS = {
    'PhonePe': {
        'Date': 'date',
        'Transaction Details': 'description',
        'Amount': 'amount',
        'Type': 'type'
    },
    'Paytm': {
        'Date': 'date',
        'Activity': 'description',
        'Amount': 'amount',
        'Status': 'type'
    },
    'GooglePay': {
        'Time': 'date',
        'Description': 'description',
        'Amount': 'amount',
        'Status': 'type'
    },
    'Generic': {
        'date': 'date',
        'description': 'description',
        'amount': 'amount',
        'type': 'type',
        'category': 'category',
        'payment_mode': 'payment_mode',
        'notes': 'notes'
    }
}

def clean_amount(value):
    """
    Removes currency symbols, commas, and spaces, and converts to float.
    """
    if pd.isna(value):
        return 0.0
    
    val_str = str(value)
    # Remove unwanted characters
    val_str = val_str.replace('₹', '').replace(',', '').replace('Rs.', '').replace(' ', '').strip()
    
    # Handle negative signs if any, though amounts should be positive
    try:
        amount = float(val_str)
        return abs(amount) # Keep amount positive
    except ValueError:
        return 0.0

def clean_date(value):
    """
    Tries multiple date formats and returns a datetime.date object.
    """
    if pd.isna(value):
        return datetime.date.today()
        
    val_str = str(value).strip()
    
    formats_to_try = [
        '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d',
        '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%b %d, %Y', '%d %b %Y'
    ]
    
    for fmt in formats_to_try:
        try:
            dt = datetime.datetime.strptime(val_str, fmt)
            return dt.date()
        except ValueError:
            continue
            
    # If all formats fail, use pandas to parse
    try:
        dt = pd.to_datetime(val_str)
        return dt.date()
    except:
        return datetime.date.today()

def detect_source(columns):
    """
    Identifies the app source by looking at the column names.
    """
    cols_upper = [str(c).upper() for c in columns]
    
    if 'TRANSACTION DETAILS' in cols_upper:
        return 'PhonePe'
    elif 'ACTIVITY' in cols_upper and 'PAYTM' in ' '.join(cols_upper):
        return 'Paytm'
    elif 'TIME' in cols_upper and 'GOOGLE' in ' '.join(cols_upper):
        return 'GooglePay'
    else:
        return 'Generic'

def normalize_columns(df, source):
    """
    Renames columns to our standard names: date, description, amount, type
    """
    # Create a lower case mapping of the source's expected columns
    source_mapping = COLUMN_MAPPINGS.get(source, COLUMN_MAPPINGS['Generic'])
    
    # We will do a case-insensitive rename
    rename_dict = {}
    for col in df.columns:
        for expected_col, standard_col in source_mapping.items():
            if str(col).upper() == expected_col.upper():
                rename_dict[col] = standard_col
                
    return df.rename(columns=rename_dict)

def process_uploaded_file(filepath, user_id, source_override=None):
    """
    Reads a CSV or Excel file, cleans the data, categorizes transactions,
    and returns a list of transaction dictionaries.
    """
    success_count = 0
    skip_count = 0
    error_messages = []
    transactions = []
    
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            return [], 0, 0, ["Unsupported file format"]
            
        source = source_override if source_override else detect_source(df.columns)
        df = normalize_columns(df, source)
        
        # Check if required columns exist
        required_cols = ['date', 'description', 'amount']
        for col in required_cols:
            if col not in df.columns:
                return [], 0, 0, [f"Missing required column: {col}"]
                
        # Process row by row
        for index, row in df.iterrows():
            try:
                desc = str(row['description']) if pd.notna(row['description']) else ''
                amount = clean_amount(row['amount'])
                
                # Skip zero amounts
                if amount <= 0:
                    skip_count += 1
                    continue
                    
                date_val = clean_date(row['date'])
                
                # Determine type (income or expense)
                t_type = 'expense'
                if 'type' in df.columns:
                    type_val = str(row['type']).lower()
                    if 'credit' in type_val or 'received' in type_val or 'income' in type_val:
                        t_type = 'income'
                        
                # Use category if present, else auto-categorize from description
                category = 'Other'
                if 'category' in df.columns and pd.notna(row['category']) and str(row['category']).strip():
                    category = str(row['category']).strip()
                else:
                    category = categorize_transaction(desc)
                    
                expense_type = classify_expense_type(desc, amount, category)
                
                # Determine payment mode
                payment_mode = 'UPI'
                if 'payment_mode' in df.columns and pd.notna(row['payment_mode']) and str(row['payment_mode']).strip():
                    pm = str(row['payment_mode']).strip()
                    # Standardize common values
                    if pm.lower() in ('upi', 'gpay', 'phonepe', 'paytm'):
                        payment_mode = 'UPI'
                    elif pm.lower() in ('card', 'debit card', 'credit card', 'visa', 'mastercard'):
                        payment_mode = 'Card'
                    elif pm.lower() in ('bank', 'bank transfer', 'net banking', 'neft', 'rtgs', 'imps'):
                        payment_mode = 'Bank Transfer'
                    elif pm.lower() in ('cash',):
                        payment_mode = 'Cash'
                    else:
                        payment_mode = pm
                else:
                    # Infer from description if possible
                    if 'cash' in desc.lower() or 'petrol' in desc.lower():
                        payment_mode = 'Cash'
                    elif 'salary' in desc.lower() or 'freelance' in desc.lower() or 'transfer' in desc.lower():
                        payment_mode = 'Bank Transfer'
                    else:
                        payment_mode = 'UPI'

                notes = ''
                if 'notes' in df.columns and pd.notna(row['notes']):
                    notes = str(row['notes']).strip()
                
                transaction_dict = {
                    'user_id': user_id,
                    'date': date_val,
                    'description': desc[:255],  # Limit to 255 chars
                    'amount': amount,
                    'type': t_type,
                    'category': category,
                    'expense_type': expense_type,
                    'payment_mode': payment_mode,
                    'source': source,
                    'notes': notes
                }
                
                transactions.append(transaction_dict)
                success_count += 1
                
            except Exception as e:
                skip_count += 1
                error_messages.append(f"Row {index+1} error: {str(e)}")
                
        return transactions, success_count, skip_count, error_messages
        
    except Exception as e:
        return [], 0, 0, [f"Failed to process file: {str(e)}"]
