import random

def fetch_comments(url):
    comments = []

    for i in range(17000):
        comments.append({
            "username": f"user_{i}",
            "avatar": f"https://i.pravatar.cc/150?img={i%70}"
        })

    return comments

def pick(comments):
    random.shuffle(comments)
    winners = comments[:2]
    backups = comments[2:4]
    return winners, backups
