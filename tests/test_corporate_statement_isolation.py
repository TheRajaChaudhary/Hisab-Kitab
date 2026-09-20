import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("=== STARTING COMPREHENSIVE TEST: CORPORATE STATEMENTS & COUNTRY ISOLATION ===")

from hisab_kitab_bot.database import (
    init_db,
    add_expense,
    get_today_total,
    get_month_category_breakdown,
    get_date_range_expenses,
    get_user_country,
    get_connection
)
from hisab_kitab_bot.pdf_generator import generate_statement_pdf
from hisab_kitab_bot.excel_generator import generate_statement_excel
from hisab_kitab_bot.i18n import get_statement_str

init_db()

# -------------------------------------------------------------
# TEST 1: ZERO PROMOTION IN PDF & EXCEL SOURCE FILES
# -------------------------------------------------------------
print("\n[Test 1] Verifying ZERO promotional links in PDF & Excel generators...")
with open("hisab_kitab_bot/pdf_generator.py", "r", encoding="utf-8") as f:
    pdf_src = f.read()
    assert "DEALS_FETCHER_URL" not in pdf_src, "DEALS_FETCHER_URL found in pdf_generator.py"
    assert "dealsfetcher" not in pdf_src.lower(), "dealsfetcher found in pdf_generator.py"

with open("hisab_kitab_bot/excel_generator.py", "r", encoding="utf-8") as f:
    excel_src = f.read()
    assert "DEALS_FETCHER_URL" not in excel_src, "DEALS_FETCHER_URL found in excel_generator.py"
    assert "dealsfetcher" not in excel_src.lower(), "dealsfetcher found in excel_generator.py"

print("  ✓ PASSED: ZERO website promotions or deals links in PDF and Excel generators!")

# -------------------------------------------------------------
# TEST 2: COUNTRY-WISE ACCOUNTING ISOLATION
# -------------------------------------------------------------
print("\n[Test 2] Verifying Country-Wise Accounting Isolation...")
test_uid = 99998888

# Clean up any previous test entries
conn = get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM expenses WHERE user_id = ?", (test_uid,))
cursor.execute("DELETE FROM users WHERE user_id = ?", (test_uid,))
conn.commit()

# Register test user
cursor.execute("""
    INSERT INTO users (user_id, username, first_name, country_code, country_name, currency_code, currency_symbol)
    VALUES (?, 'test_isolation', 'Corporate Tester', 'IN', 'India', 'INR', '₹')
""", (test_uid,))
conn.commit()
conn.close()

# 1. Add expense under India (IN)
id_in = add_expense(test_uid, 500.0, "Office Supplies", "Printer Paper", "expense", country_code="IN")
# 2. Add expense under United States (US)
id_us = add_expense(test_uid, 45.0, "Software", "Cloud Hosting", "expense", country_code="US")
# 3. Add income under United States (US)
id_us_inc = add_expense(test_uid, 1200.0, "Client Consulting", "Retainer", "income", country_code="US")

# Check totals for India
tot_in = get_today_total(test_uid, country_code="IN")
assert tot_in == 500.0, f"Expected 500.0 for IN, got {tot_in}"

# Check totals for US
tot_us = get_today_total(test_uid, country_code="US")
assert tot_us == 45.0, f"Expected 45.0 for US, got {tot_us}"

# Check breakdowns
bd_in = get_month_category_breakdown(test_uid, country_code="IN")
assert bd_in['total_expense'] == 500.0, f"IN expense breakdown mismatch: {bd_in}"
assert bd_in['total_income'] == 0.0, "IN income should be 0"

bd_us = get_month_category_breakdown(test_uid, country_code="US")
assert bd_us['total_expense'] == 45.0, f"US expense breakdown mismatch: {bd_us}"
assert bd_us['total_income'] == 1200.0, f"US income mismatch: {bd_us}"

# Check date range queries
today_iso = os.popen('py -3.10 -c "import datetime; print(datetime.date.today().isoformat())"').read().strip()
txs_in = get_date_range_expenses(test_uid, today_iso, today_iso, country_code="IN")
assert len(txs_in) == 1, f"Expected 1 tx for IN, got {len(txs_in)}"
assert txs_in[0]['amount'] == 500.0 and txs_in[0]['country_code'] == 'IN'

txs_us = get_date_range_expenses(test_uid, today_iso, today_iso, country_code="US")
assert len(txs_us) == 2, f"Expected 2 txs for US, got {len(txs_us)}"
assert set(t['country_code'] for t in txs_us) == {'US'}

print("  ✓ PASSED: Ledgers for India and USA are 100% strictly isolated and never mix!")

# -------------------------------------------------------------
# TEST 3: MULTI-LANGUAGE PROFESSIONAL PDF GENERATION
# -------------------------------------------------------------
print("\n[Test 3] Verifying Multi-Language Professional Corporate PDF generation...")
test_languages = ['en', 'hi', 'bn', 'ru', 'es', 'pt', 'ar', 'de', 'fr']

for lang in test_languages:
    pdf_path = generate_statement_pdf(
        user_id=test_uid,
        first_name="Corporate Tester",
        start_date=today_iso,
        end_date=today_iso,
        period_label="Current Audit Cycle",
        lang=lang,
        country_code="IN"
    )
    assert os.path.exists(pdf_path), f"PDF file not found for lang: {lang}"
    assert os.path.getsize(pdf_path) > 1000, f"PDF file too small for lang: {lang}"
    print(f"  ✓ {lang.upper()} Corporate PDF: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path):,} bytes)")

# -------------------------------------------------------------
# TEST 4: MULTI-LANGUAGE PROFESSIONAL EXCEL GENERATION
# -------------------------------------------------------------
print("\n[Test 4] Verifying Multi-Language Professional Corporate Excel generation...")
for lang in test_languages:
    excel_path = generate_statement_excel(
        user_id=test_uid,
        first_name="Corporate Tester",
        start_date=today_iso,
        end_date=today_iso,
        period_label="Current Audit Cycle",
        lang=lang,
        country_code="US"
    )
    assert os.path.exists(excel_path), f"Excel file not found for lang: {lang}"
    assert os.path.getsize(excel_path) > 1000, f"Excel file too small for lang: {lang}"
    print(f"  ✓ {lang.upper()} Corporate Excel: {os.path.basename(excel_path)} ({os.path.getsize(excel_path):,} bytes)")

# Clean up test rows
conn = get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM expenses WHERE user_id = ?", (test_uid,))
cursor.execute("DELETE FROM users WHERE user_id = ?", (test_uid,))
conn.commit()
conn.close()

print("\n=== ALL TESTS PASSED WITH 100% SUCCESS! ===")
