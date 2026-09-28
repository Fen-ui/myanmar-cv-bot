"""
Myanmar CV Builder — Conversation Flow
"""

FIELDS = [
    {"key":"full_name","label":"နာမည် အပြည့်အစုံ","question":"👤 သင့်နာမည် အပြည့်အစုံ ရိုက်ထည့်ပါ။\n_(ဥပမာ - အောင်ကျော်ဇင်)_","required":True,"step":1},
    {"key":"dob","label":"မွေးသက္ကရာဇ်","question":"🎂 မွေးသက္ကရာဇ် ရိုက်ထည့်ပါ။\n_(ဥပမာ - 15/03/1995)_","required":True,"step":2},
    {"key":"nationality","label":"နိုင်ငံသား","question":"🏳️ နိုင်ငံသား\n_(ဥပမာ - မြန်မာ)_","required":True,"step":3},
    {"key":"phone","label":"ဖုန်းနံပတ်","question":"📱 ဆက်သွယ်ရမည့် ဖုန်းနံပတ် ရိုက်ထည့်ပါ။\n_(ဥပမာ - 09123456789)_","required":True,"step":4},
    {"key":"email","label":"အီးမေးလ်","question":"📧 Email လိပ်စာ ရိုက်ထည့်ပါ။\n_(မရှိပါက /skip ရိုက်ပါ)_","required":False,"step":5},
    {"key":"address","label":"နေရပ်လိပ်စာ","question":"🏠 နေရပ်လိပ်စာ ရိုက်ထည့်ပါ။\n_(မြို့နယ်၊ တိုင်းဒေသကြီး)_","required":True,"step":6},
    {"key":"education","label":"ပညာအရည်အချင်း","question":"🎓 ပညာအရည်အချင်း ရေးပါ။\n_(ဥပမာ - B.C.Sc, RIT, 2018)_","required":True,"step":7},
    {"key":"experience","label":"အလုပ်အတွေ့အကြုံ","question":"💼 အလုပ်အတွေ့အကြုံ ရေးပါ။\n_(မရှိပါက /skip ရိုက်ပါ)_","required":False,"step":8},
    {"key":"skills","label":"ကျွမ်းကျင်မှုများ","question":"⚡ ကျွမ်းကျင်မှုများ ရေးပါ။\n_(ဥပမာ - Python, MS Office)_","required":True,"step":9},
    {"key":"languages","label":"ဘာသာစကား","question":"🌐 တတ်ကျွမ်းသောဘာသာစကားများ ရေးပါ။\n_(ဥပမာ - မြန်မာ (မိခင်ဘာသာ), အင်္ဂလိပ်)_","required":True,"step":10},
    {"key":"references","label":"ကိုးကားစာ","question":"📋 ကိုးကားစာ ပေးနိုင်သူ ရေးပါ။\n_(မရှိပါက /skip ရိုက်ပါ)_","required":False,"step":11},
    {"key":"objective","label":"ရည်ရွယ်ချက်","question":"🎯 Career Objective ရေးပါ။\n_(မရှိပါက /skip ရိုက်ပါ)_","required":False,"step":12},
]

TOTAL_STEPS = len(FIELDS)

TEMPLATES = {
    "1": {"key":"modern",   "name":"Modern Blue",         "emoji":"🔵"},
    "2": {"key":"classic",  "name":"Classic Professional", "emoji":"⚫"},
    "3": {"key":"creative", "name":"Creative Dark",        "emoji":"🟣"},
    "4": {"key":"myanmar",  "name":"Myanmar Traditional",  "emoji":"🟡"},
}

MSG_WELCOME = """🌟 *မင်္ဂလာပါ! CV Builder Bot မှ ကြိုဆိုပါသည်။*

ဤ Bot သည် သင့်အား လှပသော CV PDF ကို အလိုအလျောက် ပြုလုပ်ပေးပါမည်။

📋 *CV Template ရွေးချယ်ပါ:*

🔵 1 — Modern Blue
⚫ 2 — Classic Professional
🟣 3 — Creative Dark
🟡 4 — Myanmar Traditional

*1, 2, 3 သို့မဟုတ် 4 ရိုက်ပါ။*"""

MSG_TEMPLATE_CHOSEN = """✅ *{emoji} {name}* template ရွေးပြီးပါပြီ!

📝 မေးခွန်း {total} ခုသာ ဖြေရပါမည်။

/cancel — ပြန်ထွက်နိုင်သည်
/skip — optional မေးခွန်းများ ကျော်နိုင်သည်

━━━━━━━━━━━━━━━━━━━━"""

MSG_PROGRESS = "📊 *တိုးတက်မှု: {step}/{total}*\n━━━━━━━━━━━━━━━━━━━━\n\n"
MSG_SKIP_REQUIRED = "⚠️ ဤမေးခွန်းကို မဖြေမဖြစ် ဖြေရပါမည်:"
MSG_GENERATING = "⏳ *CV ပြောင်းဆွဲနေပါသည်...*\n\n🤖 AI ပြင်ဆင်နေသည်...\n📄 PDF ဖန်တီးနေသည်...\n\nခဏစောင့်ပါ ⏱"
MSG_DONE = "✅ *CV ပြီးပါပြီ!*\n\n📄 {filename}\n🎨 Template: {template}\n📅 {date}\n\n💡 နောက်ထပ် CV → /start"
MSG_CANCEL = "❌ *CV ပြုလုပ်ခြင်း ရပ်ဆိုင်းလိုက်ပါသည်။*\n\nနောက်တစ်ကြိမ် → /start"
MSG_INVALID_TEMPLATE = "⚠️ 1, 2, 3 သို့မဟုတ် 4 သာ ရိုက်ပါ:"
MSG_ERROR = "❌ *အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့သည်။*\n\n/start ပြန်ရိုက်ပါ။"
MSG_PHOTO_ASK = "📸 *ဓာတ်ပုံ ထည့်သွင်းလိုပါသလား?*\n\n📷 ဓာတ်ပုံ ပေးပို့ပါ _သို့မဟုတ်_\n/skip ရိုက်၍ ကျော်ပါ"
MSG_PHOTO_SAVED = "✅ ဓာတ်ပုံ သိမ်းပြီးပါပြီ!"
MSG_EXPORT_CHOICE = """📤 *Export format ရွေးပါ:*

1️⃣ — PDF only
2️⃣ — PDF + Excel (.xlsx)
3️⃣ — PDF + Google Sheets
4️⃣ — အားလုံး

*1, 2, 3 သို့မဟုတ် 4 ရိုက်ပါ:*"""


def get_next_empty_field(data: dict, from_step: int = 1):
    for f in FIELDS:
        if f["step"] >= from_step and f["key"] not in data:
            return f
    return None


def is_complete(data: dict) -> bool:
    return all(f["key"] in data for f in FIELDS if f["required"])


def build_summary(data: dict) -> str:
    lines = ["📋 *CV အချက်အလက် အကျဉ်းချုပ်*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for f in FIELDS:
        val = data.get(f["key"], "—")
        lines.append(f"*{f['label']}:* {val}")
    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def format_progress(step: int) -> str:
    filled = "█" * step
    empty  = "░" * (TOTAL_STEPS - step)
    pct    = int(step / TOTAL_STEPS * 100)
    return f"{filled}{empty} {pct}%"
