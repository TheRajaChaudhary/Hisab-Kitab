import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import datetime
from hisab_kitab_bot.database import (
    init_db,
    register_user,
    set_user_country,
    set_user_language,
    get_user_access_tier,
    get_channel_shares_count,
    record_channel_share,
    has_claimed_share_reward,
    set_share_reward_claimed,
    add_vip_months
)
from hisab_kitab_bot.i18n import get_referral_inline_keyboard
from hisab_kitab_bot.config import COUNTRY_CHANNELS

def test_lucky_vip_flow():
    init_db()
    test_user_id = 9999111122
    register_user(test_user_id, "lucky_tester", "Lucky")
    set_user_country(test_user_id, "IN", "India", "INR", "₹")
    set_user_language(test_user_id, "hi")

    tier_info = get_user_access_tier(test_user_id)
    assert tier_info['is_active'] is True
    assert "expires_at" in tier_info
    print(f"[PASS] Tier info active: {tier_info['badge']}, expires_at: {tier_info['expires_at']}")

    # Check Referral keyboard with Shopping Channel Share in Hindi
    cshare_url = f"https://t.me/test_bot?start=cshare_{test_user_id}_IN"
    kb_hi = get_referral_inline_keyboard(
        "https://t.me/test_bot?start=ref_9999111122",
        country_code="IN",
        lang="hi",
        already_claimed=False,
        channel_share_url=cshare_url,
        shares_count=0,
        share_reward_claimed=False
    )
    found_shopping_share_btn = False
    for row in kb_hi.inline_keyboard:
        for btn in row:
            if "शॉपिंग चैनल" in btn.text:
                found_shopping_share_btn = True
                print(f"[DEBUG URL]: {btn.url}")
                assert "t.me/share/url" in btn.url
                print(f"[PASS] Found shopping share button: {btn.text}")
    assert found_shopping_share_btn, "Shopping channel share button not found!"

    # English version
    kb_en = get_referral_inline_keyboard(
        "https://t.me/test_bot?start=ref_9999111122",
        country_code="US",
        lang="en",
        already_claimed=False,
        channel_share_url=f"https://t.me/test_bot?start=cshare_{test_user_id}_US",
        shares_count=0,
        share_reward_claimed=False
    )
    found_shopping_share_en = False
    for row in kb_en.inline_keyboard:
        for btn in row:
            if "Shopping Channel" in btn.text:
                found_shopping_share_en = True
                print(f"[DEBUG EN URL]: {btn.url}")
                assert "t.me/share/url" in btn.url
                print(f"[PASS] Found English shopping share button: {btn.text}")
    assert found_shopping_share_en, "English shopping channel share button not found!"

    print("ALL LUCKY VIP & SHOPPING SHARE TESTS PASSED!")

if __name__ == "__main__":
    test_lucky_vip_flow()
