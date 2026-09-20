import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("Testing hisab_kitab_bot.i18n and hisab_kitab_bot.bot...")

from hisab_kitab_bot.i18n import (
    KEYBOARD_BUTTONS,
    BUTTON_TO_ACTION,
    get_main_keyboard,
    get_settings_keyboard,
    get_vip_pass_keyboard,
    format_expense_logged,
    format_income_logged,
    format_today_summary,
    format_month_summary,
    format_back_message,
    format_daily_summary,
    format_del_response
)

# 1. Check all 19 languages exist in KEYBOARD_BUTTONS
all_19 = ['en', 'hi', 'bn', 'ur', 'es', 'pt', 'ru', 'ar', 'id', 'fr', 'de', 'it', 'tr', 'vi', 'ja', 'ko', 'uk', 'uz', 'kk']
for l in all_19:
    assert l in KEYBOARD_BUTTONS, f"Missing {l} in KEYBOARD_BUTTONS"
    assert 'vip' in KEYBOARD_BUTTONS[l], f"Missing vip button in {l}"
    assert 'loot' in KEYBOARD_BUTTONS[l], f"Missing loot button in {l}"
    assert 'back' in KEYBOARD_BUTTONS[l], f"Missing back button in {l}"

print(f"PASS: All {len(all_19)} languages verified in KEYBOARD_BUTTONS.")

# 2. Check main keyboard for India vs Non-India
in_kb = get_main_keyboard(lang='hi', country_code='IN')
in_buttons = [b.text for row in in_kb.keyboard for b in row]
assert "🔥 Today's Loot Deals" in in_buttons, "India keyboard missing Loot Deals"
assert "🌟 VIP पास" in in_buttons, "India keyboard missing VIP Pass"

us_kb = get_main_keyboard(lang='en', country_code='US')
us_buttons = [b.text for row in us_kb.keyboard for b in row]
assert "🌟 VIP Pass" in us_buttons, "US keyboard missing VIP Pass"
assert "🔥 Today's Loot Deals" not in us_buttons, "US keyboard shouldn't have Loot Deals"

# Check back button in settings keyboard
settings_hi = get_settings_keyboard('hi')
settings_hi_btns = [b.text for row in settings_hi.inline_keyboard for b in row]
assert any("🔙" in b for b in settings_hi_btns), "Settings keyboard missing Back button"

print("PASS: Main keyboard correctly configured for India (Loot + VIP) and Non-India (VIP only, no Loot).")

# 3. Check formatters
hi_daily = format_daily_summary('hi', '20 September 2026', '₹', 450.0, 12000.0, 20000.0, is_india=True)
assert "Deals Fetcher" in hi_daily
assert "आज का दैनिक हिसाब" in hi_daily

us_daily = format_daily_summary('en', '20 September 2026', '$', 50.0, 1200.0, 2000.0, is_india=False)
assert "Deals Fetcher" not in us_daily
assert "Daily Recap" in us_daily

# 4. Import bot to check syntax and integrity
import hisab_kitab_bot.bot as bot
assert bot.daily_night_summary_job is not None
print("PASS: hisab_kitab_bot.bot imported cleanly with zero errors.")
print("ALL TESTS PASSED SUCCESSFULLY!")
