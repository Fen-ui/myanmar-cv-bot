"""
CV Handler — Telegram ConversationHandler
"""
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import db
from flows.conversation import (
    FIELDS, TEMPLATES, TOTAL_STEPS,
    MSG_WELCOME, MSG_TEMPLATE_CHOSEN, MSG_PROGRESS,
    MSG_GENERATING, MSG_DONE, MSG_CANCEL,
    MSG_INVALID_TEMPLATE, MSG_ERROR,
    MSG_PHOTO_ASK, MSG_PHOTO_SAVED, MSG_SKIP_REQUIRED,
    get_next_empty_field, is_complete, build_summary, format_progress,
)
from flows.exporter import export_all, MSG_EXPORT_CHOICE

log = logging.getLogger(__name__)

CHOOSE_TEMPLATE, COLLECT_FIELD, ASK_PHOTO, CHOOSE_EXPORT, CONFIRM_SUBMIT = range(5)

TEMPLATE_KB = ReplyKeyboardMarkup([["1","2"],["3","4"]], resize_keyboard=True, one_time_keyboard=True)
EXPORT_KB   = ReplyKeyboardMarkup([["1","2"],["3","4"]], resize_keyboard=True, one_time_keyboard=True)
CONFIRM_KB  = ReplyKeyboardMarkup([["✅ အတည်ပြုမည်","✏️ ပြင်ဆင်မည်"],["❌ ပယ်ဖျက်မည်"]], resize_keyboard=True, one_time_keyboard=True)
SKIP_KB     = ReplyKeyboardMarkup([["/skip"]], resize_keyboard=True)
CANCEL_KB   = ReplyKeyboardMarkup([["/cancel"]], resize_keyboard=True)


async def _ask_field(msg, context, field):
    step   = field["step"]
    header = MSG_PROGRESS.format(step=step, total=TOTAL_STEPS)
    text   = header + field["question"]
    kb     = SKIP_KB if not field["required"] else CANCEL_KB
    await msg.reply_text(text, reply_markup=kb, parse_mode="Markdown")
    context.user_data["current_field"] = field["key"]


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, username=user.username or "", full_name=user.full_name or "")
    old_sid = context.user_data.get("session_id")
    if old_sid: db.cancel_session(old_sid)
    context.user_data.clear()
    await update.message.reply_text(MSG_WELCOME, reply_markup=TEMPLATE_KB, parse_mode="Markdown")
    return CHOOSE_TEMPLATE


