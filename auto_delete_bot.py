import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# 🔹 Default delete time (in seconds)
DEFAULT_DELETE_TIME = 30

# 🟢 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "🤖 <b>Auto Delete Bot is Active!</b>\n\n"
        "⏳ Messages will be deleted automatically after <b>30 seconds</b>.\n"
        "🧑‍💼 Only <b>group admins</b> can change settings.\n"
        "💡 Use <b>/help</b> for all commands.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_own(msg, 10))

# 📘 HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "📚 <b>Available Commands:</b>\n\n"
        "✅ <b>/start</b> – Activate the bot\n"
        "🧹 <b>/clean</b> – Delete all recent messages\n"
        "⏱️ <b>/settime 10m</b> – Set auto delete time (in minutes)\n"
        "ℹ️ <b>/help</b> – Show this help message\n\n"
        "⚠️ Only <b>admins</b> can change delete time.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_own(msg, 20))

# 🧹 CLEAN COMMAND (deletes all messages)
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
        asyncio.create_task(delete_own(msg, 10))
        return

    info_msg = await update.message.reply_text("🧹 Cleaning all recent messages...", parse_mode="HTML")

    try:
        async for message in context.bot.get_chat(chat.id).get_messages():
            try:
                await context.bot.delete_message(chat.id, message.message_id)
            except:
                continue
        await info_msg.edit_text("✅ All messages have been cleaned!", parse_mode="HTML")
        asyncio.create_task(delete_own(info_msg, 10))
    except Exception as e:
        await info_msg.edit_text(f"❌ Clean failed: {str(e)}", parse_mode="HTML")

# ⏱️ SETTIME (minutes supported)
async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 <b>You must be a group admin</b> to change settings.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_own(msg, 10))
        return

    if not context.args:
        msg = await update.message.reply_text(
            "⚙️ Usage: <b>/settime 10m</b>\n"
            "⏳ Example: <b>/settime 5m</b> → Deletes messages every 5 minutes.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_own(msg, 15))
        return

    try:
        input_time = context.args[0].lower()
        if input_time.endswith("m"):
            minutes = int(input_time[:-1])
            seconds = minutes * 60
        else:
            seconds = int(input_time)
            minutes = seconds // 60

        context.chat_data["delete_time"] = seconds
        msg = await update.message.reply_text(
            f"⏱️ Auto delete time set to <b>{minutes}</b> minute(s).",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_own(msg, 10))
    except ValueError:
        msg = await update.message.reply_text(
            "⚠️ Invalid format! Please use <b>/settime 5m</b> (minutes).",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_own(msg, 10))

# 💣 AUTO DELETE EVERY MESSAGE (user + bots + own)
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        delete_time = context.chat_data.get("delete_time", DEFAULT_DELETE_TIME)
        await asyncio.sleep(delete_time)
        try:
            await update.message.delete()
        except:
            pass

# 🗑️ DELETE OWN MESSAGE (safe)
async def delete_own(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# 🚀 APP SETUP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("clean", clean))
app.add_handler(CommandHandler("settime", settime))

app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, auto_delete))

print("🚀 Auto Delete Pro Bot is Running...")
app.run_polling()
