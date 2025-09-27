import logging
import os
import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
import yt_dlp

# লগিং সেটআপ করা হচ্ছে, যা ডিবাগিং এ সাহায্য করবে
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# -------------------- কনফিগারেশন --------------------
# আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
# ----------------------------------------------------

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
        # --- ডাউনলোড პროగ్ర্রেস দেখানোর জন্য হুক ফাংশন ---
        async def progress_hook(d):
            nonlocal last_update_time
            if d['status'] == 'downloading':
                # প্রতি ২ সেকেন্ডে একবার মেসেজ আপডেট হবে, যাতে টেলিগ্রামের লিমিট ক্রস না হয়
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
                    except BadRequest: # যদি মেসেজ একই থাকে তাহলে BadRequest এরর আসে
                        pass
            elif d['status'] == 'finished':
                 await reply_msg.edit_text("✅ ডাউনলোড সম্পন্ন!\n\n📤 এখন আপনাকে ভিডিওটি পাঠাচ্ছি...")


        # yt-dlp এর জন্য অপশন সেট করা হচ্ছে
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'logger': logger,
            'progress_hooks': [progress_hook], # პროగ్ర্রেস হুক যোগ করা হলো
        }

        # yt-dlp ব্যবহার করে ভিডিও ডাউনলোড
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info_dict)

        # টেলিগ্রামে ভিডিও পাঠানো হচ্ছে
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(filename, 'rb'),
            caption=info_dict.get('title', 'Downloaded Video'),
            reply_to_message_id=message.message_id,
            supports_streaming=True
        )
        
        # সফলভাবে পাঠানোর পর স্ট্যাটাস মেসেজটি ডিলিট করা
        await reply_msg.delete()

    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        error_message = str(e)
        # এরর মেসেজ ছোট করে দেখানো
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        await reply_msg.edit_text(f"❌ দুঃখিত, একটি সমস্যা হয়েছে।\n\nত্রুটি: {error_message}")

    finally:
        # ডাউনলোড করা ফাইলটি মুছে ফেলা হচ্ছে
        if filename and os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Deleted local file: {filename}")

def main() -> None:
    """বটটি শুরু এবং চালানোর ফাংশন"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    logger.info("Bot has started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
