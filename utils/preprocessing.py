# preprocessing.py - OM'S MODULE: CSV / Excel Ingestion & Cleaning
import pandas as pd
import datetime
from utils.categorization import categorize_transaction
from utils.expense_classifier import classify_expense_type

def clean_date(val):
    """Safely converts any date format to YYYY-MM-DD string (never returns NaT)."""
    if isinstance(val, pd.Series):
        val = val.dropna().iloc[0] if not val.dropna().empty else None
    if pd.isna(val) or val is None or str(val).strip().lower() in ['', 'nat', 'nan', 'none']:
        return datetime.date.today().strftime('%Y-%m-%d')
    if isinstance(val, (datetime.date, datetime.datetime, pd.Timestamp)):
        return val.strftime('%Y-%m-%d')
    s = str(val).strip()
    
    # Try common formats first
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y', '%d %b %Y', '%b %d, %Y', '%Y/%m/%d'):
        try:
            return datetime.datetime.strptime(s.split()[0], fmt).strftime('%Y-%m-%d')
        except Exception:
            pass

    # Try pandas parser as backup
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt) and str(dt) != 'NaT':
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass

    return datetime.date.today().strftime('%Y-%m-%d')

def find_header_row_csv(filepath):
    """Detects table header row in CSV statements (e.g. PhonePe metadata lines)."""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    lines = []
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                lines = [f.readline() for _ in range(50)]
            break
        except Exception:
            continue
            
    key_terms = ['date', 'amount', 'details', 'description', 'particulars', 'narration', 'transaction', 'debit', 'credit', 'balance', 'withdrawal', 'deposit', 'txn']
    for idx, line in enumerate(lines):
        line_clean = line.strip().lower()
        if not line_clean:
            continue
        parts = [p.strip().strip('"\'').lower() for p in line_clean.split(',')]
        matched = sum(1 for part in parts if any(kt in part for kt in key_terms))
        if matched >= 2:
            return idx
    return 0

def find_header_row_excel(filepath):
    """Detects table header row in Excel statements."""
    try:
        preview_df = pd.read_excel(filepath, header=None, nrows=40)
        key_terms = ['date', 'amount', 'details', 'description', 'particulars', 'narration', 'transaction', 'debit', 'credit', 'balance', 'withdrawal', 'deposit', 'txn']
        for idx, row in preview_df.iterrows():
            row_vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
            matched = sum(1 for val in row_vals if any(kt in val for kt in key_terms))
            if matched >= 2:
                return idx
    except Exception:
        pass
    return 0

def load_statement_dataframe(filepath):
    """Loads CSV or Excel safely with automatic header detection and encoding fallbacks."""
    if filepath.endswith('.csv'):
        header_idx = find_header_row_csv(filepath)
        for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                return pd.read_csv(filepath, skiprows=header_idx, encoding=enc, on_bad_lines='skip')
            except Exception:
                continue
        return pd.read_csv(filepath, skiprows=header_idx, on_bad_lines='skip')
    else:
        header_idx = find_header_row_excel(filepath)
        return pd.read_excel(filepath, skiprows=header_idx)

