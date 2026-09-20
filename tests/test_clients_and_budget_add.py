import sys
sys.stdout.reconfigure(encoding='utf-8')
from hisab_kitab_bot.database import (
    set_budget, get_user_budget, add_to_budget,
    add_client, get_client, update_client_phone, update_client_email,
    delete_client, get_all_clients, get_client_details_with_balance,
    add_client_transaction, get_client_transactions, get_clients_overall_summary
)
from hisab_kitab_bot.bot import parse_amount_and_note

test_uid = 88887777

# 1. Test Budget Add
set_budget(test_uid, 10000.0, country_code='IN')
b1 = get_user_budget(test_uid, country_code='IN')
assert b1 == 10000.0, f"Expected 10000, got {b1}"
b2 = add_to_budget(test_uid, 5000.0, country_code='IN')
assert b2 == 15000.0, f"Expected 15000, got {b2}"
print("Budget add test PASSED!")

# 2. Test parse_amount_and_note
a1, n1 = parse_amount_and_note("1500 2 cement bags")
assert a1 == 1500.0 and n1 == "2 cement bags", f"Parse failed: {a1}, {n1}"
a2, n2 = parse_amount_and_note("₹2,500.50 advance payment")
assert a2 == 2500.5 and n2 == "advance payment", f"Parse failed: {a2}, {n2}"
a3, n3 = parse_amount_and_note("500")
assert a3 == 500.0 and n3 == "", f"Parse failed: {a3}, {n3}"
print("Amount & note parsing test PASSED!")

# Clean any previous test data
clients = get_all_clients(test_uid, country_code='IN')
for c in clients:
    delete_client(c['id'], test_uid)

# 3. Test Client Creation (skip phone initially)
cid1 = add_client(test_uid, name="Ramesh Kumar", phone="", email="", country_code='IN')
c1 = get_client(cid1, test_uid)
assert c1['name'] == "Ramesh Kumar" and c1['phone'] == "", "Client creation failed"

# 4. Test Updating Phone & Email from detail view
update_client_phone(cid1, test_uid, "+91 98765 43210")
update_client_email(cid1, test_uid, "ramesh@example.com")
c1_updated = get_client(cid1, test_uid)
assert c1_updated['phone'] == "+91 98765 43210", "Phone update failed"
assert c1_updated['email'] == "ramesh@example.com", "Email update failed"
print("Client creation & field updates PASSED!")

# 5. Test Lena & Dena Transactions
add_client_transaction(cid1, test_uid, 5000.0, 'lena', note="Goods sold")
add_client_transaction(cid1, test_uid, 2000.0, 'dena', note="Cash paid back")
det1 = get_client_details_with_balance(cid1, test_uid)
assert det1['total_lena'] == 5000.0, f"Expected lena 5000, got {det1['total_lena']}"
assert det1['total_dena'] == 2000.0, f"Expected dena 2000, got {det1['total_dena']}"
assert det1['balance'] == 3000.0, f"Expected balance 3000, got {det1['balance']}"

# Add second client (creditor)
cid2 = add_client(test_uid, name="Sharma Stores", phone="9123456780", country_code='IN')
add_client_transaction(cid2, test_uid, 4000.0, 'dena', note="Raw materials bought")

# 6. Overall Summary
summary = get_clients_overall_summary(test_uid, country_code='IN')
assert summary['total_clients'] == 2, f"Expected 2 clients, got {summary['total_clients']}"
assert summary['total_lena'] == 3000.0, f"Expected total lena 3000, got {summary['total_lena']}"
assert summary['total_dena'] == 4000.0, f"Expected total dena 4000, got {summary['total_dena']}"
assert summary['net_balance'] == -1000.0, f"Expected net -1000, got {summary['net_balance']}"
assert len(summary['top_debtors']) >= 1 and summary['top_debtors'][0]['name'] == "Ramesh Kumar", "Top debtor check failed"
assert len(summary['top_creditors']) >= 1 and summary['top_creditors'][0]['name'] == "Sharma Stores", "Top creditor check failed"
print("Transactions & Overall Summary test PASSED!")

# 7. Country Isolation Check
us_clients = get_all_clients(test_uid, country_code='US')
assert len(us_clients) == 0, f"Expected 0 US clients, got {len(us_clients)}"
print("Country isolation test PASSED!")

# Clean up
delete_client(cid1, test_uid)
delete_client(cid2, test_uid)
print("Cleanup completed. ALL TESTS 100% PASSED!")
