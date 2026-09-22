# anomaly_detection.py
# Uses Machine Learning to find unusual transactions (abnormally high amounts).

from sklearn.ensemble import IsolationForest
import numpy as np
from database import get_db_connection

def detect_anomalies_for_user(user_id):
    """
    Finds and flags unusual transactions for a user using IsolationForest or Z-score.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    # Get all expenses grouped by category
    query = "SELECT id, category, amount FROM transactions WHERE user_id = %s AND type = 'expense'"
    cursor.execute(query, (user_id,))
    transactions = cursor.fetchall()
    
    # Group transactions by category
    cat_transactions = {}
    for tx in transactions:
        cat = tx['category']
        if cat not in cat_transactions:
            cat_transactions[cat] = []
        cat_transactions[cat].append({'id': tx['id'], 'amount': float(tx['amount'])})
        
    anomalies = []
    
    for category, items in cat_transactions.items():
        amounts = [item['amount'] for item in items]
        
        # If we have 5 or more, use Machine Learning (IsolationForest)
        if len(items) >= 5:
            # Reshape amounts for sklearn
            X = np.array(amounts).reshape(-1, 1)
            
            # Train IsolationForest
            model = IsolationForest(contamination=0.1, random_state=42)
            preds = model.fit_predict(X)
            
            # preds == -1 means anomaly
            for i, pred in enumerate(preds):
                if pred == -1:
                    anomalies.append(items[i]['id'])
                    
        # If fewer than 5, use simple statistics (Z-score)
        elif len(items) > 1:
            mean_amt = np.mean(amounts)
            std_amt = np.std(amounts)
            
            if std_amt > 0: # Avoid division by zero
                for item in items:
                    z_score = (item['amount'] - mean_amt) / std_amt
                    if abs(z_score) > 2.0: # More than 2 standard deviations away
                        anomalies.append(item['id'])
                        
    # Update database
    if anomalies:
        # First reset all is_unusual flags
        cursor.execute("UPDATE transactions SET is_unusual = 0 WHERE user_id = %s", (user_id,))
        
        # Then set the flag for anomalies
        format_strings = ','.join(['%s'] * len(anomalies))
        update_query = f"UPDATE transactions SET is_unusual = 1 WHERE id IN ({format_strings})"
        cursor.execute(update_query, tuple(anomalies))
        conn.commit()
        
    conn.close()
    
    # Return the updated unusual transactions
    return get_unusual_transactions(user_id)

def get_unusual_transactions(user_id, limit=10):
    """
    Fetches flagged unusual transactions from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM transactions 
        WHERE user_id = %s AND is_unusual = 1 
        ORDER BY date DESC LIMIT %s
    """
    cursor.execute(query, (user_id, limit))
    results = cursor.fetchall()
    
    conn.close()
    
    for row in results:
        row['amount'] = float(row['amount'])
        row['date'] = str(row['date'])
        row['created_at'] = str(row['created_at'])
        
    return results
