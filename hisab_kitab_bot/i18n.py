# -*- coding: utf-8 -*-
import urllib.parse
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from .config import (
    STARS_PDF_PRICE,
    STARS_EXCEL_PRICE,
    STARS_BUNDLE_PRICE,
    BOT_USERNAME,
    DEALS_FETCHER_URL,
    COUNTRY_CHANNELS,
    get_stars_price_for_months,
    MONTHLY_PASS_PRICING
)

# Action Identifiers
ACTION_TODAY = "ACTION_TODAY"
ACTION_MONTH = "ACTION_MONTH"
ACTION_BUDGET = "ACTION_BUDGET"
ACTION_STATEMENT = "ACTION_STATEMENT"
ACTION_UNDO = "ACTION_UNDO"
ACTION_LANGUAGE = "ACTION_LANGUAGE"
ACTION_COUNTRY = "ACTION_COUNTRY"
ACTION_LOOT = "ACTION_LOOT"
ACTION_REFER = "ACTION_REFER"
ACTION_VIP = "ACTION_VIP"
ACTION_BACK = "ACTION_BACK"
ACTION_CLIENTS = "ACTION_CLIENTS"
ACTION_TEXT_SAVER = "ACTION_TEXT_SAVER"

# 19 Supported Languages Keyboard Buttons
KEYBOARD_BUTTONS = {
    'en': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Today's Expenses",
        'month': "📅 Monthly Summary",
        'budget': "💰 Set Budget",
        'statement': "📥 Download Statement (PDF / Excel)",
        'undo': "🗑️ Undo Last Entry",
        'refer': "🎁 Refer & Earn (1 Mo Free)",
        'vip': "🌟 VIP Pass",
        'language': "🌐 Country / Language",
        'loot': "🔥 Today's Loot Deals",
        'back': "🔙 Back to Main Menu"
    },
    'hi': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 आज का हिसाब",
        'month': "📅 इस महीने का हिसाब",
        'budget': "💰 बजट सेट करें",
        'statement': "📥 स्टेटमेंट (PDF / Excel)",
        'undo': "🗑️ एंट्री हटाएं (Undo)",
        'refer': "🎁 रेफर करें (1 Mo Free)",
        'vip': "🌟 VIP पास",
        'language': "🌐 भाषा / देश बदलें",
        'loot': "🔥 Today's Loot Deals",
        'back': "🔙 मुख्य मेनू (Back)"
    },
    'bn': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 আজকের হিসাব",
        'month': "📅 এই মাসের হিসাব",
        'budget': "💰 বাজেট নির্ধারণ",
        'statement': "📥 স্টেটমেন্ট (PDF/Excel)",
        'undo': "🗑️ এন্ট্রি মুছুন (Undo)",
        'refer': "🎁 রেফার করুন (১ মাস ফ্রি)",
        'vip': "🌟 ভিআইপি পাস (VIP)",
        'language': "🌐 ভাষা / দেশ পরিবর্তন",
        'loot': "🔥 আজকের সেরা অফার",
        'back': "🔙 মূল মেনু (Back)"
    },
    'ur': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 آج کا حساب",
        'month': "📅 اس ماہ کا خلاصہ",
        'budget': "💰 بجٹ سیٹ کریں",
        'statement': "📥 اسٹیٹمنٹ (PDF/Excel)",
        'undo': "🗑️ انٹری ختم کریں (Undo)",
        'refer': "🎁 ریفر کریں (1 ماہ مفت)",
        'vip': "🌟 وی آئی پی پاس (VIP)",
        'language': "🌐 زبان / ملک تبدیل کریں",
        'loot': "🔥 آج کی لوٹ ڈیلز",
        'back': "🔙 مین مینو (Back)"
    },
    'es': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Gastos de Hoy",
        'month': "📅 Resumen Mensual",
        'budget': "💰 Fijar Presupuesto",
        'statement': "📥 Descargar Estado (PDF/Excel)",
        'undo': "🗑️ Eliminar Registro",
        'refer': "🎁 Invitar (1 Mes Gratis)",
        'vip': "🌟 Pase VIP",
        'language': "🌐 Idioma / País",
        'loot': "🔥 Ofertas del Día",
        'back': "🔙 Menú Principal (Volver)"
    },
    'pt': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Gastos de Hoje",
        'month': "📅 Resumo Mensal",
        'budget': "💰 Definir Orçamento",
        'statement': "📥 Baixar Extrato (PDF/Excel)",
        'undo': "🗑️ Desfazer Registro",
        'refer': "🎁 Indicar (1 Mês Grátis)",
        'vip': "🌟 Passe VIP",
        'language': "🌐 Idioma / País",
        'loot': "🔥 Melhores Ofertas",
        'back': "🔙 Menu Principal (Voltar)"
    },
    'ru': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Расходы за сегодня",
        'month': "📅 Итоги за месяц",
        'budget': "💰 Установить бюджет",
        'statement': "📥 Скачать отчет (PDF/Excel)",
        'undo': "🗑️ Удалить запись",
        'refer': "🎁 Рефералы (1 мес. бесплатно)",
        'vip': "🌟 VIP Подписка",
        'language': "🌐 Язык / Страна",
        'loot': "🔥 Горящие скидки",
        'back': "🔙 Главное меню (Назад)"
    },
    'ar': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 مصاريف اليوم",
        'month': "📅 ملخص الشهر",
        'budget': "💰 تحديد الميزانية",
        'statement': "📥 تحميل الكشف (PDF/Excel)",
        'undo': "🗑️ حذف قيد (تراجع)",
        'refer': "🎁 دعوة الأصدقاء (شهر مجاني)",
        'vip': "🌟 اشتراك VIP",
        'language': "🌐 اللغة / الدولة",
        'loot': "🔥 عروض اليوم المميزة",
        'back': "🔙 القائمة الرئيسية (رجوع)"
    },
    'id': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Pengeluaran Hari Ini",
        'month': "📅 Ringkasan Bulanan",
        'budget': "💰 Atur Anggaran",
        'statement': "📥 Unduh Laporan (PDF/Excel)",
        'undo': "🗑️ Hapus Catatan (Undo)",
        'refer': "🎁 Undang Teman (1 Bln Gratis)",
        'vip': "🌟 VIP Langganan",
        'language': "🌐 Bahasa / Negara",
        'loot': "🔥 Promo Hari Ini",
        'back': "🔙 Menu Utama (Kembali)"
    },
    'fr': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Dépenses du Jour",
        'month': "📅 Résumé Mensuel",
        'budget': "💰 Définir le Budget",
        'statement': "📥 Télécharger Relevé (PDF/Excel)",
        'undo': "🗑️ Annuler la Saisie",
        'refer': "🎁 Parrainer (1 Mois Gratuit)",
        'vip': "🌟 Pass VIP",
        'language': "🌐 Langue / Pays",
        'loot': "🔥 Bons Plans du Jour",
        'back': "🔙 Menu Principal (Retour)"
    },
    'de': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Heutige Ausgaben",
        'month': "📅 Monatsübersicht",
        'budget': "💰 Budget Festlegen",
        'statement': "📥 Auszug Herunterladen (PDF/Excel)",
        'undo': "🗑️ Eintrag Löschen (Undo)",
        'refer': "🎁 Freunde Einladen (1 Monat Gratis)",
        'vip': "🌟 VIP-Pass",
        'language': "🌐 Sprache / Land",
        'loot': "🔥 Top-Angebote Heute",
        'back': "🔙 Hauptmenü (Zurück)"
    },
    'it': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Spese di Oggi",
        'month': "📅 Riepilogo Mensile",
        'budget': "💰 Imposta Budget",
        'statement': "📥 Scarica Estratto Conto (PDF/Excel)",
        'undo': "🗑️ Annulla Voce (Undo)",
        'refer': "🎁 Invita Amici (1 Mese Gratis)",
        'vip': "🌟 Pass VIP",
        'language': "🌐 Lingua / Paese",
        'loot': "🔥 Offerte del Giorno",
        'back': "🔙 Menu Principale (Indietro)"
    },
    'tr': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Bugünün Giderleri",
        'month': "📅 Aylık Özet",
        'budget': "💰 Bütçe Belirle",
        'statement': "📥 Ekstre İndir (PDF/Excel)",
        'undo': "🗑️ Kaydı Sil (Geri Al)",
        'refer': "🎁 Davet Et (1 Ay Ücretsiz)",
        'vip': "🌟 VIP Üyelik",
        'language': "🌐 Dil / Ülke",
        'loot': "🔥 Günün Fırsatları",
        'back': "🔙 Ana Menü (Geri)"
    },
    'vi': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Chi Tiêu Hôm Nay",
        'month': "📅 Tổng Kết Tháng",
        'budget': "💰 Đặt Ngân Sách",
        'statement': "📥 Tải Báo Cáo (PDF/Excel)",
        'undo': "🗑️ Xoá Giao Dịch (Hoàn tác)",
        'refer': "🎁 Giới Thiệu (1 Tháng Miễn Phí)",
        'vip': "🌟 Gói VIP",
        'language': "🌐 Ngôn Ngữ / Quốc Gia",
        'loot': "🔥 Ưu Đãi Hôm Nay",
        'back': "🔙 Menu Chính (Quay lại)"
    },
    'ja': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 今日の支出",
        'month': "📅 今月のまとめ",
        'budget': "💰 予算を設定",
        'statement': "📥 明細をダウンロード (PDF/Excel)",
        'undo': "🗑️ 記録を削除 (元に戻す)",
        'refer': "🎁 友達を招待 (1ヶ月無料)",
        'vip': "🌟 VIPパス",
        'language': "🌐 言語 / 国の変更",
        'loot': "🔥 今日のセール",
        'back': "🔙 メインメニュー (戻る)"
    },
    'ko': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 오늘의 지출",
        'month': "📅 이번 달 요약",
        'budget': "💰 예산 설정",
        'statement': "📥 내역서 다운로드 (PDF/Excel)",
        'undo': "🗑️ 항목 삭제 (실행 취소)",
        'refer': "🎁 친구 초대 (1개월 무료)",
        'vip': "🌟 VIP 패스",
        'language': "🌐 언어 / 국가 변경",
        'loot': "🔥 오늘의 특가",
        'back': "🔙 메인 메뉴 (돌아가기)"
    },
    'uk': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Витрати за сьогодні",
        'month': "📅 Підсумки місяця",
        'budget': "💰 Встановити бюджет",
        'statement': "📥 Завантажити виписку (PDF/Excel)",
        'undo': "🗑️ Видалити запис (Undo)",
        'refer': "🎁 Запросити друга (1 міс. безкоштовно)",
        'vip': "🌟 VIP Підписка",
        'language': "🌐 Мова / Країна",
        'loot': "🔥 Знижки дня",
        'back': "🔙 Головне меню (Назад)"
    },
    'uz': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Bugungi xarajatlar",
        'month': "📅 Oylik hisobot",
        'budget': "💰 Byudjet belgilash",
        'statement': "📥 Hisobotni yuklash (PDF/Excel)",
        'undo': "🗑️ Yozuvni oʻchirish (Undo)",
        'refer': "🎁 Taklif qilish (1 oy bepul)",
        'vip': "🌟 VIP Obuna",
        'language': "🌐 Til / Mamlakat",
        'loot': "🔥 Bugungi chegirmalar",
        'back': "🔙 Asosiy menyu (Orqaga)"
    },
    'kk': {
        'clients': "👥 Client",
        'text_saver': "📝 Text Saver",
        'today': "📊 Бүгінгі шығыстар",
        'month': "📅 Айлық қорытынды",
        'budget': "💰 Бюджет орнату",
        'statement': "📥 Көшірмені жүктеу (PDF/Excel)",
        'undo': "🗑️ Жазбаны жою (Undo)",
        'refer': "🎁 Досыңды шақыр (1 ай тегін)",
        'vip': "🌟 VIP Жазылым",
        'language': "🌐 Тіл / Ел",
        'loot': "🔥 Бүгінгі жеңілдіктер",
        'back': "🔙 Басты мәзір (Артқа)"
    }
}

BUTTON_TO_ACTION = {}
for l_code, b_map in KEYBOARD_BUTTONS.items():
    BUTTON_TO_ACTION[b_map['today']] = ACTION_TODAY
    BUTTON_TO_ACTION[b_map['month']] = ACTION_MONTH
    BUTTON_TO_ACTION[b_map['budget']] = ACTION_BUDGET
    BUTTON_TO_ACTION[b_map['statement']] = ACTION_STATEMENT
    BUTTON_TO_ACTION[b_map['undo']] = ACTION_UNDO
    BUTTON_TO_ACTION[b_map['refer']] = ACTION_REFER
    BUTTON_TO_ACTION[b_map['vip']] = ACTION_VIP
    BUTTON_TO_ACTION[b_map['language']] = ACTION_LANGUAGE
    BUTTON_TO_ACTION[b_map['loot']] = ACTION_LOOT
    BUTTON_TO_ACTION[b_map['back']] = ACTION_BACK
    BUTTON_TO_ACTION[b_map['clients']] = ACTION_CLIENTS

BUTTON_TO_ACTION.update({
    "📊 Aaj Ka Hisab": ACTION_TODAY,
    "📅 Is Mahine Ka Hisab": ACTION_MONTH,
    "💰 Budget Set Karein": ACTION_BUDGET,
    "⭐ Monthly PDF Download": ACTION_STATEMENT,
    "🗑️ आखरी एंट्री हटाएं": ACTION_UNDO,
    "🗑️ Undo Last Entry": ACTION_UNDO,
    "🎁 रेफर करें (Free Statement)": ACTION_REFER,
    "🎁 Refer & Earn": ACTION_REFER,
    "🌐 भाषा बदलें (Language)": ACTION_LANGUAGE,
    "🌐 Bhasha Badlein / Language": ACTION_LANGUAGE,
    "🌐 भाषा / देश बदलें": ACTION_LANGUAGE,
    "🌟 VIP पास": ACTION_VIP,
    "🔥 Today's Loot Deals": ACTION_LOOT,
    "🗑️ Manage / Delete Entry": ACTION_UNDO,
    "🗑️ Undo Entry": ACTION_UNDO,
    "🎁 Refer & Earn (Free Statement)": ACTION_REFER,
    "🌐 Change Language / Country": ACTION_LANGUAGE,
    "🌐 Change Language / भाषा": ACTION_LANGUAGE,
    "🔙 वापस": ACTION_BACK,
    "🔙 Back": ACTION_BACK,
    "🔙 वापस (Back)": ACTION_BACK,
    "🔙 Main Menu": ACTION_BACK,
    "🔙 मुख्य मेनू": ACTION_BACK,
    "back": ACTION_BACK,
    "/back": ACTION_BACK,
    "wapas": ACTION_BACK,
    "वापस": ACTION_BACK,
    "menu": ACTION_BACK,
    "/menu": ACTION_BACK,
    "👥 Client": ACTION_CLIENTS,
    "📝 Text Saver": ACTION_TEXT_SAVER,
    "Text Saver": ACTION_TEXT_SAVER,
    "text saver": ACTION_TEXT_SAVER,
    "TextSaver": ACTION_TEXT_SAVER,
    "/text_saver": ACTION_TEXT_SAVER,
    "/textsaver": ACTION_TEXT_SAVER,
    "/saver": ACTION_TEXT_SAVER,
    "/notes": ACTION_TEXT_SAVER,
    "/list": ACTION_TEXT_SAVER,
    "/todo": ACTION_TEXT_SAVER,
    "/saman": ACTION_TEXT_SAVER,
    "सामान": ACTION_TEXT_SAVER,
    "सामान लिस्ट": ACTION_TEXT_SAVER,
    "👥 Client Khata": ACTION_CLIENTS,
    "👥 ग्राहक खाता (Khata)": ACTION_CLIENTS,
    "Client": ACTION_CLIENTS,
    "Clients": ACTION_CLIENTS,
    "clients": ACTION_CLIENTS,
    "/clients": ACTION_CLIENTS,
    "client": ACTION_CLIENTS,
    "/client": ACTION_CLIENTS,
    "khata": ACTION_CLIENTS,
    "/khata": ACTION_CLIENTS,
    "udhar": ACTION_CLIENTS,
    "len den": ACTION_CLIENTS,
    "खाता": ACTION_CLIENTS,
    "उधार": ACTION_CLIENTS,
    "लेन देन": ACTION_CLIENTS,
    "ग्राहक": ACTION_CLIENTS,
})

def get_main_keyboard(lang: str = 'en', country_code: str = 'GLOBAL') -> ReplyKeyboardMarkup:
    """
    Renders fully localized main keyboard.
    - If country is India (IN): includes BOTH Today's Loot Deals AND VIP Pass!
    - For all other countries: includes VIP Pass and Country/Language (Loot Deals excluded).
    """
    is_india = (country_code and country_code.upper() == 'IN')
    btns = KEYBOARD_BUTTONS.get(lang, KEYBOARD_BUTTONS['en'])

    text_saver_btn = btns.get('text_saver', "📝 Text Saver")
    if is_india:
        # India has Both Loot Deals and VIP Pass + Client + Text Saver!
        rows = [
            [KeyboardButton(btns['today']), KeyboardButton(btns['month'])],
            [KeyboardButton(btns['budget']), KeyboardButton(btns['statement'])],
            [KeyboardButton(btns['clients']), KeyboardButton(text_saver_btn)],
            [KeyboardButton(btns['undo']), KeyboardButton(btns['loot'])],
            [KeyboardButton(btns['vip']), KeyboardButton(btns['refer'])],
            [KeyboardButton(btns['language'])],
        ]
    else:
        # Non-India layout with Client + Text Saver
        rows = [
            [KeyboardButton(btns['today']), KeyboardButton(btns['month'])],
            [KeyboardButton(btns['budget']), KeyboardButton(btns['statement'])],
            [KeyboardButton(btns['clients']), KeyboardButton(text_saver_btn)],
            [KeyboardButton(btns['undo']), KeyboardButton(btns['vip'])],
            [KeyboardButton(btns['refer']), KeyboardButton(btns['language'])],
        ]

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

