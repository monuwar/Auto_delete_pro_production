# -*- coding: utf-8 -*-
asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_DELETE_TIME = 30
delete_times = {}

async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    delete_time = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
    minutes = delete_time // 60
    msg = await update.message.reply_text(
        f"🤖 <b>Auto Delete Bot is Active!</b>\n\n"
        f"⏳ Messages will be deleted automatically after <b>{minutes}</b> minute(s).\n"
        f"🧑‍💼 Only <b>group admins</b> can change settings.\n"
        f"💡 Use <code>/help</code> for all commands.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 20))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "📘 <b>Auto Delete Bot — Command List</b>\n\n"
        "⏱️ <code>/settime &lt;minutes&gt;</code> — Set delete delay\n"
        "📊 <code>/status</code> — Show current delete delay\n"
        "🧹 <code>/clean</code> — Delete last messages\n"
        "ℹ️ <code>/help</code> — Show this help menu\n\n"
        "⚠️ Only admins can manage bot settings.",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 25))

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 <b>Access Denied!</b> Only admins can use <code>/settime</code>.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    if not context.args:
        msg = await update.message.reply_text(
            "⚙️ Usage: <code>/settime 10m</code><br>Example: <code>/settime 5m</code> — deletes every 5 minutes.",
            parse_mode="HTML"
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
            f"✅ Auto delete time set to <b>{minutes}</b> minute(s) for this chat.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
    except ValueError:
        msg = await update.message.reply_text(
            "⚠️ Invalid format! Use <code>/settime 5m</code>",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "⚠️ You must be an <b>admin</b> to check status.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    delay = delete_times.get(chat.id, DEFAULT_DELETE_TIME)
    minutes = delay // 60
    msg = await update.message.reply_text(
        f"📊 <b>Current delete delay:</b> {minutes} minute(s)",
        parse_mode="HTML"
    )
    asyncio.create_task(delete_later(msg, 20))

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)

    if member.status not in ("administrator", "creator"):
        msg = await update.message.reply_text(
            "🚫 <b>Access Denied!</b> Only admins can use <code>/clean</code>.",
            parse_mode="HTML"
        )
        asyncio.create_task(delete_later(msg, 10))
        return

    msg = await update.message.reply_text("🧹 Cleaning recent messages...", parse_mode="HTML")
    await asyncio.sleep(2)
    await msg.edit_text("✅ <b>Clean completed!</b>", parse_mode="HTML")
    asyncio.create_task(delete_later(msg, 10))

async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id
        delay = delete_times.get(chat_id, DEFAULT_DELETE_TIME)
        await asyncio.sleep(delay)
        try:
            await update.message.delete()
        except:
            pass

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("settime", settime))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("clean", clean))
app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, auto_delete))

print("🚀 Auto Delete Bot Pro (HTML mode) Running...")
app.run_polling()
