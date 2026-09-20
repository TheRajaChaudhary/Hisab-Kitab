import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from hisab_kitab_bot.database import (
    register_user,
    set_user_language,
    set_user_country,
    add_text_saver_items,
    get_text_saver_items,
    toggle_text_saver_item,
    delete_text_saver_item,
    clear_completed_text_saver_items,
    clear_all_text_saver_items,
    get_text_saver_stats
)
from hisab_kitab_bot.i18n import (
    get_main_keyboard,
    get_text_saver_keyboard,
    get_text_saver_clear_confirm_keyboard,
    BUTTON_TO_ACTION,
    ACTION_TEXT_SAVER
)

def run_tests():
    print("=== STARTING TEXT SAVER TESTS ===")
    test_user_id = 77665544
    register_user(test_user_id, username="test_textsaver_user", first_name="SaverUser")
    set_user_language(test_user_id, "hi")
    set_user_country(test_user_id, "IN", "India", "INR", "₹")

    # Clean initial state
    clear_all_text_saver_items(test_user_id)

    # 1. Test adding items via multi-line text
    print("\n--- 1. Testing Multi-Line Text Addition ---")
    multi_line = """
    दूध 1 लीटर
    ब्रेड (Brown Bread)
    - चाय पत्ती (Tata Tea)
    • चीनी 2 किलो
    1. नमक पैकेट
    """
    created = add_text_saver_items(test_user_id, multi_line, country_code="IN")
    print(f"Created {len(created)} items: {[c['text'] for c in created]}")
    assert len(created) == 5, f"Expected 5 items, got {len(created)}"
    assert created[0]['text'] == "दूध 1 लीटर"
    assert created[2]['text'] == "चाय पत्ती (Tata Tea)", f"Prefix not stripped properly: {created[2]['text']}"
    assert created[3]['text'] == "चीनी 2 किलो"
    assert created[4]['text'] == "नमक पैकेट"
    print("OK: Multi-line parsing and prefix stripping works accurately!")

    # 2. Test comma-separated addition
    print("\n--- 2. Testing Comma-Separated Addition ---")
    comma_text = "साबुन, शैम्पू, टूथपेस्ट"
    created_comma = add_text_saver_items(test_user_id, comma_text, country_code="IN")
    assert len(created_comma) == 3, f"Expected 3 items, got {len(created_comma)}"
    print("OK: Comma separated text added 3 items!")

    # 3. Test get items & stats
    print("\n--- 3. Testing get_text_saver_items & stats ---")
    items = get_text_saver_items(test_user_id)
    assert len(items) == 8, f"Expected 8 total items, got {len(items)}"
    stats = get_text_saver_stats(test_user_id)
    assert stats['total'] == 8
    assert stats['pending'] == 8
    assert stats['done'] == 0
    print(f"OK: Stats verified -> Total: {stats['total']}, Pending: {stats['pending']}, Done: {stats['done']}")

    # 4. Test toggle item
    print("\n--- 4. Testing Item Toggle (Done / Pending) ---")
    first_item_id = items[0]['id']
    success, new_status, txt = toggle_text_saver_item(first_item_id, test_user_id)
    assert success is True
    assert new_status == 1, f"Expected status 1 (done), got {new_status}"
    print(f"Toggled item '{txt}' to done (status: {new_status})")

    # Toggle second item
    second_item_id = items[1]['id']
    toggle_text_saver_item(second_item_id, test_user_id)

    stats_after_toggle = get_text_saver_stats(test_user_id)
    assert stats_after_toggle['pending'] == 6
    assert stats_after_toggle['done'] == 2
    print(f"OK: Pending is now {stats_after_toggle['pending']}, Done is {stats_after_toggle['done']}")

    # Toggle first item back to pending
    success, new_status, txt = toggle_text_saver_item(first_item_id, test_user_id)
    assert new_status == 0
    print(f"OK: Toggled '{txt}' back to pending (status: {new_status})")

    # 5. Test clear completed
    print("\n--- 5. Testing Clear Completed Items ---")
    cleared_cnt = clear_completed_text_saver_items(test_user_id)
    assert cleared_cnt == 1, f"Expected 1 item cleared, got {cleared_cnt}"
    items_remaining = get_text_saver_items(test_user_id)
    assert len(items_remaining) == 7
    print(f"OK: Cleared completed items, remaining: {len(items_remaining)}")

    # 6. Test delete single item
    print("\n--- 6. Testing Single Item Deletion ---")
    del_id = items_remaining[0]['id']
    del_ok = delete_text_saver_item(del_id, test_user_id)
    assert del_ok is True
    assert len(get_text_saver_items(test_user_id)) == 6
    print("OK: Single item deleted successfully!")

    # 7. Test clear all items
    print("\n--- 7. Testing Clear All Items ---")
    cleared_all = clear_all_text_saver_items(test_user_id)
    assert cleared_all == 6
    assert len(get_text_saver_items(test_user_id)) == 0
    print("OK: All items cleared!")

    # 8. Test Keyboards and Mappings
    print("\n--- 8. Testing Keyboards & Action Mappings ---")
    main_kb = get_main_keyboard(lang='hi', country_code='IN')
    found_ts_btn = False
    for row in main_kb.keyboard:
        for btn in row:
            if "Text Saver" in btn.text:
                found_ts_btn = True
                print(f"Found Text Saver button on main keyboard: '{btn.text}'")
    assert found_ts_btn, "Text Saver button missing from main keyboard!"

    assert BUTTON_TO_ACTION.get("📝 Text Saver") == ACTION_TEXT_SAVER
    assert BUTTON_TO_ACTION.get("/text_saver") == ACTION_TEXT_SAVER
    assert BUTTON_TO_ACTION.get("/saver") == ACTION_TEXT_SAVER
    assert BUTTON_TO_ACTION.get("सामान") == ACTION_TEXT_SAVER
    print("OK: Action mappings verified!")

    # Test interactive keyboard
    dummy_items = [
        {"id": 1, "text": "दूध", "is_done": 0},
        {"id": 2, "text": "ब्रेड", "is_done": 1}
    ]
    ts_kb = get_text_saver_keyboard(dummy_items, page=1, per_page=6, lang='hi')
    assert any("दूध" in b.text for row in ts_kb.inline_keyboard for b in row)
    assert any("ब्रेड" in b.text for row in ts_kb.inline_keyboard for b in row)
    assert any("सामान जोड़ें" in b.text for row in ts_kb.inline_keyboard for b in row)
    print("OK: Interactive Text Saver keyboard verified!")

    conf_kb = get_text_saver_clear_confirm_keyboard(lang='hi')
    assert len(conf_kb.inline_keyboard) == 2
    print("OK: Clear confirm keyboard verified!")

    print("\n🎉 ALL TEXT SAVER TESTS PASSED 100%! 🎉")

if __name__ == "__main__":
    run_tests()
