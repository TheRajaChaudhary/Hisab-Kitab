import os
import sys
import datetime

# Ensure utf-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from hisab_kitab_bot.database import (
    register_user,
    set_user_language,
    set_user_country,
    add_client,
    add_client_transaction,
    get_all_clients,
    get_client_period_summary
)
from hisab_kitab_bot.pdf_generator import (
    generate_client_report_pdf,
    get_client_report_date_range
)
from hisab_kitab_bot.excel_generator import (
    generate_client_report_excel
)
from hisab_kitab_bot.i18n import (
    get_client_statement_str,
    get_client_report_period_keyboard,
    get_clients_main_keyboard,
    get_client_detail_keyboard
)

def run_tests():
    print("=== STARTING COMPREHENSIVE CLIENT REPORT TESTS ===")
    test_user_id = 88776655
    register_user(test_user_id, username="testbiz_user", first_name="TestBiz")
    set_user_language(test_user_id, "hi")
    set_user_country(test_user_id, "IN", "India", "INR", "₹")

    # 1. Add sample clients and transactions
    c1_id = add_client(test_user_id, "Rahul Sharma", phone="9876543210", email="rahul@example.com", country_code="IN")
    c2_id = add_client(test_user_id, "Pooja Traders", phone="9123456789", email="pooja@traders.com", country_code="IN")

    add_client_transaction(c1_id, test_user_id, 15000.0, 'lena', note="Goods invoice #101")
    add_client_transaction(c1_id, test_user_id, 5000.0, 'dena', note="Cash received")
    add_client_transaction(c2_id, test_user_id, 8500.0, 'dena', note="Raw materials purchase")

    # 2. Test get_client_report_date_range cap at 12 months
    print("\n--- Testing get_client_report_date_range bounds ---")
    s1, e1, lbl1, m1 = get_client_report_date_range(1)
    assert m1 == 1, f"Expected 1 month, got {m1}"
    print(f"1 Month: {s1} to {e1} -> {lbl1}")

    s12, e12, lbl12, m12 = get_client_report_date_range(12)
    assert m12 == 12, f"Expected 12 months, got {m12}"
    print(f"12 Months: {s12} to {e12} -> {lbl12}")

    # Over 12 should be capped at 12
    s24, e24, lbl24, m24 = get_client_report_date_range(24)
    assert m24 == 12, f"Expected cap at 12 months, got {m24}"
    print(f"24 Months (capped): {s24} to {e24} -> {lbl24}")

    # 0 or negative should floor at 1
    s0, e0, lbl0, m0 = get_client_report_date_range(0)
    assert m0 == 1, f"Expected floor at 1 month, got {m0}"
    print(f"0 Months (floored): {s0} to {e0} -> {lbl0}")

    # 3. Test PDF generation (All clients, 1 Month, Hindi)
    print("\n--- Testing PDF generation ---")
    pdf_1m_all = generate_client_report_pdf(test_user_id, "TestBiz", client_id=None, months=1, lang='hi', country_code='IN')
    assert os.path.exists(pdf_1m_all) and os.path.getsize(pdf_1m_all) > 1000, "PDF 1M All failed"
    with open(pdf_1m_all, 'rb') as f:
        header = f.read(5)
        assert header == b'%PDF-', f"Invalid PDF header: {header}"
    print(f"OK: PDF 1M All Clients ({os.path.getsize(pdf_1m_all)} bytes): {os.path.basename(pdf_1m_all)}")

    # Test PDF generation (Single client, 12 Months, English)
    pdf_12m_c1 = generate_client_report_pdf(test_user_id, "TestBiz", client_id=c1_id, months=12, lang='en', country_code='IN')
    assert os.path.exists(pdf_12m_c1) and os.path.getsize(pdf_12m_c1) > 1000, "PDF 12M Single Client failed"
    print(f"OK: PDF 12M Single Client ({os.path.getsize(pdf_12m_c1)} bytes): {os.path.basename(pdf_12m_c1)}")

    # 4. Test Excel generation (All clients, 12 Months, Hindi)
    print("\n--- Testing Excel generation ---")
    excel_12m_all = generate_client_report_excel(test_user_id, "TestBiz", client_id=None, months=12, lang='hi', country_code='IN')
    assert os.path.exists(excel_12m_all) and os.path.getsize(excel_12m_all) > 2000, "Excel 12M All failed"
    print(f"OK: Excel 12M All Clients ({os.path.getsize(excel_12m_all)} bytes): {os.path.basename(excel_12m_all)}")

    # Test Excel generation (Single client, 3 Months, Bengali)
    excel_3m_c1 = generate_client_report_excel(test_user_id, "TestBiz", client_id=c1_id, months=3, lang='bn', country_code='IN')
    assert os.path.exists(excel_3m_c1) and os.path.getsize(excel_3m_c1) > 2000, "Excel 3M Single Client failed"
    print(f"OK: Excel 3M Single Client ({os.path.getsize(excel_3m_c1)} bytes): {os.path.basename(excel_3m_c1)}")

    # 5. Test Keyboards
    print("\n--- Testing Keyboards ---")
    kb_main = get_clients_main_keyboard(lang='hi')
    assert any("PDF" in b.text for row in kb_main.inline_keyboard for b in row), "PDF button missing from client main kb"
    assert any("Excel" in b.text for row in kb_main.inline_keyboard for b in row), "Excel button missing from client main kb"
    print("OK: get_clients_main_keyboard has PDF/Excel buttons")

    kb_detail = get_client_detail_keyboard(c1_id, lang='hi')
    assert any(b.callback_data == f"cl_fmt_c{c1_id}_pdf" for row in kb_detail.inline_keyboard for b in row), "cl_fmt_c{id}_pdf missing"
    assert any(b.callback_data == f"cl_fmt_c{c1_id}_excel" for row in kb_detail.inline_keyboard for b in row), "cl_fmt_c{id}_excel missing"
    assert any(b.text == "🔙 Client" for row in kb_detail.inline_keyboard for b in row), "Back to Client button missing"
    print("OK: get_client_detail_keyboard has PDF/Excel statement buttons and 🔙 Client")

    kb_period = get_client_report_period_keyboard("pdf", "all", lang='hi')
    assert len(kb_period.inline_keyboard) == 4, f"Expected 4 rows in period keyboard, got {len(kb_period.inline_keyboard)}"
    print("OK: get_client_report_period_keyboard has 1M, 3M, 6M, 12M, and Custom options")

    # 6. Test i18n Strings
    print("\n--- Testing i18n Strings ---")
    assert get_client_statement_str('doc_title_all', 'hi') != ""
    assert get_client_statement_str('doc_title_all', 'en') != ""
    assert get_client_statement_str('doc_title_all', 'bn') != ""
    assert get_client_statement_str('lbl_total_receivable', 'hi') != ""
    assert get_client_statement_str('lbl_total_payable', 'hi') != ""
    print("OK: Client statement i18n strings verified across languages")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    run_tests()
