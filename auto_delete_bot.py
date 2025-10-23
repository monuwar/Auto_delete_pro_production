# -*- coding: utf-8 -*-
# 🤖 Auto Delete Bot (Base Version - English + Emoji + Admin Protected)
# Author: Monuwar Edition

import os
import asyncio
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# === Load BOT TOKEN ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("🚨 BOT_TOKEN missing! Add it in Railway → Variables")

# === Default Settings ===
DELETE_DELAY = 5  # seconds before message deletion (changeable by /setdelay)
BULK_DELETE_COUNT = 100  # how many messages /clean deletes

# === Helper: Check if user is admin ===
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

# === Commands ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Auto Delete Bot is Active!*\n\n"
        f"🕒 Messages will be deleted automatically after *{DELETE_DELAY} seconds*.\n"
        "👮‍♂️ Only group admins can change settings.\n"
        "💡 Use /help for all commands.",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *Auto Delete Bot — Command List*\n\n"
        "🕒 `/setdelay <seconds>` – Set delete delay\n"
        "📊 `/status` – Show current delete delay\n"
        "🧹 `/clean` – Delete last messages\n"
        "ℹ️ `/help` – Show this help menu\n\n"
        "⚠️ *Only admins can manage bot settings.*",
        parse_mode="Markdown"
    )

async def setdelay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DELETE_DELAY
    if not await is_admin(update, context):
        await update.message.reply_text(
            "⚠️ Sorry! You don’t have permission to use this command.\n"
            "👮‍♂️ Only *group admins* can manage bot settings.",
            parse_mode="Markdown"
        )
        return

    try:
        if len(context.args) == 0:
            await update.message.reply_text(f"⏱ Current delete delay: *{DELETE_DELAY} seconds*", parse_mode="Markdown")
            return

        delay = int(context.args[0])
        if delay < 1 or delay > 3600:
            await update.message.reply_text("⚠️ Delay must be between *1–3600 seconds*.", parse_mode="Markdown")
            return

        DELETE_DELAY = delay
        await update.message.reply_text(f"✅ Delete delay set to *{DELETE_DELAY} seconds*.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text(
            "⚠️ You must be a *group admin* to check bot status.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📊 *Bot Status:*\n"
        f"🕒 Current delete delay: *{DELETE_DELAY} seconds*\n"
        f"🧹 Bulk clean deletes: *{BULK_DELETE_COUNT} messages*",
        parse_mode="Markdown"
    )

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text(
            "⚠️ Sorry! This command is for *admins only.*",
            parse_mode="Markdown"
        )
        return

    chat = update.effective_chat
    await update.message.reply_text("🧹 Cleaning recent messages...")

    try:
        # Get message IDs
        async for msg in context.bot.get_chat_history(chat.id, limit=BULK_DELETE_COUNT):
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
            except:
                pass
        await update.message.reply_text("✅ Chat cleaned successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Clean failed: {e}")

# === Auto Delete Logic ===
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        chat = update.effective_chat

        if chat.type not in ("group", "supergroup"):
            return  # Ignore private chats

        # Skip pinned / service messages
        if msg.pinned_message or msg.new_chat_members or msg.left_chat_member:
            return

        await asyncio.sleep(DELETE_DELAY)
        await context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    except Exception as e:
        print(f"⚠️ Delete error: {e}")

# === Main Application ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("setdelay", setdelay))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clean", clean))

    # Message auto delete handler
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, auto_delete))

    print("🚀 Auto Delete Bot (Base Version) is Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
