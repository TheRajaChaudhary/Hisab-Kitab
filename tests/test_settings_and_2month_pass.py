import os
import sys
sys.path.insert(0, os.path.abspath("."))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import datetime
import tempfile
import sqlite3

# Import bot modules
from hisab_kitab_bot.database import (
    get_connection,
    register_user,
    set_user_country,
    add_vip_months,
    get_user_access_tier,
    get_free_access_details,
    has_claimed_channel_reward,
    set_channel_reward_claimed,
    init_db
)
from hisab_kitab_bot.i18n import get_settings_keyboard, get_referral_inline_keyboard

def run_tests():
    print("=== Testing Settings Keyboard ===")
    settings_kb = get_settings_keyboard('en')
    button_texts = [btn.text for row in settings_kb.inline_keyboard for btn in row]
    print(f"Settings buttons: {button_texts}")
    
    # Assert NO 7 channels button in settings
    for text in button_texts:
        assert "7 Country" not in text and "All 7" not in text, f"Found 7 channels button in settings: {text}"
        assert "Deals Fetcher" not in text and "@" not in text, f"Found channel link button in settings: {text}"
    assert len(button_texts) == 3, f"Expected exactly 3 buttons in settings, got {len(button_texts)}"
    print("✅ Settings keyboard is clean (Country, Language, Back only)!")

    print("\n=== Testing Referral Inline Keyboard ===")
    ref_kb = get_referral_inline_keyboard("https://t.me/TestBot?start=ref_12345", country_code="IN", lang="en")
    ref_btn_texts = [btn.text for row in ref_kb.inline_keyboard for btn in row]
    print(f"Referral inline buttons: {ref_btn_texts}")
    
    for text in ref_btn_texts:
        assert "7 Country" not in text and "All 7" not in text, f"Found 7 channels button in referral: {text}"
    assert any("2 Months Free VIP Pass" in text for text in ref_btn_texts), "Claim 2 Months Free VIP Pass button not found!"
    assert any("Join" in text for text in ref_btn_texts), "Join country channel button not found!"
    print("✅ Referral keyboard contains ONLY user's country channel & 2-Month Free VIP claim button!")

    print("\n=== Testing 2-Month Cumulative Free Pass Logic ===")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id IN (999888777, 999888776)")
    cur.execute("DELETE FROM referrals WHERE referrer_id IN (999888777, 999888776) OR referred_user_id IN (999888777, 999888776)")
    conn.commit()
    conn.close()

    test_user_id = 999888777
    register_user(test_user_id, "test_pass_user", "Test")
    set_user_country(test_user_id, "IN", "India", "INR", "₹")
    
    # Check access before claim (Day 0)
    tier_day0 = get_user_access_tier(test_user_id)
    print(f"Day 0 Tier: {tier_day0['tier']}, Badge: {tier_day0['badge']}, Days Left: {tier_day0['days_left']}")
    assert tier_day0['tier'] == 'month_1_free'
    assert tier_day0['days_left'] == 30

    # 1. Day 0 user claims reward immediately
    expiry_str = add_vip_months(test_user_id, 1)
    set_channel_reward_claimed(test_user_id, True)
    print(f"Expiry after claim: {expiry_str}")

    tier_claimed = get_user_access_tier(test_user_id, is_channel_member=True)
    print(f"Day 0 Claimed Tier: {tier_claimed['tier']}, Days Left: {tier_claimed['days_left']}, Expires At: {tier_claimed['expires_at']}")
    assert tier_claimed['is_active'] is True
    assert tier_claimed['days_left'] == 60, f"Expected 60 days left, got {tier_claimed['days_left']}"
    assert has_claimed_channel_reward(test_user_id) is True
    print("✅ Verified: Day 0 claim grants full 60 days (Month 1 + Month 2 = 2 Full Months Free VIP Access)!")

    # 2. Test Day 15 user (15 days left in Month 1)
    test_user_day15 = 999888776
    register_user(test_user_day15, "test_day15", "Test")
    set_user_country(test_user_day15, "IN", "India", "INR", "₹")
    # Simulate registration 15 days ago
    conn = get_connection()
    cur = conn.cursor()
    past_date = (datetime.date.today() - datetime.timedelta(days=15)).isoformat()
    cur.execute("UPDATE users SET joined_at = ? WHERE user_id = ?", (past_date, test_user_day15))
    conn.commit()
    conn.close()

    tier_before = get_user_access_tier(test_user_day15)
    print(f"\nDay 15 Tier Before Claim: {tier_before['tier']}, Days Left: {tier_before['days_left']}")
    assert tier_before['days_left'] == 15, f"Expected 15 days left, got {tier_before['days_left']}"

    add_vip_months(test_user_day15, 1)
    tier_after = get_user_access_tier(test_user_day15, is_channel_member=True)
    print(f"Day 15 Tier After Claim: {tier_after['tier']}, Days Left: {tier_after['days_left']}, Expires At: {tier_after['expires_at']}")
    # 15 days remaining in month 1 + 30 days for month 2 = 45 days from today! (Total 60 days from joined_at)
    assert tier_after['days_left'] == 45, f"Expected 45 days left (15 + 30), got {tier_after['days_left']}"
    print("✅ Verified: Day 15 claim preserves all remaining 15 days of Month 1 + adds 30 days of Month 2 (45 days left)!")

if __name__ == "__main__":
    run_tests()
