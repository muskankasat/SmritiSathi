"""Caregiver / health-worker web dashboard (Flet web).
Run:  flet run --web caregiver/dashboard.py     (reads the same SQLite file for now; swap DataSource for FastAPI later)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from collections import defaultdict
from datetime import date, timedelta
import flet as ft
from config import DB_PATH
from core.db import DB
from games import DOMAINS

NAMES = {"memory": "Memory", "attention": "Attention", "language": "Language",
         "executive": "Executive function", "calculation": "Calculation", "visuospatial": "Visuospatial"}
INK, SAFFRON, TEAL, GREEN, RED, SOFT = "#2B2118", "#E07A2F", "#1F6F8B", "#2E7D4F", "#B3261E", "#F3E6D3"


class DataSource:
    """Single place that knows where data comes from. Replace with httpx calls to FastAPI in the backend phase."""
    def __init__(self): self.db = DB(DB_PATH)
    def patient(self): return self.db.patient()
    def results(self, days): return self.db.results_since(days)
    def reminders(self): return self.db.reminders_today()
    def compliance(self): return self.db.compliance(7)
    def add_reminder(self, kind, label, time): self.db.add_reminder(kind, label, time)


def daily_domain_scores(results, days=14):
    """-> {domain: [score or None per day, oldest..newest]}"""
    per = defaultdict(lambda: defaultdict(list))
    for r in results:
        for d in r["domains"]:
            per[d][r["played_at"][:10]].append(r["score"])
    today = date.today()
    out = {}
    for d in DOMAINS:
        series = []
        for i in range(days - 1, -1, -1):
            vals = per[d].get((today - timedelta(days=i)).isoformat())
            series.append(sum(vals) / len(vals) if vals else None)
        out[d] = series
    return out


def avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def spark(series, color):
    bars = [ft.Container(width=14, height=max(4, (v or 0) * 0.5), bgcolor=color if v is not None else "#E5E5E5",
                         border_radius=3, tooltip=f"{v:.0f}" if v is not None else "no data") for v in series[-14:]]
    return ft.Row(bars, spacing=3, vertical_alignment=ft.CrossAxisAlignment.END, height=52)


def card(content, width=None, bg="white"):
    return ft.Container(content, bgcolor=bg, border_radius=16, padding=18, width=width,
                        border=ft.Border.all(1, SOFT))


def build(page: ft.Page, ds: DataSource):
    page.title, page.bgcolor, page.scroll = "SmritiSaathi — Caregiver Dashboard", "#FFF8EE", ft.ScrollMode.AUTO
    page.padding = 24
    P = ds.patient()
    res = ds.results(14)
    series = daily_domain_scores(res)
    alerts = []

    # ---- six-domain trend cards
    cards = []
    for d in DOMAINS:
        s = series[d]; cur, prev = avg(s[7:]), avg(s[:7])
        if cur is None:
            body = ft.Text("No data this week", color="#777")
            delta = ft.Text("")
        else:
            diff = None if prev is None else cur - prev
            col = GREEN if diff is None or diff >= -3 else RED
            delta = ft.Text("" if diff is None else f"{'▲' if diff >= 0 else '▼'} {abs(diff):.0f} vs last week",
                            color=col, size=14)
            body = ft.Text(f"{cur:.0f}", size=38, weight=ft.FontWeight.BOLD, color=INK)
            if diff is not None and diff <= -10:
                alerts.append(f"{NAMES[d]} fell {abs(diff):.0f} points this week — consider a clinical review.")
        cards.append(card(ft.Column([ft.Text(NAMES[d], weight=ft.FontWeight.BOLD, color=TEAL), body, delta,
                                     spark(s, TEAL)], spacing=4), width=260))

    # ---- activity (sessions per day)
    counts = defaultdict(int)
    for r in res: counts[r["played_at"][:10]] += 1
    days = [(date.today() - timedelta(days=i)) for i in range(13, -1, -1)]
    act = ft.Row([ft.Column([ft.Container(width=26, height=max(4, counts[d.isoformat()] * 14),
                                          bgcolor=SAFFRON if counts[d.isoformat()] else "#E5E5E5", border_radius=4),
                             ft.Text(d.strftime("%d"), size=11)], spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER) for d in days],
                 vertical_alignment=ft.CrossAxisAlignment.END, spacing=6, height=120)
    idle = 0
    for d in reversed(days):
        if counts[d.isoformat()] == 0 and d != date.today(): idle += 1
        else: break
    if idle >= 2: alerts.append(f"No activity for the last {idle} days.")

    # ---- reminders compliance
    done, expected = ds.compliance()
    pct = 100 * done / expected if expected else 0
    if expected and pct < 70: alerts.append(f"Reminder compliance is {pct:.0f}% over the last 7 days.")
    todays = ft.Column([ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE if r["done_at"] else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                        color=GREEN if r["done_at"] else "#999"),
                                ft.Text(f'{r["time"]}  {r["label"]}')]) for r in ds.reminders()])

    kind = ft.Dropdown(label="Type", width=160, value="med", options=[ft.DropdownOption(k, v) for k, v in
                       [("med", "Medicine"), ("water", "Hydration"), ("activity", "Activity"), ("appt", "Appointment")]])
    label = ft.TextField(label="Label", width=240)
    time = ft.TextField(label="Time (HH:MM)", width=140, value="09:00")
    msg = ft.Text("")

    def add(e):
        if not label.value or len(time.value) != 5:
            msg.value, msg.color = "Enter a label and time as HH:MM", RED
        else:
            ds.add_reminder(kind.value, label.value, time.value)
            page.controls.clear(); build(page, ds); return
        page.update()

    recent = ft.Column([ft.Text(f'{r["played_at"][5:16].replace("T", " ")}   {r["game"]}   L{r["level"]}   score {r["score"]}',
                                size=14) for r in reversed(res[-12:])])

    alert_box = card(ft.Column([ft.Row([ft.Icon(ft.Icons.WARNING_AMBER, color=RED), ft.Text(a, color=RED)])
                                for a in alerts]), bg="#FDECEA") if alerts else \
        card(ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=GREEN), ft.Text("No alerts — things look steady.")]),
             bg="#EEF8F0")

    page.add(
        ft.Row([ft.Icon(ft.Icons.PSYCHOLOGY_ALT, size=40, color=SAFFRON),
                ft.Column([ft.Text("SmritiSaathi — Caregiver Dashboard", size=28, weight=ft.FontWeight.BOLD, color=INK),
                           ft.Text(f"Patient: {P['name']}   •   Cognitive engagement aid, not a diagnostic tool.",
                                   size=13, color="#666")], spacing=0)]),
        alert_box,
        ft.Text("Six-domain trends (last 14 days, avg score)", size=20, weight=ft.FontWeight.BOLD, color=INK),
        ft.Row(cards, wrap=True, spacing=14, run_spacing=14),
        ft.Row([card(ft.Column([ft.Text("Daily activity (sessions)", weight=ft.FontWeight.BOLD), act]), width=520),
                card(ft.Column([ft.Text("Reminder compliance (7 days)", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{pct:.0f}%", size=40, weight=ft.FontWeight.BOLD,
                                        color=GREEN if pct >= 70 else RED), ft.Text("Today"), todays]), width=360)],
               wrap=True, spacing=14, run_spacing=14, vertical_alignment=ft.CrossAxisAlignment.START),
        card(ft.Column([ft.Text("Add a reminder", weight=ft.FontWeight.BOLD),
                        ft.Row([kind, label, time, ft.Button("Add", on_click=add)], wrap=True), msg])),
        card(ft.Column([ft.Text("Recent sessions", weight=ft.FontWeight.BOLD), recent])),
    )


def main(page: ft.Page):
    build(page, DataSource())


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)
