import asyncio, random
import flet as ft
from games.base import Game
from core import theme

PICS = ["🥭", "🪔", "🐄", "🛺", "☕", "🌸", "🥥", "🪁"]


class MemoryCards(Game):
    def build(self):
        pairs = {1: 3, 2: 4, 3: 6}[self.level]
        cols = 3 if pairs <= 4 else 4
        deck = random.sample(PICS, pairs) * 2
        random.shuffle(deck)
        self.deck, self.open, self.matched, self.moves, self.busy = deck, [], set(), 0, False
        self.cards = []
        for i, pic in enumerate(deck):
            self.cards.append(ft.Container(ft.Text("?", size=46, color="white", weight=ft.FontWeight.BOLD),
                                           bgcolor=theme.TEAL, border_radius=18, alignment=ft.Alignment.CENTER,
                                           on_click=self._handler(i), ink=True))
        self.pairs = pairs
        grid = ft.GridView(controls=self.cards, runs_count=cols, spacing=14, run_spacing=14,
                           child_aspect_ratio=1.0, expand=True)
        return ft.Container(grid, expand=True, padding=8)

    def _handler(self, i):
        async def h(e):
            await self.flip(i)
        return h

    def _show(self, i, face):
        c = self.cards[i]
        c.content = ft.Text(self.deck[i] if face else "?", size=56 if face else 46, color="white")
        c.bgcolor = "#FFFFFF" if face else theme.TEAL
        c.border = ft.Border.all(3, theme.SAFFRON) if face else None

    async def flip(self, i):
        if self.busy or i in self.open or i in self.matched or not self.active:
            return
        self._show(i, True); self.open.append(i); self.refresh()
        if len(self.open) == 2:
            self.moves += 1
            a, b = self.open
            if self.deck[a] == self.deck[b]:
                self.matched |= {a, b}
                for k in (a, b):
                    self.cards[k].bgcolor = "#D9F0DF"
                self.open = []
                self.refresh()
                if len(self.matched) == len(self.deck):
                    await asyncio.sleep(0.8)
                    self.finish(100 * self.pairs / max(self.moves, self.pairs))
            else:
                self.busy = True
                await asyncio.sleep(1.0)
                if self.active:
                    for k in (a, b):
                        self._show(k, False)
                    self.open, self.busy = [], False
                    self.refresh()
