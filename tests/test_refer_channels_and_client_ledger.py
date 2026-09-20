import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from hisab_kitab_bot.config import COUNTRY_CHANNELS
from hisab_kitab_bot.i18n import get_referral_inline_keyboard
from hisab_kitab_bot.database import (
    init_db,
    add_client,
    get_client,
    add_client_transaction,
    get_client_transactions_with_running_balance,
    get_client_details_with_balance,
    has_claimed_channel_reward,
    set_channel_reward_claimed,
    add_vip_months,
    get_user_access_tier
)

print("=== 1. VERIFYING INDIA CHANNEL UPDATED TO DEALS FETCHER ===")
in_ch = COUNTRY_CHANNELS['IN']
print("India Channel:", in_ch)
assert in_ch['channel_username'] == '@DealsFetcher', f"Expected @DealsFetcher, got {in_ch['channel_username']}"
assert in_ch['channel_url'] == 'https://t.me/DealsFetcher', f"Expected https://t.me/DealsFetcher, got {in_ch['channel_url']}"
assert in_ch['title'] == 'Deals Fetcher 🇮🇳', f"Expected Deals Fetcher 🇮🇳, got {in_ch['title']}"
print("OK: India channel verified as Deals Fetcher!")

print("\n=== 2. VERIFYING REFERRAL KEYBOARD WITH CHANNEL & 1-MONTH CLAIM ===")
ref_kb = get_referral_inline_keyboard("https://t.me/Hisab_Kitab_1Bot?start=ref_999", country_code="IN", lang="en")
for r_idx, row in enumerate(ref_kb.inline_keyboard):
    for btn in row:
        print(f"  Row {r_idx}: '{btn.text}' | cb: {btn.callback_data} | url: {getattr(btn, 'url', None)}")

assert any("Join Deals Fetcher" in btn.text for row in ref_kb.inline_keyboard for btn in row)
assert any(btn.callback_data == "claim_channel_free_pass_IN" for row in ref_kb.inline_keyboard for btn in row)
assert any(btn.callback_data == "view_all_channels" for row in ref_kb.inline_keyboard for btn in row)
print("OK: Referral keyboard contains Channel Join, 1-Month Claim, and All 7 Channels buttons!")

print("\n=== 3. VERIFYING CLIENT WITH TIMESTAMPED TRANSACTIONS & RUNNING DUE ===")
init_db()
test_user = 99887766
client_id = add_client(test_user, "Ramesh Kumar Sharma", phone="+91 9876543210", email="ramesh@example.com", country_code="IN")
print(f"Created test client ID: {client_id}")

# Add 3 transactions
tx1 = add_client_transaction(client_id, test_user, 12000.0, "lena", note="Goods sold bill #501")
tx2 = add_client_transaction(client_id, test_user, 4000.0, "dena", note="Part payment cash")
tx3 = add_client_transaction(client_id, test_user, 2000.0, "lena", note="Extra freight charges")

details = get_client_details_with_balance(client_id, test_user)
print("Client Details:", details)
assert details['total_lena'] == 14000.0, f"Expected 14000, got {details['total_lena']}"
assert details['total_dena'] == 4000.0, f"Expected 4000, got {details['total_dena']}"
assert details['balance'] == 10000.0, f"Expected 10000, got {details['balance']}"

txs = get_client_transactions_with_running_balance(client_id, test_user, limit=5)
print(f"\nFetched {len(txs)} transactions with running balances (newest first):")
for t in txs:
    print(f"  ID {t['id']} | Type: {t['type']} | Amount: {t['amount']} | Running Bal: {t['running_balance']} | Date: {t['date']} | CreatedAt: {t['created_at']} | Note: {t['note']}")

# Oldest was tx1 (+12000), then tx2 (-4000 => 8000), then tx3 (+2000 => 10000)
# Newest first:
assert txs[0]['id'] == tx3 and txs[0]['running_balance'] == 10000.0
assert txs[1]['id'] == tx2 and txs[1]['running_balance'] == 8000.0
assert txs[2]['id'] == tx1 and txs[2]['running_balance'] == 12000.0
print("OK: Running balances accurately calculated chronologically!")

print("\n=== 4. VERIFYING CHANNEL REWARD CLAIM LOGIC ===")
from hisab_kitab_bot.database import register_user
register_user(test_user, "test_ramesh", "Ramesh")
assert not has_claimed_channel_reward(test_user)
exp = add_vip_months(test_user, 1)
set_channel_reward_claimed(test_user, True)
assert has_claimed_channel_reward(test_user)
tier = get_user_access_tier(test_user, is_channel_member=True)
print(f"User VIP Status after claiming: {tier}")
assert tier['is_active'] is True
assert tier['tier'] == 'vip'
print("OK: 1-Month free pass claimed and verified active!")

print("\n=== ALL UNIT TESTS PASSED WITH 100% SUCCESS! ===")