# UI Strings for Inline Keyboards
UI_STRINGS = {
    'en': {
        'settings_country': "🌍 Change Country & Currency",
        'settings_lang': "🌐 Change Language",
        'back_main': "🔙 Back to Main Menu",
        'back_period': "🔙 Back to Periods",
        'back_statement': "🔙 Back to Statement",
        'period_this_month': "📅 This Month",
        'period_last_month': "⏮️ Last Month",
        'period_last_30': "📆 Last 30 Days",
        'period_custom': "🗓️ Custom Date Range",
        'vip_buy_n_mo': "💳 Buy {months} Month Pass ({price} ⭐)",
        'vip_refer_promo': "🎁 Refer 1 Friend = 1 Month Free!",
        'btn_verify_channel': "🔄 Verify & Resume Free Access",
        'btn_buy_vip': "💳 Buy VIP Pass (1-12 Months)",
        'btn_refer_friend': "🎁 Refer 1 Friend (+1 Mo Free)",
        'btn_join_channel': "📢 Join {title}",
        'download_pdf_vip': "📄 Download PDF (Free VIP)",
        'download_excel_vip': "📊 Download Excel (Free VIP)",
        'download_both_vip': "📦 Download Both (PDF + Excel) (Free VIP)",
        'unlock_vip': "🌟 Unlock VIP Pass (1 - 12 Months)",
        'single_pdf': "📄 Single PDF ({price} ⭐)",
        'single_excel': "📊 Single Excel ({price} ⭐)",
        'combo_bundle': "📦 Combo (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 Refer 1 Friend = 1 Month Unlimited Free!",
        'change_dates': "🔙 Change Dates",
        'done_keep': "✅ Done / Keep Others",
        'share_telegram': "📲 Share on Telegram",
        'download_stmt_btn': "📥 Download Statement",
        'manage_entries_btn': "🗑️ Manage / Delete Any Entry",
        'manage_all_btn': "📋 Manage All",
        'undo_btn': "🗑️ Undo (#{id})"
    },
    'hi': {
        'settings_country': "🌍 देश व करेंसी बदलें (Country & Currency)",
        'settings_lang': "🌐 भाषा बदलें (Language)",
        'back_main': "🔙 मुख्य मेनू (Back to Main Menu)",
        'back_period': "🔙 तारीख मेनू (Periods)",
        'back_statement': "🔙 स्टेटमेंट मेनू",
        'period_this_month': "📅 इस महीने का",
        'period_last_month': "⏮️ पिछले महीने का",
        'period_last_30': "📆 पिछले 30 दिन",
        'period_custom': "🗓️ कस्टम तारीख (Date Range)",
        'vip_buy_n_mo': "💳 {months} महीने का पास खरीदें ({price} ⭐)",
        'vip_refer_promo': "🎁 दोस्त को रेफर करें = 1 महीना फ्री!",
        'btn_verify_channel': "🔄 जॉइन कर लिया / वेरिफाई करें",
        'btn_buy_vip': "💳 VIP पास खरीदें (1-12 महीने)",
        'btn_refer_friend': "🎁 दोस्त को रेफर करें (+1 महीना मुफ्त)",
        'btn_join_channel': "📢 {title} जॉइन करें",
        'download_pdf_vip': "📄 PDF डाउनलोड करें (Free VIP)",
        'download_excel_vip': "📊 Excel डाउनलोड करें (Free VIP)",
        'download_both_vip': "📦 दोनों (PDF + Excel) डाउनलोड करें (Free VIP)",
        'unlock_vip': "🌟 VIP पास लें (1 से 12 महीने अनलिमिटेड)",
        'single_pdf': "📄 सिंगल PDF रिपोर्ट ({price} ⭐)",
        'single_excel': "📊 सिंगल Excel फाइल ({price} ⭐)",
        'combo_bundle': "📦 दोनों (PDF + Excel कॉम्बो) ({price} ⭐)",
        'refer_offer': "🎁 1 दोस्त को रेफर करें = 1 महीना Unlimited Free!",
        'change_dates': "🔙 तारीख बदलें (Back)",
        'done_keep': "✅ सब ठीक है (बाकी रखें)",
        'share_telegram': "📲 दोस्तों को Telegram पर भेजें",
        'download_stmt_btn': "📥 स्टेटमेंट डाउनलोड करें",
        'manage_entries_btn': "🗑️ कोई भी एंट्री हटाएं (Manage)",
        'manage_all_btn': "📋 बाकी एंट्रियां देखें",
        'undo_btn': "🗑️ हटाएं / Undo (#{id})"
    },
    'bn': {
        'settings_country': "🌍 দেশ ও মুদ্রা পরিবর্তন করুন",
        'settings_lang': "🌐 ভাষা পরিবর্তন করুন",
        'back_main': "🔙 মূল মেনু (Back to Main Menu)",
        'back_period': "🔙 সময়সীমা মেনু (Periods)",
        'back_statement': "🔙 স্টেটমেন্ট মেনু",
        'period_this_month': "📅 এই মাসের",
        'period_last_month': "⏮️ গত মাসের",
        'period_last_30': "📆 গত ৩০ দিন",
        'period_custom': "🗓️ কাস্টম তারিখ (Date Range)",
        'vip_buy_n_mo': "💳 {months} মাসের পাস কিনুন ({price} ⭐)",
        'vip_refer_promo': "🎁 বন্ধুকে রেফার করুন = ১ মাস ফ্রি!",
        'btn_verify_channel': "🔄 জয়েন করেছি / যাচাই করুন",
        'btn_buy_vip': "💳 VIP পাস কিনুন (১-১২ মাস)",
        'btn_refer_friend': "🎁 বন্ধুকে রেফার করুন (+১ মাস ফ্রি)",
        'btn_join_channel': "📢 {title}-এ যোগ দিন",
        'download_pdf_vip': "📄 PDF ডাউনলোড (ফ্রি VIP)",
        'download_excel_vip': "📊 Excel ডাউনলোড (ফ্রি VIP)",
        'download_both_vip': "📦 দুটিই ডাউনলোড (PDF + Excel) (VIP)",
        'unlock_vip': "🌟 ভিআইপি পাস নিন (১-১২ মাস)",
        'single_pdf': "📄 সিঙ্গেল PDF ({price} ⭐)",
        'single_excel': "📊 সিঙ্গেল Excel ({price} ⭐)",
        'combo_bundle': "📦 কম্বো (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 ১ বন্ধুকে রেফার = ১ মাস ফ্রি আনলিমিটেড!",
        'change_dates': "🔙 তারিখ পরিবর্তন",
        'done_keep': "✅ সম্পন্ন / বাকিগুলো রাখুন",
        'share_telegram': "📲 টেলিগ্রামে শেয়ার করুন",
        'download_stmt_btn': "📥 স্টেটমেন্ট ডাউনলোড",
        'manage_entries_btn': "🗑️ এন্ট্রি মুছুন বা পরিবর্তন করুন",
        'manage_all_btn': "📋 সব এন্ট্রি দেখুন",
        'undo_btn': "🗑️ মুছুন (#{id})"
    },
    'ur': {
        'settings_country': "🌍 ملک اور کرنسی تبدیل کریں",
        'settings_lang': "🌐 زبان تبدیل کریں",
        'back_main': "🔙 مین مینو (Back to Main Menu)",
        'back_period': "🔙 تاریخ کے انتخاب پر واپس",
        'back_statement': "🔙 اسٹیٹمنٹ مینو",
        'period_this_month': "📅 اس ماہ کا",
        'period_last_month': "⏮️ پچھلے ماہ کا",
        'period_last_30': "📆 گزشتہ 30 دن",
        'period_custom': "🗓️ مخصوص تاریخ (Custom)",
        'vip_buy_n_mo': "💳 {months} ماہ کا پاس خریدیں ({price} ⭐)",
        'vip_refer_promo': "🎁 دوست کو ریفر کریں = 1 ماہ مفت!",
        'btn_verify_channel': "🔄 جوائن کر لیا / تصدیق کریں",
        'btn_buy_vip': "💳 VIP پاس خریدیں (1 تا 12 ماہ)",
        'btn_refer_friend': "🎁 دوست کو ریفر کریں (+1 ماہ مفت)",
        'btn_join_channel': "📢 {title} جوائن کریں",
        'download_pdf_vip': "📄 PDF ڈاؤن لوڈ کریں (مفت VIP)",
        'download_excel_vip': "📊 Excel ڈاؤن لوڈ کریں (مفت VIP)",
        'download_both_vip': "📦 دونوں ڈاؤن لوڈ کریں (PDF + Excel)",
        'unlock_vip': "🌟 VIP پاس انلاک کریں (1 تا 12 ماہ)",
        'single_pdf': "📄 سنگل PDF ({price} ⭐)",
        'single_excel': "📊 سنگل Excel ({price} ⭐)",
        'combo_bundle': "📦 کومبو (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 دوست کو ریفر کریں = 1 ماہ لامحدود مفت!",
        'change_dates': "🔙 تاریخ تبدیل کریں",
        'done_keep': "✅ ٹھیک ہے / باقی رکھیں",
        'share_telegram': "📲 ٹیلیگرام پر شیئر کریں",
        'download_stmt_btn': "📥 اسٹیٹمنٹ ڈاؤن لوڈ کریں",
        'manage_entries_btn': "🗑️ انٹریز کا انتظام کریں",
        'manage_all_btn': "📋 تمام انٹریز دیکھیں",
        'undo_btn': "🗑️ ڈیلیٹ (#{id})"
    },
    'ru': {
        'settings_country': "🌍 Изменить страну и валюту",
        'settings_lang': "🌐 Изменить язык интерфейса",
        'back_main': "🔙 Главное меню (Назад)",
        'back_period': "🔙 К выбору периода",
        'back_statement': "🔙 Меню отчетов",
        'period_this_month': "📅 Этот месяц",
        'period_last_month': "⏮️ Прошлый месяц",
        'period_last_30': "📆 Последние 30 дней",
        'period_custom': "🗓️ Свой период дат",
        'vip_buy_n_mo': "💳 Купить подписку на {months} мес. ({price} ⭐)",
        'vip_refer_promo': "🎁 Пригласи друга = 1 месяц бесплатно!",
        'btn_verify_channel': "🔄 Проверить подписку на канал",
        'btn_buy_vip': "💳 Купить VIP (1-12 мес.)",
        'btn_refer_friend': "🎁 Пригласить друга (+1 мес.)",
        'btn_join_channel': "📢 Вступить в {title}",
        'download_pdf_vip': "📄 Скачать PDF (VIP Бесплатно)",
        'download_excel_vip': "📊 Скачать Excel (VIP Бесплатно)",
        'download_both_vip': "📦 Скачать оба (PDF + Excel)",
        'unlock_vip': "🌟 Получить VIP доступ (1 - 12 мес.)",
        'single_pdf': "📄 Отчет PDF ({price} ⭐)",
        'single_excel': "📊 Файл Excel ({price} ⭐)",
        'combo_bundle': "📦 Комбо (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 друг = 1 месяц безлимита бесплатно!",
        'change_dates': "🔙 Назад к датам",
        'done_keep': "✅ Готово / Оставить остальные",
        'share_telegram': "📲 Поделиться в Telegram",
        'download_stmt_btn': "📥 Скачать выписку",
        'manage_entries_btn': "🗑️ Управление записями",
        'manage_all_btn': "📋 Все записи",
        'undo_btn': "🗑️ Удалить (#{id})"
    },
    'es': {
        'settings_country': "🌍 Cambiar País y Moneda",
        'settings_lang': "🌐 Cambiar Idioma",
        'back_main': "🔙 Menú Principal (Volver)",
        'back_period': "🔙 Volver a Períodos",
        'back_statement': "🔙 Menú de Extractos",
        'period_this_month': "📅 Este Mes",
        'period_last_month': "⏮️ Mes Pasado",
        'period_last_30': "📆 Últimos 30 días",
        'period_custom': "🗓️ Rango Personalizado",
        'vip_buy_n_mo': "💳 Comprar Pase de {months} Meses ({price} ⭐)",
        'vip_refer_promo': "🎁 Invitar 1 amigo = ¡1 Mes Gratis!",
        'btn_verify_channel': "🔄 Verificar Canal y Reanudar",
        'btn_buy_vip': "💳 Comprar Pase VIP (1-12 Meses)",
        'btn_refer_friend': "🎁 Invitar 1 Amigo (+1 Mes Gratis)",
        'btn_join_channel': "📢 Unirse a {title}",
        'download_pdf_vip': "📄 Descargar PDF (VIP Gratis)",
        'download_excel_vip': "📊 Descargar Excel (VIP Gratis)",
        'download_both_vip': "📦 Descargar Ambos (PDF + Excel)",
        'unlock_vip': "🌟 Desbloquear VIP (1 - 12 Meses)",
        'single_pdf': "📄 PDF Individual ({price} ⭐)",
        'single_excel': "📊 Excel Individual ({price} ⭐)",
        'combo_bundle': "📦 Combo (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 amigo = ¡1 Mes Ilimitado Gratis!",
        'change_dates': "🔙 Cambiar Fechas",
        'done_keep': "✅ Listo / Mantener los demás",
        'share_telegram': "📲 Compartir en Telegram",
        'download_stmt_btn': "📥 Descargar Extracto",
        'manage_entries_btn': "🗑️ Gestionar / Eliminar Registros",
        'manage_all_btn': "📋 Ver Todos los Registros",
        'undo_btn': "🗑️ Deshacer (#{id})"
    },
    'pt': {
        'settings_country': "🌍 Mudar País e Moeda",
        'settings_lang': "🌐 Mudar Idioma",
        'back_main': "🔙 Menu Principal (Voltar)",
        'back_period': "🔙 Voltar aos Períodos",
        'back_statement': "🔙 Menu de Extratos",
        'period_this_month': "📅 Este Mês",
        'period_last_month': "⏮️ Mês Passado",
        'period_last_30': "📆 Últimos 30 dias",
        'period_custom': "🗓️ Período Personalizado",
        'vip_buy_n_mo': "💳 Comprar Passe de {months} Meses ({price} ⭐)",
        'vip_refer_promo': "🎁 Indicar 1 amigo = 1 Mês Grátis!",
        'btn_verify_channel': "🔄 Verificar e Retomar Acesso",
        'btn_buy_vip': "💳 Comprar VIP (1-12 Meses)",
        'btn_refer_friend': "🎁 Indicar 1 Amigo (+1 Mês)",
        'btn_join_channel': "📢 Entrar no canal {title}",
        'download_pdf_vip': "📄 Baixar PDF (VIP Grátis)",
        'download_excel_vip': "📊 Baixar Excel (VIP Grátis)",
        'download_both_vip': "📦 Baixar Ambos (PDF + Excel)",
        'unlock_vip': "🌟 Desbloquear VIP (1 - 12 Meses)",
        'single_pdf': "📄 PDF Individual ({price} ⭐)",
        'single_excel': "📊 Excel Individual ({price} ⭐)",
        'combo_bundle': "📦 Combo (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 indicação = 1 Mês Grátis Ilimitado!",
        'change_dates': "🔙 Mudar Datas",
        'done_keep': "✅ Pronto / Manter os outros",
        'share_telegram': "📲 Compartilhar no Telegram",
        'download_stmt_btn': "📥 Baixar Extrato",
        'manage_entries_btn': "🗑️ Gerenciar Registros",
        'manage_all_btn': "📋 Ver Todos os Registros",
        'undo_btn': "🗑️ Desfazer (#{id})"
    },
    'ar': {
        'settings_country': "🌍 تغيير الدولة والعملة",
        'settings_lang': "🌐 تغيير لغة البوت",
        'back_main': "🔙 القائمة الرئيسية (رجوع)",
        'back_period': "🔙 العودة للفترات",
        'back_statement': "🔙 قائمة الكشوفات",
        'period_this_month': "📅 هذا الشهر",
        'period_last_month': "⏮️ الشهر الماضي",
        'period_last_30': "📆 آخر 30 يوماً",
        'period_custom': "🗓️ فترة مخصصة",
        'vip_buy_n_mo': "💳 شراء اشتراك لمدة {months} شهر ({price} ⭐)",
        'vip_refer_promo': "🎁 دعوة صديق = شهر مجاني!",
        'btn_verify_channel': "🔄 تحقق من الاشتراك بالقناة",
        'btn_buy_vip': "💳 شراء اشتراك VIP (1-12 شهر)",
        'btn_refer_friend': "🎁 دعوة صديق (+1 شهر مجاني)",
        'btn_join_channel': "📢 انضم إلى {title}",
        'download_pdf_vip': "📄 تحميل PDF (مجاناً VIP)",
        'download_excel_vip': "📊 تحميل Excel (مجاناً VIP)",
        'download_both_vip': "📦 تحميل الاثنين (PDF + Excel)",
        'unlock_vip': "🌟 فتح اشتراك VIP (1 إلى 12 شهر)",
        'single_pdf': "📄 ملف PDF فردي ({price} ⭐)",
        'single_excel': "📊 ملف Excel فردي ({price} ⭐)",
        'combo_bundle': "📦 باقة التوفير (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 صديق واحد = شهر كامل مجاناً بلا حدود!",
        'change_dates': "🔙 تغيير التواريخ",
        'done_keep': "✅ تم / الاحتفاظ بالباقي",
        'share_telegram': "📲 مشاركة عبر تليجرام",
        'download_stmt_btn': "📥 تحميل الكشف",
        'manage_entries_btn': "🗑️ إدارة القيود والحذف",
        'manage_all_btn': "📋 عرض كل القيود",
        'undo_btn': "🗑️ حذف (#{id})"
    },
    'id': {
        'settings_country': "🌍 Ubah Negara & Mata Uang",
        'settings_lang': "🌐 Ubah Bahasa",
        'back_main': "🔙 Menu Utama (Kembali)",
        'back_period': "🔙 Kembali ke Pilihan Periode",
        'back_statement': "🔙 Menu Laporan",
        'period_this_month': "📅 Bulan Ini",
        'period_last_month': "⏮️ Bulan Lalu",
        'period_last_30': "📆 30 Hari Terakhir",
        'period_custom': "🗓️ Rentang Tanggal Kustom",
        'vip_buy_n_mo': "💳 Beli Akses {months} Bulan ({price} ⭐)",
        'vip_refer_promo': "🎁 Undang 1 Teman = 1 Bulan Gratis!",
        'btn_verify_channel': "🔄 Verifikasi & Lanjutkan Akses",
        'btn_buy_vip': "💳 Beli Akses VIP (1-12 Bulan)",
        'btn_refer_friend': "🎁 Undang 1 Teman (+1 Bulan Gratis)",
        'btn_join_channel': "📢 Gabung Saluran {title}",
        'download_pdf_vip': "📄 Unduh PDF (VIP Gratis)",
        'download_excel_vip': "📊 Unduh Excel (VIP Gratis)",
        'download_both_vip': "📦 Unduh Keduanya (PDF + Excel)",
        'unlock_vip': "🌟 Buka Akses VIP (1 - 12 Bulan)",
        'single_pdf': "📄 PDF Tunggal ({price} ⭐)",
        'single_excel': "📊 Excel Tunggal ({price} ⭐)",
        'combo_bundle': "📦 Paket Combo (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 teman = 1 Bulan Gratis Tanpa Batas!",
        'change_dates': "🔙 Ubah Tanggal",
        'done_keep': "✅ Selesai / Simpan Lainnya",
        'share_telegram': "📲 Bagikan di Telegram",
        'download_stmt_btn': "📥 Unduh Laporan",
        'manage_entries_btn': "🗑️ Kelola / Hapus Catatan",
        'manage_all_btn': "📋 Lihat Semua Catatan",
        'undo_btn': "🗑️ Hapus (#{id})"
    },
    'fr': {
        'settings_country': "🌍 Changer de Pays et Devise",
        'settings_lang': "🌐 Changer de Langue",
        'back_main': "🔙 Menu Principal (Retour)",
        'back_period': "🔙 Retour aux Périodes",
        'back_statement': "🔙 Menu des Relevés",
        'period_this_month': "📅 Ce Mois-ci",
        'period_last_month': "⏮️ Le Mois Dernier",
        'period_last_30': "📆 Les 30 Derniers Jours",
        'period_custom': "🗓️ Période Personnalisée",
        'vip_buy_n_mo': "💳 Acheter Pass {months} Mois ({price} ⭐)",
        'vip_refer_promo': "🎁 Parrainez 1 ami = 1 Mois Gratuit !",
        'btn_verify_channel': "🔄 Vérifier et Reprendre l'Accès",
        'btn_buy_vip': "💳 Acheter Pass VIP (1-12 Mois)",
        'btn_refer_friend': "🎁 Parrainer 1 Ami (+1 Mois)",
        'btn_join_channel': "📢 Rejoindre {title}",
        'download_pdf_vip': "📄 Télécharger PDF (VIP Gratuit)",
        'download_excel_vip': "📊 Télécharger Excel (VIP Gratuit)",
        'download_both_vip': "📦 Télécharger les Deux (PDF + Excel)",
        'unlock_vip': "🌟 Débloquer VIP (1 - 12 Mois)",
        'single_pdf': "📄 PDF Seul ({price} ⭐)",
        'single_excel': "📊 Excel Seul ({price} ⭐)",
        'combo_bundle': "📦 Pack Combo (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 ami = 1 Mois Illimité Gratuit !",
        'change_dates': "🔙 Changer les Dates",
        'done_keep': "✅ Terminé / Conserver le Reste",
        'share_telegram': "📲 Partager sur Telegram",
        'download_stmt_btn': "📥 Télécharger Relevé",
        'manage_entries_btn': "🗑️ Gérer les Entrées",
        'manage_all_btn': "📋 Toutes les Entrées",
        'undo_btn': "🗑️ Supprimer (#{id})"
    },
    'de': {
        'settings_country': "🌍 Land und Währung Ändern",
        'settings_lang': "🌐 Sprache Ändern",
        'back_main': "🔙 Hauptmenü (Zurück)",
        'back_period': "🔙 Zurück zu Zeiträumen",
        'back_statement': "🔙 Auszugsmenü",
        'period_this_month': "📅 Dieser Monat",
        'period_last_month': "⏮️ Letzter Monat",
        'period_last_30': "📆 Letzte 30 Tage",
        'period_custom': "🗓️ Benutzerdefinierter Zeitraum",
        'vip_buy_n_mo': "💳 {months}-Monats-Pass Kaufen ({price} ⭐)",
        'vip_refer_promo': "🎁 1 Freund Einladen = 1 Monat Gratis!",
        'btn_verify_channel': "🔄 Überprüfen & Fortsetzen",
        'btn_buy_vip': "💳 VIP-Pass Kaufen (1-12 Monate)",
        'btn_refer_friend': "🎁 Freund Einladen (+1 Monat)",
        'btn_join_channel': "📢 Kanal {title} Beitreten",
        'download_pdf_vip': "📄 PDF Herunterladen (VIP Gratis)",
        'download_excel_vip': "📊 Excel Herunterladen (VIP Gratis)",
        'download_both_vip': "📦 Beides Herunterladen (PDF + Excel)",
        'unlock_vip': "🌟 VIP-Pass Freischalten (1-12 Monate)",
        'single_pdf': "📄 Einzelnes PDF ({price} ⭐)",
        'single_excel': "📊 Einzelne Excel ({price} ⭐)",
        'combo_bundle': "📦 Kombi-Paket ({price} ⭐)",
        'refer_offer': "🎁 1 Freund = 1 Monat Unbegrenzt Gratis!",
        'change_dates': "🔙 Datum Ändern",
        'done_keep': "✅ Fertig / Rest Behalten",
        'share_telegram': "📲 Auf Telegram Teilen",
        'download_stmt_btn': "📥 Auszug Herunterladen",
        'manage_entries_btn': "🗑️ Einträge Verwalten",
        'manage_all_btn': "📋 Alle Einträge Anzeigen",
        'undo_btn': "🗑️ Löschen (#{id})"
    },
    'it': {
        'settings_country': "🌍 Cambia Paese e Valuta",
        'settings_lang': "🌐 Cambia Lingua",
        'back_main': "🔙 Menu Principale (Indietro)",
        'back_period': "🔙 Torna ai Periodi",
        'back_statement': "🔙 Menu Estratto Conto",
        'period_this_month': "📅 Questo Mese",
        'period_last_month': "⏮️ Mese Scorso",
        'period_last_30': "📆 Ultimi 30 Giorni",
        'period_custom': "🗓️ Periodo Personalizzato",
        'vip_buy_n_mo': "💳 Acquista Pass {months} Mesi ({price} ⭐)",
        'vip_refer_promo': "🎁 Invita 1 amico = 1 Mese Gratis!",
        'btn_verify_channel': "🔄 Verifica e Ripristina Accesso",
        'btn_buy_vip': "💳 Compra Pass VIP (1-12 Mesi)",
        'btn_refer_friend': "🎁 Invita 1 Amico (+1 Mese)",
        'btn_join_channel': "📢 Unisciti a {title}",
        'download_pdf_vip': "📄 Scarica PDF (VIP Gratis)",
        'download_excel_vip': "📊 Scarica Excel (VIP Gratis)",
        'download_both_vip': "📦 Scarica Entrambi (PDF + Excel)",
        'unlock_vip': "🌟 Sblocca VIP (1 - 12 Mesi)",
        'single_pdf': "📄 Singolo PDF ({price} ⭐)",
        'single_excel': "📊 Singolo Excel ({price} ⭐)",
        'combo_bundle': "📦 Pacchetto Combo ({price} ⭐)",
        'refer_offer': "🎁 1 amico = 1 Mese Illimitato Gratis!",
        'change_dates': "🔙 Modifica Date",
        'done_keep': "✅ Fatto / Mantieni il Resto",
        'share_telegram': "📲 Condividi su Telegram",
        'download_stmt_btn': "📥 Scarica Estratto Conto",
        'manage_entries_btn': "🗑️ Gestisci le Voci",
        'manage_all_btn': "📋 Tutte le Voci",
        'undo_btn': "🗑️ Elimina (#{id})"
    },
    'tr': {
        'settings_country': "🌍 Ülke ve Para Birimi Değiştir",
        'settings_lang': "🌐 Dili Değiştir",
        'back_main': "🔙 Ana Menü (Geri)",
        'back_period': "🔙 Dönem Seçimine Geri Dön",
        'back_statement': "🔙 Ekstre Menüsü",
        'period_this_month': "📅 Bu Ay",
        'period_last_month': "⏮️ Geçen Ay",
        'period_last_30': "📆 Son 30 Gün",
        'period_custom': "🗓️ Özel Tarih Aralığı",
        'vip_buy_n_mo': "💳 {months} Aylık Pasaport Al ({price} ⭐)",
        'vip_refer_promo': "🎁 1 Arkadaşını Davet Et = 1 Ay Ücretsiz!",
        'btn_verify_channel': "🔄 Doğrula ve Erişimi Başlat",
        'btn_buy_vip': "💳 VIP Satın Al (1-12 Ay)",
        'btn_refer_friend': "🎁 Arkadaşını Davet Et (+1 Ay)",
        'btn_join_channel': "📢 {title} Kanalına Katıl",
        'download_pdf_vip': "📄 PDF İndir (VIP Ücretsiz)",
        'download_excel_vip': "📊 Excel İndir (VIP Ücretsiz)",
        'download_both_vip': "📦 İkisini de İndir (PDF + Excel)",
        'unlock_vip': "🌟 VIP Kilidini Aç (1 - 12 Ay)",
        'single_pdf': "📄 Tek PDF ({price} ⭐)",
        'single_excel': "📊 Tek Excel ({price} ⭐)",
        'combo_bundle': "📦 Kombo Paket ({price} ⭐)",
        'refer_offer': "🎁 1 arkadaş = 1 Ay Sınırsız Ücretsiz!",
        'change_dates': "🔙 Tarihleri Değiştir",
        'done_keep': "✅ Tamam / Diğerlerini Koru",
        'share_telegram': "📲 Telegram'da Paylaş",
        'download_stmt_btn': "📥 Ekstreyi İndir",
        'manage_entries_btn': "🗑️ Kayıtları Yönet / Sil",
        'manage_all_btn': "📋 Tüm Kayıtları Gör",
        'undo_btn': "🗑️ Geri Al (#{id})"
    },
    'vi': {
        'settings_country': "🌍 Đổi Quốc Gia & Tiền Tệ",
        'settings_lang': "🌐 Đổi Ngôn Ngữ",
        'back_main': "🔙 Menu Chính (Quay lại)",
        'back_period': "🔙 Quay lại chọn kỳ",
        'back_statement': "🔙 Menu Báo Cáo",
        'period_this_month': "📅 Tháng Này",
        'period_last_month': "⏮️ Tháng Trước",
        'period_last_30': "📆 30 Ngày Qua",
        'period_custom': "🗓️ Khoảng Thời Gian Tuỳ Chọn",
        'vip_buy_n_mo': "💳 Mua Gói {months} Tháng ({price} ⭐)",
        'vip_refer_promo': "🎁 Giới thiệu 1 người = 1 Tháng Miễn Phí!",
        'btn_verify_channel': "🔄 Xác minh & Tiếp tục Truy cập",
        'btn_buy_vip': "💳 Mua VIP (1-12 Tháng)",
        'btn_refer_friend': "🎁 Giới thiệu 1 Bạn (+1 Tháng)",
        'btn_join_channel': "📢 Tham gia kênh {title}",
        'download_pdf_vip': "📄 Tải PDF (VIP Miễn Phí)",
        'download_excel_vip': "📊 Tải Excel (VIP Miễn Phí)",
        'download_both_vip': "📦 Tải Cả Hai (PDF + Excel)",
        'unlock_vip': "🌟 Mở Gói VIP (1 - 12 Tháng)",
        'single_pdf': "📄 Bản PDF ({price} ⭐)",
        'single_excel': "📊 Bản Excel ({price} ⭐)",
        'combo_bundle': "📦 Gói Combo ({price} ⭐)",
        'refer_offer': "🎁 1 lượt giới thiệu = 1 Tháng Không Giới Hạn!",
        'change_dates': "🔙 Đổi Ngày",
        'done_keep': "✅ Xong / Giữ lại các mục khác",
        'share_telegram': "📲 Chia sẻ qua Telegram",
        'download_stmt_btn': "📥 Tải Báo Cáo",
        'manage_entries_btn': "🗑️ Quản lý / Xoá Giao Dịch",
        'manage_all_btn': "📋 Xem Tất Cả Giao Dịch",
        'undo_btn': "🗑️ Xoá (#{id})"
    },
    'ja': {
        'settings_country': "🌍 国と通貨を変更",
        'settings_lang': "🌐 言語を変更",
        'back_main': "🔙 メインメニュー (戻る)",
        'back_period': "🔙 期間選択に戻る",
        'back_statement': "🔙 明細メニュー",
        'period_this_month': "📅 今月",
        'period_last_month': "⏮️ 先月",
        'period_last_30': "📆 過去30日間",
        'period_custom': "🗓️ カスタム期間",
        'vip_buy_n_mo': "💳 {months}ヶ月パスを購入 ({price} ⭐)",
        'vip_refer_promo': "🎁 友達1人招待 = 1ヶ月無料！",
        'btn_verify_channel': "🔄 チャンネル参加を確認して再開",
        'btn_buy_vip': "💳 VIPパス購入 (1〜12ヶ月)",
        'btn_refer_friend': "🎁 友達を招待 (+1ヶ月無料)",
        'btn_join_channel': "📢 {title} に参加",
        'download_pdf_vip': "📄 PDFダウンロード (VIP無料)",
        'download_excel_vip': "📊 Excelダウンロード (VIP無料)",
        'download_both_vip': "📦 両方ダウンロード (PDF + Excel)",
        'unlock_vip': "🌟 VIPパスをアンロック (1〜12ヶ月)",
        'single_pdf': "📄 単品 PDF ({price} ⭐)",
        'single_excel': "📊 単品 Excel ({price} ⭐)",
        'combo_bundle': "📦 コンボセット ({price} ⭐)",
        'refer_offer': "🎁 1人招待 = 1ヶ月間ダウンロード無制限無料！",
        'change_dates': "🔙 日付を変更",
        'done_keep': "✅ 完了 / 他の記録を残す",
        'share_telegram': "📲 Telegramで共有",
        'download_stmt_btn': "📥 明細をダウンロード",
        'manage_entries_btn': "🗑️ 支出記録を管理・削除",
        'manage_all_btn': "📋 すべての記録を見る",
        'undo_btn': "🗑️ 削除 (#{id})"
    },
    'ko': {
        'settings_country': "🌍 국가 및 통화 변경",
        'settings_lang': "🌐 언어 변경",
        'back_main': "🔙 메인 메뉴 (돌아가기)",
        'back_period': "🔙 기간 선택으로 돌아가기",
        'back_statement': "🔙 내역서 메뉴",
        'period_this_month': "📅 이번 달",
        'period_last_month': "⏮️ 지난 달",
        'period_last_30': "📆 최근 30일",
        'period_custom': "🗓️ 사용자 지정 기간",
        'vip_buy_n_mo': "💳 {months}개월 패스 구매 ({price} ⭐)",
        'vip_refer_promo': "🎁 친구 1명 초대 = 1개월 무료!",
        'btn_verify_channel': "🔄 채널 가입 확인 및 무료 혜택 재개",
        'btn_buy_vip': "💳 VIP 패스 구매 (1-12개월)",
        'btn_refer_friend': "🎁 친구 초대하기 (+1개월 무료)",
        'btn_join_channel': "📢 {title} 채널 가입",
        'download_pdf_vip': "📄 PDF 다운로드 (VIP 무료)",
        'download_excel_vip': "📊 Excel 다운로드 (VIP 무료)",
        'download_both_vip': "📦 둘 다 다운로드 (PDF + Excel)",
        'unlock_vip': "🌟 VIP 패스 이용권 (1 - 12개월)",
        'single_pdf': "📄 단일 PDF ({price} ⭐)",
        'single_excel': "📊 단일 Excel ({price} ⭐)",
        'combo_bundle': "📦 콤보 세트 ({price} ⭐)",
        'refer_offer': "🎁 친구 1명 = 1개월 무제한 무료 다운로드!",
        'change_dates': "🔙 날짜 변경",
        'done_keep': "✅ 완료 / 다른 항목 유지",
        'share_telegram': "📲 Telegram으로 공유",
        'download_stmt_btn': "📥 내역서 다운로드",
        'manage_entries_btn': "🗑️ 항목 관리 및 삭제",
        'manage_all_btn': "📋 전체 항목 보기",
        'undo_btn': "🗑️ 삭제 (#{id})"
    },
    'uk': {
        'settings_country': "🌍 Змінити країну та валюту",
        'settings_lang': "🌐 Змінити мову",
        'back_main': "🔙 Головне меню (Назад)",
        'back_period': "🔙 До вибору періоду",
        'back_statement': "🔙 Меню виписок",
        'period_this_month': "📅 Цей місяць",
        'period_last_month': "⏮️ Минулий місяць",
        'period_last_30': "📆 Останні 30 днів",
        'period_custom': "🗓️ Власний період",
        'vip_buy_n_mo': "💳 Купити підписку на {months} міс. ({price} ⭐)",
        'vip_refer_promo': "🎁 Запросити друга = 1 місяць безкоштовно!",
        'btn_verify_channel': "🔄 Перевірити підписку на канал",
        'btn_buy_vip': "💳 Купити VIP (1-12 міс.)",
        'btn_refer_friend': "🎁 Запросити друга (+1 міс.)",
        'btn_join_channel': "📢 Приєднатися до {title}",
        'download_pdf_vip': "📄 Завантажити PDF (VIP Безкоштовно)",
        'download_excel_vip': "📊 Завантажити Excel (VIP Безкоштовно)",
        'download_both_vip': "📦 Завантажити обидва (PDF + Excel)",
        'unlock_vip': "🌟 Отримати VIP доступ (1 - 12 міс.)",
        'single_pdf': "📄 Звіт PDF ({price} ⭐)",
        'single_excel': "📊 Файл Excel ({price} ⭐)",
        'combo_bundle': "📦 Комбо (PDF + Excel) ({price} ⭐)",
        'refer_offer': "🎁 1 друг = 1 місяць безліміту безкоштовно!",
        'change_dates': "🔙 Змінити дати",
        'done_keep': "✅ Готово / Залишити інші",
        'share_telegram': "📲 Поділитися в Telegram",
        'download_stmt_btn': "📥 Завантажити виписку",
        'manage_entries_btn': "🗑️ Керування записами",
        'manage_all_btn': "📋 Всі записи",
        'undo_btn': "🗑️ Видалити (#{id})"
    },
    'uz': {
        'settings_country': "🌍 Mamlakat va valyutani oʻzgartirish",
        'settings_lang': "🌐 Tilni oʻzgartirish",
        'back_main': "🔙 Asosiy menyu (Orqaga)",
        'back_period': "🔙 Muddat tanlashga qaytish",
        'back_statement': "🔙 Hisobotlar menyusi",
        'period_this_month': "📅 Shu oy",
        'period_last_month': "⏮️ Oʻtgan oy",
        'period_last_30': "📆 Oxirgi 30 kun",
        'period_custom': "🗓️ Boshqa muddat",
        'vip_buy_n_mo': "💳 {months} oylik obuna olish ({price} ⭐)",
        'vip_refer_promo': "🎁 Doʻstni taklif qiling = 1 oy bepul!",
        'btn_verify_channel': "🔄 Kanalga aʼzolikni tekshirish",
        'btn_buy_vip': "💳 VIP obuna (1-12 oy)",
        'btn_refer_friend': "🎁 Doʻstni taklif qilish (+1 oy)",
        'btn_join_channel': "📢 {title} kanaliga qoʻshilish",
        'download_pdf_vip': "📄 PDF yuklab olish (VIP Bepul)",
        'download_excel_vip': "📊 Excel yuklab olish (VIP Bepul)",
        'download_both_vip': "📦 Ikkalasini yuklash (PDF + Excel)",
        'unlock_vip': "🌟 VIP obunani faollashtirish (1 - 12 oy)",
        'single_pdf': "📄 Alohida PDF ({price} ⭐)",
        'single_excel': "📊 Alohida Excel ({price} ⭐)",
        'combo_bundle': "📦 Kombo toʻplam ({price} ⭐)",
        'refer_offer': "🎁 1 doʻst = 1 oy cheksiz bepul yuklash!",
        'change_dates': "🔙 Sanani oʻzgartirish",
        'done_keep': "✅ Tayyor / Boshqalarini saqlash",
        'share_telegram': "📲 Telegramda ulashish",
        'download_stmt_btn': "📥 Hisobotni yuklash",
        'manage_entries_btn': "🗑️ Yozuvlarni boshqarish",
        'manage_all_btn': "📋 Barcha yozuvlar",
        'undo_btn': "🗑️ Oʻchirish (#{id})"
    },
    'kk': {
        'settings_country': "🌍 Ел мен валютаны өзгерту",
        'settings_lang': "🌐 Тілді өзгерту",
        'back_main': "🔙 Басты мәзір (Артқа)",
        'back_period': "🔙 Кезеңді таңдауға оралу",
        'back_statement': "🔙 Үзінді көшірме мәзірі",
        'period_this_month': "📅 Осы ай",
        'period_last_month': "⏮️ Өткен ай",
        'period_last_30': "📆 Соңғы 30 күн",
        'period_custom': "🗓️ Басқа кезең",
        'vip_buy_n_mo': "💳 {months} айлық жазылым сатып алу ({price} ⭐)",
        'vip_refer_promo': "🎁 Досыңды шақыр = 1 ай тегін!",
        'btn_verify_channel': "🔄 Каналға тіркелуді тексеру",
        'btn_buy_vip': "💳 VIP сатып алу (1-12 ай)",
        'btn_refer_friend': "🎁 Досыңды шақыр (+1 ай)",
        'btn_join_channel': "📢 {title} каналына қосылу",
        'download_pdf_vip': "📄 PDF жүктеу (VIP Тегін)",
        'download_excel_vip': "📊 Excel жүктеу (VIP Тегін)",
        'download_both_vip': "📦 Екеуін де жүктеу (PDF + Excel)",
        'unlock_vip': "🌟 VIP жазылымды ашу (1 - 12 ай)",
        'single_pdf': "📄 Жеке PDF ({price} ⭐)",
        'single_excel': "📊 Жеке Excel ({price} ⭐)",
        'combo_bundle': "📦 Комбо топтама ({price} ⭐)",
        'refer_offer': "🎁 1 дос = 1 ай шексіз тегін жүктеу!",
        'change_dates': "🔙 Күндерді өзгерту",
        'done_keep': "✅ Дайын / Қалғандарын сақтау",
        'share_telegram': "📲 Telegram-да бөлісу",
        'download_stmt_btn': "📥 Көшірмені жүктеу",
        'manage_entries_btn': "🗑️ Жазбаларды басқару",
        'manage_all_btn': "📋 Барлық жазбаларды көру",
        'undo_btn': "🗑️ Жою (#{id})"
    }
}

