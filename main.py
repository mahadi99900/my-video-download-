import logging
import os
import sys
import asyncio
import time
import getpass  # টোকেন ইনপুট নেওয়ার জন্য নতুন লাইব্রেরী
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
import yt_dlp

# লগিং সেটআপ করা হচ্ছে
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# /start কমান্ডের ফাংশন
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"👋 হাই {user.mention_html()}!\n\n"
        "আমি একটি শক্তিশালী ভিডিও ডাউনলোডার বট। আমাকে যেকোনো সাপোর্টেড সাইটের ভিডিও লিংক পাঠান, আমি ডাউনলোড করে পাঠিয়ে দেব।"
    )

# ভিডিও ডাউনলোড এবং পাঠানোর মূল ফাংশন
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    url = message.text.strip()
    
    reply_msg = await message.reply_text(
        "⏳ লিঙ্ক প্রসেস করছি...",
        reply_to_message_id=message.message_id
    )

    filename = None
    last_update_time = 0
    
    try:
        # ডাউনলোড პროగ్ర্রেস দেখানোর জন্য হুক ফাংশন
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
                            f"📥 ডাউনলোড চলছে...\n\n"
                            f" avance: {percentage}\n"
                            f" গতি: {speed}\n"
                            f" বাকি সময়: {eta}"
                        )
                        last_update_time = current_time
                    except BadRequest:
                        pass
            elif d['status'] == 'finished':
                 await reply_msg.edit_text("✅ ডাউনলোড সম্পন্ন!\n\n📤 এখন আপনাকে ভিডিওটি পাঠাচ্ছি...")

        # yt-dlp এর জন্য অপশন
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'logger': logger,
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info_dict)

        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(filename, 'rb'),
            caption=info_dict.get('title', 'Downloaded Video'),
            reply_to_message_id=message.message_id,
            supports_streaming=True
        )
        
        await reply_msg.delete()

    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        error_message = str(e)
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        await reply_msg.edit_text(f"❌ দুঃখিত, একটি সমস্যা হয়েছে।\n\nত্রুটি: {error_message}")

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Deleted local file: {filename}")


def main() -> None:
    """বটটি শুরু এবং চালানোর ফাংশন"""
    
    # --- এখানেই মূল পরিবর্তন করা হয়েছে ---
    # ব্যবহারকারীর কাছ থেকে টোকেন ইনপুট নেওয়া হচ্ছে
    try:
        bot_token = getpass.getpass(" অনুগ্রহ করে আপনার টেলিগ্রাম বট টোকেন পেস্ট করে Enter চাপুন: ")
        if not bot_token:
            logger.error("টোকেন দেওয়া হয়নি! প্রোগ্রাম বন্ধ করা হচ্ছে।")
            sys.exit(1) # টোকেন না দিলে প্রোগ্রাম বন্ধ হয়ে যাবে
    except (KeyboardInterrupt, EOFError):
        logger.info("\nপ্রোগ্রাম বন্ধ করা হয়েছে।")
        sys.exit(0)
    
    # ইনপুট করা টোকেন দিয়ে বট চালু করা হচ্ছে
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logger.info("বট সফলভাবে চালু হয়েছে!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
