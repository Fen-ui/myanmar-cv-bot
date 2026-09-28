"""
Myanmar CV Builder Bot — main.py
"""
import asyncio, logging, sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from telegram.ext import Application
from config import BOT_TOKEN
import db
from handlers.cv_handler import register

logging.basicConfig(
    format="%(asctime)s [%(name)-20s] %(levelname)s  %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


async def run():
    db.init()
    log.info("✅ Database ready")
    app = Application.builder().token(BOT_TOKEN).build()
    try:
        me = await app.bot.get_me()
        log.info("✅ Bot → @%s (ID: %d)", me.username, me.id)
    except Exception as e:
        log.error("❌ Bot token error: %s", e)
        return
    register(app)
    log.info("✅ Handlers registered")
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message","callback_query"],
        )
        log.info("\n🤖 Myanmar CV Builder Bot is running!\n   Ctrl-C to stop.\n")
        try:
            await asyncio.Event().wait()
        finally:
            await app.updater.stop()
            await app.stop()
    log.info("Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass
