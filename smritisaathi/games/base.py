import flet as ft


class Game:
    """Every game: build() -> control, start() after mounting, dispose() on leaving, finish(score)."""

    def __init__(self, app, level, on_done, **opts):
        self.app, self.level, self.on_done, self.opts = app, level, on_done, opts
        self.active = True
        self.finished = False

    def t(self, key, **kw):
        return self.app.t(key, **kw)

    def refresh(self):
        if self.active:
            self.app.page.update()

    def build(self) -> ft.Control:
        raise NotImplementedError

    def start(self):
        pass

    def dispose(self):
        self.active = False

    def finish(self, score, detail=None):
        if self.finished:
            return
        self.finished = True
        self.active = False
        self.on_done(max(0, min(100, int(round(score)))), detail or {})
