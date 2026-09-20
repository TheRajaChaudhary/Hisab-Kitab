import os
import sys
sys.path.insert(0, os.path.abspath("."))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import datetime

from hisab_kitab_bot.database import (
    get_connection,
    register_user,
    set_user_country,
    add_vip_months,
    get_user_access_tier,
    has_claimed_channel_reward,
    set_channel_reward_claimed,
    record_channel_share,
    get_channel_shares_count,
    has_claimed_share_reward,
    set_share_reward_claimed,
    init_db
)
from hisab_kitab_bot.i18n import (
    get_main_keyboard,
    get_referral_inline_keyboard,
    get_vip_pass_keyboard,
    get_all_channels_keyboard
)

def run_tests():
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id IN (888111, 888222, 888333, 888444)")
    cur.execute("DELETE FROM channel_shares WHERE sharer_id IN (888111, 888222)")
    conn.commit()
    conn.close()

    print("=== Test 1: Today's Loot Deals Button EXCLUSIVELY for India ===")
    kb_india = get_main_keyboard('en', 'IN')
    kb_india_texts = [btn.text for row in kb_india.keyboard for btn in row]
    print(f"India Menu Buttons: {kb_india_texts}")
    assert "🔥 Today's Loot Deals" in kb_india_texts, "India menu MUST contain Today's Loot Deals!"

    kb_us = get_main_keyboard('en', 'US')
    kb_us_texts = [btn.text for row in kb_us.keyboard for btn in row]
    print(f"US Menu Buttons: {kb_us_texts}")
    assert "🔥 Today's Loot Deals" not in kb_us_texts, "US menu MUST NOT contain Today's Loot Deals!"

    kb_global = get_main_keyboard('en', 'GLOBAL')
    kb_global_texts = [btn.text for row in kb_global.keyboard for btn in row]
    print(f"Global Menu Buttons: {kb_global_texts}")
    assert "🔥 Today's Loot Deals" not in kb_global_texts, "Global menu MUST NOT contain Today's Loot Deals!"
    print("✅ Verified: 'Today's Loot Deals' is strictly exclusive to India!")

    print("\n=== Test 2: No User Gets Access to 7 Channels at Once ===")
    single_kb = get_all_channels_keyboard('IN', 'en')
    btn_texts = [btn.text for row in single_kb.inline_keyboard for btn in row]
    print(f"Channels Keyboard Buttons: {btn_texts}")
    assert len(btn_texts) <= 2, f"Expected single channel and back, got: {btn_texts}"
    assert "Deals Fetcher 🇮🇳" in btn_texts[0]
    print("✅ Verified: No multi-channel list exposed!")

    print("\n=== Test 3: Channel Free Pass Claim Button Disappears Once Claimed ===")
    # Unclaimed state
    ref_kb_unclaimed = get_referral_inline_keyboard(
        "https://t.me/TestBot?start=ref_123",
        country_code="IN",
        lang="en",
        already_claimed=False,
        channel_share_url="https://t.me/TestBot?start=cshare_123_IN",
        shares_count=0,
        share_reward_claimed=False
    )
    unclaimed_btns = [btn.text for row in ref_kb_unclaimed.inline_keyboard for btn in row]
    print(f"Unclaimed Refer Buttons: {unclaimed_btns}")
    assert any("Claim 2 Months Free VIP Pass" in text for text in unclaimed_btns), "Claim button should be visible when unclaimed!"

    # Claimed state
    ref_kb_claimed = get_referral_inline_keyboard(
        "https://t.me/TestBot?start=ref_123",
        country_code="IN",
        lang="en",
        already_claimed=True,
        channel_share_url="https://t.me/TestBot?start=cshare_123_IN",
        shares_count=0,
        share_reward_claimed=False
    )
    claimed_btns = [btn.text for row in ref_kb_claimed.inline_keyboard for btn in row]
    print(f"Claimed Refer Buttons: {claimed_btns}")
    assert not any("Claim 2 Months Free VIP Pass" in text for text in claimed_btns), "Claim button MUST NOT be visible when already claimed!"
    print("✅ Verified: Channel claim button shows ONLY until claimed!")

    # VIP screen claim button
    vip_kb_unclaimed = get_vip_pass_keyboard(1, 'en', channel_claimable=True, country_code='IN')
    vip_unclaimed_btns = [btn.text for row in vip_kb_unclaimed.inline_keyboard for btn in row]
    assert any("Join India Channel for 1 Mo Free VIP" in text for text in vip_unclaimed_btns), "Channel VIP option should appear when claimable!"

    vip_kb_claimed = get_vip_pass_keyboard(1, 'en', channel_claimable=False, country_code='IN')
    vip_claimed_btns = [btn.text for row in vip_kb_claimed.inline_keyboard for btn in row]
    assert not any("Join India Channel for 1 Mo Free VIP" in text for text in vip_claimed_btns), "Channel VIP option MUST disappear once claimed!"
    print("✅ Verified: VIP pass menu channel option shows ONLY until claimed!")

    print("\n=== Test 4: 10-Friends Channel Share Anti-Cheating & VIP Reward ===")
    sharer_id = 888111
    register_user(sharer_id, "sharer_user", "Sharer")
    set_user_country(sharer_id, "IN", "India", "INR", "₹")

    # Anti-cheat test: User tries to click own share link
    is_new, count = record_channel_share(sharer_id, sharer_id, "IN")
    assert is_new is False and count == 0, "Anti-cheat failed: User was able to refer themselves!"
    print("🛡️ Anti-cheat 1: Self-referral rejected successfully.")

    # Friend 1 visits
    f1_id = 9001
    is_new, count = record_channel_share(sharer_id, f1_id, "IN")
    assert is_new is True and count == 1, f"Expected count=1, got {count}"

    # Friend 1 visits again (cheat attempt: duplicate click)
    is_new, count = record_channel_share(sharer_id, f1_id, "IN")
    assert is_new is False and count == 1, f"Anti-cheat failed: Duplicate friend visit counted! Count={count}"
    print("🛡️ Anti-cheat 2: Duplicate clicks from same friend rejected successfully.")

    # Friends 2 to 10 visit
    for i in range(2, 11):
        friend_id = 9000 + i
        is_new, count = record_channel_share(sharer_id, friend_id, "IN")
        assert is_new is True, f"Failed to record friend {friend_id}"

    total_shares = get_channel_shares_count(sharer_id)
    print(f"Total distinct friends tracked: {total_shares}/10")
    assert total_shares == 10, f"Expected 10 distinct friends, got {total_shares}"

    # Before claiming 10 friends reward
    tier_before = get_user_access_tier(sharer_id)
    exp_before = tier_before['days_left']

    # Claim reward: +1 Month (+30 days) VIP
    new_exp = add_vip_months(sharer_id, 1)
    set_share_reward_claimed(sharer_id, True)

    assert has_claimed_share_reward(sharer_id) is True

    tier_after = get_user_access_tier(sharer_id)
    print(f"VIP Days Before Share Reward: {exp_before} days -> After Share Reward: {tier_after['days_left']} days (Expiry: {new_exp})")
    assert tier_after['days_left'] == exp_before + 30, f"Expected +30 days added, got {tier_after['days_left'] - exp_before}"
    print("✅ Verified: Reaching 10 distinct friends grants +1 Extra Month Free VIP Access!")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