def get_ui_str(key: str, lang: str = 'en', **kwargs) -> str:
    lang_dict = UI_STRINGS.get(lang, UI_STRINGS['en'])
    val = lang_dict.get(key, UI_STRINGS['en'].get(key, key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val

def get_settings_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    """Returns options to change country/currency or change language."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_ui_str('settings_country', lang), callback_data="open_country_picker")],
        [InlineKeyboardButton(get_ui_str('settings_lang', lang), callback_data="open_language_picker")],
        [InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")]
    ])


def get_all_channels_keyboard(country_code: str = 'IN', lang: str = 'en') -> InlineKeyboardMarkup:
    """Returns keyboard with join button for user's country deals channel only (no 7 channels)."""
    from .config import COUNTRY_CHANNELS
    ch_info = COUNTRY_CHANNELS.get((country_code or 'IN').upper()) or COUNTRY_CHANNELS.get("IN")
    btn_join = f"📢 {ch_info['title']} ज्वाइन करें" if lang == 'hi' else f"📢 Join {ch_info['title']}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_join, url=ch_info['channel_url'])],
        [InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")]
    ])

def get_period_select_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_ui_str('period_this_month', lang), callback_data="period_this_month"),
            InlineKeyboardButton(get_ui_str('period_last_month', lang), callback_data="period_last_month")
        ],
        [
            InlineKeyboardButton(get_ui_str('period_last_30', lang), callback_data="period_last_30"),
            InlineKeyboardButton(get_ui_str('period_custom', lang), callback_data="period_custom")
        ],
        [
            InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")
        ]
    ])

def get_vip_pass_keyboard(selected_months: int = 1, lang: str = 'en', channel_claimable: bool = False, country_code: str = 'IN') -> InlineKeyboardMarkup:
    """Renders keyboard allowing user to select and purchase 1 to 12 months VIP Pass."""
    selected_months = max(1, min(12, int(selected_months)))
    price = get_stars_price_for_months(selected_months)

    rows = [
        # Shortcut presets
        [
            InlineKeyboardButton("1 Mo (25 ⭐)", callback_data="vip_mo_set_1"),
            InlineKeyboardButton("3 Mo (70 ⭐)", callback_data="vip_mo_set_3"),
            InlineKeyboardButton("6 Mo (130 ⭐)", callback_data="vip_mo_set_6"),
            InlineKeyboardButton("12 Mo (240 ⭐)", callback_data="vip_mo_set_12"),
        ],
        # Stepper row: ➖ | Months | ➕
        [
            InlineKeyboardButton("➖ 1 Mo", callback_data=f"vip_mo_set_{max(1, selected_months - 1)}"),
            InlineKeyboardButton(f"📅 {selected_months} Mo ({price} ⭐)", callback_data="vip_mo_noop"),
            InlineKeyboardButton("➕ 1 Mo", callback_data=f"vip_mo_set_{min(12, selected_months + 1)}")
        ],
        # Buy button for selected months
        [
            InlineKeyboardButton(
                get_ui_str('vip_buy_n_mo', lang, months=selected_months, price=price),
                callback_data=f"vip_buy_{selected_months}"
            )
        ],
    ]

    # Show channel free pass button ONLY UNTIL CLAIMED!
    if channel_claimable:
        from .config import COUNTRY_CHANNELS
        c_code = (country_code or 'IN').upper()
        ch_info = COUNTRY_CHANNELS.get(c_code) or COUNTRY_CHANNELS.get("IN")
        btn_ch_vip = f"🎁 {ch_info['name']} चैनल ज्वाइन कर 1 महीना मुफ़्त लें" if lang == 'hi' else f"🎁 Join {ch_info['name']} Channel for 1 Mo Free VIP"
        rows.append([
            InlineKeyboardButton(btn_ch_vip, callback_data="open_referral")
        ])

    # Free referral option
    rows.append([
        InlineKeyboardButton(
            get_ui_str('vip_refer_promo', lang),
            callback_data="open_referral"
        )
    ])
    rows.append([
        InlineKeyboardButton(get_ui_str('back_statement', lang), callback_data="open_statement"),
        InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(rows)

def get_channel_join_keyboard(country_code: str = 'IN', lang: str = 'en') -> InlineKeyboardMarkup:
    """Returns join & verify keyboard for special countries during Month 2."""
    from .config import COUNTRY_CHANNELS
    ch_info = COUNTRY_CHANNELS.get(country_code.upper(), COUNTRY_CHANNELS.get("IN"))
    ch_title = ch_info.get("title", "Official Deals Channel")
    ch_url = ch_info.get("channel_url", "https://t.me/DealsFetcher")

    btn_join = get_ui_str('btn_join_channel', lang, title=ch_title)
    btn_verify = get_ui_str('btn_verify_channel', lang)
    btn_buy = get_ui_str('btn_buy_vip', lang)
    btn_refer = get_ui_str('btn_refer_friend', lang)
    btn_back = get_ui_str('back_main', lang)

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_join, url=ch_url)],
        [InlineKeyboardButton(btn_verify, callback_data="verify_channel")],
        [InlineKeyboardButton(btn_buy, callback_data="open_vip_menu")],
        [InlineKeyboardButton(btn_refer, callback_data="open_referral")],
        [InlineKeyboardButton(btn_back, callback_data="back_to_main")]
    ])

def get_format_select_keyboard(start_date: str, end_date: str, lang: str = 'en', is_vip: bool = False, is_channel_paused: bool = False, country_code: str = 'IN') -> InlineKeyboardMarkup:
    rows = []

    if is_vip:
        vip_pdf_cb = f"vip_pdf_{start_date}_{end_date}"
        vip_excel_cb = f"vip_excel_{start_date}_{end_date}"
        vip_both_cb = f"vip_both_{start_date}_{end_date}"

        rows.append([
            InlineKeyboardButton(get_ui_str('download_pdf_vip', lang), callback_data=vip_pdf_cb),
            InlineKeyboardButton(get_ui_str('download_excel_vip', lang), callback_data=vip_excel_cb)
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('download_both_vip', lang), callback_data=vip_both_cb)
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('change_dates', lang), callback_data="period_back"),
            InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")
        ])
    elif is_channel_paused:
        from .config import COUNTRY_CHANNELS
        ch_info = COUNTRY_CHANNELS.get(country_code.upper(), COUNTRY_CHANNELS.get("IN"))
        rows.append([
            InlineKeyboardButton(get_ui_str('btn_join_channel', lang, title=ch_info['title']), url=ch_info['channel_url'])
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('btn_verify_channel', lang), callback_data="verify_channel")
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('btn_buy_vip', lang), callback_data="open_vip_menu")
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('change_dates', lang), callback_data="period_back"),
            InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")
        ])
    else:
        pdf_cb = f"buy_pdf_{start_date}_{end_date}"
        excel_cb = f"buy_excel_{start_date}_{end_date}"
        both_cb = f"buy_both_{start_date}_{end_date}"

        rows.append([
            InlineKeyboardButton(
                get_ui_str('unlock_vip', lang),
                callback_data="open_vip_menu"
            )
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('single_pdf', lang, price=STARS_PDF_PRICE), callback_data=pdf_cb),
            InlineKeyboardButton(get_ui_str('single_excel', lang, price=STARS_EXCEL_PRICE), callback_data=excel_cb)
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('combo_bundle', lang, price=STARS_BUNDLE_PRICE), callback_data=both_cb)
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('refer_offer', lang), callback_data="open_referral")
        ])
        rows.append([
            InlineKeyboardButton(get_ui_str('change_dates', lang), callback_data="period_back"),
            InlineKeyboardButton(get_ui_str('back_main', lang), callback_data="back_to_main")
        ])

    return InlineKeyboardMarkup(rows)

