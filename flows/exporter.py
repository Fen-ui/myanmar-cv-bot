"""
CV Exporter — Excel + Google Sheets
"""
import os, logging
from datetime import datetime
from config import OUTPUT_DIR

log = logging.getLogger(__name__)


async def export_excel(raw_data: dict, session_id: str):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        log.error("openpyxl not installed")
        return None
    try:
        wb  = openpyxl.Workbook()
        ws  = wb.active
        ws.title = "CV Data"
        hdr_font  = Font(name="Arial", bold=True, size=11, color="FFFFFF")
        hdr_fill  = PatternFill("solid", fgColor="1565C0")
        lbl_font  = Font(name="Arial", bold=True, size=10, color="1A237E")
        lbl_fill  = PatternFill("solid", fgColor="E3F2FD")
        val_font  = Font(name="Arial", size=10)
        wrap      = Alignment(horizontal="left", vertical="top", wrap_text=True)
        thin      = Side(style="thin", color="BBDEFB")
        border    = Border(left=thin, right=thin, top=thin, bottom=thin)

        ws.merge_cells("A1:C1")
        tc = ws["A1"]
        tc.value     = "Myanmar CV Builder — Exported Data"
        tc.font      = Font(name="Arial", bold=True, size=14, color="FFFFFF")
        tc.fill      = PatternFill("solid", fgColor="0D47A1")
        tc.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        for col, h in enumerate(["Section","Field","Content"], 1):
            cell = ws.cell(row=2, column=col, value=h)
            cell.font = hdr_font; cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border
        ws.row_dimensions[2].height = 20

        ROWS = [
            ("Personal","Full Name","full_name"),
            ("Personal","Date of Birth","dob"),
            ("Personal","Nationality","nationality"),
            ("Personal","Phone","phone"),
            ("Personal","Email","email"),
            ("Personal","Address","address"),
            ("Career","Objective","objective"),
            ("Education","Qualifications","education"),
            ("Experience","Work History","experience"),
            ("Skills","Technical Skills","skills"),
            ("Languages","Languages","languages"),
            ("References","References","references"),
            ("Meta","Template","template"),
        ]

        for ri, (sec, fld, key) in enumerate(ROWS, 3):
            v = raw_data.get(key, "")
            if isinstance(v, list):
                value = "\n".join(f"• {str(i)}" for i in v) if v else "—"
            else:
                value = str(v) if v else "—"
            for col, (val, font, fill) in enumerate([
                (sec, Font(name="Arial",size=9,color="777777",italic=True), None),
                (fld, lbl_font, lbl_fill),
                (value, val_font, None),
            ], 1):
                cell = ws.cell(row=ri, column=col, value=val)
                cell.font = font
                if fill: cell.fill = fill
                cell.alignment = wrap
                cell.border = border
            ws.row_dimensions[ri].height = max(15, value.count("\n")*14+14)

        ws.column_dimensions["A"].width = 16
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 55
        ws.freeze_panes = "A3"

        fname = f"CV_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path  = os.path.join(OUTPUT_DIR, fname)
        wb.save(path)
        log.info("[exporter] Excel → %s", path)
        return path
    except Exception as e:
        log.error("[exporter] Excel failed: %s", e)
        return None


async def export_all(raw_data, session_id, choice="1", **kwargs) -> dict:
    result = {"excel_path": None, "sheets_url": None}
    if choice in ("2","4"):
        result["excel_path"] = await export_excel(raw_data, session_id)
    return result


MSG_EXPORT_CHOICE = """📤 *Export format ရွေးပါ:*

1️⃣ — PDF only
2️⃣ — PDF + Excel (.xlsx)
3️⃣ — PDF + Google Sheets
4️⃣ — အားလုံး

*1, 2, 3 သို့မဟုတ် 4 ရိုက်ပါ:*"""


def format_export_done(pdf_path, excel_path=None, sheets_url=None) -> str:
    lines = []
    if pdf_path:   lines.append(f"📄 PDF: {os.path.basename(pdf_path)}")
    if excel_path: lines.append(f"📊 Excel: {os.path.basename(excel_path)}")
    if sheets_url: lines.append(f"🔗 Sheets: {sheets_url}")
    return "\n".join(lines)
