import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

COUNTRIES = {
    "IN": {
        "name": "India",
        "flag": "🇮🇳",
        "currency_code": "INR",
        "currency_symbol": "₹",
        "languages": [("en", "🇬🇧 English"), ("hi", "🇮🇳 हिंदी (Hindi)"), ("bn", "🇧🇩 বাংলা (Bengali)")],
    },
    "US": {
        "name": "United States",
        "flag": "🇺🇸",
        "currency_code": "USD",
        "currency_symbol": "$",
        "languages": [("en", "🇬🇧 English"), ("es", "🇪🇸 Español")],
    },
    "GB": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "currency_code": "GBP",
        "currency_symbol": "£",
        "languages": [("en", "🇬🇧 English")],
    },
    "EU": {
        "name": "Eurozone (EU)",
        "flag": "🇪🇺",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "languages": [
            ("en", "🇬🇧 English"),
            ("de", "🇩🇪 Deutsch"),
            ("fr", "🇫🇷 Français"),
            ("es", "🇪🇸 Español"),
            ("it", "🇮🇹 Italiano")
        ],
    },
    "RU": {
        "name": "Russia",
        "flag": "🇷🇺",
        "currency_code": "RUB",
        "currency_symbol": "₽",
        "languages": [("en", "🇬🇧 English"), ("ru", "🇷🇺 Русский")],
    },
    "BR": {
        "name": "Brazil",
        "flag": "🇧🇷",
        "currency_code": "BRL",
        "currency_symbol": "R$",
        "languages": [("en", "🇬🇧 English"), ("pt", "🇧🇷 Português")],
    },
    "ID": {
        "name": "Indonesia",
        "flag": "🇮🇩",
        "currency_code": "IDR",
        "currency_symbol": "Rp",
        "languages": [("en", "🇬🇧 English"), ("id", "🇮🇩 Bahasa Indonesia")],
    },
    "AE": {
        "name": "UAE (Emirates)",
        "flag": "🇦🇪",
        "currency_code": "AED",
        "currency_symbol": "AED",
        "languages": [("en", "🇬🇧 English"), ("ar", "🇸🇦 العربية (Arabic)")],
    },
    "SA": {
        "name": "Saudi Arabia",
        "flag": "🇸🇦",
        "currency_code": "SAR",
        "currency_symbol": "SAR",
        "languages": [("en", "🇬🇧 English"), ("ar", "🇸🇦 العربية (Arabic)")],
    },
    "EG": {
        "name": "Egypt",
        "flag": "🇪🇬",
        "currency_code": "EGP",
        "currency_symbol": "EGP",
        "languages": [("en", "🇬🇧 English"), ("ar", "🇪🇬 العربية (Arabic)")],
    },
    "TR": {
        "name": "Turkey",
        "flag": "🇹🇷",
        "currency_code": "TRY",
        "currency_symbol": "₺",
        "languages": [("en", "🇬🇧 English"), ("tr", "🇹🇷 Türkçe")],
    },
    "NG": {
        "name": "Nigeria",
        "flag": "🇳🇬",
        "currency_code": "NGN",
        "currency_symbol": "₦",
        "languages": [("en", "🇬🇧 English")],
    },
    "PK": {
        "name": "Pakistan",
        "flag": "🇵🇰",
        "currency_code": "PKR",
        "currency_symbol": "₨",
        "languages": [("en", "🇬🇧 English"), ("ur", "🇵🇰 اردو (Urdu)")],
    },
    "BD": {
        "name": "Bangladesh",
        "flag": "🇧🇩",
        "currency_code": "BDT",
        "currency_symbol": "৳",
        "languages": [("en", "🇬🇧 English"), ("bn", "🇧🇩 বাংলা (Bengali)")],
    },
    "PH": {
        "name": "Philippines",
        "flag": "🇵🇭",
        "currency_code": "PHP",
        "currency_symbol": "₱",
        "languages": [("en", "🇬🇧 English")],
    },
    "VN": {
        "name": "Vietnam",
        "flag": "🇻🇳",
        "currency_code": "VND",
        "currency_symbol": "₫",
        "languages": [("en", "🇬🇧 English"), ("vi", "🇻🇳 Tiếng Việt")],
    },
    "MX": {
        "name": "Mexico",
        "flag": "🇲🇽",
        "currency_code": "MXN",
        "currency_symbol": "$",
        "languages": [("en", "🇬🇧 English"), ("es", "🇪🇸 Español")],
    },
    "CA": {
        "name": "Canada",
        "flag": "🇨🇦",
        "currency_code": "CAD",
        "currency_symbol": "CA$",
        "languages": [("en", "🇬🇧 English"), ("fr", "🇫🇷 Français")],
    },
    "AU": {
        "name": "Australia",
        "flag": "🇦🇺",
        "currency_code": "AUD",
        "currency_symbol": "AU$",
        "languages": [("en", "🇬🇧 English")],
    },
    "DE": {
        "name": "Germany",
        "flag": "🇩🇪",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "languages": [("en", "🇬🇧 English"), ("de", "🇩🇪 Deutsch")],
    },
    "FR": {
        "name": "France",
        "flag": "🇫🇷",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "languages": [("en", "🇬🇧 English"), ("fr", "🇫🇷 Français")],
    },
    "ES": {
        "name": "Spain",
        "flag": "🇪🇸",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "languages": [("en", "🇬🇧 English"), ("es", "🇪🇸 Español")],
    },
    "IT": {
        "name": "Italy",
        "flag": "🇮🇹",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "languages": [("en", "🇬🇧 English"), ("it", "🇮🇹 Italiano")],
    },
    "JP": {
        "name": "Japan",
        "flag": "🇯🇵",
        "currency_code": "JPY",
        "currency_symbol": "¥",
        "languages": [("en", "🇬🇧 English"), ("ja", "🇯🇵 日本語")],
    },
    "KR": {
        "name": "South Korea",
        "flag": "🇰🇷",
        "currency_code": "KRW",
        "currency_symbol": "₩",
        "languages": [("en", "🇬🇧 English"), ("ko", "🇰🇷 한국어")],
    },
    "ZA": {
        "name": "South Africa",
        "flag": "🇿🇦",
        "currency_code": "ZAR",
        "currency_symbol": "R",
        "languages": [("en", "🇬🇧 English")],
    },
    "KE": {
        "name": "Kenya",
        "flag": "🇰🇪",
        "currency_code": "KES",
        "currency_symbol": "KSh",
        "languages": [("en", "🇬🇧 English")],
    },
    "MY": {
        "name": "Malaysia",
        "flag": "🇲🇾",
        "currency_code": "MYR",
        "currency_symbol": "RM",
        "languages": [("en", "🇬🇧 English")],
    },
    "SG": {
        "name": "Singapore",
        "flag": "🇸🇬",
        "currency_code": "SGD",
        "currency_symbol": "S$",
        "languages": [("en", "🇬🇧 English")],
    },
    "AR": {
        "name": "Argentina",
        "flag": "🇦🇷",
        "currency_code": "ARS",
        "currency_symbol": "$",
        "languages": [("en", "🇬🇧 English"), ("es", "🇪🇸 Español")],
    },
    "CO": {
        "name": "Colombia",
        "flag": "🇨🇴",
        "currency_code": "COP",
        "currency_symbol": "$",
        "languages": [("en", "🇬🇧 English"), ("es", "🇪🇸 Español")],
    },
    "UA": {
        "name": "Ukraine",
        "flag": "🇺🇦",
        "currency_code": "UAH",
        "currency_symbol": "₴",
        "languages": [("en", "🇬🇧 English"), ("uk", "🇺🇦 Українська"), ("ru", "🇷🇺 Русский")],
    },
    "KZ": {
        "name": "Kazakhstan",
        "flag": "🇰🇿",
        "currency_code": "KZT",
        "currency_symbol": "₸",
        "languages": [("en", "🇬🇧 English"), ("ru", "🇷🇺 Русский"), ("kk", "🇰🇿 Қазақша")],
    },
    "UZ": {
        "name": "Uzbekistan",
        "flag": "🇺🇿",
        "currency_code": "UZS",
        "currency_symbol": "so'm",
        "languages": [("en", "🇬🇧 English"), ("uz", "🇺🇿 Oʻzbek"), ("ru", "🇷🇺 Русский")],
    },
    "GLOBAL": {
        "name": "Other / Worldwide",
        "flag": "🌐",
        "currency_code": "USD",
        "currency_symbol": "$",
        "languages": [("en", "🇬🇧 English")],
    },
}

