# 💰 Hisab-Kitab Telegram Bot (@Hisab_Kitab_1Bot)

An advanced, international personal finance, expense tracker, and khata/ledger management Telegram bot supporting **19 languages**, **180+ global currencies**, PDF/Excel statement exports, client khata ledgers, budget tracking, and an integrated VIP membership system linked with 7 country shopping deals channels.

---

## 🌟 Key Features

1. **Daily Expense & Income Tracking**:
   - Natural language and voice transcription parsing (e.g., `chai 20`, `petrol 100`, `salary +50000`).
   - Category breakdowns with visual progress indicators and monthly budget tracking.
2. **Client Khata / Ledger (उधारी एवं जमा)**:
   - Manage unlimited clients, record Got (जमा) and Gave (उधार) transactions with real-time running balances.
   - Date and time stamped ledger entries with complete debit/credit calculation.
3. **Statement Exports**:
   - Executive PDF statements with custom date ranges.
   - Detailed Excel spreadsheets (`.xlsx`) with transaction histories and client reports.
4. **VIP Pass & 3-Month Free Trial System**:
   - **Month 1 (30 Days)**: 100% Free Trial awarded on registration with an automatic *"You are Lucky!"* announcement.
   - **Month 2 (30 Days)**: 100% Free Pass for joining your country's official shopping deals channel.
   - **Month 3 (30 Days)**: 100% Free Pass for sharing your country's shopping channel with 10 friends.
   - Total of **3 Full Months (90 Days) Free VIP Access**!
5. **Country & Language Isolation**:
   - Localized menus and currencies.
   - Exclusive `🔥 Today's Loot Deals` button strictly visible for India (`IN`) users.
   - Single country deals channel confinement: no user is exposed to all 7 channels together.
6. **7 Supported Country Shopping Channels**:
   - 🇮🇳 India: `@DealsFetcher` (`https://t.me/DealsFetcher`)
   - 🇺🇸 USA: `@ApexDealsDaily` (`https://t.me/ApexDealsDaily`)
   - 🇮🇹 Italy: `@AffariImperdibili` (`https://t.me/AffariImperdibili`)
   - 🇪🇸 Spain: `@ChollosAlDiaES` (`https://t.me/ChollosAlDiaES`)
   - 🇬🇧 UK: `@TheCrownDeals` (`https://t.me/TheCrownDeals`)
   - 🇩🇪 Germany: `@Sparangebote` (`https://t.me/Sparangebote`)
   - 🇫🇷 France: `@MaxiOffres` (`https://t.me/MaxiOffres`)

---

## 📂 Project Structure

```
Hisab Kitab/
├── hisab_kitab_bot/           # Main Python package
│   ├── bot.py                 # Bot handlers, UI keyboards, command routers
│   ├── config.py              # Configuration constants, tokens, channel links
│   ├── countries.py           # Supported countries, currencies, and languages
│   ├── database.py            # SQLite database schema, operations & VIP tiers
│   ├── excel_generator.py     # Excel (.xlsx) statement & client report engine
│   ├── i18n.py                # 19-language translations & dynamic keyboard builders
│   ├── parser.py              # Text and voice transaction parsing logic
│   ├── pdf_generator.py       # PDF report generation engine
│   ├── hisab_kitab.db         # Live SQLite database
│   └── generated_pdfs/        # Temporary statement cache directory
├── tests/                     # 13 Automated test suites
├── .env                       # Environment configuration
├── .env.example               # Template environment configuration
├── requirements.txt           # Python dependencies
├── start.bat                  # One-click Windows starter
├── start_hisab_kitab_bot.bat  # Alternative batch launcher
└── README.md                  # This documentation
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10 or newer

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Bot
Double-click `start.bat` or run in terminal:
```bash
python -m hisab_kitab_bot.bot
```

---

## 🧪 Running Tests

Run any of the 13 automated tests from the `Hisab Kitab` folder:
```bash
python tests/test_all_7_countries_shopping_channel_url.py
python tests/test_lucky_vip_and_shopping_share.py
python tests/test_full_client_reports.py
```
