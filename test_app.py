import os
import tempfile
import unittest

import app as quiz_app


class QuizTests(unittest.TestCase):
    def setUp(self):
        self.fd, self.path = tempfile.mkstemp()
        quiz_app.app.config.update(DATABASE=self.path, TESTING=True)
        quiz_app.init_db()
        self.client = quiz_app.app.test_client()

    def tearDown(self):
        os.close(self.fd)
        os.unlink(self.path)

    def test_questions_seeded_once(self):
        quiz_app.init_db()  # calling twice must not duplicate
        r = self.client.get("/")
        self.assertIn(b"5 multiple-choice", r.data)

    def test_name_required(self):
        r = self.client.post("/quiz", data={"player": " "}, follow_redirects=True)
        self.assertIn(b"enter your name", r.data)

    def test_perfect_score(self):
        answers = {f"q{i + 1}": q[5] for i, q in enumerate(quiz_app.SEED_QUESTIONS)}
        answers["player"] = "Monica"
        r = self.client.post("/submit", data=answers)
        self.assertIn(b"5 / 5", r.data)

    def test_leaderboard_orders_best_first(self):
        perfect = {f"q{i + 1}": q[5] for i, q in enumerate(quiz_app.SEED_QUESTIONS)}
        self.client.post("/submit", data={"player": "Low"})
        self.client.post("/submit", data={**perfect, "player": "High"})
        page = self.client.get("/leaderboard").data.decode()
        self.assertLess(page.index("High"), page.index("Low"))


if __name__ == "__main__":
    unittest.main()
