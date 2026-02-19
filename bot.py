import os
import json
import datetime
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الجديد الخاص بك
TOKEN = '8499600478:AAG6vtT-pLgAd3LFXvYeMulWyhusgw-JC28'
WEBSITE_URL = 'https://ramadan-dz1.netlify.app/'
ADMIN_ID = 7408327565 # مخفي في الخلفية ليعمل الإرسال الجماعي لك فقط
USERS_FILE = 'users.json'

# --- 1. نظام حفظ المشتركين ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(list(users), f)

users = load_users()

# --- خادم الويب المصغر لإبقاء Render يعمل ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Perfectly")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- 2. القائمة السفلية التفاعلية ---
def get_main_menu():
    keyboard = [
        [KeyboardButton("☀️ أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
        [KeyboardButton("💰 الصدقات"), KeyboardButton("🌐 منصة رمضان")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="اختر من القائمة...")

# رسالة الترحيب (تم تعديلها لتكون عامة)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in users:
        users.add(user_id)
        save_users(users)
        
    text = "🌙 أهلاً بك في المساعد الرمضاني\n\nتم تفعيل التنبيهات، ويمكنك استخدام القائمة السفلية للوصول السريع للأذكار والمنصة:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

# تفاعل البوت مع أزرار القائمة
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "☀️ أذكار الصباح":
        await update.message.reply_text(f"☀️ لقراءة أذكار الصباح كاملة بالحركات، تفضل بزيارة المنصة:\n{WEBSITE_URL}")
    elif text == "🌙 أذكار المساء":
        await update.message.reply_text(f"🌙 لقراءة أذكار المساء كاملة بالحركات، تفضل بزيارة المنصة:\n{WEBSITE_URL}")
    elif text == "💰 الصدقات":
        await update.message.reply_text(f"💰 (صنائع المعروف تقي مصارع السوء)\nللتصدق الآمن والمضمون عبر منصتنا:\n{WEBSITE_URL}")
    elif text == "🌐 منصة رمضان":
        await update.message.reply_text(f"🌐 تتبع إنجازك اليومي، خطة الختم، والأذكار من هنا:\n{WEBSITE_URL}")

# --- 3. ميزة الإذاعة (تم إخفاء الاسم) ---
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return # يتجاهل الأمر بصمت إذا لم تكن أنت

    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرسالة بعد الأمر، مثال:\n/send_all السلام عليكم، لا تنسوا قراءة القرآن اليوم.")
        return

    message = " ".join(context.args)
    count = 0
    for u in users:
        try:
            # تم تحويلها إلى تذكير عام
            await context.bot.send_message(chat_id=u, text=f"📢 تذكير رمضاني:\n\n{message}")
            count += 1
        except: pass
    
    await update.message.reply_text(f"✅ تم إرسال رسالتك بنجاح إلى {count} مشترك.")

# --- 4. نظام التذكير التلقائي ---
async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    msg = f"☀️ حان الآن وقت أذكار الصباح.\nابدأ يومك بذكر الله لعلها تكون ساعة استجابة.\n\nاقرأها كاملة من هنا: {WEBSITE_URL}"
    for u in users:
        try: await context.bot.send_message(chat_id=u, text=msg)
        except: pass

async def evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    msg = f"🌙 حان الآن وقت أذكار المساء.\nختام اليوم بالذكر طمأنينة للقلب.\n\nاقرأها كاملة من هنا: {WEBSITE_URL}"
    for u in users:
        try: await context.bot.send_message(chat_id=u, text=msg)
        except: pass

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    tz_algeria = datetime.timezone(datetime.timedelta(hours=1))
    
    app.job_queue.run_daily(morning_reminder, time=datetime.time(hour=7, minute=0, tzinfo=tz_algeria))
    app.job_queue.run_daily(evening_reminder, time=datetime.time(hour=17, minute=0, tzinfo=tz_algeria))
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send_all", send_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    app.run_polling()
