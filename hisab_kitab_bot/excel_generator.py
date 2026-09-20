import os
import datetime
import calendar
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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
from hisab_kitab_bot.pdf_generator import get_client_report_date_range

def generate_statement_excel(user_id: int, first_name: str, start_date: str = None, end_date: str = None, period_label: str = None, lang: str = 'en', country_code: str = None) -> str:
    """
    Generates a high-end corporate executive financial statement Excel workbook (.xlsx).
    - Zero website promotions or external deal links.
    - Fully localized into the user's selected language.
    - Strict country-wise ledger isolation.
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
    file_name = f"Financial_Statement_{c_code}_{user_id}_{safe_start}_{safe_end}_{lang}.xlsx"
    file_path = os.path.join(PDF_TEMP_DIR, file_name)

    # 3. Fetch data scoped by country
    expenses = get_date_range_expenses(user_id, start_date, end_date, country_code=c_code)
    breakdown = get_date_range_breakdown(user_id, start_date, end_date, country_code=c_code)
    budget = get_user_budget(user_id, country_code=c_code)

    total_expense = breakdown['total_expense']
    total_income = breakdown['total_income']
    net_savings = total_income - total_expense
    categories = breakdown['categories']

    wb = Workbook()

    # Corporate styling palette
    c_navy = "0F172A"       # Deep Navy Header
    c_slate_dark = "1E293B" # Dark Slate
    c_income = "166534"     # Corporate Green
    c_income_bg = "F0FDF4"  # Light Green
    c_expense = "991B1B"    # Corporate Red
    c_expense_bg = "FEF2F2" # Light Red
    c_zebra = "F8FAFC"      # Light Slate
    c_border = "CBD5E1"     # Slate Border

    thin_border = Border(
        left=Side(style='thin', color=c_border),
        right=Side(style='thin', color=c_border),
        top=Side(style='thin', color=c_border),
        bottom=Side(style='thin', color=c_border)
    )

    header_border = Border(
        left=Side(style='thin', color="475569"),
        right=Side(style='thin', color="475569"),
        top=Side(style='medium', color="0F172A"),
        bottom=Side(style='medium', color="0F172A")
    )

    # -------------------------------------------------------------
    # SHEET 1: EXECUTIVE FINANCIAL SUMMARY
    # -------------------------------------------------------------
    ws_summary = wb.active
    ws_summary.title = get_statement_str('sheet_summary', lang)[:31]
    ws_summary.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_summary.merge_cells("A1:E1")
    title_cell = ws_summary["A1"]
    title_cell.value = get_statement_str('doc_title', lang)
    title_cell.font = Font(name="Arial", size=15, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color=c_navy, end_color=c_navy, fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[1].height = 36

    # Subtitle / Metadata Banner
    ws_summary.merge_cells("A2:E2")
    sub_cell = ws_summary["A2"]
    sub_cell.value = f"{get_statement_str('lbl_period', lang)}: {period_label}  |  {get_statement_str('lbl_account_holder', lang)}: {first_name} (ACC-{user_id})  |  {get_statement_str('lbl_jurisdiction', lang)}: {c_name} ({currency_code} - {curr})  |  {now.strftime('%d-%b-%Y %H:%M')} UTC"
    sub_cell.font = Font(name="Arial", size=9, italic=True, color="475569")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[2].height = 20

    # KPI Summary Cards Header
    ws_summary.cell(row=4, column=1, value=get_statement_str('sec_summary', lang)).font = Font(name="Arial", size=11, bold=True, color=c_slate_dark)

    rem_budget = max(0.0, budget - total_expense) if budget > 0 else 0.0
    kpis = [
        (get_statement_str('kpi_income', lang), total_income, c_income_bg, c_income),
        (get_statement_str('kpi_expense', lang), total_expense, c_expense_bg, c_expense),
        (get_statement_str('kpi_net', lang), net_savings, c_income_bg if net_savings >= 0 else c_expense_bg, c_income if net_savings >= 0 else c_expense),
        (get_statement_str('kpi_budget', lang), budget, "F8FAFC", c_slate_dark),
        (get_statement_str('kpi_variance', lang), rem_budget, "F8FAFC", c_income if rem_budget >= 0 else c_expense)
    ]

    for col_idx, (kpi_name, kpi_val, bg_col, text_col) in enumerate(kpis, start=1):
        c_lbl = ws_summary.cell(row=5, column=col_idx, value=kpi_name)
        c_lbl.font = Font(name="Arial", size=8.5, bold=True, color="64748B")
        c_lbl.alignment = Alignment(horizontal="center", vertical="center")
        c_lbl.fill = PatternFill(start_color=bg_col, end_color=bg_col, fill_type="solid")
        c_lbl.border = thin_border

        c_val = ws_summary.cell(row=6, column=col_idx, value=kpi_val)
        c_val.font = Font(name="Arial", size=12, bold=True, color=text_col)
        c_val.alignment = Alignment(horizontal="center", vertical="center")
        c_val.fill = PatternFill(start_color=bg_col, end_color=bg_col, fill_type="solid")
        c_val.number_format = f'"{curr}"#,##0.00'
        c_val.border = thin_border

    ws_summary.row_dimensions[5].height = 22
    ws_summary.row_dimensions[6].height = 28

    # Category Breakdown Table
    start_row = 9
    ws_summary.cell(row=start_row, column=1, value=get_statement_str('sec_breakdown', lang)).font = Font(name="Arial", size=11, bold=True, color=c_slate_dark)

    cat_headers = [
        get_statement_str('col_category', lang),
        f"{get_statement_str('col_spent', lang)} ({curr})",
        get_statement_str('col_count', lang),
        get_statement_str('col_share', lang)
    ]
    for col_idx, h_text in enumerate(cat_headers, start=1):
        c = ws_summary.cell(row=start_row + 1, column=col_idx, value=h_text)
        c.font = Font(name="Arial", size=9.5, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=c_slate_dark, end_color=c_slate_dark, fill_type="solid")
        c.alignment = Alignment(horizontal="center" if col_idx > 1 else "left", vertical="center")
        c.border = header_border
    ws_summary.row_dimensions[start_row + 1].height = 24

    current_row = start_row + 2
    if categories:
        for cat in categories:
            cat_name = str(cat['category'])
            cat_tot = float(cat['total'])
            cat_count = int(cat['count'])
            pct = (cat_tot / total_expense) if total_expense > 0 else 0.0

            c1 = ws_summary.cell(row=current_row, column=1, value=cat_name)
            c2 = ws_summary.cell(row=current_row, column=2, value=cat_tot)
            c3 = ws_summary.cell(row=current_row, column=3, value=cat_count)
            c4 = ws_summary.cell(row=current_row, column=4, value=pct)

            c1.font = Font(name="Arial", size=9, bold=True)
            c2.font = Font(name="Arial", size=9)
            c3.font = Font(name="Arial", size=9)
            c4.font = Font(name="Arial", size=9)

            c1.border = thin_border
            c2.border = thin_border
            c3.border = thin_border
            c4.border = thin_border

            c2.number_format = f'"{curr}"#,##0.00'
            c3.alignment = Alignment(horizontal="center")
            c4.number_format = '0.0%'
            c4.alignment = Alignment(horizontal="right")

            if (current_row % 2) == 0:
                for cell in (c1, c2, c3, c4):
                    cell.fill = PatternFill(start_color=c_zebra, end_color=c_zebra, fill_type="solid")

            ws_summary.row_dimensions[current_row].height = 20
            current_row += 1

        # Total Row
        ws_summary.cell(row=current_row, column=1, value="TOTAL").font = Font(name="Arial", size=9.5, bold=True, color=c_slate_dark)
        tot_c2 = ws_summary.cell(row=current_row, column=2, value=f"=SUM(B{start_row + 2}:B{current_row - 1})")
        tot_c3 = ws_summary.cell(row=current_row, column=3, value=f"=SUM(C{start_row + 2}:C{current_row - 1})")
        tot_c4 = ws_summary.cell(row=current_row, column=4, value="100.0%")

        for cell in (ws_summary.cell(row=current_row, column=1), tot_c2, tot_c3, tot_c4):
            cell.font = Font(name="Arial", size=9.5, bold=True)
            cell.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
            cell.border = header_border

        tot_c2.number_format = f'"{curr}"#,##0.00'
        tot_c3.alignment = Alignment(horizontal="center")
        tot_c4.alignment = Alignment(horizontal="right")
        ws_summary.row_dimensions[current_row].height = 22
        current_row += 2
    else:
        empty_cell = ws_summary.cell(row=current_row, column=1, value=get_statement_str('no_records', lang))
        empty_cell.font = Font(name="Arial", size=9, italic=True, color="64748B")
        current_row += 2

    # Confidential Audit Notice Footer
    ws_summary.merge_cells(f"A{current_row}:E{current_row}")
    notice_cell = ws_summary[f"A{current_row}"]
    notice_cell.value = get_statement_str('footer_notice', lang)
    notice_cell.font = Font(name="Arial", size=7.5, italic=True, color="94A3B8")
    notice_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[current_row].height = 18

    # -------------------------------------------------------------
    # SHEET 2: DETAILED TRANSACTION AUDIT LEDGER
    # -------------------------------------------------------------
    ws_tx = wb.create_sheet(title=get_statement_str('sheet_ledger', lang)[:31])
    ws_tx.views.sheetView[0].showGridLines = True

    # Ledger Title
    ws_tx.merge_cells("A1:F1")
    tx_title_cell = ws_tx["A1"]
    tx_title_cell.value = f"{get_statement_str('sec_ledger', lang)} ({period_label})"
    tx_title_cell.font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    tx_title_cell.fill = PatternFill(start_color=c_navy, end_color=c_navy, fill_type="solid")
    tx_title_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws_tx.row_dimensions[1].height = 32

    # Ledger Column Headers
    tx_headers = [
        "#",
        get_statement_str('col_date', lang),
        get_statement_str('col_category', lang),
        get_statement_str('col_desc', lang),
        get_statement_str('col_type', lang),
        f"{get_statement_str('col_amount', lang)} ({curr})"
    ]

    for col_idx, h_text in enumerate(tx_headers, start=1):
        c = ws_tx.cell(row=2, column=col_idx, value=h_text)
        c.font = Font(name="Arial", size=9.5, bold=True, color="FFFFFF")
        c.fill = PatternFill(start_color=c_slate_dark, end_color=c_slate_dark, fill_type="solid")
        c.alignment = Alignment(horizontal="center" if col_idx in (1, 2, 5) else ("right" if col_idx == 6 else "left"), vertical="center")
        c.border = header_border
    ws_tx.row_dimensions[2].height = 24

    t_row = 3
    for idx, tx in enumerate(expenses, start=1):
        is_inc = (tx['type'] == 'income')
        type_str = get_statement_str('type_income', lang) if is_inc else get_statement_str('type_expense', lang)

        c_idx = ws_tx.cell(row=t_row, column=1, value=idx)
        c_date = ws_tx.cell(row=t_row, column=2, value=tx['date'])
        c_cat = ws_tx.cell(row=t_row, column=3, value=tx['category'])
        c_note = ws_tx.cell(row=t_row, column=4, value=tx['note'] or "-")
        c_type = ws_tx.cell(row=t_row, column=5, value=type_str)
        c_amt = ws_tx.cell(row=t_row, column=6, value=float(tx['amount']))

        for c in (c_idx, c_date, c_cat, c_note, c_type, c_amt):
            c.font = Font(name="Arial", size=9)
            c.border = thin_border

        c_idx.alignment = Alignment(horizontal="center")
        c_date.alignment = Alignment(horizontal="center")
        c_type.alignment = Alignment(horizontal="center")
        c_amt.alignment = Alignment(horizontal="right")

        if is_inc:
            c_type.font = Font(name="Arial", size=9, bold=True, color=c_income)
            c_type.fill = PatternFill(start_color=c_income_bg, end_color=c_income_bg, fill_type="solid")
            c_amt.font = Font(name="Arial", size=9, bold=True, color=c_income)
        else:
            c_type.font = Font(name="Arial", size=9, bold=True, color=c_expense)
            c_amt.font = Font(name="Arial", size=9, bold=True, color=c_expense)

        c_amt.number_format = f'"{curr}"#,##0.00'

        if (t_row % 2) == 0 and not is_inc:
            for cell in (c_idx, c_date, c_cat, c_note):
                cell.fill = PatternFill(start_color=c_zebra, end_color=c_zebra, fill_type="solid")

        ws_tx.row_dimensions[t_row].height = 20
        t_row += 1

    if not expenses:
        empty_row = ws_tx.cell(row=t_row, column=1, value=get_statement_str('no_records', lang))
        empty_row.font = Font(name="Arial", size=9, italic=True, color="64748B")
        t_row += 1

    # Auto-adjust column widths for both sheets
    for ws in (ws_summary, ws_tx):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if cell.row in (1, 2):  # skip merged banners
                    continue
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    wb.save(file_path)
    return file_path

def generate_monthly_excel(user_id: int, first_name: str, year: int = None, month: int = None, lang: str = 'en', country_code: str = None) -> str:
    now = datetime.datetime.now()
    year = year or now.year
    month = month or now.month
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    period_label = datetime.date(year, month, 1).strftime("%B %Y")
    return generate_statement_excel(user_id, first_name, start_date, end_date, period_label, lang=lang, country_code=country_code)


def generate_client_report_excel(user_id: int, first_name: str, client_id: int = None, months: int = 1, start_date: str = None, end_date: str = None, period_label: str = None, lang: str = 'en', country_code: str = None) -> str:
    """Generates corporate executive multi-tab Excel workbook for clients (1 to 12 months)."""
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
    file_name = f"Client_Report_{c_code}_{user_id}_{target_tag}_{safe_start}_{safe_end}_{lang}.xlsx"
    file_path = os.path.join(PDF_TEMP_DIR, file_name)

    summary = get_client_period_summary(user_id, start_date, end_date, client_id=client_id, country_code=c_code)

    wb = Workbook()
    ws1 = wb.active
    ws1.title = get_client_statement_str('sheet_summary', lang)[:31]

    # Styling colors
    NAVY_FILL = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    SLATE_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    LIGHT_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    GREEN_FILL = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
    RED_FILL = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

    FONT_TITLE = Font(name="Arial", size=15, bold=True, color="FFFFFF")
    FONT_WHITE = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    FONT_BOLD = Font(name="Arial", size=10, bold=True, color="0F172A")
    FONT_REG = Font(name="Arial", size=9, color="334155")
    FONT_GREEN = Font(name="Arial", size=10, bold=True, color="166534")
    FONT_RED = Font(name="Arial", size=10, bold=True, color="991B1B")

    THIN_BORDER = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Header Banner
    if client_id:
        c_info = get_client(client_id, user_id)
        c_title_name = c_info['name'] if c_info else "Client"
        title_str = f"{get_client_statement_str('doc_title_single', lang)} - {c_title_name}"
    else:
        title_str = get_client_statement_str('doc_title_all', lang)

    ws1.merge_cells("A1:F2")
    ws1["A1"] = f"  {title_str}"
    ws1["A1"].font = FONT_TITLE
    ws1["A1"].fill = NAVY_FILL
    ws1["A1"].alignment = Alignment(vertical="center")

    # 2. Metadata
    ws1["A4"] = get_client_statement_str('lbl_account_holder', lang)
    ws1["B4"] = first_name
    ws1["A5"] = get_client_statement_str('lbl_period', lang)
    ws1["B5"] = period_label
    ws1["D4"] = get_client_statement_str('lbl_jurisdiction', lang)
    ws1["E4"] = f"{c_name} ({curr})"
    ws1["D5"] = get_client_statement_str('lbl_issue_date', lang)
    ws1["E5"] = now.strftime("%d %b %Y, %I:%M %p")

    for r in range(4, 6):
        for c in [1, 2, 4, 5]:
            cell = ws1.cell(row=r, column=c)
            cell.font = FONT_BOLD if c in (1, 4) else FONT_REG
            cell.fill = LIGHT_FILL
            cell.border = THIN_BORDER

    # 3. KPI Cards
    ws1["A7"] = get_client_statement_str('lbl_total_receivable', lang)
    ws1["A8"] = summary['total_receivable']
    ws1["A8"].number_format = f'"{curr}"#,##0.00'
    ws1["A8"].font = FONT_GREEN
    ws1["A8"].fill = GREEN_FILL

    ws1["C7"] = get_client_statement_str('lbl_total_payable', lang)
    ws1["C8"] = summary['total_payable']
    ws1["C8"].number_format = f'"{curr}"#,##0.00'
    ws1["C8"].font = FONT_RED
    ws1["C8"].fill = RED_FILL

    ws1["E7"] = get_client_statement_str('lbl_net_position', lang)
    ws1["E8"] = summary['net_position']
    ws1["E8"].number_format = f'"{curr}"#,##0.00'
    ws1["E8"].font = FONT_BOLD
    ws1["E8"].fill = LIGHT_FILL

    for k in ["A7", "C7", "E7"]:
        ws1[k].font = FONT_BOLD
        ws1[k].fill = LIGHT_FILL
        ws1[k].border = THIN_BORDER
    for k in ["A8", "C8", "E8"]:
        ws1[k].border = THIN_BORDER

    # 4. Table of Clients
    row_idx = 11
    headers = [
        get_client_statement_str('col_client', lang),
        get_client_statement_str('lbl_phone', lang),
        get_client_statement_str('lbl_email', lang),
        get_client_statement_str('lbl_total_receivable', lang),
        get_client_statement_str('lbl_total_payable', lang),
        get_client_statement_str('col_balance', lang),
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws1.cell(row=row_idx, column=col_idx, value=h)
        cell.font = FONT_WHITE
        cell.fill = SLATE_FILL
        cell.alignment = Alignment(horizontal="center" if col_idx > 3 else "left")
        cell.border = THIN_BORDER

    for c in summary['clients']:
        row_idx += 1
        ws1.cell(row=row_idx, column=1, value=c['name']).font = FONT_BOLD
        ws1.cell(row=row_idx, column=2, value=c.get('phone') or "-").font = FONT_REG
        ws1.cell(row=row_idx, column=3, value=c.get('email') or "-").font = FONT_REG

        c_rec = ws1.cell(row=row_idx, column=4, value=c.get('total_lena', 0.0))
        c_rec.number_format = f'"{curr}"#,##0.00'
        c_rec.font = FONT_GREEN

        c_pay = ws1.cell(row=row_idx, column=5, value=c.get('total_dena', 0.0))
        c_pay.number_format = f'"{curr}"#,##0.00'
        c_pay.font = FONT_RED

        c_bal = ws1.cell(row=row_idx, column=6, value=f"=D{row_idx}-E{row_idx}")
        c_bal.number_format = f'"{curr}"#,##0.00'
        c_bal.font = FONT_BOLD

        for c_num in range(1, 7):
            ws1.cell(row=row_idx, column=c_num).border = THIN_BORDER

    # Auto-fit columns
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 13)

    # 5. Sheet 2: Transaction Ledger
    ws2 = wb.create_sheet(title=get_client_statement_str('sheet_ledger', lang)[:31])
    ws2.merge_cells("A1:E2")
    ws2["A1"] = f"  {get_client_statement_str('sec_ledger', lang)}"
    ws2["A1"].font = FONT_TITLE
    ws2["A1"].fill = NAVY_FILL
    ws2["A1"].alignment = Alignment(vertical="center")

    tx_headers = [
        get_client_statement_str('col_date', lang),
        get_client_statement_str('col_client', lang),
        get_client_statement_str('col_type', lang),
        get_client_statement_str('col_amount', lang),
        get_client_statement_str('col_note', lang),
    ]
    for col_idx, h in enumerate(tx_headers, 1):
        cell = ws2.cell(row=4, column=col_idx, value=h)
        cell.font = FONT_WHITE
        cell.fill = SLATE_FILL
        cell.alignment = Alignment(horizontal="center" if col_idx in (1, 3) else "left")
        cell.border = THIN_BORDER

    r_tx = 4
    for t in summary['transactions']:
        r_tx += 1
        ws2.cell(row=r_tx, column=1, value=t['date']).font = FONT_REG
        ws2.cell(row=r_tx, column=2, value=t.get('client_name') or "Client").font = FONT_BOLD
        ws2.cell(row=r_tx, column=3, value=t['type'].upper()).font = FONT_BOLD
        amt_cell = ws2.cell(row=r_tx, column=4, value=t['amount'])
        amt_cell.number_format = f'"{curr}"#,##0.00'
        amt_cell.font = FONT_GREEN if t['type'] == 'lena' else FONT_RED
        ws2.cell(row=r_tx, column=5, value=t.get('note') or "-").font = FONT_REG
        for c_num in range(1, 6):
            ws2.cell(row=r_tx, column=c_num).border = THIN_BORDER

    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 3, 14)

    wb.save(file_path)
    return file_path
