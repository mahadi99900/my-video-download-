import logging
import os
import sys
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest, InvalidToken
import yt_dlp

# --- Setup basic logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n"
        "I am a powerful video downloader bot. Send me a link from any supported site, and I will download and send it to you."
    )

# --- Core Functionality ---
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles video download requests."""
    message = update.message
    url = message.text.strip()
    
    reply_msg = await message.reply_text(
        "⏳ Processing link...",
        reply_to_message_id=message.message_id
    )

    filename = None
    last_update_time = 0
    
    try:
        # --- Progress hook for yt-dlp to show download status ---
        async def progress_hook(d):
            nonlocal last_update_time
            if d['status'] == 'downloading':
                current_time = time.time()
                if current_time - last_update_time > 2:
                    percentage = d['_percent_str']
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    
                    try:
                        await reply_msg.edit_text(
                            f"📥 Downloading...\n\n"
                            f"Progress: {percentage}\n"
                            f"Speed: {speed}\n"
                            f"ETA: {eta}"
                        )
                        last_update_time = current_time
                    except BadRequest:
                        pass
            elif d['status'] == 'finished':
                 await reply_msg.edit_text("✅ Download complete!\n\n📤 Now uploading to you...")

        # --- yt-dlp options ---
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'logger': logger,
            'progress_hooks': [progress_hook],
        }

        # --- Download process ---
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info_dict)

        # --- Upload video to Telegram ---
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(filename, 'rb'),
            caption=info_dict.get('title', 'Downloaded Video'),
            reply_to_message_id=message.message_id,
            supports_streaming=True
        )
        
        await reply_msg.delete()

    except Exception as e:
        logger.error(f"Error in download_video: {e}", exc_info=True)
        error_message = str(e)
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        await reply_msg.edit_text(f"❌ Sorry, an error occurred.\n\nError: {error_message}")

    finally:
        # --- Clean up the downloaded file ---
        if filename and os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Deleted local file: {filename}")


async def main() -> None:
    """Starts the bot using the modern async with context manager."""
    
    bot_token = input("Please paste your Telegram bot token and press Enter: ")
    if not bot_token:
        logger.error("Token was not provided! Exiting.")
        sys.exit(1)
    
    # Build the application
    application = Application.builder().token(bot_token).build()

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # The 'async with' block automatically handles application.initialize() on entry
    # and application.shutdown() on exit, which gracefully handles startup and cleanup.
    try:
        async with application:
            logger.info("Bot started successfully and is now polling...")
            await application.run_polling(allowed_updates=Update.ALL_TYPES)
    except InvalidToken:
        logger.error("❌ Invalid Bot Token! Please get a correct token from @BotFather and restart.")
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot shutdown initiated by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"An unexpected error occurred in main: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())