import re
from typing import Optional, Tuple

# Ordered by priority
CATEGORY_RULES = {
    "🎬 Entertainment & Leisure": [
        "movie", "cinema", "theatre", "theater", "netflix", "prime", "hotstar",
        "party", "pub", "club", "game", "gaming", "outing", "trip", "fun"
    ],
    "🍔 Food & Dining": [
        "chai", "tea", "coffee", "breakfast", "lunch", "dinner", "snack", "snacks",
        "samosa", "maggie", "maggi", "pizza", "burger", "biryani", "roti", "hotel",
        "restaurant", "dhaba", "zomato", "swiggy", "biscuit", "egg", "ice cream", "water",
        "sweets", "mithai", "cold drink"
    ],
    "⛽ Travel & Commute": [
        "petrol", "diesel", "fuel", "cng", "auto", "rickshaw", "ola", "uber",
        "rapido", "bus", "train", "metro", "bus ticket", "train ticket", "toll", "parking", "flight", "cab"
    ],
    "🛒 Groceries & Ration": [
        "ration", "grocery", "groceries", "sabji", "vegetables", "fruit", "fruits",
        "milk", "dudh", "doodh", "paneer", "dahi", "oil", "tel", "atta", "chawal", "rice",
        "dukan", "shop", "supermarket", "blinkit", "zepto", "instamart"
    ],
    "🛍️ Shopping & Lifestyle": [
        "shopping", "clothes", "kapde", "shirt", "pant", "shoes", "chappal", "sandals",
        "amazon", "flipkart", "myntra", "meesho", "ajio", "gift", "watch", "perfume"
    ],
    "💡 Bills & Utilities": [
        "recharge", "mobile", "wifi", "internet", "electricity", "bijli", "water bill",
        "gas", "cylinder", "rent", "room rent", "flat rent", "emi", "loan", "broadband"
    ],
    "💊 Health & Medical": [
        "medicine", "dawa", "dawakhana", "doctor", "hospital", "clinic", "test", "tablet",
        "syrup", "medical", "pharmacy", "dentist"
    ],
    "💼 Personal Care & Grooming": [
        "haircut", "salon", "barber", "shave", "facial", "parlour", "soap", "shampoo"
    ]
}

INCOME_KEYWORDS = [
    "salary", "income", "received", "credited", "payment received", "freelance",
    "profit", "cashback", "refund", "bonus", "diwali bonus"
]

def parse_expense_text(text: str) -> Optional[Tuple[float, str, str, str]]:
    cleaned = text.strip()
    if not cleaned:
        return None

    is_income = False
    if cleaned.startswith("+"):
        is_income = True
        cleaned = cleaned[1:].strip()

    # Matches global currency prefix/suffix: $, €, £, ¥, ₹, ₽, ₺, ₦, ₨, ৳, ₱, ₫, Rp, AED, SAR, USD, EUR, INR, etc.
    currency_pattern = r'(?:\$|€|£|¥|₹|₽|₺|₦|₨|৳|₱|₫|rp\.?|aed|sar|egp|inr|usd|eur|gbp|rub|try|brl|cad|aud|rs\.?)\s*'
    
    # Try finding number with optional currency prefix
    matches = list(re.finditer(rf'(?:{currency_pattern})?(\d+(?:\.\d{{1,2}})?)|\b(\d+(?:\.\d{{1,2}})?)\s*(?:{currency_pattern})?', cleaned, re.IGNORECASE))
    if not matches:
        return None

    amount_match = None
    amount = 0.0
    for m in matches:
        val_str = m.group(1) or m.group(2)
        if val_str:
            try:
                val = float(val_str)
                if val > 0:
                    amount_match = m
                    amount = val
                    break
            except ValueError:
                continue

    if not amount_match or amount <= 0:
        return None

    start, end = amount_match.span()
    note_part = (cleaned[:start] + " " + cleaned[end:]).strip()
    # Strip any dangling currency symbols from note
    note_part = re.sub(rf'\b{currency_pattern}', '', note_part, flags=re.IGNORECASE).strip()
    note_part = re.sub(r'[\$€£¥₹₽₺₦₨৳₱₫]', '', note_part).strip()
    note = note_part if note_part else "General Expense"

    note_lower = note.lower()
    
    if is_income or any(ik in note_lower for ik in INCOME_KEYWORDS):
        return (amount, "💰 Income", note, "income")

    category = "📦 Other"
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', note_lower):
                category = cat
                break
        if category != "📦 Other":
            break

    return (amount, category, note, "expense")
