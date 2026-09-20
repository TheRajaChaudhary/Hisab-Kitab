import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import logging
import datetime
import calendar
from typing import Tuple
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters
)

from .config import (
    BOT_TOKEN,
    BOT_USERNAME,
    DEALS_FETCHER_URL,
    STARS_PDF_PRICE,
    STARS_EXCEL_PRICE,
    STARS_BUNDLE_PRICE,
    COUNTRY_CHANNELS,
    get_stars_price_for_months,
    MONTHLY_PASS_PRICING,
    get_country_channel_info
)
from .database import (
    register_user,
    set_user_language,
    get_user_language,
    set_user_country,
    has_user_selected_country,
    get_user_country,
    get_user_currency,
    add_expense,
    delete_last_expense,
    delete_expense_by_id,
    get_recent_expenses,
    get_today_expenses,
    get_today_total,
    get_month_category_breakdown,
    set_budget,
    get_user_budget,
    add_to_budget,
    add_client,
    get_client,
    update_client_phone,
    update_client_email,
    delete_client,
    get_all_clients,
    get_client_details_with_balance,
    add_client_transaction,
    get_client_transactions,
    get_client_transactions_with_running_balance,
    delete_client_transaction,
    has_claimed_channel_reward,
    set_channel_reward_claimed,
    record_channel_share,
    get_channel_shares_count,
    has_claimed_share_reward,
    set_share_reward_claimed,
    get_clients_overall_summary,
    log_stars_payment,
    add_referral,
    get_free_access_details,
    get_user_access_tier,
    is_free_access_active,
    has_user_selected_language,
    get_all_active_user_ids,
    add_vip_months,
    set_user_channel_status,
    get_user_channel_status,
    SPECIAL_7_COUNTRIES,
    add_text_saver_items,
    get_text_saver_items,
    toggle_text_saver_item,
    delete_text_saver_item,
    clear_completed_text_saver_items,
    clear_all_text_saver_items,
    get_text_saver_stats
)
from .countries import (
    COUNTRIES,
    get_country,
    get_country_select_keyboard,
    get_country_languages_keyboard,
    get_all_languages_keyboard
)
from .parser import parse_expense_text
from .pdf_generator import generate_statement_pdf, generate_client_report_pdf, get_client_report_date_range
from .excel_generator import generate_statement_excel, generate_client_report_excel
from .i18n import (
    get_main_keyboard,
    get_settings_keyboard,
    get_all_channels_keyboard,
    get_period_select_keyboard,
    get_format_select_keyboard,
    get_vip_pass_keyboard,
    get_channel_join_keyboard,
    get_entries_management_keyboard,
    get_referral_inline_keyboard,
    get_budget_prompt_keyboard,
    get_clients_main_keyboard,
    get_client_skip_phone_keyboard,
    get_client_detail_keyboard,
    get_client_list_keyboard,
    get_client_delete_confirm_keyboard,
    get_client_report_period_keyboard,
    get_client_statement_str,
    get_text_saver_keyboard,
    get_text_saver_clear_confirm_keyboard,
    ACTION_TEXT_SAVER,
    FIRST_TIME_COUNTRY_PROMPT,
    FIRST_TIME_LANG_PROMPT,
    get_msg,
    get_ui_str,
    format_expense_logged,
    format_income_logged,
    format_today_summary,
    format_month_summary,
    format_back_message,
    format_daily_summary,
    format_del_response,
    get_statement_str,
    BUTTON_TO_ACTION,
    ACTION_TODAY,
    ACTION_MONTH,
    ACTION_BUDGET,
    ACTION_STATEMENT,
    ACTION_UNDO,
    ACTION_LANGUAGE,
    ACTION_COUNTRY,
    ACTION_LOOT,
    ACTION_REFER,
    ACTION_VIP,
    ACTION_BACK,
    ACTION_CLIENTS
)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("HisabKitabBot")


# ==========================================
# CHANNEL MEMBERSHIP CHECKER
# ==========================================

async def check_user_channel_membership(bot, user_id: int, country_code: str) -> Tuple[bool, str]:
    """
    Checks if a user is currently a member of their country's deals channel.
    Returns (is_member: bool, detail: str)
    detail can be: 'member', 'admin', 'creator', 'left', 'kicked', 'bot_not_admin', or 'no_channel_needed'
    """
    ch_info = get_country_channel_info(country_code)
    if not ch_info:
        return (True, "no_channel_needed")

    ch_username = ch_info["channel_username"]
    try:
        member = await bot.get_chat_member(chat_id=ch_username, user_id=user_id)
        if member.status in ('creator', 'administrator', 'member'):
            set_user_channel_status(user_id, True)
            return (True, member.status)
        else:
            set_user_channel_status(user_id, False)
            return (False, member.status)
    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Error checking channel member for {user_id} in {ch_username}: {err_msg}")
        if "Member list is inaccessible" in err_msg or "not an administrator" in err_msg.lower():
            # If bot is not admin in channel, fallback to user's verified confirmation state in DB
            verified_in_db = get_user_channel_status(user_id)
            return (verified_in_db, "bot_not_admin")
        return (False, "error")


# ==========================================
# DATE HELPER FUNCTIONS
# ==========================================

def parse_date_range(text: str):
    """
    Parses date range strings such as:
    - '01-08-2026 to 15-09-2026'
    - '01/08/2026 to 20/09/2026'
    - '2026-08-01 - 2026-09-20'
    - '10-09-2026 se 20-09-2026'
    Returns (start_iso, end_iso, display_label) or None
    """
    text = text.strip()
    m = re.search(r'(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})\s*(?:to|se|tak|-)\s*(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})', text, re.IGNORECASE)
    if not m:
        return None

    d1_str = m.group(1).replace('/', '-').replace('.', '-')
    d2_str = m.group(2).replace('/', '-').replace('.', '-')

    def parse_one(s):
        parts = s.split('-')
        if len(parts[0]) == 4:  # YYYY-MM-DD
            return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:  # DD-MM-YYYY
            return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))

    try:
        dt1 = parse_one(d1_str)
        dt2 = parse_one(d2_str)
        if dt1 > dt2:
            dt1, dt2 = dt2, dt1
        lbl = f"{dt1.strftime('%d %b %Y')} - {dt2.strftime('%d %b %Y')}"
        return dt1.isoformat(), dt2.isoformat(), lbl
    except Exception:
        return None


def get_preset_date_range(preset: str):
    today = datetime.date.today()
    if preset == "this_month":
        start_date = datetime.date(today.year, today.month, 1)
        end_date = today
        label = today.strftime("%B %Y")
    elif preset == "last_month":
        first_of_this_month = datetime.date(today.year, today.month, 1)
        last_day_last_month = first_of_this_month - datetime.timedelta(days=1)
        start_date = datetime.date(last_day_last_month.year, last_day_last_month.month, 1)
        end_date = last_day_last_month
        label = last_day_last_month.strftime("%B %Y")
    elif preset == "last_30":
        start_date = today - datetime.timedelta(days=30)
        end_date = today
        label = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
    else:
        start_date = datetime.date(today.year, today.month, 1)
        end_date = today
        label = today.strftime("%B %Y")

    return start_date.isoformat(), end_date.isoformat(), label


# ==========================================
# COMMAND HANDLERS
# ==========================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/start] User {user.id} (@{user.username or ''}) started bot. args={context.args}")
    register_user(user.id, user.username or "", user.first_name or "")

    # 1. Check for Referral Deep Link (e.g., /start ref_12345678)
    if context.args and context.args[0].startswith("ref_"):
        try:
            referrer_id = int(context.args[0].replace("ref_", ""))
            rewarded = add_referral(referrer_id, user.id)
            if rewarded:
                ref_lang = get_user_language(referrer_id)
                ref_country = get_user_country(referrer_id)
                is_ch, _ = await check_user_channel_membership(context.bot, referrer_id, ref_country['country_code'])
                ref_details = get_free_access_details(referrer_id, is_channel_member=is_ch)
                notify_msg = get_msg(
                    'referral_reward_notice',
                    lang=ref_lang,
                    expires_at=ref_details['expires_at']
                )
                try:
                    await context.bot.send_message(chat_id=referrer_id, text=notify_msg, parse_mode="HTML")
                except Exception as e:
                    logger.warning(f"Could not notify referrer {referrer_id}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing referral link: {e}")

    # 1b. Check for Channel Share Deep Link (e.g., /start cshare_12345678_IN)
    elif context.args and context.args[0].startswith("cshare_"):
        try:
            parts = context.args[0].split("_")
            sharer_id = int(parts[1])
            share_c_code = parts[2].upper() if len(parts) > 2 else "IN"

            # Anti-cheating: self-referrals are disallowed
            if user.id != sharer_id:
                is_new, count = record_channel_share(sharer_id, user.id, share_c_code)
                if is_new:
                    sharer_lang = get_user_language(sharer_id)
                    already_rewarded = has_claimed_share_reward(sharer_id)
                    if count >= 10 and not already_rewarded:
                        new_expiry = add_vip_months(sharer_id, 1)
                        set_share_reward_claimed(sharer_id, True)
                        congrats_sharer = (
                            f"🎉 <b>शानदार! 10 दोस्तों का शॉपिंग चैनल शेयर लक्ष्य पूरा हुआ!</b>\n\n"
                            f"आपके 10 दोस्तों ने आपके देश के आधिकारिक शॉपिंग डील्स चैनल लिंक पर विज़िट किया है।\n"
                            f"🎁 आपको मिला है <b>+1 अतिरिक्त महीना (30 दिन) 100% मुफ़्त VIP पास</b>!\n\n"
                            f"🌟 नई वैधता (Valid Until): <b>{new_expiry}</b>"
                            if sharer_lang == 'hi' else
                            f"🎉 <b>Awesome! 10-Friends Shopping Channel Share Goal Reached!</b>\n\n"
                            f"10 friends have visited through your country's official shopping deals channel link.\n"
                            f"🎁 You have received <b>+1 EXTRA MONTH (30 Days) of 100% FREE VIP Pass</b>!\n\n"
                            f"🌟 New Valid Until: <b>{new_expiry}</b>"
                        )
                        try:
                            await context.bot.send_message(chat_id=sharer_id, text=congrats_sharer, parse_mode="HTML")
                        except Exception as e:
                            logger.warning(f"Could not notify sharer {sharer_id}: {e}")
                    elif count < 10:
                        progress_sharer = (
                            f"📢 <b>एक और दोस्त ने आपके शॉपिंग डील्स चैनल लिंक पर क्लिक किया!</b>\n\n"
                            f"📊 प्रगति (Progress): <b>{count}/10 दोस्त</b>\n"
                            f"💡 <i>{10 - count} और दोस्त जुड़ने पर आपको मिलेगा +1 महीना मुफ़्त VIP पास!</i>"
                            if sharer_lang == 'hi' else
                            f"📢 <b>A friend just visited through your shopping deals channel link!</b>\n\n"
                            f"📊 Progress: <b>{count}/10 Friends</b>\n\n"
                            f"💡 <i>{10 - count} more friends needed to unlock +1 Extra Month Free VIP Pass!</i>"
                        )
                        try:
                            await context.bot.send_message(chat_id=sharer_id, text=progress_sharer, parse_mode="HTML")
                        except Exception as e:
                            logger.warning(f"Could not notify sharer {sharer_id}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing channel share link: {e}")

    # 2. Check if user has selected country (FIRST STEP for onboarding)
    if not has_user_selected_country(user.id):
        kb = get_country_select_keyboard(page=0)
        await update.message.reply_text(
            FIRST_TIME_COUNTRY_PROMPT,
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # 3. Check if user has selected language (SECOND STEP for onboarding)
    if not has_user_selected_language(user.id):
        country_info = get_user_country(user.id)
        kb = get_country_languages_keyboard(country_info['country_code'], prefix="initlang")
        await update.message.reply_text(
            FIRST_TIME_LANG_PROMPT,
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # 4. Existing user with country & language configured: send welcome & main keyboard
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    curr_code, curr_sym = get_user_currency(user.id)
    welcome_text = get_msg(
        'welcome',
        lang=lang,
        name=user.first_name or "User",
        currency=curr_sym,
        country=country_info['country_name']
    )
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=keyboard)


async def back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Navigates back to the main menu from any state or sub-menu."""
    user = update.effective_user
    context.user_data['awaiting_custom_dates'] = False
    context.user_data['awaiting_budget_add'] = False
    context.user_data['awaiting_budget'] = False
    context.user_data.pop('client_add_step', None)
    context.user_data.pop('new_client_name', None)
    context.user_data.pop('editing_client_field', None)
    context.user_data.pop('client_tx_flow', None)
    context.user_data.pop('awaiting_client_report_period', None)
    context.user_data.pop('awaiting_text_saver_input', None)
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])

    text = format_back_message(lang)

    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="👇", reply_markup=keyboard)


async def country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows user to view/change their country & local currency."""
    user = update.effective_user
    lang = get_user_language(user.id)
    prompt = get_msg('country_prompt', lang=lang)
    kb = get_country_select_keyboard(page=0)
    await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=kb)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows user to view/change display language."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    prompt = get_msg('language_prompt', lang=lang)
    kb = get_country_languages_keyboard(country_info['country_code'], prefix="setlang")
    await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=kb)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Opens country and language management menu."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    curr_code, curr_sym = get_user_currency(user.id)
    c_code = country_info.get('country_code', 'GLOBAL')

    if lang == 'hi':
        text = (
            f"⚙️ <b>देश एवं भाषा सेटिंग्स (Preferences):</b>\n\n"
            f"• देश (Country): <b>{country_info['country_name']}</b> ({c_code})\n"
            f"• मुद्रा (Currency): <b>{curr_sym} ({curr_code})</b>\n"
            f"• भाषा (Language): <b>{lang.upper()}</b>\n\n"
            f"बदलने के लिए नीचे दिए गए विकल्पों पर टैप करें:"
        )
    else:
        text = (
            f"⚙️ <b>Country & Language Preferences:</b>\n\n"
            f"• Country: <b>{country_info['country_name']}</b> ({c_code})\n"
            f"• Currency: <b>{curr_sym} ({curr_code})</b>\n"
            f"• Language: <b>{lang.upper()}</b>\n\n"
            f"Select an option below to update:"
        )
    kb = get_settings_keyboard(lang)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays user's localized country deals channel with direct join link."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    user_country_code = country_info.get('country_code', 'GLOBAL').upper()

    ch_info = COUNTRY_CHANNELS.get(user_country_code)
    if ch_info:
        if lang == 'hi':
            text = (
                f"📢 <b>{ch_info['flag']} {ch_info['name']} का आधिकारिक डील्स चैनल:</b>\n\n"
                f"• चैनल: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n\n"
                f"<i>रोज़ाना लूट डील्स, डिस्काउंट्स और मुफ़्त VIP पास के लिए चैनल से जुड़ें! 🛍️</i>"
            )
            btn_join = f"📢 {ch_info['title']} ज्वाइन करें"
        else:
            text = (
                f"📢 <b>Official Deals Channel for {ch_info['flag']} {ch_info['name']}:</b>\n\n"
                f"• Channel: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n\n"
                f"<i>Join your country's official channel for daily deals, loot drops, and free VIP pass! 🛍️</i>"
            )
            btn_join = f"📢 Join {ch_info['title']}"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(btn_join, url=ch_info['channel_url'])],
            [InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")]
        ])
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    else:
        text = (
            "🌍 Official deals channels are currently active for supported regions (e.g. India 🇮🇳). Select your country in /settings."
            if lang == 'en' else
            "🌍 आधिकारिक डील्स चैनल समर्थित देशों (जैसे भारत 🇮🇳) के लिए उपलब्ध हैं। आप /settings में अपना देश चुन सकते हैं।"
        )
        await update.message.reply_text(text, parse_mode="HTML")


async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows user to select and purchase 1 to 12 months unlimited VIP statement pass."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    c_code = (country_info.get('country_code') or 'GLOBAL').upper()

    is_ch, _ = await check_user_channel_membership(context.bot, user.id, c_code)
    tier_info = get_user_access_tier(user.id, is_channel_member=is_ch)

    already_claimed = has_claimed_channel_reward(user.id)
    channel_claimable = (c_code in COUNTRY_CHANNELS) and (not already_claimed)

    selected_months = 1
    price = get_stars_price_for_months(selected_months)
    prompt = get_msg(
        'vip_pass_selector_prompt',
        lang=lang,
        selected_months=selected_months,
        price=price
    )
    if tier_info['is_active']:
        status_line = f"🌟 <b>Current Access: {tier_info['badge']}</b> (Expires: {tier_info['expires_at']})\n\n"
        prompt = status_line + prompt

    kb = get_vip_pass_keyboard(selected_months=selected_months, lang=lang, channel_claimable=channel_claimable, country_code=c_code)
    await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=kb)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    curr_code, curr_sym = get_user_currency(user.id)
    country_info = get_user_country(user.id)

    help_text = get_msg(
        'help',
        lang=lang,
        currency=curr_sym,
        country=country_info['country_name']
    )
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])
    await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=keyboard)


