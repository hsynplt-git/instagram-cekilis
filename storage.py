import json, uuid, os

DB_FILE = "draws.json"

def load():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_draw(post_url, winners, backups):
    data = load()
    draw_id = str(uuid.uuid4())[:8]

    data[draw_id] = {
        "post_url": post_url,
        "winners": winners,
        "backups": backups
    }

    save(data)
    return draw_id

def get_draw(draw_id):
    return load().get(draw_id)
