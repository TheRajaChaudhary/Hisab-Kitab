import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import datetime
import sqlite3

# Ensure hisab_kitab_bot is importable
sys.path.insert(0, r"d:\STORM@RAJA\Antigravity\Deals Fetcher")

from hisab_kitab_bot.config import (
    COUNTRY_CHANNELS,
    MONTHLY_PASS_PRICING,
    get_stars_price_for_months,
    get_country_channel_info
)
from hisab_kitab_bot.database import (
    init_db,
    register_user,
    set_user_country,
    set_user_language,
    get_user_access_tier,
    add_vip_months,
    set_user_channel_status,
    add_referral,
    get_connection
)
from hisab_kitab_bot.i18n import (
    get_vip_pass_keyboard,
    get_channel_join_keyboard,
    get_format_select_keyboard
)

def run_tests():
    print("=== STARTING COMPREHENSIVE VERIFICATION FOR VIP & CHANNEL TIERS ===")
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    # Clean up any previous test users
    test_uids = [991001, 991002, 991003, 991004, 991005]
    for uid in test_uids:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM referrals WHERE referrer_id = ? OR referred_user_id = ?", (uid, uid))
        cursor.execute("DELETE FROM expenses WHERE user_id = ?", (uid,))
    conn.commit()

    today = datetime.date.today()

    # TEST 1: Pricing calculations (1 to 12 months)
    print("\n[Test 1] Testing Pricing for 1 to 12 Months...")
    expected_pricing = {
        1: 25, 2: 50, 3: 70, 4: 95, 5: 115, 6: 130,
        7: 155, 8: 175, 9: 190, 10: 210, 11: 225, 12: 240
    }
    for m, exp_p in expected_pricing.items():
        act_p = get_stars_price_for_months(m)
        assert act_p == exp_p, f"Month {m}: expected {exp_p}, got {act_p}"
    print("✓ All 1-12 month Stars pricing correct!")

    # TEST 2: 7 Country Channels verification
    print("\n[Test 2] Testing 7 Special Country Channels...")
    expected_codes = {'IN', 'US', 'IT', 'ES', 'GB', 'DE', 'FR'}
    assert set(COUNTRY_CHANNELS.keys()) == expected_codes
    for code in expected_codes:
        ch = get_country_channel_info(code)
        assert ch is not None
        assert ch['channel_username'].startswith("@")
        assert "t.me" in ch['channel_url']
        print(f"  ✓ {code}: {ch['title']} -> {ch['channel_username']} ({ch['channel_url']})")

    # TEST 3: Month 1 Free Access (Days 0 to 29) for ALL users
    print("\n[Test 3] Testing Month 1 Free Trial (Day 5)...")
    uid_m1 = 991001
    register_user(uid_m1, "user_m1", "Month1 User")
    set_user_country(uid_m1, "IN", "India", "INR", "₹")
    # Simulate joined 5 days ago
    day_5 = (today - datetime.timedelta(days=5)).isoformat()
    cursor.execute("UPDATE users SET joined_at = ? WHERE user_id = ?", (day_5, uid_m1))
    conn.commit()

    tier_m1 = get_user_access_tier(uid_m1, is_channel_member=False)
    assert tier_m1["is_active"] is True, "Month 1 should be active regardless of channel"
    assert tier_m1["tier"] == "month_1_free"
    assert tier_m1["days_left"] == 25
    print(f"  ✓ Month 1 User: Active={tier_m1['is_active']}, Tier={tier_m1['tier']}, Days Left={tier_m1['days_left']}")

    # TEST 4: Month 2 Free Access for 7 Countries (Days 30 to 59)
    print("\n[Test 4] Testing Month 2 Access for Special 7 Countries (Day 35)...")
    uid_m2_in = 991002
    register_user(uid_m2_in, "user_m2_in", "India User M2")
    set_user_country(uid_m2_in, "IN", "India", "INR", "₹")
    day_35 = (today - datetime.timedelta(days=35)).isoformat()
    cursor.execute("UPDATE users SET joined_at = ? WHERE user_id = ?", (day_35, uid_m2_in))
    conn.commit()

    # Case 4a: Not in channel -> PAUSED
    tier_paused = get_user_access_tier(uid_m2_in, is_channel_member=False)
    assert tier_paused["is_active"] is False
    assert tier_paused["tier"] == "month_2_paused"
    assert tier_paused["requires_channel"] is True
    print(f"  ✓ 7-Country User (Not in channel): Active={tier_paused['is_active']}, Tier={tier_paused['tier']}, RequiresChannel={tier_paused['requires_channel']}")

    # Case 4b: In channel -> ACTIVE
    tier_active = get_user_access_tier(uid_m2_in, is_channel_member=True)
    assert tier_active["is_active"] is True
    assert tier_active["tier"] == "month_2_channel"
    assert tier_active["requires_channel"] is False
    print(f"  ✓ 7-Country User (In channel): Active={tier_active['is_active']}, Tier={tier_active['tier']}, RequiresChannel={tier_active['requires_channel']}")

    # TEST 5: Month 2 for Non-7 Countries (e.g. BR, RU, GLOBAL)
    print("\n[Test 5] Testing Month 2 Access for Other Countries (Day 35)...")
    uid_m2_other = 991003
    register_user(uid_m2_other, "user_m2_other", "Brazil User")
    set_user_country(uid_m2_other, "BR", "Brazil", "BRL", "R$")
    cursor.execute("UPDATE users SET joined_at = ? WHERE user_id = ?", (day_35, uid_m2_other))
    conn.commit()

    tier_other = get_user_access_tier(uid_m2_other, is_channel_member=True)
    assert tier_other["is_active"] is False, "Other countries only get Month 1 free"
    assert tier_other["tier"] == "trial_expired"
    print(f"  ✓ Other Country User (Day 35): Active={tier_other['is_active']}, Tier={tier_other['tier']}")

    # TEST 6: Expired beyond 60 days
    print("\n[Test 6] Testing Day 65 Expired Status...")
    uid_exp = 991004
    register_user(uid_exp, "user_exp", "Expired User")
    set_user_country(uid_exp, "IN", "India", "INR", "₹")
    day_65 = (today - datetime.timedelta(days=65)).isoformat()
    cursor.execute("UPDATE users SET joined_at = ? WHERE user_id = ?", (day_65, uid_exp))
    conn.commit()

    tier_exp = get_user_access_tier(uid_exp, is_channel_member=True)
    assert tier_exp["is_active"] is False
    assert tier_exp["tier"] == "expired"
    print(f"  ✓ User beyond Day 60: Active={tier_exp['is_active']}, Tier={tier_exp['tier']}")

    # TEST 7: VIP Pass Purchase (1 to 12 Months)
    print("\n[Test 7] Testing VIP Pass Extension (1 Month and 12 Months)...")
    exp_str_1 = add_vip_months(uid_exp, 1)
    tier_vip_1 = get_user_access_tier(uid_exp)
    assert tier_vip_1["is_active"] is True
    assert tier_vip_1["tier"] == "vip"
    assert tier_vip_1["days_left"] == 30
    print(f"  ✓ 1 Month VIP Added: Expires={exp_str_1}, Days Left={tier_vip_1['days_left']}")

    # Stack 12 more months
    exp_str_12 = add_vip_months(uid_exp, 12)
    tier_vip_12 = get_user_access_tier(uid_exp)
    assert tier_vip_12["is_active"] is True
    assert tier_vip_12["days_left"] == 390  # 30 + 360
    print(f"  ✓ Stacking 12 Months: Expires={exp_str_12}, Total Days Left={tier_vip_12['days_left']}")

    # TEST 8: Referral Rewards (+30 days)
    print("\n[Test 8] Testing Referral Rewards (+30 days)...")
    referrer_id = uid_m2_other  # expired brazil user
    referred_id = 991005
    register_user(referred_id, "ref_friend", "Referred Friend")
    success = add_referral(referrer_id, referred_id)
    assert success is True

    tier_ref = get_user_access_tier(referrer_id)
    assert tier_ref["is_active"] is True
    assert tier_ref["tier"] == "vip"
    assert tier_ref["days_left"] == 30
    print(f"  ✓ Referral reward awarded 30 days active VIP to referrer! Days Left={tier_ref['days_left']}")

    # TEST 9: Keyboards Generation
    print("\n[Test 9] Testing Keyboard UI Generation...")
    kb_vip = get_vip_pass_keyboard(selected_months=3, lang='hi')
    assert kb_vip is not None
    assert len(kb_vip.inline_keyboard) >= 4

    kb_channel = get_channel_join_keyboard(country_code='IN', lang='hi')
    assert kb_channel is not None
    assert len(kb_channel.inline_keyboard) >= 4

    kb_fmt_vip = get_format_select_keyboard("2026-09-01", "2026-09-20", is_vip=True)
    assert "Free VIP" in kb_fmt_vip.inline_keyboard[0][0].text

    kb_fmt_pause = get_format_select_keyboard("2026-09-01", "2026-09-20", is_channel_paused=True, country_code='IN')
    assert "Join" in kb_fmt_pause.inline_keyboard[0][0].text

    print("  ✓ All inline keyboards generated correctly without syntax/runtime errors!")

    # Cleanup test users
    for uid in test_uids:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        cursor.execute("DELETE FROM referrals WHERE referrer_id = ? OR referred_user_id = ?", (uid, uid))
        cursor.execute("DELETE FROM expenses WHERE user_id = ?", (uid,))
    conn.commit()
    conn.close()

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