async def show_referral_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """Shows user's referral link, country deals channel, and 1-month free VIP claim button."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    c_code = country_info.get('country_code', 'GLOBAL').upper()
    ref_url = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    has_ch = c_code in COUNTRY_CHANNELS
    ch_info = COUNTRY_CHANNELS.get(c_code) or COUNTRY_CHANNELS.get("IN")

    is_ch, _ = await check_user_channel_membership(context.bot, user_id, c_code)
    details = get_free_access_details(user_id, is_channel_member=is_ch)

    already_claimed = has_claimed_channel_reward(user_id)
    ch_status = "✅ Active Member" if is_ch else "📢 Not Joined Yet"

    # 10-Friends Channel Share tracking
    cshare_url = f"https://t.me/{BOT_USERNAME}?start=cshare_{user_id}_{c_code}"
    shares_count = get_channel_shares_count(user_id)
    share_reward_claimed = has_claimed_share_reward(user_id)

    if already_claimed:
        reward_note = "✅ <i>(2 Months Free VIP Pass Active!)</i>"
        claim_instruction_hi = "✅ <i>(2 महीने का मुफ़्त VIP पास पहले से एक्टिव है!)</i>"
        claim_instruction_en = "✅ <i>(2 Months Free VIP Pass is already active!)</i>"
    else:
        reward_note = "🎁 <i>(Join & Tap 'Claim' below for 2 FULL MONTHS Free VIP Pass!)</i>"
        claim_instruction_hi = "👉 <i>चैनल से जुड़ें और नीचे <b>'🎁 2 महीने मुफ़्त VIP पास एक्टिव करें'</b> पर क्लिक करें!</i>"
        claim_instruction_en = "👉 <i>Join the channel and tap <b>'🎁 Claim 2 Months Free VIP Pass'</b> below to activate!</i>"

    if lang == 'hi':
        share_status_hi = (
            "✅ <b>क्लेम किया गया!</b> (+1 अतिरिक्त महीना VIP एक्टिव)"
            if share_reward_claimed else
            "⏳ <i>10 दोस्तों को शॉपिंग चैनल शेयर करें और नीचे दिए गए क्लेम बटन पर टैप करें!</i>"
        )

        msg = f"🎁 <b>रेफरल एवं मुफ़्त VIP पास (VIP Passes & Referrals)</b>\n\n"
        if has_ch:
            msg += (
                f"🌟 <b>ऑफर 1: {ch_info['flag']} {ch_info['name']} का आधिकारिक शॉपिंग डील्स चैनल:</b>\n"
                f"• चैनल: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n"
                f"• स्थिति: <b>{ch_status}</b> {reward_note}\n"
                f"{claim_instruction_hi}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌟 <b>ऑफर 2: 10 दोस्तों को शॉपिंग चैनल शेयर करें (+1 अतिरिक्त महीना मुफ़्त):</b>\n"
                f"• शॉपिंग चैनल लिंक: <a href='{ch_info['channel_url']}'>{ch_info['channel_url']}</a>\n"
                f"• स्थिति: {share_status_hi}\n"
                f"👉 <i>नीचे दिए गए <b>'🛍️ 10 दोस्तों को शॉपिंग चैनल शेयर करें'</b> बटन से अपने देश का शॉपिंग चैनल 10 दोस्तों को भेजें, फिर <b>'🎁 10 दोस्तों को शेयर किया? +1 महीना VIP क्लेम करें'</b> पर टैप करके एक्टिव करें!</i>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )

        msg += (
            f"👥 <b>दोस्तों को बॉट में रेफर करें:</b>\n"
            f"• कुल रेफरल: <b>{details['total_referred']} दोस्त</b>\n"
            f"• वर्तमान स्टेटस: <b>{details.get('badge', 'मुफ़्त पास')}</b>"
        )
        if details['is_active'] and details.get('expires_at'):
            msg += f"\n• वैधता (Expires): <b>{details['expires_at']}</b> ({details.get('days_left', 0)} दिन बाकी)"
        msg += (
            f"\n\n🔗 <b>आपका बॉट रेफरल लिंक:</b>\n"
            f"<code>{ref_url}</code>\n\n"
            f"💡 <i>हर दोस्त के जुड़ने पर आपको अतिरिक्त मुफ़्त VIP दिन मिलते हैं!</i>"
        )
    else:
        share_status_en = (
            "✅ <b>Claimed!</b> (+1 Extra Month VIP Active)"
            if share_reward_claimed else
            "⏳ <i>Share the shopping channel with 10 friends, then tap the claim button below!</i>"
        )

        msg = f"🎁 <b>Referrals & Free VIP Passes</b>\n\n"
        if has_ch:
            msg += (
                f"🌟 <b>Offer 1: Join {ch_info['flag']} {ch_info['name']}'s Shopping Deals Channel:</b>\n"
                f"• Channel: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n"
                f"• Status: <b>{ch_status}</b> {reward_note}\n"
                f"{claim_instruction_en}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌟 <b>Offer 2: Share Shopping Channel with 10 Friends (+1 Extra Month FREE):</b>\n"
                f"• Shopping Channel Link: <a href='{ch_info['channel_url']}'>{ch_info['channel_url']}</a>\n"
                f"• Status: {share_status_en}\n"
                f"👉 <i>Tap <b>'🛍️ Share {ch_info['name']} Shopping Channel'</b> below to share with 10 friends, then tap <b>'🎁 Claim +1 Mo Free VIP'</b> to activate!</i>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )

        msg += (
            f"👥 <b>Refer Friends to Bot:</b>\n"
            f"• Total Friends Referred: <b>{details['total_referred']}</b>\n"
            f"• Current Status: <b>{details.get('badge', 'Free Pass')}</b>"
        )
        if details['is_active'] and details.get('expires_at'):
            msg += f"\n• Valid Until: <b>{details['expires_at']}</b> ({details.get('days_left', 0)} days left)"
        msg += (
            f"\n\n🔗 <b>Your Bot Referral Link:</b>\n"
            f"<code>{ref_url}</code>\n\n"
            f"💡 <i>Earn extra VIP days whenever your friends join!</i>"
        )

    inline_kb = get_referral_inline_keyboard(
        ref_url,
        country_code=c_code,
        lang=lang,
        already_claimed=already_claimed,
        share_reward_claimed=share_reward_claimed
    )

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(msg, parse_mode="HTML", reply_markup=inline_kb, disable_web_page_preview=True)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", reply_markup=inline_kb, disable_web_page_preview=True)


async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows user's referral link, VIP status, country deals channel, and 1-month free VIP claim button."""
    await show_referral_screen(update, context, edit=False)


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    curr_code, curr_sym = get_user_currency(user_id)
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])

    expenses = get_today_expenses(user_id)
    total = get_today_total(user_id)

    if not expenses:
        text = get_msg('today_empty', lang=lang)
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    today_str = datetime.date.today().strftime("%d %B %Y")
    is_india = (country_info.get('country_code', '').upper() == 'IN')
    summary_text = format_today_summary(lang, expenses, total, curr_sym, today_str, is_india=is_india)

    action_btn_label = get_ui_str('manage_entries_btn', lang)
    today_actions = InlineKeyboardMarkup([
        [InlineKeyboardButton(action_btn_label, callback_data="manage_entries")]
    ])

    await update.message.reply_text(summary_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=today_actions)


async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    curr_code, curr_sym = get_user_currency(user_id)
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])

    now = datetime.datetime.now()
    month_name = now.strftime("%B %Y")

    breakdown = get_month_category_breakdown(user_id)
    total_exp = breakdown['total_expense']
    total_inc = breakdown['total_income']
    budget = get_user_budget(user_id)

    summary_text = format_month_summary(lang, month_name, total_exp, total_inc, budget, breakdown, curr_sym)
    await update.message.reply_text(summary_text, parse_mode="HTML", reply_markup=keyboard)


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    c_code = country_info.get('country_code', 'GLOBAL')
    curr_code, curr_sym = get_user_currency(user.id)
    keyboard = get_main_keyboard(lang, country_code=c_code)

    if context.args:
        raw_arg = context.args[0].strip()
        is_add = raw_arg.startswith("+")
        cleaned = raw_arg.replace("+", "").replace(",", "").replace(curr_sym, "").replace("₹", "").replace("$", "").strip()
        try:
            val = float(cleaned)
            if is_add:
                new_budget = add_to_budget(user.id, val, country_code=c_code)
                if lang == 'hi':
                    msg = f"✅ <b>बजट में राशि जोड़ी गई!</b>\n\n➕ जोड़ी गई राशि: <b>{curr_sym}{val:,.0f}</b>\n🎯 अब कुल नया बजट: <b>{curr_sym}{new_budget:,.0f}</b>"
                else:
                    msg = f"✅ <b>Budget Updated!</b>\n\n➕ Added: <b>{curr_sym}{val:,.0f}</b>\n🎯 Total Monthly Budget: <b>{curr_sym}{new_budget:,.0f}</b>"
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
                return
            else:
                set_budget(user.id, val, country_code=c_code)
                msg = get_msg('budget_set', lang=lang, val=val, currency=curr_sym)
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
                return
        except ValueError:
            pass

    current_budget = get_user_budget(user.id, country_code=c_code)
    if current_budget > 0:
        if lang == 'hi':
            prompt = (
                f"🎯 <b>मासिक बजट प्रबंधन (Monthly Budget):</b>\n\n"
                f"ℹ️ <i>वर्तमान बजट: <b>{curr_sym}{current_budget:,.0f}</b></i>\n\n"
                f"क्या आप मौजूदा बजट में और राशि जोड़ना चाहते हैं या नया बजट सेट करना चाहते हैं?"
            )
        elif lang == 'ru':
            prompt = (
                f"🎯 <b>Управление бюджетом:</b>\n\n"
                f"ℹ️ <i>Текущий бюджет: <b>{curr_sym}{current_budget:,.0f}</b></i>\n\n"
                f"Хотите добавить сумму к текущему бюджету или установить новый?"
            )
        else:
            prompt = (
                f"🎯 <b>Monthly Budget Management:</b>\n\n"
                f"ℹ️ <i>Current Budget: <b>{curr_sym}{current_budget:,.0f}</b></i>\n\n"
                f"Would you like to add more amount to this budget, or set a new budget?"
            )
        inline_kb = get_budget_prompt_keyboard(lang, current_budget, curr_sym)
        await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=inline_kb)
    else:
        prompt = get_msg('budget_prompt', lang=lang, currency=curr_sym)
        context.user_data['awaiting_budget'] = True
        await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=keyboard)


# ==========================================
# CLIENT KHATA & LEN-DEN (RECEIVABLE/PAYABLE)
# ==========================================

def parse_amount_and_note(text: str) -> Tuple[float, str]:
    """Extracts positive numerical amount and optional note from freeform text."""
    text = text.strip()
    cleaned = re.sub(r'^[₹$€£¥\s]+', '', text)
    m = re.match(r'^([\d,]+(?:\.\d+)?)\s*(.*)$', cleaned)
    if m:
        num_str = m.group(1).replace(',', '')
        try:
            amt = float(num_str)
            note = m.group(2).strip()
            return amt, note
        except ValueError:
            pass
    return 0.0, ""


