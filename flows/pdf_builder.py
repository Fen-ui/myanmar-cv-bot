"""
CV PDF Builder — 4 Templates
"""
import os, logging, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from config import OUTPUT_DIR

log = logging.getLogger(__name__)
W, H   = A4
MARGIN = 18 * mm

PALETTES = {
    "modern":   {"primary":colors.HexColor("#1565C0"),"secondary":colors.HexColor("#E3F2FD"),"accent":colors.HexColor("#0D47A1"),"text":colors.HexColor("#212121"),"light":colors.HexColor("#F5F5F5"),"white":colors.white,"line":colors.HexColor("#BBDEFB"),"sidebar_bg":colors.HexColor("#1565C0"),"sidebar_fg":colors.white},
    "classic":  {"primary":colors.HexColor("#212121"),"secondary":colors.HexColor("#F5F5F5"),"accent":colors.HexColor("#455A64"),"text":colors.HexColor("#212121"),"light":colors.HexColor("#FAFAFA"),"white":colors.white,"line":colors.HexColor("#B0BEC5"),"sidebar_bg":colors.HexColor("#37474F"),"sidebar_fg":colors.white},
    "creative": {"primary":colors.HexColor("#7B1FA2"),"secondary":colors.HexColor("#F3E5F5"),"accent":colors.HexColor("#E040FB"),"text":colors.HexColor("#212121"),"light":colors.HexColor("#FCE4EC"),"white":colors.white,"line":colors.HexColor("#CE93D8"),"sidebar_bg":colors.HexColor("#4A148C"),"sidebar_fg":colors.white},
    "myanmar":  {"primary":colors.HexColor("#B71C1C"),"secondary":colors.HexColor("#FFF8E1"),"accent":colors.HexColor("#F57F17"),"text":colors.HexColor("#212121"),"light":colors.HexColor("#FFF3E0"),"white":colors.white,"line":colors.HexColor("#FFCC80"),"sidebar_bg":colors.HexColor("#B71C1C"),"sidebar_fg":colors.white},
}


def _s(p):
    return {
        "name":    ParagraphStyle("name",fontSize=20,fontName="Helvetica-Bold",textColor=p["sidebar_fg"],alignment=TA_CENTER,spaceAfter=2,leading=24),
        "sub":     ParagraphStyle("sub",fontSize=8,fontName="Helvetica",textColor=p["sidebar_fg"],alignment=TA_CENTER,spaceAfter=1,leading=11),
        "sec":     ParagraphStyle("sec",fontSize=10,fontName="Helvetica-Bold",textColor=p["primary"],spaceAfter=3,spaceBefore=8,leading=13),
        "body":    ParagraphStyle("body",fontSize=9,fontName="Helvetica",textColor=p["text"],leading=13,spaceAfter=2),
        "bold":    ParagraphStyle("bold",fontSize=9.5,fontName="Helvetica-Bold",textColor=p["text"],leading=13,spaceAfter=1),
        "tag":     ParagraphStyle("tag",fontSize=8.5,fontName="Helvetica",textColor=p["primary"],leading=12),
        "footer":  ParagraphStyle("footer",fontSize=7,fontName="Helvetica",textColor=colors.HexColor("#999999"),alignment=TA_CENTER),
        "sl":      ParagraphStyle("sl",fontSize=8,fontName="Helvetica-Bold",textColor=p["accent"],leading=11,spaceAfter=2),
        "sv":      ParagraphStyle("sv",fontSize=8.5,fontName="Helvetica",textColor=p["sidebar_fg"],leading=12,spaceAfter=5,wordWrap="LTR"),
    }


def _sec(title, st, p):
    return [HRFlowable(width="100%",thickness=1.5,color=p["primary"],spaceAfter=3),
            Paragraph(title.upper(), st["sec"])]


def _exp(lst, st, p):
    items = []
    for e in lst:
        if not e: continue
        rt = Table([[Paragraph(f"<b>{e.get('title','')}</b>",st["bold"]),
                     Paragraph(e.get("period",""),ParagraphStyle("pr",fontSize=8,fontName="Helvetica",textColor=p["accent"],alignment=TA_RIGHT))]],
                   colWidths=["70%","30%"])
        rt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),1),("TOPPADDING",(0,0),(-1,-1),0)]))
        items.append(rt)
        if e.get("company"):
            items.append(Paragraph(e["company"],ParagraphStyle("co",fontSize=8.5,fontName="Helvetica",textColor=p["accent"],leading=12,spaceAfter=2,italic=True)))
        for d in e.get("duties",[]):
            items.append(Paragraph(f"• {d}",st["body"]))
        items.append(Spacer(1,4))
    return items


