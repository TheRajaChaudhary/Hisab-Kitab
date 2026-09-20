import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

sys.path.insert(0, r"d:\STORM@RAJA\Antigravity\Deals Fetcher")

from hisab_kitab_bot.i18n import (
    get_main_keyboard,
    get_settings_keyboard,
    get_period_select_keyboard,
    get_vip_pass_keyboard,
    get_channel_join_keyboard,
    get_format_select_keyboard,
    get_entries_management_keyboard,
    get_referral_inline_keyboard,
    BUTTON_TO_ACTION,
    ACTION_BACK,
    ACTION_VIP,
    ACTION_LOOT
)
from hisab_kitab_bot.countries import (
    get_country_select_keyboard,
    get_country_languages_keyboard,
    get_all_languages_keyboard
)

def run_tests():
    print("=== STARTING VERIFICATION FOR BACK BUTTON & INDIA-ONLY LOOT DEALS ===")

    # 1. Test India vs Non-India Main Keyboard
    print("\n[Test 1] Testing get_main_keyboard for India ('IN')...")
    kb_in_hi = get_main_keyboard(lang='hi', country_code='IN')
    kb_in_en = get_main_keyboard(lang='en', country_code='IN')
    
    # Check that "🔥 Today's Loot Deals" exists for India
    in_buttons_hi = [b.text for row in kb_in_hi.keyboard for b in row]
    in_buttons_en = [b.text for row in kb_in_en.keyboard for b in row]
    assert "🔥 Today's Loot Deals" in in_buttons_hi, "Loot Deals must be on India keyboard"
    assert "🔥 Today's Loot Deals" in in_buttons_en, "Loot Deals must be on India keyboard"
    print("  ✓ India keyboard includes '🔥 Today's Loot Deals'")

    print("\n[Test 2] Testing get_main_keyboard for NON-India Countries ('US', 'GB', 'RU', 'BR', 'GLOBAL')...")
    non_in_countries = ['US', 'GB', 'RU', 'BR', 'GLOBAL', 'FR', 'DE', 'AE']
    for c_code in non_in_countries:
        for lang in ('en', 'hi', 'ru', 'es', 'ar', 'id'):
            kb = get_main_keyboard(lang=lang, country_code=c_code)
            buttons = [b.text for row in kb.keyboard for b in row]
            assert "🔥 Today's Loot Deals" not in buttons, f"Loot Deals MUST NOT be on {c_code} keyboard ({lang})"
    print("  ✓ Verified: '🔥 Today's Loot Deals' is completely absent for all other countries!")

    # 2. Test Non-India has VIP Pass button on row 4
    kb_us_en = get_main_keyboard(lang='en', country_code='US')
    us_buttons = [b.text for row in kb_us_en.keyboard for b in row]
    assert "🌟 VIP Pass" in us_buttons, "Non-India English keyboard should have '🌟 VIP Pass'"
    
    kb_us_hi = get_main_keyboard(lang='hi', country_code='US')
    us_hi_buttons = [b.text for row in kb_us_hi.keyboard for b in row]
    assert "🌟 VIP पास" in us_hi_buttons, "Non-India Hindi keyboard should have '🌟 VIP पास'"
    print("  ✓ Verified: Non-India keyboards have VIP Pass button instead of Loot Deals!")

    # 3. Test BUTTON_TO_ACTION for Back triggers
    print("\n[Test 3] Testing BUTTON_TO_ACTION for Back triggers...")
    back_triggers = ["🔙 वापस", "🔙 Back", "🔙 वापस (Back)", "🔙 Main Menu", "🔙 मुख्य मेनू", "back", "/back", "wapas", "वापस"]
    for t in back_triggers:
        assert BUTTON_TO_ACTION.get(t) == ACTION_BACK, f"Trigger '{t}' should map to ACTION_BACK"
    print("  ✓ All Back button texts and chat words map correctly to ACTION_BACK!")

    # 4. Test Inline Keyboards have Back buttons
    print("\n[Test 4] Testing Inline Keyboards have Back buttons...")
    
    # 4a: Period select keyboard
    p_kb = get_period_select_keyboard('hi')
    p_cbs = [b.callback_data for row in p_kb.inline_keyboard for b in row]
    assert "back_to_main" in p_cbs, "get_period_select_keyboard must have back_to_main"
    print("  ✓ get_period_select_keyboard has 'back_to_main'")

    # 4b: Settings keyboard
    s_kb = get_settings_keyboard('hi')
    s_cbs = [b.callback_data for row in s_kb.inline_keyboard for b in row]
    assert "back_to_main" in s_cbs, "get_settings_keyboard must have back_to_main"
    print("  ✓ get_settings_keyboard has 'back_to_main'")

    # 4c: VIP pass keyboard
    v_kb = get_vip_pass_keyboard(3, 'hi')
    v_cbs = [b.callback_data for row in v_kb.inline_keyboard for b in row]
    assert "open_statement" in v_cbs and "back_to_main" in v_cbs, "get_vip_pass_keyboard must have both statement and back_to_main"
    print("  ✓ get_vip_pass_keyboard has 'open_statement' and 'back_to_main'")

    # 4d: Channel join keyboard
    ch_kb = get_channel_join_keyboard('IN', 'hi')
    ch_cbs = [b.callback_data for row in ch_kb.inline_keyboard for b in row]
    assert "back_to_main" in ch_cbs, "get_channel_join_keyboard must have back_to_main"
    print("  ✓ get_channel_join_keyboard has 'back_to_main'")

    # 4e: Format select keyboard (both VIP and regular)
    fmt_vip = get_format_select_keyboard("2026-09-01", "2026-09-20", 'hi', is_vip=True)
    fmt_vip_cbs = [b.callback_data for row in fmt_vip.inline_keyboard for b in row]
    assert "period_back" in fmt_vip_cbs and "back_to_main" in fmt_vip_cbs
    
    fmt_reg = get_format_select_keyboard("2026-09-01", "2026-09-20", 'hi', is_vip=False)
    fmt_reg_cbs = [b.callback_data for row in fmt_reg.inline_keyboard for b in row]
    assert "period_back" in fmt_reg_cbs and "back_to_main" in fmt_reg_cbs
    print("  ✓ get_format_select_keyboard has 'period_back' and 'back_to_main'")

    # 4f: Entries management keyboard
    dummy_entries = [{"id": 1, "amount": 50, "category": "Food", "note": "Tea", "type": "expense"}]
    em_kb = get_entries_management_keyboard(dummy_entries, 'hi', '₹')
    em_cbs = [b.callback_data for row in em_kb.inline_keyboard for b in row]
    assert "del_done" in em_cbs and "back_to_main" in em_cbs
    print("  ✓ get_entries_management_keyboard has 'del_done' and 'back_to_main'")

    # 4g: Referral inline keyboard
    ref_kb = get_referral_inline_keyboard("https://t.me/dummy", 'hi')
    ref_cbs = [b.callback_data for row in ref_kb.inline_keyboard for b in row]
    assert "open_statement" in ref_cbs and "back_to_main" in ref_cbs
    print("  ✓ get_referral_inline_keyboard has 'open_statement' and 'back_to_main'")

    # 4h: Country selector with show_back=True
    c_kb = get_country_select_keyboard(page=0, show_back=True)
    c_cbs = [b.callback_data for row in c_kb.inline_keyboard for b in row]
    assert "back_to_main" in c_cbs
    print("  ✓ get_country_select_keyboard has 'back_to_main'")

    # 4i: Country languages with prefix='setlang'
    lang_kb = get_country_languages_keyboard('IN', prefix='setlang', show_back=True)
    l_cbs = [b.callback_data for row in lang_kb.inline_keyboard for b in row]
    assert "open_settings" in l_cbs and "back_to_main" in l_cbs
    print("  ✓ get_country_languages_keyboard has 'open_settings' and 'back_to_main'")

    # 4j: All languages with prefix='setlang'
    all_lang_kb = get_all_languages_keyboard(prefix='setlang')
    al_cbs = [b.callback_data for row in all_lang_kb.inline_keyboard for b in row]
    assert "open_language_picker" in al_cbs and "back_to_main" in al_cbs
    print("  ✓ get_all_languages_keyboard has 'open_language_picker' and 'back_to_main'")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