async def show_client_home(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """Renders main overview of Client Khata."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    c_code = country_info.get('country_code', 'GLOBAL')
    curr_code, curr_sym = get_user_currency(user_id)

    summary = get_clients_overall_summary(user_id, country_code=c_code)
    tot_lena = summary['total_lena']
    tot_dena = summary['total_dena']
    net_bal = summary['net_balance']
    client_cnt = summary['total_clients']

    if lang == 'hi':
        title = "👥 <b>Client (ग्राहक & लेन-देन)</b>"
        sub = f"देश/खाता: <b>{country_info.get('country_name', 'India')}</b>"
        lena_str = f"🟢 कुल लेना है (You'll Get): <b>{curr_sym}{tot_lena:,.2f}</b>"
        dena_str = f"🔴 कुल देना है (You'll Give): <b>{curr_sym}{tot_dena:,.2f}</b>"
        if net_bal > 0:
            net_str = f"⚖️ नेट स्थिति: <b>🟢 +{curr_sym}{net_bal:,.2f} (लेना बाकी है)</b>"
        elif net_bal < 0:
            net_str = f"⚖️ नेट स्थिति: <b>🔴 -{curr_sym}{abs(net_bal):,.2f} (देना बाकी है)</b>"
        else:
            net_str = f"⚖️ नेट स्थिति: <b>⚪ हिसाब बराबर (Settled)</b>"
        cnt_str = f"👤 कुल सक्रिय ग्राहक: <b>{client_cnt}</b>"
        hint = "नीचे दिए गए बटनों से नया ग्राहक जोड़ें, सूची देखें या रिपोर्ट देखें:"
    elif lang == 'bn':
        title = "👥 <b>Client (গ্রাহক খাতা)</b>"
        sub = f"দেশ: <b>{country_info.get('country_name', 'Global')}</b>"
        lena_str = f"🟢 মোট পাওনা (You'll Get): <b>{curr_sym}{tot_lena:,.2f}</b>"
        dena_str = f"🔴 মোট দেনা (You'll Give): <b>{curr_sym}{tot_dena:,.2f}</b>"
        if net_bal > 0:
            net_str = f"⚖️ নেট ব্যালেন্স: <b>🟢 +{curr_sym}{net_bal:,.2f}</b>"
        elif net_bal < 0:
            net_str = f"⚖️ নেট ব্যালেন্স: <b>🔴 -{curr_sym}{abs(net_bal):,.2f}</b>"
        else:
            net_str = f"⚖️ নেট ব্যালেন্স: <b>⚪ ০ (হিসাব সমান)</b>"
        cnt_str = f"👤 মোট গ্রাহক: <b>{client_cnt}</b>"
        hint = "নিচের বোতাম থেকে পরিচালনা করুন:"
    else:
        title = "👥 <b>Client Accounts (Receivable/Payable)</b>"
        sub = f"Country Ledger: <b>{country_info.get('country_name', 'Global')}</b>"
        lena_str = f"🟢 Total You'll Get (Receivable): <b>{curr_sym}{tot_lena:,.2f}</b>"
        dena_str = f"🔴 Total You'll Give (Payable): <b>{curr_sym}{tot_dena:,.2f}</b>"
        if net_bal > 0:
            net_str = f"⚖️ Net Position: <b>🟢 +{curr_sym}{net_bal:,.2f} (Net Receivable)</b>"
        elif net_bal < 0:
            net_str = f"⚖️ Net Position: <b>🔴 -{curr_sym}{abs(net_bal):,.2f} (Net Payable)</b>"
        else:
            net_str = f"⚖️ Net Position: <b>⚪ Settled ({curr_sym}0.00)</b>"
        cnt_str = f"👤 Total Active Clients: <b>{client_cnt}</b>"
        hint = "Select an option below to manage clients or download reports:"

    text = f"{title}\n{sub}\n\n{lena_str}\n{dena_str}\n{net_str}\n{cnt_str}\n\n<i>{hint}</i>"
    kb = get_clients_main_keyboard(lang)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


async def show_client_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int, edit: bool = False):
    """Renders profile and financial ledger status of an individual client."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    curr_code, curr_sym = get_user_currency(user_id)

    client = get_client_details_with_balance(client_id, user_id)
    if not client:
        err = "❌ Client not found." if lang == 'en' else "❌ ग्राहक नहीं मिला।"
        if edit and update.callback_query:
            await update.callback_query.answer(err, show_alert=True)
            return
        chat_id = update.effective_chat.id if update.effective_chat else user_id
        await context.bot.send_message(chat_id=chat_id, text=err)
        return

    name = client['name']
    phone = client['phone'] or ("Not set ✏️" if lang == 'en' else "दर्ज नहीं है ✏️")
    email = client['email'] or ("Not set ✏️" if lang == 'en' else "दर्ज नहीं है ✏️")
    lena = client['total_lena']
    dena = client['total_dena']
    bal = client['balance']

    total_tx_count = client.get('tx_count', 0)

    if lang == 'hi':
        header = f"👤 <b>ग्राहक विवरण: {name}</b>"
        info = f"📞 फोन: <b>{phone}</b>\n✉️ ईमेल: <b>{email}</b>"
        fin = (
            f"📊 <b>खाता सारांश (Account Summary):</b>\n"
            f"• 🔴 कुल DEBIT (दिया / You Gave): <b>{curr_sym}{lena:,.2f}</b>\n"
            f"• 🟢 कुल CREDIT (मिला / Received): <b>{curr_sym}{dena:,.2f}</b>"
        )
        if bal > 0:
            status = f"⚖️ <b>कुल बाकी (Net Due): 🟢 {curr_sym}{bal:,.2f}</b>\n👉 <i>आपको यह राशि ग्राहक से लेनी है (Client owes you)</i>"
        elif bal < 0:
            status = f"⚖️ <b>कुल बाकी (Net Due): 🔴 {curr_sym}{abs(bal):,.2f}</b>\n👉 <i>आपको यह राशि ग्राहक को देनी है (You owe client)</i>"
        else:
            status = f"⚖️ <b>कुल बाकी (Net Due): ⚪ {curr_sym}0.00 (हिसाब चुकता / Settled)</b>"

        tx_title = f"📜 <b>लेन-देन इतिहास (Transactions & Due Ledger - {total_tx_count}):</b>"
    else:
        header = f"👤 <b>Client Profile: {name}</b>"
        info = f"📞 Phone: <b>{phone}</b>\n✉️ Email: <b>{email}</b>"
        fin = (
            f"📊 <b>Account Summary:</b>\n"
            f"• 🔴 Total DEBIT (You Gave): <b>{curr_sym}{lena:,.2f}</b>\n"
            f"• 🟢 Total CREDIT (Received): <b>{curr_sym}{dena:,.2f}</b>"
        )
        if bal > 0:
            status = f"⚖️ <b>Net Due: 🟢 {curr_sym}{bal:,.2f}</b>\n👉 <i>Client owes you this amount (Receivable)</i>"
        elif bal < 0:
            status = f"⚖️ <b>Net Due: 🔴 {curr_sym}{abs(bal):,.2f}</b>\n👉 <i>You owe client this amount (Payable)</i>"
        else:
            status = f"⚖️ <b>Net Due: ⚪ {curr_sym}0.00 (Fully Settled)</b>"

        tx_title = f"📜 <b>Transactions & Due Ledger ({total_tx_count}):</b>"

    txs = get_client_transactions_with_running_balance(client_id, user_id, limit=6)
    tx_lines = []
    if txs:
        for idx, t in enumerate(txs, 1):
            amt = t['amount']
            r_bal = t.get('running_balance', 0.0)
            note = t['note']
            note_str = f"\n   📝 <i>{note}</i>" if note else ""

            # Format Date and Time
            created_at_raw = t.get('created_at') or t.get('date') or ''
            try:
                dt_obj = datetime.datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S")
                dt_str = dt_obj.strftime("%d-%m-%Y ⏰ %I:%M %p")
            except Exception:
                try:
                    dt_obj = datetime.datetime.strptime(created_at_raw.split()[0], "%Y-%m-%d")
                    dt_str = dt_obj.strftime("%d-%m-%Y")
                except Exception:
                    dt_str = created_at_raw

            if t['type'] == 'lena':
                type_label = "🔴 DEBIT (दिया / You Gave)" if lang == 'hi' else "🔴 DEBIT (You Gave)"
            else:
                type_label = "🟢 CREDIT (मिला / Received)" if lang == 'hi' else "🟢 CREDIT (Payment Received)"

            if r_bal > 0:
                due_label = f"🟢 {curr_sym}{r_bal:,.2f} लेना बाकी" if lang == 'hi' else f"🟢 {curr_sym}{r_bal:,.2f} Due"
            elif r_bal < 0:
                due_label = f"🔴 {curr_sym}{abs(r_bal):,.2f} देना बाकी" if lang == 'hi' else f"🔴 {curr_sym}{abs(r_bal):,.2f} Advance"
            else:
                due_label = f"⚪ {curr_sym}0.00 चुकता" if lang == 'hi' else f"⚪ {curr_sym}0.00 Settled"

            tx_lines.append(
                f"<b>{idx}. {type_label}: {curr_sym}{amt:,.2f}</b>\n"
                f"   📅 {dt_str}{note_str}\n"
                f"   ⚖️ उस समय बाकी (Due): <b>{due_label}</b>"
            )
        if total_tx_count > 6:
            more_hint = f"\n<i>... और {total_tx_count - 6} पुराने लेन-देन देखने के लिए '📜 पूरा लेजर' दबाएं।</i>" if lang == 'hi' else f"\n<i>... tap '📜 Full Ledger' to view all {total_tx_count} transactions.</i>"
            tx_lines.append(more_hint)
    else:
        tx_lines.append("<i>" + ("कोई लेन-देन दर्ज नहीं है।" if lang == 'hi' else "No transactions recorded yet.") + "</i>")

    tx_block = "\n\n".join(tx_lines)
    text = f"{header}\n\n{info}\n\n{fin}\n\n{status}\n\n{tx_title}\n\n{tx_block}"
    kb = get_client_detail_keyboard(client_id, lang)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


async def show_client_list(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, edit: bool = False):
    """Renders paginated list of all active clients with net balances."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    c_code = country_info.get('country_code', 'GLOBAL')
    curr_code, curr_sym = get_user_currency(user_id)

    clients = get_all_clients(user_id, country_code=c_code)
    if not clients:
        no_cl = (
            "📋 <b>Client (ग्राहक सूची):</b>\n\n"
            "अभी तक कोई ग्राहक नहीं जोड़ा गया है।\n"
            "नया ग्राहक जोड़ने के लिए नीचे दिए गए बटन पर टैप करें! 👇"
        ) if lang == 'hi' else (
            "📋 <b>Client List:</b>\n\n"
            "No clients added yet.\n"
            "Tap below to add your first client! 👇"
        )
        add_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ " + ("नया ग्राहक जोड़ें" if lang == 'hi' else "Add Client"), callback_data="client_action_add")],
            [InlineKeyboardButton("🔙 Client", callback_data="client_action_home")]
        ])
        if edit and update.callback_query:
            try:
                await update.callback_query.edit_message_text(no_cl, parse_mode="HTML", reply_markup=add_kb)
                return
            except Exception:
                pass
        chat_id = update.effective_chat.id if update.effective_chat else user_id
        await context.bot.send_message(chat_id=chat_id, text=no_cl, parse_mode="HTML", reply_markup=add_kb)
        return

    title = (
        f"📋 <b>सभी ग्राहक (All Clients - {country_info.get('country_name', 'Global')}):</b>\n"
        f"<i>ग्राहक का पूरा विवरण देखने या लेन-देन जोड़ने के लिए उसके नाम पर टैप करें:</i>"
    ) if lang == 'hi' else (
        f"📋 <b>All Clients ({country_info.get('country_name', 'Global')}):</b>\n"
        f"<i>Tap any client name to view profile or record payment/dues:</i>"
    )

    kb = get_client_list_keyboard(clients, page=page, per_page=5, lang=lang, curr_sym=curr_sym)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(title, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=title, parse_mode="HTML", reply_markup=kb)


async def show_client_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """Renders comprehensive accounts receivable/payable summary report."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    c_code = country_info.get('country_code', 'GLOBAL')
    curr_code, curr_sym = get_user_currency(user_id)

    summary = get_clients_overall_summary(user_id, country_code=c_code)
    tot_lena = summary['total_lena']
    tot_dena = summary['total_dena']
    net_bal = summary['net_balance']
    cnt = summary['total_clients']
    top_debtors = summary['top_debtors']
    top_creditors = summary['top_creditors']

    if lang == 'hi':
        lines = [
            f"📊 <b>Client सारांश रिपोर्ट (Summary Report)</b>",
            f"क्षेत्र/देश: <b>{country_info.get('country_name', 'India')}</b>\n",
            f"• कुल सक्रिय ग्राहक: <b>{cnt}</b>",
            f"• 🟢 कुल लेना है (Receivable): <b>{curr_sym}{tot_lena:,.2f}</b>",
            f"• 🔴 कुल देना है (Payable): <b>{curr_sym}{tot_dena:,.2f}</b>"
        ]
        if net_bal > 0:
            lines.append(f"• ⚖️ शुद्ध बकाया स्थिति: <b>🟢 +{curr_sym}{net_bal:,.2f} (लेना बाकी)</b>")
        elif net_bal < 0:
            lines.append(f"• ⚖️ शुद्ध देनदारी स्थिति: <b>🔴 -{curr_sym}{abs(net_bal):,.2f} (देना बाकी)</b>")
        else:
            lines.append(f"• ⚖️ शुद्ध स्थिति: <b>⚪ सब बराबर ({curr_sym}0.00)</b>")

        lines.append("\n<b>🔝 शीर्ष देनदार (जिनसे सबसे ज्यादा लेना है):</b>")
        if top_debtors:
            for i, d in enumerate(top_debtors, 1):
                lines.append(f"{i}. {d['name']} — 🟢 <b>+{curr_sym}{d['balance']:,.2f}</b>")
        else:
            lines.append("<i>कोई देनदार नहीं (No pending receivables)</i>")

        lines.append("\n<b>🔻 शीर्ष लेनदार (जिनको सबसे ज्यादा देना है):</b>")
        if top_creditors:
            for i, c in enumerate(top_creditors, 1):
                lines.append(f"{i}. {c['name']} — 🔴 <b>-{curr_sym}{abs(c['balance']):,.2f}</b>")
        else:
            lines.append("<i>कोई लेनदार नहीं (No pending payables)</i>")

        back_label = "🔙 Client"
    else:
        lines = [
            f"📊 <b>Client Summary Report</b>",
            f"Ledger: <b>{country_info.get('country_name', 'Global')}</b>\n",
            f"• Total Active Clients: <b>{cnt}</b>",
            f"• 🟢 Total You'll Get (Receivable): <b>{curr_sym}{tot_lena:,.2f}</b>",
            f"• 🔴 Total You'll Give (Payable): <b>{curr_sym}{tot_dena:,.2f}</b>"
        ]
        if net_bal > 0:
            lines.append(f"• ⚖️ Net Position: <b>🟢 +{curr_sym}{net_bal:,.2f} (Net Receivable)</b>")
        elif net_bal < 0:
            lines.append(f"• ⚖️ Net Position: <b>🔴 -{curr_sym}{abs(net_bal):,.2f} (Net Payable)</b>")
        else:
            lines.append(f"• ⚖️ Net Position: <b>⚪ Settled ({curr_sym}0.00)</b>")

        lines.append("\n<b>🔝 Top Debtors (Highest to Receive):</b>")
        if top_debtors:
            for i, d in enumerate(top_debtors, 1):
                lines.append(f"{i}. {d['name']} — 🟢 <b>+{curr_sym}{d['balance']:,.2f}</b>")
        else:
            lines.append("<i>None</i>")

        lines.append("\n<b>🔻 Top Creditors (Highest to Pay):</b>")
        if top_creditors:
            for i, c in enumerate(top_creditors, 1):
                lines.append(f"{i}. {c['name']} — 🔴 <b>-{curr_sym}{abs(c['balance']):,.2f}</b>")
        else:
            lines.append("<i>None</i>")

        back_label = "🔙 Client"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ " + ("नया ग्राहक जोड़ें" if lang == 'hi' else "Add Client"), callback_data="client_action_add")],
        [InlineKeyboardButton("📋 " + ("सभी ग्राहक देखें" if lang == 'hi' else "View All Clients"), callback_data="client_action_list_1")],
        [InlineKeyboardButton(back_label, callback_data="client_action_home")]
    ])

    text = "\n".join(lines)
    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


async def show_client_ledger(update: Update, context: ContextTypes.DEFAULT_TYPE, client_id: int):
    """Renders full historical transaction ledger for a client with exact dates, times, debit/credit and running dues."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    curr_code, curr_sym = get_user_currency(user_id)

    client = get_client_details_with_balance(client_id, user_id)
    if not client:
        return

    txs = get_client_transactions_with_running_balance(client_id, user_id, limit=25)
    title = f"📜 <b>{client['name']} - " + ("विस्तृत खाता लेजर (Full Ledger)" if lang == 'hi' else "Detailed Transaction Ledger") + "</b>\n"
    lines = [title]

    if not txs:
        lines.append("<i>" + ("कोई लेन-देन दर्ज नहीं है।" if lang == 'hi' else "No transactions recorded.") + "</i>")
    else:
        for idx, t in enumerate(txs, 1):
            amt = t['amount']
            r_bal = t.get('running_balance', 0.0)
            note = t['note']
            note_str = f" - <i>{note}</i>" if note else ""

            created_at_raw = t.get('created_at') or t.get('date') or ''
            try:
                dt_obj = datetime.datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S")
                dt_str = dt_obj.strftime("%d-%m-%Y ⏰ %I:%M %p")
            except Exception:
                try:
                    dt_obj = datetime.datetime.strptime(created_at_raw.split()[0], "%Y-%m-%d")
                    dt_str = dt_obj.strftime("%d-%m-%Y")
                except Exception:
                    dt_str = created_at_raw

            if t['type'] == 'lena':
                tag = "🔴 DEBIT (दिया)" if lang == 'hi' else "🔴 DEBIT (Gave)"
            else:
                tag = "🟢 CREDIT (मिला)" if lang == 'hi' else "🟢 CREDIT (Recv)"

            if r_bal > 0:
                bal_tag = f"🟢 {curr_sym}{r_bal:,.2f} लेना" if lang == 'hi' else f"🟢 {curr_sym}{r_bal:,.2f} Due"
            elif r_bal < 0:
                bal_tag = f"🔴 {curr_sym}{abs(r_bal):,.2f} देना" if lang == 'hi' else f"🔴 {curr_sym}{abs(r_bal):,.2f} Adv"
            else:
                bal_tag = "⚪ 0.00"

            lines.append(f"{idx}. {tag} <b>{curr_sym}{amt:,.2f}</b> [📅 {dt_str}]{note_str}\n   └ ⚖️ उस समय बाकी: <b>{bal_tag}</b>")

    bal = client['balance']
    lena = client['total_lena']
    dena = client['total_dena']
    lines.append(
        f"\n📊 <b>" + ("कुल दिया (DEBIT):" if lang == 'hi' else "Total DEBIT:") + f" {curr_sym}{lena:,.2f} | " +
        ("कुल मिला (CREDIT):" if lang == 'hi' else "Total CREDIT:") + f" {curr_sym}{dena:,.2f}</b>"
    )
    if bal > 0:
        lines.append(f"⚖️ <b>" + ("वर्तमान में कुल लेना बाकी: " if lang == 'hi' else "Net Due (Receivable): ") + f"🟢 {curr_sym}{bal:,.2f}</b>")
    elif bal < 0:
        lines.append(f"⚖️ <b>" + ("वर्तमान में कुल देना बाकी: " if lang == 'hi' else "Net Due (Payable): ") + f"🔴 {curr_sym}{abs(bal):,.2f}</b>")
    else:
        lines.append(f"⚖️ <b>" + ("हिसाब चुकता" if lang == 'hi' else "Fully Settled") + f" (⚪ {curr_sym}0.00)</b>")

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 + लेना (Get)", callback_data=f"client_tx_get_{client_id}"),
            InlineKeyboardButton("🔴 - देना (Give)", callback_data=f"client_tx_give_{client_id}")
        ],
        [InlineKeyboardButton("🔙 " + ("ग्राहक प्रोफ़ाइल" if lang == 'hi' else "Back to Profile"), callback_data=f"client_view_{client_id}")],
        [InlineKeyboardButton("🔙 Client", callback_data="client_action_home")]
    ])

    text = "\n".join(lines)
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for /clients, /client, /khata, /udhar or Clients button."""
    await show_client_home(update, context, edit=False)

async def show_text_saver_home(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, edit: bool = False):
    """Renders interactive Text Saver / Shopping List home overview."""
    user = update.effective_user
    user_id = user.id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)
    c_code = country_info.get('country_code', 'GLOBAL')

    items = get_text_saver_items(user_id, country_code=c_code)
    pending_items = [i for i in items if not i.get('is_done')]
    done_items = [i for i in items if i.get('is_done')]

    if lang == 'hi':
        title = "📝 <b>Text Saver (सामान & नोट्स लिस्ट)</b>"
        sub = f"देश/क्षेत्र: <b>{country_info.get('country_name', 'India')}</b>"
        empty_text = (
            f"{title}\n{sub}\n\n"
            f"🛒 <i>अभी आपकी लिस्ट खाली है!</i>\n\n"
            f"बाजार या दुकान से कोई भी सामान लाना हो, उसका नाम याद रखने के लिए नीचे <b>'➕ नया सामान जोड़ें'</b> पर टैप करें।\n\n"
            f"💡 <i>आप एक साथ कितने भी सामान लिख सकते हैं!</i>"
        )
    elif lang == 'bn':
        title = "📝 <b>Text Saver (কেনাকাটার তালিকা)</b>"
        sub = f"দেশ: <b>{country_info.get('country_name', 'Global')}</b>"
        empty_text = (
            f"{title}\n{sub}\n\n"
            f"🛒 <i>আপনার তালিকা বর্তমানে খালি!</i>\n\n"
            f"যেকোনো প্রয়োজনীয় জিনিস লিখে রাখতে নিচে <b>'➕ নতুন জিনিস যোগ করুন'</b> চাপুন।"
        )
    else:
        title = "📝 <b>Text Saver & Shopping List</b>"
        sub = f"Region: <b>{country_info.get('country_name', 'Global')}</b>"
        empty_text = (
            f"{title}\n{sub}\n\n"
            f"🛒 <i>Your list is currently empty!</i>\n\n"
            f"Save any items you need to bring or buy by tapping <b>'➕ Add Items'</b> below.\n\n"
            f"💡 <i>You can add as many items as you want!</i>"
        )

    if not items:
        text = empty_text
    else:
        lines = [title, sub, ""]
        if pending_items:
            p_hdr = f"🛒 <b>लाने बाकी सामान (Pending - {len(pending_items)}):</b>" if lang == 'hi' else f"🛒 <b>Items To Bring ({len(pending_items)}):</b>"
            lines.append(p_hdr)
            for idx, p in enumerate(pending_items, 1):
                lines.append(f"{idx}. ⬜ <code>{p['text']}</code>")
            lines.append("")

        if done_items:
            d_hdr = f"✅ <b>ला चुके सामान (Purchased/Done - {len(done_items)}):</b>" if lang == 'hi' else f"✅ <b>Completed ({len(done_items)}):</b>"
            lines.append(d_hdr)
            for d in done_items:
                lines.append(f"• <s><code>{d['text']}</code></s>")
            lines.append("")

        hint = (
            "💡 <i>सामान के नाम या '📋 Copy' पर टैप करके तुरंत कॉपी (1-Click Copy) करें।\nखरीदने के बाद नीचे चेकबॉक्स बटन से टिक (✅) लगाएं।</i>"
        ) if lang == 'hi' else (
            "💡 <i>Tap any item name or '📋 Copy' to copy to clipboard instantly (1-Click Copy).\nTap the checkbox button to mark as done (✅).</i>"
        )
        lines.append(hint)
        text = "\n".join(lines)

    kb = get_text_saver_keyboard(items, page=page, per_page=6, lang=lang)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
            return
        except Exception:
            pass

    chat_id = update.effective_chat.id if update.effective_chat else user_id
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=kb)


