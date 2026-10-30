"""On-device SQLite store (offline-first). Every result is written here first; sync.py pushes later.
Schema here is the source for Table 4.2 in the report."""
import json, sqlite3, random
from datetime import datetime, timedelta, date

SCHEMA = """
CREATE TABLE IF NOT EXISTS patient(id INTEGER PRIMARY KEY, name TEXT, language TEXT,
    hometown TEXT, child_name TEXT);
CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, level INTEGER,
    score INTEGER, domains TEXT, daily INTEGER DEFAULT 0, played_at TEXT, synced INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS difficulty(game TEXT PRIMARY KEY, level INTEGER);
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, label TEXT,
    time TEXT, synced INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS reminder_log(reminder_id INTEGER, day TEXT, done_at TEXT,
    PRIMARY KEY(reminder_id, day));
"""


class DB:
    def __init__(self, path):
        self.c = sqlite3.connect(str(path), check_same_thread=False)
        self.c.row_factory = sqlite3.Row
        self.c.executescript(SCHEMA)
        if not self.c.execute("SELECT 1 FROM patient").fetchone():
            self.c.execute("INSERT INTO patient(id,name,language,hometown,child_name) VALUES(1,?,?,?,?)",
                           ("Aaji", "hi", "Nagpur", "Sunita"))
            for k, l, t in [("med", "Morning tablets", "08:00"), ("water", "Drink a glass of water", "11:00"),
                            ("activity", "Short walk", "17:00"), ("med", "Evening tablets", "20:00")]:
                self.c.execute("INSERT INTO reminders(kind,label,time) VALUES(?,?,?)", (k, l, t))
            self.c.commit()

    # patient
    def patient(self):
        return dict(self.c.execute("SELECT * FROM patient WHERE id=1").fetchone())

    def set_language(self, lang):
        self.c.execute("UPDATE patient SET language=? WHERE id=1", (lang,)); self.c.commit()

    # results
    def add_result(self, game, level, score, domains, daily=False, when=None):
        self.c.execute("INSERT INTO results(game,level,score,domains,daily,played_at) VALUES(?,?,?,?,?,?)",
                       (game, level, score, json.dumps(domains), int(daily),
                        (when or datetime.now()).isoformat(timespec="seconds")))
        self.c.commit()

    def results_since(self, days):
        since = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.c.execute("SELECT * FROM results WHERE played_at>=? ORDER BY played_at", (since,)).fetchall()
        return [dict(r, domains=json.loads(r["domains"])) for r in rows]

    def daily_done_today(self):
        return bool(self.c.execute("SELECT 1 FROM results WHERE daily=1 AND substr(played_at,1,10)=?",
                                   (date.today().isoformat(),)).fetchone())

    def unsynced(self):
        return [dict(r) for r in self.c.execute("SELECT * FROM results WHERE synced=0").fetchall()]

    def mark_synced(self, ids):
        self.c.executemany("UPDATE results SET synced=1 WHERE id=?", [(i,) for i in ids]); self.c.commit()

    # adaptive difficulty
    def level(self, game):
        r = self.c.execute("SELECT level FROM difficulty WHERE game=?", (game,)).fetchone()
        return r["level"] if r else 1

    def set_level(self, game, level):
        self.c.execute("INSERT OR REPLACE INTO difficulty(game,level) VALUES(?,?)", (game, level)); self.c.commit()

    def recent_scores(self, game, n=3):
        return [r["score"] for r in self.c.execute(
            "SELECT score FROM results WHERE game=? ORDER BY id DESC LIMIT ?", (game, n))]

    # reminders
    def reminders_today(self):
        today = date.today().isoformat()
        rows = self.c.execute("""SELECT r.*, l.done_at FROM reminders r
            LEFT JOIN reminder_log l ON l.reminder_id=r.id AND l.day=? ORDER BY r.time""", (today,)).fetchall()
        return [dict(r) for r in rows]

    def mark_reminder_done(self, rid):
        self.c.execute("INSERT OR REPLACE INTO reminder_log VALUES(?,?,?)",
                       (rid, date.today().isoformat(), datetime.now().isoformat(timespec="seconds")))
        self.c.commit()

    def add_reminder(self, kind, label, time):
        self.c.execute("INSERT INTO reminders(kind,label,time) VALUES(?,?,?)", (kind, label, time)); self.c.commit()

    def compliance(self, days=7):
        """Returns (done, expected) over the last `days` full days incl. today."""
        n = self.c.execute("SELECT COUNT(*) FROM reminders").fetchone()[0]
        since = (date.today() - timedelta(days=days - 1)).isoformat()
        done = self.c.execute("SELECT COUNT(*) FROM reminder_log WHERE day>=?", (since,)).fetchone()[0]
        return done, n * days

    def seed_demo(self):
        """Fill 14 days of plausible data so the caregiver dashboard has something to show."""
        from games import REGISTRY
        rnd = random.Random(7)
        ids = [g for g, m in REGISTRY.items() if m["ready"]]
        for d in range(14, 0, -1):
            day = datetime.now() - timedelta(days=d)
            if d in (9, 4):  # a couple of missed days
                continue
            for g in rnd.sample(ids, 4):
                drift = (14 - d) * (-0.8 if "memory" in REGISTRY[g]["domains"] else 0.3)
                score = max(20, min(100, int(rnd.gauss(72, 10) + drift)))
                self.add_result(g, 1 + rnd.randint(0, 1), score, REGISTRY[g]["domains"],
                                daily=g in ("digit_f", "knox"), when=day.replace(hour=rnd.randint(9, 18)))
            for r in self.c.execute("SELECT id FROM reminders").fetchall():
                if rnd.random() < 0.8:
                    self.c.execute("INSERT OR REPLACE INTO reminder_log VALUES(?,?,?)",
                                   (r["id"], day.date().isoformat(), day.isoformat(timespec="seconds")))
        self.c.commit()
