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
        data = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": text}
        ).encode()
        urllib.request.urlopen(
            url + "/sendMessage", data, timeout=10
        )
    except Exception as e:
        print("send error:", e)

def get_updates(url, offset):
    req = urllib.request.urlopen(
        url + "/getUpdates?offset=" + str(offset)
        + "&timeout=20", timeout=30
    )
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
                    m = "مرحبا بيك فـ Speed Charge\n"
                    m += "كيشحن 1xBet فقط\n"
                    m += "و بتعبئة Inwi فقط\n"
                    m += "1 - 20 Inwi = 16 DH\n"
                    m += "2 - 30 Inwi = 26 DH\n"
                    m += "3 - 50 Inwi = 46 DH\n"
                    m += "4 - 100 Inwi = 90 DH\n"
                    m += "صيفط رقم العرض"
                    send(URL, chat_id, m)
                    user_step[chat_id] = "offer"
                elif user_step.get(chat_id) == "offer":
                    if text in OFFERS:
                        user_offer[chat_id] = OFFERS[text]
                        m = "ختاريتي: " + OFFERS[text] + "\n"
                        m += "دابا صيفط ID ديال 1xBet"
                        send(URL, chat_id, m)
                        user_step[chat_id] = "id"
                    else:
                        send(URL, chat_id, "صيفط غير 1 ولا 2 ولا 3 ولا 4")
                elif user_step.get(chat_id) == "id":
                    if not text.isdigit():
                        send(URL, chat_id, "ID غالط، صيفط غير الأرقام")
                        continue
                    if not (8 <= len(text) <= 10):
                        send(URL, chat_id, "ID غالط، خاصو 8 حتى 10 أرقام")
                        continue
                    user_data[chat_id] = text
                    offer = user_offer.get(chat_id, "")
                    m = "ID ديالك: " + text + "\n"
                    m += "دابا صيفط كود Inwi\n"
                    m += offer
                    send(URL, chat_id, m)
                    user_step[chat_id] = "code"
                elif user_step.get(chat_id) == "code":
                    if not text.isdigit():
                        send(URL, chat_id, "الكود غالط، صيفط غير الأرقام")
                        continue
                    if len(text) != 14:
                        send(URL, chat_id, "الكود غالط، خاصو 14 رقم")
                        continue
                    offer = user_offer.get(chat_id, "")
                    id_1x = user_data.get(chat_id, "")
                    m = "طلب جديد\n"
                    m += "العرض: " + offer + "\n"
                    m += "ID: " + id_1x + "\n"
                    m += "الكود: " + text + "\n"
                    m += "الكليان: " + str(chat_id) + "\n"
                    m += "/done " + str(chat_id) + "\n"
                    m += "/id_ghalat " + str(chat_id) + "\n"
                    m += "/code_ghalat " + str(chat_id)
                    send(ADMIN_URL, ADMIN_ID, m)
                    m2 = "وصل الطلب ديالك\n"
                    m2 += offer + "\n"
                    m2 += "تسنا شوية غادي نشحن ليك"
                    send(URL, chat_id, m2)
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
                        cid = parts[1]
                        m = "تم شحن حسابك بنجاح\n"
                        m += "شكرا على ثقتك فـ Speed Charge"
                        send(URL, cid, m)
                        send(ADMIN_URL, ADMIN_ID, "صافي دازت ليه")
                    else:
                        send(ADMIN_URL, ADMIN_ID, "صيفط: /done + الكود")
                elif text.startswith("/id_ghalat"):
                    parts = text.split()
                    if len(parts) == 2:
                        cid = int(parts[1])
                        user_step[cid] = "id"
                        m = "ID اللي صيفطي غالط\n"
                        m += "عاود صيفط ID صحيح"
                        send(URL, cid, m)
                        send(ADMIN_URL, ADMIN_ID, "صيفطنا ليه ID غالط")
                    else:
                        send(ADMIN_URL, ADMIN_ID, "صيفط: /id_ghalat + الكود")
                elif text.startswith("/code_ghalat"):
                    parts = text.split()
                    if len(parts) == 2:
                        cid = int(parts[1])
                        user_step[cid] = "code"
                        m = "كود التعبئة غالط\n"
                        m += "عاود صيفط كود جديد"
                        send(URL, cid, m)
                        send(ADMIN_URL, ADMIN_ID, "صيفطنا ليه الكود غالط")
                    else:
                        send(ADMIN_URL, ADMIN_ID, "صيفط: /code_ghalat + الكود")
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
