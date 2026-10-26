
import numpy as np
from database import get_db_connection

def detect_anomalies_for_user(user_id):
    """Flags unusual transactions using statistical Z-Score: Z = (X - mean) / std_dev."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, category, amount FROM transactions WHERE user_id = %s AND type = 'expense'", (user_id,))
    txs = cursor.fetchall()

    cat_map = {}
    for t in txs:
        cat_map.setdefault(t['category'], []).append((t['id'], float(t['amount'])))

    anomalies = []
    for cat, items in cat_map.items():
        if len(items) > 1:
            amts = [amt for _, amt in items]
            m, s = float(np.mean(amts)), float(np.std(amts))
            if s > 0:
                for tx_id, amt in items:
                    if abs((amt - m) / s) > 2.0:  # |Z| > 2 is an outlier
                        anomalies.append(tx_id)

    cursor.execute("UPDATE transactions SET is_unusual = 0 WHERE user_id = %s", (user_id,))
    if anomalies:
        fmt = ','.join(['%s'] * len(anomalies))
        cursor.execute(f"UPDATE transactions SET is_unusual = 1 WHERE id IN ({fmt})", tuple(anomalies))
        conn.commit()
    conn.close()
    return get_unusual_transactions(user_id)

def get_unusual_transactions(user_id, limit=10):
    """Fetches transactions flagged as unusual."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id = %s AND is_unusual = 1 ORDER BY date DESC LIMIT %s", (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    for r in rows:
        r['amount'] = float(r['amount'])
        r['date'] = str(r['date'])
    return rows