def get_entries_management_keyboard(entries: list, lang: str = 'en', currency: str = '$') -> InlineKeyboardMarkup:
    keyboard_rows = []

    for tx in entries:
        tx_id = tx['id']
        amount = tx['amount']
        category = tx['category']
        note = tx.get('note', '') or ''
        is_inc = (tx.get('type') == 'income')

        sign = "+" if is_inc else "-"
        note_snippet = f" ({note[:10]})" if note else ""
        btn_text = f"❌ [#{tx_id}] {sign}{currency}{amount:,.0f} {category}{note_snippet}"

        keyboard_rows.append([
            InlineKeyboardButton(btn_text, callback_data=f"del_tx_{tx_id}")
        ])

    close_label = get_ui_str('done_keep', lang)
    back_label = get_ui_str('back_main', lang)

    keyboard_rows.append([
        InlineKeyboardButton(close_label, callback_data="del_done"),
        InlineKeyboardButton(back_label, callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(keyboard_rows)

def get_referral_inline_keyboard(
    ref_url: str,
    country_code: str = 'IN',
    lang: str = 'en',
    already_claimed: bool = False,
    channel_share_url: str = None,
    shares_count: int = 0,
    share_reward_claimed: bool = False
) -> InlineKeyboardMarkup:
    from .config import COUNTRY_CHANNELS
    c_code = (country_code or 'IN').upper()
    has_ch = c_code in COUNTRY_CHANNELS
    ch_info = COUNTRY_CHANNELS.get(c_code) or COUNTRY_CHANNELS.get("IN")

    share_text = (
        "I track all my daily expenses effortlessly with Hisab-Kitab Bot! Join here to track your expenses in 1 click: "
    )
    if lang == 'hi':
        share_text = "Main Hisab-Kitab Bot par apna roz ka kharcha track karta hu! 1 click me hisab ban jata hai. Aap bhi use karein: "
    elif lang == 'bn':
        share_text = "আমি Hisab-Kitab Bot দিয়ে প্রতিদিনের খরচ ট্র্যাক করি! এক ক্লিকে হিসাব তৈরি হয়: "
    elif lang == 'ur':
        share_text = "میں اپنے روزمرہ کے اخراجات Hisab-Kitab Bot سے ٹریک کرتا ہوں! آپ بھی جوائن کریں: "
    elif lang == 'ru':
        share_text = "Я веду учет своих ежедневных расходов с помощью Hisab-Kitab Bot! Попробуй и ты: "
    elif lang == 'es':
        share_text = "¡Llevo el control de mis gastos diarios con Hisab-Kitab Bot! Pruébalo gratis aquí: "
    elif lang == 'pt':
        share_text = "Controlo meus gastos diários com o Hisab-Kitab Bot! Experimente grátis aqui: "
    elif lang == 'ar':
        share_text = "أنا أتابع جميع مصاريفي اليومية بسهولة مع Hisab-Kitab Bot! جربه الآن: "
    elif lang == 'id':
        share_text = "Saya mencatat pengeluaran harian dengan mudah di Hisab-Kitab Bot! Yuk coba juga: "

    telegram_share_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_url)}&text={urllib.parse.quote(share_text)}"

    btn_download = get_ui_str('download_stmt_btn', lang)
    btn_back = get_ui_str('back_main', lang)
    rows = []

    if has_ch:
        btn_join = f"📢 {ch_info['title']} ज्वाइन करें" if lang == 'hi' else f"📢 Join {ch_info['title']}"
        rows.append([InlineKeyboardButton(btn_join, url=ch_info['channel_url'])])

        # SHOW CLAIM BUTTON ONLY UNTIL CLAIMED!
        if not already_claimed:
            btn_claim = "🎁 2 महीने मुफ़्त VIP पास एक्टिव करें" if lang == 'hi' else "🎁 Claim 2 Months Free VIP Pass"
            rows.append([InlineKeyboardButton(btn_claim, callback_data=f"claim_channel_free_pass_{c_code}")])

        # 10-Friends Shopping Channel Share button (shares the official shopping channel URL of this country!)
        ch_target_url = ch_info['channel_url']
        ch_share_caption = (
            f"🛍️ {ch_info['title']} — आपके देश का आधिकारिक शॉपिंग और लूट डील्स चैनल!\n\n"
            f"🔥 रोज़ाना 90% तक डिस्काउंट्स, लूट डील्स और ऑनलाइन शॉपिंग ऑफर्स!\n\n"
            f"👉 चैनल ज्वाइन करने के लिए यहाँ क्लिक करें: {ch_target_url}"
            if lang == 'hi' else
            f"🛍️ {ch_info['title']} — Official Shopping & Deals Telegram Channel!\n\n"
            f"🔥 Daily up to 90% discounts, loot drops and top shopping savings!\n\n"
            f"👉 Tap to join: {ch_target_url}"
        )
        tg_ch_share = f"https://t.me/share/url?url={urllib.parse.quote(ch_target_url)}&text={urllib.parse.quote(ch_share_caption)}"
        btn_cshare = f"🛍️ 10 दोस्तों को शॉपिंग चैनल शेयर करें (+1 Mo)" if lang == 'hi' else f"🛍️ Share {ch_info['name']} Shopping Channel (10 Friends = +1 Mo)"
        rows.append([InlineKeyboardButton(btn_cshare, url=tg_ch_share)])

        # SHOW OFFER 2 CLAIM BUTTON ONLY UNTIL CLAIMED!
        if not share_reward_claimed:
            btn_claim_share = "🎁 10 दोस्तों को शेयर किया? +1 महीना VIP क्लेम करें" if lang == 'hi' else "🎁 Claim +1 Mo Free VIP (10 Friends Shared)"
            rows.append([InlineKeyboardButton(btn_claim_share, callback_data=f"claim_share_reward_{c_code}")])

    # Bot referral share button
    btn_share_bot = "📤 दोस्तों को बॉट शेयर करें" if lang == 'hi' else "📤 Share Bot with Friends"
    rows.append([InlineKeyboardButton(btn_share_bot, url=telegram_share_url)])

    # Statement & Back
    rows.append([
        InlineKeyboardButton(btn_download, callback_data="open_statement"),
        InlineKeyboardButton(btn_back, callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(rows)

FIRST_TIME_COUNTRY_PROMPT = """🌍 <b>Welcome to Hisab-Kitab Bot! 💰</b>
<i>Your personal global finance & expense tracker bot.</i>

To get started, please select your <b>Country / Region</b>:
• Your daily accounts and statements will be recorded in your <b>local currency</b>.
• You can choose your native language right after.

👇 <b>Choose your country from the list below:</b>"""

FIRST_TIME_LANG_PROMPT = """🌐 <b>Select Your Preferred Language:</b>
Default is English. You can switch to your country's native language or any global language below:"""

MESSAGES = {
    'en': {
        'welcome': """👋 <b>Hello {name}! Welcome to Hisab-Kitab Bot 💰</b>

Tracking your daily expenses and income is now instant and hassle-free! No clunky apps or physical registers needed.

<b>Just type naturally in chat:</b>
👉 <code>Coffee 50</code>
👉 <code>Fuel 200</code>
👉 <code>Groceries 850</code>
👉 <code>Internet 499</code>
👉 <code>+50000 Salary</code> (To record income)

I automatically categorize transactions and provide a nightly recap at 9:00 PM! 📊

<i>🌍 Currency: <b>{currency}</b> | Country: <b>{country}</b></i>
<i>🎁 Refer 1 friend to unlock <b>1 Full Month of Unlimited Free Downloads</b>!</i>
<i>📥 Download reports in PDF & Excel (.xlsx) for any custom date range!</i>
🌐 <i>To change Country or Language anytime, use /country or /language.</i>""",

        'help': """📖 <b>Hisab-Kitab Bot Guide & Commands:</b>

<b>How to log expenses & income:</b>
• <code>Coffee 50</code> ➔ Added {currency}50 to Food
• <code>Fuel 200</code> ➔ Added {currency}200 to Travel
• <code>Groceries 450</code> ➔ Added {currency}450 to Grocery
• <code>Movie 300</code> ➔ Added {currency}300 to Entertainment
• <code>+50000 Salary</code> ➔ Added {currency}50,000 to Income

<b>Commands:</b>
/today - View today's itemized expenses (with IDs)
/month - View this month's category summary & savings
/budget - Set or view your monthly spending limit
/country - Change your country & currency 🌍
/language - Change your display language 🌐
/delete - Selectively choose which entry to keep or delete (Undo)
/refer - Invite friends and unlock 1 Full Month of Unlimited Free Downloads 🎁
/statement - Download financial statement with custom date range
/excel - Instant download for Excel (.xlsx) spreadsheet
/pdf - Instant download for official PDF statement
/help - View this guide anytime""",

        'language_prompt': "🌐 <b>Choose your preferred language:</b>",
        'language_changed': "✅ Language updated successfully! All messages and menus are now localized.",
        'country_prompt': "🌍 <b>Select your Country & Currency:</b>",
        'country_changed': "✅ Country and currency updated to <b>{country} ({currency})</b>!",

        'manage_entries_title': """🗑️ <b>Manage & Undo Entries:</b>

Here are your recent entries. Tap <b>[❌]</b> on any entry you wish to delete/undo. All other entries will remain safe:""",

        'entry_deleted': "🗑️ <b>Entry #{tx_id} deleted:</b> {currency}{amount:,.0f} ({category})",
        'all_entries_safe': "✅ <b>All other entries remain saved!</b>",

        'referral_card_active': """🌟 <b>Your 1 Month Unlimited Free VIP Pass is Active!</b> 🎁

• Status: <b>VIP Active ✅</b>
• Expiry Date: <b>{expires_at}</b> ({days_left} days left)
• Friends Invited: <b>{total_referred}</b>
• Download Limit: <b>Unlimited (Download as many PDF & Excel files as you want)</b>

💡 <i>Invite 1 more friend to extend by <b>+1 Month (+30 Days)</b>!</i>

🔗 <b>Your Personal Referral Link:</b>
<code>{ref_url}</code>

<i>Tap the button below to share with friends and groups 👇</i>""",

        'referral_card_inactive': """🎁 <b>Refer Friends & Unlock 1 Month of Unlimited Free Downloads!</b>

Invite just <b>1 friend</b> to Hisab-Kitab Bot to unlock a <b>Full 1-Month (+30 Days) Free VIP Pass</b>!
During the free month, you can download unlimited PDF & Excel statements anytime for 100% free.

📊 <b>Your Referral Status:</b>
• Friends Invited: <b>{total_referred}</b>
• VIP Pass Status: <b>Inactive (Activates as soon as 1 friend joins)</b>

🔗 <b>Your Personal Referral Link:</b>
<code>{ref_url}</code>

<i>Tap the button below to share with friends and groups 👇</i>""",

        'referral_reward_notice': """🎉 <b>Congratulations! Your friend just joined Hisab-Kitab Bot!</b> 🎁

You have unlocked <b>1 Full Month (+30 Days) of Unlimited Free Statement Downloads</b>!
You can now download as many PDF & Excel statements as you want for 100% free until <b>{expires_at}</b>!

👉 Type /statement to download anytime!""",

        'vip_download_msg': "🌟 <b>VIP Free Download Ready!</b>\nYour statement for {period_label} is being generated and attached below:",

        'month_2_paused_msg': """⏸️ <b>2nd Month Free Access is Paused!</b> 📢

To enjoy free statement downloads in Month 2 for {country}, you must stay joined in our official deals channel:
👉 <b>{channel_title}</b> ({channel_username})

⚠️ <i>If you leave the channel, your 2nd month free access is paused. Re-join anytime to instantly resume your 30-day free access!</i>

Tap below to join the channel, then tap Verify 👇""",

        'channel_verified_success': """🎉 <b>Channel Membership Verified!</b> 📢
Your <b>2nd Month Free Access</b> is now active! You can download unlimited PDF & Excel statements until <b>{expires_at}</b>.""",

        'channel_not_joined_alert': "❌ You have not joined {channel_username} yet! Please join the channel first, then tap Verify.",

        'vip_pass_selector_prompt': """🌟 <b>Hisab-Kitab VIP Pass (1 to 12 Months Unlimited)</b> 💳

Choose your desired duration (1 to 12 Months):
• <b>1 Month</b>: 25 ⭐
• <b>3 Months</b>: 70 ⭐ (Save 5 ⭐)
• <b>6 Months</b>: 130 ⭐ (Save 20 ⭐)
• <b>12 Months</b>: 240 ⭐ (Best Value — Save 60 ⭐ / Only 20 ⭐/mo!)

📅 <b>Selected Duration:</b> {selected_months} Month(s) ({price} ⭐)
<i>(Unlimited PDF & Excel statements for any date range with 0 extra stars)</i>""",

        'vip_purchased_notice': """🎉 <b>Congratulations! {months} Month(s) VIP Pass Activated!</b> 🌟
Your pass is active until <b>{expires_at}</b>. Enjoy unlimited PDF & Excel statement downloads anytime!""",

        'period_prompt': """📅 <b>Select Statement Date Range:</b>

For which date range would you like to download your statement? Choose an option below or specify custom dates 👇""",

        'custom_date_prompt': """🗓️ <b>Enter Custom Date Range:</b>

Please send the date range in chat like this:
👉 <code>DD-MM-YYYY to DD-MM-YYYY</code>

<b>Examples:</b>
👉 <code>01-08-2026 to 15-09-2026</code>
👉 <code>01/09/2026 to 20/09/2026</code>
👉 <code>10-09-2026 to 20-09-2026</code>""",

        'custom_date_invalid': """❌ <b>Invalid date range format!</b>

Please format as:
👉 <code>01-08-2026 to 15-09-2026</code>
(DD-MM-YYYY to DD-MM-YYYY)""",

        'format_select_prompt_vip': """🌟 <b>VIP Free Pass Active! ({days_left} days left)</b>

You can download unlimited PDF and Excel files for 100% free (0 Stars):
• 📄 <b>PDF Report</b>: Print & share ready
• 📊 <b>Excel Sheet (.xlsx)</b>: Full formulas and data log
• 📦 <b>Combo Bundle</b>: Both files together

Choose your download option below 👇""",

        'format_select_prompt_regular': """📄 <b>Select Statement Format ({period_label})</b>

You can download single PDF, single Excel, or both as a combo pack:
• <b>📄 Single PDF ({pdf_price} ⭐)</b>: Official verified print & share ready report
• <b>📊 Single Excel ({excel_price} ⭐)</b>: Full spreadsheet (.xlsx) with formulas and data log
• <b>📦 Combo Bundle ({bundle_price} ⭐)</b>: Both PDF + Excel (Value Saver Pack!)

💡 <i>Refer just 1 friend and get <b>1 Full Month of Unlimited Free Downloads</b>!</i>

Choose your option below 👇""",

        'today_empty': "ℹ️ <b>No expenses recorded yet today!</b>\n\nTo log an expense, simply type: <code>Coffee 50</code> or <code>Fuel 200</code>",
        'undo_empty': "ℹ️ No recent transaction found to delete.",
        'undo_success': "🗑️ <b>Entry deleted:</b> {currency}{amount:,.0f} ({category})\n📊 Updated Today's Total: <b>{currency}{today_total:,.0f}</b>",

        'budget_prompt': """💰 <b>Set Your Monthly Budget:</b>

To set your monthly budget limit, type:
👉 <code>/budget 15000</code>
or simply send:
👉 <code>Budget 15000</code>

The bot will proactively alert you as you approach your spending limit! 🔔""",
        'budget_set': "✅ Your monthly budget has been set to <b>{currency}{val:,.0f}</b>!",

        'expense_added_title': "✅ <b>{currency}{amount:,.0f} spent!</b> ({category})",
        'income_added_title': "✅ <b>Income Added!</b> 💰",

        'unknown_input': """🤔 <b>Could not understand!</b> To log an expense, just type the item and amount:
👉 <code>Coffee 50</code>
👉 <code>Fuel 200</code>
👉 <code>Groceries 500</code>

Or type /help for commands!"""
    },

    'hi': {
        'welcome': """👋 <b>नमस्ते {name}! मैं हूँ Hisab-Kitab Bot 💰</b>

रोज़ का खर्चा लिखना अब सबसे आसान है! डायरी या भारी ऐप्स की कोई ज़रूरत नहीं।

<b>बस चैट में टाइप करें:</b>
👉 <code>Chai 20</code>
👉 <code>Petrol 150</code>
👉 <code>Ration 850</code>
👉 <code>Recharge 299</code>
👉 <code>+50000 Salary</code> (कमाई लिखने के लिए)

मैं अपने आप सही केटेगरी बना लूँगा और रोज़ रात 9 बजे पूरा हिसाब दूँगा! 📊

<i>🌍 करेंसी: <b>{currency}</b> | देश: <b>{country}</b></i>
<i>🎁 1 दोस्त को रेफर करने पर पाएँ <b>पूरे 1 महीने तक Unlimited Free Downloads</b>!</i>
<i>📥 अपनी पसंद की तारीख (Date Range) का PDF और Excel दोनों डाउनलोड कर सकते हैं!</i>
🌐 <i>करेंसी या भाषा बदलने के लिए <b>'🌐 भाषा / देश बदलें'</b> बटन दबाएं या /country या /language टाइप करें।</i>""",

        'help': """📖 <b>Hisab-Kitab Bot गाइड और कमांड्स:</b>

<b>खर्चा कैसे लिखें:</b>
• <code>Chai 20</code> ➔ Food में {currency}20 ऐड होगा
• <code>Petrol 200</code> ➔ Travel में {currency}200 ऐड होगा
• <code>Dukan 450</code> ➔ Grocery में {currency}450 ऐड होगा
• <code>Movie 300</code> ➔ Entertainment में {currency}300 ऐड होगा
• <code>+50000 Salary</code> ➔ Income में {currency}50,000 ऐड होगा

<b>कमांड्स:</b>
/today - आज का खर्चा देखें (ID के साथ)
/month - इस महीने का केटेगरी-वाइज़ हिसाब
/budget - मंथली बजट सेट करें
/country - अपना देश और लोकल करेंसी बदलें 🌍
/language - भाषा बदलें (Hindi, English, etc.) 🌐
/delete - किसी भी पुरानी एंट्री को चुनकर हटाएं (Undo)
/refer - दोस्तों को इनवाइट करें और 1 महीने के लिए Unlimited Free Downloads पाएँ 🎁
/statement - मनपसंद तारीख का PDF या Excel स्टेटमेंट डाउनलोड करें
/excel - तुरंत Excel (.xlsx) फाइल डाउनलोड करें
/pdf - PDF रिपोर्ट डाउनलोड करें
/help - यह गाइड दोबारा देखें""",

        'language_prompt': "🌐 <b>अपनी पसंदीदा भाषा चुनें (Choose Language):</b>",
        'language_changed': "✅ भाषा सफलतापूर्वक बदल दी गई है! अब सभी संदेश और कीबोर्ड अपडेट हो गए हैं।",
        'country_prompt': "🌍 <b>अपना देश और करेंसी चुनें (Select Country & Currency):</b>",
        'country_changed': "✅ देश और करेंसी सफलतापूर्वक <b>{country} ({currency})</b> पर सेट कर दी गई है!",

        'manage_entries_title': """🗑️ <b>एंट्री हटाएं या रखें (Manage & Undo Entries):</b>

नीचे आपकी हालिया एंट्रियां दी गई हैं। आप जिस एंट्री को हटाना चाहते हैं, उसके बटन <b>[❌]</b> पर टैप करें। बाकी सभी एंट्रियां सुरक्षित रहेंगी 👇""",

        'entry_deleted': "🗑️ <b>एंट्री #{tx_id} हटा दी गई:</b> {currency}{amount:,.0f} ({category})",
        'all_entries_safe': "✅ <b>बाकी सभी एंट्रियां सुरक्षित हैं!</b>",

        'referral_card_active': """🌟 <b>आपका 1 Month Unlimited Free VIP Pass एक्टिव है!</b> 🎁

• स्टेटस: <b>VIP Active ✅</b>
• एक्सपायरी डेट: <b>{expires_at}</b> ({days_left} दिन बाकी)
• कुल इनवाइट किए गए दोस्त: <b>{total_referred}</b>
• डाउनलोड लिमिट: <b>अनलिमिटेड (जितनी मर्ज़ी उतनी बार PDF व Excel डाउनलोड करें)</b>

💡 <i>हर 1 और दोस्त को रेफर करने पर <b>+1 महीना (+30 दिन)</b> और बढ़ जाएगा!</i>

🔗 <b>आपका पर्सनल रेफरल लिंक:</b>
<code>{ref_url}</code>

<i>नीचे दिए गए बटन से अपने दोस्तों और ग्रुप्स में शेयर करें 👇</i>""",

        'referral_card_inactive': """🎁 <b>दोस्तों को रेफर करें और पूरे 1 महीने के लिए Unlimited Free Downloads पाएँ!</b>

सिर्फ <b>1 दोस्त</b> को Hisab-Kitab Bot जॉइन कराते ही आपको मिलेगा <b>पूरे 1 महीने (+30 दिन) का Free VIP Pass</b>!
उस पूरे महीने में आप जितनी मर्ज़ी उतनी PDF व Excel फाइल्स कभी भी मुफ्त डाउनलोड कर सकते हैं।

📊 <b>आपकी रेफरल रिपोर्ट:</b>
• कुल इनवाइट किए गए दोस्त: <b>{total_referred}</b>
• VIP पास स्टेटस: <b>इनएक्टिव (1 दोस्त को जोड़ते ही एक्टिव हो जाएगा)</b>

🔗 <b>आपका पर्सनल रेफरल लिंक:</b>
<code>{ref_url}</code>

<i>नीचे दिए गए बटन से अपने दोस्तों और ग्रुप्स में शेयर करें 👇</i>""",

        'referral_reward_notice': """🎉 <b>बधाई हो! आपके दोस्त ने Hisab-Kitab Bot जॉइन किया है!</b> 🎁

आपको मिला है <b>पूरे 1 महीने (+30 दिन) का Unlimited Free Statement Pass</b>!
अब आप <b>{expires_at}</b> तक कभी भी कितनी भी PDF व Excel फाइल्स बिल्कुल मुफ्त डाउनलोड कर सकते हैं!

👉 अभी डाउनलोड करने के लिए /statement दबाएं!""",

        'vip_download_msg': "🌟 <b>VIP Free Download Ready!</b>\nआपका {period_label} का स्टेटमेंट तैयार करके नीचे भेजा जा रहा है:",

        'month_2_paused_msg': """⏸️ <b>2nd Month Free Access रुका हुआ है!</b> 📢

आपके देश ({country}) के लिए 2nd Month में फ्री स्टेटमेंट डाउनलोड्स पाने के लिए आपको हमारे ऑफिशियल डील्स चैनल से जुड़े रहना आवश्यक है:
👉 <b>{channel_title}</b> ({channel_username})

⚠️ <i>यदि आप चैनल छोड़ देते हैं तो 2nd Month का फ्री एक्सेस रुक जाता है। जैसे ही आप दोबारा जॉइन करेंगे, आपका 30 दिन का फ्री एक्सेस फिर से चालू हो जाएगा!</i>

नीचे दिए गए बटन से चैनल जॉइन करें और 'वेरिफाई करें' दबाएं 👇""",

        'channel_verified_success': """🎉 <b>चैनल सदस्यता वेरिफाई हो गई!</b> 📢
आपका <b>2nd Month Free Access</b> सक्रिय हो गया है! अब आप <b>{expires_at}</b> तक सभी PDF व Excel फाइल्स बिल्कुल मुफ्त डाउनलोड कर सकते हैं।""",

        'channel_not_joined_alert': "❌ आप अभी {channel_username} चैनल में नहीं जुड़े हैं! कृपया पहले चैनल जॉइन करें और फिर वेरिफाई करें।",

        'vip_pass_selector_prompt': """🌟 <b>Hisab-Kitab VIP पास (1 से 12 महीने अनलिमिटेड)</b> 💳

अपनी पसंद की अवधि चुनें (1 से 12 महीने):
• <b>1 महीना</b>: 25 ⭐
• <b>3 महीने</b>: 70 ⭐ (5 स्टार्स बचत!)
• <b>6 महीने</b>: 130 ⭐ (20 स्टार्स बचत!)
• <b>12 महीने</b>: 240 ⭐ (60 स्टार्स बचत — केवल 20 ⭐/महीना!)

📅 <b>चुनी गई अवधि:</b> {selected_months} महीना ({price} ⭐)
<i>(इस अवधि में जितने मर्जी उतने PDF और Excel स्टेटमेंट्स कभी भी मुफ्त डाउनलोड करें)</i>""",

        'vip_purchased_notice': """🎉 <b>बधाई हो! {months} महीने का VIP पास एक्टिव हो गया है!</b> 🌟
आपका पास <b>{expires_at}</b> तक एक्टिव रहेगा। अब आप किसी भी तारीख का PDF व Excel स्टेटमेंट अनलिमिटेड बार डाउनलोड कर सकते हैं!""",

        'period_prompt': """📅 <b>स्टेटमेंट का समय (Date Range) चुनें:</b>

आप किस तारीख से किस तारीख तक का स्टेटमेंट डाउनलोड करना चाहते हैं? नीचे से विकल्प चुनें या अपनी मर्ज़ी की तारीख डालें 👇""",

        'custom_date_prompt': """🗓️ <b>कस्टम तारीख (Date Range) डालें:</b>

कृपया चैट में तारीख इस फॉर्मेट में लिखकर भेजें:
👉 <code>DD-MM-YYYY to DD-MM-YYYY</code>

<b>उदाहरण (Examples):</b>
👉 <code>01-08-2026 to 15-09-2026</code>
👉 <code>01/09/2026 to 20/09/2026</code>
👉 <code>10-09-2026 to 20-09-2026</code>""",

        'custom_date_invalid': """❌ <b>तारीख का फॉर्मेट सही नहीं है!</b>

कृपया इस तरह लिखें:
👉 <code>01-08-2026 to 15-09-2026</code>
(तारीख-महीना-साल से तारीख-महीना-साल)""",

        'format_select_prompt_vip': """🌟 <b>VIP Free Pass एक्टिव है! ({days_left} दिन बाकी)</b>

आप इस महीने जितनी बार चाहें उतनी बार PDF व Excel फाइल्स बिल्कुल मुफ्त (0 Stars) डाउनलोड कर सकते हैं:
• 📄 <b>PDF रिपोर्ट</b>: प्रिंट व शेयर रेडी
• 📊 <b>Excel स्प्रेडशीट (.xlsx)</b>: फुल फॉर्मूलों और डेटा शीट के साथ
• 📦 <b>कॉम्बो पैक</b>: PDF + Excel दोनों एक साथ

नीचे से अपना विकल्प चुनें 👇""",

        'format_select_prompt_regular': """📄 <b>स्टेटमेंट फॉर्मेट चुनें ({period_label})</b>

आप सिंगल PDF, सिंगल Excel या दोनों का कॉम्बो पैक डाउनलोड कर सकते हैं:
• <b>📄 सिंगल PDF ({pdf_price} ⭐)</b>: ऑफिशियल प्रिंट/शेयर रेडी रिपोर्ट
• <b>📊 सिंगल Excel ({excel_price} ⭐)</b>: पूरी स्प्रेडशीट (.xlsx) फॉर्मूलों और ट्रांजेक्शन लॉग के साथ
• <b>📦 कॉम्बो पैक ({bundle_price} ⭐)</b>: PDF + Excel दोनों एक साथ (बचत ऑफर!)

💡 <i>सिर्फ 1 दोस्त को रेफर करें और <b>पूरे 1 महीने तक अनलिमिटेड फ्री डाउनलोड्स</b> पाएँ!</i>

नीचे से अपना विकल्प चुनें 👇""",

        'today_empty': "ℹ️ <b>आज अभी तक कोई खर्चा दर्ज नहीं हुआ है!</b>\n\nलिखने के लिए बस टाइप करें: <code>Chai 20</code> या <code>Petrol 100</code>",
        'undo_empty': "ℹ️ कोई ट्रांजेक्शन डिलीट करने के लिए नहीं मिला।",
        'undo_success': "🗑️ <b>एंट्री डिलीट हो गई:</b> {currency}{amount:,.0f} ({category})\n📊 आज का अपडेटेड टोटल: <b>{currency}{today_total:,.0f}</b>",

        'budget_prompt': """💰 <b>Monthly Budget Set Karein:</b>

Apna monthly budget set karne ke liye aise likhein:
👉 <code>/budget 15000</code>
ya chat me bas likhein:
👉 <code>Budget 15000</code>

Jab aapka kharcha budget ke kareeb aayega, bot aapko alert karega! 🔔""",
        'budget_set': "✅ आपका मंथली बजट <b>{currency}{val:,.0f}</b> सेट हो गया!",

        'expense_added_title': "✅ <b>{currency}{amount:,.0f} खर्च हुआ!</b> ({category})",
        'income_added_title': "✅ <b>कमाई जुड़ गई!</b> 💰",

        'unknown_input': """🤔 <b>समझ नहीं आया!</b> खर्चा लिखने के लिए बस राशि और नाम लिखें:
👉 <code>Chai 20</code>
👉 <code>Petrol 150</code>
👉 <code>Ration 500</code>

या मदद के लिए /help टाइप करें!"""
    },

    'bn': {
        'welcome': """👋 <b>হ্যালো {name}! Hisab-Kitab Bot-এ স্বাগতম 💰</b>

দৈনন্দিন খরচ ও আয়ের হিসাব রাখা এখন আরও সহজ!

<b>চ্যাটে সহজে লিখুন:</b>
👉 <code>চা ২০</code>
👉 <code>পেট্রোল ২০০</code>
👉 <code>বাজার ৮৫০</code>
👉 <code>+৫০০০০ বেতন</code> (আয়ের জন্য)

<i>🌍 মুদ্রা: <b>{currency}</b> | দেশ: <b>{country}</b></i>
<i>🎁 ১ জন বন্ধুকে রেফার করলে পাবেন <b>পুরো ১ মাস ফ্রি আনলিমিটেড ডাউনলোড</b>!</i>
<i>📥 যে কোনো তারিখের PDF ও Excel ফাইল ডাউনলোড করুন!</i>""",

        'help': """📖 <b>Hisab-Kitab গাইড ও কমান্ড:</b>
• <code>Coffee 50</code> ➔ খাবারে {currency}50 যোগ হবে
• <code>Petrol 200</code> ➔ যাতায়াতে {currency}200 যোগ হবে
• <code>+50000 Salary</code> ➔ আয়ে {currency}50,000 যোগ হবে

/today - আজকের হিসাব
/month - এই মাসের হিসাব
/budget - মাসিক বাজেট
/country - দেশ ও মুদ্রা পরিবর্তন 🌍
/language - ভাষা পরিবর্তন 🌐
/delete - এন্ট্রি মুছুন (Undo)
/statement - স্টেটমেন্ট ডাউনলোড (PDF/Excel)""",

        'language_prompt': "🌐 <b>আপনার পছন্দের ভাষা নির্বাচন করুন:</b>",
        'language_changed': "✅ ভাষা সফলভাবে পরিবর্তিত হয়েছে!",
        'country_prompt': "🌍 <b>আপনার দেশ ও মুদ্রা বেছে নিন:</b>",
        'country_changed': "✅ দেশ ও মুদ্রা সেট হয়েছে: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ আজ এখনো কোনো খরচ লেখা হয়নি।",
        'undo_empty': "ℹ️ মোছার মতো কোনো এন্ট্রি পাওয়া যায়নি।",
        'undo_success': "🗑️ <b>এন্ট্রি মোছা হয়েছে:</b> {currency}{amount:,.0f} ({category})\n📊 আজকের মোট: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ আপনার মাসিক বাজেট <b>{currency}{val:,.0f}</b> নির্ধারণ করা হয়েছে!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} খরচ হয়েছে!</b> ({category})",
        'income_added_title': "✅ <b>আয় যোগ করা হয়েছে!</b> 💰",
        'unknown_input': "🤔 বুঝতে পারিনি। যেমন লিখুন: <code>চা ২০</code> বা <code>পেট্রোল ২০০</code>।"
    },

    'ur': {
        'welcome': """👋 <b>ہیلو {name}! Hisab-Kitab Bot میں خوش آمدید 💰</b>

اپنے روزمرہ کے اخراجات اور آمدنی کا حساب رکھنا اب انتہائی آسان ہے!

<b>صرف چیٹ میں لکھیں:</b>
👉 <code>Chai 20</code>
👉 <code>Petrol 200</code>
👉 <code>Ration 850</code>
👉 <code>+50000 Salary</code> (آمدنی کے لیے)

<i>🌍 کرنسی: <b>{currency}</b> | ملک: <b>{country}</b></i>
<i>🎁 1 دوست کو ریفر کریں اور پائیں <b>پورے 1 ماہ کے لیے مفت لامحدود ڈاؤن لوڈز</b>!</i>""",

        'help': """📖 <b>Hisab-Kitab گائیڈ اور کمانڈز:</b>
• <code>Chai 20</code> ➔ کھانے میں {currency}20 شامل ہوگا
• <code>Petrol 200</code> ➔ سفر میں {currency}200 شامل ہوگا
• <code>+50000 Salary</code> ➔ آمدنی میں {currency}50,000 شامل ہوگا

/today - آج کا خرچہ
/month - اس ماہ کا خلاصہ
/budget - بجٹ مقرر کریں
/country - ملک اور کرنسی تبدیل کریں 🌍
/language - زبان تبدیل کریں 🌐
/delete - انٹری ڈیلیٹ کریں
/statement - اسٹیٹمنٹ ڈاؤن لوڈ کریں (PDF/Excel)""",

        'language_prompt': "🌐 <b>اپنی پسندیدہ زبان منتخب کریں:</b>",
        'language_changed': "✅ زبان کامیابی سے تبدیل کر دی گئی ہے!",
        'country_prompt': "🌍 <b>اپنا ملک اور کرنسی منتخب کریں:</b>",
        'country_changed': "✅ ملک اور کرنسی سیٹ ہو گئی: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ آج ابھی تک کوئی خرچہ درج نہیں کیا گیا۔",
        'undo_empty': "ℹ️ ڈیلیٹ کرنے کے لیے کوئی انٹری نہیں ملی۔",
        'undo_success': "🗑️ <b>انٹری ڈیلیٹ ہو گئی:</b> {currency}{amount:,.0f} ({category})\n📊 آج کا ٹوٹل: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ آپ کا ماہانہ بجٹ <b>{currency}{val:,.0f}</b> مقرر ہو گیا!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} خرچ ہوا!</b> ({category})",
        'income_added_title': "✅ <b>آمدنی شامل ہو گئی!</b> 💰",
        'unknown_input': "🤔 سمجھ نہیں آیا۔ صرف رقم اور نام لکھیں، مثلاً: <code>Chai 20</code>"
    },

    'ru': {
        'welcome': """👋 <b>Привет {name}! Добро пожаловать в Hisab-Kitab Bot 💰</b>

Учет ежедневных расходов и доходов теперь стал невероятно простым!

<b>Просто напишите в чат:</b>
👉 <code>Кофе 250</code>
👉 <code>Бензин 1500</code>
👉 <code>Продукты 850</code>
👉 <code>+50000 Зарплата</code> (для дохода)

<i>🌍 Валюта: <b>{currency}</b> | Страна: <b>{country}</b></i>
<i>🎁 Пригласите 1 друга и получите <b>1 месяц безлимитных бесплатных отчетов</b>!</i>
🌐 <i>Изменить страну или язык: /country или /language.</i>""",

        'help': """📖 <b>Справка и команды Hisab-Kitab:</b>

• <code>Кофе 250</code> ➔ {currency}250 в Еда
• <code>Бензин 1500</code> ➔ {currency}1,500 в Транспорт
• <code>+50000 Зарплата</code> ➔ {currency}50,000 в Доходы

/today - Расходы за сегодня
/month - Итоги месяца и категории
/budget - Установить бюджет
/country - Сменить страну и валюту 🌍
/language - Сменить язык 🌐
/delete - Удалить любую запись
/statement - Скачать отчет (PDF/Excel)""",

        'language_prompt': "🌐 <b>Выберите язык интерфейса:</b>",
        'language_changed': "✅ Язык успешно изменен на <b>Русский</b>!",
        'country_prompt': "🌍 <b>Выберите страну и валюту:</b>",
        'country_changed': "✅ Страна и валюта установлены: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Сегодня пока нет расходов.",
        'undo_empty': "ℹ️ Нет записей для удаления.",
        'undo_success': "🗑️ <b>Запись удалена:</b> {currency}{amount:,.0f} ({category})\n📊 Всего за сегодня: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Ваш месячный бюджет установлен: <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>Потрачено {currency}{amount:,.0f}!</b> ({category})",
        'income_added_title': "✅ <b>Доход добавлен!</b> 💰",
        'unknown_input': "🤔 Не удалось распознать запись. Напишите, например: <code>Кофе 250</code>."
    },

    'es': {
        'welcome': """👋 <b>¡Hola {name}! Bienvenido a Hisab-Kitab Bot 💰</b>

¡Llevar el control de tus gastos e ingresos ahora es muy fácil!

<b>Solo escribe en el chat:</b>
👉 <code>Café 50</code>
👉 <code>Gasolina 200</code>
👉 <code>Supermercado 850</code>
👉 <code>+50000 Salario</code> (para ingresos)

<i>🌍 Moneda: <b>{currency}</b> | País: <b>{country}</b></i>
<i>🎁 ¡Invita a 1 amigo y obtén <b>1 mes de descargas ilimitadas gratis</b>!</i>
🌐 <i>Para cambiar país o idioma usa /country o /language.</i>""",

        'help': """📖 <b>Guía y Comandos de Hisab-Kitab:</b>
• <code>Café 50</code> ➔ Comida
• <code>Gasolina 200</code> ➔ Transporte
• <code>+50000 Salario</code> ➔ Ingresos

/today - Gastos de hoy
/month - Resumen mensual
/budget - Fijar presupuesto mensual
/country - Cambiar país y moneda 🌍
/language - Cambiar idioma 🌐
/delete - Eliminar registros
/statement - Descargar reporte (PDF/Excel)""",

        'language_prompt': "🌐 <b>Elige tu idioma:</b>",
        'language_changed': "✅ ¡Idioma cambiado a <b>Español</b>!",
        'country_prompt': "🌍 <b>Elige tu país y moneda:</b>",
        'country_changed': "✅ País y moneda configurados: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ No hay gastos registrados hoy.",
        'undo_empty': "ℹ️ No hay registros para eliminar.",
        'undo_success': "🗑️ <b>Registro eliminado:</b> {currency}{amount:,.0f} ({category})\n📊 Total de hoy: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Tu presupuesto mensual es: <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>¡{currency}{amount:,.0f} gastados!</b> ({category})",
        'income_added_title': "✅ <b>¡Ingreso añadido!</b> 💰",
        'unknown_input': "🤔 No entendí. Escribe por ejemplo: <code>Café 50</code> o <code>Gasolina 200</code>."
    },

    'pt': {
        'welcome': """👋 <b>Olá {name}! Bem-vindo ao Hisab-Kitab Bot 💰</b>

Controlar seus gastos e receitas diárias ficou muito mais fácil!

<b>Basta enviar no chat:</b>
👉 <code>Café 10</code>
👉 <code>Gasolina 50</code>
👉 <code>Mercado 120</code>
👉 <code>+5000 Salário</code> (para renda)

<i>🌍 Moeda: <b>{currency}</b> | País: <b>{country}</b></i>
<i>🎁 Convide 1 amigo para desbloquear <b>1 mês de downloads grátis</b>!</i>
🌐 <i>Mudar país ou idioma: /country ou /language.</i>""",

        'help': """📖 <b>Comandos do Hisab-Kitab:</b>
• <code>Café 10</code> ➔ Alimentação
• <code>Gasolina 50</code> ➔ Transporte
• <code>+5000 Salário</code> ➔ Renda

/today - Gastos de hoje
/month - Resumo mensal
/budget - Orçamento mensal
/country - Mudar país e moeda 🌍
/language - Mudar idioma 🌐
/delete - Desfazer registros
/statement - Baixar extrato (PDF/Excel)""",

        'language_prompt': "🌐 <b>Escolha o seu idioma:</b>",
        'language_changed': "✅ Idioma alterado para <b>Português</b>!",
        'country_prompt': "🌍 <b>Escolha o seu país e moeda:</b>",
        'country_changed': "✅ País e moeda definidos para <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Nenhum gasto registrado hoje.",
        'undo_empty': "ℹ️ Nenhum registro para apagar.",
        'undo_success': "🗑️ <b>Registro apagado:</b> {currency}{amount:,.0f} ({category})\n📊 Total de hoje: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Seu orçamento mensal é: <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} gastos!</b> ({category})",
        'income_added_title': "✅ <b>Receita adicionada!</b> 💰",
        'unknown_input': "🤔 Não entendi. Digite por exemplo: <code>Café 10</code>."
    },

    'ar': {
        'welcome': """👋 <b>أهلاً {name}! مرحباً بك في Hisab-Kitab Bot 💰</b>

تسجيل مصاريفك ودخلك اليومي أصبح في غاية السهولة!

<b>فقط اكتب في المحادثة:</b>
👉 <code>قهوة 15</code>
👉 <code>بنزين 50</code>
👉 <code>بقالة 120</code>
👉 <code>+5000 راتب</code> (لتسجيل الدخل)

<i>🌍 العملة: <b>{currency}</b> | الدولة: <b>{country}</b></i>
<i>🎁 ادعُ صديقاً واحداً واحصل على <b>شهر كامل من التحميل المجاني غير المحدود</b>!</i>
🌐 <i>لتغيير الدولة أو اللغة: /country أو /language.</i>""",

        'help': """📖 <b>دليل وأوامر Hisab-Kitab:</b>
• <code>قهوة 15</code> ➔ طعام
• <code>بنزين 50</code> ➔ مواصلات
• <code>+5000 راتب</code> ➔ دخل

/today - مصاريف اليوم
/month - ملخص الشهر
/budget - الميزانية الشهرية
/country - تغيير الدولة والعملة 🌍
/language - تغيير اللغة 🌐
/delete - حذف أو تعديل قيد
/statement - تحميل الكشف (PDF/Excel)""",

        'language_prompt': "🌐 <b>اختر لغتك المفضلة:</b>",
        'language_changed': "✅ تم تغيير اللغة إلى <b>العربية</b>!",
        'country_prompt': "🌍 <b>اختر الدولة والعملة:</b>",
        'country_changed': "✅ تم ضبط الدولة والعملة: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ لا توجد مصاريف مسجلة اليوم.",
        'undo_empty': "ℹ️ لا يوجد قيد لحذفه.",
        'undo_success': "🗑️ <b>تم حذف القيد:</b> {currency}{amount:,.0f} ({category})\n📊 مجموع اليوم: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ تم تحديد ميزانيتك الشهرية: <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>تم صرف {currency}{amount:,.0f}!</b> ({category})",
        'income_added_title': "✅ <b>تمت إضافة الدخل!</b> 💰",
        'unknown_input': "🤔 لم أفهم ذلك. اكتب مثلاً: <code>قهوة 15</code>."
    },

    'id': {
        'welcome': """👋 <b>Halo {name}! Selamat datang di Hisab-Kitab Bot 💰</b>

Mencatat pengeluaran dan pemasukan harian kini super mudah!

<b>Cukup ketik langsung di chat:</b>
👉 <code>Kopi 25000</code>
👉 <code>Bensin 50000</code>
👉 <code>Makan 35000</code>
👉 <code>+5000000 Gaji</code> (untuk pemasukan)

<i>🌍 Mata Uang: <b>{currency}</b> | Negara: <b>{country}</b></i>
<i>🎁 Undang 1 teman untuk mendapatkan <b>1 Bulan Unduhan Gratis Tanpa Batas</b>!</i>
🌐 <i>Ganti negara atau bahasa: /country atau /language.</i>""",

        'help': """📖 <b>Panduan & Perintah Hisab-Kitab:</b>
• <code>Kopi 25000</code> ➔ Makanan
• <code>Bensin 50000</code> ➔ Transportasi
• <code>+5000000 Gaji</code> ➔ Pemasukan

/today - Pengeluaran hari ini
/month - Ringkasan bulanan
/budget - Atur anggaran bulanan
/country - Ganti negara & mata uang 🌍
/language - Ganti bahasa 🌐
/delete - Hapus catatan (Undo)
/statement - Unduh laporan (PDF/Excel)""",

        'language_prompt': "🌐 <b>Pilih bahasa Anda:</b>",
        'language_changed': "✅ Bahasa berhasil diubah ke <b>Bahasa Indonesia</b>!",
        'country_prompt': "🌍 <b>Pilih Negara & Mata Uang Anda:</b>",
        'country_changed': "✅ Negara dan mata uang diatur ke: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Belum ada pengeluaran hari ini.",
        'undo_empty': "ℹ️ Tidak ada catatan untuk dihapus.",
        'undo_success': "🗑️ <b>Catatan dihapus:</b> {currency}{amount:,.0f} ({category})\n📊 Total hari ini: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Anggaran bulanan Anda disetel ke <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} dibelanjakan!</b> ({category})",
        'income_added_title': "✅ <b>Pemasukan ditambahkan!</b> 💰",
        'unknown_input': "🤔 Tidak dimengerti. Ketik misalnya: <code>Kopi 25000</code>."
    },

    'fr': {
        'welcome': """👋 <b>Bonjour {name} ! Bienvenue sur Hisab-Kitab Bot 💰</b>

Suivez vos dépenses et revenus quotidiens en un clin d'œil !

<b>Écrivez simplement dans le chat :</b>
👉 <code>Café 5</code>
👉 <code>Essence 50</code>
👉 <code>Courses 80</code>
👉 <code>+3000 Salaire</code> (pour les revenus)

<i>🌍 Devise: <b>{currency}</b> | Pays: <b>{country}</b></i>
<i>🎁 Parrainez 1 ami pour obtenir <b>1 mois de téléchargements gratuits illimités</b> !</i>""",

        'help': """📖 <b>Guide & Commandes Hisab-Kitab :</b>
• <code>Café 5</code> ➔ Nourriture
• <code>Essence 50</code> ➔ Transport
• <code>+3000 Salaire</code> ➔ Revenu

/today - Dépenses du jour
/month - Résumé mensuel
/budget - Définir le budget
/country - Changer de pays et devise 🌍
/language - Changer de langue 🌐
/delete - Annuler une saisie
/statement - Télécharger le relevé (PDF/Excel)""",

        'language_prompt': "🌐 <b>Choisissez votre langue :</b>",
        'language_changed': "✅ Langue mise à jour en <b>Français</b> !",
        'country_prompt': "🌍 <b>Sélectionnez votre pays et devise :</b>",
        'country_changed': "✅ Pays et devise définis sur : <b>{country} ({currency})</b> !",
        'today_empty': "ℹ️ Aucune dépense enregistrée aujourd'hui.",
        'undo_empty': "ℹ️ Aucune saisie à annuler.",
        'undo_success': "🗑️ <b>Saisie supprimée :</b> {currency}{amount:,.0f} ({category})\n📊 Total du jour : <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Votre budget mensuel est fixé à <b>{currency}{val:,.0f}</b> !",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} dépensés !</b> ({category})",
        'income_added_title': "✅ <b>Revenu ajouté !</b> 💰",
        'unknown_input': "🤔 Pas compris. Tapez par exemple : <code>Café 5</code>."
    },

    'de': {
        'welcome': """👋 <b>Hallo {name}! Willkommen beim Hisab-Kitab Bot 💰</b>

Verfolgen Sie Ihre täglichen Ausgaben und Einnahmen mühelos!

<b>Einfach im Chat eingeben:</b>
👉 <code>Kaffee 5</code>
👉 <code>Tanken 60</code>
👉 <code>Supermarkt 90</code>
👉 <code>+3500 Gehalt</code> (für Einnahmen)

<i>🌍 Währung: <b>{currency}</b> | Land: <b>{country}</b></i>
<i>🎁 1 Freund einladen = <b>1 Monat unbegrenzte Downloads gratis</b>!</i>""",

        'help': """📖 <b>Hisab-Kitab Befehle:</b>
• <code>Kaffee 5</code> ➔ Essen
• <code>Tanken 60</code> ➔ Transport
• <code>+3500 Gehalt</code> ➔ Einnahmen

/today - Heutige Ausgaben
/month - Monatsübersicht
/budget - Monatsbudget festlegen
/country - Land & Währung ändern 🌍
/language - Sprache ändern 🌐
/delete - Eintrag löschen
/statement - Auszug herunterladen (PDF/Excel)""",

        'language_prompt': "🌐 <b>Wählen Sie Ihre Sprache:</b>",
        'language_changed': "✅ Sprache erfolgreich geändert!",
        'country_prompt': "🌍 <b>Wählen Sie Land und Währung:</b>",
        'country_changed': "✅ Land und Währung eingestellt: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Heute noch keine Ausgaben erfasst.",
        'undo_empty': "ℹ️ Kein Eintrag zum Löschen gefunden.",
        'undo_success': "🗑️ <b>Eintrag gelöscht:</b> {currency}{amount:,.0f} ({category})\n📊 Heute gesamt: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Ihr Monatsbudget wurde auf <b>{currency}{val:,.0f}</b> festgelegt!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} ausgegeben!</b> ({category})",
        'income_added_title': "✅ <b>Einnahme hinzugefügt!</b> 💰",
        'unknown_input': "🤔 Nicht verstanden. Schreiben Sie z.B.: <code>Kaffee 5</code>."
    },

    'it': {
        'welcome': """👋 <b>Ciao {name}! Benvenuto su Hisab-Kitab Bot 💰</b>

Gestire le tue spese e le tue entrate quotidiane ora è facilissimo!

<b>Scrivi semplicemente in chat:</b>
👉 <code>Caffè 2</code>
👉 <code>Benzina 50</code>
👉 <code>Spesa 80</code>
👉 <code>+2500 Stipendio</code> (per le entrate)

<i>🌍 Valuta: <b>{currency}</b> | Paese: <b>{country}</b></i>
<i>🎁 Invita 1 amico per avere <b>1 mese di download gratuiti illimitati</b>!</i>""",

        'help': """📖 <b>Comandi di Hisab-Kitab:</b>
• <code>Caffè 2</code> ➔ Cibo
• <code>Benzina 50</code> ➔ Trasporti
• <code>+2500 Stipendio</code> ➔ Entrate

/today - Spese di oggi
/month - Riepilogo mensile
/budget - Imposta budget
/country - Cambia paese e valuta 🌍
/language - Cambia lingua 🌐
/delete - Annulla voce
/statement - Scarica estratto conto (PDF/Excel)""",

        'language_prompt': "🌐 <b>Scegli la tua lingua:</b>",
        'language_changed': "✅ Lingua aggiornata con successo!",
        'country_prompt': "🌍 <b>Scegli paese e valuta:</b>",
        'country_changed': "✅ Paese e valuta impostati su: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Nessuna spesa registrata oggi.",
        'undo_empty': "ℹ️ Nessuna voce trovata da cancellare.",
        'undo_success': "🗑️ <b>Voce eliminata:</b> {currency}{amount:,.0f} ({category})\n📊 Totale di oggi: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Il tuo budget mensile è impostato su <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} spesi!</b> ({category})",
        'income_added_title': "✅ <b>Entrata aggiunta!</b> 💰",
        'unknown_input': "🤔 Non ho capito. Scrivi per esempio: <code>Caffè 2</code>."
    },

    'tr': {
        'welcome': """👋 <b>Merhaba {name}! Hisab-Kitab Bot'a Hoş Geldiniz 💰</b>

Günlük gelir ve giderlerinizi takip etmek artık çok kolay!

<b>Sadece sohbete yazın:</b>
👉 <code>Kahve 40</code>
👉 <code>Benzin 500</code>
👉 <code>Market 350</code>
👉 <code>+35000 Maaş</code> (gelir kaydetmek için)

<i>🌍 Para Birimi: <b>{currency}</b> | Ülke: <b>{country}</b></i>
<i>🎁 1 arkadaşını davet et, <b>1 Ay Sınırsız Ücretsiz İndirme</b> kazan!</i>""",

        'help': """📖 <b>Hisab-Kitab Komutları:</b>
• <code>Kahve 40</code> ➔ Yemek
• <code>Benzin 500</code> ➔ Ulaşım
• <code>+35000 Maaş</code> ➔ Gelir

/today - Bugünün harcamaları
/month - Aylık özet
/budget - Bütçe belirle
/country - Ülke ve para birimi 🌍
/language - Dili değiştir 🌐
/delete - Kayıt sil (Geri al)
/statement - Ekstre indir (PDF/Excel)""",

        'language_prompt': "🌐 <b>Tercih ettiğiniz dili seçin:</b>",
        'language_changed': "✅ Dil başarıyla güncellendi!",
        'country_prompt': "🌍 <b>Ülkenizi ve para biriminizi seçin:</b>",
        'country_changed': "✅ Ülke ve para birimi ayarlandı: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Bugün henüz harcama kaydedilmedi.",
        'undo_empty': "ℹ️ Silinecek kayıt bulunamadı.",
        'undo_success': "🗑️ <b>Kayıt silindi:</b> {currency}{amount:,.0f} ({category})\n📊 Bugünün toplamı: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Aylık bütçeniz <b>{currency}{val:,.0f}</b> olarak belirlendi!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} harcandı!</b> ({category})",
        'income_added_title': "✅ <b>Gelir eklendi!</b> 💰",
        'unknown_input': "🤔 Anlaşılamadı. Örneğin yazın: <code>Kahve 40</code>."
    },

    'vi': {
        'welcome': """👋 <b>Xin chào {name}! Chào mừng đến với Hisab-Kitab Bot 💰</b>

Theo dõi thu chi hằng ngày của bạn thật dễ dàng và tiện lợi!

<b>Chỉ cần gõ vào khung chat:</b>
👉 <code>Cà phê 30000</code>
👉 <code>Xăng 50000</code>
👉 <code>Đi chợ 150000</code>
👉 <code>+15000000 Lương</code> (để ghi thu nhập)

<i>🌍 Tiền tệ: <b>{currency}</b> | Quốc gia: <b>{country}</b></i>
<i>🎁 Giới thiệu 1 người bạn để nhận <b>1 Tháng Tải Miễn Phí Không Giới Hạn</b>!</i>""",

        'help': """📖 <b>Hướng Dẫn & Lệnh Hisab-Kitab:</b>
• <code>Cà phê 30000</code> ➔ Ăn uống
• <code>Xăng 50000</code> ➔ Đi lại
• <code>+15000000 Lương</code> ➔ Thu nhập

/today - Chi tiêu hôm nay
/month - Tổng kết tháng
/budget - Đặt hạn mức ngân sách
/country - Đổi quốc gia & tiền tệ 🌍
/language - Đổi ngôn ngữ 🌐
/delete - Xoá giao dịch (Hoàn tác)
/statement - Tải báo cáo (PDF/Excel)""",

        'language_prompt': "🌐 <b>Chọn ngôn ngữ của bạn:</b>",
        'language_changed': "✅ Ngôn ngữ đã được cập nhật!",
        'country_prompt': "🌍 <b>Chọn quốc gia và đơn vị tiền tệ:</b>",
        'country_changed': "✅ Quốc gia & tiền tệ: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Hôm nay chưa có khoản chi nào.",
        'undo_empty': "ℹ️ Không tìm thấy giao dịch nào để xoá.",
        'undo_success': "🗑️ <b>Đã xoá giao dịch:</b> {currency}{amount:,.0f} ({category})\n📊 Tổng hôm nay: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Ngân sách tháng của bạn là <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>Đã chi {currency}{amount:,.0f}!</b> ({category})",
        'income_added_title': "✅ <b>Đã thêm thu nhập!</b> 💰",
        'unknown_input': "🤔 Chưa hiểu. Ví dụ gõ: <code>Cà phê 30000</code>."
    },

    'ja': {
        'welcome': """👋 <b>こんにちは {name}さん！ Hisab-Kitab Botへようこそ 💰</b>

毎日の家計簿・収支管理がチャットだけで手軽に完了します！

<b>チャットに直接入力するだけ:</b>
👉 <code>カフェ 450</code>
👉 <code>ガソリン 3000</code>
👉 <code>スーパー 2500</code>
👉 <code>+280000 給料</code> (収入の記録)

<i>🌍 通貨: <b>{currency}</b> | 国: <b>{country}</b></i>
<i>🎁 友達を1人招待すると<b>1ヶ月間無制限無料ダウンロード</b>！</i>""",

        'help': """📖 <b>Hisab-Kitab コマンド一覧:</b>
• <code>カフェ 450</code> ➔ 食費
• <code>ガソリン 3000</code> ➔ 交通費
• <code>+280000 給料</code> ➔ 収入

/today - 今日の支出
/month - 今月のまとめ
/budget - 予算設定
/country - 国と通貨の変更 🌍
/language - 言語の変更 🌐
/delete - 記録の削除 (元に戻す)
/statement - 明細ダウンロード (PDF/Excel)""",

        'language_prompt': "🌐 <b>言語を選択してください:</b>",
        'language_changed': "✅ 言語が更新されました！",
        'country_prompt': "🌍 <b>国と通貨を選択してください:</b>",
        'country_changed': "✅ 国と通貨が設定されました: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ 今日の支出はまだ記録されていません。",
        'undo_empty': "ℹ️ 削除できる記録がありません。",
        'undo_success': "🗑️ <b>記録を削除しました:</b> {currency}{amount:,.0f} ({category})\n📊 今日の合計: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ 今月の予算を <b>{currency}{val:,.0f}</b> に設定しました！",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} の支出を記録！</b> ({category})",
        'income_added_title': "✅ <b>収入を記録しました！</b> 💰",
        'unknown_input': "🤔 認識できませんでした。例: <code>カフェ 450</code>"
    },

    'ko': {
        'welcome': """👋 <b>안녕하세요 {name}님! Hisab-Kitab Bot에 오신 것을 환영합니다 💰</b>

매일의 지출과 수입을 채팅으로 간편하게 관리하세요!

<b>채팅창에 바로 입력하세요:</b>
👉 <code>커피 5000</code>
👉 <code>주유 50000</code>
👉 <code>마트 35000</code>
👉 <code>+3500000 월급</code> (수입 기록)

<i>🌍 통화: <b>{currency}</b> | 국가: <b>{country}</b></i>
<i>🎁 친구 1명 초대 시 <b>1개월 무제한 무료 다운로드</b> 제공!</i>""",

        'help': """📖 <b>Hisab-Kitab 명령어:</b>
• <code>커피 5000</code> ➔ 식비
• <code>주유 50000</code> ➔ 교통비
• <code>+3500000 월급</code> ➔ 수입

/today - 오늘의 지출
/month - 이번 달 요약
/budget - 예산 설정
/country - 국가 및 통화 변경 🌍
/language - 언어 변경 🌐
/delete - 항목 삭제 (실행 취소)
/statement - 내역서 다운로드 (PDF/Excel)""",

        'language_prompt': "🌐 <b>원하시는 언어를 선택하세요:</b>",
        'language_changed': "✅ 언어가 성공적으로 변경되었습니다!",
        'country_prompt': "🌍 <b>국가 및 통화를 선택하세요:</b>",
        'country_changed': "✅ 설정 완료: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ 오늘 기록된 지출이 없습니다.",
        'undo_empty': "ℹ️ 삭제할 내역이 없습니다.",
        'undo_success': "🗑️ <b>항목 삭제 완료:</b> {currency}{amount:,.0f} ({category})\n📊 오늘 총합: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ 이번 달 예산이 <b>{currency}{val:,.0f}</b>으로 설정되었습니다!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} 지출 완료!</b> ({category})",
        'income_added_title': "✅ <b>수입 추가 완료!</b> 💰",
        'unknown_input': "🤔 이해하지 못했습니다. 예: <code>커피 5000</code>"
    },

    'uk': {
        'welcome': """👋 <b>Привіт {name}! Ласкаво просимо до Hisab-Kitab Bot 💰</b>

Облік щоденних витрат і доходів тепер став неймовірно простим!

<b>Просто напишіть у чат:</b>
👉 <code>Кава 60</code>
👉 <code>Бензин 1000</code>
👉 <code>Продукти 500</code>
👉 <code>+30000 Зарплата</code> (для доходу)

<i>🌍 Валюта: <b>{currency}</b> | Країна: <b>{country}</b></i>
<i>🎁 Запросіть 1 друга та отримайте <b>1 місяць безліміту безкоштовно</b>!</i>""",

        'help': """📖 <b>Команди Hisab-Kitab:</b>
• <code>Кава 60</code> ➔ Їжа
• <code>Бензин 1000</code> ➔ Транспорт
• <code>+30000 Зарплата</code> ➔ Дохід

/today - Витрати за сьогодні
/month - Підсумки місяця
/budget - Встановити бюджет
/country - Змінити країну та валюту 🌍
/language - Змінити мову 🌐
/delete - Видалити запис
/statement - Завантажити виписку (PDF/Excel)""",

        'language_prompt': "🌐 <b>Оберіть мову інтерфейсу:</b>",
        'language_changed': "✅ Мову успішно оновлено!",
        'country_prompt': "🌍 <b>Оберіть країну та валюту:</b>",
        'country_changed': "✅ Встановлено: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Сьогодні ще немає витрат.",
        'undo_empty': "ℹ️ Немає записів для видалення.",
        'undo_success': "🗑️ <b>Запис видалено:</b> {currency}{amount:,.0f} ({category})\n📊 Всього за сьогодні: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Ваш місячний бюджет: <b>{currency}{val:,.0f}</b>!",
        'expense_added_title': "✅ <b>Витрачено {currency}{amount:,.0f}!</b> ({category})",
        'income_added_title': "✅ <b>Дохід додано!</b> 💰",
        'unknown_input': "🤔 Не вдалося розпізнати. Напишіть, наприклад: <code>Кава 60</code>."
    },

    'uz': {
        'welcome': """👋 <b>Salom {name}! Hisab-Kitab Bot-ga xush kelibsiz 💰</b>

Kundalik xarajat va daromadlarni hisoblab borish endi juda oson!

<b>Shunchaki chatga yozing:</b>
👉 <code>Qahva 15000</code>
👉 <code>Benzin 100000</code>
👉 <code>Bozor 85000</code>
👉 <code>+5000000 Oylik</code> (daromad uchun)

<i>🌍 Valyuta: <b>{currency}</b> | Mamlakat: <b>{country}</b></i>
<i>🎁 1 doʻstingizni taklif qiling va <b>1 oy bepul cheksiz hisobot</b> oling!</i>""",

        'help': """📖 <b>Hisab-Kitab buyruqlari:</b>
• <code>Qahva 15000</code> ➔ Taom
• <code>Benzin 100000</code> ➔ Yoʻl
• <code>+5000000 Oylik</code> ➔ Daromad

/today - Bugungi xarajatlar
/month - Oylik hisobot
/budget - Byudjet belgilash
/country - Mamlakat va valyutani oʻzgartirish 🌍
/language - Tilni oʻzgartirish 🌐
/delete - Yozuvni oʻchirish
/statement - Hisobotni yuklash (PDF/Excel)""",

        'language_prompt': "🌐 <b>Oʻzingizga qulay tilni tanlang:</b>",
        'language_changed': "✅ Til muvaffaqiyatli oʻzgartirildi!",
        'country_prompt': "🌍 <b>Mamlakat va valyutani tanlang:</b>",
        'country_changed': "✅ Oʻrnatildi: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Bugun hali xarajatlar kiritilmadi.",
        'undo_empty': "ℹ️ Oʻchirish uchun yozuv topilmadi.",
        'undo_success': "🗑️ <b>Yozuv oʻchirildi:</b> {currency}{amount:,.0f} ({category})\n📊 Bugungi jami: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Oylik byudjetingiz <b>{currency}{val:,.0f}</b> qilib belgilandi!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} sarflandi!</b> ({category})",
        'income_added_title': "✅ <b>Daromad qoʻshildi!</b> 💰",
        'unknown_input': "🤔 Tushunarsiz. Masalan yozing: <code>Qahva 15000</code>."
    },

    'kk': {
        'welcome': """👋 <b>Сәлем {name}! Hisab-Kitab Bot-қа қош келдіңіз 💰</b>

Күнделікті кіріс пен шығысты есепке алу енді өте оңай!

<b>Тек чатқа жазыңыз:</b>
👉 <code>Кофе 1200</code>
👉 <code>Бензин 8000</code>
👉 <code>Азық-түлік 5000</code>
👉 <code>+350000 Жалақы</code> (кіріс үшін)

<i>🌍 Валюта: <b>{currency}</b> | Ел: <b>{country}</b></i>
<i>🎁 1 досыңызды шақырып, <b>1 ай шексіз тегін жүктеуге</b> қол жеткізіңіз!</i>""",

        'help': """📖 <b>Hisab-Kitab командалары:</b>
• <code>Кофе 1200</code> ➔ Тамақ
• <code>Бензин 8000</code> ➔ Көлік
• <code>+350000 Жалақы</code> ➔ Кіріс

/today - Бүгінгі шығыстар
/month - Айлық қорытынды
/budget - Бюджет орнату
/country - Ел мен валютаны өзгерту 🌍
/language - Тілді өзгерту 🌐
/delete - Жазбаны жою
/statement - Көшірмені жүктеу (PDF/Excel)""",

        'language_prompt': "🌐 <b>Тілді таңдаңыз:</b>",
        'language_changed': "✅ Тіл сәтті жаңартылды!",
        'country_prompt': "🌍 <b>Ел мен валютаны таңдаңыз:</b>",
        'country_changed': "✅ Орнатылды: <b>{country} ({currency})</b>!",
        'today_empty': "ℹ️ Бүгін әлі шығыстар жазылмаған.",
        'undo_empty': "ℹ️ Жою үшін жазба табылмады.",
        'undo_success': "🗑️ <b>Жазба жойылды:</b> {currency}{amount:,.0f} ({category})\n📊 Бүгінгі барлығы: <b>{currency}{today_total:,.0f}</b>",
        'budget_set': "✅ Айлық бюджетіңіз <b>{currency}{val:,.0f}</b> болып белгіленді!",
        'expense_added_title': "✅ <b>{currency}{amount:,.0f} жұмсалды!</b> ({category})",
        'income_added_title': "✅ <b>Кіріс қосылды!</b> 💰",
        'unknown_input': "🤔 Түсініксіз. Мысалы жазыңыз: <code>Кофе 1200</code>."
    }
}

def get_msg(key: str, lang: str = 'en', **kwargs) -> str:
    lang_dict = MESSAGES.get(lang, MESSAGES['en'])
    template = lang_dict.get(key)
    if template is None:
        template = MESSAGES['en'].get(key, "")

    if kwargs:
        kwargs.setdefault('currency', '$')
        kwargs.setdefault('country', 'Worldwide')
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


# =========================================================================
# HELPER FORMATTERS FOR REPLIES & NOTIFICATIONS ACROSS ALL 19 LANGUAGES
# =========================================================================

def format_expense_logged(lang: str, amount: float, category: str, note: str, expense_id: int, curr_sym: str, today_total: float, budget: float = 0.0, rem_budget: float = 0.0) -> str:
    """Formats response when an expense is logged in the user's language."""
    if lang == 'hi':
        text = f"✅ <b>{curr_sym}{amount:,.0f} खर्च हुआ!</b> ({category})\n• ID: <code>#{expense_id}</code> | नोट: <i>{note}</i>\n📊 <b>आज का कुल खर्चा: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 बचा हुआ मंथली बजट: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'bn':
        text = f"✅ <b>{curr_sym}{amount:,.0f} খরচ হয়েছে!</b> ({category})\n• ID: <code>#{expense_id}</code> | বিবরণ: <i>{note}</i>\n📊 <b>আজকের মোট: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 অবশিষ্ট বাজেট: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'ur':
        text = f"✅ <b>{curr_sym}{amount:,.0f} خرچ ہوا!</b> ({category})\n• ID: <code>#{expense_id}</code> | نوٹ: <i>{note}</i>\n📊 <b>آج کا ٹوٹل خرچ: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 باقی بجٹ: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'ru':
        text = f"✅ <b>Потрачено {curr_sym}{amount:,.0f}!</b> ({category})\n• ID: <code>#{expense_id}</code> | Заметка: <i>{note}</i>\n📊 <b>Всего за сегодня: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Остаток бюджета: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'es':
        text = f"✅ <b>¡{curr_sym}{amount:,.0f} gastados!</b> ({category})\n• ID: <code>#{expense_id}</code> | Nota: <i>{note}</i>\n📊 <b>Total de hoy: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Presupuesto restante: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'pt':
        text = f"✅ <b>{curr_sym}{amount:,.0f} gastos!</b> ({category})\n• ID: <code>#{expense_id}</code> | Nota: <i>{note}</i>\n📊 <b>Total de hoje: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Orçamento restante: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'ar':
        text = f"✅ <b>تم صرف {curr_sym}{amount:,.0f}!</b> ({category})\n• ID: <code>#{expense_id}</code> | ملاحظة: <i>{note}</i>\n📊 <b>مجموع اليوم: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 المتبقي من الميزانية: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'id':
        text = f"✅ <b>{curr_sym}{amount:,.0f} dibelanjakan!</b> ({category})\n• ID: <code>#{expense_id}</code> | Catatan: <i>{note}</i>\n📊 <b>Total hari ini: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Sisa anggaran: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'fr':
        text = f"✅ <b>{curr_sym}{amount:,.0f} dépensés !</b> ({category})\n• ID: <code>#{expense_id}</code> | Note: <i>{note}</i>\n📊 <b>Total du jour: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Budget restant: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'de':
        text = f"✅ <b>{curr_sym}{amount:,.0f} ausgegeben!</b> ({category})\n• ID: <code>#{expense_id}</code> | Notiz: <i>{note}</i>\n📊 <b>Heute gesamt: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Restbudget: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'it':
        text = f"✅ <b>{curr_sym}{amount:,.0f} spesi!</b> ({category})\n• ID: <code>#{expense_id}</code> | Nota: <i>{note}</i>\n📊 <b>Totale di oggi: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Budget rimanente: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'tr':
        text = f"✅ <b>{curr_sym}{amount:,.0f} harcandı!</b> ({category})\n• ID: <code>#{expense_id}</code> | Not: <i>{note}</i>\n📊 <b>Bugünün toplamı: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Kalan bütçe: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'vi':
        text = f"✅ <b>Đã chi {curr_sym}{amount:,.0f}!</b> ({category})\n• ID: <code>#{expense_id}</code> | Ghi chú: <i>{note}</i>\n📊 <b>Tổng hôm nay: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Ngân sách còn lại: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'ja':
        text = f"✅ <b>{curr_sym}{amount:,.0f} の支出を記録！</b> ({category})\n• ID: <code>#{expense_id}</code> | メモ: <i>{note}</i>\n📊 <b>今日の合計: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 残りの予算: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'ko':
        text = f"✅ <b>{curr_sym}{amount:,.0f} 지출 완료!</b> ({category})\n• ID: <code>#{expense_id}</code> | 메모: <i>{note}</i>\n📊 <b>오늘 총합: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 남은 예산: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'uk':
        text = f"✅ <b>Витрачено {curr_sym}{amount:,.0f}!</b> ({category})\n• ID: <code>#{expense_id}</code> | Замітка: <i>{note}</i>\n📊 <b>Всього за сьогодні: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Залишок бюджету: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'uz':
        text = f"✅ <b>{curr_sym}{amount:,.0f} sarflandi!</b> ({category})\n• ID: <code>#{expense_id}</code> | Eslatma: <i>{note}</i>\n📊 <b>Bugungi jami: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Qolgan byudjet: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    elif lang == 'kk':
        text = f"✅ <b>{curr_sym}{amount:,.0f} жұмсалды!</b> ({category})\n• ID: <code>#{expense_id}</code> | Жазба: <i>{note}</i>\n📊 <b>Бүгінгі барлығы: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Қалған бюджет: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text
    else:  # en
        text = f"✅ <b>{curr_sym}{amount:,.0f} spent!</b> ({category})\n• ID: <code>#{expense_id}</code> | Note: <i>{note}</i>\n📊 <b>Today's Total: {curr_sym}{today_total:,.0f}</b>"
        if budget > 0:
            text += f"\n🎯 Monthly Budget Remaining: <b>{curr_sym}{rem_budget:,.0f}</b>"
        return text

def format_income_logged(lang: str, amount: float, category: str, note: str, expense_id: int, curr_sym: str) -> str:
    """Formats response when an income is logged in the user's language."""
    if lang == 'hi':
        return f"✅ <b>कमाई जुड़ गई!</b> 💰\n• ID: <code>#{expense_id}</code>\n• राशि: <b>+{curr_sym}{amount:,.0f}</b>\n• केटेगरी: {category} ({note})"
    elif lang == 'bn':
        return f"✅ <b>আয় যোগ করা হয়েছে!</b> 💰\n• ID: <code>#{expense_id}</code>\n• পরিমাণ: <b>+{curr_sym}{amount:,.0f}</b>\n• ক্যাটাগরি: {category} ({note})"
    elif lang == 'ur':
        return f"✅ <b>آمدنی شامل ہو گئی!</b> 💰\n• ID: <code>#{expense_id}</code>\n• رقم: <b>+{curr_sym}{amount:,.0f}</b>\n• کیٹیگری: {category} ({note})"
    elif lang == 'ru':
        return f"✅ <b>Доход добавлен!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Сумма: <b>+{curr_sym}{amount:,.0f}</b>\n• Категория: {category} ({note})"
    elif lang == 'es':
        return f"✅ <b>¡Ingreso añadido!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Monto: <b>+{curr_sym}{amount:,.0f}</b>\n• Categoría: {category} ({note})"
    elif lang == 'pt':
        return f"✅ <b>Receita adicionada!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Valor: <b>+{curr_sym}{amount:,.0f}</b>\n• Categoria: {category} ({note})"
    elif lang == 'ar':
        return f"✅ <b>تمت إضافة الدخل!</b> 💰\n• ID: <code>#{expense_id}</code>\n• المبلغ: <b>+{curr_sym}{amount:,.0f}</b>\n• الفئة: {category} ({note})"
    elif lang == 'id':
        return f"✅ <b>Pemasukan ditambahkan!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Jumlah: <b>+{curr_sym}{amount:,.0f}</b>\n• Kategori: {category} ({note})"
    elif lang == 'fr':
        return f"✅ <b>Revenu ajouté !</b> 💰\n• ID: <code>#{expense_id}</code>\n• Montant: <b>+{curr_sym}{amount:,.0f}</b>\n• Catégorie: {category} ({note})"
    elif lang == 'de':
        return f"✅ <b>Einnahme hinzugefügt!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Betrag: <b>+{curr_sym}{amount:,.0f}</b>\n• Kategorie: {category} ({note})"
    elif lang == 'it':
        return f"✅ <b>Entrata aggiunta!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Importo: <b>+{curr_sym}{amount:,.0f}</b>\n• Categoria: {category} ({note})"
    elif lang == 'tr':
        return f"✅ <b>Gelir eklendi!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Tutar: <b>+{curr_sym}{amount:,.0f}</b>\n• Kategori: {category} ({note})"
    elif lang == 'vi':
        return f"✅ <b>Đã thêm thu nhập!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Số tiền: <b>+{curr_sym}{amount:,.0f}</b>\n• Danh mục: {category} ({note})"
    elif lang == 'ja':
        return f"✅ <b>収入を記録しました！</b> 💰\n• ID: <code>#{expense_id}</code>\n• 金額: <b>+{curr_sym}{amount:,.0f}</b>\n• カテゴリ: {category} ({note})"
    elif lang == 'ko':
        return f"✅ <b>수입 추가 완료!</b> 💰\n• ID: <code>#{expense_id}</code>\n• 금액: <b>+{curr_sym}{amount:,.0f}</b>\n• 카테고리: {category} ({note})"
    elif lang == 'uk':
        return f"✅ <b>Дохід додано!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Сума: <b>+{curr_sym}{amount:,.0f}</b>\n• Категорія: {category} ({note})"
    elif lang == 'uz':
        return f"✅ <b>Daromad qoʻshildi!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Miqdor: <b>+{curr_sym}{amount:,.0f}</b>\n• Toifa: {category} ({note})"
    elif lang == 'kk':
        return f"✅ <b>Кіріс қосылды!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Сомасы: <b>+{curr_sym}{amount:,.0f}</b>\n• Санат: {category} ({note})"
    else:
        return f"✅ <b>Income Added!</b> 💰\n• ID: <code>#{expense_id}</code>\n• Amount: <b>+{curr_sym}{amount:,.0f}</b>\n• Category: {category} ({note})"

def format_today_summary(lang: str, expenses: list, total: float, curr_sym: str, today_str: str, is_india: bool = False) -> str:
    """Renders the itemized list of today's transactions in user's language."""
    titles = {
        'hi': f"📊 <b>आज का हिसाब ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'bn': f"📊 <b>আজকের হিসাব ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ur': f"📊 <b>آج کا حساب ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ru': f"📊 <b>Расходы за сегодня ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'es': f"📊 <b>Gastos de Hoy ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'pt': f"📊 <b>Gastos de Hoje ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ar': f"📊 <b>مصاريف اليوم ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'id': f"📊 <b>Pengeluaran Hari Ini ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'fr': f"📊 <b>Dépenses du Jour ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'de': f"📊 <b>Heutige Ausgaben ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'it': f"📊 <b>Spese di Oggi ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'tr': f"📊 <b>Bugünün Giderleri ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'vi': f"📊 <b>Chi Tiêu Hôm Nay ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ja': f"📊 <b>今日の支出 ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ko': f"📊 <b>오늘의 지출 ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'uk': f"📊 <b>Витрати за сьогодні ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'uz': f"📊 <b>Bugungi xarajatlar ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'kk': f"📊 <b>Бүгінгі шығыстар ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'en': f"📊 <b>Today's Expenses ({today_str}):</b>\n━━━━━━━━━━━━━━━━━━━"
    }

    lines = [titles.get(lang, titles['en'])]

    for e in expenses:
        is_inc = (e.get('type') == 'income')
        sign = "+" if is_inc else "-"
        color_tag = "🟢" if is_inc else "🔴"
        tx_id = e.get('id', '')
        id_badge = f"[#{tx_id}] " if tx_id else ""
        lines.append(f"{color_tag} {id_badge}{e['category']}: <b>{sign}{curr_sym}{e['amount']:,.0f}</b> (<i>{e['note']}</i>)")

    lines.append("━━━━━━━━━━━━━━━━━━━")

    footers = {
        'hi': f"💰 <b>आज का कुल खर्चा: {curr_sym}{total:,.0f}</b>",
        'bn': f"💰 <b>আজকের মোট খরচ: {curr_sym}{total:,.0f}</b>",
        'ur': f"💰 <b>آج کا کل خرچ: {curr_sym}{total:,.0f}</b>",
        'ru': f"💰 <b>Всего за сегодня: {curr_sym}{total:,.0f}</b>",
        'es': f"💰 <b>Total de Gastos de Hoy: {curr_sym}{total:,.0f}</b>",
        'pt': f"💰 <b>Total de Gastos de Hoje: {curr_sym}{total:,.0f}</b>",
        'ar': f"💰 <b>إجمالي مصاريف اليوم: {curr_sym}{total:,.0f}</b>",
        'id': f"💰 <b>Total Pengeluaran Hari Ini: {curr_sym}{total:,.0f}</b>",
        'fr': f"💰 <b>Total des Dépenses du Jour: {curr_sym}{total:,.0f}</b>",
        'de': f"💰 <b>Gesamtausgaben Heute: {curr_sym}{total:,.0f}</b>",
        'it': f"💰 <b>Totale Spese di Oggi: {curr_sym}{total:,.0f}</b>",
        'tr': f"💰 <b>Bugünün Toplam Gideri: {curr_sym}{total:,.0f}</b>",
        'vi': f"💰 <b>Tổng Chi Tiêu Hôm Nay: {curr_sym}{total:,.0f}</b>",
        'ja': f"💰 <b>今日の支出合計: {curr_sym}{total:,.0f}</b>",
        'ko': f"💰 <b>오늘 총 지출: {curr_sym}{total:,.0f}</b>",
        'uk': f"💰 <b>Всього за сьогодні: {curr_sym}{total:,.0f}</b>",
        'uz': f"💰 <b>Bugungi jami xarajat: {curr_sym}{total:,.0f}</b>",
        'kk': f"💰 <b>Бүгінгі жалпы шығыс: {curr_sym}{total:,.0f}</b>",
        'en': f"💰 <b>Total Expenses Today: {curr_sym}{total:,.0f}</b>"
    }
    lines.append(footers.get(lang, footers['en']))

    if is_india:
        lines.append(f"\n🔥 <i>आज के टॉप लूट ऑफर्स: <a href='{DEALS_FETCHER_URL}'>Deals Fetcher</a></i>")

    return "\n".join(lines)

def format_month_summary(lang: str, month_name: str, total_exp: float, total_inc: float, budget: float, breakdown: dict, curr_sym: str) -> str:
    """Renders the monthly category breakdown & budget status in user's language."""
    headers = {
        'hi': f"📅 <b>इस महीने का हिसाब ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'bn': f"📅 <b>এই মাসের হিসাব ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ur': f"📅 <b>اس ماہ کا خلاصہ ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ru': f"📅 <b>Итоги месяца ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'es': f"📅 <b>Resumen Mensual ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'pt': f"📅 <b>Resumo Mensal ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ar': f"📅 <b>ملخص الشهر ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'id': f"📅 <b>Ringkasan Bulanan ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'fr': f"📅 <b>Résumé Mensuel ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'de': f"📅 <b>Monatsübersicht ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'it': f"📅 <b>Riepilogo Mensile ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'tr': f"📅 <b>Aylık Özet ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'vi': f"📅 <b>Tổng Kết Tháng ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ja': f"📅 <b>今月のまとめ ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'ko': f"📅 <b>이번 달 요약 ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'uk': f"📅 <b>Підсумки місяця ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'uz': f"📅 <b>Oylik hisobot ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'kk': f"📅 <b>Айлық қорытынды ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━",
        'en': f"📅 <b>Monthly Summary ({month_name}):</b>\n━━━━━━━━━━━━━━━━━━━"
    }

    lines = [headers.get(lang, headers['en'])]

    # Total expenses
    lbl_exp = {
        'hi': "💸 <b>कुल खर्चा:</b>",
        'bn': "💸 <b>মোট খরচ:</b>",
        'ur': "💸 <b>کل خرچ:</b>",
        'ru': "💸 <b>Всего расходов:</b>",
        'es': "💸 <b>Total de Gastos:</b>",
        'pt': "💸 <b>Total de Gastos:</b>",
        'ar': "💸 <b>إجمالي المصاريف:</b>",
        'id': "💸 <b>Total Pengeluaran:</b>",
        'fr': "💸 <b>Total des Dépenses:</b>",
        'de': "💸 <b>Gesamtausgaben:</b>",
        'it': "💸 <b>Spese Totali:</b>",
        'tr': "💸 <b>Toplam Gider:</b>",
        'vi': "💸 <b>Tổng Chi Tiêu:</b>",
        'ja': "💸 <b>総支出:</b>",
        'ko': "💸 <b>총 지출:</b>",
        'uk': "💸 <b>Всього витрат:</b>",
        'uz': "💸 <b>Jami xarajat:</b>",
        'kk': "💸 <b>Жалпы шығыс:</b>",
        'en': "💸 <b>Total Expenses:</b>"
    }
    lines.append(f"{lbl_exp.get(lang, lbl_exp['en'])} {curr_sym}{total_exp:,.0f}")

    if total_inc > 0:
        lbl_inc = {
            'hi': "💰 <b>कुल कमाई (Income):</b>",
            'bn': "💰 <b>মোট আয়:</b>",
            'ur': "💰 <b>کل آمدنی:</b>",
            'ru': "💰 <b>Всего доходов:</b>",
            'es': "💰 <b>Ingresos Totales:</b>",
            'pt': "💰 <b>Renda Total:</b>",
            'ar': "💰 <b>إجمالي الدخل:</b>",
            'id': "💰 <b>Total Pemasukan:</b>",
            'fr': "💰 <b>Revenu Total:</b>",
            'de': "💰 <b>Gesamteinnahmen:</b>",
            'it': "💰 <b>Entrate Totali:</b>",
            'tr': "💰 <b>Toplam Gelir:</b>",
            'vi': "💰 <b>Tổng Thu Nhập:</b>",
            'ja': "💰 <b>総収入:</b>",
            'ko': "💰 <b>총 수입:</b>",
            'uk': "💰 <b>Всього доходів:</b>",
            'uz': "💰 <b>Jami daromad:</b>",
            'kk': "💰 <b>Жалпы кіріс:</b>",
            'en': "💰 <b>Total Income:</b>"
        }
        lbl_sav = {
            'hi': "🏦 <b>बचत (Savings):</b>",
            'bn': "🏦 <b>সঞ্চয় (Savings):</b>",
            'ur': "🏦 <b>بچت (Savings):</b>",
            'ru': "🏦 <b>Накопления:</b>",
            'es': "🏦 <b>Ahorro Neto:</b>",
            'pt': "🏦 <b>Poupança Líquida:</b>",
            'ar': "🏦 <b>صافي الادخار:</b>",
            'id': "🏦 <b>Tabungan Bersih:</b>",
            'fr': "🏦 <b>Épargne Nette:</b>",
            'de': "🏦 <b>Netto-Ersparnis:</b>",
            'it': "🏦 <b>Risparmio Netto:</b>",
            'tr': "🏦 <b>Net Tasarruf:</b>",
            'vi': "🏦 <b>Tiết Kiệm Ròng:</b>",
            'ja': "🏦 <b>貯蓄額:</b>",
            'ko': "🏦 <b>순 저축:</b>",
            'uk': "🏦 <b>Заощадження:</b>",
            'uz': "🏦 <b>Sof tejov:</b>",
            'kk': "🏦 <b>Таза жинақ:</b>",
            'en': "🏦 <b>Net Savings:</b>"
        }
        lines.append(f"{lbl_inc.get(lang, lbl_inc['en'])} {curr_sym}{total_inc:,.0f}")
        lines.append(f"{lbl_sav.get(lang, lbl_sav['en'])} {curr_sym}{(total_inc - total_exp):,.0f}")

    if budget > 0:
        pct = (total_exp / budget * 100) if budget > 0 else 0
        rem = max(0.0, budget - total_exp)
        filled = min(10, int(pct / 10))
        bar = "▓" * filled + "░" * (10 - filled)
        lbl_bgt = {
            'hi': f"\n🎯 <b>मंथली बजट:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% खर्च हुआ\n💵 <b>बचा हुआ बजट:</b> {curr_sym}{rem:,.0f}",
            'bn': f"\n🎯 <b>মাসিক বাজেট:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% ব্যয় হয়েছে\n💵 <b>অবশিষ্ট:</b> {curr_sym}{rem:,.0f}",
            'ur': f"\n🎯 <b>ماہانہ بجٹ:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% خرچ ہوا\n💵 <b>باقی:</b> {curr_sym}{rem:,.0f}",
            'ru': f"\n🎯 <b>Месячный бюджет:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% потрачено\n💵 <b>Остаток:</b> {curr_sym}{rem:,.0f}",
            'es': f"\n🎯 <b>Presupuesto Mensual:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% usado\n💵 <b>Restante:</b> {curr_sym}{rem:,.0f}",
            'pt': f"\n🎯 <b>Orçamento Mensal:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% usado\n💵 <b>Restante:</b> {curr_sym}{rem:,.0f}",
            'ar': f"\n🎯 <b>الميزانية الشهرية:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% مستهلك\n💵 <b>المتبقي:</b> {curr_sym}{rem:,.0f}",
            'id': f"\n🎯 <b>Anggaran Bulanan:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% terpakai\n💵 <b>Sisa:</b> {curr_sym}{rem:,.0f}",
            'en': f"\n🎯 <b>Monthly Budget:</b> {curr_sym}{budget:,.0f}\n[{bar}] {pct:.1f}% used\n💵 <b>Remaining:</b> {curr_sym}{rem:,.0f}"
        }
        lines.append(lbl_bgt.get(lang, lbl_bgt['en']))

    lbl_cat = {
        'hi': "\n📂 <b>केटेगरी-वाइज़ विवरण:</b>",
        'bn': "\n📂 <b>ক্যাটাগরি ভিত্তিক হিসাব:</b>",
        'ur': "\n📂 <b>کیٹیگری وار تفصیل:</b>",
        'ru': "\n📂 <b>По категориям:</b>",
        'es': "\n📂 <b>Desglose por Categoría:</b>",
        'pt': "\n📂 <b>Detalhamento por Categoria:</b>",
        'ar': "\n📂 <b>تفصيل حسب الفئات:</b>",
        'id': "\n📂 <b>Rincian per Kategori:</b>",
        'fr': "\n📂 <b>Répartition par Catégorie :</b>",
        'de': "\n📂 <b>Aufschlüsselung nach Kategorien:</b>",
        'it': "\n📂 <b>Dettaglio per Categoria:</b>",
        'tr': "\n📂 <b>Kategori Bazında Dağılım:</b>",
        'vi': "\n📂 <b>Chi Tiết Theo Danh Mục:</b>",
        'ja': "\n📂 <b>カテゴリ別内訳:</b>",
        'ko': "\n📂 <b>카테고리별 내역:</b>",
        'uk': "\n📂 <b>За категоріями:</b>",
        'uz': "\n📂 <b>Kategoriyalar boʻyicha:</b>",
        'kk': "\n📂 <b>Санаттар бойынша:</b>",
        'en': "\n📂 <b>Category-wise Breakdown:</b>"
    }
    lines.append(lbl_cat.get(lang, lbl_cat['en']))

    if breakdown['categories']:
        for c in breakdown['categories']:
            share = (c['total'] / total_exp * 100) if total_exp > 0 else 0
            lines.append(f"• {c['category']}: <b>{curr_sym}{c['total']:,.0f}</b> ({share:.0f}%)")
    else:
        empty_lbl = {
            'hi': "<i>इस महीने अभी तक कोई खर्चा नहीं लिखा गया है।</i>",
            'bn': "<i>এই মাসে এখনো কোনো খরচ লেখা হয়নি।</i>",
            'ur': "<i>اس ماہ ابھی تک کوئی خرچ نہیں لکھا گیا۔</i>",
            'ru': "<i>В этом месяце еще нет записей.</i>",
            'es': "<i>No hay gastos registrados este mes.</i>",
            'pt': "<i>Nenhum gasto registrado este mês.</i>",
            'ar': "<i>لا توجد مصاريف مسجلة هذا الشهر.</i>",
            'id': "<i>Belum ada pengeluaran bulan ini.</i>",
            'en': "<i>No expenses recorded yet this month.</i>"
        }
        lines.append(empty_lbl.get(lang, empty_lbl['en']))

    lines.append("━━━━━━━━━━━━━━━━━━━")
    stmt_hint = {
        'hi': "📥 <i>किसी भी तारीख का स्टेटमेंट डाउनलोड करें: /statement</i>",
        'bn': "📥 <i>স্টেটমেন্ট ডাউনলোড করতে লিখুন: /statement</i>",
        'ur': "📥 <i>اسٹیٹمنٹ ڈاؤن لوڈ کے لیے لکھیں: /statement</i>",
        'ru': "📥 <i>Скачать отчет за любой период: /statement</i>",
        'es': "📥 <i>Descarga tu extracto de cualquier fecha: /statement</i>",
        'pt': "📥 <i>Baixe seu extrato de qualquer período: /statement</i>",
        'ar': "📥 <i>تحميل كشف الحساب لأي فترة: /statement</i>",
        'id': "📥 <i>Unduh laporan untuk rentang tanggal apa pun: /statement</i>",
        'en': "📥 <i>Download statement for any date range: /statement</i>"
    }
    lines.append(stmt_hint.get(lang, stmt_hint['en']))

    return "\n".join(lines)

def format_back_message(lang: str) -> str:
    """Returns the localized response when user presses or types Back."""
    msgs = {
        'hi': "🔙 <b>मुख्य मेनू:</b>\nनीचे दिए गए कीबोर्ड से कोई भी विकल्प चुनें 👇",
        'bn': "🔙 <b>মূল মেনু:</b>\nনিচের কিবোর্ড থেকে বিকল্প নির্বাচন করুন 👇",
        'ur': "🔙 <b>مین مینو:</b>\nنیچے دیے گئے کی بورڈ سے آپشن منتخب کریں 👇",
        'ru': "🔙 <b>Главное меню:</b>\nВыберите действие из меню ниже 👇",
        'es': "🔙 <b>Menú Principal:</b>\nElija una opción del menú 👇",
        'pt': "🔙 <b>Menu Principal:</b>\nEscolha uma opção do menu 👇",
        'ar': "🔙 <b>القائمة الرئيسية:</b>\nاختر خياراً من القائمة أدناه 👇",
        'id': "🔙 <b>Menu Utama:</b>\nSilakan pilih menu di bawah ini 👇",
        'fr': "🔙 <b>Menu Principal :</b>\nChoisissez une option dans le menu ci-dessous 👇",
        'de': "🔙 <b>Hauptmenü:</b>\nWählen Sie eine Option aus dem Menü unten 👇",
        'it': "🔙 <b>Menu Principale:</b>\nScegli un'opzione dal menu sottostante 👇",
        'tr': "🔙 <b>Ana Menü:</b>\nAşağıdaki menüden bir seçenek seçin 👇",
        'vi': "🔙 <b>Menu Chính:</b>\nChọn một tuỳ chọn bên dưới 👇",
        'ja': "🔙 <b>メインメニュー:</b>\n下のメニューから操作を選択してください 👇",
        'ko': "🔙 <b>메인 메뉴:</b>\n아래 메뉴에서 옵션을 선택하세요 👇",
        'uk': "🔙 <b>Головне меню:</b>\nОберіть дію з меню нижче 👇",
        'uz': "🔙 <b>Asosiy menyu:</b>\nQuyidagi menyudan birini tanlang 👇",
        'kk': "🔙 <b>Басты мәзір:</b>\nТөмендегі мәзірден әрекетті таңдаңыз 👇",
        'en': "🔙 <b>Main Menu:</b>\nChoose an option from the menu below 👇"
    }
    return msgs.get(lang, msgs['en'])

def format_daily_summary(lang: str, today_str: str, curr_sym: str, today_tot: float, month_tot: float, budget: float = 0.0, is_india: bool = False) -> str:
    """Renders the 9:00 PM nightly summary in the user's language."""
    headers = {
        'hi': f"🌙 <b>Hisab-Kitab: आज का दैनिक हिसाब ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nआज आपने कुल <b>{curr_sym}{today_tot:,.0f}</b> खर्च किए!\n\n📅 इस महीने का कुल खर्चा: <b>{curr_sym}{month_tot:,.0f}</b>",
        'bn': f"🌙 <b>Hisab-Kitab: দৈনিক হিসাব ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nআজ আপনি মোট <b>{curr_sym}{today_tot:,.0f}</b> খরচ করেছেন!\n\n📅 এই মাসের মোট খরচ: <b>{curr_sym}{month_tot:,.0f}</b>",
        'ur': f"🌙 <b>Hisab-Kitab: روزانہ کا حساب ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nآج آپ نے کل <b>{curr_sym}{today_tot:,.0f}</b> خرچ کیے!\n\n📅 اس ماہ کا کل خرچ: <b>{curr_sym}{month_tot:,.0f}</b>",
        'ru': f"🌙 <b>Hisab-Kitab: Итоги дня ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nСегодня вы потратили всего <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 Расходы за месяц: <b>{curr_sym}{month_tot:,.0f}</b>",
        'es': f"🌙 <b>Hisab-Kitab: Resumen Diario ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nHoy gastaste un total de <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 Gasto de este mes: <b>{curr_sym}{month_tot:,.0f}</b>",
        'pt': f"🌙 <b>Hisab-Kitab: Resumo Diário ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nHoje você gastou um total de <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 Gastos deste mês: <b>{curr_sym}{month_tot:,.0f}</b>",
        'ar': f"🌙 <b>Hisab-Kitab: الملخص اليومي ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nلقد صرفت اليوم ما مجموعه <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 مصاريف هذا الشهر: <b>{curr_sym}{month_tot:,.0f}</b>",
        'id': f"🌙 <b>Hisab-Kitab: Rekap Harian ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nHari ini Anda membelanjakan <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 Pengeluaran bulan ini: <b>{curr_sym}{month_tot:,.0f}</b>",
        'en': f"🌙 <b>Hisab-Kitab: Daily Recap ({today_str})</b>\n━━━━━━━━━━━━━━━━━━━\nToday you spent a total of <b>{curr_sym}{today_tot:,.0f}</b>.\n\n📅 This month's total spending: <b>{curr_sym}{month_tot:,.0f}</b>"
    }
    text = headers.get(lang, headers['en'])

    if budget > 0:
        rem = max(0.0, budget - month_tot)
        if lang == 'hi':
            text += f"\n💰 बचा हुआ बजट: <b>{curr_sym}{rem:,.0f}</b> (कुल {curr_sym}{budget:,.0f} में से)"
        elif lang == 'ru':
            text += f"\n💰 Остаток бюджета: <b>{curr_sym}{rem:,.0f}</b> (из {curr_sym}{budget:,.0f})"
        else:
            text += f"\n💰 Budget remaining: <b>{curr_sym}{rem:,.0f}</b> (out of {curr_sym}{budget:,.0f})"

    if is_india:
        text += f"\n━━━━━━━━━━━━━━━━━━━\n🔥 <i>आज के टॉप 90% लूट डील्स: <a href='{DEALS_FETCHER_URL}'>Deals Fetcher</a></i>"

    return text

def format_del_response(lang: str, tx_id: int, deleted: dict, curr_sym: str, today_tot: float, remaining: list) -> str:
    """Formats the inline message text when an entry is deleted."""
    if lang == 'hi':
        if remaining:
            return (
                f"🗑️ <b>एंट्री #{tx_id} हटा दी गई!</b> ({curr_sym}{deleted['amount']:,.0f} {deleted['category']})\n"
                f"📊 आज का कुल खर्चा: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"आप किसी और एंट्री को हटाना चाहते हैं तो नीचे टैप करें, या 'सब ठीक है' दबाएं 👇"
            )
        else:
            return (
                f"🗑️ <b>एंट्री #{tx_id} हटा दी गई!</b>\n"
                f"📊 आज का कुल खर्चा: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"ℹ️ हालिया लिस्ट में अब कोई एंट्री नहीं बची है।"
            )
    elif lang == 'ru':
        if remaining:
            return (
                f"🗑️ <b>Запись #{tx_id} удалена!</b> ({curr_sym}{deleted['amount']:,.0f} {deleted['category']})\n"
                f"📊 Всего за сегодня: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"Чтобы удалить другие записи, выберите их ниже 👇"
            )
        else:
            return (
                f"🗑️ <b>Запись #{tx_id} удалена!</b>\n"
                f"📊 Всего за сегодня: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"ℹ️ В списке больше нет записей."
            )
    else:
        if remaining:
            return (
                f"🗑️ <b>Entry #{tx_id} Deleted!</b> ({curr_sym}{deleted['amount']:,.0f} {deleted['category']})\n"
                f"📊 Today's Total: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"Tap another entry to delete, or tap 'Done / Keep Others' below 👇"
            )
        else:
            return (
                f"🗑️ <b>Entry #{tx_id} Deleted!</b>\n"
                f"📊 Today's Total: <b>{curr_sym}{today_tot:,.0f}</b>\n\n"
                f"ℹ️ No more entries in recent list."
            )


# ==========================================
# STATEMENT I18N (PDF & EXCEL LOCALIZATION)
# ==========================================
# -*- coding: utf-8 -*-
STATEMENT_I18N = {
    'en': {
        'doc_title': "FINANCIAL STATEMENT OF ACCOUNTS",
        'subtitle_system': "Enterprise Financial Management & Audit System",
        'lbl_period': "Reporting Period",
        'lbl_account_holder': "Account Holder",
        'lbl_account_id': "Account Reference ID",
        'lbl_jurisdiction': "Country / Jurisdiction",
        'lbl_currency': "Base Currency",
        'lbl_issue_date': "Issue Timestamp",
        'lbl_audit_ref': "Audit Document Ref",
        'sec_summary': "EXECUTIVE FINANCIAL DASHBOARD",
        'kpi_income': "Total Inflow (Income)",
        'kpi_expense': "Total Outflow (Expenses)",
        'kpi_net': "Net Operating Balance",
        'kpi_budget': "Budget Allocation",
        'kpi_variance': "Budget Remaining",
        'sec_breakdown': "EXPENDITURE BREAKDOWN BY CATEGORY",
        'col_category': "Category / Classification",
        'col_count': "Transactions",
        'col_spent': "Total Spent",
        'col_share': "Allocation (%)",
        'sec_ledger': "CHRONOLOGICAL TRANSACTION AUDIT LEDGER",
        'col_date': "Posting Date",
        'col_desc': "Particulars / Memo",
        'col_type': "Classification",
        'col_amount': "Net Value",
        'type_income': "Inflow (Income)",
        'type_expense': "Outflow (Expense)",
        'no_records': "No itemized transactions recorded in this accounting period.",
        'sheet_summary': "Financial Summary",
        'sheet_ledger': "Audit Ledger",
        'footer_notice': "STRICTLY CONFIDENTIAL FINANCIAL RECORD • PREPARED ELECTRONICALLY FOR AUTHORIZED ENTITY ONLY • GENERATED IN ACCORDANCE WITH INTERNAL AUDIT COMPLIANCE STANDARDS"
    },
    'hi': {
        'doc_title': "वित्तीय खाता विवरण (FINANCIAL STATEMENT)",
        'subtitle_system': "एंटरप्राइज वित्तीय प्रबंधन एवं ऑडिट प्रणाली",
        'lbl_period': "विवरण अवधि",
        'lbl_account_holder': "खाता धारक",
        'lbl_account_id': "खाता संदर्भ संख्या",
        'lbl_jurisdiction': "देश / क्षेत्राधिकार",
        'lbl_currency': "मूल मुद्रा",
        'lbl_issue_date': "जारी करने का समय",
        'lbl_audit_ref': "ऑडिट संदर्भ कोड",
        'sec_summary': "कार्यकारी वित्तीय सारांश (EXECUTIVE DASHBOARD)",
        'kpi_income': "कुल प्राप्तियां (आय)",
        'kpi_expense': "कुल भुगतान (खर्च)",
        'kpi_net': "शुद्ध परिचालन शेष (Net Balance)",
        'kpi_budget': "आवंटित बजट",
        'kpi_variance': "बचा हुआ बजट (Surplus)",
        'sec_breakdown': "श्रेणीवार खर्च विश्लेषण तालिका",
        'col_category': "व्यय श्रेणी",
        'col_count': "प्रविष्टियां (Count)",
        'col_spent': "खर्च राशि",
        'col_share': "अनुपात (%)",
        'sec_ledger': "कालक्रमानुसार लेन-देन ऑडिट खाता (Ledger)",
        'col_date': "प्रविष्टि तारीख",
        'col_desc': "विवरण / प्रयोजन",
        'col_type': "वर्गीकरण",
        'col_amount': "शुद्ध राशि",
        'type_income': "आय (Inflow)",
        'type_expense': "खर्च (Outflow)",
        'no_records': "इस लेखा अवधि में कोई लेन-देन दर्ज नहीं है।",
        'sheet_summary': "वित्तीय सारांश",
        'sheet_ledger': "ऑडिट लेजर",
        'footer_notice': "अत्यंत गोपनीय वित्तीय दस्तावेज • केवल अधिकृत व्यक्ति/संस्था के उपयोग हेतु • आंतरिक लेखा परीक्षा अनुपालन मानकों के तहत स्वचालित रूप से तैयार"
    },
    'bn': {
        'doc_title': "আর্থিক হিসাব বিবরণী (FINANCIAL STATEMENT)",
        'subtitle_system': "এন্টারপ্রাইজ আর্থিক ব্যবস্থাপনা ও অডিট সিস্টেম",
        'lbl_period': "রিপোর্টিং মেয়াদ",
        'lbl_account_holder': "হিসাবধারী",
        'lbl_account_id': "অ্যাকাউন্ট রেফারেন্স আইডি",
        'lbl_jurisdiction': "এখতিয়ার / দেশ",
        'lbl_currency': "মূল মুদ্রা",
        'lbl_issue_date': "ইস্যুর সময়",
        'lbl_audit_ref': "অডিট রেফারেন্স কোড",
        'sec_summary': "নির্বাহী আর্থিক ড্যাশবোর্ড (EXECUTIVE DASHBOARD)",
        'kpi_income': "মোট আয় (Inflow)",
        'kpi_expense': "মোট খরচ (Outflow)",
        'kpi_net': "নিট ব্যালেন্স (Net Balance)",
        'kpi_budget': "বরাদ্দকৃত বাজেট",
        'kpi_variance': "অবশিষ্ট বাজেট",
        'sec_breakdown': "বিভাগ অনুযায়ী খরচ বিশ্লেষণ",
        'col_category': "খরচের বিভাগ",
        'col_count': "লেনদেন সংখ্যা",
        'col_spent': "মোট খরচ",
        'col_share': "অনুপাত (%)",
        'sec_ledger': "ধারাবাহিক লেনদেন অডিট লেজার",
        'col_date': "পোস্টিং তারিখ",
        'col_desc': "বিবরণ / মেমো",
        'col_type': "শ্রেণিবিভাগ",
        'col_amount': "মোট অঙ্ক",
        'type_income': "আয় (Inflow)",
        'type_expense': "খরচ (Outflow)",
        'no_records': "এই হিসাব মেয়াদে কোনো লেনদেন লিপিবদ্ধ নেই।",
        'sheet_summary': "আর্থিক সারসংক্ষেপ",
        'sheet_ledger': "অডিট লেজার",
        'footer_notice': "সম্পূর্ণ গোপনীয় আর্থিক বিবরণী • কেবল অনুমোদিত সত্তার ব্যবহারের জন্য • অভ্যন্তরীণ অডিট মান অনুসারে প্রস্তুত"
    },
    'ur': {
        'doc_title': "مالیاتی کھاتے کا گوشوارہ (FINANCIAL STATEMENT)",
        'subtitle_system': "انٹرپرائز مالیاتی انتظام و آڈٹ سسٹم",
        'lbl_period': "رپورٹنگ کی مدت",
        'lbl_account_holder': "اکاؤنٹ ہولڈر",
        'lbl_account_id': "اکاؤنٹ حوالہ نمبر",
        'lbl_jurisdiction': "ملک / دائرہ اختیار",
        'lbl_currency': "بنیادی کرنسی",
        'lbl_issue_date': "اجرا کا وقت",
        'lbl_audit_ref': "آڈٹ ریفرنس کوڈ",
        'sec_summary': "ایگزیکٹو مالیاتی ڈیش بورڈ",
        'kpi_income': "کل آمدنی (Inflow)",
        'kpi_expense': "کل اخراجات (Outflow)",
        'kpi_net': "خالص بیلنس (Net)",
        'kpi_budget': "مقررہ بجٹ",
        'kpi_variance': "باقی بجٹ",
        'sec_breakdown': "شعبہ وار اخراجات کی تفصیل",
        'col_category': "شعبہ / زمرہ",
        'col_count': "اندراجات",
        'col_spent': "کل خرچ",
        'col_share': "تناسب (%)",
        'sec_ledger': "تاریخ وار لین دین کا آڈٹ لیجر",
        'col_date': "تاریخ",
        'col_desc': "تفصیل / مد",
        'col_type': "درجہ بندی",
        'col_amount': "خالص رقم",
        'type_income': "آمدنی (Inflow)",
        'type_expense': "خرچ (Outflow)",
        'no_records': "اس مدت میں کوئی لین دین درج نہیں ہے۔",
        'sheet_summary': "مالیاتی خلاصہ",
        'sheet_ledger': "آڈٹ لیجر",
        'footer_notice': "انتہائی خفیہ مالیاتی دستاویز • صرف مجاز استعمال کے لیے • اندرونی آڈٹ کے معیارات کے مطابق خودکار تیار کردہ"
    },
    'es': {
        'doc_title': "ESTADO FINANCIERO DE CUENTAS",
        'subtitle_system': "Sistema Corporativo de Gestión Financiera y Auditoría",
        'lbl_period': "Período del Informe",
        'lbl_account_holder': "Titular de la Cuenta",
        'lbl_account_id': "ID de Referencia de Cuenta",
        'lbl_jurisdiction': "País / Jurisdicción",
        'lbl_currency': "Moneda Base",
        'lbl_issue_date': "Fecha de Emisión",
        'lbl_audit_ref': "Ref. de Auditoría",
        'sec_summary': "PANEL FINANCIERO EJECUTIVO",
        'kpi_income': "Entradas Totales (Ingresos)",
        'kpi_expense': "Salidas Totales (Gastos)",
        'kpi_net': "Saldo Operativo Neto",
        'kpi_budget': "Presupuesto Asignado",
        'kpi_variance': "Presupuesto Restante",
        'sec_breakdown': "DESGLOSE DE GASTOS POR CATEGORÍA",
        'col_category': "Categoría / Clasificación",
        'col_count': "Transacciones",
        'col_spent': "Total Gastado",
        'col_share': "Participación (%)",
        'sec_ledger': "LIBRO MAYOR CRONOLÓGICO DE AUDITORÍA",
        'col_date': "Fecha de Registro",
        'col_desc': "Concepto / Detalle",
        'col_type': "Clasificación",
        'col_amount': "Importe Neto",
        'type_income': "Ingreso (Entrada)",
        'type_expense': "Gasto (Salida)",
        'no_records': "No hay transacciones registradas en este período contable.",
        'sheet_summary': "Resumen Financiero",
        'sheet_ledger': "Libro de Auditoría",
        'footer_notice': "DOCUMENTO FINANCIERO ESTRICTAMENTE CONFIDENCIAL • SOLO PARA USO AUTORIZADO • CUMPLE CON NORMAS DE AUDITORÍA INTERNA"
    },
    'pt': {
        'doc_title': "DEMONSTRATIVO FINANCEIRO DE CONTAS",
        'subtitle_system': "Sistema Corporativo de Gestão Financeira e Auditoria",
        'lbl_period': "Período do Relatório",
        'lbl_account_holder': "Titular da Conta",
        'lbl_account_id': "ID de Referência da Conta",
        'lbl_jurisdiction': "País / Jurisdição",
        'lbl_currency': "Moeda Base",
        'lbl_issue_date': "Data de Emissão",
        'lbl_audit_ref': "Ref. de Auditoria",
        'sec_summary': "PAINEL FINANCEIRO EXECUTIVO",
        'kpi_income': "Entradas Totais (Receitas)",
        'kpi_expense': "Saídas Totais (Despesas)",
        'kpi_net': "Saldo Operacional Líquido",
        'kpi_budget': "Orçamento Alocado",
        'kpi_variance': "Saldo Orçamentário",
        'sec_breakdown': "DETALHAMENTO DE DESPESAS POR CATEGORIA",
        'col_category': "Categoria / Classificação",
        'col_count': "Transações",
        'col_spent': "Total Gasto",
        'col_share': "Proporção (%)",
        'sec_ledger': "LIVRO RAZÃO CRONOLÓGICO DE AUDITORIA",
        'col_date': "Data de Lançamento",
        'col_desc': "Histórico / Detalhe",
        'col_type': "Classificação",
        'col_amount': "Valor Líquido",
        'type_income': "Receita (Entrada)",
        'type_expense': "Despesa (Saída)",
        'no_records': "Nenhuma transação registrada neste período contábil.",
        'sheet_summary': "Resumo Financeiro",
        'sheet_ledger': "Razão de Auditoria",
        'footer_notice': "DOCUMENTO FINANCEIRO ESTRITAMENTE CONFIDENCIAL • EXCLUSIVO PARA USO AUTORIZADO • EM CONFORMIDADE COM NORMAS DE AUDITORIA"
    },
    'ru': {
        'doc_title': "ФИНАНСОВЫЙ ОТЧЕТ ПО СЧЕТАМ",
        'subtitle_system': "Корпоративная система финансового учета и аудита",
        'lbl_period': "Отчетный период",
        'lbl_account_holder': "Владелец счета",
        'lbl_account_id': "Идентификатор счета",
        'lbl_jurisdiction': "Страна / Юрисдикция",
        'lbl_currency': "Базовая валюта",
        'lbl_issue_date': "Дата формирования",
        'lbl_audit_ref': "Код аудита",
        'sec_summary': "СВОДКА ФИНАНСОВЫХ ПОКАЗАТЕЛЕЙ",
        'kpi_income': "Общий приход (Доход)",
        'kpi_expense': "Общий расход (Затраты)",
        'kpi_net': "Чистый операционный баланс",
        'kpi_budget': "Выделенный бюджет",
        'kpi_variance': "Остаток бюджета",
        'sec_breakdown': "СТРУКТУРА РАСХОДОВ ПО КАТЕГОРИЯМ",
        'col_category': "Категория расходов",
        'col_count': "Кол-во записей",
        'col_spent': "Сумма расходов",
        'col_share': "Доля (%)",
        'sec_ledger': "ХРОНОЛОГИЧЕСКИЙ ЖУРНАЛ ОПЕРАЦИЙ (АУДИТ)",
        'col_date': "Дата проводки",
        'col_desc': "Назначение платежа / Примечание",
        'col_type': "Классификация",
        'col_amount': "Сумма операции",
        'type_income': "Приход (Доход)",
        'type_expense': "Расход (Затраты)",
        'no_records': "За указанный отчетный период операции отсутствуют.",
        'sheet_summary': "Сводный отчет",
        'sheet_ledger': "Журнал операций",
        'footer_notice': "СТРОГО КОНФИДЕНЦИАЛЬНЫЙ ФИНАНСОВЫЙ ДОКУМЕНТ • ТОЛЬКО ДЛЯ АВТОРИЗОВАННОГО ИСПОЛЬЗОВАНИЯ • СИСТЕМНЫЙ АУДИТ"
    },
    'ar': {
        'doc_title': "كشف الحسابات المالية (FINANCIAL STATEMENT)",
        'subtitle_system': "نظام الإدارة المالية والتدقيق المالي للمؤسسات",
        'lbl_period': "فترة التقرير",
        'lbl_account_holder': "صاحب الحساب",
        'lbl_account_id': "رقم مرجع الحساب",
        'lbl_jurisdiction': "الدولة / الاختصاص القضائي",
        'lbl_currency': "العملة الأساسية",
        'lbl_issue_date': "تاريخ ووقت الإصدار",
        'lbl_audit_ref': "رمز مرجع التدقيق",
        'sec_summary': "لوحة المؤشرات المالية التنفيذية",
        'kpi_income': "إجمالي المقبوضات (الدخل)",
        'kpi_expense': "إجمالي المدفوعات (المصاريف)",
        'kpi_net': "صافي الرصيد التشغيلي",
        'kpi_budget': "الميزانية المخصصة",
        'kpi_variance': "الميزانية المتبقية",
        'sec_breakdown': "تفصيل المصروفات حسب الفئة",
        'col_category': "الفئة / البند",
        'col_count': "عدد المعاملات",
        'col_spent': "إجمالي المصروف",
        'col_share': "النسبة (%)",
        'sec_ledger': "سجل المعاملات والتدقيق المالي الزمني",
        'col_date': "تاريخ القيد",
        'col_desc': "البيان / الملاحظة",
        'col_type': "التصنيف",
        'col_amount': "القيمة الصافية",
        'type_income': "دخل (مقبوضات)",
        'type_expense': "مصروف (مدفوعات)",
        'no_records': "لا توجد حركات مسجلة خلال هذه الفترة المحاسبية.",
        'sheet_summary': "الملخص المالي",
        'sheet_ledger': "دفتر الأستاذ",
        'footer_notice': "وثيقة مالية سرية للغاية • للاستخدام المصرح به فقط • مطابقة لمعايير التدقيق المالي الداخلي"
    },
    'id': {
        'doc_title': "LAPORAN KEUANGAN REKENING",
        'subtitle_system': "Sistem Manajemen Keuangan dan Audit Perusahaan",
        'lbl_period': "Periode Laporan",
        'lbl_account_holder': "Pemilik Rekening",
        'lbl_account_id': "ID Referensi Rekening",
        'lbl_jurisdiction': "Negara / Yurisdiksi",
        'lbl_currency': "Mata Uang Dasar",
        'lbl_issue_date': "Waktu Penerbitan",
        'lbl_audit_ref': "Ref. Audit Dokumen",
        'sec_summary': "DASHBOARD KEUANGAN EKSEKUTIF",
        'kpi_income': "Total Arus Masuk (Pemasukan)",
        'kpi_expense': "Total Arus Keluar (Pengeluaran)",
        'kpi_net': "Saldo Operasional Bersih",
        'kpi_budget': "Alokasi Anggaran",
        'kpi_variance': "Sisa Anggaran",
        'sec_breakdown': "RINCIAN PENGELUARAN BERDASARKAN KATEGORI",
        'col_category': "Kategori / Klasifikasi",
        'col_count': "Jumlah Transaksi",
        'col_spent': "Total Dibelanjakan",
        'col_share': "Porsi (%)",
        'sec_ledger': "BUKU BESAR AUDIT TRANSAKSI KRONOLOGIS",
        'col_date': "Tanggal Pembukuan",
        'col_desc': "Keterangan / Memo",
        'col_type': "Klasifikasi",
        'col_amount': "Nilai Bersih",
        'type_income': "Pemasukan (Masuk)",
        'type_expense': "Pengeluaran (Keluar)",
        'no_records': "Tidak ada transaksi tercatat dalam periode akuntansi ini.",
        'sheet_summary': "Ringkasan Keuangan",
        'sheet_ledger': "Buku Besar Audit",
        'footer_notice': "DOKUMEN KEUANGAN SANGAT RAHASIA • HANYA UNTUK PENGGUNAAN RESMI • SESUAI STANDAR AUDIT INTERNAL"
    },
    'fr': {
        'doc_title': "ÉTAT FINANCIER DES COMPTES",
        'subtitle_system': "Système d'Audit et de Gestion Financière d'Entreprise",
        'lbl_period': "Période de Référence",
        'lbl_account_holder': "Titulaire du Compte",
        'lbl_account_id': "ID Référence Compte",
        'lbl_jurisdiction': "Pays / Juridiction",
        'lbl_currency': "Devise de Base",
        'lbl_issue_date': "Date d'Émission",
        'lbl_audit_ref': "Réf. d'Audit",
        'sec_summary': "TABLEAU DE BORD FINANCIER EXÉCUTIF",
        'kpi_income': "Total des Entrées (Revenus)",
        'kpi_expense': "Total des Sorties (Dépenses)",
        'kpi_net': "Solde d'Exploitation Net",
        'kpi_budget': "Budget Alloué",
        'kpi_variance': "Solde Budgétaire",
        'sec_breakdown': "VENTILATION DES DÉPENSES PAR CATÉGORIE",
        'col_category': "Catégorie / Classement",
        'col_count': "Opérations",
        'col_spent': "Total Dépensé",
        'col_share': "Part (%)",
        'sec_ledger': "GRAND LIVRE D'AUDIT CHRONOLOGIQUE",
        'col_date': "Date d'Écriture",
        'col_desc': "Libellé / Détail",
        'col_type': "Classement",
        'col_amount': "Montant Net",
        'type_income': "Revenu (Entrée)",
        'type_expense': "Dépense (Sortie)",
        'no_records': "Aucune opération enregistrée sur cette période comptable.",
        'sheet_summary': "Synthèse Financière",
        'sheet_ledger': "Grand Livre",
        'footer_notice': "DOCUMENT FINANCIER STRICTEMENT CONFIDENTIEL • USAGE AUTORISÉ UNIQUEMENT • CONFORME AUX NORMES D'AUDIT INTERNE"
    },
    'de': {
        'doc_title': "FINANZBERICHT & KONTOAUSZUG",
        'subtitle_system': "Unternehmensfinanzmanagement- & Auditsystem",
        'lbl_period': "Abrechnungszeitraum",
        'lbl_account_holder': "Kontoinhaber",
        'lbl_account_id': "Konto-Referenznummer",
        'lbl_jurisdiction': "Land / Gerichtsstand",
        'lbl_currency': "Basiswährung",
        'lbl_issue_date': "Erstellungszeitpunkt",
        'lbl_audit_ref': "Audit-Referenzcode",
        'sec_summary': "FINANZÜBERSICHT FÜR DIE GESCHÄFTSLEITUNG",
        'kpi_income': "Gesamteinnahmen (Zufluss)",
        'kpi_expense': "Gesamtausgaben (Abfluss)",
        'kpi_net': "Nettobetriebsergebnis",
        'kpi_budget': "Budgetrahmen",
        'kpi_variance': "Verbleibendes Budget",
        'sec_breakdown': "AUSGABENSTRUKTUR NACH KATEGORIEN",
        'col_category': "Kategorie / Bereich",
        'col_count': "Buchungen",
        'col_spent': "Gesamtbetrag",
        'col_share': "Anteil (%)",
        'sec_ledger': "CHRONOLOGISCHES AUDIT-TRANSAKTIONSJOURNAL",
        'col_date': "Buchungsdatum",
        'col_desc': "Verwendungszweck / Buchungstext",
        'col_type': "Klassifizierung",
        'col_amount': "Nettobetrag",
        'type_income': "Einnahme (Zufluss)",
        'type_expense': "Ausgabe (Abfluss)",
        'no_records': "In diesem Abrechnungszeitraum wurden keine Transaktionen erfasst.",
        'sheet_summary': "Finanzübersicht",
        'sheet_ledger': "Audit-Journal",
        'footer_notice': "STRENG VERTRAULICHES FINANZDOKUMENT • NUR FÜR AUTORISIERTE NUTZUNG • ENTSPRICHT INTERNEN AUDIT-STANDARDS"
    },
    'it': {
        'doc_title': "RENDICONTO FINANZIARIO DEI CONTI",
        'subtitle_system': "Sistema di Gestione Finanziaria e Revisione Aziendale",
        'lbl_period': "Periodo di Rendicontazione",
        'lbl_account_holder': "Intestatario del Conto",
        'lbl_account_id': "ID Riferimento Conto",
        'lbl_jurisdiction': "Paese / Giurisdizione",
        'lbl_currency': "Valuta Base",
        'lbl_issue_date': "Data di Emissione",
        'lbl_audit_ref': "Rif. Audit Documento",
        'sec_summary': "CRUSCOTTO FINANZIARIO ESECUTIVO",
        'kpi_income': "Entrate Totali (Incassi)",
        'kpi_expense': "Uscite Totali (Spese)",
        'kpi_net': "Saldo Operativo Netto",
        'kpi_budget': "Budget Stanziato",
        'kpi_variance': "Budget Residuo",
        'sec_breakdown': "RIPARTIZIONE DELLE SPESE PER CATEGORIA",
        'col_category': "Categoria / Voce",
        'col_count': "Operazioni",
        'col_spent': "Totale Speso",
        'col_share': "Percentuale (%)",
        'sec_ledger': "MASTRO CRONOLOGICO DI AUDIT TRANSAZIONI",
        'col_date': "Data Contabile",
        'col_desc': "Causale / Descrizione",
        'col_type': "Classificazione",
        'col_amount': "Importo Netto",
        'type_income': "Entrata (Incasso)",
        'type_expense': "Uscita (Spesa)",
        'no_records': "Nessuna operazione registrata nel periodo contabile selezionato.",
        'sheet_summary': "Riepilogo Finanziario",
        'sheet_ledger': "Mastro di Audit",
        'footer_notice': "DOCUMENTO FINANZIARIO STRETTAMENTE RISERVATO • ESCLUSIVO USO AUTORIZZATO • CONFORME AGLI STANDARD DI REVISIONE INTERNA"
    },
    'tr': {
        'doc_title': "HESAP MALİ TABLOSU",
        'subtitle_system': "Kurumsal Finansal Yönetim ve Denetim Sistemi",
        'lbl_period': "Raporlama Dönemi",
        'lbl_account_holder': "Hesap Sahibi",
        'lbl_account_id': "Hesap Referans No",
        'lbl_jurisdiction': "Ülke / Yetki Alanı",
        'lbl_currency': "Temel Para Birimi",
        'lbl_issue_date': "Düzenlenme Tarihi",
        'lbl_audit_ref': "Denetim Referans Kodu",
        'sec_summary': "YÖNETİCİ FİNANSAL GÖSTERGE PANELİ",
        'kpi_income': "Toplam Giriş (Gelir)",
        'kpi_expense': "Toplam Çıkış (Gider)",
        'kpi_net': "Net Faaliyet Bakiyesi",
        'kpi_budget': "Tahsis Edilen Bütçe",
        'kpi_variance': "Kalan Bütçe",
        'sec_breakdown': "KATEGORİLERE GÖRE HARCAMA DAĞILIMI",
        'col_category': "Kategori / Sınıflandırma",
        'col_count': "İşlem Sayısı",
        'col_spent': "Toplam Harcama",
        'col_share': "Oran (%)",
        'sec_ledger': "KRONOLOJİK İŞLEM DENETİM DEFTERİ",
        'col_date': "Kayıt Tarihi",
        'col_desc': "Açıklama / Not",
        'col_type': "Sınıflandırma",
        'col_amount': "Net Tutar",
        'type_income': "Gelir (Giriş)",
        'type_expense': "Gider (Çıkış)",
        'no_records': "Bu muhasebe döneminde kaydedilmiş işlem bulunmamaktadır.",
        'sheet_summary': "Finansal Özet",
        'sheet_ledger': "Denetim Defteri",
        'footer_notice': "KESİNLİKLE GİZLİ MALİ BELGE • YALNIZCA YETKİLİ KULLANIM İÇİNDİR • İÇ DENETİM STANDARTLARINA UYGUNDUR"
    },
    'vi': {
        'doc_title': "BÁO CÁO TÀI CHÍNH TÀI KHOẢN",
        'subtitle_system': "Hệ Thống Kiểm Toán & Quản Trị Tài Chính Doanh Nghiệp",
        'lbl_period': "Kỳ Báo Cáo",
        'lbl_account_holder': "Chủ Tài Khoản",
        'lbl_account_id': "Mã Tham Chiếu Tài Khoản",
        'lbl_jurisdiction': "Quốc Gia / Khu Vực",
        'lbl_currency': "Đơn Vị Tiền Tệ",
        'lbl_issue_date': "Thời Gian Thiết Lập",
        'lbl_audit_ref': "Mã Kiểm Toán",
        'sec_summary': "BẢNG ĐIỀU HÀNH TÀI CHÍNH",
        'kpi_income': "Tổng Thu Vào (Thu Nhập)",
        'kpi_expense': "Tổng Chi Ra (Chi Phí)",
        'kpi_net': "Số Dư Hoạt Động Thuần",
        'kpi_budget': "Ngân Sách Phân Bổ",
        'kpi_variance': "Ngân Sách Còn Lại",
        'sec_breakdown': "PHÂN TÍCH CHI PHÍ THEO HẠNG MỤC",
        'col_category': "Hạng Mục Chi Phí",
        'col_count': "Số Giao Dịch",
        'col_spent': "Tổng Chi",
        'col_share': "Tỷ Trọng (%)",
        'sec_ledger': "SỔ CÁI KIỂM TOÁN GIAO DỊCH THEO TRÌNH TỰ",
        'col_date': "Ngày Ghi Sổ",
        'col_desc': "Nội Dung / Diễn Giải",
        'col_type': "Phân Loại",
        'col_amount': "Giá Trị Ròng",
        'type_income': "Thu Vào (Thu Nhập)",
        'type_expense': "Chi Ra (Chi Phí)",
        'no_records': "Không có giao dịch nào được ghi nhận trong kỳ kế toán này.",
        'sheet_summary': "Tổng Quan Tài Chính",
        'sheet_ledger': "Sổ Cái Kiểm Toán",
        'footer_notice': "TÀI LIỆU TÀI CHÍNH BẢO MẬT TUYỆT ĐỐI • CHỈ DÀNH CHO MỤC ĐÍCH ĐƯỢC ỦY QUYỀN • TUÂN THỦ TIÊU CHUẨN KIỂM TOÁN NỘI BỘ"
    },
    'ja': {
        'doc_title': "財務諸表・勘定報告書",
        'subtitle_system': "企業財務管理および内部監査システム",
        'lbl_period': "報告対象期間",
        'lbl_account_holder': "口座名義人",
        'lbl_account_id': "口座参照番号",
        'lbl_jurisdiction': "国／管轄",
        'lbl_currency': "基準通貨",
        'lbl_issue_date': "発行日時",
        'lbl_audit_ref': "監査参照コード",
        'sec_summary': "エグゼクティブ財務ダッシュボード",
        'kpi_income': "総流入額（収入）",
        'kpi_expense': "総流出額（支出）",
        'kpi_net': "純営業残高",
        'kpi_budget': "配分予算",
        'kpi_variance': "予算残額",
        'sec_breakdown': "費目別支出内訳",
        'col_category': "費目／分類",
        'col_count': "取引件数",
        'col_spent': "支出総額",
        'col_share': "構成比 (%)",
        'sec_ledger': "時系列取引監査元帳",
        'col_date': "記帳日",
        'col_desc': "摘要／備考",
        'col_type': "区分",
        'col_amount': "純額",
        'type_income': "収入（流入）",
        'type_expense': "支出（流出）",
        'no_records': "この会計期間に対象となる取引記録はありません。",
        'sheet_summary': "財務サマリー",
        'sheet_ledger': "監査元帳",
        'footer_notice': "極秘財務文書 • 承認された利用限定 • 内部監査基準準拠システム自動生成"
    },
    'ko': {
        'doc_title': "재무 계정 명세서",
        'subtitle_system': "기업 재무 관리 및 감사 시스템",
        'lbl_period': "보고 기간",
        'lbl_account_holder': "계정 소유자",
        'lbl_account_id': "계정 참조 ID",
        'lbl_jurisdiction': "국가 / 관할",
        'lbl_currency': "기본 통화",
        'lbl_issue_date': "발행 일시",
        'lbl_audit_ref': "감사 참조 코드",
        'sec_summary': "경영진 재무 대시보드",
        'kpi_income': "총 유입액 (수입)",
        'kpi_expense': "총 유출액 (지출)",
        'kpi_net': "순 영업 잔액",
        'kpi_budget': "배정 예산",
        'kpi_variance': "예산 잔여액",
        'sec_breakdown': "항목별 지출 분석표",
        'col_category': "항목 / 분류",
        'col_count': "거래 건수",
        'col_spent': "총 지출액",
        'col_share': "비중 (%)",
        'sec_ledger': "연대기적 거래 감사 원장",
        'col_date': "전기 일자",
        'col_desc': "적요 / 비고",
        'col_type': "구분",
        'col_amount': "순액",
        'type_income': "수입 (유입)",
        'type_expense': "지출 (유출)",
        'no_records': "해당 회계 기간에 기록된 거래 내역이 없습니다.",
        'sheet_summary': "재무 요약",
        'sheet_ledger': "감사 원장",
        'footer_notice': "대외비 재무 기록 • 승인된 사용자 전용 • 내부 감사 기준 준수 자동 생성"
    },
    'uk': {
        'doc_title': "ФІНАНСОВИЙ ЗВІТ ЗА РАХУНКАМИ",
        'subtitle_system': "Корпоративна система фінансового обліку та аудиту",
        'lbl_period': "Звітний період",
        'lbl_account_holder': "Власник рахунку",
        'lbl_account_id': "Ідентифікатор рахунку",
        'lbl_jurisdiction': "Країна / Юрисдикція",
        'lbl_currency': "Базова валюта",
        'lbl_issue_date': "Дата формування",
        'lbl_audit_ref': "Код аудиту",
        'sec_summary': "ЗВЕДЕННЯ ФІНАНСОВИХ ПОКАЗНИКІВ",
        'kpi_income': "Загальний прихід (Дохід)",
        'kpi_expense': "Загальні витрати",
        'kpi_net': "Чистий операційний баланс",
        'kpi_budget': "Виділений бюджет",
        'kpi_variance': "Залишок бюджету",
        'sec_breakdown': "СТРУКТУРА ВИТРАТ ЗА КАТЕГОРІЯМИ",
        'col_category': "Категорія витрат",
        'col_count': "К-ть записів",
        'col_spent': "Сума витрат",
        'col_share': "Частка (%)",
        'sec_ledger': "ХРОНОЛОГІЧНИЙ ЖУРНАЛ ОПЕРАЦІЙ (АУДИТ)",
        'col_date': "Дата проведення",
        'col_desc': "Призначення платежу / Примітка",
        'col_type': "Класифікація",
        'col_amount': "Сума операції",
        'type_income': "Прихід (Дохід)",
        'type_expense': "Витрата",
        'no_records': "За вказаний період операцій не зафіксовано.",
        'sheet_summary': "Фінансове зведення",
        'sheet_ledger': "Журнал аудиту",
        'footer_notice': "СУВОРО КОНФІДЕНЦІЙНИЙ ФІНАНСОВИЙ ДОКУМЕНТ • ЛИШЕ ДЛЯ АВТОРИЗОВАНОГО ВИКОРИСТАННЯ • ВІДПОВІДАЄ СТАНДАРТАМ ВНУТРІШНЬОГО АУДИТУ"
    },
    'uz': {
        'doc_title': "HISOB BO'YICHA MOLIYAVIY HISOBOT",
        'subtitle_system': "Korporativ moliyaviy boshqaruv va audit tizimi",
        'lbl_period': "Hisobot davri",
        'lbl_account_holder': "Hisob egasi",
        'lbl_account_id': "Hisob raqami kodi",
        'lbl_jurisdiction': "Mamlakat / Yurisdiksiya",
        'lbl_currency': "Asosiy valyuta",
        'lbl_issue_date': "Shakllantirilgan vaqt",
        'lbl_audit_ref': "Audit kodi",
        'sec_summary': "RAHBARIYAT MOLIYAVIY KO'RSATKICHLARI",
        'kpi_income': "Jami tushum (Daromad)",
        'kpi_expense': "Jami chiqim (Xarajat)",
        'kpi_net': "Sof operatsion qoldiq",
        'kpi_budget': "Ajratilgan byudjet",
        'kpi_variance': "Byudjet qoldig'i",
        'sec_breakdown': "XARAJATLARNING TOIFALAR BO'YICHA TAQSIMOTI",
        'col_category': "Xarajat toifasi",
        'col_count': "Amallar soni",
        'col_spent': "Sarflangan summa",
        'col_share': "Ulushi (%)",
        'sec_ledger': "XRONOLOGIK AMALLAR AUDIT DAFTARI",
        'col_date': "O'tkazilgan sana",
        'col_desc': "To'lov maqsadi / Izoh",
        'col_type': "Tasnif",
        'col_amount': "Sof miqdor",
        'type_income': "Kirim (Daromad)",
        'type_expense': "Chiqim (Xarajat)",
        'no_records': "Ushbu hisob davrida hech qanday operatsiya qayd etilmagan.",
        'sheet_summary': "Moliyaviy xulosa",
        'sheet_ledger': "Audit daftari",
        'footer_notice': "QAT'IY MAXFIY MOLIYAVIY HUJJAT • FAQAT RUXSAT ETILGAN FOYDALANUVCHILAR UCHUN • ICHKI AUDIT STANDARTLARIGA MOS"
    },
    'kk': {
        'doc_title': "ШОТТАР БОЙЫНША ҚАРЖЫЛЫҚ ЕСЕП",
        'subtitle_system': "Корпоративтік қаржылық басқару және аудит жүйесі",
        'lbl_period': "Есепті кезең",
        'lbl_account_holder': "Шот иесі",
        'lbl_account_id': "Шот анықтамалық коды",
        'lbl_jurisdiction': "Ел / Құзырет",
        'lbl_currency': "Негізгі валюта",
        'lbl_issue_date': "Берілген уақыты",
        'lbl_audit_ref': "Аудит коды",
        'sec_summary': "БАСҚАРМА ҚАРЖЫЛЫҚ КӨРСЕТКІШТЕРІ",
        'kpi_income': "Жалпы түсім (Кіріс)",
        'kpi_expense': "Жалпы шығыс (Шығын)",
        'kpi_net': "Таза операциялық қалдық",
        'kpi_budget': "Бөлінген бюджет",
        'kpi_variance': "Бюджет қалдығы",
        'sec_breakdown': "ШЫҒЫСТАРДЫҢ САНАТТАР БОЙЫНША ҚҰРЫЛЫМЫ",
        'col_category': "Шығыс санаты",
        'col_count': "Жазбалар саны",
        'col_spent': "Жұмсалған сома",
        'col_share': "Үлесі (%)",
        'sec_ledger': "ХРОНОЛОГИЯЛЫҚ ОПЕРАЦИЯЛАР АУДИТ ЖУРНАЛЫ",
        'col_date': "Жүргізілген күні",
        'col_desc': "Төлем мақсаты / Түсініктеме",
        'col_type': "Жіктеу",
        'col_amount': "Таза сома",
        'type_income': "Кіріс (Түсім)",
        'type_expense': "Шығыс (Шығын)",
        'no_records': "Осы есепті кезеңде тіркелген операциялар жоқ.",
        'sheet_summary': "Қаржылық шолу",
        'sheet_ledger': "Аудит журналы",
        'footer_notice': "ҚАТАҢ ҚҰПИЯ ҚАРЖЫЛЫҚ ҚҰЖАТ • ТЕК РҰҚСАТ ЕТІЛГЕН ТҰЛҒАЛАР ҮШІН • ІШКІ АУДИТ СТАНДАРТТАРЫНА СӘЙКЕС КЕЛЕДІ"
    }
}

def get_statement_str(key: str, lang: str = 'en') -> str:
    """Fetches localized label for PDF / Excel statement generation."""
    lang_dict = STATEMENT_I18N.get(lang, STATEMENT_I18N['en'])
    return lang_dict.get(key, STATEMENT_I18N['en'].get(key, key))


# ==========================================
# BUDGET & CLIENT INLINE KEYBOARDS
# ==========================================

def get_budget_prompt_keyboard(lang: str, current_budget: float, curr_sym: str) -> InlineKeyboardMarkup:
    """Provides Add to Budget vs Set New Budget buttons when user already has a budget."""
    lbl_add = f"➕ बजट में और जोड़ें (+{curr_sym})" if lang == 'hi' else f"➕ Add to Budget (+{curr_sym})"
    lbl_new = "✏️ नया बजट सेट करें" if lang == 'hi' else "✏️ Set New Budget"
    lbl_back = "🔙 मुख्य मेनू (Back)" if lang == 'hi' else "🔙 Main Menu"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lbl_add, callback_data="budget_opt_add")],
        [InlineKeyboardButton(lbl_new, callback_data="budget_opt_new")],
        [InlineKeyboardButton(lbl_back, callback_data="back_main")]
    ])

