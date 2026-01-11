from flask import Flask, request, jsonify, send_file, render_template
import requests, random
from PIL import Image, ImageDraw
import os

app = Flask(__name__)

REQUIRED_ACCOUNTS = [
    "lezzetkayseride",
    "gazezoglutupvekomur",
    "muhammedgeziyor"
]

@app.route("/")
def home():
    return render_template("index.html")

# Instagram yardımcı fonksiyonları
def ig_get(url, sessionid):
    return requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cookie": f"sessionid={sessionid};"
        }
    )

def get_user_id(username, sessionid):
    r = ig_get(f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}", sessionid).json()
    return r["data"]["user"]["id"]

def get_following_ids(user_id, sessionid):
    url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/"
    ids = set()
    while True:
        r = ig_get(url, sessionid).json()
        for u in r.get("users", []):
            ids.add(u["username"])
        if "next_max_id" not in r:
            break
        url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?max_id={r['next_max_id']}"
    return ids

def get_comments(media_id, sessionid):
    url = f"https://i.instagram.com/api/v1/media/{media_id}/comments/"
    users = set()
    while True:
        r = ig_get(url, sessionid).json()
        for c in r.get("comments", []):
            users.add(c["user"]["username"])
        if "next_max_id" not in r:
            break
        url = f"https://i.instagram.com/api/v1/media/{media_id}/comments/?max_id={r['next_max_id']}"
    return list(users)

def make_image(asils, yedeks):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    d.text((W//2 - 200, 30), "Kazanan Talihliler", fill=(0,0,0))
    y = 120

    for i,u in enumerate(asils):
        d.text((100, y), f"Asıl {i+1}: {u}", fill=(0,150,0))
        y += 80

    y += 40
    d.text((W//2 - 200, y), "Yedek Talihliler", fill=(0,0,0))
    y += 80

    for i,u in enumerate(yedeks):
        d.text((100, y), f"Yedek {i+1}: {u}", fill=(200,0,0))
        y += 80

    img.save("winners.png")

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    sessionid = data["session"]
    post_url = data["post"]

    # Post ID
    post = ig_get(post_url + "?__a=1&__d=dis", sessionid).json()
    media_id = post["items"][0]["id"]

    commenters = get_comments(media_id, sessionid)

    valid_users = []

    for user in commenters:
        try:
            uid = get_user_id(user, sessionid)
            following = get_following_ids(uid, sessionid)

            if all(acc.lower() in [f.lower() for f in following] for acc in REQUIRED_ACCOUNTS):
                valid_users.append(user)
        except:
            pass

    if len(valid_users) < 4:
        return jsonify({"error": "Yeterli şartı sağlayan kullanıcı bulunamadı"})

    random.shuffle(valid_users)
    asils = valid_users[:2]
    yedeks = valid_users[2:4]

    make_image(asils, yedeks)

    return jsonify({
        "asil1": asils[0],
        "asil2": asils[1],
        "yedek1": yedeks[0],
        "yedek2": yedeks[1],
        "image": "/image"
    })

@app.route("/image")
def image():
    return send_file("winners.png", mimetype="image/png")

app.run(host="0.0.0.0", port=3000)
