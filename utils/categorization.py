
# Uses dictionary lookup and keyword search to categorize spending.

CATEGORY_KEYWORDS = {
    'Food': [
        # Food delivery
        'swiggy', 'zomato', 'magicpin', 'eatsure', 'eat sure','dominos', 'domino', 'mcdonald', 'kfc', 'burger king','pizza hut', 'subway', 'faasos', 'behrouz', 'oven story','box8', 'biryani by kilo', 'wow momo', 'wow china',

        # Indian restaurants and cafes
        'restaurant', 'hotel food', 'dhaba', 'bhojanalaya',
        'mess', 'canteen', 'tiffin', 'dabba', 'catering',
        'biryani', 'thali', 'misal', 'vada pav', 'pav bhaji',
        'panipuri', 'pani puri', 'golgappa', 'chaat',
        'samosa', 'kachori', 'poha', 'dosa', 'idli',
        'paratha', 'roti', 'naan', 'chinese food',
        'chai point', 'chaayos', 'chai sutta bar',
        'chayos', 'starbucks', 'cafe coffee day', 'ccd',
        'barista', 'third wave coffee', 'irani cafe',
        'bakery', 'mithai', 'sweet shop', 'haldiram',
        'bikanervala', 'bikaji', 'naturals ice cream',
        'amul ice cream', 'kwality walls',

        # Local food purchases
        'tea stall', 'chai tapri', 'juice center', 'juice centre',
        'fruit juice', 'sugarcane juice', 'nasta', 'nashta',
        'breakfast', 'lunch', 'dinner', 'snacks', 'food court',
        'ice cream', 'milkshake', 'falooda', 'kulfi',
        'paan shop', 'paanwala', 'paan',
        'milk', 'dairy', 'doodh', 'curd', 'dahi',
        'paneer', 'eggs', 'egg shop', 'chicken shop',
        'mutton shop', 'fish market', 'meat shop',
        'fruits', 'vegetables', 'sabzi', 'bhaji',
        'coconut water', 'nariyal pani'
    ],

    'Transport': [
        # Cab and bike
        'uber', 'ola', 'rapido', 'namma yatri', 'nammayatri',
        'inDrive', 'blusmart', 'auto rickshaw', 'rickshaw',
        'taxi', 'cab', 'bike taxi',

        # Public transport
        'maha metro', 'pune metro', 'mumbai metro',
        'metro card', 'chalo', 'best bus', 'msrtc',
        'shivneri', 'neeta bus', 'redbus', 'abhibus',
        'irctc', 'indian railway', 'railway', 'rail ticket',
        'local train', 'suburban railway', 'bus ticket',
        'bus pass', 'railway station',

        # Vehicle expenses
        'petrol pump', 'petrol', 'diesel', 'cng',
        'fuel', 'hp pay', 'indian oil', 'bharat petroleum',
        'hindustan petroleum', 'nayara energy',
        'fastag', 'toll plaza', 'toll', 'parking',
        'vehicle service', 'car wash', 'bike service',
        'puncture', 'tyre', 'tyres', 'automobile',
        'driving school', 'driving licence', 'rto'
    ],

    'Shopping': [
        # E-commerce
        'amazon', 'flipkart', 'myntra', 'ajio', 'meesho',
        'nykaa', 'tatacliq', 'tata cliq', 'snapdeal',
        'shopsy', 'jiomart', 'jio mart', 'firstcry',
        'industrybuying', 'blinkit', 'zepto', 'instamart',
        'bigbasket', 'big basket', 'dmart ready',

        # Indian retail chains
        'dmart', 'd mart', 'reliance smart', 'reliance trends',
        'reliance digital', 'vishal mega mart', 'max fashion',
        'westside', 'pantaloons', 'shoppers stop',
        'lifestyle', 'zudio', 'decathlon', 'ikea',
        'croma', 'vijay sales', 'poorvika', 'sangeetha mobiles',
        'tanishq', 'malabar gold', 'kalyan jewellers',
        'jewellery', 'jewelry', 'gold shop', 'silver shop',

        # Local Indian stores
        'kirana', 'kirana store', 'general store',
        'provision store', 'provisions', 'grocery',
        'grocery store', 'supermarket', 'departmental store',
        'medical general store', 'stationery shop',
        'clothing store', 'garments', 'readymade garments',
        'mens wear', 'ladies wear', 'footwear',
        'shoe shop', 'tailor', 'tailoring',
        'cosmetics', 'beauty products', 'utensils',
        'hardware store', 'electrical shop',
        'mobile shop', 'mobile accessories',
        'furniture shop', 'home decor', 'plastic store',
        'bangle shop', 'gift shop', 'toy shop',
        'market', 'bazaar', 'mall', 'retail store'
    ],

    'Entertainment': [
        # OTT and subscriptions
        'netflix', 'amazon prime video', 'prime video',
        'hotstar', 'jiohotstar', 'sony liv', 'sonyliv',
        'zee5', 'zee5', 'aha', 'shemaroo', 'hoichoi',
        'lionsgate play', 'mubi', 'youtube premium',
        'spotify', 'gaana', 'jiosaavn', 'wynk',
        'apple music', 'audible',

        # Cinema and activities
        'pvr', 'inox', 'cinepolis', 'bookmyshow',
        'district by zomato', 'movie ticket', 'cinema',
        'multiplex', 'theatre', 'theater',
        'bowling', 'arcade', 'gaming cafe',
        'game zone', 'amusement park', 'water park',
        'imagicaa', 'esselworld', 'wonderla',
        'escape room', 'concert', 'live show',
        'comedy show', 'standup comedy', 'stand-up comedy',
        'pub entry', 'club entry', 'karaoke',
        'playstation', 'steam', 'epic games',
        'play store games', 'in-app purchase',
        'bgmi', 'free fire', 'roblox'
    ],

    'Bills': [
        # Utilities
        'electricity bill', 'electricity', 'mahavitaran',
        'mseb', 'msedcl', 'best electricity',
        'water bill', 'municipal water', 'gas bill',
        'mahanagar gas', 'mgl', 'adani gas',
        'igl', 'piped gas', 'lpg', 'indane',
        'bharat gas', 'hp gas', 'cylinder booking',

        # Mobile and internet
        'jio recharge', 'airtel recharge', 'vi recharge',
        'vodafone idea', 'bsnl', 'jio fiber', 'jiofiber',
        'airtel xstream', 'airtel broadband',
        'tata play', 'dish tv', 'd2h',
        'broadband', 'wifi bill', 'internet bill',
        'mobile recharge', 'prepaid recharge',
        'postpaid bill', 'telephone bill',

        # Financial obligations and services
        'loan emi', 'home loan', 'car loan',
        'personal loan', 'credit card bill',
        'credit card payment', 'insurance premium',
        'life insurance', 'lic premium',
        'health insurance premium', 'term insurance',
        'society maintenance', 'maintenance charge',
        'rent payment', 'house rent', 'property tax',
        'municipal tax', 'water tax',
        'google cloud', 'aws', 'azure',
        'domain renewal', 'hosting renewal',
        'google one', 'icloud storage',
        'annual fee', 'bank charges', 'processing fee',
        'late payment fee', 'overdraft fee'
    ],

    'Education': [
        # Educational institutions
        'college fee', 'college fees', 'school fee',
        'school fees', 'tuition fee', 'tuition fees',
        'admission fee', 'exam fee', 'exam fees',
        'university fee', 'hostel fee', 'semester fee',
        'coaching class', 'coaching centre',
        'classes', 'lectures', 'private tutor',
        'online tuition', 'competitive exam',

        # Indian education platforms
        'nptel', 'swayam', 'iit madras', 'coursera',
        'udemy', 'edx', 'unacademy', 'testbook',
        'physics wallah', 'pw', 'adda247',
        'vedantu', 'byjus', 'chegg',
        'leetcode', 'hackerrank', 'geeksforgeeks',
        'skillshare', 'linkedin learning',

        # Books and supplies
        'bookstore', 'book shop', 'textbook',
        'notebook', 'stationery', 'xerox',
        'photocopy', 'printing shop', 'lamination',
        'library fee', 'lab fee', 'project fee',
        'calculator', 'educational material'
    ],

    'Health': [
        # Pharmacies and hospitals
        'apollo pharmacy', 'medplus', 'netmeds',
        'pharmeasy', '1mg', 'tata 1mg',
        'wellness forever', 'wellness forever',
        'jan aushadhi', 'generic medicine',
        'medical store', 'chemist', 'pharmacy',
        'hospital', 'clinic', 'doctor consultation',
        'diagnostic centre', 'diagnostic center',
        'pathology lab', 'blood test', 'health checkup',
        'thyrocare', 'lal pathlabs', 'dr lal pathlabs',
        'metropolis healthcare', 'suburban diagnostics',

        # Fitness and personal care
        'cult fit', 'cultfit', 'gold gym', 'gym membership',
        'fitness centre', 'fitness center', 'yoga class',
        'yoga studio', 'personal trainer',
        'physiotherapy', 'dentist', 'dental clinic',
        'eye hospital', 'optician', 'spectacles',
        'contact lenses', 'hearing aid',
        'salon', 'barber', 'haircut',
        'beauty parlour', 'beauty parlor',
        'spa', 'massage', 'skincare',
        'healthcare', 'vaccination', 'medical test'
    ],

    'Travel': [
        # Flights and booking
        'makemytrip', 'make my trip', 'goibibo',
        'cleartrip', 'ixigo', 'yatra', 'easemytrip',
        'air india', 'indigo', 'akasa air',
        'spicejet', 'vistara', 'air india express',
        'flight ticket', 'airport transfer',
        'booking.com', 'airbnb', 'oyo',
        'goa trip', 'hotel booking', 'resort booking',
        'hostelworld', 'agoda', 'trivago',
        'irctc tourism', 'bharat gaurav',
        'tour package', 'travel agency',
        'visa fee', 'passport fee',
        'forex', 'foreign exchange',
        'holiday package', 'sightseeing',
        'resort', 'homestay', 'guest house'
    ]
}
def categorize_transaction(desc):
    """Matches keywords in description to return category."""
    if not desc: return 'Other'
    d = str(desc).lower()
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in d for w in words):
            return cat
    return 'Other'
