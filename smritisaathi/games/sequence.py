"""Digit span (forward/backward) and Knox cube imitation share one engine: show a sequence, patient repeats it."""
import asyncio, random
import flet as ft
from games.base import Game
from core import theme


class SequenceGame(Game):
    n_symbols = 10
    trials = 3

    # --- subclasses implement
    def make_pad(self): raise NotImplementedError
    async def flash(self, idx, on): raise NotImplementedError
    def start_len(self): return 2 + self.level
    backward = False

    def build(self):
        self.msg = ft.Text("", size=34, weight=ft.FontWeight.BOLD, color=theme.INK, text_align=ft.TextAlign.CENTER)
        self.shown = ft.Text("", size=64, weight=ft.FontWeight.BOLD, color=theme.SAFFRON)
        self.pad = self.make_pad()
        self.enabled, self.entered, self.seq, self.waiting = False, [], [], None
        return ft.Column([ft.Container(self.msg, padding=10),
                          ft.Container(self.shown, height=90, alignment=ft.Alignment.CENTER),
                          self.pad], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14)

    def start(self):
        self.app.page.run_task(self.run)

    def tap(self, idx):
        if not (self.enabled and self.active):
            return
        self.entered.append(idx)
        self.shown.value = self.label(idx) if self.shows_input else ""
        if len(self.entered) == len(self.seq):
            self.enabled = False
            self.waiting.set()
        self.refresh()

    shows_input = False
    def label(self, idx): return str(idx)

    async def run(self):
        L, ok_len, tot_len = self.start_len(), 0, 0
        for trial in range(self.trials):
            n = L + trial
            self.seq = [random.randrange(self.n_symbols) for _ in range(n)]
            if self.n_symbols > 1:  # avoid immediate repeats
                for i in range(1, n):
                    while self.seq[i] == self.seq[i - 1]:
                        self.seq[i] = random.randrange(self.n_symbols)
            self.msg.value = self.t("watch"); self.shown.value = ""; self.refresh()
            self.app.voice.speak(self.t("watch"), self.app.lang)
            await asyncio.sleep(1.0)
            for s in self.seq:
                if not self.active: return
                await self.flash(s, True); self.refresh()
                await asyncio.sleep(0.9)
                await self.flash(s, False); self.refresh()
                await asyncio.sleep(0.35)
            self.app.voice.speak(self.t("your_turn"), self.app.lang)
            self.msg.value = self.t("your_turn"); self.shown.value = ""
            self.entered, self.waiting, self.enabled = [], asyncio.Event(), True
            self.refresh()
            await self.waiting.wait()
            if not self.active: return
            want = self.seq[::-1] if self.backward else self.seq
            good = self.entered == want
            tot_len += n
            if good: ok_len += n
            self.msg.value = self.t("correct") if good else self.t("wrong")
            self.msg.color = theme.GREEN if good else theme.MAROON
            self.app.voice.speak(self.msg.value, self.app.lang)
            self.refresh()
            await asyncio.sleep(1.2)
            self.msg.color = theme.INK
        self.finish(100 * ok_len / tot_len, {"span": L})

    def dispose(self):
        super().dispose()
        if self.waiting: self.waiting.set()


class DigitSpan(SequenceGame):
    shows_input = True

    @property
    def backward(self): return self.opts.get("backward", False)

    def make_pad(self):
        def key(d):
            return ft.Container(ft.Text(str(d), size=40, weight=ft.FontWeight.BOLD, color="white"),
                                bgcolor=theme.TEAL, width=96, height=84, border_radius=20,
                                alignment=ft.Alignment.CENTER, ink=True, on_click=lambda e, d=d: self.tap(d))
        rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        col = [ft.Row([key(d) for d in r], alignment=ft.MainAxisAlignment.CENTER) for r in rows]
        col.append(ft.Row([key(0)], alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(col, spacing=12)

    async def flash(self, idx, on):
        self.shown.value = str(idx) if on else ""
        if on: self.app.voice.speak(str(idx), self.app.lang)


class KnoxCube(SequenceGame):
    n_symbols = 5
    def start_len(self): return 1 + self.level

    def make_pad(self):
        self.cubes = [ft.Container(width=62, height=62, bgcolor="#B07A45", border_radius=10,
                                   border=ft.Border.all(3, "#7A4F26"), ink=True,
                                   on_click=lambda e, i=i: self.tap(i)) for i in range(5)]
        # irregular positions like the real Knox cube tapping board
        offs = [10, 70, 0, 80, 30]
        stack = ft.Stack([ft.Container(c, left=i * 66, top=offs[i]) for i, c in enumerate(self.cubes)],
                         width=340, height=160)
        return ft.Container(stack, padding=ft.Padding.only(top=20))

    async def flash(self, idx, on):
        self.cubes[idx].bgcolor = theme.GOLD if on else "#B07A45"