def get_clients_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Main menu inline keyboard for Client with Report Download options."""
    if lang == 'hi':
        lbl_add = "➕ नया ग्राहक जोड़ें (Add Client)"
        lbl_list = "📋 सभी ग्राहक देखें (View All)"
        lbl_summary = "📊 क्लाइंट सारांश (Summary)"
        lbl_pdf = "📄 PDF रिपोर्ट (Max 12M)"
        lbl_excel = "📊 Excel रिपोर्ट (Max 12M)"
        lbl_back = "🔙 मुख्य मेनू (Back)"
    elif lang == 'bn':
        lbl_add = "➕ নতুন গ্রাহক যোগ করুন"
        lbl_list = "📋 সকল গ্রাহক দেখুন"
        lbl_summary = "📊 ক্লায়েন্ট সারাংশ"
        lbl_pdf = "📄 PDF রিপোর্ট (Max 12M)"
        lbl_excel = "📊 Excel রিপোর্ট (Max 12M)"
        lbl_back = "🔙 মূল মেনু (Back)"
    else:
        lbl_add = "➕ Add New Client"
        lbl_list = "📋 View All Clients"
        lbl_summary = "📊 Client Summary Report"
        lbl_pdf = "📄 Download PDF (Max 12M)"
        lbl_excel = "📊 Download Excel (Max 12M)"
        lbl_back = "🔙 Back to Main Menu"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lbl_add, callback_data="client_action_add")],
        [InlineKeyboardButton(lbl_list, callback_data="client_action_list_1")],
        [InlineKeyboardButton(lbl_summary, callback_data="client_action_summary")],
        [
            InlineKeyboardButton(lbl_pdf, callback_data="cl_fmt_all_pdf"),
            InlineKeyboardButton(lbl_excel, callback_data="cl_fmt_all_excel")
        ],
        [InlineKeyboardButton(lbl_back, callback_data="back_main")]
    ])

def get_client_skip_phone_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Allows skipping phone number entry when creating a client."""
    lbl_skip = "⏩ छोड़ें (Skip Phone)" if lang == 'hi' else "⏩ Skip Phone"
    lbl_cancel = "❌ रद्द करें (Cancel)" if lang == 'hi' else "❌ Cancel"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lbl_skip, callback_data="client_add_skip_phone")],
        [InlineKeyboardButton(lbl_cancel, callback_data="client_action_home")]
    ])