async def text_saver_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for /text_saver, /textsaver, /saver, /notes, /list, /saman or Text Saver button."""
    await show_text_saver_home(update, context, page=1, edit=False)



async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Allows user to undo/delete any specific entry.
    Supports:
    - /delete 12 or /undo 12 (deletes entry #12 directly)
    - /delete or /undo without args (opens interactive entry selector)
    """
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    curr_code, curr_sym = get_user_currency(user.id)
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])

    if context.args:
        try:
            tx_id = int(context.args[0].replace("#", ""))
            deleted = delete_expense_by_id(user.id, tx_id)
            if deleted:
                today_tot = get_today_total(user.id)
                msg = get_msg('undo_success', lang=lang, amount=deleted['amount'], category=deleted['category'], today_total=today_tot, currency=curr_sym)
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
                return
            else:
                not_found = (
                    f"❌ Entry #{tx_id} not found or already deleted."
                ) if lang == 'en' else (
                    f"❌ एंट्री #{tx_id} नहीं मिली या पहले ही डिलीट हो चुकी है।"
                )
                await update.message.reply_text(not_found, reply_markup=keyboard)
                return
        except ValueError:
            pass

    entries = get_recent_expenses(user.id, limit=8)
    if not entries:
        msg = get_msg('undo_empty', lang=lang)
        await update.message.reply_text(msg, reply_markup=keyboard)
        return

    prompt = get_msg('manage_entries_title', lang=lang)
    inline_kb = get_entries_management_keyboard(entries, lang, currency=curr_sym)
    await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=inline_kb)


async def statement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Prompt user to choose Date Range (Period)."""
    user = update.effective_user
    lang = get_user_language(user.id)

    prompt = get_msg('period_prompt', lang=lang)
    inline_kb = get_period_select_keyboard(lang)
    await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=inline_kb)


async def excel_quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /excel command: checks VIP pass or generates Stars invoice."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    start_date, end_date, label = get_preset_date_range("this_month")

    is_ch, _ = await check_user_channel_membership(context.bot, user.id, country_info['country_code'])
    tier_info = get_user_access_tier(user.id, is_channel_member=is_ch)

    if tier_info['is_active']:
        conf_msg = get_msg('vip_download_msg', lang=lang, period_label=label)
        await update.message.reply_text(conf_msg, parse_mode="HTML")
        await deliver_statement_files(context, update.effective_chat.id, user, "excel", start_date, end_date, label, lang)
    elif tier_info.get("requires_channel"):
        ch_info = get_country_channel_info(country_info['country_code'])
        pause_msg = get_msg(
            'month_2_paused_msg',
            lang=lang,
            country=country_info['country_name'],
            channel_title=ch_info['title'],
            channel_username=ch_info['channel_username']
        )
        kb = get_channel_join_keyboard(country_info['country_code'], lang=lang)
        await update.message.reply_text(pause_msg, parse_mode="HTML", reply_markup=kb)
    else:
        await create_and_send_invoice(context, user, update.effective_chat.id, "excel", start_date, end_date, label, lang)


async def pdf_quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct /pdf command: checks VIP pass or generates Stars invoice."""
    user = update.effective_user
    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    start_date, end_date, label = get_preset_date_range("this_month")

    is_ch, _ = await check_user_channel_membership(context.bot, user.id, country_info['country_code'])
    tier_info = get_user_access_tier(user.id, is_channel_member=is_ch)

    if tier_info['is_active']:
        conf_msg = get_msg('vip_download_msg', lang=lang, period_label=label)
        await update.message.reply_text(conf_msg, parse_mode="HTML")
        await deliver_statement_files(context, update.effective_chat.id, user, "pdf", start_date, end_date, label, lang)
    elif tier_info.get("requires_channel"):
        ch_info = get_country_channel_info(country_info['country_code'])
        pause_msg = get_msg(
            'month_2_paused_msg',
            lang=lang,
            country=country_info['country_name'],
            channel_title=ch_info['title'],
            channel_username=ch_info['channel_username']
        )
        kb = get_channel_join_keyboard(country_info['country_code'], lang=lang)
        await update.message.reply_text(pause_msg, parse_mode="HTML", reply_markup=kb)
    else:
        await create_and_send_invoice(context, user, update.effective_chat.id, "pdf", start_date, end_date, label, lang)


# ==========================================
# TELEGRAM STARS & FILE DELIVERY HANDLERS
# ==========================================

async def create_and_send_invoice(context: ContextTypes.DEFAULT_TYPE, user, chat_id: int, fmt: str, start_date: str, end_date: str, period_label: str, lang: str):
    if fmt == "pdf":
        title = f"📄 PDF Statement ({period_label})" if lang == 'en' else f"📄 PDF स्टेटमेंट ({period_label})"
        price_stars = STARS_PDF_PRICE
        desc = (
            f"Official verified PDF statement for {period_label}. Instant download."
        ) if lang == 'en' else (
            f"{period_label} के लिए ऑफिशियल PDF स्टेटमेंट। तुरंत डाउनलोड करें।"
        )
    elif fmt == "excel":
        title = f"📊 Excel Sheet (.xlsx) ({period_label})" if lang == 'en' else f"📊 Excel फाइल (.xlsx) ({period_label})"
        price_stars = STARS_EXCEL_PRICE
        desc = (
            f"Complete editable Excel spreadsheet (.xlsx) with formulas for {period_label}."
        ) if lang == 'en' else (
            f"{period_label} के लिए संपूर्ण Excel स्प्रेडशीट (.xlsx) फॉर्मूलों सहित।"
        )
    else:  # both
        title = f"📦 Combo (PDF + Excel) ({period_label})" if lang == 'en' else f"📦 कॉम्बो (PDF + Excel) ({period_label})"
        price_stars = STARS_BUNDLE_PRICE
        desc = (
            f"Value pack: Both PDF statement and Excel (.xlsx) spreadsheet for {period_label}."
        ) if lang == 'en' else (
            f"वैल्यू पैक: {period_label} के लिए PDF और Excel (.xlsx) दोनों फाइलें।"
        )

    payload = f"stmt_{fmt}_{user.id}_{start_date}_{end_date}"
    currency = "XTR"  # Official Telegram Stars currency
    prices = [LabeledPrice(title, price_stars)]

    try:
        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=desc,
            payload=payload,
            currency=currency,
            prices=prices,
            provider_token=""  # MUST be empty for Telegram Stars
        )
    except Exception as e:
        logger.error(f"Error sending Stars invoice ({fmt}): {e}")
        # Fallback if client is in test mode or doesn't support stars: generate and send directly
        await deliver_statement_files(context, chat_id, user, fmt, start_date, end_date, period_label, lang)


