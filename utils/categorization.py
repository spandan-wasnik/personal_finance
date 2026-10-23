# categorization.py - OM'S MODULE: Transaction Categorization
# Uses dictionary lookup and keyword search to categorize spending.

CATEGORY_KEYWORDS = {
    'Food': ['swiggy', 'zomato', 'mcdonald', 'kfc', 'domino', 'pizza', 'cafe', 'restaurant', 'biryani', 'tea', 'coffee', 'burger', 'mess', 'canteen', 'food', 'stall', 'panipuri', 'catering', 'bakery', 'sweets', 'snack', 'dining', 'kitchen', 'mcdelivery', 'fruit', 'juice'],
    'Transport': ['uber', 'ola', 'rapido', 'auto', 'metro', 'bus', 'train', 'petrol', 'fuel', 'fastag', 'irctc', 'petroleum', 'transport', 'cab'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'clothes', 'shoes', 'mall', 'electronics', 'croma', 'store', 'mart', 'mens wear', 'wear', 'bazaar', 'supermarket', 'market', 'provisions', 'retail', 'trading', 'general store'],
    'Entertainment': ['netflix', 'prime', 'hotstar', 'spotify', 'youtube', 'movie', 'cinema', 'pvr', 'inox', 'bookmyshow', 'game', 'gamerz', 'gaming', 'theatre'],
    'Bills': ['electricity', 'water', 'gas', 'recharge', 'wifi', 'internet', 'airtel', 'jio', 'vi', 'bill', 'emi', 'loan', 'maintenance', 'google cloud', 'aws', 'securities', 'angel one', 'zerodha', 'groww', 'insurance', 'sahakari'],
    'Education': ['college', 'school', 'books', 'fee', 'tuition', 'udemy', 'coursera', 'exam', 'library', 'stationery', 'computer', 'classes', 'vidyarthi'],
    'Health': ['hospital', 'clinic', 'doctor', 'medicine', 'pharmacy', 'gym', 'fitness', 'apollo', 'lab', 'medical', 'chemist', 'healthcare'],
    'Travel': ['flight', 'hotel', 'airbnb', 'oyo', 'trip', 'holiday', 'makemytrip', 'booking', 'yatra', 'tour', 'resort']
}

def categorize_transaction(desc):
    """Matches keywords in description to return category."""
    if not desc: return 'Other'
    d = str(desc).lower()
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in d for w in words):
            return cat
    return 'Other'