def get_client_detail_keyboard(client_id: int, lang: str) -> InlineKeyboardMarkup:
    """Inline keyboard for a specific client profile page."""
    if lang == 'hi':
        lbl_get = "🟢 + लेना है (Got Credit)"
        lbl_give = "🔴 - देना है (Paid/Due)"
        lbl_phone = "✏️ फोन बदलें / जोड़ें"
        lbl_email = "✏️ ईमेल बदलें / जोड़ें"
        lbl_ledger = "📜 पूरा लेजर (Ledger)"
        lbl_del = "🗑️ ग्राहक हटाएं (Delete)"
        lbl_list = "🔙 ग्राहकों की सूची"
        lbl_home = "🔙 Client"
    elif lang == 'bn':
        lbl_get = "🟢 + পাওনা (You'll Get)"
        lbl_give = "🔴 - দেনা (You'll Give)"
        lbl_phone = "✏️ ফোন নম্বর দিন"
        lbl_email = "✏️ ইমেইল দিন"
        lbl_ledger = "📜 সম্পূর্ণ লেজার"
        lbl_del = "🗑️ গ্রাহক মুছুন"
        lbl_list = "🔙 গ্রাহক তালিকা"
        lbl_home = "🔙 Client"
    else:
        lbl_get = "🟢 + You'll Get (Lena)"
        lbl_give = "🔴 - You'll Give (Dena)"
        lbl_phone = "✏️ Edit / Add Phone"
        lbl_email = "✏️ Edit / Add Email"
        lbl_ledger = "📜 Full Ledger"
        lbl_del = "🗑️ Delete Client"
        lbl_list = "🔙 All Clients"
        lbl_home = "🔙 Client"

    lbl_pdf = "📄 PDF स्टेटमेंट" if lang == 'hi' else "📄 PDF Statement"
    lbl_excel = "📊 Excel स्टेटमेंट" if lang == 'hi' else "📊 Excel Statement"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(lbl_get, callback_data=f"client_tx_get_{client_id}"),
            InlineKeyboardButton(lbl_give, callback_data=f"client_tx_give_{client_id}")
        ],
        [
            InlineKeyboardButton(lbl_phone, callback_data=f"client_edit_phone_{client_id}"),
            InlineKeyboardButton(lbl_email, callback_data=f"client_edit_email_{client_id}")
        ],
        [
            InlineKeyboardButton(lbl_ledger, callback_data=f"client_ledger_{client_id}"),
            InlineKeyboardButton(lbl_del, callback_data=f"client_del_prompt_{client_id}")
        ],
        [
            InlineKeyboardButton(lbl_pdf, callback_data=f"cl_fmt_c{client_id}_pdf"),
            InlineKeyboardButton(lbl_excel, callback_data=f"cl_fmt_c{client_id}_excel")
        ],
        [
            InlineKeyboardButton(lbl_list, callback_data="client_action_list_1"),
            InlineKeyboardButton(lbl_home, callback_data="client_action_home")
        ]
    ])

