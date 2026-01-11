from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Instagram Çekiliş Aracı</title>
<style>
body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
.container { background:#020617; padding:30px; max-width:600px; margin:50px auto; border-radius:12px; }
input, button { width:100%; padding:12px; margin:10px 0; border-radius:8px; border:none; }
button { background:#6366f1; color:white; font-size:16px; cursor:pointer; }
button:hover { background:#4f46e5; }
.result { margin-top:20px; font-size:20px; color:#22c55e; }
</style>
</head>
<body>
<div class="container">
<h1>🎉 Instagram Çekiliş Aracı</h1>
<input id="post" placeholder="Instagram Post Linki">
<button onclick="getComments()">Yorumları Çek</button>
<button onclick="drawWinner()">Kazananı Seç</button>
<div id="info"></div>
<div class="result" id="winner"></div>
</div>

<script>
let comments = [];

function getComments(){
  fetch("/fetch-comments", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({link: document.getElementById("post").value})
  })
  .then(r=>r.json())
  .then(d=>{
    comments = d.comments;
    document.getElementById("info").innerHTML = "Toplam Yorum: " + comments.length;
  });
}

function drawWinner(){
  fetch("/draw-winner", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({comments: comments})
  })
  .then(r=>r.json())
  .then(d=>{
    document.getElementById("winner").innerHTML = "🏆 Kazanan: " + d.winner;
  });
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/fetch-comments", methods=["POST"])
def fetch_comments():
    # DEMO: Gerçek Instagram yerine sahte yorumlar
    fake_comments = [
        "ahmet", "mehmet", "ayse", "fatma", "can",
        "elif", "murat", "zeynep", "burak", "seda"
    ]
    return jsonify({"comments": fake_comments})

@app.route("/draw-winner", methods=["POST"])
def draw():
    data = request.json
    winner = random.choice(data["comments"])
    return jsonify({"winner": winner})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
