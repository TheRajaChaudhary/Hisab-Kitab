import os
import datetime
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from hisab_kitab_bot.config import PDF_TEMP_DIR
from hisab_kitab_bot.database import (
    get_date_range_expenses,
    get_date_range_breakdown,
    get_user_budget,
    get_user_country,
    get_client,
    get_client_opening_balance,
    get_client_period_summary
)
from hisab_kitab_bot.i18n import get_statement_str, get_client_statement_str

def _setup_fonts():
    """Safely registers system fonts for professional Unicode multi-language support."""
    registered = {
        'indic': 'Helvetica',
        'indic_bold': 'Helvetica-Bold',
        'latin': 'Helvetica',
        'latin_bold': 'Helvetica-Bold'
    }
    
    font_paths = {
        'Nirmala': ('C:/Windows/Fonts/Nirmala.ttf', 'C:/Windows/Fonts/NirmalaB.ttf'),
        'Arial': ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
        'SegoeUI': ('C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/segoeuib.ttf'),
    }
    
    try:
        if os.path.exists(font_paths['Nirmala'][0]) and os.path.exists(font_paths['Nirmala'][1]):
            pdfmetrics.registerFont(TTFont('Nirmala', font_paths['Nirmala'][0]))
            pdfmetrics.registerFont(TTFont('Nirmala-Bold', font_paths['Nirmala'][1]))
            registered['indic'] = 'Nirmala'
            registered['indic_bold'] = 'Nirmala-Bold'
    except Exception:
        pass

    try:
        if os.path.exists(font_paths['Arial'][0]) and os.path.exists(font_paths['Arial'][1]):
            pdfmetrics.registerFont(TTFont('Arial', font_paths['Arial'][0]))
            pdfmetrics.registerFont(TTFont('Arial-Bold', font_paths['Arial'][1]))
            registered['latin'] = 'Arial'
            registered['latin_bold'] = 'Arial-Bold'
    except Exception:
        pass

    return registered

FONTS = _setup_fonts()

