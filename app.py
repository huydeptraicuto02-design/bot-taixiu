from flask import Flask, request
import requests, random, json, time

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "TOKEN_CUA_BAN"
VERIFY_TOKEN = "123456"

users = {}

# ================== DATA ==================
def load():
    global users
    try:
        with open("data.json") as f:
            users = json.load(f)
    except:
        users = {}

def save():
    with open("data.json", "w") as f:
        json.dump(users, f)

load()

# ================== SEND ==================
def send(uid, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": uid},
        "message": {"text": text}
    }
    requests.post(url, json=data)

# ================== GAME ==================
def roll():
    return random.randint(1,6) + random.randint(1,6) + random.randint(1,6)

def result_text(total):
    return "tai" if total >= 11 else "xiu"

# ================== VERIFY ==================
@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error"

# ================== WEBHOOK ==================
@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    try:
        msg = data["entry"][0]["messaging"][0]
        sender = msg["sender"]["id"]

        if "message" not in msg:
            return "ok"

        text = msg["message"].get("text", "").lower()

        # ===== INIT USER =====
        if sender not in users:
            users[sender] = {
                "money": 1000,
                "last_daily": 0,
                "win": 0,
                "lose": 0
            }

        user = users[sender]

        # ===== COMMAND =====
        if text.startswith("tx"):
            try:
                _, bet, choice = text.split()
                bet = int(bet)

                if bet <= 0 or bet > user["money"]:
                    send(sender, "❌ Tiền không hợp lệ")
                    return "ok"

                if choice not in ["tai", "xiu"]:
                    send(sender, "❌ Chọn tai hoặc xiu")
                    return "ok"

                total = roll()
                res = result_text(total)

                if choice == res:
                    user["money"] += bet
                    user["win"] += 1
                    msg = f"🎲 {total} => {res.upper()}\n✅ Thắng +{bet}"
                else:
                    user["money"] -= bet
                    user["lose"] += 1
                    msg = f"🎲 {total} => {res.upper()}\n❌ Thua -{bet}"

                msg += f"\n💰 Tiền: {user['money']}"
                send(sender, msg)
                save()

            except:
                send(sender, "📌 Cách chơi: tx 100 tai")

        elif text == "money":
            send(sender, f"💰 Tiền: {user['money']}")

        elif text == "daily":
            now = time.time()
            if now - user["last_daily"] >= 86400:
                user["money"] += 500
                user["last_daily"] = now
                send(sender, "🎁 Nhận 500 xu")
                save()
            else:
                send(sender, "⏳ Đã nhận hôm nay rồi")

        elif text == "top":
            top = sorted(users.items(), key=lambda x: x[1]["money"], reverse=True)[:5]
            msg = "🏆 TOP\n"
            for i, (uid, u) in enumerate(top):
                msg += f"{i+1}. {u['money']}\n"
            send(sender, msg)

        elif text == "stat":
            send(sender, f"📊 Win: {user['win']} | Lose: {user['lose']}")

        elif text == "allin tai" or text == "allin xiu":
            choice = text.split()[1]
            bet = user["money"]

            total = roll()
            res = result_text(total)

            if choice == res:
                user["money"] += bet
                user["win"] += 1
                msg = f"🎲 {total} => {res}\n🔥 ALL IN THẮNG"
            else:
                user["money"] -= bet
                user["lose"] += 1
                msg = f"🎲 {total} => {res}\n💀 ALL IN THUA"

            msg += f"\n💰 {user['money']}"
            send(sender, msg)
            save()

        elif text == "help":
            send(sender,
            "🎲 BOT TÀI XỈU\n"
            "tx 100 tai\n"
            "money\n"
            "daily\n"
            "top\n"
            "stat\n"
            "allin tai/xiu"
            )

        else:
            send(sender, "Gõ help để xem lệnh")

    except Exception as e:
        print(e)

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)

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
  
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
