"""App controller: navigation, language, game sessions (single game or the hidden daily battery)."""
import flet as ft
from config import DB_PATH, DEFAULT_LANG
from core.db import DB
from core.i18n import tr
from core.voice import Voice
from core.adaptive import DifficultyEngine
from core.sync import sync_loop
from core import theme
from games import REGISTRY, DAILY_BATTERY
from screens import patient as sc


class App:
    def __init__(self, page: ft.Page, db=None):
        self.page = page
        self.db = db or DB(DB_PATH)
        self.patient = self.db.patient()
        self.lang = self.patient.get("language") or DEFAULT_LANG
        self.voice = Voice(page)
        self.engine = DifficultyEngine(self.db)
        self.current_game = None
        self.last_game = None        # for the "recent memory" question
        self.session_scores = []     # [(gid, score)] for the running daily battery

    # ---- basics
    def t(self, key, **kw):
        return tr(self.lang, key, **kw)

    def set_lang(self, lang):
        self.lang = lang
        self.db.set_language(lang)
        self.home()

    def toast(self, text):
        self.page.show_dialog(ft.SnackBar(ft.Text(text, size=22), duration=2500))

    def start(self):
        p = self.page
        p.title = "SmritiSaathi"
        p.bgcolor = theme.BG
        p.padding = 0
        p.theme = ft.Theme(color_scheme_seed=theme.SAFFRON)
        p.run_task(sync_loop, self)
        self.go(sc.language_screen(self))

    def go(self, control, game=None):
        if self.current_game:
            self.current_game.dispose()
        self.current_game = game
        self.page.controls.clear()
        self.page.add(control)
        if game:
            game.start()

    # ---- routes
    def home(self): self.go(sc.home_screen(self))
    def games_menu(self):
        self.voice.speak(self.t("games_title"), self.lang)
        self.go(sc.games_screen(self))

    def reminders(self):
        self.voice.speak(self.t("r_title"), self.lang)
        self.go(sc.reminders_screen(self))

    def route(self, intent):
        {"games": self.games_menu, "reminders": self.reminders, "home": self.home,
         "daily": self.start_daily}.get(intent, self.home)()

    def open_voice(self):
        sc.voice_dialog(self)

    # ---- sessions
    def start_game(self, gid, queue=None, daily=False):
        meta = REGISTRY[gid]
        level = self.engine.level_for(gid)
        step = None
        if queue is not None:
            n = len(DAILY_BATTERY)
            step = self.t("step_of", i=n - len(queue), n=n)

        def done(score, detail):
            self._game_done(gid, level, score, queue, daily)

        game = meta["cls"](self, level, done, **meta.get("opts", {}))
        self.voice.speak(self.t(meta["instr"]), self.lang)
        self.go(sc.intro_screen(self, gid, level, step, lambda: self.go(
            sc.game_screen(self, gid, game), game)))

    def start_daily(self):
        self.session_scores = []
        self.last_game = None
        self.start_game(DAILY_BATTERY[0], queue=DAILY_BATTERY[1:], daily=True)

    def _game_done(self, gid, level, score, queue, daily):
        self.db.add_result(gid, level, score, REGISTRY[gid]["domains"], daily=daily)
        self.engine.update(gid, score)
        self.last_game = gid
        self.session_scores.append((gid, score))
        if queue:
            self.go(sc.result_screen(self, gid, score, next_label=self.t("next"),
                                     on_next=lambda: self.start_game(queue[0], queue[1:], True)))
        elif daily:
            self.go(sc.daily_summary_screen(self))
        else:
            self.go(sc.result_screen(self, gid, score, next_label=self.t("play_again"),
                                     on_next=lambda: self.start_game(gid)))