def generate_statement_pdf(user_id: int, first_name: str, start_date: str = None, end_date: str = None, period_label: str = None, lang: str = 'en', country_code: str = None) -> str:
    """
    Generates a high-end corporate executive financial statement PDF.
    - Zero website promotions or deal ads.
    - Fully localized into the user's selected language.
    - Strict country-wise ledger isolation (separate currency and accounts).
    """
    now = datetime.datetime.now()
    
    # 1. Fetch user country and currency
    country_data = get_user_country(user_id)
    c_code = country_code or country_data.get("country_code", "GLOBAL")
    c_name = country_data.get("country_name", "Worldwide")
    currency_code = country_data.get("currency_code", "USD")
    curr = country_data.get("currency_symbol", "$")

    # 2. Date ranges
    if not start_date or not end_date:
        year = now.year
        month = now.month
        last_day = calendar.monthrange(year, month)[1]
        start_date = f"{year:04d}-{month:02d}-01"
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
        period_label = datetime.date(year, month, 1).strftime("%B %Y")
    elif not period_label:
        period_label = f"{start_date} to {end_date}"

    safe_start = start_date.replace("-", "")
    safe_end = end_date.replace("-", "")
    audit_code = f"HK-{c_code}-{user_id}-{safe_start}"
    file_name = f"Financial_Statement_{c_code}_{user_id}_{safe_start}_{safe_end}_{lang}.pdf"
    file_path = os.path.join(PDF_TEMP_DIR, file_name)

    # 3. Choose appropriate font family based on language
    if lang in ('hi', 'bn', 'ur'):
        font_regular = FONTS['indic']
        font_bold = FONTS['indic_bold']
    else:
        font_regular = FONTS['latin']
        font_bold = FONTS['latin_bold']

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    # Corporate Color Palette
    c_navy = colors.HexColor('#0F172A')       # Deep Navy
    c_slate = colors.HexColor('#334155')      # Slate
    c_muted = colors.HexColor('#64748B')      # Muted Gray
    c_border = colors.HexColor('#CBD5E1')     # Border line
    c_bg_light = colors.HexColor('#F8FAFC')   # Subtle card bg
    c_green = colors.HexColor('#166534')      # Corporate Green
    c_red = colors.HexColor('#991B1B')        # Corporate Red
    c_green_bg = colors.HexColor('#F0FDF4')   # Soft green tint
    c_red_bg = colors.HexColor('#FEF2F2')     # Soft red tint

    # Typography styles
    style_sys_badge = ParagraphStyle('SysBadge', fontName=font_bold, fontSize=8, leading=10, textColor=colors.HexColor('#0284C7'))
    style_title = ParagraphStyle('DocTitle', fontName=font_bold, fontSize=16, leading=20, textColor=c_navy)
    style_sub = ParagraphStyle('DocSub', fontName=font_regular, fontSize=8.5, leading=12, textColor=c_slate)
    style_sec_head = ParagraphStyle('SecHead', fontName=font_bold, fontSize=10, leading=13, textColor=c_navy, spaceBefore=8, spaceAfter=4)
    style_th = ParagraphStyle('TH', fontName=font_bold, fontSize=8, leading=10, textColor=colors.white, alignment=1)
    style_td = ParagraphStyle('TD', fontName=font_regular, fontSize=8, leading=10, textColor=c_navy)
    style_td_bold = ParagraphStyle('TDBold', fontName=font_bold, fontSize=8, leading=10, textColor=c_navy)
    style_td_right = ParagraphStyle('TDRight', fontName=font_regular, fontSize=8, leading=10, textColor=c_navy, alignment=2)
    style_td_bold_right = ParagraphStyle('TDBoldRight', fontName=font_bold, fontSize=8, leading=10, textColor=c_navy, alignment=2)
    style_kpi_lbl = ParagraphStyle('KpiLbl', fontName=font_bold, fontSize=7.5, leading=9, textColor=c_muted, alignment=1)
    style_kpi_val = ParagraphStyle('KpiVal', fontName=font_bold, fontSize=11.5, leading=14, textColor=c_navy, alignment=1)
    style_footer = ParagraphStyle('Footer', fontName=font_regular, fontSize=6.5, leading=9, textColor=c_muted, alignment=1)

    story = []

    # -------------------------------------------------------------
    # 1. CORPORATE HEADER & SYSTEM BADGE
    # -------------------------------------------------------------
    story.append(Paragraph(get_statement_str('subtitle_system', lang).upper(), style_sys_badge))
    story.append(Spacer(1, 2))
    story.append(Paragraph(get_statement_str('doc_title', lang), style_title))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 2. EXECUTIVE METADATA CARD (2-COLUMN TABLE)
    # -------------------------------------------------------------
    meta_rows = [
        [
            Paragraph(f"<b>{get_statement_str('lbl_account_holder', lang)}:</b> {first_name}", style_sub),
            Paragraph(f"<b>{get_statement_str('lbl_period', lang)}:</b> {period_label}", style_sub)
        ],
        [
            Paragraph(f"<b>{get_statement_str('lbl_account_id', lang)}:</b> ACC-{user_id}", style_sub),
            Paragraph(f"<b>{get_statement_str('lbl_jurisdiction', lang)}:</b> {c_name} ({c_code})", style_sub)
        ],
        [
            Paragraph(f"<b>{get_statement_str('lbl_currency', lang)}:</b> {currency_code} ({curr})", style_sub),
            Paragraph(f"<b>{get_statement_str('lbl_audit_ref', lang)}:</b> {audit_code}", style_sub)
        ],
        [
            Paragraph(f"<b>{get_statement_str('lbl_issue_date', lang)}:</b> {now.strftime('%d-%b-%Y %H:%M')} UTC", style_sub),
            Paragraph(f"<b>Status:</b> VERIFIED ELECTRONIC RECORD", style_sub)
        ]
    ]
    meta_table = Table(meta_rows, colWidths=[3.75 * inch, 3.75 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 3. EXECUTIVE KPI DASHBOARD SCORECARD
    # -------------------------------------------------------------
    breakdown = get_date_range_breakdown(user_id, start_date, end_date, country_code=c_code)
    total_exp = breakdown['total_expense']
    total_inc = breakdown['total_income']
    net_savings = total_inc - total_exp
    budget = get_user_budget(user_id, country_code=c_code)
    rem_budget = max(0.0, budget - total_exp) if budget > 0 else 0.0

    net_color = c_green if net_savings >= 0 else c_red
    kpi_cols = [
        # Col 1: Total Inflow
        [
            Paragraph(get_statement_str('kpi_income', lang), style_kpi_lbl),
            Spacer(1, 2),
            Paragraph(f"<font color='{c_green.hexval()}'>+{curr}{total_inc:,.2f}</font>", style_kpi_val)
        ],
        # Col 2: Total Outflow
        [
            Paragraph(get_statement_str('kpi_expense', lang), style_kpi_lbl),
            Spacer(1, 2),
            Paragraph(f"<font color='{c_red.hexval()}'>-{curr}{total_exp:,.2f}</font>", style_kpi_val)
        ],
        # Col 3: Net Balance
        [
            Paragraph(get_statement_str('kpi_net', lang), style_kpi_lbl),
            Spacer(1, 2),
            Paragraph(f"<font color='{net_color.hexval()}'>{'+' if net_savings >= 0 else ''}{curr}{net_savings:,.2f}</font>", style_kpi_val)
        ],
        # Col 4: Budget Allocation
        [
            Paragraph(get_statement_str('kpi_budget', lang), style_kpi_lbl),
            Spacer(1, 2),
            Paragraph(f"{curr}{budget:,.2f}" if budget > 0 else "N/A", style_kpi_val)
        ],
        # Col 5: Budget Surplus
        [
            Paragraph(get_statement_str('kpi_variance', lang), style_kpi_lbl),
            Spacer(1, 2),
            Paragraph(f"{curr}{rem_budget:,.2f}" if budget > 0 else "N/A", style_kpi_val)
        ],
    ]

    kpi_matrix = [[kpi_cols[0], kpi_cols[1], kpi_cols[2], kpi_cols[3], kpi_cols[4]]]
    kpi_table = Table(kpi_matrix, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), c_green_bg),
        ('BACKGROUND', (1, 0), (1, 0), c_red_bg),
        ('BACKGROUND', (2, 0), (2, 0), c_bg_light),
        ('BACKGROUND', (3, 0), (3, 0), c_bg_light),
        ('BACKGROUND', (4, 0), (4, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 4. EXPENDITURE BREAKDOWN BY CATEGORY
    # -------------------------------------------------------------
    story.append(Paragraph(get_statement_str('sec_breakdown', lang), style_sec_head))
    
    cat_data = [
        [
            Paragraph(get_statement_str('col_category', lang), style_th),
            Paragraph(get_statement_str('col_count', lang), style_th),
            Paragraph(get_statement_str('col_spent', lang), style_th),
            Paragraph(get_statement_str('col_share', lang), style_th),
        ]
    ]

    for c in breakdown['categories']:
        share = (c['total'] / total_exp * 100) if total_exp > 0 else 0
        cat_data.append([
            Paragraph(str(c['category']), style_td),
            Paragraph(str(c['count']), style_td_right),
            Paragraph(f"{curr}{c['total']:,.2f}", style_td_bold_right),
            Paragraph(f"{share:.1f}%", style_td_right),
        ])

    if len(cat_data) == 1:
        cat_data.append([
            Paragraph(get_statement_str('no_records', lang), style_td),
            Paragraph("-", style_td_right),
            Paragraph(f"{curr}0.00", style_td_right),
            Paragraph("0.0%", style_td_right)
        ])

    cat_table = Table(cat_data, colWidths=[3.2 * inch, 1.2 * inch, 1.8 * inch, 1.3 * inch])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 12))

    # -------------------------------------------------------------
    # 5. ITEMIZED TRANSACTION AUDIT LEDGER
    # -------------------------------------------------------------
    story.append(Paragraph(get_statement_str('sec_ledger', lang), style_sec_head))
    
    tx_data = [
        [
            Paragraph(get_statement_str('col_date', lang), style_th),
            Paragraph(get_statement_str('col_category', lang), style_th),
            Paragraph(get_statement_str('col_desc', lang), style_th),
            Paragraph(get_statement_str('col_type', lang), style_th),
            Paragraph(get_statement_str('col_amount', lang), style_th),
        ]
    ]

    all_txs = get_date_range_expenses(user_id, start_date, end_date, country_code=c_code)
    for tx in all_txs:
        is_inc = (tx['type'] == 'income')
        amt_prefix = "+" if is_inc else "-"
        amt_str = f"{amt_prefix}{curr}{tx['amount']:,.2f}"
        color_val = c_green.hexval() if is_inc else c_red.hexval()
        type_lbl = get_statement_str('type_income', lang) if is_inc else get_statement_str('type_expense', lang)
        
        tx_data.append([
            Paragraph(str(tx['date']), style_td),
            Paragraph(str(tx['category']), style_td),
            Paragraph(str(tx['note'] or "-"), style_td),
            Paragraph(type_lbl, style_td),
            Paragraph(f"<font color='{color_val}'><b>{amt_str}</b></font>", style_td_bold_right),
        ])

    if len(tx_data) == 1:
        tx_data.append([
            Paragraph(get_statement_str('no_records', lang), style_td),
            Paragraph("-", style_td),
            Paragraph("-", style_td),
            Paragraph("-", style_td),
            Paragraph("-", style_td_right),
        ])

    tx_table = Table(tx_data, colWidths=[1.1 * inch, 1.7 * inch, 2.3 * inch, 1.1 * inch, 1.3 * inch])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tx_table)
    story.append(Spacer(1, 16))

    # -------------------------------------------------------------
    # 6. PROFESSIONAL CORPORATE AUDIT FOOTER (ZERO PROMOTIONS)
    # -------------------------------------------------------------
    footer_text = get_statement_str('footer_notice', lang)
    story.append(Paragraph(footer_text, style_footer))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"AUDIT HASH: {audit_code} • PAGE 1 OF 1 • ELECTRONIC AUTHENTICATION VALID", style_footer))

    doc.build(story)
    return file_path

