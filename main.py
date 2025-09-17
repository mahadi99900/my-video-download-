import logging
‎import os
‎import asyncio
‎from telegram import Update
‎from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
‎import yt_dlp
‎
‎# লগিং সেটআপ করা হচ্ছে, যা ডিবাগিং এ সাহায্য করবে
‎logging.basicConfig(
‎    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
‎    level=logging.INFO
‎)
‎logging.getLogger("httpx").setLevel(logging.WARNING) # httpx এর অপ্রয়োজনীয় লগ বন্ধ করা হলো
‎logger = logging.getLogger(__name__)
‎
‎# আপনার দেওয়া টেলিগ্রাম বটের টোকেন
‎BOT_TOKEN = "8257221379:AAGpRJXMHkRNLsson3ETnaZPwZZJfCK5I5E"
‎
‎# /start কমান্ডের ফাংশন
‎async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
‎    user = update.effective_user
‎    await update.message.reply_html(
‎        f"👋 হাই {user.mention_html()}!\n\nআমি একটি শক্তিশালী ভিডিও ডাউনলোডার বট। আমাকে যেকোনো সাপোর্টেড সাইটের ভিডিও লিংক পাঠান, আমি ডাউনলোড করে পাঠিয়ে দেব।",
‎    )
‎
‎# ভিডিও ডাউনলোড এবং পাঠানোর মূল ফাংশন
‎async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
‎    message = update.message
‎    url = message.text.strip()
‎
‎    # === এখানেই পরিবর্তন করা হয়েছে ===
‎    # ব্যবহারকারীকে জানানো হচ্ছে যে ডাউনলোড শুরু হয়েছে এবং তার মেসেজের রিপ্লাই দেওয়া হচ্ছে
‎    reply_msg = await message.reply_text(
‎        "📥 ডাউনলোড শুরু করছি, অনুগ্রহ করে অপেক্ষা করুন...",
‎        reply_to_message_id=message.message_id  # quote=True এর পরিবর্তে এটি ব্যবহার করা হয়েছে
‎    )
‎
‎    filename = None
‎    try:
‎        # yt-dlp এর জন্য অপশন সেট করা হচ্ছে
‎        ydl_opts = {
‎            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
‎            'outtmpl': '%(title)s.%(ext)s',
‎            'noplaylist': True,
‎            'logger': logger,
‎        }
‎
‎        # yt-dlp ব্যবহার করে ভিডিও ডাউনলোড
‎        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
‎            info_dict = ydl.extract_info(url, download=True)
‎            filename = ydl.prepare_filename(info_dict)
‎
‎        # ব্যবহারকারীকে আপলোডের জন্য প্রস্তুত হতে বলা হচ্ছে
‎        await reply_msg.edit_text(f"✅ ডাউনলোড সম্পন্ন!\n\n📤 এখন আপনাকে ভিডিওটি পাঠাচ্ছি...")
‎
‎        # টেলিগ্রামে ভিডিও পাঠানো হচ্ছে
‎        await context.bot.send_video(
‎            chat_id=update.effective_chat.id,
‎            video=open(filename, 'rb'),
‎            caption=info_dict.get('title', 'Downloaded Video'),
‎            reply_to_message_id=message.message_id,
‎            supports_streaming=True
‎        )
‎        
‎        # সফলভাবে পাঠানোর পর আগের মেসেজগুলো ডিলিট করা
‎        await reply_msg.delete()
‎
‎    except Exception as e:
‎        logger.error(f"Error downloading {url}: {e}")
‎        await reply_msg.edit_text(f"❌ দুঃখিত, এই ভিডিওটি ডাউনলোড করতে একটি সমস্যা হয়েছে।\n\nত্রুটি: {str(e)}")
‎
‎    finally:
‎        # ডাউনলোড করা ফাইলটি ফোন থেকে মুছে ফেলা হচ্ছে
‎        if filename and os.path.exists(filename):
‎            os.remove(filename)
‎            logger.info(f"Deleted local file: {filename}")
‎
‎
‎def main() -> None:
‎    """বটটি শুরু এবং চালানোর ফাংশন"""
‎    application = Application.builder().token(BOT_TOKEN).build()
‎
‎    application.add_handler(CommandHandler("start", start))
‎    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
‎
‎    logger.info("Bot has started successfully!")
‎    application.run_polling(allowed_updates=Update.ALL_TYPES)
‎
‎
‎if __name__ == '__main__':
‎    main()
‎