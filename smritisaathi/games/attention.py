"""Eysenck-style attention/concentration task (target cancellation). Placeholder mechanics —
confirm exact protocol with the clinical psychologists before validation."""
import random
import flet as ft
from games.base import Game
from core import theme

SYMS = ["●", "▲", "■", "◆"]


class FindStars(Game):
    def build(self):
        n = {1: 12, 2: 20, 3: 30}[self.level]
        targets = {1: 4, 2: 6, 3: 9}[self.level]
        star_at = set(random.sample(range(n), targets))
        self.targets, self.sel, self.cells, self.star_at = targets, set(), [], star_at
        for i in range(n):
            ch = "★" if i in star_at else random.choice(SYMS)
            self.cells.append(ft.Container(ft.Text(ch, size=44, color=theme.INK), bgcolor="white",
                                           border=ft.Border.all(2, theme.SOFT), border_radius=14,
                                           alignment=ft.Alignment.CENTER, ink=True,
                                           on_click=lambda e, i=i: self.toggle(i)))
        grid = ft.GridView(controls=self.cells, runs_count=4, spacing=10, run_spacing=10, expand=True)
        return ft.Column([ft.Container(grid, expand=True),
                          theme.big_button(self.t("done_btn"), on_click=lambda e: self.submit(),
                                           icon=ft.Icons.CHECK, color=theme.GREEN)], expand=True)

    def toggle(self, i):
        if i in self.sel: self.sel.remove(i)
        else: self.sel.add(i)
        self.cells[i].bgcolor = theme.GOLD if i in self.sel else "white"
        self.refresh()

    def submit(self):
        hits, false = len(self.sel & self.star_at), len(self.sel - self.star_at)
        self.finish(100 * max(0, hits - false) / self.targets, {"hits": hits, "false": false})
