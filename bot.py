import urllib.request
import urllib.parse
import json
import time
import threading

TOKEN = "9090336574:AAEwDUPF8kF3TYpOtdz8HGKRJtmsQuUHXXc"
ADMIN_BOT_TOKEN = "9164215304:AAGmIWz-YgGqVMZ6GCmxRjALJ4B0Dwq2Hw4"
ADMIN_ID = 8968860182

URL = "https://api.telegram.org/bot" + TOKEN
ADMIN_URL = "https://api.telegram.org/bot" + ADMIN_BOT_TOKEN

user_step = {}
user_data = {}
user_offer = {}

OFFERS = {
    "1": "20 Inwi = 16 DH",
    "2": "30 Inwi = 26 DH",
    "3": "50 Inwi = 46 DH",
    "4": "100 Inwi = 90 DH"
}

def send(url, chat_id, text):
    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(url + "/sendMessage", data, timeout=10)
    except Exception as e:
        print("send error:", e)

def get_updates(url, offset):
    req = urllib.request.urlopen(url + "/getUpdates?offset=" + str(offset) + "&timeout=20", timeout=30)
    return json.loads(req.read().decode())

def customer_bot():
    offset = 0
    print("Bot dyal client khdam...")
    while True:
        try:
            r = get_updates(URL, offset)
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "").strip()
                if not text:
                    continue
                if text == "/start":
                    send(URL, chat_id, "👋 مرحبا بيك فـ Speed Charge ⚡\n\n🎰 هاد البوت كيشحن منصة 1xBet فقط\n📱 و بتعبئة Inwi فقط\n\n👇 ختار العرض:\n\n1️⃣ - 20 Inwi = 16 DH\n2️⃣ - 30 Inwi = 26 DH\n3️⃣ - 50 Inwi = 46 DH\n4️⃣ - 100 Inwi = 90 DH\n\nصيفط رقم العرض: 1 ولا 2 ولا 3 ولا 4")
                    user_step[chat_id] = "offer"
                elif user_step.get(chat_id) == "offer":
                    if text in OFFERS:
                        user_offer[chat_id] = OFFERS[text]
                        send(URL, chat_id, "✅ ختاريتي: " + OFFERS[text] + "\n\n🆔 دابا صيفط ليا ID ديالك ديال 1xBet")
                        user_step[chat_id] = "id"
                    else:
                        send(URL, chat_id, "❌ صيفط غير رقم العرض: 1 ولا 2 ولا 3 ولا 4")
                elif user_step.get(chat_id) == "id":
                    user_data[chat_id] = text
                    offer = user_offer.get(chat_id, "")
                    send(URL, chat_id, "✅ ID ديالك: " + text + "\n\n💳 دابا صيفط كود تعبئة Inwi:\n" + offer)
                    user_step[chat_id] = "code"
                elif user_step.get(chat_id) == "code":
                    offer = user_offer.get(chat_id, "")
                    id_1x = user_data.get(chat_id, "")
                    send(ADMIN_URL, ADMIN_ID, "🔥 طلب جديد\n\n🎁 العرض: " + offer + "\n🆔 ID: " + id_1x + "\n💳 الكود: " + text + "\n👤 كود الكليان: " + str(chat_id) + "\n\nباش تأكدو صيفط:\n/done " + str(chat_id))
                    send(URL, chat_id, "✅ وصل الطلب ديالك\n🎁 العرض: " + offer + "\n⏳ تسنا شوية غادي نتأكد و نشحن ليك")
                    user_step[chat_id] = "done"
        except Exception as e:
            print("Error client:", e)
            time.sleep(2)

def admin_bot():
    offset = 0
    print("Bot dyal admin khdam...")
    while True:
        try:
            r = get_updates(ADMIN_URL, offset)
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "").strip()
                if chat_id != ADMIN_ID:
                    continue
                if text.startswith("/done"):
                    parts = text.split()
                    if len(parts) == 2:
                        client_id = parts[1]
                        send(URL, client_id, "✅ تم شحن حسابك بنجاح 🎉\nشكرا على ثقتك فـ Speed Charge ⚡")
                        send(ADMIN_URL, ADMIN_ID, "صافي دازت ليه ✅")
                    else:
                        send(ADMIN_URL, ADMIN_ID, "صيفط هكا: /done + كود الكليان")
        except Exception as e:
            print("Error admin:", e)
            time.sleep(2)

t1 = threading.Thread(target=customer_bot, daemon=True)
t2 = threading.Thread(target=admin_bot, daemon=True)
t1.start()
t2.start()
print("2 bots khdamin...")
while True:
    time.sleep(10)