async def deliver_statement_files(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user, fmt: str, start_date: str, end_date: str, period_label: str, lang: str):
    """Generates and delivers PDF, Excel, or both files with zero promotions in user's language."""
    user_name = user.first_name or "User"
    country_info = get_user_country(user.id)
    c_code = country_info.get("country_code", "GLOBAL")
    c_name = country_info.get("country_name", "Worldwide")
    curr = country_info.get("currency_symbol", "$")
    doc_title = get_statement_str('doc_title', lang)

    if fmt in ("pdf", "both"):
        try:
            pdf_path = generate_statement_pdf(
                user.id, user_name, start_date, end_date, period_label,
                lang=lang, country_code=c_code
            )
            with open(pdf_path, "rb") as pf:
                caption = (
                    f"📄 <b>{doc_title}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"• {get_statement_str('lbl_account_holder', lang)}: <b>{user_name}</b>\n"
                    f"• {get_statement_str('lbl_period', lang)}: <b>{period_label}</b>\n"
                    f"• {get_statement_str('lbl_jurisdiction', lang)}: <b>{c_name} ({curr})</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🔒 <i>{get_statement_str('footer_notice', lang)}</i>"
                )
                await context.bot.send_document(chat_id=chat_id, document=pf, caption=caption, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")

    if fmt in ("excel", "both"):
        try:
            excel_path = generate_statement_excel(
                user.id, user_name, start_date, end_date, period_label,
                lang=lang, country_code=c_code
            )
            sheet_title = get_statement_str('sheet_ledger', lang)
            with open(excel_path, "rb") as ef:
                caption = (
                    f"📊 <b>{doc_title} (.xlsx)</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"• {get_statement_str('lbl_account_holder', lang)}: <b>{user_name}</b>\n"
                    f"• {get_statement_str('lbl_period', lang)}: <b>{period_label}</b>\n"
                    f"• {get_statement_str('lbl_jurisdiction', lang)}: <b>{c_name} ({curr})</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📋 <i>{sheet_title}</i>"
                )
                await context.bot.send_document(chat_id=chat_id, document=ef, caption=caption, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error generating Excel: {e}")


async def deliver_client_report_files(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user,
    fmt: str,
    target,  # None, 'all', or client_id (int or 'c5')
    months: int = 1,
    start_date: str = None,
    end_date: str = None,
    period_label: str = None,
    lang: str = 'en'
):
    """Generates and delivers professional corporate PDF/Excel Client Statement reports (up to 12 months)."""
    user_name = user.first_name or "User"
    country_info = get_user_country(user.id)
    c_code = country_info.get("country_code", "GLOBAL")
    c_name = country_info.get("country_name", "Worldwide")
    curr = country_info.get("currency_symbol", "$")

    client_id = None
    client_name = None
    if target and target != 'all':
        if isinstance(target, str) and target.startswith('c'):
            client_id = int(target.replace('c', ''))
        else:
            client_id = int(target)
        c_info = get_client(client_id, user.id)
        client_name = c_info['name'] if c_info else "Client"

    if not start_date or not end_date:
        start_date, end_date, auto_label, num_months = get_client_report_date_range(months)
        if not period_label:
            period_label = auto_label

    doc_title = get_client_statement_str('doc_title_single' if client_id else 'doc_title_all', lang)
    if client_id:
        scope_str = client_name
    else:
        scope_str = get_client_statement_str('lbl_all_clients', lang)

    if fmt in ("pdf", "both"):
        try:
            pdf_path = generate_client_report_pdf(
                user_id=user.id,
                first_name=user_name,
                client_id=client_id,
                months=months,
                start_date=start_date,
                end_date=end_date,
                period_label=period_label,
                lang=lang,
                country_code=c_code
            )
            with open(pdf_path, "rb") as pf:
                caption = (
                    f"📄 <b>{doc_title}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"• {get_client_statement_str('lbl_account_holder', lang)}: <b>{user_name}</b>\n"
                    f"• {get_client_statement_str('lbl_scope', lang)}: <b>{scope_str}</b>\n"
                    f"• {get_client_statement_str('lbl_period', lang)}: <b>{period_label}</b>\n"
                    f"• {get_client_statement_str('lbl_jurisdiction', lang)}: <b>{c_name} ({curr})</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🔒 <i>{get_client_statement_str('footer_notice', lang)}</i>"
                )
                await context.bot.send_document(chat_id=chat_id, document=pf, caption=caption, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error generating Client PDF: {e}", exc_info=True)
            err_msg = "❌ Error generating PDF statement." if lang == 'en' else "❌ PDF रिपोर्ट बनाने में त्रुटि हुई।"
            await context.bot.send_message(chat_id=chat_id, text=err_msg)

    if fmt in ("excel", "both"):
        try:
            excel_path = generate_client_report_excel(
                user_id=user.id,
                first_name=user_name,
                client_id=client_id,
                months=months,
                start_date=start_date,
                end_date=end_date,
                period_label=period_label,
                lang=lang,
                country_code=c_code
            )
            sheet_title = get_client_statement_str('sheet_ledger', lang)
            with open(excel_path, "rb") as ef:
                caption = (
                    f"📊 <b>{doc_title} (.xlsx)</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"• {get_client_statement_str('lbl_account_holder', lang)}: <b>{user_name}</b>\n"
                    f"• {get_client_statement_str('lbl_scope', lang)}: <b>{scope_str}</b>\n"
                    f"• {get_client_statement_str('lbl_period', lang)}: <b>{period_label}</b>\n"
                    f"• {get_client_statement_str('lbl_jurisdiction', lang)}: <b>{c_name} ({curr})</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📋 <i>{sheet_title}</i>"
                )
                await context.bot.send_document(chat_id=chat_id, document=ef, caption=caption, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error generating Client Excel: {e}", exc_info=True)
            err_msg = "❌ Error generating Excel statement." if lang == 'en' else "❌ Excel रिपोर्ट बनाने में त्रुटि हुई।"
            await context.bot.send_message(chat_id=chat_id, text=err_msg)


async def client_pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Directly triggers period selector for Client PDF Report."""
    user = update.effective_user
    lang = get_user_language(user.id)
    kb = get_client_report_period_keyboard(fmt="pdf", target="all", lang=lang)
    prompt = (
        "📄 <b>Client PDF रिपोर्ट (अधिकतम 12 महीने):</b>\n\n"
        "अवधि चुनें:"
    ) if lang == 'hi' else (
        "📄 <b>Client PDF Report (Max 12 Months):</b>\n\n"
        "Choose duration below:"
    )
    chat_id = update.effective_chat.id if update.effective_chat else user.id
    await context.bot.send_message(chat_id=chat_id, text=prompt, parse_mode="HTML", reply_markup=kb)


async def client_excel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Directly triggers period selector for Client Excel Report."""
    user = update.effective_user
    lang = get_user_language(user.id)
    kb = get_client_report_period_keyboard(fmt="excel", target="all", lang=lang)
    prompt = (
        "📊 <b>Client Excel रिपोर्ट (अधिकतम 12 महीने):</b>\n\n"
        "अवधि चुनें:"
    ) if lang == 'hi' else (
        "📊 <b>Client Excel Report (Max 12 Months):</b>\n\n"
        "Choose duration below:"
    )
    chat_id = update.effective_chat.id if update.effective_chat else user.id
    await context.bot.send_message(chat_id=chat_id, text=prompt, parse_mode="HTML", reply_markup=kb)


async def client_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shortcut for client reports."""
    await client_pdf_command(update, context)


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user = update.effective_user
    stars_amount = payment.total_amount
    charge_id = payment.telegram_payment_charge_id
    payload = payment.invoice_payload
    lang = get_user_language(user.id)

    log_stars_payment(user.id, charge_id, stars_amount)

    # 1. Check if user purchased a Monthly VIP Pass (1 to 12 Months)
    if payload.startswith("vip_pass_"):
        try:
            parts = payload.split("_")
            months = int(parts[3])
            new_expiry_str = add_vip_months(user.id, months)
            notice = get_msg(
                'vip_purchased_notice',
                lang=lang,
                months=months,
                expires_at=new_expiry_str
            )
            await update.message.reply_text(notice, parse_mode="HTML")
            p_prompt = get_msg('period_prompt', lang=lang)
            p_kb = get_period_select_keyboard(lang)
            await update.message.reply_text(p_prompt, parse_mode="HTML", reply_markup=p_kb)
            return
        except Exception as e:
            logger.error(f"Error activating VIP pass payment: {e}")

    # 2. Check if user purchased a single statement
    fmt = "both"
    start_date = None
    end_date = None
    try:
        parts = payload.split("_")
        fmt = parts[1]
        start_date = parts[3]
        end_date = parts[4]
        period_label = f"{start_date} to {end_date}"
    except Exception:
        period_label = "Selected Period"

    success_msg = (
        f"🎉 <b>Payment Successful! ({stars_amount} Stars ⭐ received)</b>\n"
        f"Your financial statement is being generated and sent below:"
    ) if lang == 'en' else (
        f"🎉 <b>भुगतान सफल! ({stars_amount} Stars ⭐ प्राप्त हुए)</b>\n"
        f"आपका वित्तीय स्टेटमेंट तैयार करके नीचे भेजा जा रहा है:"
    )
    await update.message.reply_text(success_msg, parse_mode="HTML")
    await deliver_statement_files(context, update.effective_chat.id, user, fmt, start_date, end_date, period_label, lang)


# ==========================================
# CALLBACK QUERIES (INLINE BUTTONS)
# ==========================================

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    user_id = user.id
    chat_id = update.effective_chat.id if update.effective_chat else user_id
    lang = get_user_language(user_id)
    country_info = get_user_country(user_id)

    logger.info(f"[Callback] User {user_id} (@{user.username or ''}) triggered: {data}")

    if data == "noop":
        return

    # 0. Country Pagination
    if data.startswith("cpage_"):
        if data == "cpage_noop":
            return
        try:
            page_num = int(data.replace("cpage_", ""))
            kb = get_country_select_keyboard(page=page_num)
            await query.edit_message_reply_markup(reply_markup=kb)
        except Exception as e:
            logger.error(f"Error in cpage pagination: {e}")
        return

    # 1. Country Selection Handler
    elif data.startswith("setcountry_"):
        code = data.replace("setcountry_", "")
        c_info = get_country(code)
        set_user_country(
            user_id=user_id,
            country_code=code,
            country_name=c_info["name"],
            currency_code=c_info["currency_code"],
            currency_symbol=c_info["currency_symbol"]
        )
        is_onboarding = not has_user_selected_language(user_id)

        if is_onboarding:
            msg = (
                f"🌍 <b>Country Set: {c_info['flag']} {c_info['name']}!</b>\n"
                f"• Currency: <b>{c_info['currency_symbol']} ({c_info['currency_code']})</b>\n\n"
                f"Now choose your preferred language (Default is English):"
            )
            lang_kb = get_country_languages_keyboard(code, prefix="initlang")
            await query.edit_message_text(msg, parse_mode="HTML", reply_markup=lang_kb)
        else:
            confirm = get_msg(
                'country_changed',
                lang=lang,
                country=f"{c_info['flag']} {c_info['name']}",
                currency=f"{c_info['currency_symbol']} ({c_info['currency_code']})"
            )
            await query.edit_message_text(confirm, parse_mode="HTML")
            # Also offer to switch language
            lang_kb = get_country_languages_keyboard(code, prefix="setlang")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🌐 Would you like to switch to languages for {c_info['name']}?",
                parse_mode="HTML",
                reply_markup=lang_kb
            )
        return

    # 2. View All Global Languages
    elif data.startswith("initlang_more_"):
        kb = get_all_languages_keyboard(prefix="initlang")
        await query.edit_message_text(
            "🌐 <b>All Supported Global Languages:</b>\nSelect your language below:",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    elif data.startswith("setlang_more_"):
        kb = get_all_languages_keyboard(prefix="setlang")
        await query.edit_message_text(
            "🌐 <b>All Supported Global Languages:</b>\nSelect your language below:",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # 3. First-Time Onboarding Language Selection
    elif data.startswith("initlang_"):
        chosen_lang = data.replace("initlang_", "")
        set_user_language(user_id, chosen_lang)
        country_info = get_user_country(user_id)
        curr_code, curr_sym = get_user_currency(user_id)

        try:
            await query.edit_message_text(
                f"✅ <b>Language set: {chosen_lang.upper()}!</b>\n🌍 Currency: <b>{curr_sym} ({curr_code})</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

        welcome_text = get_msg(
            'welcome',
            lang=chosen_lang,
            name=user.first_name or "User",
            currency=curr_sym,
            country=country_info['country_name']
        )
        new_keyboard = get_main_keyboard(chosen_lang, country_code=country_info['country_code'])
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=new_keyboard
        )

        # Automatic Follow-up Announcement: "You are Lucky! 1 Month Free VIP Pass"
        tier_info = get_user_access_tier(user_id)
        exp_str = tier_info.get('expires_at') or (datetime.date.today() + datetime.timedelta(days=30)).strftime("%d %B %Y")

        if chosen_lang == 'hi':
            lucky_msg = (
                f"🎉 <b>बधाई हो! आप बहुत भाग्यशाली (Lucky) हैं!</b> 🌟\n\n"
                f"🎁 आपको मिला है <b>1 महीना (30 दिन) 100% मुफ़्त VIP पास</b>!\n\n"
                f"✨ <b>आपके VIP फायदे:</b>\n"
                f"• 📑 अनलिमिटेड PDF एवं Excel स्टेटमेंट डाउनलोड\n"
                f"• 👥 अनलिमिटेड ग्राहक (Clients) व उधारी/जमा खाता लेज़र\n"
                f"• 🔒 100% सुरक्षित एवं प्राइवेट क्लाउड स्टोरेज\n"
                f"• 📊 विस्तृत वित्तीय विश्लेषण एवं लाभ/हानि रिपोर्ट\n\n"
                f"📅 <b>वैधता (Valid Until):</b> <b>{exp_str}</b>\n\n"
                f"💡 <i>ऑफर: आप अपने देश के शॉपिंग चैनल से जुड़कर और दोस्तों को शेयर करके <b>2 महीने और मुफ़्त VIP पास</b> पा सकते हैं (कुल 3 महीने मुफ़्त)!</i>"
            )
            lucky_btn_text = "🎁 मुफ़्त VIP ऑफर्स देखें (+2 महीने)"
        else:
            lucky_msg = (
                f"🎉 <b>Congratulations! You are Lucky!</b> 🌟\n\n"
                f"🎁 You have received <b>1 Month (30 Days) of 100% FREE VIP Pass</b>!\n\n"
                f"✨ <b>Your VIP Benefits:</b>\n"
                f"• 📑 Unlimited PDF & Excel Statement Downloads\n"
                f"• 👥 Unlimited Clients & Ledger Management\n"
                f"• 🔒 100% Secure & Private Cloud Storage\n"
                f"• 📊 Comprehensive Financial & P&L Analytics\n\n"
                f"📅 <b>Valid Until:</b> <b>{exp_str}</b>\n\n"
                f"💡 <i>Bonus: You can unlock <b>2 more months of free VIP</b> (Total 3 Months Free!) by joining your country's shopping deals channel and sharing with friends!</i>"
            )
            lucky_btn_text = "🎁 View VIP Offers (+2 Months Free)"

        lucky_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(lucky_btn_text, callback_data="open_referral")]
        ])

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=lucky_msg,
                parse_mode="HTML",
                reply_markup=lucky_kb
            )
        except Exception as e:
            logger.warning(f"Could not send lucky VIP announcement to {user_id}: {e}")

        return

    # 4. Regular Language Switch (via /language or settings)
    elif data.startswith("setlang_"):
        chosen_lang = data.replace("setlang_", "")
        set_user_language(user_id, chosen_lang)
        new_keyboard = get_main_keyboard(chosen_lang, country_code=country_info['country_code'])
        confirm_msg = get_msg('language_changed', lang=chosen_lang)
        await query.edit_message_text(confirm_msg, parse_mode="HTML")
        menu_updated_text = format_back_message(chosen_lang)
        await context.bot.send_message(
            chat_id=chat_id,
            text=menu_updated_text,
            parse_mode="HTML",
            reply_markup=new_keyboard
        )
        return

    elif data.startswith("back_to_init_langs_"):
        c_code = data.replace("back_to_init_langs_", "")
        prompt = FIRST_TIME_LANG_PROMPT
        kb = get_country_languages_keyboard(c_code, prefix="initlang")
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    # 5. Open Country or Language Picker from Settings
    elif data == "open_country_picker":
        prompt = get_msg('country_prompt', lang=lang)
        kb = get_country_select_keyboard(page=0, show_back=True)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    elif data == "open_language_picker":
        country_info = get_user_country(user_id)
        prompt = get_msg('language_prompt', lang=lang)
        kb = get_country_languages_keyboard(country_info['country_code'], prefix="setlang", show_back=True)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    elif data == "open_settings":
        curr_code, curr_sym = get_user_currency(user_id)
        country_info = get_user_country(user_id)
        c_code = country_info.get('country_code', 'GLOBAL')

        if lang == 'hi':
            text = (
                f"⚙️ <b>देश एवं भाषा सेटिंग्स (Preferences):</b>\n\n"
                f"• देश (Country): <b>{country_info['country_name']}</b> ({c_code})\n"
                f"• मुद्रा (Currency): <b>{curr_sym} ({curr_code})</b>\n"
                f"• भाषा (Language): <b>{lang.upper()}</b>\n\n"
                f"बदलने के लिए नीचे दिए गए विकल्पों पर टैप करें:"
            )
        else:
            text = (
                f"⚙️ <b>Country & Language Preferences:</b>\n\n"
                f"• Country: <b>{country_info['country_name']}</b> ({c_code})\n"
                f"• Currency: <b>{curr_sym} ({curr_code})</b>\n"
                f"• Language: <b>{lang.upper()}</b>\n\n"
                f"Select an option below to update:"
            )
        kb = get_settings_keyboard(lang)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        return

    elif data == "view_all_channels":
        country_info = get_user_country(user_id)
        user_c_code = country_info.get('country_code', 'IN').upper()
        ch_info = COUNTRY_CHANNELS.get(user_c_code) or COUNTRY_CHANNELS.get("IN")

        if lang == 'hi':
            text = (
                f"📢 <b>{ch_info['flag']} {ch_info['name']} का आधिकारिक डील्स चैनल:</b>\n\n"
                f"• चैनल: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n\n"
                f"<i>रोज़ाना लूट डील्स, डिस्काउंट्स और मुफ़्त VIP पास के लिए अपने देश के चैनल से जुड़ें!</i>"
            )
            btn_join = f"📢 {ch_info['title']} ज्वाइन करें"
        else:
            text = (
                f"📢 <b>Official Deals Channel for {ch_info['flag']} {ch_info['name']}:</b>\n\n"
                f"• Channel: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n\n"
                f"<i>Join your country's channel for daily deals, loot drops, and free VIP pass!</i>"
            )
            btn_join = f"📢 Join {ch_info['title']}"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(btn_join, url=ch_info['channel_url'])],
            [InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")]
        ])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        return

    elif data in ("back_to_main", "back_main"):
        context.user_data['awaiting_custom_dates'] = False
        country_info = get_user_country(user_id)
        menu_text = "🔙 <b>Main Menu</b>\nChoose an option from the menu below 👇" if lang == 'en' else "🔙 <b>मुख्य मेनू</b>\nनीचे दिए गए कीबोर्ड से कोई भी विकल्प चुनें 👇"
        kb = get_main_keyboard(lang, country_code=country_info['country_code'])
        await query.edit_message_text(menu_text, parse_mode="HTML")
        await context.bot.send_message(chat_id=chat_id, text="👇", reply_markup=kb)
        return

    # 6. Date Range Period Presets
    elif data in ("period_this_month", "period_last_month", "period_last_30"):
        preset_key = data.replace("period_", "")
        start_date, end_date, period_label = get_preset_date_range(preset_key)

        is_ch, _ = await check_user_channel_membership(context.bot, user_id, country_info['country_code'])
        tier_info = get_user_access_tier(user_id, is_channel_member=is_ch)

        is_vip = tier_info['is_active']
        is_channel_paused = bool(tier_info.get("requires_channel"))

        if is_vip:
            prompt = get_msg(
                'format_select_prompt_vip',
                lang=lang,
                days_left=tier_info['days_left']
            )
        elif is_channel_paused:
            ch_info = get_country_channel_info(country_info['country_code'])
            prompt = get_msg(
                'month_2_paused_msg',
                lang=lang,
                country=country_info['country_name'],
                channel_title=ch_info['title'],
                channel_username=ch_info['channel_username']
            )
        else:
            prompt = get_msg(
                'format_select_prompt_regular',
                lang=lang,
                period_label=period_label,
                pdf_price=STARS_PDF_PRICE,
                excel_price=STARS_EXCEL_PRICE,
                bundle_price=STARS_BUNDLE_PRICE
            )

        fmt_kb = get_format_select_keyboard(
            start_date,
            end_date,
            lang=lang,
            is_vip=is_vip,
            is_channel_paused=is_channel_paused,
            country_code=country_info['country_code']
        )
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=fmt_kb)
        return

    elif data == "period_custom":
        context.user_data['awaiting_custom_dates'] = True
        custom_prompt = get_msg('custom_date_prompt', lang=lang)
        back_kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 Back to Periods" if lang == 'en' else "🔙 तारीख मेनू", callback_data="period_back"),
                InlineKeyboardButton("🔙 Main Menu" if lang == 'en' else "🔙 मुख्य मेनू", callback_data="back_to_main")
            ]
        ])
        await query.edit_message_text(custom_prompt, parse_mode="HTML", reply_markup=back_kb)
        return

    elif data == "period_back":
        prompt = get_msg('period_prompt', lang=lang)
        inline_kb = get_period_select_keyboard(lang)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=inline_kb)
        return

    # 7. Channel Verification Callback (Month 2 for 7 countries)
    elif data == "verify_channel":
        c_code = country_info['country_code']
        ch_info = get_country_channel_info(c_code)

        is_member, detail = await check_user_channel_membership(context.bot, user_id, c_code)
        if detail == "bot_not_admin":
            set_user_channel_status(user_id, True)
            is_member = True

        if is_member:
            set_user_channel_status(user_id, True)
            tier_info = get_user_access_tier(user_id, is_channel_member=True)
            success_text = get_msg(
                'channel_verified_success',
                lang=lang,
                expires_at=tier_info['expires_at']
            )
            await query.edit_message_text(success_text, parse_mode="HTML")
            p_prompt = get_msg('period_prompt', lang=lang)
            p_kb = get_period_select_keyboard(lang)
            await context.bot.send_message(chat_id=chat_id, text=p_prompt, parse_mode="HTML", reply_markup=p_kb)
        else:
            alert_text = get_msg('channel_not_joined_alert', lang=lang, channel_username=ch_info['channel_username'] if ch_info else "@DealsFetcher")
            await query.answer(alert_text, show_alert=True)
        return

    # 8. VIP Pass Selector & Purchases (1 to 12 Months)
    elif data == "open_vip_menu":
        selected_months = 1
        price = get_stars_price_for_months(selected_months)
        prompt = get_msg(
            'vip_pass_selector_prompt',
            lang=lang,
            selected_months=selected_months,
            price=price
        )
        c_code = (country_info.get('country_code') or 'GLOBAL').upper()
        ch_claimable = (c_code in COUNTRY_CHANNELS) and (not has_claimed_channel_reward(user_id))
        kb = get_vip_pass_keyboard(selected_months=selected_months, lang=lang, channel_claimable=ch_claimable, country_code=c_code)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    elif data.startswith("vip_mo_set_"):
        try:
            selected_months = int(data.replace("vip_mo_set_", ""))
            selected_months = max(1, min(12, selected_months))
            price = get_stars_price_for_months(selected_months)
            prompt = get_msg(
                'vip_pass_selector_prompt',
                lang=lang,
                selected_months=selected_months,
                price=price
            )
            c_code = (country_info.get('country_code') or 'GLOBAL').upper()
            ch_claimable = (c_code in COUNTRY_CHANNELS) and (not has_claimed_channel_reward(user_id))
            kb = get_vip_pass_keyboard(selected_months=selected_months, lang=lang, channel_claimable=ch_claimable, country_code=c_code)
            await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            logger.error(f"Error updating VIP months: {e}")
        return

    elif data == "vip_mo_noop":
        return

    elif data.startswith("vip_buy_"):
        try:
            months = int(data.replace("vip_buy_", ""))
            months = max(1, min(12, months))
            price_stars = get_stars_price_for_months(months)

            title = f"🌟 {months} Month(s) VIP Pass" if lang == 'en' else f"🌟 {months} महीने का VIP पास"
            desc = (
                f"Unlimited PDF & Excel statement downloads for {months} full month(s) with 0 extra stars."
            ) if lang == 'en' else (
                f"{months} महीने के लिए अनलिमिटेड PDF व Excel स्टेटमेंट डाउनलोड्स (0 स्टार्स पर)।"
            )

            payload = f"vip_pass_{user_id}_{months}"
            currency = "XTR"
            prices = [LabeledPrice(title, price_stars)]

            await context.bot.send_invoice(
                chat_id=chat_id,
                title=title,
                description=desc,
                payload=payload,
                currency=currency,
                prices=prices,
                provider_token=""
            )
        except Exception as e:
            logger.error(f"Error sending VIP pass invoice: {e}")
        return

    # 9. VIP Free Statement Downloads (Unlimited during trial / VIP pass)
    elif data.startswith("vip_"):
        parts = data.split("_")
        fmt = parts[1]  # pdf, excel, or both
        start_date = parts[2]
        end_date = parts[3]
        period_label = f"{start_date} to {end_date}"

        is_ch, _ = await check_user_channel_membership(context.bot, user_id, country_info['country_code'])
        tier_info = get_user_access_tier(user_id, is_channel_member=is_ch)

        if tier_info['is_active']:
            conf_msg = get_msg('vip_download_msg', lang=lang, period_label=period_label)
            await query.edit_message_text(conf_msg, parse_mode="HTML")
            await deliver_statement_files(context, user_id, user, fmt, start_date, end_date, period_label, lang)
        elif tier_info.get("requires_channel"):
            ch_info = get_country_channel_info(country_info['country_code'])
            pause_msg = get_msg(
                'month_2_paused_msg',
                lang=lang,
                country=country_info['country_name'],
                channel_title=ch_info['title'],
                channel_username=ch_info['channel_username']
            )
            kb = get_channel_join_keyboard(country_info['country_code'], lang=lang)
            await query.edit_message_text(pause_msg, parse_mode="HTML", reply_markup=kb)
        else:
            expired_alert = (
                "Your free trial has expired! Refer friends or buy a VIP Pass (1 to 12 Months)."
            ) if lang == 'en' else (
                "आपका फ्री ट्रायल समाप्त हो चुका है! दोस्त को रेफर करें या 1-12 महीने का VIP पास लें।"
            )
            await query.answer(expired_alert, show_alert=True)
            # Re-render with Stars pricing
            prompt = get_msg(
                'format_select_prompt_regular',
                lang=lang,
                period_label=period_label,
                pdf_price=STARS_PDF_PRICE,
                excel_price=STARS_EXCEL_PRICE,
                bundle_price=STARS_BUNDLE_PRICE
            )
            fmt_kb = get_format_select_keyboard(start_date, end_date, lang, is_vip=False, is_channel_paused=False)
            await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=fmt_kb)
        return

    # 10. Open Referral Card
    elif data == "open_referral":
        await show_referral_screen(update, context, edit=True)
        return

    # 10b. Claim 1 Month Free Pass for Joining Deals Channel
    elif data.startswith("claim_channel_free_pass"):
        parts = data.split("_")
        target_code = parts[-1] if len(parts) > 4 else country_info.get('country_code', 'IN')
        ch_info = COUNTRY_CHANNELS.get(target_code) or COUNTRY_CHANNELS.get("IN")

        is_member, detail = await check_user_channel_membership(context.bot, user_id, target_code)
        if detail == "bot_not_admin":
            set_user_channel_status(user_id, True)
            is_member = True

        if is_member:
            set_user_channel_status(user_id, True)
            already_claimed = has_claimed_channel_reward(user_id)
            if not already_claimed:
                new_expiry = add_vip_months(user_id, 1)
                set_channel_reward_claimed(user_id, True)
                if lang == 'hi':
                    congrats_text = (
                        f"🎉 <b>बधाई हो! चैनल वेरिफिकेशन सफल!</b>\n\n"
                        f"आप <b>{ch_info['title']}</b> के आधिकारिक सदस्य हैं।\n"
                        f"🎁 आपको मिला है <b>पूरे 2 महीने (60 दिन) 100% मुफ़्त VIP पास</b>!\n"
                        f"• पहला महीना: रजिस्ट्रेशन फ़्री ट्रायल (30 दिन)\n"
                        f"• दूसरा महीना: चैनल जॉइनिंग बोनस (30 दिन)\n\n"
                        f"🌟 वैधता (Valid Until): <b>{new_expiry}</b>\n\n"
                        f"अब आप बिना किसी रोक-टोक के 60 दिनों तक अनलिमिटेड PDF एवं Excel स्टेटमेंट्स और क्लाइंट रिपोर्ट्स डाउनलोड कर सकते हैं।"
                    )
                else:
                    congrats_text = (
                        f"🎉 <b>Congratulations! Channel Verified!</b>\n\n"
                        f"You are an active member of <b>{ch_info['title']}</b>.\n"
                        f"🎁 You have received <b>2 FULL MONTHS (60 Days) of 100% FREE VIP Access</b>!\n"
                        f"• Month 1: Welcome Free Trial (30 Days)\n"
                        f"• Month 2: Deals Channel Member Pass (30 Days)\n\n"
                        f"🌟 Valid Until: <b>{new_expiry}</b>\n\n"
                        f"Enjoy unlimited PDF & Excel statements and client reports for the next 60 days!"
                    )
                await query.answer("🎉 2 Months Free VIP Pass Activated!", show_alert=True)
                ref_url = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
                s_claimed = has_claimed_share_reward(user_id)
                c_kb = get_referral_inline_keyboard(
                    ref_url,
                    country_code=target_code,
                    lang=lang,
                    already_claimed=True,
                    share_reward_claimed=s_claimed
                )
                await query.edit_message_text(congrats_text, parse_mode="HTML", reply_markup=c_kb, disable_web_page_preview=True)
            else:
                tier = get_user_access_tier(user_id, is_channel_member=True)
                exp_info = f" ({tier['expires_at']} तक मान्य)" if tier.get('expires_at') else ""
                already_msg = (
                    f"✅ आप पहले ही 2 महीने का मुफ़्त VIP पास एक्टिव कर चुके हैं{exp_info}!\nआप चैनल के एक्टिव सदस्य हैं।"
                    if lang == 'hi' else
                    f"✅ You have already claimed your 2 Months Free VIP Pass{exp_info}!\nYou are an active channel member."
                )
                await query.answer(already_msg, show_alert=True)
        else:
            alert_text = (
                f"📢 आपने अभी तक {ch_info['title']} ({ch_info['channel_username']}) चैनल ज्वाइन नहीं किया है!\n\n"
                f"कृपया पहले '📢 {ch_info['title']} ज्वाइन करें' पर टैप करके चैनल से जुड़ें, फिर मुफ़्त पास एक्टिव करें।"
                if lang == 'hi' else
                f"📢 You have not joined {ch_info['title']} ({ch_info['channel_username']}) yet!\n\n"
                f"Please tap '📢 Join {ch_info['title']}' to join first, then tap Claim."
            )
            await query.answer(alert_text, show_alert=True)
        return

    # 10c. Claim 1 Month Free Pass for Sharing Shopping Deals Channel with 10 Friends
    elif data.startswith("claim_share_reward_"):
        parts = data.split("_")
        target_code = parts[-1] if len(parts) > 3 else country_info.get('country_code', 'IN')
        ch_info = COUNTRY_CHANNELS.get(target_code) or COUNTRY_CHANNELS.get("IN")
        already_rewarded = has_claimed_share_reward(user_id)

        if already_rewarded:
            msg = "✅ You have already claimed your 10-Friends Shopping Channel Share reward!" if lang == 'en' else "✅ आप 10-फ्रेंड्स शॉपिंग चैनल शेयर का मुफ़्त पास पहले ही ले चुके हैं!"
            await query.answer(msg, show_alert=True)
            return

        is_member, _ = await check_user_channel_membership(context.bot, user_id, target_code)
        if not is_member:
            alert = (
                f"📢 कृपया पहले अपने देश के शॉपिंग चैनल {ch_info['title']} ({ch_info['channel_username']}) को ज्वाइन करें!\n\n"
                f"चैनल ज्वाइन करने के बाद 10 दोस्तों को शेयर करें और मुफ़्त VIP पास एक्टिव करें।"
                if lang == 'hi' else
                f"📢 Please join {ch_info['title']} ({ch_info['channel_username']}) first!\n\n"
                f"Join the channel, share it with 10 friends, then tap Claim to activate your free VIP pass."
            )
            await query.answer(alert, show_alert=True)
            return

        new_expiry = add_vip_months(user_id, 1)
        set_share_reward_claimed(user_id, True)

        if lang == 'hi':
            success_msg = (
                f"🎉 <b>शानदार! 10 दोस्तों का शॉपिंग चैनल शेयर बोनस एक्टिव!</b>\n\n"
                f"🎁 आपको मिला है <b>+1 अतिरिक्त महीना (30 दिन) 100% मुफ़्त VIP पास</b>!\n\n"
                f"🌟 नई वैधता (Valid Until): <b>{new_expiry}</b>\n\n"
                f"अनलिमिटेड PDF एवं Excel स्टेटमेंट्स और क्लाइंट लेज़र का आनंद लें।"
            )
        else:
            success_msg = (
                f"🎉 <b>Awesome! 10-Friends Shopping Channel Share Bonus Activated!</b>\n\n"
                f"🎁 You have received <b>+1 Extra Month (30 Days) of 100% FREE VIP Pass</b>!\n\n"
                f"🌟 New Valid Until: <b>{new_expiry}</b>\n\n"
                f"Enjoy unlimited PDF & Excel statements and full client ledgers."
            )
        await query.answer("🎉 +1 Month Free VIP Pass Activated!", show_alert=True)
        ref_url = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        c_kb = get_referral_inline_keyboard(
            ref_url,
            country_code=target_code,
            lang=lang,
            already_claimed=has_claimed_channel_reward(user_id),
            share_reward_claimed=True
        )
        await query.edit_message_text(success_msg, parse_mode="HTML", reply_markup=c_kb, disable_web_page_preview=True)
        return

    # 11. Open Statement Menu from Referral Screen
    elif data == "open_statement":
        prompt = get_msg('period_prompt', lang=lang)
        inline_kb = get_period_select_keyboard(lang)
        await context.bot.send_message(chat_id=user_id, text=prompt, parse_mode="HTML", reply_markup=inline_kb)
        return

    # 12. Format & Stars Purchase Handlers (Single PDF / Single Excel / Combo)
    elif data.startswith("buy_"):
        parts = data.split("_")
        fmt = parts[1]  # pdf, excel, or both
        start_date = parts[2]
        end_date = parts[3]
        period_label = f"{start_date} to {end_date}"

        await create_and_send_invoice(context, user, user_id, fmt, start_date, end_date, period_label, lang)
        return

    # 13. Open Interactive Entry Management
    elif data == "manage_entries":
        curr_code, curr_sym = get_user_currency(user_id)
        entries = get_recent_expenses(user_id, limit=8)
        if not entries:
            empty_msg = get_msg('undo_empty', lang=lang)
            await query.answer(empty_msg, show_alert=True)
            return

        prompt = get_msg('manage_entries_title', lang=lang)
        kb = get_entries_management_keyboard(entries, lang, currency=curr_sym)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    # 14. Delete Specific Entry by ID: del_tx_{id}
    elif data.startswith("del_tx_"):
        try:
            curr_code, curr_sym = get_user_currency(user_id)
            tx_id = int(data.replace("del_tx_", ""))
            deleted = delete_expense_by_id(user_id, tx_id)
            if deleted:
                today_tot = get_today_total(user_id)
                remaining = get_recent_expenses(user_id, limit=8)

                del_msg = format_del_response(lang, tx_id, deleted, curr_sym, today_tot, remaining)
                if remaining:
                    kb = get_entries_management_keyboard(remaining, lang, currency=curr_sym)
                    await query.edit_message_text(del_msg, parse_mode="HTML", reply_markup=kb)
                else:
                    await query.edit_message_text(del_msg, parse_mode="HTML")
            else:
                alert_text = "Entry already deleted!" if lang == 'en' else "यह एंट्री पहले ही हटाई जा चुकी है!"
                await query.answer(alert_text, show_alert=True)
        except Exception as e:
            logger.error(f"Error in del_tx callback: {e}")
        return

    # 15. User clicked 'Done / Keep Others'
    elif data == "del_done":
        safe_msg = get_msg('all_entries_safe', lang=lang)
        await query.edit_message_text(safe_msg, parse_mode="HTML")
        return

    # 16. Back to Main Menu from any inline sub-menu
    elif data == "back_main":
        await back_command(update, context)
        return

    # 17. Budget Options (Add to existing vs Set new)
    elif data == "budget_opt_add":
        context.user_data['awaiting_budget_add'] = True
        context.user_data['awaiting_budget'] = False
        curr_code, curr_sym = get_user_currency(user_id)
        if lang == 'hi':
            prompt = (
                f"➕ <b>बजट में और राशि जोड़ें:</b>\n\n"
                f"कृपया वह राशि लिखें जो आप मौजूदा बजट में जोड़ना चाहते हैं:\n"
                f"उदा. <code>5000</code> या <code>+5000</code>"
            )
        else:
            prompt = (
                f"➕ <b>Add to Existing Budget:</b>\n\n"
                f"Please enter the amount to add to your current budget:\n"
                f"e.g. <code>5000</code> or <code>+5000</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data == "budget_opt_new":
        context.user_data['awaiting_budget'] = True
        context.user_data['awaiting_budget_add'] = False
        curr_code, curr_sym = get_user_currency(user_id)
        if lang == 'hi':
            prompt = (
                f"✏️ <b>नया मासिक बजट सेट करें:</b>\n\n"
                f"कृपया अपना नया मासिक बजट दर्ज करें:\n"
                f"उदा. <code>15000</code>"
            )
        else:
            prompt = (
                f"✏️ <b>Set New Monthly Budget:</b>\n\n"
                f"Please enter your new monthly budget amount:\n"
                f"e.g. <code>15000</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    # 18. Client Khata Callbacks
    elif data == "client_action_home":
        context.user_data.pop('client_add_step', None)
        context.user_data.pop('new_client_name', None)
        context.user_data.pop('editing_client_field', None)
        context.user_data.pop('client_tx_flow', None)
        await show_client_home(update, context, edit=True)
        return

    elif data == "client_action_add":
        context.user_data['client_add_step'] = 'awaiting_name'
        if lang == 'hi':
            prompt = (
                "➕ <b>नया ग्राहक जोड़ें (Add Client):</b>\n\n"
                "कृपया ग्राहक या पार्टी का नाम लिखें:\n"
                "उदा. <code>रमेश कुमार</code> या <code>गुप्ता ट्रेडर्स</code>"
            )
        else:
            prompt = (
                "➕ <b>Add New Client:</b>\n\n"
                "Please enter the client or business name:\n"
                "e.g. <code>Ramesh Kumar</code> or <code>Gupta Traders</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data == "client_add_skip_phone":
        client_name = context.user_data.pop('new_client_name', 'Client')
        context.user_data.pop('client_add_step', None)
        c_code = country_info.get('country_code', 'GLOBAL')
        new_id = add_client(user_id, name=client_name, phone='', email='', country_code=c_code)
        succ = (
            f"✅ ग्राहक '{client_name}' जोड़ा गया!"
        ) if lang == 'hi' else (
            f"✅ Client '{client_name}' added!"
        )
        await query.answer(succ)
        await show_client_detail(update, context, client_id=new_id, edit=True)
        return

    elif data.startswith("client_action_list_"):
        page_str = data.replace("client_action_list_", "")
        page = int(page_str) if page_str.isdigit() else 1
        await show_client_list(update, context, page=page, edit=True)
        return

    elif data == "client_action_summary":
        await show_client_summary(update, context, edit=True)
        return

    elif data.startswith("client_view_"):
        cid = int(data.replace("client_view_", ""))
        await show_client_detail(update, context, client_id=cid, edit=True)
        return

    elif data.startswith("client_edit_phone_"):
        cid = int(data.replace("client_edit_phone_", ""))
        client = get_client(cid, user_id)
        c_name = client['name'] if client else "Client"
        context.user_data['editing_client_field'] = ('phone', cid)
        if lang == 'hi':
            prompt = (
                f"📱 <b>फोन नंबर बदलें / जोड़ें:</b>\n\n"
                f"ग्राहक <b>{c_name}</b> का नया फोन नंबर लिखें:\n"
                f"उदा. <code>9876543210</code>"
            )
        else:
            prompt = (
                f"📱 <b>Update Phone Number:</b>\n\n"
                f"Enter phone number for <b>{c_name}</b>:\n"
                f"e.g. <code>+91 9876543210</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data.startswith("client_edit_email_"):
        cid = int(data.replace("client_edit_email_", ""))
        client = get_client(cid, user_id)
        c_name = client['name'] if client else "Client"
        context.user_data['editing_client_field'] = ('email', cid)
        if lang == 'hi':
            prompt = (
                f"📧 <b>ईमेल पता बदलें / जोड़ें:</b>\n\n"
                f"ग्राहक <b>{c_name}</b> का ईमेल पता लिखें:\n"
                f"उदा. <code>client@example.com</code>"
            )
        else:
            prompt = (
                f"📧 <b>Update Email Address:</b>\n\n"
                f"Enter email address for <b>{c_name}</b>:\n"
                f"e.g. <code>client@example.com</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data.startswith("client_tx_get_"):
        cid = int(data.replace("client_tx_get_", ""))
        client = get_client(cid, user_id)
        c_name = client['name'] if client else "Client"
        context.user_data['client_tx_flow'] = {'client_id': cid, 'type': 'lena'}
        curr_code, curr_sym = get_user_currency(user_id)
        if lang == 'hi':
            prompt = (
                f"🟢 <b>लेना दर्ज करें (You'll Get):</b>\n\n"
                f"ग्राहक: <b>{c_name}</b>\n\n"
                f"राशि और वैकल्पिक विवरण लिखें:\n"
                f"उदा. <code>1500 माल दिया</code> या सिर्फ <code>1500</code>"
            )
        else:
            prompt = (
                f"🟢 <b>Record Receivable (You'll Get):</b>\n\n"
                f"Client: <b>{c_name}</b>\n\n"
                f"Enter amount and optional note:\n"
                f"e.g. <code>1500 goods delivered</code> or just <code>1500</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data.startswith("client_tx_give_"):
        cid = int(data.replace("client_tx_give_", ""))
        client = get_client(cid, user_id)
        c_name = client['name'] if client else "Client"
        context.user_data['client_tx_flow'] = {'client_id': cid, 'type': 'dena'}
        curr_code, curr_sym = get_user_currency(user_id)
        if lang == 'hi':
            prompt = (
                f"🔴 <b>देना दर्ज करें (You'll Give):</b>\n\n"
                f"ग्राहक: <b>{c_name}</b>\n\n"
                f"राशि और वैकल्पिक विवरण लिखें:\n"
                f"उदा. <code>500 कच्चा माल</code> या सिर्फ <code>500</code>"
            )
        else:
            prompt = (
                f"🔴 <b>Record Payable (You'll Give):</b>\n\n"
                f"Client: <b>{c_name}</b>\n\n"
                f"Enter amount and optional note:\n"
                f"e.g. <code>500 raw materials</code> or just <code>500</code>"
            )
        await query.edit_message_text(prompt, parse_mode="HTML")
        return

    elif data.startswith("client_ledger_"):
        cid = int(data.replace("client_ledger_", ""))
        await show_client_ledger(update, context, client_id=cid)
        return

    elif data.startswith("client_del_prompt_"):
        cid = int(data.replace("client_del_prompt_", ""))
        client = get_client(cid, user_id)
        c_name = client['name'] if client else "Client"
        if lang == 'hi':
            prompt = (
                f"⚠️ <b>क्या आप सचमुच '{c_name}' को हटाना चाहते हैं?</b>\n\n"
                f"इस ग्राहक के सभी लेन-देन और हिसाब हमेशा के लिए हट जाएंगे।"
            )
        else:
            prompt = (
                f"⚠️ <b>Are you sure you want to delete '{c_name}'?</b>\n\n"
                f"All transactions and history for this client will be permanently erased."
            )
        del_kb = get_client_delete_confirm_keyboard(cid, lang)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=del_kb)
        return

    elif data.startswith("client_del_confirm_"):
        cid = int(data.replace("client_del_confirm_", ""))
        delete_client(cid, user_id)
        alert_msg = "ग्राहक हटा दिया गया।" if lang == 'hi' else "Client deleted successfully."
        await query.answer(alert_msg)
        await show_client_home(update, context, edit=True)
        return

    elif data.startswith("cl_fmt_"):
        # Format: cl_fmt_{target}_{fmt}
        # e.g. cl_fmt_all_pdf, cl_fmt_all_excel, cl_fmt_c5_pdf, cl_fmt_c5_excel
        parts = data.split("_")
        target = parts[2]
        fmt = parts[3]
        if target == 'all':
            if lang == 'hi':
                prompt = (
                    f"📄 <b>Client {fmt.upper()} रिपोर्ट अवधि चुनें (अधिकतम 12 महीने):</b>\n\n"
                    f"आप कितने महीने की रिपोर्ट डाउनलोड करना चाहते हैं? नीचे से अवधि चुनें:"
                )
            else:
                prompt = (
                    f"📄 <b>Select Client {fmt.upper()} Report Period (Max 12 Months):</b>\n\n"
                    f"Choose report duration below:"
                )
        else:
            cid = int(target.replace('c', ''))
            c_data = get_client(cid, user_id)
            c_name = c_data['name'] if c_data else "Client"
            if lang == 'hi':
                prompt = (
                    f"📄 <b>{c_name} - {fmt.upper()} स्टेटमेंट अवधि (अधिकतम 12 महीने):</b>\n\n"
                    f"कितने महीने का स्टेटमेंट डाउनलोड करना चाहते हैं? नीचे से अवधि चुनें:"
                )
            else:
                prompt = (
                    f"📄 <b>{c_name} - {fmt.upper()} Statement Period (Max 12 Months):</b>\n\n"
                    f"Choose statement duration below:"
                )

        kb = get_client_report_period_keyboard(fmt=fmt, target=target, lang=lang)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    elif data.startswith("cl_rep_"):
        # Format: cl_rep_{fmt}_{target}_{val}
        # e.g. cl_rep_pdf_all_1, cl_rep_excel_c5_12, cl_rep_pdf_all_custom
        parts = data.split("_")
        fmt = parts[2]
        target = parts[3]
        val = parts[4]

        if val == "custom":
            context.user_data['awaiting_client_report_period'] = {'fmt': fmt, 'target': target}
            back_cb = f"cl_fmt_{target}_{fmt}"
            if lang == 'hi':
                prompt = (
                    f"🗓️ <b>कस्टम अवधि दर्ज करें (अधिकतम 12 महीने):</b>\n\n"
                    f"आप जितने महीने की {fmt.upper()} रिपोर्ट चाहते हैं वह संख्या लिखें (उदा. <code>4</code> या <code>8</code> या अधिकतम <code>12</code>)\n"
                    f"या तारीख रेंज लिखें (उदा. <code>2026-01-01 to 2026-06-01</code>):"
                )
            else:
                prompt = (
                    f"🗓️ <b>Enter Custom Period (Max 12 Months):</b>\n\n"
                    f"Enter number of months (e.g. <code>4</code>, <code>8</code>, up to <code>12</code>)\n"
                    f"or a date range (e.g. <code>2026-01-01 to 2026-06-01</code>):"
                )
            await query.edit_message_text(
                prompt,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Client", callback_data=back_cb)]])
            )
            return
        else:
            months = int(val) if val.isdigit() else 1
            months = max(1, min(12, months))
            wait_text = "⏳ रिपोर्ट तैयार हो रही है..." if lang == 'hi' else "⏳ Generating statement..."
            await query.answer(wait_text)
            chat_id = query.message.chat_id if query.message else user_id
            await deliver_client_report_files(
                context,
                chat_id=chat_id,
                user=user,
                fmt=fmt,
                target=target,
                months=months,
                lang=lang
            )
            return

    # 19. Text Saver Callbacks
    elif data == "ts_action_home":
        context.user_data.pop('awaiting_text_saver_input', None)
        await show_text_saver_home(update, context, page=1, edit=True)
        return

    elif data == "ts_action_add":
        context.user_data['awaiting_text_saver_input'] = True
        if lang == 'hi':
            prompt = (
                "➕ <b>नया सामान जोड़ें (Text Saver):</b>\n\n"
                "लाने वाले सामान का नाम लिखें।\n"
                "आप एक बार में <b>कितने भी सामान</b> लिख सकते हैं!\n\n"
                "💡 <i>टिप: हर सामान को नई लाइन (Enter) में लिखें या कॉमा (,) लगाएं:</i>\n\n"
                "<b>उदाहरण:</b>\n"
                "<code>दूध\nब्रेड\nचीनी 2 किलो\nसाबुन\nचाय पत्ती</code>"
            )
        else:
            prompt = (
                "➕ <b>Add Items to Text Saver:</b>\n\n"
                "Type the items you want to buy/bring.\n"
                "You can enter <b>as many items as you want</b>!\n\n"
                "💡 <i>Tip: Put each item on a new line (Enter) or separate with commas:</i>\n\n"
                "<b>Example:</b>\n"
                "<code>Milk 1L\nBread\nSugar 2kg\nSoap\nTea</code>"
            )
        cancel_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + ("रद्द करें" if lang == 'hi' else "Cancel"), callback_data="ts_action_home")]
        ])
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=cancel_kb)
        return

    elif data.startswith("ts_toggle_"):
        parts = data.split("_")
        item_id = int(parts[2])
        page = int(parts[3]) if len(parts) > 3 else 1
        success, new_status, item_text = toggle_text_saver_item(item_id, user_id)
        if success:
            if new_status == 1:
                toast = f"✅ '{item_text}' खरीदा गया!" if lang == 'hi' else f"✅ '{item_text}' marked as done!"
            else:
                toast = f"⬜ '{item_text}' वापस बाकी लिस्ट में डाला!" if lang == 'hi' else f"⬜ '{item_text}' moved to pending!"
            await query.answer(toast)
        else:
            await query.answer()
        await show_text_saver_home(update, context, page=page, edit=True)
        return

    elif data.startswith("ts_page_"):
        page_val = int(data.replace("ts_page_", ""))
        await show_text_saver_home(update, context, page=page_val, edit=True)
        return

    elif data == "ts_action_clear_done":
        cnt = clear_completed_text_saver_items(user_id, country_code=c_code)
        toast = f"🧹 {cnt} खरीदे हुए सामान हटा दिए गए!" if lang == 'hi' else f"🧹 {cnt} completed items cleared!"
        await query.answer(toast)
        await show_text_saver_home(update, context, page=1, edit=True)
        return

    elif data == "ts_action_clear_all_prompt":
        if lang == 'hi':
            prompt = (
                "⚠️ <b>क्या आप सचमुच सभी सामान हटाना चाहते हैं?</b>\n\n"
                "आपकी पूरी Text Saver लिस्ट खाली हो जाएगी।"
            )
        else:
            prompt = (
                "⚠️ <b>Are you sure you want to clear all items?</b>\n\n"
                "Your entire Text Saver list will be emptied."
            )
        conf_kb = get_text_saver_clear_confirm_keyboard(lang)
        await query.edit_message_text(prompt, parse_mode="HTML", reply_markup=conf_kb)
        return

    elif data == "ts_action_clear_all_confirm":
        clear_all_text_saver_items(user_id, country_code=c_code)
        toast = "🗑️ पूरी लिस्ट साफ कर दी गई।" if lang == 'hi' else "🗑️ Entire list cleared."
        await query.answer(toast)
        await show_text_saver_home(update, context, page=1, edit=True)
        return



# ==========================================
# MESSAGE ROUTER (KEYBOARD, DATE & EXPENSES)
# ==========================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user = update.effective_user
    logger.info(f"[Message] User {user.id} (@{user.username or ''}) sent: '{text}'")

    # If first-time user hasn't selected country yet, prompt them with country selector
    if not has_user_selected_country(user.id):
        kb = get_country_select_keyboard(page=0)
        await update.message.reply_text(
            FIRST_TIME_COUNTRY_PROMPT,
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    # If first-time user hasn't selected language yet, prompt them with language selector
    if not has_user_selected_language(user.id):
        country_info = get_user_country(user.id)
        kb = get_country_languages_keyboard(country_info['country_code'], prefix="initlang")
        await update.message.reply_text(
            FIRST_TIME_LANG_PROMPT,
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    lang = get_user_language(user.id)
    country_info = get_user_country(user.id)
    curr_code, curr_sym = get_user_currency(user.id)
    keyboard = get_main_keyboard(lang, country_code=country_info['country_code'])

    # 1. Check if user was asked for Custom Date Range OR sent a Date Range directly
    date_parsed = parse_date_range(text)
    if date_parsed or context.user_data.get('awaiting_custom_dates'):
        if date_parsed:
            context.user_data['awaiting_custom_dates'] = False
            start_date, end_date, period_label = date_parsed

            is_ch, _ = await check_user_channel_membership(context.bot, user.id, country_info['country_code'])
            tier_info = get_user_access_tier(user.id, is_channel_member=is_ch)

            is_vip = tier_info['is_active']
            is_channel_paused = bool(tier_info.get("requires_channel"))

            if is_vip:
                prompt = get_msg(
                    'format_select_prompt_vip',
                    lang=lang,
                    days_left=tier_info['days_left']
                )
            elif is_channel_paused:
                ch_info = get_country_channel_info(country_info['country_code'])
                prompt = get_msg(
                    'month_2_paused_msg',
                    lang=lang,
                    country=country_info['country_name'],
                    channel_title=ch_info['title'],
                    channel_username=ch_info['channel_username']
                )
            else:
                prompt = get_msg(
                    'format_select_prompt_regular',
                    lang=lang,
                    period_label=period_label,
                    pdf_price=STARS_PDF_PRICE,
                    excel_price=STARS_EXCEL_PRICE,
                    bundle_price=STARS_BUNDLE_PRICE
                )

            fmt_kb = get_format_select_keyboard(
                start_date,
                end_date,
                lang=lang,
                is_vip=is_vip,
                is_channel_paused=is_channel_paused,
                country_code=country_info['country_code']
            )
            await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=fmt_kb)
            return
        elif context.user_data.get('awaiting_custom_dates'):
            inv_msg = get_msg('custom_date_invalid', lang=lang)
            await update.message.reply_text(inv_msg, parse_mode="HTML")
            return

    # 2. Check button clicks from registered button mappings
    action = BUTTON_TO_ACTION.get(text)
    if action:
        # Reset any active conversational input states when a main menu button is pressed
        context.user_data['awaiting_custom_dates'] = False
        context.user_data['awaiting_budget_add'] = False
        context.user_data['awaiting_budget'] = False
        context.user_data.pop('client_add_step', None)
        context.user_data.pop('new_client_name', None)
        context.user_data.pop('editing_client_field', None)
        context.user_data.pop('client_tx_flow', None)
        context.user_data.pop('awaiting_client_report_period', None)
        context.user_data.pop('awaiting_text_saver_input', None)

        if action == ACTION_BACK:
            await back_command(update, context)
            return
        elif action == ACTION_TODAY:
            await today_command(update, context)
            return
        elif action == ACTION_MONTH:
            await month_command(update, context)
            return
        elif action == ACTION_BUDGET:
            await budget_command(update, context)
            return
        elif action == ACTION_CLIENTS:
            await clients_command(update, context)
            return
        elif action == ACTION_TEXT_SAVER:
            await text_saver_command(update, context)
            return
        elif action == ACTION_STATEMENT:
            await statement_command(update, context)
            return
        elif action == ACTION_UNDO:
            await undo_command(update, context)
            return
        elif action == ACTION_REFER:
            await refer_command(update, context)
            return
        elif action == ACTION_VIP:
            await vip_command(update, context)
            return
        elif action == ACTION_LANGUAGE:
            await settings_command(update, context)
            return
        elif action == ACTION_COUNTRY:
            await country_command(update, context)
            return
        elif action == ACTION_LOOT:
            c_code = (country_info.get('country_code') or 'GLOBAL').upper()
            if c_code != 'IN':
                non_india_msg = (
                    "🔥 <b>Today's Loot Deals</b> is available exclusively for users in India 🇮🇳 with Deals Fetcher.\n\n"
                    "If you would like to access Indian loot deals, you can select India in /settings!"
                    if lang == 'en' else
                    "🔥 <b>आज के लूट डील्स</b> केवल भारत 🇮🇳 के यूज़र्स (Deals Fetcher) के लिए उपलब्ध हैं।\n\n"
                    "यदि आप भारतीय लूट डील्स देखना चाहते हैं, तो कृपया /settings में India चुनें!"
                )
                await update.message.reply_text(non_india_msg, parse_mode="HTML")
                return

            ch_info = COUNTRY_CHANNELS.get('IN')
            if lang == 'hi':
                loot_text = (
                    f"🔥 <b>आज के टॉप 90% लूट डील्स — {ch_info['flag']} {ch_info['name']}:</b>\n\n"
                    f"• आधिकारिक टेलीग्राम चैनल: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n"
                    f"• वेबसाइट: <b><a href='{DEALS_FETCHER_URL}'>Deals Fetcher Official Website</a></b>\n\n"
                    f"<i>रोज़ाना लूट डील्स और भारी डिस्काउंट के लिए चैनल से जुड़ें! 🛍️</i>"
                )
                btn_join = f"📢 {ch_info['title']} से जुड़ें"
                btn_web = "🌐 Deals Fetcher वेबसाइट"
            else:
                loot_text = (
                    f"🔥 <b>Today's Top 90% Loot Deals — {ch_info['flag']} {ch_info['name']}:</b>\n\n"
                    f"• Official Telegram Channel: <a href='{ch_info['channel_url']}'>{ch_info['title']}</a> (<code>{ch_info['channel_username']}</code>)\n"
                    f"• Website: <b><a href='{DEALS_FETCHER_URL}'>Deals Fetcher Official Website</a></b>\n\n"
                    f"<i>Join the channel for daily curated loot deals and price drops! 🛍️</i>"
                )
                btn_join = f"📢 Join {ch_info['title']}"
                btn_web = "🌐 Deals Fetcher Website"

            loot_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn_join, url=ch_info['channel_url'])],
                [InlineKeyboardButton(btn_web, url=DEALS_FETCHER_URL)]
            ])
            await update.message.reply_text(loot_text, parse_mode="HTML", reply_markup=loot_kb, disable_web_page_preview=False)
            return

    # 3. Active Conversational States (Budget & Client Management)

    # 3a. Awaiting Budget Addition
    if context.user_data.get('awaiting_budget_add'):
        context.user_data['awaiting_budget_add'] = False
        cleaned = text.replace("+", "").replace(",", "").replace(curr_sym, "").replace("₹", "").replace("$", "").strip()
        try:
            val = float(cleaned)
            if val > 0:
                c_code = country_info.get('country_code', 'GLOBAL')
                new_b = add_to_budget(user.id, val, country_code=c_code)
                if lang == 'hi':
                    msg = f"✅ <b>बजट में सफलतापूर्वक जोड़ा गया!</b>\n\n➕ जोड़ी गई राशि: <b>{curr_sym}{val:,.0f}</b>\n🎯 अब कुल नया बजट: <b>{curr_sym}{new_b:,.0f}</b>"
                else:
                    msg = f"✅ <b>Amount added to budget!</b>\n\n➕ Added: <b>{curr_sym}{val:,.0f}</b>\n🎯 Total Monthly Budget: <b>{curr_sym}{new_b:,.0f}</b>"
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
                return
        except ValueError:
            pass

    # 3b. Awaiting New Budget Set
    if context.user_data.get('awaiting_budget'):
        context.user_data['awaiting_budget'] = False
        cleaned = text.replace(",", "").replace(curr_sym, "").replace("₹", "").replace("$", "").strip()
        try:
            val = float(cleaned)
            if val > 0:
                c_code = country_info.get('country_code', 'GLOBAL')
                set_budget(user.id, val, country_code=c_code)
                msg = get_msg('budget_set', lang=lang, val=val, currency=curr_sym)
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
                return
        except ValueError:
            pass

    # 3b-2. Client Custom Report Period
    if context.user_data.get('awaiting_client_report_period'):
        rep_meta = context.user_data.pop('awaiting_client_report_period')
        fmt = rep_meta['fmt']
        target = rep_meta['target']
        raw_val = text.strip()

        cleaned_num = re.sub(r'[^0-9]', '', raw_val)
        date_range_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*(?:to|-)\s*(\d{4}-\d{2}-\d{2})', raw_val)

        if date_range_match:
            try:
                d1 = datetime.date.fromisoformat(date_range_match.group(1))
                d2 = datetime.date.fromisoformat(date_range_match.group(2))
                if d1 > d2:
                    d1, d2 = d2, d1
                span_months = (d2.year - d1.year) * 12 + (d2.month - d1.month) + 1
                if span_months > 12:
                    warn = "⚠️ अधिकतम 12 महीने की रिपोर्ट मान्य है। अंतिम 12 महीने सेट किए जा रहे हैं।" if lang == 'hi' else "⚠️ Maximum duration is 12 months. Adjusting to last 12 months."
                    await update.message.reply_text(warn)
                    start_date, end_date, period_label, months = get_client_report_date_range(12)
                else:
                    start_date = d1.isoformat()
                    end_date = d2.isoformat()
                    period_label = f"{d1.strftime('%b %Y')} - {d2.strftime('%b %Y')}"
                    months = span_months
            except Exception:
                start_date, end_date, period_label, months = get_client_report_date_range(1)
        elif cleaned_num:
            m_val = int(cleaned_num)
            if m_val > 12:
                warn = "⚠️ अधिकतम 12 महीने की रिपोर्ट मान्य है। 12 महीने की रिपोर्ट तैयार की जा रही है..." if lang == 'hi' else "⚠️ Maximum duration is 12 months. Generating 12 months report..."
                await update.message.reply_text(warn)
                m_val = 12
            m_val = max(1, m_val)
            start_date, end_date, period_label, months = get_client_report_date_range(m_val)
        else:
            start_date, end_date, period_label, months = get_client_report_date_range(1)

        wait_msg = "⏳ रिपोर्ट तैयार की जा रही है..." if lang == 'hi' else "⏳ Generating statement..."
        await update.message.reply_text(wait_msg)
        await deliver_client_report_files(
            context,
            chat_id=update.effective_chat.id,
            user=user,
            fmt=fmt,
            target=target,
            months=months,
            start_date=start_date,
            end_date=end_date,
            period_label=period_label,
            lang=lang
        )
        return


    # 3b-3. Text Saver Awaiting Input
    if context.user_data.get('awaiting_text_saver_input'):
        context.user_data.pop('awaiting_text_saver_input', None)
        c_code = country_info.get('country_code', 'GLOBAL')
        created_items = add_text_saver_items(user.id, text, country_code=c_code)
        if created_items:
            num = len(created_items)
            succ_msg = (
                f"✅ <b>{num} सामान Text Saver में जोड़ दिए गए!</b>"
            ) if lang == 'hi' else (
                f"✅ <b>{num} item(s) saved to Text Saver!</b>"
            )
            await update.message.reply_text(succ_msg, parse_mode="HTML", reply_markup=keyboard)
        await show_text_saver_home(update, context, page=1, edit=False)
        return

    # 3c. Client Creation Step 1: Client Name
    if context.user_data.get('client_add_step') == 'awaiting_name':
        client_name = text.strip()
        if not client_name:
            err_txt = "⚠️ कृपया ग्राहक का नाम लिखें:" if lang == 'hi' else "⚠️ Please enter client name:"
            await update.message.reply_text(err_txt, reply_markup=keyboard)
            return
        context.user_data['new_client_name'] = client_name
        context.user_data['client_add_step'] = 'awaiting_phone'
        if lang == 'hi':
            prompt = (
                f"👤 <b>ग्राहक का नाम: {client_name}</b>\n\n"
                f"कृपया इस ग्राहक का <b>फोन नंबर</b> दर्ज करें (या नीचे <b>'छोड़ें' (Skip Phone)</b> दबाएं):"
            )
        else:
            prompt = (
                f"👤 <b>Client: {client_name}</b>\n\n"
                f"Please enter <b>Phone Number</b> for this client (or press <b>Skip Phone</b> below):"
            )
        kb = get_client_skip_phone_keyboard(lang)
        await update.message.reply_text(prompt, parse_mode="HTML", reply_markup=kb)
        return

    # 3d. Client Creation Step 2: Client Phone (Optional)
    if context.user_data.get('client_add_step') == 'awaiting_phone':
        phone_val = text.strip()
        client_name = context.user_data.pop('new_client_name', 'Client')
        context.user_data.pop('client_add_step', None)
        c_code = country_info.get('country_code', 'GLOBAL')
        new_id = add_client(user.id, name=client_name, phone=phone_val, email='', country_code=c_code)
        succ = (
            f"✅ <b>ग्राहक '{client_name}' सफलतापूर्वक जोड़ा गया!</b>"
        ) if lang == 'hi' else (
            f"✅ <b>Client '{client_name}' added successfully!</b>"
        )
        await update.message.reply_text(succ, parse_mode="HTML", reply_markup=keyboard)
        await show_client_detail(update, context, client_id=new_id, edit=False)
        return

    # 3e. Updating Phone or Email on Client Profile
    if context.user_data.get('editing_client_field'):
        field, client_id = context.user_data.pop('editing_client_field')
        if field == 'phone':
            update_client_phone(client_id, user.id, text.strip())
            msg = "✅ फोन नंबर अपडेट हो गया!" if lang == 'hi' else "✅ Phone number updated!"
        else:
            update_client_email(client_id, user.id, text.strip())
            msg = "✅ ईमेल पता अपडेट हो गया!" if lang == 'hi' else "✅ Email address updated!"
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        await show_client_detail(update, context, client_id=client_id, edit=False)
        return

    # 3f. Recording Lena or Dena Transaction
    if context.user_data.get('client_tx_flow'):
        tx_info = context.user_data.pop('client_tx_flow')
        client_id = tx_info['client_id']
        tx_type = tx_info['type']

        amt, note = parse_amount_and_note(text)
        if amt <= 0:
            err_msg = (
                "⚠️ अमान्य राशि। कृपया वैध संख्या दर्ज करें (जैसे <code>1500</code> या <code>1500 सामान</code>)।"
            ) if lang == 'hi' else (
                "⚠️ Invalid amount. Please enter a valid positive number (e.g. <code>1500</code> or <code>1500 goods</code>)."
            )
            context.user_data['client_tx_flow'] = tx_info
            await update.message.reply_text(err_msg, parse_mode="HTML")
            return

        add_client_transaction(client_id, user.id, amt, tx_type, note=note)
        client = get_client(client_id, user.id)
        c_name = client['name'] if client else "Client"

        if tx_type == 'lena':
            confirm = (
                f"✅ <b>लेना दर्ज हुआ (You'll Get)!</b>\n\n"
                f"👤 ग्राहक: <b>{c_name}</b>\n"
                f"🟢 राशि: <b>{curr_sym}{amt:,.2f}</b>"
            ) if lang == 'hi' else (
                f"✅ <b>Receivable Recorded!</b>\n\n"
                f"👤 Client: <b>{c_name}</b>\n"
                f"🟢 Amount: <b>{curr_sym}{amt:,.2f}</b>"
            )
        else:
            confirm = (
                f"✅ <b>देना दर्ज हुआ (You'll Give)!</b>\n\n"
                f"👤 ग्राहक: <b>{c_name}</b>\n"
                f"🔴 राशि: <b>{curr_sym}{amt:,.2f}</b>"
            ) if lang == 'hi' else (
                f"✅ <b>Payable Recorded!</b>\n\n"
                f"👤 Client: <b>{c_name}</b>\n"
                f"🔴 Amount: <b>{curr_sym}{amt:,.2f}</b>"
            )
        if note:
            confirm += f"\n📝 विवरण: <i>{note}</i>"

        await update.message.reply_text(confirm, parse_mode="HTML", reply_markup=keyboard)
        await show_client_detail(update, context, client_id=client_id, edit=False)
        return

    # 4. Check for budget addition quick text: "+5000", "budget +5000", "बजट +5000"
    budget_add_match = re.match(r'^(?:(?:budget|बजट)\s+)?\+(\d+(?:\.\d+)?)$', text, re.IGNORECASE)
    if budget_add_match:
        val = float(budget_add_match.group(1))
        c_code = country_info.get('country_code', 'GLOBAL')
        new_b = add_to_budget(user.id, val, country_code=c_code)
        if lang == 'hi':
            msg = f"✅ <b>बजट में राशि जोड़ी गई!</b>\n\n➕ जोड़ी गई राशि: <b>{curr_sym}{val:,.0f}</b>\n🎯 अब कुल नया बजट: <b>{curr_sym}{new_b:,.0f}</b>"
        else:
            msg = f"✅ <b>Budget Updated!</b>\n\n➕ Added: <b>{curr_sym}{val:,.0f}</b>\n🎯 Total Monthly Budget: <b>{curr_sym}{new_b:,.0f}</b>"
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    # 5. Check for budget set quick text: "Budget 15000" or "बजट 15000"
    budget_match = re.match(r'^(?:budget|बजट)\s+(\d+(?:\.\d+)?)$', text, re.IGNORECASE)
    if budget_match:
        val = float(budget_match.group(1))
        c_code = country_info.get('country_code', 'GLOBAL')
        set_budget(user.id, val, country_code=c_code)
        msg = get_msg('budget_set', lang=lang, val=val, currency=curr_sym)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    # 4. Try parsing as an Expense / Income
    parsed = parse_expense_text(text)
    if parsed:
        amount, category, note, tx_type = parsed
        register_user(user.id, user.username or "", user.first_name or "")
        expense_id = add_expense(user.id, amount, category, note, tx_type)

        today_total = get_today_total(user.id)
        budget = get_user_budget(user.id)
        is_inc = (tx_type == 'income')

        if is_inc:
            reply = format_income_logged(lang, amount, category, note, expense_id, curr_sym)
        else:
            month_spent = get_month_category_breakdown(user.id)['total_expense'] if budget > 0 else 0.0
            rem = max(0.0, budget - month_spent) if budget > 0 else 0.0
            reply = format_expense_logged(lang, amount, category, note, expense_id, curr_sym, today_total, budget, rem)

        undo_btn_label = get_ui_str('undo_btn', lang, id=expense_id)
        manage_btn_label = get_ui_str('manage_all_btn', lang)

        undo_kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(undo_btn_label, callback_data=f"del_tx_{expense_id}"),
                InlineKeyboardButton(manage_btn_label, callback_data="manage_entries")
            ]
        ])
        await update.message.reply_text(reply, parse_mode="HTML", reply_markup=undo_kb)
    else:
        msg = get_msg('unknown_input', lang=lang)
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)


# ==========================================
# 9:00 PM DAILY NIGHT SUMMARY JOB
# ==========================================

async def daily_night_summary_job(context: ContextTypes.DEFAULT_TYPE):
    user_ids = get_all_active_user_ids()
    today_str = datetime.date.today().strftime("%d %B %Y")

    for uid in user_ids:
        try:
            today_exp = get_today_expenses(uid)
            if not today_exp:
                continue

            lang = get_user_language(uid)
            curr_code, curr_sym = get_user_currency(uid)
            today_tot = get_today_total(uid)
            breakdown = get_month_category_breakdown(uid)
            month_tot = breakdown['total_expense']
            budget = get_user_budget(uid)

            country_info = get_user_country(uid)
            is_india = (country_info.get('country_code', '').upper() == 'IN')
            text = format_daily_summary(lang, today_str, curr_sym, today_tot, month_tot, budget, is_india=is_india)

            await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error sending daily summary to {uid}: {e}")


# ==========================================
# MAIN APPLICATION SETUP
# ==========================================

def build_application():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Core Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler(["country", "currency"], country_command))
    app.add_handler(CommandHandler(["language", "lang"], language_command))
    app.add_handler(CommandHandler(["settings", "preferences"], settings_command))
    app.add_handler(CommandHandler(["channels", "deals_channels", "deals", "loot_channels"], channels_command))
    app.add_handler(CommandHandler(["vip", "subscribe", "buy", "pass"], vip_command))
    app.add_handler(CommandHandler(["refer", "invite"], refer_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("month", month_command))
    app.add_handler(CommandHandler("budget", budget_command))
    app.add_handler(CommandHandler(["clients", "client", "khata", "udhar"], clients_command))
    app.add_handler(CommandHandler(["client_pdf", "clientpdf"], client_pdf_command))
    app.add_handler(CommandHandler(["client_excel", "clientexcel"], client_excel_command))
    app.add_handler(CommandHandler(["client_report", "clientreport"], client_report_command))
    app.add_handler(CommandHandler(["text_saver", "textsaver", "saver", "notes", "list", "saman"], text_saver_command))
    app.add_handler(CommandHandler(["undo", "delete", "manage"], undo_command))
    app.add_handler(CommandHandler(["statement", "download"], statement_command))
    app.add_handler(CommandHandler("excel", excel_quick_command))
    app.add_handler(CommandHandler("pdf", pdf_quick_command))
    app.add_handler(CommandHandler(["back", "wapas", "menu"], back_command))

    # Telegram Stars Payments
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Messages & Inline Callbacks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Global Error Handler
    async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error("Exception in update handler:", exc_info=context.error)

    app.add_error_handler(global_error_handler)

    # Schedule Daily 9:00 PM Summary (15:30 UTC = 21:00 IST)
    try:
        if app.job_queue:
            target_time = datetime.time(hour=15, minute=30, tzinfo=datetime.timezone.utc)
            app.job_queue.run_daily(daily_night_summary_job, time=target_time, name="daily_night_summary")
            print("Daily 9:00 PM summary job scheduled successfully.")
    except Exception as e:
        print("Job queue schedule notice:", e)

    return app


def main():
    import time
    print(f"Starting Hisab-Kitab Bot (@{BOT_USERNAME})...")

    # Start Keep-Alive Web Server for Render / Cloud Hosting Port Binding
    try:
        try:
            from .keep_alive import start_keep_alive
        except ImportError:
            from keep_alive import start_keep_alive
        start_keep_alive()
        print("Keep-alive HTTP server started successfully.")
    except Exception as e:
        print("Keep-alive notice (non-fatal):", e)

    while True:
        try:
            app = build_application()
            print("Hisab-Kitab Bot is now LIVE & POLLING! Press Ctrl+C to stop.")
            app.run_polling(
                poll_interval=1.0,
                timeout=20,
                drop_pending_updates=True,
                bootstrap_retries=10
            )
            break
        except KeyboardInterrupt:
            print("Bot process stopped by user.")
            break
        except Exception as e:
            err_name = type(e).__name__
            err_msg = str(e)
            if "Conflict" in err_name or "Conflict" in err_msg:
                print(f"⚠️ Telegram Conflict: Another bot instance is currently polling (e.g. mobile or previous session). Waiting 15s before reconnecting... ({err_msg})")
            else:
                print(f"⚠️ Polling encountered error ({err_name}): {err_msg}. Retrying in 10s...")
            time.sleep(15)


if __name__ == "__main__":
    main()

