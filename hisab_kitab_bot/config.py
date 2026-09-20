import os

# Telegram Bot Credentials (Supports environment variables for cloud deployment like Render)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8821510338:AAEO5qpjTlSQ-nIYeFJ1JE0XHSkafiGEmhE")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Hisab_Kitab_1Bot")

# Deals Fetcher Branding & Affiliate Link
DEALS_FETCHER_URL = "https://dealsfetcher.blogspot.com"

# Telegram Stars Configuration (Official Telegram In-App Currency)
STARS_PDF_PRICE = 15      # 15 Stars for Single PDF statement
STARS_EXCEL_PRICE = 15    # 15 Stars for Single Excel (.xlsx) statement
STARS_BUNDLE_PRICE = 25   # 25 Stars for Combo Bundle (Both PDF + Excel)

# 7 Special Countries & Their Official Telegram Deals Channels
# Month 2 is 100% Free if user stays joined in their country channel!
COUNTRY_CHANNELS = {
    "IN": {
        "name": "India",
        "flag": "🇮🇳",
        "channel_username": "@DealsFetcher",
        "channel_url": "https://t.me/DealsFetcher",
        "title": "Deals Fetcher 🇮🇳"
    },
    "US": {
        "name": "United States",
        "flag": "🇺🇸",
        "channel_username": "@ApexDealsDaily",
        "channel_url": "https://t.me/ApexDealsDaily",
        "title": "Apex Deals Daily 🇺🇸"
    },
    "IT": {
        "name": "Italy",
        "flag": "🇮🇹",
        "channel_username": "@AffariImperdibili",
        "channel_url": "https://t.me/AffariImperdibili",
        "title": "Affari Imperdibili 🇮🇹"
    },
    "ES": {
        "name": "Spain",
        "flag": "🇪🇸",
        "channel_username": "@ChollosAlDiaES",
        "channel_url": "https://t.me/ChollosAlDiaES",
        "title": "Chollos Al Día 🇪🇸"
    },
    "GB": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "channel_username": "@TheCrownDeals",
        "channel_url": "https://t.me/TheCrownDeals",
        "title": "The Crown Deals 🇬🇧"
    },
    "DE": {
        "name": "Germany",
        "flag": "🇩🇪",
        "channel_username": "@Sparangebote",
        "channel_url": "https://t.me/Sparangebote",
        "title": "Sparangebote 🇩🇪"
    },
    "FR": {
        "name": "France",
        "flag": "🇫🇷",
        "channel_username": "@MaxiOffres",
        "channel_url": "https://t.me/MaxiOffres",
        "title": "Maxi Offres 🇫🇷"
    },
}

# VIP Monthly Pass Pricing in Telegram Stars (1 to 12 Months)
MONTHLY_PASS_PRICING = {
    1: 25,
    2: 50,
    3: 70,   # Save 5 Stars
    4: 95,
    5: 115,
    6: 130,  # Save 20 Stars
    7: 155,
    8: 175,
    9: 190,  # Save 35 Stars
    10: 210,
    11: 225,
    12: 240  # Save 60 Stars (Best Value: Only 20 Stars/month)
}

def get_stars_price_for_months(months: int) -> int:
    months = max(1, min(12, int(months)))
    return MONTHLY_PASS_PRICING.get(months, months * 25)

def get_country_channel_info(country_code: str):
    if not country_code:
        return None
    return COUNTRY_CHANNELS.get(country_code.upper(), None)

# Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hisab_kitab.db")
PDF_TEMP_DIR = os.path.join(BASE_DIR, "generated_pdfs")
os.makedirs(PDF_TEMP_DIR, exist_ok=True)
