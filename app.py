from flask import Flask, request, jsonify, render_template
import requests
import random
import time

app = Flask(__name__)

SESSION_ID = "6683989654%3AKEpYtx3t62ZYMI%3A1%3AAYhiDD_mY9W7xQgE5UCA9aPNP4LKwRdZgvmHJD_zjg"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": f"sessionid={SESSION_ID};"
}

REQUIRED_ACCOUNTS = [
    "lezzetkayseride",
    "gazezoglutupvekomur",
    "muhammedgeziyor"
]

def get_post_id(shortcode):
    url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"
    r = requests.get(url, headers=HEADERS)
    return r.json()["items"][0]["id"]

def get_all_comments(shortcode):
    post_id = get_post_id(shortcode)
    comments = {}
    max_id = None

    while True:
        url = f"https://i.instagram.com/api/v1/media/{post_id}/comments/"
        params = {"max_id": max_id} if max_id else {}
        r = requests.get(url, headers=HEADERS, params=params)
        data = r.json()

        for c in data["comments"]:
            user = c["user"]["username"]
            comments[user] = True

        if data.get("next_max_id"):
            max_id = data["next_max_id"]
            time.sleep(1.2)
        else:
            break

    return list(comments.keys())

def is_following(user, target):
    url = f"https://i.instagram.com/api/v1/friendships/{user}/following/"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    return target in [u["username"] for u in data.get("users", [])]

@app.route("/")
def home():
    return render_template("index.html")

def get_profile_pic(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    r = requests.get(url, headers=HEADERS)
    return r.json()["graphql"]["user"]["profile_pic_url_hd"]

    @app.route("/draw", methods=["POST"])
def draw():
    reel_url = request.json["url"]
    shortcode = reel_url.split("/reel/")[1].split("/")[0]

    commenters = get_all_comments(shortcode)

    valid_users = []

    for user in commenters:
        ok = True
        for acc in REQUIRED_ACCOUNTS:
            if not is_following(user, acc):
                ok = False
                break
        if ok:
            valid_users.append(user)

    selected = random.sample(valid_users, 4)

    winners = []
    for u in selected:
        winners.append({
            "username": u,
            "photo": get_profile_pic(u)
        })

    return jsonify({
        "total_comments": len(commenters),
        "valid_users": len(valid_users),
        "main_winners": winners[:2],
        "backup_winners": winners[2:]
    })

if __name__ == "__main__":
    app.run()
