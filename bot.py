import os
from telegram.ext import Updater, CommandHandler
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = '8499600478:AAGW2Pz1_AQsXK3GT5_fmg3sr0oRLOlbMOA'
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Alive")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def start(update, context):
    update.message.reply_text("🌙 تم تفعيل البوت بنجاح يا دكتور ياسين!")

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()
