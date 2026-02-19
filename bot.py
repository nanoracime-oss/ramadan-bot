import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# التوكن الخاص بك
TOKEN = '8499600478:AAGW2Pz1_AQsXK3GT5_fmg3sr0oRLOlbMOA'

# كود صغير لإيهام Render أن هناك موقع يعمل (Web Server)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), HealthCheckHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🌙 تم تفعيل البوت بنجاح يا دكتور ياسين!")

if __name__ == '__main__':
    # تشغيل خادم الـ Web في خلفية السيرفر لإرضاء Render
    threading.Thread(target=run_health_check, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    
    print("Bot is starting...")
    app.run_polling()
