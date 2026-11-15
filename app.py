import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = "change-me"
DATABASE = "quiz.db"

SEED_QUESTIONS = [
    ("Which keyword defines a function in Python?", "func", "def", "function", "define", "b"),
    ("Which data structure works on LIFO order?", "Queue", "Array", "Stack", "Tree", "c"),
    ("What does SQL stand for?", "Structured Query Language", "Simple Query Logic",
     "Sequential Query Language", "Standard Question Language", "a"),
    ("Time complexity of binary search?", "O(n)", "O(log n)", "O(n^2)", "O(1)", "b"),
    ("Which HTTP method is normally used to submit a form that changes data?", "GET", "HEAD",
     "POST", "TRACE", "c"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config.get("DATABASE", DATABASE))
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    with sqlite3.connect(app.config.get("DATABASE", DATABASE)) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL, option_b TEXT NOT NULL,
                option_c TEXT NOT NULL, option_d TEXT NOT NULL,
                answer TEXT NOT NULL CHECK(answer IN ('a','b','c','d')));
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                taken_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        if db.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
            db.executemany("INSERT INTO questions (question, option_a, option_b, option_c, option_d, answer)"
                           " VALUES (?,?,?,?,?,?)", SEED_QUESTIONS)


@app.route("/")
def home():
    count = get_db().execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    return render_template("home.html", count=count)


@app.route("/quiz", methods=["POST"])
def quiz():
    player = request.form.get("player", "").strip()
    if not player:
        flash("Please enter your name to start.", "error")
        return redirect(url_for("home"))
    questions = get_db().execute("SELECT * FROM questions ORDER BY RANDOM()").fetchall()
    return render_template("quiz.html", questions=questions, player=player)


@app.route("/submit", methods=["POST"])
def submit():
    player = request.form.get("player", "Anonymous")
    db = get_db()
    questions = db.execute("SELECT * FROM questions").fetchall()
    score, review = 0, []
    for q in questions:
        chosen = request.form.get(f"q{q['id']}")
        correct = chosen == q["answer"]
        score += correct
        review.append({"question": q["question"], "chosen": chosen,
                       "correct_option": q["answer"], "is_correct": correct,
                       "correct_text": q["option_" + q["answer"]]})
    db.execute("INSERT INTO results (player, score, total) VALUES (?,?,?)",
               (player, score, len(questions)))
    db.commit()
    return render_template("result.html", player=player, score=score,
                           total=len(questions), review=review)


@app.route("/leaderboard")
def leaderboard():
    rows = get_db().execute(
        "SELECT player, score, total, taken_at FROM results "
        "ORDER BY score * 1.0 / total DESC, taken_at ASC LIMIT 10").fetchall()
    return render_template("leaderboard.html", rows=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
