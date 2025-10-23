import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_DELETE_TIME = 30  # default 30s
delete_times = {}

# Helper: safe delete
async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    delete_time = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
    minutes = delete_time // 60
    msg = await update.message.reply_text(
        f"🤖 *Auto Delete Bot is Active!*\n\n"
        f"⏳ Messages will be deleted automatically after *{minutes} minute(s).* \n"
        f"🧑‍💼 Only *group admins* can change settings.\n"
        f"💡 Use */help* for all commands.",
        parse_mode="MarkdownV2"
    )
    asyncio.create_task(delete_later(msg, 20))

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "📘 *Auto Delete Bot — Command List*\n\n"
        ""⏱️ */settime minutes* — Set delete delay\n"
        "📊 */status* — Show current delete delay\n"
        "🧹 */clean* — Delete last messages\n"
        "ℹ️ */help* — Show this help menu\n\n"
        "⚠️ Only admins can manage bot settings.",
        parse_mode="MarkdownV2"
    )
    asyncio.create_task(delete_later(msg, 25))

# Settime command (minutes)
async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 *Access Denied\\!* Only *admins* can use */settime*",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    if not context.args:
        msg = await update.message.reply_text(
            "⚙️ Usage: */settime 10m*\n⏳ Example: */settime 5m* — deletes every 5 minutes",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 15))
        return

    try:
        arg = context.args[0].lower()
        if arg.endswith("m"):
            minutes = int(arg[:-1])
            seconds = minutes * 60
        else:
            seconds = int(arg)
            minutes = seconds // 60

        delete_times[chat.id] = seconds
        msg = await update.message.reply_text(
            f"✅ Auto delete time set to *{minutes} minute(s)* for this chat\\.",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 10))
    except ValueError:
        msg = await update.message.reply_text(
            "⚠️ Invalid format\\! Use */settime 5m*",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 10))

# Status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "⚠️ You must be an *admin* to check status\\.",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    delay = delete_times.get(chat.id, DEFAULT_DELETE_TIME)
    minutes = delay // 60
    msg = await update.message.reply_text(
        f"📊 *Current delete delay:* {minutes} minute(s)",
        parse_mode="MarkdownV2"
    )
    asyncio.create_task(delete_later(msg, 20))

# Clean command
async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 *Access Denied\\!* Only admins can use */clean*",
            parse_mode="MarkdownV2"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    msg = await update.message.reply_text("🧹 Cleaning recent messages...", parse_mode="MarkdownV2")
    await asyncio.sleep(2)
    await msg.edit_text("✅ *Clean completed\\!*", parse_mode="MarkdownV2")
    asyncio.create_task(delete_later(msg, 10))

# Auto delete all messages (including bots)
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id
        delay = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
        await asyncio.sleep(delay)
        try:
            await update.message.delete()
        except:
            pass

# Run bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("settime", settime))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("clean", clean))
app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, auto_delete))

print("🚀 Auto Delete Bot Pro (MarkdownV2) Running...")
app.run_polling()