def _edu(lst, st, p):
    items = []
    for e in lst:
        rt = Table([[Paragraph(f"<b>{e.get('degree','')}</b>",st["bold"]),
                     Paragraph(e.get("year",""),ParagraphStyle("yr",fontSize=8,fontName="Helvetica",textColor=p["accent"],alignment=TA_RIGHT))]],
                   colWidths=["70%","30%"])
        rt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),1),("TOPPADDING",(0,0),(-1,-1),0)]))
        items.append(rt)
        if e.get("institution"):
            items.append(Paragraph(e["institution"],ParagraphStyle("ist",fontSize=8,fontName="Helvetica",textColor=p["accent"],leading=12,spaceAfter=3,italic=True)))
    return items


def _skills(lst, st, p):
    if not lst: return []
    cells = [Paragraph(f"  {s}  ",st["tag"]) for s in lst]
    cols  = min(4,len(cells))
    while len(cells)%cols: cells.append(Paragraph("",st["tag"]))
    rows  = [cells[i:i+cols] for i in range(0,len(cells),cols)]
    cw    = [(W-2*MARGIN)/cols]*cols
    tbl   = Table(rows,colWidths=cw)
    tbl.setStyle(TableStyle([("BOX",(0,0),(-1,-1),0.5,p["line"]),("INNERGRID",(0,0),(-1,-1),0.5,p["line"]),("BACKGROUND",(0,0),(-1,-1),p["secondary"]),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5)]))
    return [tbl]


def _footer(story, st):
    story.append(Spacer(1,6))
    story.append(HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#CCCCCC"),spaceAfter=4))
    story.append(Paragraph(f"Generated by Myanmar CV Builder Bot · {datetime.now().strftime('%d %b %Y')}",st["footer"]))


def generate_cv(processed_data: dict, template: str, session_id: str) -> str:
    p    = PALETTES.get(template, PALETTES["modern"])
    st   = _s(p)
    name = processed_data.get("full_name","Unknown").replace(" ","_")
    path = os.path.join(OUTPUT_DIR, f"CV_{name}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=MARGIN*1.5, rightMargin=MARGIN*1.5,
                             topMargin=MARGIN, bottomMargin=MARGIN)
    story = []

    # Header
    story.append(Paragraph(processed_data.get("full_name",""), ParagraphStyle("n",fontSize=22,fontName="Helvetica-Bold",textColor=p["primary"],alignment=TA_CENTER,spaceAfter=4)))
    story.append(HRFlowable(width="100%",thickness=2,color=p["primary"],spaceAfter=4))

    contacts = [v for k,v in processed_data.items() if k in ("phone","email","address") and v]
    story.append(Paragraph("  ·  ".join(contacts), ParagraphStyle("cc",fontSize=9,fontName="Helvetica",textColor=p["accent"],alignment=TA_CENTER,spaceAfter=8)))

    if processed_data.get("objective"):
        story += _sec("Career Objective", st, p)
        story.append(Paragraph(processed_data["objective"], st["body"]))

    if processed_data.get("education"):
        story += _sec("Education", st, p)
        story += _edu(processed_data["education"], st, p)

    if processed_data.get("experience"):
        story += _sec("Work Experience", st, p)
        story += _exp(processed_data["experience"], st, p)

    if processed_data.get("skills"):
        story += _sec("Skills", st, p)
        story += _skills(processed_data["skills"], st, p)
        story.append(Spacer(1,6))

    if processed_data.get("languages"):
        story += _sec("Languages", st, p)
        for lang in processed_data["languages"]:
            story.append(Paragraph(f"• {lang.get('language','')} ({lang.get('level','')})", st["body"]))

    if processed_data.get("references"):
        story += _sec("References", st, p)
        for r in processed_data["references"]:
            story.append(Paragraph(f"<b>{r.get('name','')}</b> — {r.get('title','')} — {r.get('company','')}", st["body"]))

    _footer(story, st)
    doc.build(story)
    log.info("[pdf] %s → %s", template, path)
    return path
