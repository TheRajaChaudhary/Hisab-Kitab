import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.parse
from hisab_kitab_bot.config import COUNTRY_CHANNELS
from hisab_kitab_bot.i18n import get_referral_inline_keyboard
from hisab_kitab_bot.database import (
    init_db,
    register_user,
    set_user_country,
    set_user_language,
    get_user_access_tier,
    add_vip_months,
    has_claimed_share_reward,
    set_share_reward_claimed
)

def test_7_countries_shopping_channel_share():
    init_db()
    
    expected_channels = {
        "IN": "https://t.me/DealsFetcher",
        "US": "https://t.me/ApexDealsDaily",
        "IT": "https://t.me/AffariImperdibili",
        "ES": "https://t.me/ChollosAlDiaES",
        "GB": "https://t.me/TheCrownDeals",
        "DE": "https://t.me/Sparangebote",
        "FR": "https://t.me/MaxiOffres"
    }

    print("=== Testing All 7 Countries Shopping Channel Share URLs ===")
    
    for c_code, expected_url in expected_channels.items():
        ch_info = COUNTRY_CHANNELS[c_code]
        assert ch_info['channel_url'] == expected_url, f"Mismatch for {c_code}: {ch_info['channel_url']} != {expected_url}"
        
        # Test keyboard when not claimed
        kb = get_referral_inline_keyboard(
            ref_url=f"https://t.me/Hisab_Kitab_1Bot?start=ref_123456",
            country_code=c_code,
            lang="hi" if c_code == "IN" else "en",
            already_claimed=False,
            share_reward_claimed=False
        )
        
        share_btn_found = False
        claim_btn_found = False
        
        for row in kb.inline_keyboard:
            for btn in row:
                # Check shopping channel share button
                if "शॉपिंग चैनल" in btn.text or "Shopping Channel" in btn.text:
                    share_btn_found = True
                    print(f"[{c_code}] Button text: '{btn.text}'")
                    print(f"[{c_code}] Button URL: {btn.url}")
                    
                    # Verify Telegram share URL targets the shopping channel, NOT Hisab Kitab
                    assert "t.me/share/url" in btn.url
                    unquoted_url = urllib.parse.unquote(btn.url)
                    assert expected_url in unquoted_url, f"Expected {expected_url} in share URL for {c_code}, got: {unquoted_url}"
                    
                    # Verify Hisab Kitab bot referral is NOT in the shopping channel share URL
                    assert f"start=cshare_" not in unquoted_url
                    assert f"start=ref_" not in unquoted_url
                    print(f"[{c_code}] PASS: Direct shopping channel URL ({expected_url}) is shared! No bot refer link.")
                
                # Check claim share reward button
                if f"claim_share_reward_{c_code}" == getattr(btn, 'callback_data', None):
                    claim_btn_found = True
        
        assert share_btn_found, f"Shopping share button missing for {c_code}"
        assert claim_btn_found, f"Claim share button missing for {c_code} when unclaimed"
        
        # Test keyboard after claiming: claim button MUST be gone
        kb_claimed = get_referral_inline_keyboard(
            ref_url=f"https://t.me/Hisab_Kitab_1Bot?start=ref_123456",
            country_code=c_code,
            lang="hi" if c_code == "IN" else "en",
            already_claimed=True,
            share_reward_claimed=True
        )
        for row in kb_claimed.inline_keyboard:
            for btn in row:
                assert getattr(btn, 'callback_data', None) != f"claim_share_reward_{c_code}", f"Claim button still visible for {c_code} after claim!"
        print(f"[{c_code}] PASS: Claim button disappears once claimed!")
        print("-" * 50)

    print("\nALL 7 COUNTRIES VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_7_countries_shopping_channel_share()
