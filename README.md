# Quiz App (Flask + SQLite)

A multiple-choice quiz with automatic scoring, answer review and a leaderboard.

## Features
- Questions stored in SQLite and shuffled with `ORDER BY RANDOM()`
- Server-side scoring (correct answers are never sent to the browser)
- Per-question review after submitting
- Leaderboard ranked by percentage score
- Unit tests with unittest

## UI
Gen-Z dark theme: aurora gradient background, glassmorphism cards, pill buttons and emoji accents (pure CSS, no JS frameworks).

## Tech
Python, Flask, SQLite, HTML, CSS (Jinja2 templates)

## Run
```bash
pip install -r requirements.txt
python app.py              # open http://127.0.0.1:5000
python -m unittest         # run tests
```

## Add your own questions
Insert rows into the `questions` table (or extend `SEED_QUESTIONS` in `app.py`).