def process_uploaded_file(filepath, user_id):
    """Reads CSV/Excel, normalizes columns, categorizes, and returns clean records."""
    try:
        df = load_statement_dataframe(filepath)
    except Exception as e:
        return [], 0, 0, [f"Failed to read file: {e}"]

    if df.empty:
        return [], 0, 0, ["The uploaded file contains no data."]

    # Standardize column headers (lowercase, trimmed)
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Map possible alternative column names across PhonePe, Paytm, GPay, and banks
    col_map = {
        'transaction details': 'description', 'activity': 'description', 'narration': 'description',
        'details': 'description', 'particulars': 'description', 'remarks': 'description',
        'txn date': 'date', 'transaction date': 'date', 'value date': 'date',
        'txn amount': 'amount', 'transaction amount': 'amount',
        'transaction type': 'type', 'cr/dr': 'type', 'status': 'type',
        'credit/debit instrument': 'payment_mode', 'payment mode': 'payment_mode', 'mode': 'payment_mode'
    }
    # Only map 'time' to 'date' if 'date' column doesn't already exist
    if 'date' not in df.columns and 'time' in df.columns:
        col_map['time'] = 'date'

    df.rename(columns=col_map, inplace=True)
    # Deduplicate columns if any duplicate was created
    df = df.loc[:, ~df.columns.duplicated()]

    # Handle separate Debit / Credit or Withdrawal / Deposit columns if 'amount' is absent
    has_separate_dr_cr = False
    debit_col = next((c for c in ['withdrawal', 'debit', 'dr', 'withdrawal amount'] if c in df.columns), None)
    credit_col = next((c for c in ['deposit', 'credit', 'cr', 'deposit amount'] if c in df.columns), None)
    if 'amount' not in df.columns and (debit_col or credit_col):
        has_separate_dr_cr = True

    # Verify minimum required columns
    if 'description' not in df.columns:
        return [], 0, 0, ["File must contain a transaction description column (e.g. 'Transaction Details', 'Description', 'Narration')."]
    if 'amount' not in df.columns and not has_separate_dr_cr:
        return [], 0, 0, ["File must contain an 'amount' column (or Debit/Credit columns)."]

    transactions = []
    skipped = 0

    for _, row in df.iterrows():
        try:
            # 1. Clean amount and determine type if separate dr/cr
            t_type = None
            amt = 0.0

            if has_separate_dr_cr:
                dr_val = str(row.get(debit_col, '')).replace('₹', '').replace(',', '').replace('Rs.', '').replace('INR', '').strip() if debit_col else ''
                cr_val = str(row.get(credit_col, '')).replace('₹', '').replace(',', '').replace('Rs.', '').replace('INR', '').strip() if credit_col else ''
                dr_num = float(dr_val) if dr_val and dr_val.lower() != 'nan' else 0.0
                cr_num = float(cr_val) if cr_val and cr_val.lower() != 'nan' else 0.0
                if dr_num > 0:
                    amt = dr_num
                    t_type = 'expense'
                elif cr_num > 0:
                    amt = cr_num
                    t_type = 'income'
                else:
                    skipped += 1
                    continue
            else:
                amt_raw = str(row.get('amount', '')).replace('₹', '').replace(',', '').replace('Rs.', '').replace('INR', '').strip()
                amt = abs(float(amt_raw))
                if amt <= 0 or pd.isna(amt):
                    skipped += 1
                    continue

            # 2. Clean date (always safe YYYY-MM-DD string)
            date_val = row.get('date')
            if isinstance(date_val, pd.Series):
                date_val = date_val.dropna().iloc[0] if not date_val.dropna().empty else None
            date_str = clean_date(date_val)

            # 3. Description & type
            desc_val = row.get('description', '')
            if isinstance(desc_val, pd.Series):
                desc_val = desc_val.dropna().iloc[0] if not desc_val.dropna().empty else ''
            desc = str(desc_val).strip()[:255]
            if not desc or desc.lower() == 'nan':
                desc = "Transaction"

            if t_type is None:
                raw_type = str(row.get('type', '')).lower()
                if any(w in raw_type for w in ['credit', 'income', 'received', 'cr', 'deposit']):
                    t_type = 'income'
                elif any(w in raw_type for w in ['debit', 'expense', 'paid', 'dr', 'withdrawal']):
                    t_type = 'expense'
                elif any(w in desc.lower() for w in ['received from', 'refund from', 'cashback', 'credited']):
                    t_type = 'income'
                else:
                    t_type = 'expense'

            # 4. Category & Expense Type
            cat = str(row['category']).strip() if 'category' in row and pd.notna(row['category']) and str(row['category']).strip() else categorize_transaction(desc)
            exp_type = classify_expense_type(desc, amt, cat)

            # 5. Payment mode
            mode_raw = str(row.get('payment_mode', '')).strip().upper()
            if 'CASH' in mode_raw: mode = 'Cash'
            elif 'CARD' in mode_raw: mode = 'Card'
            elif 'BANK' in mode_raw or 'TRANSFER' in mode_raw: mode = 'Bank Transfer'
            else: mode = 'UPI'

            transactions.append({
                'user_id': user_id,
                'date': date_str,
                'description': desc,
                'amount': amt,
                'type': t_type,
                'category': cat,
                'expense_type': exp_type,
                'payment_mode': mode
            })
        except Exception:
            skipped += 1
            continue

    return transactions, len(transactions), skipped, []