async def choose_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    tmpl = TEMPLATES.get(text)
    if not tmpl:
        await update.message.reply_text(MSG_INVALID_TEMPLATE, reply_markup=TEMPLATE_KB)
        return CHOOSE_TEMPLATE
    user = update.effective_user
    sid  = db.new_session(user.id, tmpl["key"])
    context.user_data.update({"session_id":sid,"template":tmpl["key"],"data":{}})
    await update.message.reply_text(
        MSG_TEMPLATE_CHOSEN.format(emoji=tmpl["emoji"],name=tmpl["name"],total=TOTAL_STEPS),
        reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    await _ask_field(update.message, context, FIELDS[0])
    return COLLECT_FIELD


async def collect_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    field_key  = context.user_data.get("current_field")
    data       = context.user_data.setdefault("data",{})
    sid        = context.user_data.get("session_id","")
    field      = next((f for f in FIELDS if f["key"]==field_key), None)
    if not field: return ConversationHandler.END
    data[field_key] = user_input
    db.save_field(sid, field_key, user_input)
    next_field = get_next_empty_field(data, from_step=field["step"]+1)
    if next_field:
        await _ask_field(update.message, context, next_field)
        return COLLECT_FIELD
    await update.message.reply_text(MSG_PHOTO_ASK, reply_markup=SKIP_KB, parse_mode="Markdown")
    return ASK_PHOTO


async def skip_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field_key = context.user_data.get("current_field")
    data      = context.user_data.setdefault("data",{})
    sid       = context.user_data.get("session_id","")
    field     = next((f for f in FIELDS if f["key"]==field_key), None)
    if field and field["required"]:
        await update.message.reply_text(MSG_SKIP_REQUIRED, reply_markup=SKIP_KB, parse_mode="Markdown")
        return COLLECT_FIELD
    data[field_key] = "—"
    db.save_field(sid, field_key, "—")
    next_field = get_next_empty_field(data, from_step=field["step"]+1) if field else None
    if next_field:
        await _ask_field(update.message, context, next_field)
        return COLLECT_FIELD
    await update.message.reply_text(MSG_PHOTO_ASK, reply_markup=SKIP_KB, parse_mode="Markdown")
    return ASK_PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file  = await photo.get_file()
    sid   = context.user_data.get("session_id","")
    path  = f"cv_output/photo_{sid}.jpg"
    await file.download_to_drive(path)
    context.user_data["photo_path"] = path
    db.save_field(sid, "photo_path", path)
    await update.message.reply_text(MSG_PHOTO_SAVED, parse_mode="Markdown")
    return await _show_summary(update.message, context)


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo_path"] = None
    return await _show_summary(update.message, context)


async def _show_summary(msg, context):
    data = context.user_data.get("data",{})
    await msg.reply_text(
        build_summary(data) + "\n\nအချက်အလက်များ မှန်ကန်ပါသလား?",
        reply_markup=CONFIRM_KB, parse_mode="Markdown")
    return CONFIRM_SUBMIT


async def confirm_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "❌ ပယ်ဖျက်မည်":
        db.cancel_session(context.user_data.get("session_id",""))
        context.user_data.clear()
        await update.message.reply_text(MSG_CANCEL, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
        return ConversationHandler.END
    if text == "✏️ ပြင်ဆင်မည်":
        context.user_data["data"] = {}
        await _ask_field(update.message, context, FIELDS[0])
        return COLLECT_FIELD
    if text == "✅ အတည်ပြုမည်":
        await update.message.reply_text(MSG_EXPORT_CHOICE, reply_markup=EXPORT_KB, parse_mode="Markdown")
        return CHOOSE_EXPORT
    await update.message.reply_text("✅, ✏️ သို့မဟုတ် ❌ ရွေးပါ:", reply_markup=CONFIRM_KB)
    return CONFIRM_SUBMIT


async def choose_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text not in ("1","2","3","4"):
        await update.message.reply_text("1, 2, 3 သို့မဟုတ် 4 ရိုက်ပါ:", reply_markup=EXPORT_KB)
        return CHOOSE_EXPORT
    context.user_data["export_choice"] = text
    await update.message.reply_text(MSG_GENERATING, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return await _generate_and_send(update, context)


async def _generate_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from flows.ai_writer   import process_cv_data
    from flows.pdf_builder import generate_cv
    from datetime import datetime

    data     = context.user_data.get("data",{})
    sid      = context.user_data.get("session_id","")
    template = context.user_data.get("template","modern")
    choice   = context.user_data.get("export_choice","1")
    user     = update.effective_user

    data["photo_path"] = context.user_data.get("photo_path")
    data["template"]   = template

    try:
        processed    = await process_cv_data(data)
        pdf_path     = generate_cv(processed, template, sid)
        export_result= await export_all(data, sid, choice)
        db.complete_session(sid, pdf_path)
        db.increment_cv_count(user.id)

        with open(pdf_path,"rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"CV_{data.get('full_name','').replace(' ','_')}.pdf",
                caption=f"✅ *CV PDF ပြီးပါပြီ!*\nTemplate: {template.capitalize()}\n\nCV ကောင်းကောင်းဖြင့် အလုပ်ရပါစေ! 🙏",
                parse_mode="Markdown")

        if export_result.get("excel_path"):
            with open(export_result["excel_path"],"rb") as f:
                await update.message.reply_document(document=f,
                    filename=f"CV_{data.get('full_name','').replace(' ','_')}.xlsx",
                    caption="📊 Excel file")

        await update.message.reply_text(
            MSG_DONE.format(filename=f"CV_{data.get('full_name','')}.pdf",
                            template=template.capitalize(),
                            date=datetime.now().strftime("%d %b %Y")),
            parse_mode="Markdown")
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        log.error("[cv_handler] %s", e)
        await update.message.reply_text(MSG_ERROR, parse_mode="Markdown")
        return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sid = context.user_data.get("session_id")
    if sid: db.cancel_session(sid)
    context.user_data.clear()
    await update.message.reply_text(MSG_CANCEL, reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return ConversationHandler.END


async def cmd_mycvs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    cvs = db.get_user_cvs(uid)
    if not cvs:
        await update.message.reply_text("📂 CV မှတ်တမ်း မရှိသေးပါ။\n/start ဖြင့် CV ပြုလုပ်ပါ။")
        return
    lines = ["📂 *သင့် CV မှတ်တမ်း*\n"]
    for i, cv in enumerate(cvs,1):
        lines.append(f"{i}. Template: {cv['template'].capitalize()}\n   ရက်: {(cv['completed_at'] or '')[:16]}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = db.get_stats()
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n"
        f"👤 Total users: {stats['total_users']}\n"
        f"📄 Total CVs:   {stats['total_cvs']}\n"
        f"📅 Today CVs:   {stats['today_cvs']}",
        parse_mode="Markdown")


def register(app):
    conv = ConversationHandler(
        entry_points=[CommandHandler("start",cmd_start),CommandHandler("template",cmd_start)],
        states={
            CHOOSE_TEMPLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_template)],
            COLLECT_FIELD:   [CommandHandler("skip",skip_field),CommandHandler("cancel",cmd_cancel),MessageHandler(filters.TEXT & ~filters.COMMAND, collect_field)],
            ASK_PHOTO:       [CommandHandler("skip",skip_photo),CommandHandler("cancel",cmd_cancel),MessageHandler(filters.PHOTO,receive_photo),MessageHandler(filters.TEXT & ~filters.COMMAND,skip_photo)],
            CONFIRM_SUBMIT:  [CommandHandler("cancel",cmd_cancel),MessageHandler(filters.TEXT & ~filters.COMMAND,confirm_submit)],
            CHOOSE_EXPORT:   [CommandHandler("cancel",cmd_cancel),MessageHandler(filters.TEXT & ~filters.COMMAND,choose_export)],
        },
        fallbacks=[CommandHandler("start",cmd_start),CommandHandler("cancel",cmd_cancel)],
        per_user=True, per_chat=True, allow_reentry=True,
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("mycvs", cmd_mycvs))
    app.add_handler(CommandHandler("stats",  cmd_stats))
