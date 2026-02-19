import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# التوكن الخاص بك من BotFather
TOKEN = '8499600478:AAGW2Pz1_AQsXK3GT5_fmg3sr0oRLOlbMOA'

# قائمة المستخدمين (تخزين مؤقت)
users = set()

# وظيفة الترحيب عند الضغط على /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_chat.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="🌙 تم تفعيل المنبه الرمضاني بنجاح يا دكتور!\nستصلك الأذكار والمهام يومياً في مواعيدها."
    )

# وظيفة إرسال أذكار الصباح كاملة
async def send_morning(context):
    msg = "☀️ **أذكار الصباح كاملة**\n\nآية الكرسي: (اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...)\nسورة الإخلاص (3 مرات)\nسورة الفلق (3 مرات)\nسورة الناس (3 مرات)\nأصبحنا وأصبح الملك لله والحمد لله..."
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode='Markdown')
        except: continue

# وظيفة إرسال أذكار المساء كاملة
async def send_evening(context):
    msg = "🌙 **أذكار المساء كاملة**\n\nآية الكرسي...\nأمسينا وأمسى الملك لله والحمد لله...\nاللهم أنت ربي لا إله إلا أنت..."
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode='Markdown')
        except: continue

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # الجدولة الزمنية (بتوقيت السيرفر)
    scheduler = BackgroundScheduler()
    # تذكير الصباح (7:00 صباحاً)
    scheduler.add_job(lambda: app.job_queue.run_once(send_morning, 0), 'cron', hour=7, minute=0)
    # تذكير المساء (5:00 مساءً)
    scheduler.add_job(lambda: app.job_queue.run_once(send_evening, 0), 'cron', hour=17, minute=0)
    scheduler.start()

    app.add_handler(CommandHandler('start', start))
    
    # Render يحتاج لمنفذ (Port) ليعرف أن التطبيق يعمل
    port = int(os.environ.get("PORT", 5000))
    app.run_polling()
