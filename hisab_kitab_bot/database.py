import sqlite3
import datetime
import re
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        monthly_budget REAL DEFAULT 0,
        lang TEXT DEFAULT 'en',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check and add lang column if table existed without it
    cursor.execute("PRAGMA table_info(users)")
    cols = [r['name'] if isinstance(r, sqlite3.Row) else r[1] for r in cursor.fetchall()]
    if 'lang' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'")
    if 'lang_selected' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN lang_selected INTEGER DEFAULT 0")
    if 'free_credits' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN free_credits INTEGER DEFAULT 0")
    if 'free_access_until' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN free_access_until TEXT DEFAULT NULL")
    if 'referred_by' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL")
    if 'country_code' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN country_code TEXT DEFAULT 'GLOBAL'")
    if 'country_name' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN country_name TEXT DEFAULT 'Worldwide'")
    if 'currency_code' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN currency_code TEXT DEFAULT 'USD'")
    if 'currency_symbol' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN currency_symbol TEXT DEFAULT '$'")
    if 'country_selected' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN country_selected INTEGER DEFAULT 0")
    if 'channel_verified' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN channel_verified INTEGER DEFAULT 0")
    if 'channel_joined_at' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN channel_joined_at TEXT DEFAULT NULL")
    if 'channel_reward_claimed' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN channel_reward_claimed INTEGER DEFAULT 0")
    if 'channel_share_reward_claimed' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN channel_share_reward_claimed INTEGER DEFAULT 0")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sharer_id INTEGER NOT NULL,
        friend_id INTEGER NOT NULL,
        country_code TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sharer_id, friend_id),
        FOREIGN KEY (sharer_id) REFERENCES users (user_id),
        FOREIGN KEY (friend_id) REFERENCES users (user_id)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_shares_sharer ON channel_shares(sharer_id)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        note TEXT,
        type TEXT DEFAULT 'expense',
        date TEXT NOT NULL,
        country_code TEXT DEFAULT 'GLOBAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    cursor.execute("PRAGMA table_info(expenses)")
    exp_cols = [r['name'] if isinstance(r, sqlite3.Row) else r[1] for r in cursor.fetchall()]
    if 'country_code' not in exp_cols:
        cursor.execute("ALTER TABLE expenses ADD COLUMN country_code TEXT DEFAULT 'GLOBAL'")
        cursor.execute("""
            UPDATE expenses SET country_code = (
                SELECT country_code FROM users WHERE users.user_id = expenses.user_id
            ) WHERE country_code IS NULL OR country_code = 'GLOBAL'
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS country_budgets (
        user_id INTEGER,
        country_code TEXT,
        budget REAL DEFAULT 0,
        PRIMARY KEY (user_id, country_code)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stars_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        telegram_payment_charge_id TEXT,
        amount_stars INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_user_id INTEGER UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (referrer_id) REFERENCES users (user_id),
        FOREIGN KEY (referred_user_id) REFERENCES users (user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        country_code TEXT DEFAULT 'GLOBAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        note TEXT DEFAULT '',
        date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS text_saver_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        is_done INTEGER DEFAULT 0,
        country_code TEXT DEFAULT 'GLOBAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    conn.commit()
    conn.close()

def register_user(user_id: int, username: str = "", first_name: str = "") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, lang_selected, country_selected FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    is_new = (row is None)
    if is_new:
        cursor.execute("""
            INSERT INTO users (
                user_id, username, first_name, lang, lang_selected,
                country_code, country_name, currency_code, currency_symbol, country_selected
            )
            VALUES (?, ?, ?, 'en', 0, 'GLOBAL', 'Worldwide', 'USD', '$', 0)
        """, (user_id, username or "", first_name or ""))
    else:
        cursor.execute("""
            UPDATE users SET username = ?, first_name = ? WHERE user_id = ?
        """, (username or "", first_name or "", user_id))
    conn.commit()
    conn.close()
    return is_new

def set_user_country(user_id: int, country_code: str, country_name: str, currency_code: str, currency_symbol: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET
            country_code = ?,
            country_name = ?,
            currency_code = ?,
            currency_symbol = ?,
            country_selected = 1
        WHERE user_id = ?
    """, (country_code, country_name, currency_code, currency_symbol, user_id))
    conn.commit()
    conn.close()

