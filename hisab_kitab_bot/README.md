# 💰 Hisab-Kitab Telegram Bot (@Hisab_Kitab_1Bot)

Smart Daily Expense & Budget Tracker Bot with Hindi & English Dual Language, Manual Date Range Selection, Single-File Telegram Stars Monetization, Viral Referral Program (Free Statement Downloads), and Deals Fetcher Integration.

---

## 🌟 Key Features

1. **🎁 Viral Referral Program (Free Monthly Statements)**:
   - Every user gets a personal referral link: `https://t.me/Hisab_Kitab_1Bot?start=ref_{user_id}`.
   - For **every 1 friend** who joins using their link, the user automatically earns **1 Free Monthly Statement Download** (PDF + Excel)!
   - Users can check their referral stats and share directly to Telegram via **`🎁 रेफर करें (Free Statement)`** or `/refer`.
   - When downloading a statement, users with free credits can download instantly with 1 tap without spending Telegram Stars!

2. **🗑️ Selective Entry Management (Undo / Delete Anytime)**:
   - Users can choose which specific entry they want to keep or delete at any time.
   - Command `/delete` or button **`🗑️ एंट्री हटाएं (Undo)`** shows an interactive list of recent transactions with individual `[❌]` delete buttons.
   - Direct command: `/delete <id>` or `/undo <id>`.

3. **🗓️ Manual & Custom Date Range Selection**:
   - Choose any period for your statement:
     - 📅 **इस महीने का (This Month)**
     - ⏮️ **पिछले महीने का (Last Month)**
     - 📆 **पिछले 30 दिन (Last 30 Days)**
     - 🗓️ **कस्टम तारीख (Custom Date Range)**: e.g. `01-08-2026 to 15-09-2026`.

4. **⭐ Telegram Stars on Single Files & Combo**:
   - **📄 Single PDF Statement**: 15 Stars (⭐)
   - **📊 Single Excel Sheet (.xlsx)**: 15 Stars (⭐)
   - **📦 Combo Pack (PDF + Excel)**: 25 Stars (⭐) *(Save 5 Stars!)*
   - Monetization triggers official Telegram Stars invoices directly in chat.

5. **🌐 Dual Language Support (Hindi & English)**:
   - Switch between **हिंदी** and **English** at any time using `/language` or button **`🌐 भाषा बदलें (Language)`**.
   - All messages, menus, and summaries dynamically update.

6. **📊 Rich Excel (.xlsx) & PDF Formats**:
   - **Excel Spreadsheet (.xlsx)**: Itemized transactions log, formulas, KPI cards, and category breakdown.
   - **PDF Report**: Professional, print-ready document formatted with ReportLab.

7. **Natural Language Expense Logging**:
   - `Chai 20` ➔ 🍔 Food / Khana-Pina (₹20)
   - `Petrol 150` ➔ ⛽ Travel / Petrol (₹150)
   - `Ration 850` ➔ 🛒 Groceries / Rashan (₹850)
   - `Recharge 299` ➔ 📱 Bills / Recharge (₹299)
   - `+50000 Salary` ➔ 💵 Income / Kamai (₹50,000)

8. **Instant Reports & Budget Alerts**:
   - `/today` or **📊 आज का हिसाब**: Today's itemized entries with transaction IDs.
   - `/month` or **📅 इस महीने का हिसाब**: Visual progress bar + category breakdown.
   - `/budget 15000`: Set a monthly limit with proactive alerts.

9. **Deals Fetcher Affiliate Promotion**:
   - Cross-promotes your Deals Fetcher site to generate affiliate commissions.

10. **Nightly 9:00 PM Summary**:
    - Automated daily notification sent to all active users in their chosen language every evening at 9:00 PM IST (15:30 UTC).

---

## 🚀 How to Run Locally

1. Double-click **`start_hisab_kitab_bot.bat`** in the root directory.
2. The bot will automatically start polling and stay live as long as the terminal window is open.

---

## ☁️ How to Run 24/7 for Free (Cloud Hosting)

You can host this bot 100% free on **Render**, **Railway**, or **PythonAnywhere**:

### Free Deployment on Render (Background Worker):
1. Push this repository to GitHub.
2. Go to [Render.com](https://render.com) and create a new **Background Worker**.
3. Set **Build Command**: `pip install python-telegram-bot[job-queue] reportlab openpyxl`
4. Set **Start Command**: `python -m hisab_kitab_bot.bot`
5. Click **Deploy**. Your bot will run 24/7 forever for free!

---

## 💸 Withdrawing Your Telegram Stars Earnings:
1. Open `@BotFather` on Telegram.
2. Send `/mybots` > Choose `@Hisab_Kitab_1Bot` > **Bot Settings** > **Payments**.
3. Connect your Telegram account / Fragment wallet.
4. When users buy PDF (15 Stars), Excel (15 Stars), or Combo (25 Stars), your Stars balance increases.
5. Withdraw via **Fragment.com** as TON crypto or cash to your bank!
