from flask import Flask, request
import random
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "123456"
PAGE_ACCESS_TOKEN = "DAN_TOKEN_VAO_DAY"

users = {}

def tai_xiu():
    x1 = random.randint(1,6)
    x2 = random.randint(1,6)
    x3 = random.randint(1,6)
    tong = x1 + x2 + x3

    if x1 == x2 == x3:
        return tong, "BO BA"
    elif tong >= 11:
        return tong, "TAI"
    else:
        return tong, "XIU"

def get_user(uid):
    if uid not in users:
        users[uid] = {"money":1000}
    return users[uid]

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    if token == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Sai token"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        event = data['entry'][0]['messaging'][0]
        sender = event['sender']['id']
        message = event['message']['text'].lower()

        user = get_user(sender)

        if message == "start":
            send(sender, "Chào bạn 🎮 Gõ: tx 100 tai để chơi")
        
        elif message.startswith("tx"):
            parts = message.split()

            if len(parts) != 3:
                send(sender, "Sai cú pháp: tx 100 tai")
                return "ok"

            bet = int(parts[1])
            choice = parts[2].upper()

            if bet > user["money"]:
                send(sender, "Không đủ tiền!")
                return "ok"

            tong, result = tai_xiu()

            if choice == result:
                user["money"] += bet
                msg = f"🎲 {tong} => {result}\nThắng +{bet}"
            else:
                user["money"] -= bet
                msg = f"🎲 {tong} => {result}\nThua -{bet}"

            msg += f"\n💰 Tiền: {user['money']}"
            send(sender, msg)

        elif message == "money":
            send(sender, f"💰 Tiền: {user['money']}")

        else:
            send(sender, "Gõ: tx 100 tai để chơi 🎲")

    except:
        pass

    return "ok"

def send(uid, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": uid},
        "message": {"text": text}
    }
    requests.post(url, json=data)

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