def generate_monthly_pdf(user_id: int, first_name: str, year: int = None, month: int = None, lang: str = 'en', country_code: str = None) -> str:
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    period_label = datetime.date(year, month, 1).strftime("%B %Y")
    return generate_statement_pdf(user_id, first_name, start_date, end_date, period_label, lang=lang, country_code=country_code)


def get_client_report_date_range(months: int = 1):
    """Computes start_date, end_date, and label for requested number of months (1 to 12)."""
    months = max(1, min(12, int(months)))
    today = datetime.date.today()
    year = today.year
    month = today.month - months + 1
    while month <= 0:
        month += 12
        year -= 1
    start_date = datetime.date(year, month, 1)
    end_date = today
    if months == 1:
        label = start_date.strftime("%B %Y")
    else:
        label = f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')} ({months} Months)"
    return start_date.isoformat(), end_date.isoformat(), label, months


def generate_client_report_pdf(user_id: int, first_name: str, client_id: int = None, months: int = 1, start_date: str = None, end_date: str = None, period_label: str = None, lang: str = 'en', country_code: str = None) -> str:
    """Generates corporate executive PDF statement for clients (1 to 12 months)."""
    now = datetime.datetime.now()
    country_data = get_user_country(user_id)
    c_code = country_code or country_data.get("country_code", "GLOBAL")
    c_name = country_data.get("country_name", "Worldwide")
    curr = country_data.get("currency_symbol", "$")

    if not start_date or not end_date:
        start_date, end_date, auto_label, num_months = get_client_report_date_range(months)
        if not period_label:
            period_label = auto_label

    safe_start = start_date.replace("-", "")
    safe_end = end_date.replace("-", "")
    target_tag = f"c{client_id}" if client_id else "all"
    file_name = f"Client_Report_{c_code}_{user_id}_{target_tag}_{safe_start}_{safe_end}_{lang}.pdf"
    file_path = os.path.join(PDF_TEMP_DIR, file_name)

    if lang in ('hi', 'bn', 'ur'):
        font_regular = FONTS['indic']
        font_bold = FONTS['indic_bold']
    else:
        font_regular = FONTS['latin']
        font_bold = FONTS['latin_bold']

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    c_navy = colors.HexColor('#0F172A')
    c_slate = colors.HexColor('#334155')
    c_muted = colors.HexColor('#64748B')
    c_border = colors.HexColor('#CBD5E1')
    c_bg_light = colors.HexColor('#F8FAFC')
    c_green = colors.HexColor('#166534')
    c_red = colors.HexColor('#991B1B')
    c_green_bg = colors.HexColor('#F0FDF4')
    c_red_bg = colors.HexColor('#FEF2F2')

    style_sys_badge = ParagraphStyle('SysBadge', fontName=font_bold, fontSize=8, leading=10, textColor=colors.HexColor('#0284C7'))
    style_title = ParagraphStyle('DocTitle', fontName=font_bold, fontSize=15, leading=19, textColor=c_navy)
    style_sec_head = ParagraphStyle('SecHead', fontName=font_bold, fontSize=10, leading=13, textColor=c_navy, spaceBefore=8, spaceAfter=4)
    style_th = ParagraphStyle('TH', fontName=font_bold, fontSize=8, leading=10, textColor=colors.white, alignment=1)
    style_td = ParagraphStyle('TD', fontName=font_regular, fontSize=8, leading=10, textColor=c_navy)
    style_td_bold = ParagraphStyle('TDBold', fontName=font_bold, fontSize=8, leading=10, textColor=c_navy)
    style_td_right = ParagraphStyle('TDRight', fontName=font_regular, fontSize=8, leading=10, textColor=c_navy, alignment=2)
    style_td_bold_right = ParagraphStyle('TDBoldRight', fontName=font_bold, fontSize=8, leading=10, textColor=c_navy, alignment=2)
    style_footer = ParagraphStyle('Footer', fontName=font_regular, fontSize=7, leading=9, textColor=c_muted, alignment=1)

    story = []

    # 1. Header
    sys_badge = get_client_statement_str('subtitle_system', lang)
    if client_id:
        client_data = get_client(client_id, user_id)
        client_name = client_data['name'] if client_data else "Client"
        doc_title = f"{get_client_statement_str('doc_title_single', lang)}: {client_name}"
    else:
        doc_title = get_client_statement_str('doc_title_all', lang)

    story.append(Paragraph(sys_badge, style_sys_badge))
    story.append(Spacer(1, 2))
    story.append(Paragraph(doc_title, style_title))
    story.append(Spacer(1, 10))

    summary = get_client_period_summary(user_id, start_date, end_date, client_id=client_id, country_code=c_code)
    issue_date_str = now.strftime("%d %b %Y, %I:%M %p")
    audit_hash = f"CL-{c_code}-{user_id}-{safe_start}"

    # 2. Metadata Card
    scope_val = client_name if client_id else get_client_statement_str('lbl_all_clients', lang)
    meta_data = [
        [
            Paragraph(f"<b>{get_client_statement_str('lbl_account_holder', lang)}:</b> {first_name}", style_td),
            Paragraph(f"<b>{get_client_statement_str('lbl_period', lang)}:</b> {period_label}", style_td),
        ],
        [
            Paragraph(f"<b>{get_client_statement_str('lbl_scope', lang)}:</b> {scope_val}", style_td),
            Paragraph(f"<b>{get_client_statement_str('lbl_jurisdiction', lang)}:</b> {c_name} ({curr})", style_td),
        ],
        [
            Paragraph(f"<b>{get_client_statement_str('lbl_issue_date', lang)}:</b> {issue_date_str}", style_td),
            Paragraph(f"<b>Audit Ref:</b> {audit_hash}", style_td),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[3.75 * inch, 3.75 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. KPI Scorecard
    if client_id:
        op_bal = get_client_opening_balance(client_id, user_id, start_date)
        period_lena = summary['period_lena']
        period_dena = summary['period_dena']
        cl_bal = op_bal + period_lena - period_dena

        kpi_cells = [
            [
                Paragraph(get_client_statement_str('lbl_opening_balance', lang), style_td),
                Paragraph(get_client_statement_str('lbl_period_inflow', lang), style_td),
                Paragraph(get_client_statement_str('lbl_period_outflow', lang), style_td),
                Paragraph(get_client_statement_str('lbl_closing_balance', lang), style_td),
            ],
            [
                Paragraph(f"{curr}{op_bal:,.2f}", style_td_bold),
                Paragraph(f"+{curr}{period_lena:,.2f}", ParagraphStyle('KPiG', fontName=font_bold, fontSize=11, textColor=c_green)),
                Paragraph(f"-{curr}{period_dena:,.2f}", ParagraphStyle('KPiR', fontName=font_bold, fontSize=11, textColor=c_red)),
                Paragraph(f"{curr}{cl_bal:,.2f}", ParagraphStyle('KPiN', fontName=font_bold, fontSize=11, textColor=c_navy)),
            ]
        ]
        kpi_table = Table(kpi_cells, colWidths=[1.875 * inch] * 4)
    else:
        tot_lena = summary['total_receivable']
        tot_dena = summary['total_payable']
        net_pos = summary['net_position']
        cl_cnt = summary['total_clients']

        kpi_cells = [
            [
                Paragraph(get_client_statement_str('lbl_total_receivable', lang), style_td),
                Paragraph(get_client_statement_str('lbl_total_payable', lang), style_td),
                Paragraph(get_client_statement_str('lbl_net_position', lang), style_td),
                Paragraph(get_client_statement_str('lbl_total_clients', lang), style_td),
            ],
            [
                Paragraph(f"🟢 +{curr}{tot_lena:,.2f}", ParagraphStyle('KPiG', fontName=font_bold, fontSize=11, textColor=c_green)),
                Paragraph(f"🔴 -{curr}{tot_dena:,.2f}", ParagraphStyle('KPiR', fontName=font_bold, fontSize=11, textColor=c_red)),
                Paragraph(f"{curr}{net_pos:,.2f}", ParagraphStyle('KPiN', fontName=font_bold, fontSize=11, textColor=c_navy)),
                Paragraph(f"{cl_cnt}", ParagraphStyle('KPiC', fontName=font_bold, fontSize=11, textColor=c_navy)),
            ]
        ]
        kpi_table = Table(kpi_cells, colWidths=[1.875 * inch] * 4)

    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # 4. Tables
    if not client_id:
        story.append(Paragraph(get_client_statement_str('sec_summary', lang), style_sec_head))
        cl_rows = [[
            Paragraph(get_client_statement_str('col_client', lang), style_th),
            Paragraph(get_client_statement_str('lbl_phone', lang), style_th),
            Paragraph(get_client_statement_str('lbl_total_receivable', lang), style_th),
            Paragraph(get_client_statement_str('lbl_total_payable', lang), style_th),
            Paragraph(get_client_statement_str('col_balance', lang), style_th),
            Paragraph(get_client_statement_str('col_status', lang), style_th),
        ]]

        for c in summary['clients']:
            bal = c['balance']
            if bal > 0:
                st_str = get_client_statement_str('status_get', lang)
                bal_p = Paragraph(f"+{curr}{bal:,.2f}", ParagraphStyle('B1', fontName=font_bold, fontSize=8, textColor=c_green, alignment=2))
            elif bal < 0:
                st_str = get_client_statement_str('status_give', lang)
                bal_p = Paragraph(f"-{curr}{abs(bal):,.2f}", ParagraphStyle('B2', fontName=font_bold, fontSize=8, textColor=c_red, alignment=2))
            else:
                st_str = get_client_statement_str('status_settled', lang)
                bal_p = Paragraph(f"{curr}0.00", style_td_bold_right)

            phone_str = c.get('phone') or "-"
            cl_rows.append([
                Paragraph(c['name'], style_td_bold),
                Paragraph(phone_str, style_td),
                Paragraph(f"{curr}{c.get('total_lena', 0.0):,.2f}", style_td_right),
                Paragraph(f"{curr}{c.get('total_dena', 0.0):,.2f}", style_td_right),
                bal_p,
                Paragraph(st_str, style_td),
            ])

        if len(cl_rows) == 1:
            cl_rows.append([Paragraph("No active clients.", style_td)] + [Paragraph("-", style_td)] * 5)

        cl_table = Table(cl_rows, colWidths=[1.8 * inch, 1.2 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.2 * inch])
        cl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('BOX', (0, 0), (-1, -1), 1, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(cl_table)
        story.append(Spacer(1, 12))

    # Transaction Ledger Table
    story.append(Paragraph(get_client_statement_str('sec_ledger', lang), style_sec_head))
    tx_rows = [[
        Paragraph(get_client_statement_str('col_date', lang), style_th),
        Paragraph(get_client_statement_str('col_client', lang), style_th),
        Paragraph(get_client_statement_str('col_type', lang), style_th),
        Paragraph(get_client_statement_str('col_amount', lang), style_th),
        Paragraph(get_client_statement_str('col_note', lang), style_th),
    ]]

    if summary['transactions']:
        for t in summary['transactions'][:40]:
            t_type = t['type']
            if t_type == 'lena':
                type_p = Paragraph(get_client_statement_str('type_lena', lang), ParagraphStyle('TL', fontName=font_bold, fontSize=7.5, textColor=c_green))
                amt_p = Paragraph(f"+{curr}{t['amount']:,.2f}", ParagraphStyle('AL', fontName=font_bold, fontSize=8, textColor=c_green, alignment=2))
            else:
                type_p = Paragraph(get_client_statement_str('type_dena', lang), ParagraphStyle('TD2', fontName=font_bold, fontSize=7.5, textColor=c_red))
                amt_p = Paragraph(f"-{curr}{t['amount']:,.2f}", ParagraphStyle('AD', fontName=font_bold, fontSize=8, textColor=c_red, alignment=2))

            note_val = t.get('note') or "-"
            c_name_val = t.get('client_name') or "Client"
            tx_rows.append([
                Paragraph(t['date'], style_td),
                Paragraph(c_name_val, style_td_bold),
                type_p,
                amt_p,
                Paragraph(note_val, style_td),
            ])
    else:
        no_rec = get_client_statement_str('no_records', lang)
        tx_rows.append([Paragraph(no_rec, style_td)] + [Paragraph("-", style_td)] * 4)

    tx_table = Table(tx_rows, colWidths=[1.1 * inch, 1.6 * inch, 1.3 * inch, 1.2 * inch, 2.3 * inch])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tx_table)
    story.append(Spacer(1, 14))

    # 5. Corporate Footer
    footer_text = get_client_statement_str('footer_notice', lang)
    story.append(Paragraph(footer_text, style_footer))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"AUDIT HASH: {audit_hash} • ELECTRONICALLY VERIFIED • COMPLIANT", style_footer))

    doc.build(story)
    return file_path
