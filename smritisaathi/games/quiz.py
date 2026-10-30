"""Multiple-choice rounds: Arrow Sums (calculation) and Recall (memory/language)."""
import asyncio, random
import flet as ft
from games.base import Game
from core import theme
from core.voice import match_option
from core.content import CK, PERSONAL_Q, NAMES, TOWNS


class Quiz(Game):
    def rounds(self):  # -> list of (question_control, [option_str], correct_index)
        raise NotImplementedError

    def build(self):
        self.R, self.i, self.score, self.locked = self.rounds(), 0, 0, False
        self.q = ft.Container(alignment=ft.Alignment.CENTER, padding=10)
        self.fb = ft.Text("", size=30, weight=ft.FontWeight.BOLD)
        self.opts_col = ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self._load()
        self.heard = ft.Text("", size=22, color=theme.TEAL)
        extras = []
        if self.app.voice.stt is not None:   # answer-by-voice is offered wherever STT exists
            self.mic = ft.Container(ft.Row([ft.Icon(ft.Icons.MIC, color="white", size=36),
                                            ft.Text(self.t("speak_answer"), size=24, color="white",
                                                    weight=ft.FontWeight.BOLD)], tight=True),
                                    bgcolor=theme.MAROON, border_radius=40, padding=16, ink=True,
                                    on_click=self._voice_answer)
            extras = [self.mic, self.heard]
        return ft.Column([self.q, self.opts_col, self.fb] + extras, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                         scroll=ft.ScrollMode.AUTO, expand=True, spacing=16)

    def _load(self):
        q, opts, ans = self.R[self.i]
        self.q.content, self.fb.value, self.locked = q, "", False
        if isinstance(q, ft.Text):
            self.app.voice.speak(q.value, self.app.lang)
        self.btns = []
        for k, o in enumerate(opts):
            b = ft.Container(ft.Text(o, size=30, weight=ft.FontWeight.BOLD, color="white",
                                     text_align=ft.TextAlign.CENTER), bgcolor=theme.TEAL, border_radius=20,
                             width=340, padding=18, alignment=ft.Alignment.CENTER, ink=True)
            b.on_click = self._h(k)
            self.btns.append(b)
        self.opts_col.controls = self.btns

    async def _voice_answer(self, e):
        if self.locked or not self.active:
            return
        self.heard.value = self.t("listening"); self.refresh()
        cands = await self.app.voice.listen(self.app.lang, seconds=6)
        k = match_option(cands, [b.content.value for b in self.btns]) if cands else None
        if k is None:
            self.heard.value = self.t("say_again")
            self.app.voice.speak(self.t("say_again"), self.app.lang)
            self.refresh()
            return
        self.heard.value = cands[0]
        await self._h(k)(None)

    def _h(self, k):
        async def h(e):
            if self.locked or not self.active: return
            self.locked = True
            ans = self.R[self.i][2]
            ok = k == ans
            self.score += ok
            self.btns[k].bgcolor = theme.GREEN if ok else theme.MAROON
            self.btns[ans].bgcolor = theme.GREEN
            self.fb.value = self.t("correct") if ok else self.t("wrong")
            self.fb.color = theme.GREEN if ok else theme.MAROON
            self.app.voice.speak(self.fb.value, self.app.lang)
            self.refresh()
            await asyncio.sleep(1.4)
            if not self.active: return
            self.i += 1
            if self.i >= len(self.R):
                self.finish(100 * self.score / len(self.R))
            else:
                self._load(); self.refresh()
        return h


class ArrowSums(Quiz):
    def rounds(self):
        out = []
        for _ in range(5):
            cur = start = random.randint(8, 20 + 5 * self.level)
            chips = []
            for _ in range(1 + self.level):
                v = random.randint(1, 3 + 2 * self.level)
                up = random.random() < 0.5 or cur - v < 0
                cur += v if up else -v
                chips.append(ft.Container(ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD if up else ft.Icons.ARROW_DOWNWARD,
                                                          color="white", size=34),
                                                  ft.Text(str(v), size=34, color="white", weight=ft.FontWeight.BOLD)],
                                                 tight=True), bgcolor=theme.GREEN if up else theme.MAROON,
                                          border_radius=16, padding=12))
            wrong = set()
            while len(wrong) < 3:
                d = random.choice([-3, -2, -1, 1, 2, 3, 10])
                if cur + d >= 0 and d != 0: wrong.add(cur + d)
            opts = [cur] + sorted(wrong); random.shuffle(opts)
            q = ft.Column([ft.Text(self.t("start_at", n=start), size=34, weight=ft.FontWeight.BOLD, color=theme.INK),
                           ft.Row(chips, alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=10)],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            out.append((q, [str(o) for o in opts], opts.index(cur)))
        return out




def _opts(correct, pool):
    o = random.sample([p for p in pool if p != correct], 3) + [correct]
    random.shuffle(o)
    return o, o.index(correct)


class Recall(Quiz):
    def rounds(self):
        txt = lambda s: ft.Text(s, size=32, weight=ft.FontWeight.BOLD, color=theme.INK, text_align=ft.TextAlign.CENTER)
        R = []
        for q, o, a in random.sample(CK[self.app.lang], 2):
            R.append((txt(q), o, a))
        p = self.app.patient  # remote personal memory (profile is set by the caregiver)
        o, a = _opts(p["child_name"], NAMES)
        R.append((txt(PERSONAL_Q["child"][self.app.lang]), o, a))
        o, a = _opts(p["hometown"], TOWNS)
        R.append((txt(PERSONAL_Q["town"][self.app.lang]), o, a))
        last = self.app.last_game  # recent memory
        if last:
            from games import REGISTRY
            names = [self.app.t(m["title"]) for m in REGISTRY.values() if m["ready"]]
            o, a = _opts(self.app.t(REGISTRY[last]["title"]), names)
            R.append((txt(self.t("q_recent")), o, a))
        return R
