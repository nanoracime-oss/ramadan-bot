import os
import datetime
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

TOKEN = '8499600478:AAG6vtT-pLgAd3LFXvYeMulWyhusgw-JC28'
WEBSITE_URL = 'https://ramadan-dz1.netlify.app/'
ADMIN_ID = 7408327565 

# --- إعدادات قاعدة البيانات السحابية (MongoDB) ---
# ⚠️ ضع كلمة المرور الخاصة بك بدلاً من الكلمة العربية أدناه:
MONGO_URI = 'mongodb+srv://Yacinebranis:ramadan2026@cluster0.9bezeak.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client['ramadan_bot']
users_collection = db['users']

# --- خادم الويب المصغر ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Perfectly")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- القائمة السفلية ---
def get_main_menu():
    keyboard = [
        [KeyboardButton("☀️ أذكار الصباح"), KeyboardButton("🌙 أذكار المساء")],
        [KeyboardButton("💊 كبسولة طبية"), KeyboardButton("⏳ متى الإفطار؟")],
        [KeyboardButton("💰 الصدقات"), KeyboardButton("🌐 منصة رمضان")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="اختر من القائمة...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    
    # حفظ المستخدم في قاعدة البيانات السحابية فوراً
    users_collection.update_one({'user_id': user_id}, {'$set': {'user_id': user_id}}, upsert=True)
        
    text = "🌙 أهلاً بك في المساعد الرمضاني\n\nتم تفعيل التنبيهات، ويمكنك استخدام القائمة السفلية للوصول السريع للأذكار، النصائح الطبية، والمنصة:"
    await update.message.reply_text(text, reply_markup=get_main_menu())

# --- التفاعل مع الأزرار ---
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "☀️ أذكار الصباح":
        await update.message.reply_text(f"☀️ لقراءة أذكار الصباح كاملة بالحركات:\n{WEBSITE_URL}")
    elif text == "🌙 أذكار المساء":
        await update.message.reply_text(f"🌙 لقراءة أذكار المساء كاملة بالحركات:\n{WEBSITE_URL}")
    elif text == "💰 الصدقات":
        await update.message.reply_text(f"💰 (صنائع المعروف تقي مصارع السوء)\nللتصدق الآمن والمضمون عبر منصتنا:\n{WEBSITE_URL}")
    elif text == "🌐 منصة رمضان":
        await update.message.reply_text(f"🌐 تتبع إنجازك اليومي، خطة الختم، والأذكار من هنا:\n{WEBSITE_URL}")
        
    elif text == "💊 كبسولة طبية":
        tip = (
            "👨‍⚕️ *الكبسولة الطبية الرمضانية:*\n\n"
            "لتجنب الصداع والجفاف أثناء الصيام، احرص على شرب من 8 إلى 10 أكواب من الماء مقسمة بين وجبتي الإفطار والسحور، "
            "وقلل من المشروبات الغنية بالكافيين كالقهوة والشاي لأنها تزيد من إدرار البول والعطش."
        )
        await update.message.reply_text(tip, parse_mode='Markdown')
        
    elif text == "⏳ متى الإفطار؟":
        tz_algeria = datetime.timezone(datetime.timedelta(hours=1))
        now = datetime.datetime.now(tz_algeria)
        iftar_time = now.replace(hour=19, minute=10, second=0, microsecond=0)
        
        if now > iftar_time:
            await update.message.reply_text("🍽️ أفطرنا والحمد لله! تقبل الله صيامكم وقيامكم.")
        else:
            diff = iftar_time - now
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await update.message.reply_text(f"⏳ باقي على أذان المغرب تقريباً:\n*{hours} ساعات و {minutes} دقيقة* 🌙", parse_mode='Markdown')

# --- ميزة الإرسال الجماعي ---
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return 

    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرسالة بعد الأمر، مثال:\n/send_all السلام عليكم.")
        return

    message = " ".join(context.args)
    count = 0
    
    # جلب المشتركين من قاعدة البيانات السحابية
    users = users_collection.find()
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=f"📢 تذكير رمضاني:\n\n{message}")
            count += 1
        except: pass
    
    await update.message.reply_text(f"✅ تم إرسال رسالتك بنجاح إلى {count} مشترك.")

# --- التنبيهات المجدولة ---
async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    users = users_collection.find()
    for u in users:
        try: await context.bot.send_message(chat_id=u['user_id'], text=f"☀️ حان الآن وقت أذكار الصباح.\nابدأ يومك بذكر الله.\n\nاقرأها كاملة من هنا: {WEBSITE_URL}")
        except: pass

async def evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    users = users_collection.find()
    for u in users:
        try: await context.bot.send_message(chat_id=u['user_id'], text=f"🌙 حان الآن وقت أذكار المساء.\nختام اليوم بالذكر طمأنينة.\n\nاقرأها كاملة من هنا: {WEBSITE_URL}")
        except: pass

async def iftar_dua_reminder(context: ContextTypes.DEFAULT_TYPE):
    dua = "🤲 *دعاء ما قبل الإفطار:*\n\n(اللهم لك صمت، وعلى رزقك أفطرت، ذهب الظمأ وابتلت العروق، وثبت الأجر إن شاء الله).\nلا تنسونا من صالح دعائكم 🌙."
    users = users_collection.find()
    for u in users:
        try: await context.bot.send_message(chat_id=u['user_id'], text=dua, parse_mode='Markdown')
        except: pass

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    tz_algeria = datetime.timezone(datetime.timedelta(hours=1))
    
    app.job_queue.run_daily(morning_reminder, time=datetime.time(hour=7, minute=0, tzinfo=tz_algeria))
    app.job_queue.run_daily(evening_reminder, time=datetime.time(hour=17, minute=0, tzinfo=tz_algeria))
    app.job_queue.run_daily(iftar_dua_reminder, time=datetime.time(hour=18, minute=45, tzinfo=tz_algeria))
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send_all", send_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    app.run_polling() 
