import flet as ft
from core import theme
from core.i18n import LANGS
from games import REGISTRY


def stars(score):
    n = 3 if score >= 80 else 2 if score >= 50 else 1
    return ft.Row([ft.Icon(ft.Icons.STAR if i < n else ft.Icons.STAR_BORDER, size=64, color=theme.GOLD)
                   for i in range(3)], alignment=ft.MainAxisAlignment.CENTER)


def shell(app, title, body, back=True, mic=True):
    left = [ft.IconButton(ft.Icons.ARROW_BACK, icon_size=40, on_click=lambda e: app.home(),
                          tooltip=app.t("back"))] if back else []
    right = [ft.IconButton(ft.Icons.MIC, icon_size=40, icon_color="white", bgcolor=theme.TEAL,
                           on_click=lambda e: app.open_voice(), tooltip=app.t("speak"))] if mic else []
    header = ft.Row(left + [ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=theme.INK, expand=True)] + right,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER)
    return ft.SafeArea(ft.Container(ft.Column([header, ft.Container(body, expand=True)], expand=True, spacing=10),
                                    padding=16, bgcolor=theme.BG, expand=True), expand=True)


def language_screen(app):
    btns = [theme.big_button(name, on_click=lambda e, c=code: app.set_lang(c), height=96, text_size=36,
                             color=[theme.SAFFRON, theme.TEAL, theme.GREEN][i], width=320)
            for i, (code, name) in enumerate(LANGS.items())]
    body = ft.Column([ft.Icon(ft.Icons.PSYCHOLOGY_ALT, size=96, color=theme.SAFFRON),
                      ft.Text("SmritiSaathi  •  स्मृतिसाथी", size=36, weight=ft.FontWeight.BOLD, color=theme.INK,
                              text_align=ft.TextAlign.CENTER),
                      ft.Text("भाषा  /  भाषा  /  Language", size=26, color=theme.INK)] + btns,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
                    spacing=22, scroll=ft.ScrollMode.AUTO)
    return ft.SafeArea(ft.Container(body, expand=True, padding=20, bgcolor=theme.BG), expand=True)


