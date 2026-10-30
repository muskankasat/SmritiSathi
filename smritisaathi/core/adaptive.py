"""Adaptive-difficulty engine. Rule-based today; the TFLite model slots in at `predict`."""
from config import MAX_LEVEL


class DifficultyEngine:
    def __init__(self, db):
        self.db = db
        self.model = None  # TODO: load assets/difficulty.tflite once trained on usability-test logs

    def level_for(self, game):
        return self.db.level(game)

    def update(self, game, score):
        scores = self.db.recent_scores(game, 3)   # includes the result just saved
        lvl = self.db.level(game)
        new = self.predict(lvl, scores)
        self.db.set_level(game, new)
        return new

    def predict(self, level, scores):
        if self.model is not None:
            pass  # run TFLite interpreter on [level, *scores] and return its level
        avg = sum(scores) / len(scores) if scores else 0
        if scores and scores[0] >= 80 and avg >= 70:
            return min(MAX_LEVEL, level + 1)
        if scores and scores[0] < 40:
            return max(1, level - 1)
        return level
