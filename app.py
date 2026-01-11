from flask import Flask, request, jsonify, render_template
import requests, random, time, sqlite3, io, os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__, static_folder="static")

# ========== INSTAGRAM SESSION ==========
SESSION_ID = "6683989654%3AKEpYtx3t62ZYMI%3A1%3AAYhiDD_mY9W7xQgE5UCA9aPNP4LKwRdZgvmHJD_zjg"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": f"sessionid={SESSION_ID};"
}

REQUIRED_ACCOUNTS = ["lezzetkayseride","gazezoglutupvekomur","muhammedgeziyor"]

# ========== DATABASE ==========
def db():
    return sqlite3.connect("draws.db", check_same_thread=False)

c = db().cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS draws(
id TEXT,
reel TEXT,
date TEXT,
total INTEGER,
main1 TEXT,
main2 TEXT,
backup1 TEXT,
backup2 TEXT,
story TEXT
)
""")
db().commit()

# ========== INSTAGRAM ==========
def get_post_id(shortcode):
    url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"
    return requests.get(url, headers=HEADERS).json()["items"][0]["id"]

def get_all_comments(shortcode):
    post_id = get_post_id(shortcode)
    users = {}
    max_id = None

    while True:
        url = f"https://i.instagram.com/api/v1/media/{post_id}/comments/"
        params = {"max_id": max_id} if max_id else {}
        r = requests.get(url, headers=HEADERS, params=params).json()

        for c in r["comments"]:
            users[c["user"]["username"]] = True

        if r.get("next_max_id"):
            max_id = r["next_max_id"]
            time.sleep(1.3)
        else:
            break

    return list(users.keys())

def get_profile(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    return requests.get(url, headers=HEADERS).json()["graphql"]["user"]["profile_pic_url_hd"]

# ========== STORY ==========
def create_story(main, backup):
    img = Image.new("RGB", (1080,1920), "#0d0d0d")
    draw = ImageDraw.Draw(img)

    draw.text((540,80),"ÇEKİLİŞ KAZANANLARI",fill="white",anchor="mm")

    y = 220

    def block(u,y):
        p = requests.get(u["photo"]).content
        av = Image.open(io.BytesIO(p)).resize((200,200))
        img.paste(av,(440,y))
        draw.text((540,y+220),"@"+u["username"],fill="white",anchor="mm")
        return y+320

    draw.text((540,y-40),"ASİL KAZANANLAR",fill="#00ffcc",anchor="mm")
    for u in main: y = block(u,y)

    y+=40
    draw.text((540,y),"YEDEKLER",fill="#ffaa00",anchor="mm")
    y+=60
    for u in backup: y = block(u,y)

    img.save("static/story.png")

# ========== ROUTES ==========
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/draw", methods=["POST"])
def draw():
    reel = request.json["url"]
    shortcode = reel.split("/reel/")[1].split("/")[0]

    commenters = get_all_comments(shortcode)

    selected = random.sample(commenters, 4)
    users = [{"username":u,"photo":get_profile(u)} for u in selected]

    create_story(users[:2], users[2:])

    draw_id = "CK-" + datetime.now().strftime("%Y%m%d%H%M%S")

    c = db().cursor()
    c.execute("INSERT INTO draws VALUES (?,?,?,?,?,?,?, ?,?)",(
        draw_id, shortcode, datetime.now().strftime("%d.%m.%Y %H:%M"),
        len(commenters),
        users[0]["username"], users[1]["username"],
        users[2]["username"], users[3]["username"],
        "/static/story.png"
    ))
    db().commit()

    return jsonify({
        "draw_id": draw_id,
        "total": len(commenters),
        "winners": users[:2],
        "backups": users[2:],
        "story": "/static/story.png"
    })

@app.route("/result/<draw_id>")
def get_draw(draw_id):
    c = db().cursor()
    c.execute("SELECT * FROM draws WHERE id=?", (draw_id,))
    d = c.fetchone()
    if not d:
        return "Bulunamadı"

    return jsonify({
        "id": d[0],
        "reel": d[1],
        "date": d[2],
        "total": d[3],
        "main": [d[4], d[5]],
        "backup": [d[6], d[7]],
        "story": d[8]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