def home_screen(app):
    pending = sum(1 for r in app.db.reminders_today() if not r["done_at"])
    done = app.db.daily_done_today()
    body = ft.Column([
        ft.Text(app.t("hello", name=app.patient["name"]), size=40, weight=ft.FontWeight.BOLD, color=theme.SAFFRON),
        theme.tile(app.t("home_daily"), ft.Icons.WB_SUNNY, theme.SAFFRON, lambda e: app.start_daily(),
                   subtitle=app.t("daily_done_today") if done else app.t("daily_intro"), height=150),
        theme.tile(app.t("home_games"), ft.Icons.EXTENSION, theme.TEAL, lambda e: app.games_menu()),
        theme.tile(app.t("home_reminders"), ft.Icons.ALARM, theme.GREEN, lambda e: app.reminders(),
                   subtitle=app.t("pending", n=pending) if pending else None, badge=pending or None),
        ft.Row([theme.big_button(app.t("speak"), icon=ft.Icons.MIC, on_click=lambda e: app.open_voice(),
                                 color=theme.MAROON, width=200, height=70),
                ft.TextButton(content=ft.Text("हिन्दी / मराठी / English", size=22),
                              on_click=lambda e: app.go(language_screen(app)))],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    ], spacing=18, scroll=ft.ScrollMode.AUTO)
    return shell(app, app.t("app_name"), body, back=False, mic=False)


def games_screen(app):
    tiles = []
    for gid, m in REGISTRY.items():
        if m["ready"]:
            tiles.append(theme.tile(app.t(m["title"]), m["icon"], m["color"],
                                    lambda e, g=gid: app.start_game(g),
                                    subtitle=app.t("level", n=app.engine.level_for(gid)), height=104))
        else:
            tiles.append(theme.tile(app.t(m["title"]), m["icon"], m["color"], None,
                                    subtitle=app.t("coming_soon"), height=104))
    return shell(app, app.t("games_title"), ft.Column(tiles, spacing=14, scroll=ft.ScrollMode.AUTO))


def intro_screen(app, gid, level, step, on_start):
    m = REGISTRY[gid]
    body = ft.Column([
        ft.Icon(m["icon"], size=110, color=m["color"]),
        ft.Text(app.t(m["instr"]), size=34, text_align=ft.TextAlign.CENTER, color=theme.INK),
        ft.Text(app.t("level", n=level), size=24, color=theme.INK),
        theme.big_button(app.t("start"), on_click=lambda e: on_start(), icon=ft.Icons.PLAY_ARROW,
                         color=theme.GREEN, width=300, height=90, text_size=34),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, spacing=26)
    title = step or app.t(m["title"])
    return shell(app, title, body)


def game_screen(app, gid, game):
    return shell(app, app.t(REGISTRY[gid]["title"]), game.build())


def result_screen(app, gid, score, next_label, on_next):
    msg = app.t("well_done") if score >= 50 else app.t("nice_try")
    app.voice.speak(msg, app.lang)
    body = ft.Column([stars(score), ft.Text(msg, size=40, weight=ft.FontWeight.BOLD, color=theme.GREEN,
                                            text_align=ft.TextAlign.CENTER),
                      theme.big_button(next_label, on_click=lambda e: on_next(), width=300, height=84),
                      theme.big_button(app.t("home"), on_click=lambda e: app.home(), color=theme.TEAL,
                                       icon=ft.Icons.HOME, width=300, height=84)],
                     horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
                     spacing=26)
    return shell(app, app.t(REGISTRY[gid]["title"]), body)


def daily_summary_screen(app):
    avg = sum(s for _, s in app.session_scores) / max(1, len(app.session_scores))
    app.voice.speak(app.t("daily_finished"), app.lang)
    body = ft.Column([stars(avg), ft.Text(app.t("daily_finished"), size=38, weight=ft.FontWeight.BOLD,
                                          color=theme.GREEN, text_align=ft.TextAlign.CENTER),
                      theme.big_button(app.t("home"), on_click=lambda e: app.home(), icon=ft.Icons.HOME,
                                       width=300, height=84)],
                     horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
                     spacing=26)
    return shell(app, app.t("home_daily"), body)


KIND = {"med": (ft.Icons.MEDICATION, "r_med"), "water": (ft.Icons.WATER_DROP, "r_water"),
        "activity": (ft.Icons.DIRECTIONS_WALK, "r_activity"), "appt": (ft.Icons.LOCAL_HOSPITAL, "r_appt")}


def reminders_screen(app):
    def mark(rid):
        app.db.mark_reminder_done(rid); app.reminders()
    items = []
    todo = [r for r in app.db.reminders_today() if not r["done_at"]]
    if todo:
        app.voice.speak(app.t(KIND.get(todo[0]["kind"], (None, "r_activity"))[1]), app.lang)
    for r in app.db.reminders_today():
        icon, key = KIND.get(r["kind"], (ft.Icons.ALARM, "r_activity"))
        done = bool(r["done_at"])
        action = ft.Icon(ft.Icons.CHECK_CIRCLE, size=56, color=theme.GREEN) if done else \
            theme.big_button(app.t("mark_done"), on_click=lambda e, i=r["id"]: mark(i), color=theme.GREEN,
                             height=64, text_size=22)
        items.append(theme.card(ft.Row([ft.Icon(icon, size=48, color=theme.SAFFRON),
                                        ft.Column([ft.Text(f'{r["time"]}  {app.t(key)}', size=26,
                                                           weight=ft.FontWeight.BOLD, color=theme.INK),
                                                   ft.Text(r["label"], size=20, color=theme.INK)],
                                                  spacing=2, expand=True), action],
                                       vertical_alignment=ft.CrossAxisAlignment.CENTER), bgcolor="#F2FBF4" if done else theme.CARD))
    if not items:
        items = [ft.Text(app.t("no_reminders"), size=28)]
    return shell(app, app.t("r_title"), ft.Column(items, spacing=14, scroll=ft.ScrollMode.AUTO))


def voice_dialog(app):
    """Voice navigation: tap the mic, speak (e.g. 'khel' / 'खेळ' / 'games'), the app routes.
    Uses the phone's recogniser via flet-stt; the text box is the fallback (desktop, no permission, noisy room)."""
    from core.voice import parse_intent
    heard = ft.Text("", size=24, color=theme.TEAL)
    status = ft.Text(app.t("voice_hint"), size=22)
    field = ft.TextField(hint_text=app.t("voice_hint"), text_size=26)
    mic_icon = ft.Icon(ft.Icons.MIC, size=72, color="white")
    mic = ft.Container(mic_icon, width=120, height=120, border_radius=60, bgcolor=theme.TEAL,
                       alignment=ft.Alignment.CENTER, ink=True)

    def go(cands):
        intent = parse_intent(cands)
        if intent:
            app.page.pop_dialog(); app.route(intent)
            return True
        return False

    async def listen(e=None):
        mic.bgcolor = theme.MAROON
        status.value, heard.value = app.t("listening"), ""
        app.page.update()
        cands = await app.voice.listen(app.lang)
        mic.bgcolor = theme.TEAL
        if cands:
            heard.value = cands[0]
            if go(cands):
                return
            status.value = app.t("voice_unknown")
        else:
            status.value = app.t("say_again") if app.voice.has_stt else app.t("voice_type")
        app.page.update()

    def typed(e=None):
        if not go(field.value):
            status.value = app.t("voice_unknown"); app.page.update()

    mic.on_click = listen
    field.on_submit = typed
    app.page.show_dialog(ft.AlertDialog(
        title=ft.Text(app.t("voice_title"), size=30),
        content=ft.Column([ft.Row([mic], alignment=ft.MainAxisAlignment.CENTER), status, heard, field],
                          tight=True, spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[ft.TextButton(content=ft.Text(app.t("close"), size=22), on_click=lambda e: app.page.pop_dialog()),
                 ft.Button(content=ft.Text(app.t("go"), size=24), on_click=typed)]))
    if app.voice.has_stt:
        app.page.run_task(listen)       # start listening immediately, no extra tap needed