ALL_SUPPORTED_LANGUAGES = [
    ("en", "🇬🇧 English (Global)"),
    ("hi", "🇮🇳 हिंदी (Hindi)"),
    ("ru", "🇷🇺 Русский (Russian)"),
    ("es", "🇪🇸 Español (Spanish)"),
    ("pt", "🇧🇷 Português (Portuguese)"),
    ("ar", "🇸🇦 العربية (Arabic)"),
    ("id", "🇮🇩 Bahasa Indonesia"),
    ("fr", "🇫🇷 Français (French)"),
    ("de", "🇩🇪 Deutsch (German)"),
    ("it", "🇮🇹 Italiano (Italian)"),
    ("tr", "🇹🇷 Türkçe (Turkish)"),
    ("bn", "🇧🇩 বাংলা (Bengali)"),
    ("ur", "🇵🇰 اردو (Urdu)"),
    ("vi", "🇻🇳 Tiếng Việt (Vietnamese)"),
    ("ja", "🇯🇵 日本語 (Japanese)"),
    ("ko", "🇰🇷 한국어 (Korean)"),
    ("uk", "🇺🇦 Українська (Ukrainian)"),
    ("uz", "🇺🇿 Oʻzbek (Uzbek)"),
    ("kk", "🇰🇿 Қазақша (Kazakh)"),
]

