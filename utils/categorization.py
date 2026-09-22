# categorization.py
# This file helps categorize transactions based on their description.

CATEGORY_KEYWORDS = {
    'Food': ['swiggy', 'zomato', 'mcdonald', 'kfc', 'domino', 'pizza', 'restaurant', 'cafe', 'food', 'eat', 'dining', 'hotel', 'breakfast', 'lunch', 'dinner', 'snack', 'barbeque', 'burger', 'biryani', 'chai', 'tea', 'coffee', 'bakery', 'sweet'],
    'Transport': ['uber', 'ola', 'rapido', 'auto', 'taxi', 'metro', 'bus', 'train', 'petrol', 'diesel', 'fuel', 'irctc', 'redbus', 'makemytrip transport', 'cab', 'rickshaw'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'nykaa', 'shopping', 'store', 'mall', 'market', 'clothes', 'shoes', 'apparel', 'fashion'],
    'Entertainment': ['netflix', 'amazon prime', 'hotstar', 'spotify', 'youtube', 'movie', 'cinema', 'pvr', 'inox', 'gaming', 'game', 'ticket'],
    'Bills': ['electricity', 'water', 'recharge', 'internet', 'wifi', 'mobile', 'broadband', 'postpaid', 'prepaid', 'bill', 'emi'],
    'Education': ['college', 'university', 'school', 'books', 'course', 'exam', 'fee', 'tuition', 'library', 'study', 'udemy', 'coursera'],
    'Health': ['hospital', 'clinic', 'doctor', 'medicine', 'pharmacy', 'medical', 'health', 'gym', 'fitness'],
    'Travel': ['flight', 'hotel', 'airbnb', 'oyo', 'booking', 'trip', 'holiday', 'vacation', 'makemytrip', 'yatra', 'goibibo']
}

def categorize_transaction(description):
    """
    Takes a transaction description, converts it to lowercase,
    and returns the matching category based on keywords.
    """
    if not description:
        return 'Other'
        
    desc_lower = description.lower()
    
    # Check each category and its keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
                
    # If no keywords match, return 'Other'
    return 'Other'