def get_client_list_keyboard(clients: list, page: int = 1, per_page: int = 5, lang: str = 'en', curr_sym: str = '$') -> InlineKeyboardMarkup:
    """Renders a paginated interactive list of clients with color-coded balance badges."""
    total_clients = len(clients)
    total_pages = max(1, (total_clients + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_clients = clients[start_idx:end_idx]

    rows = []
    for c in page_clients:
        bal = c['balance']
        if bal > 0:
            badge = f"🟢 +{curr_sym}{bal:,.0f}"
        elif bal < 0:
            badge = f"🔴 -{curr_sym}{abs(bal):,.0f}"
        else:
            badge = "⚪ 0"
        btn_text = f"👤 {c['name']} • {badge}"
        rows.append([InlineKeyboardButton(btn_text, callback_data=f"client_view_{c['id']}")])

    # Pagination controls
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⏮️ पिछला", callback_data=f"client_action_list_{page-1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("अगला ⏭️", callback_data=f"client_action_list_{page+1}"))
    if len(nav_row) > 1 or total_pages > 1:
        rows.append(nav_row)

    # Action buttons
    lbl_add = "➕ नया ग्राहक" if lang == 'hi' else "➕ Add Client"
    lbl_summary = "📊 सारांश" if lang == 'hi' else "📊 Summary"
    lbl_home = "🔙 Client"
    lbl_main = "🔙 मुख्य मेनू" if lang == 'hi' else "🔙 Main Menu"

    rows.append([
        InlineKeyboardButton(lbl_add, callback_data="client_action_add"),
        InlineKeyboardButton(lbl_summary, callback_data="client_action_summary")
    ])
    rows.append([
        InlineKeyboardButton(lbl_home, callback_data="client_action_home"),
        InlineKeyboardButton(lbl_main, callback_data="back_main")
    ])

    return InlineKeyboardMarkup(rows)

def get_client_delete_confirm_keyboard(client_id: int, lang: str) -> InlineKeyboardMarkup:
    """Confirmation prompt before deleting client."""
    lbl_yes = "⚠️ हाँ, ग्राहक को हटाएं (Delete)" if lang == 'hi' else "⚠️ Yes, Delete Client"
    lbl_no = "❌ रद्द करें (Keep)" if lang == 'hi' else "❌ Cancel"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lbl_yes, callback_data=f"client_del_confirm_{client_id}")],
        [InlineKeyboardButton(lbl_no, callback_data=f"client_view_{client_id}")]
    ])