def get_country(code: str) -> dict:
    return COUNTRIES.get(code.upper(), COUNTRIES["GLOBAL"])

def get_country_select_keyboard(page: int = 0, per_page: int = 8, show_back: bool = True) -> InlineKeyboardMarkup:
    """
    Renders an inline keyboard with countries in 2 columns and clean pagination.
    """
    country_keys = list(COUNTRIES.keys())
    total_items = len(country_keys)
    total_pages = max(1, math.ceil(total_items / per_page))
    page = max(0, min(page, total_pages - 1))

    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total_items)
    page_keys = country_keys[start_idx:end_idx]

    rows = []
    # Build 2 columns per row
    for i in range(0, len(page_keys), 2):
        row = []
        c1_key = page_keys[i]
        c1 = COUNTRIES[c1_key]
        row.append(InlineKeyboardButton(
            f"{c1['flag']} {c1['name']} ({c1['currency_symbol']})",
            callback_data=f"setcountry_{c1_key}"
        ))

        if i + 1 < len(page_keys):
            c2_key = page_keys[i + 1]
            c2 = COUNTRIES[c2_key]
            row.append(InlineKeyboardButton(
                f"{c2['flag']} {c2['name']} ({c2['currency_symbol']})",
                callback_data=f"setcountry_{c2_key}"
            ))
        rows.append(row)

    # Navigation Row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⏪ Prev", callback_data=f"cpage_{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"📍 {page + 1}/{total_pages}", callback_data="cpage_noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ⏩", callback_data=f"cpage_{page + 1}"))

    rows.append(nav_row)

    if show_back:
        rows.append([
            InlineKeyboardButton("🔙 Main Menu (मुख्य मेनू)", callback_data="back_to_main")
        ])

    return InlineKeyboardMarkup(rows)

def get_country_languages_keyboard(country_code: str, prefix: str = "initlang", show_back: bool = True) -> InlineKeyboardMarkup:
    """
    Returns language buttons for a selected country with English as default.
    Also includes a button to view all available languages.
    """
    country = get_country(country_code)
    langs = country.get("languages", [("en", "🇬🇧 English")])

    rows = []
    # Two language buttons per row
    for i in range(0, len(langs), 2):
        row = []
        code1, name1 = langs[i]
        row.append(InlineKeyboardButton(name1, callback_data=f"{prefix}_{code1}"))
        if i + 1 < len(langs):
            code2, name2 = langs[i + 1]
            row.append(InlineKeyboardButton(name2, callback_data=f"{prefix}_{code2}"))
        rows.append(row)

    # Option to view all languages
    rows.append([
        InlineKeyboardButton("🌐 View All Languages", callback_data=f"{prefix}_more_{country_code}")
    ])

    if show_back and prefix == "setlang":
        rows.append([
            InlineKeyboardButton("🔙 Back to Settings", callback_data="open_settings"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")
        ])

    return InlineKeyboardMarkup(rows)

def get_all_languages_keyboard(prefix: str = "initlang", country_code: str = "IN") -> InlineKeyboardMarkup:
    """
    Returns an inline keyboard with all supported global languages.
    """
    rows = []
    for i in range(0, len(ALL_SUPPORTED_LANGUAGES), 2):
        row = []
        code1, name1 = ALL_SUPPORTED_LANGUAGES[i]
        row.append(InlineKeyboardButton(name1, callback_data=f"{prefix}_{code1}"))
        if i + 1 < len(ALL_SUPPORTED_LANGUAGES):
            code2, name2 = ALL_SUPPORTED_LANGUAGES[i + 1]
            row.append(InlineKeyboardButton(name2, callback_data=f"{prefix}_{code2}"))
        rows.append(row)

    if prefix == "setlang":
        rows.append([
            InlineKeyboardButton("🔙 Back to Country Languages", callback_data="open_language_picker"),
            InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")
        ])
    else:
        rows.append([
            InlineKeyboardButton("🔙 Back", callback_data=f"back_to_init_langs_{country_code}")
        ])

    return InlineKeyboardMarkup(rows)
