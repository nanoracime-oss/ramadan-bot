import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# التوكن الخاص بك
TOKEN = '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' 

# نظام الحفاظ على استيقاظ السيرفر
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 تم تفعيل بوت رفيقي الرمضاني بنجاح يا دكتور ياسين!")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    # هنا تضع نص التذكير الذي تريده
    await context.bot.send_message(chat_id="ID_حسابك", text="☀️ حان وقت أذكار الصباح")

if __name__ == '__main__':
    # تشغيل خادم الويب في الخلفية
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # بناء البوت باستخدام النظام الجديد
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is Live...")
    app.run_polling()
