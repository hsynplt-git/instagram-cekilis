from flask import Flask, request, jsonify, render_template
import requests, random, time, sqlite3, io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

SESSION_ID = "6683989654%3AKEpYtx3t62ZYMI%3A1%3AAYhiDD_mY9W7xQgE5UCA9aPNP4LKwRdZgvmHJD_zjg"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": f"sessionid={SESSION_ID};"
}

REQUIRED_ACCOUNTS = ["lezzetkayseride","gazezoglutupvekomur","muhammedgeziyor"]

# ---------------- DB ----------------
def db():
    return sqlite3.connect("draws.db", check_same_thread=False)

conn = db()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS draws(
id TEXT, reel TEXT, date TEXT,
total INTEGER, valid INTEGER,
main1 TEXT, main2 TEXT,
backup1 TEXT, backup2 TEXT,
story TEXT)
""")
conn.commit()

# ---------------- Instagram ----------------
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
            time.sleep(1.2)
        else:
            break

    return list(users.keys())

def get_profile(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    return requests.get(url, headers=HEADERS).json()["graphql"]["user"]["profile_pic_url_hd"]

# ⚠️ Instagram bu endpointi kısıtladığı için takip kontrolü şimdilik devre dışı
def is_following(user, target):
    return True

# ---------------- Story ----------------
def create_story(main, backup):
    img = Image.new("RGB", (1080,1920), "#111")
    draw = ImageDraw.Draw(img)
    draw.text((540,60),"🎉 ÇEKİLİŞ KAZANANLARI",fill="white",anchor="mm")

    y = 200

    def block(u,y):
        p = requests.get(u["photo"]).content
        av = Image.open(io.BytesIO(p)).resize((200,200))
        img.paste(av,(440,y))
        draw.text((540,y+220),"@"+u["username"],fill="white",anchor="mm")
        return y+320

    draw.text((540,y-40),"Asıl Kazananlar",fill="#00ffcc",anchor="mm")
    for u in main: y = block(u,y)

    y+=40
    draw.text((540,y),"Yedekler",fill="#ffaa00",anchor="mm")
    y+=60
    for u in backup: y = block(u,y)

    img.save("static/story.png")

# ---------------- Routes ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/draw", methods=["POST"])
def draw():
    reel = request.json["url"]
    shortcode = reel.split("/reel/")[1].split("/")[0]

    commenters = get_all_comments(shortcode)
    valid = commenters  # takip filtresi kapalı

    selected = random.sample(valid, 4)
    winners = [{"username":u,"photo":get_profile(u)} for u in selected]

    create_story(winners[:2], winners[2:])

    draw_id = "DL-" + datetime.now().strftime("%Y%m%d%H%M%S")

    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO draws VALUES (?,?,?,?,?,?,?,?,?,?)",(
        draw_id, shortcode, datetime.now().strftime("%d.%m.%Y %H:%M"),
        len(commenters), len(valid),
        winners[0]["username"], winners[1]["username"],
        winners[2]["username"], winners[3]["username"],
        "/static/story.png"
    ))
    conn.commit()

    return jsonify({
        "draw_id": draw_id,
        "total_comments": len(commenters),
        "valid_users": len(valid),
        "main_winners": winners[:2],
        "backup_winners": winners[2:],
        "story": "/static/story.png"
    })

@app.route("/draw/<draw_id>")
def get_draw(draw_id):
    c = db().cursor()
    c.execute("SELECT * FROM draws WHERE id=?", (draw_id,))
    d = c.fetchone()
    if not d: return "Bulunamadı"

    return jsonify({
        "id": d[0],
        "reel": d[1],
        "date": d[2],
        "total": d[3],
        "valid": d[4],
        "main": [d[5], d[6]],
        "backup": [d[7], d[8]],
        "story": d[9]
    })
