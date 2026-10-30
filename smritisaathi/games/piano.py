import asyncio, random
import flet as ft
from games.base import Game
from core import theme

LANES, LW, H, TH = 4, 84, 360, 90


class PianoTiles(Game):
    def build(self):
        self.total = 8 + 4 * self.level
        self.speed = 5 + 2 * self.level      # px per 50 ms tick
        self.tiles, self.spawned, self.hits, self.wrong = [], 0, 0, 0
        bg = [ft.Container(left=i * LW, top=0, width=LW, height=H, bgcolor="#FFFFFF" if i % 2 else "#FBEFD9",
                           border=ft.Border.only(right=ft.BorderSide(1, theme.SOFT))) for i in range(LANES)]
        self.field = ft.Stack(bg, width=LW * LANES, height=H, clip_behavior=ft.ClipBehavior.HARD_EDGE)
        self.info = ft.Text("", size=26, color=theme.INK)
        colors = [theme.SAFFRON, theme.TEAL, theme.GREEN, theme.MAROON]
        btns = [ft.Container(ft.Icon(ft.Icons.MUSIC_NOTE, color="white", size=36), width=LW - 4, height=84,
                             bgcolor=colors[i], border_radius=18, alignment=ft.Alignment.CENTER, ink=True,
                             on_click=lambda e, i=i: self.press(i)) for i in range(LANES)]
        return ft.Column([self.info, ft.Container(self.field, border=ft.Border.all(2, theme.INK), border_radius=12),
                          ft.Row(btns, alignment=ft.MainAxisAlignment.CENTER, spacing=4)],
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)

    def start(self):
        self.app.page.run_task(self.loop)

    def press(self, lane):
        if not self.active or not self.tiles:
            return
        t = max(self.tiles, key=lambda x: x["y"])
        if t["lane"] == lane and t["y"] + TH >= H * 0.45:
            self.hits += 1
            self.field.controls.remove(t["ctl"]); self.tiles.remove(t)
        else:
            self.wrong += 1
        self._info()

    def _info(self):
        self.info.value = f"{self.hits} / {self.total}"

    async def loop(self):
        await asyncio.sleep(0.8)
        while self.active:
            if self.spawned < self.total and (not self.tiles or min(t["y"] for t in self.tiles) > TH * 1.7):
                lane = random.randrange(LANES)
                ctl = ft.Container(width=LW - 6, height=TH, bgcolor=theme.INK, border_radius=10,
                                   left=lane * LW + 3, top=-TH)
                self.field.controls.append(ctl)
                self.tiles.append({"lane": lane, "y": -TH, "ctl": ctl}); self.spawned += 1
            for t in list(self.tiles):
                t["y"] += self.speed; t["ctl"].top = t["y"]
                if t["y"] > H:
                    self.field.controls.remove(t["ctl"]); self.tiles.remove(t)
            self._info(); self.refresh()
            if self.spawned >= self.total and not self.tiles:
                break
            await asyncio.sleep(0.05)
        if self.active:
            self.finish(100 * self.hits / self.total - 4 * self.wrong)