def has_user_selected_country(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country_selected FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['country_selected'] == 1:
        return True
    return False

def get_user_country(user_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country_code, country_name, currency_code, currency_symbol FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['country_code']:
        return {
            "country_code": row['country_code'],
            "country_name": row['country_name'] or "Worldwide",
            "currency_code": row['currency_code'] or "USD",
            "currency_symbol": row['currency_symbol'] or "$"
        }
    return {
        "country_code": "GLOBAL",
        "country_name": "Worldwide",
        "currency_code": "USD",
        "currency_symbol": "$"
    }

def get_user_currency(user_id: int) -> tuple:
    data = get_user_country(user_id)
    return (data["currency_code"], data["currency_symbol"])

def set_user_language(user_id: int, lang: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lang = ?, lang_selected = 1 WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def has_user_selected_language(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lang_selected FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['lang_selected'] == 1:
        return True
    return False

def get_user_language(user_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['lang']:
        return row['lang']
    return 'en'

def set_budget(user_id: int, budget: float, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET monthly_budget = ? WHERE user_id = ?", (budget, user_id))
    cursor.execute("""
        INSERT INTO country_budgets (user_id, country_code, budget)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, country_code) DO UPDATE SET budget = excluded.budget
    """, (user_id, country_code, budget))
    conn.commit()
    conn.close()

def get_user_budget(user_id: int, country_code: str = None) -> float:
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT budget FROM country_budgets WHERE user_id = ? AND country_code = ?", (user_id, country_code))
    row = cursor.fetchone()
    if row and row['budget'] is not None:
        val = float(row['budget'])
        conn.close()
        return val
    cursor.execute("SELECT monthly_budget FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return float(row['monthly_budget']) if row and row['monthly_budget'] else 0.0

def add_to_budget(user_id: int, additional_amount: float, country_code: str = None) -> float:
    """Adds an additional amount to the user's existing budget and returns the new total."""
    current = get_user_budget(user_id, country_code)
    new_budget = current + max(0.0, float(additional_amount))
    set_budget(user_id, new_budget, country_code)
    return new_budget

def add_expense(user_id: int, amount: float, category: str, note: str, tx_type: str = 'expense', country_code: str = None) -> int:
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    today_str = datetime.date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, amount, category, note, type, date, country_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, amount, category, note, tx_type, today_str, country_code))
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def delete_last_expense(user_id: int, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, category, note, type, date, country_code FROM expenses
        WHERE user_id = ? AND country_code = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id, country_code))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    cursor.execute("DELETE FROM expenses WHERE id = ?", (row['id'],))
    conn.commit()
    conn.close()
    return dict(row)

def delete_expense_by_id(user_id: int, expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, category, note, type, date, country_code FROM expenses
        WHERE user_id = ? AND id = ?
    """, (user_id, expense_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    cursor.execute("DELETE FROM expenses WHERE user_id = ? AND id = ?", (user_id, expense_id))
    conn.commit()
    conn.close()
    return dict(row)

def get_recent_expenses(user_id: int, limit: int = 8, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, category, note, type, date, created_at, country_code FROM expenses
        WHERE user_id = ? AND country_code = ?
        ORDER BY id DESC LIMIT ?
    """, (user_id, country_code, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_today_expenses(user_id: int, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    today_str = datetime.date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, category, note, type, created_at, country_code FROM expenses
        WHERE user_id = ? AND date = ? AND country_code = ?
        ORDER BY id ASC
    """, (user_id, today_str, country_code))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_today_total(user_id: int, country_code: str = None) -> float:
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    today_str = datetime.date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount) as total FROM expenses
        WHERE user_id = ? AND date = ? AND type = 'expense' AND country_code = ?
    """, (user_id, today_str, country_code))
    row = cursor.fetchone()
    conn.close()
    return float(row['total']) if row and row['total'] else 0.0

def get_month_expenses(user_id: int, year: int = None, month: int = None, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    month_prefix = f"{year:04d}-{month:02d}-%"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT amount, category, note, type, date, created_at, country_code FROM expenses
        WHERE user_id = ? AND date LIKE ? AND country_code = ?
        ORDER BY id ASC
    """, (user_id, month_prefix, country_code))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_month_category_breakdown(user_id: int, year: int = None, month: int = None, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    month_prefix = f"{year:04d}-{month:02d}-%"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses
        WHERE user_id = ? AND date LIKE ? AND type = 'expense' AND country_code = ?
        GROUP BY category
        ORDER BY total DESC
    """, (user_id, month_prefix, country_code))
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(amount) as total_expense FROM expenses
        WHERE user_id = ? AND date LIKE ? AND type = 'expense' AND country_code = ?
    """, (user_id, month_prefix, country_code))
    total_exp_row = cursor.fetchone()
    total_expense = float(total_exp_row['total_expense']) if total_exp_row and total_exp_row['total_expense'] else 0.0

    cursor.execute("""
        SELECT SUM(amount) as total_income FROM expenses
        WHERE user_id = ? AND date LIKE ? AND type = 'income' AND country_code = ?
    """, (user_id, month_prefix, country_code))
    total_inc_row = cursor.fetchone()
    total_income = float(total_inc_row['total_income']) if total_inc_row and total_inc_row['total_income'] else 0.0

    conn.close()
    return {
        "categories": [dict(r) for r in rows],
        "total_expense": total_expense,
        "total_income": total_income
    }

def get_date_range_expenses(user_id: int, start_date: str, end_date: str, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT amount, category, note, type, date, created_at, country_code FROM expenses
        WHERE user_id = ? AND date >= ? AND date <= ? AND country_code = ?
        ORDER BY date ASC, id ASC
    """, (user_id, start_date, end_date, country_code))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_date_range_breakdown(user_id: int, start_date: str, end_date: str, country_code: str = None):
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses
        WHERE user_id = ? AND date >= ? AND date <= ? AND type = 'expense' AND country_code = ?
        GROUP BY category
        ORDER BY total DESC
    """, (user_id, start_date, end_date, country_code))
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(amount) as total_expense FROM expenses
        WHERE user_id = ? AND date >= ? AND date <= ? AND type = 'expense' AND country_code = ?
    """, (user_id, start_date, end_date, country_code))
    total_exp_row = cursor.fetchone()
    total_expense = float(total_exp_row['total_expense']) if total_exp_row and total_exp_row['total_expense'] else 0.0

    cursor.execute("""
        SELECT SUM(amount) as total_income FROM expenses
        WHERE user_id = ? AND date >= ? AND date <= ? AND type = 'income' AND country_code = ?
    """, (user_id, start_date, end_date, country_code))
    total_inc_row = cursor.fetchone()
    total_income = float(total_inc_row['total_income']) if total_inc_row and total_inc_row['total_income'] else 0.0

    conn.close()
    return {
        "categories": [dict(r) for r in rows],
        "total_expense": total_expense,
        "total_income": total_income
    }

def log_stars_payment(user_id: int, charge_id: str, stars_amount: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO stars_payments (user_id, telegram_payment_charge_id, amount_stars)
        VALUES (?, ?, ?)
    """, (user_id, charge_id, stars_amount))
    conn.commit()
    conn.close()

def add_referral(referrer_id: int, referred_user_id: int) -> bool:
    """
    Awards 1 FULL MONTH (+30 days) of UNLIMITED free statement downloads to referrer_id.
    Prevents self-referral and duplicate rewards.
    """
    if referrer_id == referred_user_id:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    # Check if this user was already referred by someone
    cursor.execute("SELECT id FROM referrals WHERE referred_user_id = ?", (referred_user_id,))
    if cursor.fetchone():
        conn.close()
        return False

    try:
        # Record referral
        cursor.execute(
            "INSERT INTO referrals (referrer_id, referred_user_id) VALUES (?, ?)",
            (referrer_id, referred_user_id)
        )

        # Calculate new free_access_until (+30 days from now or extended from current active date)
        today = datetime.date.today()
        cursor.execute("SELECT free_access_until FROM users WHERE user_id = ?", (referrer_id,))
        row = cursor.fetchone()
        curr_exp_str = row['free_access_until'] if (row and row['free_access_until']) else None

        base_date = today
        if curr_exp_str:
            try:
                curr_exp = datetime.date.fromisoformat(curr_exp_str)
                if curr_exp >= today:
                    base_date = curr_exp  # Extend from previous expiration date!
            except Exception:
                base_date = today

        new_expiry = base_date + datetime.timedelta(days=30)
        new_expiry_str = new_expiry.isoformat()

        cursor.execute(
            "UPDATE users SET free_access_until = ? WHERE user_id = ?",
            (new_expiry_str, referrer_id)
        )
        cursor.execute(
            "UPDATE users SET referred_by = ? WHERE user_id = ?",
            (referrer_id, referred_user_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

SPECIAL_7_COUNTRIES = {'IN', 'US', 'IT', 'ES', 'GB', 'DE', 'FR'}

def get_user_joined_date(user_id: int) -> datetime.date:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT joined_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['joined_at']:
        try:
            return datetime.datetime.fromisoformat(row['joined_at']).date()
        except Exception:
            try:
                return datetime.datetime.strptime(row['joined_at'].split()[0], "%Y-%m-%d").date()
            except Exception:
                pass
    return datetime.date.today()

def set_user_channel_status(user_id: int, verified: bool):
    conn = get_connection()
    cursor = conn.cursor()
    status_val = 1 if verified else 0
    now_str = datetime.datetime.now().isoformat() if verified else None
    cursor.execute("UPDATE users SET channel_verified = ?, channel_joined_at = ? WHERE user_id = ?", (status_val, now_str, user_id))
    conn.commit()
    conn.close()

def get_user_channel_status(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_verified FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row['channel_verified'] == 1:
        return True
    return False

def has_claimed_channel_reward(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_reward_claimed FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row['channel_reward_claimed'])

def set_channel_reward_claimed(user_id: int, claimed: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    val = 1 if claimed else 0
    cursor.execute("UPDATE users SET channel_reward_claimed = ? WHERE user_id = ?", (val, user_id))
    conn.commit()
    conn.close()

def record_channel_share(sharer_id: int, friend_id: int, country_code: str = 'IN') -> tuple:
    """
    Records a unique friend visiting via the user's country deals channel share link.
    Anti-cheating protections:
    - User cannot refer themselves (sharer_id != friend_id).
    - Each friend is only counted ONCE per sharer (UNIQUE constraint in DB).
    Returns (is_new, total_unique_shares).
    """
    if int(sharer_id) == int(friend_id):
        return False, get_channel_shares_count(sharer_id)

    conn = get_connection()
    cursor = conn.cursor()
    is_new = False
    try:
        cursor.execute(
            "INSERT INTO channel_shares (sharer_id, friend_id, country_code) VALUES (?, ?, ?)",
            (sharer_id, friend_id, (country_code or 'IN').upper())
        )
        conn.commit()
        is_new = True
    except sqlite3.IntegrityError:
        is_new = False

    cursor.execute("SELECT COUNT(DISTINCT friend_id) FROM channel_shares WHERE sharer_id = ?", (sharer_id,))
    row = cursor.fetchone()
    count = row[0] if row else 0
    conn.close()
    return is_new, count

def get_channel_shares_count(sharer_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT friend_id) FROM channel_shares WHERE sharer_id = ?", (sharer_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def has_claimed_share_reward(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_share_reward_claimed FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row['channel_share_reward_claimed'])

def set_share_reward_claimed(user_id: int, claimed: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    val = 1 if claimed else 0
    cursor.execute("UPDATE users SET channel_share_reward_claimed = ? WHERE user_id = ?", (val, user_id))
    conn.commit()
    conn.close()

def add_vip_months(user_id: int, months: int) -> str:
    """
    Adds months * 30 days to user's VIP access.
    Guarantees that user's 1st month free trial (30 days from joined_at) is fully preserved:
    If a user claims immediately or during Month 1, they get Month 1 Free + Channel Month Free
    = 2 Full Months (60 Days) from registration date!
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT joined_at, free_access_until FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    today = datetime.date.today()
    joined_date = today
    if row and row['joined_at']:
        try:
            joined_date = datetime.datetime.fromisoformat(row['joined_at']).date()
        except Exception:
            try:
                joined_date = datetime.datetime.strptime(row['joined_at'].split()[0], "%Y-%m-%d").date()
            except Exception:
                joined_date = today

    # User's baseline 1st month free trial ends 30 days from registration date
    month_1_end = joined_date + datetime.timedelta(days=30)

    # Base date starts from whichever is furthest: today or Month 1 trial end
    base_date = max(today, month_1_end)

    # If user already had a longer free_access_until, extend from that
    if row and row['free_access_until']:
        try:
            curr_exp = datetime.date.fromisoformat(row['free_access_until'])
            if curr_exp > base_date:
                base_date = curr_exp
        except Exception:
            pass

    new_expiry = base_date + datetime.timedelta(days=int(months) * 30)
    new_expiry_str = new_expiry.isoformat()

    cursor.execute("UPDATE users SET free_access_until = ? WHERE user_id = ?", (new_expiry_str, user_id))
    conn.commit()
    conn.close()
    return new_expiry.strftime("%d %B %Y")

def get_user_access_tier(user_id: int, is_channel_member: bool = False) -> dict:
    """
    Evaluates exact user access status across:
    - Paid / Referral VIP Pass (unlimited)
    - Month 1: 100% Free Trial for ALL users worldwide (Days 1 to 30)
    - Month 2: Free access for 7 special countries (IN, US, IT, ES, GB, DE, FR) IF in Telegram deals channel
    - Month 2 Paused: If user from 7 countries is NOT in the channel
    - Expired: Beyond trial / free period without active VIP
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT joined_at, free_access_until, country_code FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as total FROM referrals WHERE referrer_id = ?", (user_id,))
    ref_row = cursor.fetchone()
    total_referred = ref_row['total'] if ref_row else 0
    conn.close()

    today = datetime.date.today()
    joined_date = today
    if row and row['joined_at']:
        try:
            joined_date = datetime.datetime.fromisoformat(row['joined_at']).date()
        except Exception:
            try:
                joined_date = datetime.datetime.strptime(row['joined_at'].split()[0], "%Y-%m-%d").date()
            except Exception:
                joined_date = today

    country_code = (row['country_code'] or 'GLOBAL').upper() if row else 'GLOBAL'
    exp_str = row['free_access_until'] if (row and row['free_access_until']) else None

    # 1. Check Paid / Referral VIP Pass
    if exp_str:
        try:
            exp_date = datetime.date.fromisoformat(exp_str)
            days_left = (exp_date - today).days
            if days_left >= 0:
                return {
                    "is_active": True,
                    "tier": "vip",
                    "badge": "🌟 VIP Pass",
                    "expires_at": exp_date.strftime("%d %B %Y"),
                    "days_left": days_left,
                    "total_referred": total_referred,
                    "requires_channel": False,
                    "country_code": country_code
                }
        except Exception:
            pass

    # 2. Check Trial Periods based on joined_date
    days_since_joined = max(0, (today - joined_date).days)

    # MONTH 1: First 30 days are 100% FREE for everyone worldwide!
    if days_since_joined < 30:
        days_left = 30 - days_since_joined
        month_1_expiry = (joined_date + datetime.timedelta(days=30)).strftime("%d %B %Y")
        return {
            "is_active": True,
            "tier": "month_1_free",
            "badge": "🎁 Month 1 Free Trial",
            "expires_at": month_1_expiry,
            "days_left": days_left,
            "total_referred": total_referred,
            "requires_channel": False,
            "country_code": country_code
        }

    # MONTH 2: Days 31 to 60
    elif days_since_joined < 60:
        days_left = 60 - days_since_joined
        month_2_expiry = (joined_date + datetime.timedelta(days=60)).strftime("%d %B %Y")

        if country_code in SPECIAL_7_COUNTRIES:
            if is_channel_member:
                return {
                    "is_active": True,
                    "tier": "month_2_channel",
                    "badge": "📢 Month 2 Deals Channel Pass",
                    "expires_at": month_2_expiry,
                    "days_left": days_left,
                    "total_referred": total_referred,
                    "requires_channel": False,
                    "country_code": country_code
                }
            else:
                return {
                    "is_active": False,
                    "tier": "month_2_paused",
                    "badge": "⏸️ Month 2 Paused (Channel Required)",
                    "expires_at": month_2_expiry,
                    "days_left": days_left,
                    "total_referred": total_referred,
                    "requires_channel": True,
                    "country_code": country_code
                }
        else:
            # Other countries don't get Month 2 channel trial
            return {
                "is_active": False,
                "tier": "trial_expired",
                "badge": "⌛ Month 1 Trial Completed",
                "expires_at": None,
                "days_left": 0,
                "total_referred": total_referred,
                "requires_channel": False,
                "country_code": country_code
            }

    # DAY 60+: Expired for all without active VIP
    return {
        "is_active": False,
        "tier": "expired",
        "badge": "⌛ Pass Expired",
        "expires_at": None,
        "days_left": 0,
        "total_referred": total_referred,
        "requires_channel": False,
        "country_code": country_code
    }

def get_free_access_details(user_id: int, is_channel_member: bool = False) -> dict:
    tier_info = get_user_access_tier(user_id, is_channel_member)
    return {
        "is_active": tier_info["is_active"],
        "tier": tier_info["tier"],
        "badge": tier_info.get("badge", ""),
        "expires_at": tier_info["expires_at"],
        "days_left": tier_info["days_left"],
        "total_referred": tier_info["total_referred"],
        "requires_channel": tier_info.get("requires_channel", False),
        "country_code": tier_info.get("country_code", "GLOBAL")
    }

def is_free_access_active(user_id: int, is_channel_member: bool = False) -> bool:
    return get_user_access_tier(user_id, is_channel_member)["is_active"]

def get_user_credits(user_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT free_credits FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return int(row['free_credits']) if row and row['free_credits'] else 0

def use_user_credit(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT free_credits FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    credits = int(row['free_credits']) if row and row['free_credits'] else 0

    if credits > 0:
        cursor.execute("UPDATE users SET free_credits = free_credits - 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

def get_referral_stats(user_id: int) -> dict:
    details = get_free_access_details(user_id)
    return {
        "total_referred": details["total_referred"],
        "is_active": details["is_active"],
        "expires_at": details["expires_at"],
        "days_left": details["days_left"]
    }

def get_all_active_user_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r['user_id'] for r in rows]

# ==========================================
# CLIENT KHATA & LEN-DEN (ACCOUNTS RECEIVABLE / PAYABLE)
# ==========================================

def add_client(user_id: int, name: str, phone: str = '', email: str = '', country_code: str = None) -> int:
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (user_id, name, phone, email, country_code)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, name.strip(), (phone or '').strip(), (email or '').strip(), country_code))
    client_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return client_id

def get_client(client_id: int, user_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, name, phone, email, country_code, created_at
        FROM clients WHERE id = ? AND user_id = ?
    """, (client_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_client_phone(client_id: int, user_id: int, phone: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients SET phone = ? WHERE id = ? AND user_id = ?
    """, (phone.strip(), client_id, user_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def update_client_email(client_id: int, user_id: int, email: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients SET email = ? WHERE id = ? AND user_id = ?
    """, (email.strip(), client_id, user_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_client(client_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client_transactions WHERE client_id = ? AND user_id = ?", (client_id, user_id))
    cursor.execute("DELETE FROM clients WHERE id = ? AND user_id = ?", (client_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_all_clients(user_id: int, country_code: str = None) -> list:
    if not country_code:
        country_code = get_user_country(user_id)['country_code']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.id, c.user_id, c.name, c.phone, c.email, c.country_code, c.created_at,
            COALESCE(SUM(CASE WHEN t.type = 'lena' THEN t.amount ELSE 0 END), 0) AS total_lena,
            COALESCE(SUM(CASE WHEN t.type = 'dena' THEN t.amount ELSE 0 END), 0) AS total_dena,
            COALESCE(SUM(CASE WHEN t.type = 'lena' THEN t.amount ELSE -t.amount END), 0) AS balance,
            COUNT(t.id) as tx_count
        FROM clients c
        LEFT JOIN client_transactions t ON c.id = t.client_id
        WHERE c.user_id = ? AND c.country_code = ?
        GROUP BY c.id
        ORDER BY c.id DESC
    """, (user_id, country_code))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_client_details_with_balance(client_id: int, user_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.id, c.user_id, c.name, c.phone, c.email, c.country_code, c.created_at,
            COALESCE(SUM(CASE WHEN t.type = 'lena' THEN t.amount ELSE 0 END), 0) AS total_lena,
            COALESCE(SUM(CASE WHEN t.type = 'dena' THEN t.amount ELSE 0 END), 0) AS total_dena,
            COALESCE(SUM(CASE WHEN t.type = 'lena' THEN t.amount ELSE -t.amount END), 0) AS balance,
            COUNT(t.id) as tx_count
        FROM clients c
        LEFT JOIN client_transactions t ON c.id = t.client_id
        WHERE c.id = ? AND c.user_id = ?
        GROUP BY c.id
    """, (client_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_client_transaction(client_id: int, user_id: int, amount: float, tx_type: str, note: str = '', tx_date: str = None) -> int:
    now = datetime.datetime.now()
    today_str = tx_date or now.strftime("%Y-%m-%d")
    created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO client_transactions (client_id, user_id, amount, type, note, date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_id, user_id, float(amount), tx_type, (note or '').strip(), today_str, created_at_str))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tx_id

def get_client_transactions(client_id: int, user_id: int, limit: int = 10) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, client_id, user_id, amount, type, note, date, created_at
        FROM client_transactions
        WHERE client_id = ? AND user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
    """, (client_id, user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_client_transactions_with_running_balance(client_id: int, user_id: int, limit: int = 10) -> list:
    """
    Fetches client transactions with chronological running balance calculated for each transaction.
    Returns list sorted newest first (for display).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, client_id, user_id, amount, type, note, date, created_at
        FROM client_transactions
        WHERE client_id = ? AND user_id = ?
        ORDER BY date ASC, id ASC
    """, (client_id, user_id))
    rows = cursor.fetchall()
    conn.close()

    running = 0.0
    all_txs = []
    for r in rows:
        d = dict(r)
        amt = float(d['amount'])
        if d['type'] == 'lena':
            running += amt
        else:
            running -= amt
        d['running_balance'] = running
        all_txs.append(d)

    all_txs.reverse()
    return all_txs[:limit] if limit else all_txs

def delete_client_transaction(tx_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client_transactions WHERE id = ? AND user_id = ?", (tx_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_clients_overall_summary(user_id: int, country_code: str = None) -> dict:
    clients = get_all_clients(user_id, country_code)
    total_receivable = sum(c['balance'] for c in clients if c['balance'] > 0)
    total_payable = sum(abs(c['balance']) for c in clients if c['balance'] < 0)
    net_balance = total_receivable - total_payable

    debtors = sorted([c for c in clients if c['balance'] > 0], key=lambda x: x['balance'], reverse=True)[:5]
    creditors = sorted([c for c in clients if c['balance'] < 0], key=lambda x: abs(x['balance']), reverse=True)[:5]

    return {
        "count": len(clients),
        "total_clients": len(clients),
        "total_receivable": total_receivable,
        "total_lena": total_receivable,
        "total_payable": total_payable,
        "total_dena": total_payable,
        "net_balance": net_balance,
        "top_debtors": debtors,
        "top_creditors": creditors
    }

def get_client_transactions_by_period(user_id: int, start_date: str, end_date: str, client_id: int = None, country_code: str = None) -> list:
    """Fetches client transactions within a date range with client metadata joined."""
    conn = get_connection()
    cursor = conn.cursor()
    params = [user_id, start_date, end_date]
    sql = """
        SELECT ct.id, ct.client_id, c.name AS client_name, c.phone AS client_phone, c.email AS client_email,
               ct.amount, ct.type, ct.note, ct.date, ct.created_at, c.country_code
        FROM client_transactions ct
        JOIN clients c ON c.id = ct.client_id
        WHERE ct.user_id = ? AND ct.date >= ? AND ct.date <= ?
    """
    if client_id:
        sql += " AND ct.client_id = ?"
        params.append(client_id)
    if country_code:
        sql += " AND c.country_code = ?"
        params.append(country_code)

    sql += " ORDER BY ct.date ASC, ct.id ASC"
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_client_opening_balance(client_id: int, user_id: int, before_date: str) -> float:
    """Calculates client balance prior to the start date (Opening Balance)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'lena' THEN amount ELSE -amount END), 0) AS opening_balance
        FROM client_transactions
        WHERE client_id = ? AND user_id = ? AND date < ?
    """, (client_id, user_id, before_date))
    row = cursor.fetchone()
    conn.close()
    return float(row['opening_balance']) if row and row['opening_balance'] is not None else 0.0

def get_client_period_summary(user_id: int, start_date: str, end_date: str, client_id: int = None, country_code: str = None) -> dict:
    """Computes period aggregates and balance breakdown for reports."""
    clients_list = get_all_clients(user_id, country_code)
    if client_id:
        clients_list = [c for c in clients_list if c['id'] == client_id]

    txs = get_client_transactions_by_period(user_id, start_date, end_date, client_id, country_code)

    period_lena = sum(t['amount'] for t in txs if t['type'] == 'lena')
    period_dena = sum(t['amount'] for t in txs if t['type'] == 'dena')
    period_net = period_lena - period_dena

    total_receivable = sum(c['balance'] for c in clients_list if c['balance'] > 0)
    total_payable = sum(abs(c['balance']) for c in clients_list if c['balance'] < 0)
    net_position = total_receivable - total_payable

    return {
        "clients": clients_list,
        "transactions": txs,
        "total_clients": len(clients_list),
        "total_receivable": total_receivable,
        "total_payable": total_payable,
        "net_position": net_position,
        "period_lena": period_lena,
        "period_dena": period_dena,
        "period_net": period_net,
        "total_tx_count": len(txs)
    }

# ==========================================
# TEXT SAVER / SHOPPING LIST FUNCTIONS
# ==========================================

def add_text_saver_items(user_id: int, raw_text: str, country_code: str = 'GLOBAL') -> list:
    """
    Parses raw_text (multi-line or comma-separated) and adds each valid item to the database.
    Returns list of newly created item dicts: [{'id': id, 'text': text}].
    """
    if not raw_text or not raw_text.strip():
        return []

    lines = raw_text.strip().split("\n")
    candidates = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "," in line and not any(p in line for p in ["₹", "$", "Rs"]):
            parts = [p.strip() for p in line.split(",") if p.strip()]
            candidates.extend(parts)
        else:
            candidates.append(line)

    cleaned_items = []
    for c in candidates:
        clean = re.sub(r'^[\s\-\*•\d\.\)]+\s*', '', c).strip()
        if clean:
            cleaned_items.append(clean)

    if not cleaned_items:
        return []

    conn = get_connection()
    cursor = conn.cursor()
    created = []
    for item_text in cleaned_items:
        cursor.execute(
            "INSERT INTO text_saver_items (user_id, text, is_done, country_code) VALUES (?, ?, 0, ?)",
            (user_id, item_text, country_code)
        )
        created.append({"id": cursor.lastrowid, "text": item_text})
    conn.commit()
    conn.close()
    return created

def get_text_saver_items(user_id: int, country_code: str = None) -> list:
    """Returns all text saver items for user, pending items first, then completed."""
    conn = get_connection()
    cursor = conn.cursor()
    if country_code:
        cursor.execute(
            "SELECT id, user_id, text, is_done, country_code, created_at FROM text_saver_items WHERE user_id = ? AND (country_code = ? OR country_code = 'GLOBAL') ORDER BY is_done ASC, id ASC",
            (user_id, country_code)
        )
    else:
        cursor.execute(
            "SELECT id, user_id, text, is_done, country_code, created_at FROM text_saver_items WHERE user_id = ? ORDER BY is_done ASC, id ASC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_text_saver_item(item_id: int, user_id: int) -> tuple:
    """Toggles item status between done (1) and pending (0). Returns (success, new_status, text)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_done, text FROM text_saver_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return (False, 0, "")
    current_status = row['is_done']
    item_text = row['text']
    new_status = 0 if current_status == 1 else 1
    cursor.execute("UPDATE text_saver_items SET is_done = ? WHERE id = ? AND user_id = ?", (new_status, item_id, user_id))
    conn.commit()
    conn.close()
    return (True, new_status, item_text)

def delete_text_saver_item(item_id: int, user_id: int) -> bool:
    """Deletes a single text saver item."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM text_saver_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def clear_completed_text_saver_items(user_id: int, country_code: str = None) -> int:
    """Deletes all items marked as done."""
    conn = get_connection()
    cursor = conn.cursor()
    if country_code:
        cursor.execute(
            "DELETE FROM text_saver_items WHERE user_id = ? AND is_done = 1 AND (country_code = ? OR country_code = 'GLOBAL')",
            (user_id, country_code)
        )
    else:
        cursor.execute(
            "DELETE FROM text_saver_items WHERE user_id = ? AND is_done = 1",
            (user_id,)
        )
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def clear_all_text_saver_items(user_id: int, country_code: str = None) -> int:
    """Deletes all text saver items for user."""
    conn = get_connection()
    cursor = conn.cursor()
    if country_code:
        cursor.execute(
            "DELETE FROM text_saver_items WHERE user_id = ? AND (country_code = ? OR country_code = 'GLOBAL')",
            (user_id, country_code)
        )
    else:
        cursor.execute("DELETE FROM text_saver_items WHERE user_id = ?", (user_id,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def get_text_saver_stats(user_id: int, country_code: str = None) -> dict:
    """Returns summary counts of text saver items."""
    items = get_text_saver_items(user_id, country_code)
    pending = sum(1 for i in items if not i['is_done'])
    done = sum(1 for i in items if i['is_done'])
    return {
        "items": items,
        "total": len(items),
        "pending": pending,
        "done": done
    }

# Initialize tables automatically on import
init_db()