# ==========================================
# CLIENT REPORT MULTI-LANGUAGE DICTIONARY
# ==========================================

CLIENT_STATEMENT_I18N = {
    'en': {
        'doc_title_all': "CLIENTS FINANCIAL SUMMARY & AUDIT LEDGER",
        'doc_title_single': "CLIENT STATEMENT OF ACCOUNT",
        'subtitle_system': "COMMERCIAL ACCOUNTS & LEDGER AUDIT SYSTEM",
        'lbl_scope': "Report Scope",
        'lbl_all_clients': "All Active Clients Summary",
        'lbl_client_name': "Client / Party Name",
        'lbl_phone': "Phone / Mobile",
        'lbl_email': "Email Address",
        'lbl_period': "Accounting Period",
        'lbl_jurisdiction': "Country / Currency",
        'lbl_issue_date': "Generated On",
        'lbl_account_holder': "Account Holder",
        'lbl_total_receivable': "Total Receivable (You'll Get)",
        'lbl_total_payable': "Total Payable (You'll Give)",
        'lbl_net_position': "Net Financial Position",
        'lbl_opening_balance': "Opening Balance",
        'lbl_closing_balance': "Closing Balance",
        'lbl_running_balance': "Running Balance",
        'lbl_period_inflow': "Period Inflow (Lena)",
        'lbl_period_outflow': "Period Outflow (Dena)",
        'lbl_total_clients': "Active Clients",
        'lbl_tx_count': "Total Transactions",
        'col_date': "Posting Date",
        'col_client': "Client Name",
        'col_type': "Entry Type",
        'col_amount': "Amount",
        'col_note': "Description / Memo",
        'col_balance': "Balance",
        'col_status': "Status",
        'status_get': "To Receive (Lena)",
        'status_give': "To Pay (Dena)",
        'status_settled': "Settled (Nil)",
        'type_lena': "RECEIVABLE (+)",
        'type_dena': "PAYABLE (-)",
        'sec_summary': "CLIENTS ACCOUNT BALANCES",
        'sec_ledger': "ITEMIZED TRANSACTION AUDIT TRAIL",
        'no_records': "No client transactions recorded during this accounting period.",
        'sheet_summary': "Clients Summary",
        'sheet_ledger': "Transaction Ledger",
        'footer_notice': "STRICTLY CONFIDENTIAL CLIENT FINANCIAL RECORD • PREPARED ELECTRONICALLY FOR AUTHORIZED ENTITY ONLY • AUDIT COMPLIANT"
    },
    'hi': {
        'doc_title_all': "ग्राहक वित्तीय सारांश एवं ऑडिट लेजर",
        'doc_title_single': "ग्राहक खाता विवरण (स्टेटमेंट)",
        'subtitle_system': "व्यापारिक खाता एवं लेजर ऑडिट प्रणाली",
        'lbl_scope': "रिपोर्ट का दायरा",
        'lbl_all_clients': "सभी सक्रिय ग्राहक सारांश",
        'lbl_client_name': "ग्राहक / पार्टी का नाम",
        'lbl_phone': "फोन / मोबाइल नंबर",
        'lbl_email': "ईमेल पता",
        'lbl_period': "लेखा अवधि (Period)",
        'lbl_jurisdiction': "देश / मुद्रा (Currency)",
        'lbl_issue_date': "जारी करने की तारीख",
        'lbl_account_holder': "खाता धारक",
        'lbl_total_receivable': "कुल लेना है (Receivable)",
        'lbl_total_payable': "कुल देना है (Payable)",
        'lbl_net_position': "शुद्ध वित्तीय स्थिति (Net Position)",
        'lbl_opening_balance': "प्रारंभिक शेष (Opening)",
        'lbl_closing_balance': "अंतिम शेष (Closing)",
        'lbl_running_balance': "चालू शेष (Balance)",
        'lbl_period_inflow': "अवधि में कुल लेना",
        'lbl_period_outflow': "अवधि में कुल देना",
        'lbl_total_clients': "सक्रिय ग्राहक",
        'lbl_tx_count': "कुल लेन-देन",
        'col_date': "तारीख",
        'col_client': "ग्राहक का नाम",
        'col_type': "प्रकार",
        'col_amount': "राशि",
        'col_note': "विवरण / नोट",
        'col_balance': "शेष",
        'col_status': "स्थिति",
        'status_get': "लेना बाकी",
        'status_give': "देना बाकी",
        'status_settled': "चुकता (बराबर)",
        'type_lena': "लेना (+)",
        'type_dena': "देना (-)",
        'sec_summary': "ग्राहक शेष विवरण तालिका",
        'sec_ledger': "विस्तृत लेन-देन ऑडिट लेजर",
        'no_records': "इस अवधि में कोई ग्राहक लेन-देन दर्ज नहीं है।",
        'sheet_summary': "ग्राहक सारांश",
        'sheet_ledger': "लेन-देन लेजर",
        'footer_notice': "अति गोपनीय ग्राहक वित्तीय विवरण • अधिकृत इकाई के लिए इलेक्ट्रॉनिक रूप से तैयार • आंतरिक ऑडिट मानकों के अनुरूप"
    },
    'bn': {
        'doc_title_all': "গ্রাহক আর্থিক সারাংশ ও অডিট লেজার",
        'doc_title_single': "গ্রাহক হিসাব বিবরণী",
        'subtitle_system': "বাণিজ্যিক খাতা ও লেজার অডিট সিস্টেম",
        'lbl_scope': "রিপোর্টের আওতা",
        'lbl_all_clients': "সকল সক্রিয় গ্রাহক সারাংশ",
        'lbl_client_name': "গ্রাহকের নাম",
        'lbl_phone': "ফোন নম্বর",
        'lbl_email': "ইমেইল ঠিকানা",
        'lbl_period': "সময়কাল",
        'lbl_jurisdiction': "দেশ / মুদ্রা",
        'lbl_issue_date': "তৈরির তারিখ",
        'lbl_account_holder': "হিসাবধারী",
        'lbl_total_receivable': "মোট পাওনা (Receivable)",
        'lbl_total_payable': "মোট দেনা (Payable)",
        'lbl_net_position': "নেট ব্যালেন্স",
        'lbl_opening_balance': "প্রারম্ভিক জের",
        'lbl_closing_balance': "সমাপনী জের",
        'lbl_running_balance': "জের (Balance)",
        'lbl_period_inflow': "মোট জমা/পাওনা",
        'lbl_period_outflow': "মোট খরচ/দেনা",
        'lbl_total_clients': "মোট গ্রাহক",
        'lbl_tx_count': "মোট লেনদেন",
        'col_date': "তারিখ",
        'col_client': "গ্রাহক",
        'col_type': "প্রকার",
        'col_amount': "পরিমাণ",
        'col_note': "বিবরণ",
        'col_balance': "ব্যালেন্স",
        'col_status': "স্থিতি",
        'status_get': "পাওনা বাকি",
        'status_give': "দেনা বাকি",
        'status_settled': "সমান",
        'type_lena': "পাওনা (+)",
        'type_dena': "দেনা (-)",
        'sec_summary': "গ্রাহক ব্যালেন্স সারাংশ",
        'sec_ledger': "লেনদেন অডিট লেজার",
        'no_records': "এই সময়কালে কোনো লেনদেন নেই।",
        'sheet_summary': "গ্রাহক সারাংশ",
        'sheet_ledger': "লেনদেন লেজার",
        'footer_notice': "গোপনীয় গ্রাহক আর্থিক বিবরণী • অনুমোদিত সংস্থার জন্য প্রস্তুত • অডিট মানসম্মত"
    }
}

def get_client_statement_str(key: str, lang: str = 'en') -> str:
    """Fetches localized label for Client PDF / Excel statement generation with fallback."""
    lang_dict = CLIENT_STATEMENT_I18N.get(lang, CLIENT_STATEMENT_I18N['en'])
    return lang_dict.get(key, CLIENT_STATEMENT_I18N['en'].get(key, key))


def get_client_report_period_keyboard(fmt: str, target: str, lang: str = 'en') -> InlineKeyboardMarkup:
    """
    Renders period selector keyboard for downloading client reports (max 12 months).
    fmt: 'pdf' or 'excel'
    target: 'all' or 'c{client_id}'
    """
    if lang == 'hi':
        lbl_1m = "📅 1 महीना (1 Month)"
        lbl_3m = "📅 3 महीने (3 Months)"
        lbl_6m = "📅 6 महीने (6 Months)"
        lbl_12m = "📅 12 महीने (Max 1 Year)"
        lbl_custom = "🗓️ कस्टम महीने / तारीख (1-12 Mo)"
        lbl_back = "🔙 Client"
    elif lang == 'bn':
        lbl_1m = "📅 ১ মাস (1 Month)"
        lbl_3m = "📅 ৩ মাস (3 Months)"
        lbl_6m = "📅 ৬ মাস (6 Months)"
        lbl_12m = "📅 ১২ মাস (Max 1 Year)"
        lbl_custom = "🗓️ কাস্টম মাস / তারিখ (1-12 Mo)"
        lbl_back = "🔙 Client"
    else:
        lbl_1m = "📅 1 Month"
        lbl_3m = "📅 3 Months"
        lbl_6m = "📅 6 Months"
        lbl_12m = "📅 12 Months (Max 1 Year)"
        lbl_custom = "🗓️ Custom Months / Dates (Max 12M)"
        lbl_back = "🔙 Client"

    back_callback = f"client_view_{target.replace('c', '')}" if target.startswith('c') else "client_action_home"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(lbl_1m, callback_data=f"cl_rep_{fmt}_{target}_1"),
            InlineKeyboardButton(lbl_3m, callback_data=f"cl_rep_{fmt}_{target}_3")
        ],
        [
            InlineKeyboardButton(lbl_6m, callback_data=f"cl_rep_{fmt}_{target}_6"),
            InlineKeyboardButton(lbl_12m, callback_data=f"cl_rep_{fmt}_{target}_12")
        ],
        [
            InlineKeyboardButton(lbl_custom, callback_data=f"cl_rep_{fmt}_{target}_custom")
        ],
        [
            InlineKeyboardButton(lbl_back, callback_data=back_callback)
        ]
    ])


def get_text_saver_keyboard(items: list, page: int = 1, per_page: int = 6, lang: str = 'en') -> InlineKeyboardMarkup:
    """
    Renders interactive checklist keyboard for Text Saver / shopping list.
    - Each item has a toggle button (done / pending) AND a 1-click Copy button.
    - Includes pagination if items exceed per_page.
    - Quick actions: Add Item, Copy Entire List, Clear Done, Clear All, Main Menu.
    """
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]

    rows = []
    for item in page_items:
        is_done = bool(item.get('is_done'))
        display_text = item['text'][:24] + ("..." if len(item['text']) > 24 else "")
        if is_done:
            btn_text = f"✅ ~{display_text}~"
        else:
            btn_text = f"⬜ {display_text}"
        toggle_btn = InlineKeyboardButton(btn_text, callback_data=f"ts_toggle_{item['id']}_{page}")
        copy_btn = InlineKeyboardButton("📋 Copy", copy_text=CopyTextButton(text=item['text']))
        rows.append([toggle_btn, copy_btn])

    if total_pages > 1:
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton("⏮️ पिछला" if lang == 'hi' else "⏮️ Prev", callback_data=f"ts_page_{page-1}"))
        nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton("अगला ⏭️" if lang == 'hi' else "Next ⏭️", callback_data=f"ts_page_{page+1}"))
        rows.append(nav_row)

    lbl_add = "➕ नया सामान जोड़ें" if lang == 'hi' else "➕ Add Items"
    lbl_clear_done = "🧹 खरीदे हुए हटाएं" if lang == 'hi' else "🧹 Clear Done"
    lbl_clear_all = "🗑️ सब साफ करें" if lang == 'hi' else "🗑️ Clear All"
    lbl_main = "🔙 मुख्य मेनू" if lang == 'hi' else "🔙 Main Menu"

    rows.append([
        InlineKeyboardButton(lbl_add, callback_data="ts_action_add")
    ])

    # Copy Entire List button if items exist
    if total_items > 0:
        pending_texts = [f"• {i['text']}" for i in items if not i.get('is_done')]
        all_texts = [f"• {i['text']}" for i in items]
        join_char = chr(10)
        copy_target = join_char.join(pending_texts) if pending_texts else join_char.join(all_texts)
        lbl_copy_all = "📋 पूरी लिस्ट कॉपी करें (Copy List)" if lang == 'hi' else "📋 Copy Entire List"
        rows.append([
            InlineKeyboardButton(lbl_copy_all, copy_text=CopyTextButton(text=copy_target))
        ])

    cleanup_row = []
    has_done = any(i.get('is_done') for i in items)
    if has_done:
        cleanup_row.append(InlineKeyboardButton(lbl_clear_done, callback_data="ts_action_clear_done"))
    if total_items > 0:
        cleanup_row.append(InlineKeyboardButton(lbl_clear_all, callback_data="ts_action_clear_all_prompt"))

    if cleanup_row:
        rows.append(cleanup_row)

    rows.append([
        InlineKeyboardButton(lbl_main, callback_data="back_main")
    ])

    return InlineKeyboardMarkup(rows)


def get_text_saver_clear_confirm_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    """Confirmation prompt before clearing entire Text Saver list."""
    lbl_yes = "⚠️ हाँ, सभी सामान हटाएं (Clear All)" if lang == 'hi' else "⚠️ Yes, Clear All Items"
    lbl_no = "❌ रद्द करें (Cancel)" if lang == 'hi' else "❌ Cancel"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lbl_yes, callback_data="ts_action_clear_all_confirm")],
        [InlineKeyboardButton(lbl_no, callback_data="ts_action_home")]
    ])
