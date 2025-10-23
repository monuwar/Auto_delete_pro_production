import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_DELETE_TIME = 30  # fallback = 30 seconds

# ✅ Dictionary for user/group specific delete time
delete_times = {}

# 🟢 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    delete_time = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
    minutes = delete_time // 60

    msg = await update.message.reply_text(
        f"🤖 <b>Auto Delete Bot is Active!</b>\n\n"
        f"⏳ Messages will be deleted automatically after <b>{minutes}</b> minute(s).\n"
        f"🧑‍💼 Only <b>group admins</b> can change settings.\n"
        f"💡 Use <b>/help</b> for all commands.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 20))

# 📘 HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "📚 <b>Auto Delete Bot — Command List</b>\n\n"
        "⏱️ <b>/settime &lt;minutes&gt;</b> — Set delete delay\n"
        "📊 <b>/status</b> — Show current delete delay\n"
        "🧹 <b>/clean</b> — Delete last messages\n"
        "ℹ️ <b>/help</b> — Show this help menu\n\n"
        "⚠️ Only admins can manage bot settings.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 30))

# ⏱️ SETTIME (minutes)
async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    chat_id = chat.id
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 <b>Access Denied!</b>\n"
            "Only <b>group admins</b> can use <b>/settime</b>.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 15))
        return

    if not context.args:
        msg = await update.message.reply_text(
            "⚙️ Usage: <b>/settime 10m</b>\n"
            "⏳ Example: <b>/settime 5m</b> → Deletes messages every 5 minutes.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 20))
        return

    try:
        input_time = context.args[0].lower()
        if input_time.endswith("m"):
            minutes = int(input_time[:-1])
            seconds = minutes * 60
        else:
            seconds = int(input_time)
            minutes = seconds // 60

        delete_times[chat_id] = seconds
        msg = await update.message.reply_text(
            f"✅ Auto delete time set to <b>{minutes}</b> minute(s) for this chat.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
    except ValueError:
        msg = await update.message.reply_text(
            "⚠️ Invalid format! Please use <b>/settime 5m</b>.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))

# 📊 STATUS
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "⚠️ You must be a <b>group admin</b> to check bot status.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 15))
        return

    delete_time = delete_times.get(chat.id, DEFAULT_DELETE_TIME)
    minutes = delete_time // 60
    msg = await update.message.reply_text(
        f"📊 Current delete time is <b>{minutes}</b> minute(s).",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 20))

# 🧹 CLEAN COMMAND
async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 <b>Access Denied!</b>\n"
            "Only <b>group admins</b> can use <b>/clean</b>.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    msg = await update.message.reply_text("🧹 Cleaning recent messages...", parse_mode="HTML")
    await asyncio.sleep(2)
    try:
        async for message in context.bot.get_chat(chat.id).get_messages():
            try:
                await context.bot.delete_message(chat.id, message.message_id)
            except:
                continue
        await msg.edit_text("✅ All messages have been cleaned!", parse_mode="HTML")
        asyncio.create_task(delete_later(msg, 10))
    except Exception as e:
        await msg.edit_text(f"❌ Clean failed: {str(e)}", parse_mode="HTML")

# 💣 AUTO DELETE FOR ALL MESSAGES
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id
        delay = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
        await asyncio.sleep(delay)
        try:
            await update.message.delete()
        except:
            pass

# 🗑️ DELETE OWN MESSAGE SAFELY
async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# 🚀 RUN BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("settime", settime))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("clean", clean))
app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, auto_delete))

print("🚀 Auto Delete Pro Bot — Running")
app.run_polling()
