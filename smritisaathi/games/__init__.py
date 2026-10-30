"""Game registry. `domains` follows Section 3.1 of the report. ready=False games are placeholders."""
import flet as ft
from games.memory import MemoryCards
from games.sequence import DigitSpan, KnoxCube
from games.piano import PianoTiles
from games.quiz import ArrowSums, Recall
from games.attention import FindStars

I = ft.Icons
REGISTRY = {
 "memory":    dict(cls=MemoryCards, title="g_memory", instr="i_memory", icon=I.STYLE, color="#1F6F8B",
                   domains=["memory", "attention"], ready=True),
 "digit_f":   dict(cls=DigitSpan, opts={}, title="g_digit_f", instr="i_digit_f", icon=I.DIALPAD, color="#E07A2F",
                   domains=["memory", "attention"], ready=True),
 "digit_b":   dict(cls=DigitSpan, opts={"backward": True}, title="g_digit_b", instr="i_digit_b", icon=I.SWAP_HORIZ,
                   color="#9C3D54", domains=["memory", "attention", "executive"], ready=True),
 "knox":      dict(cls=KnoxCube, title="g_knox", instr="i_knox", icon=I.VIEW_IN_AR, color="#8A5A2B",
                   domains=["memory", "attention", "visuospatial"], ready=True),
 "piano":     dict(cls=PianoTiles, title="g_piano", instr="i_piano", icon=I.PIANO, color="#2E7D4F",
                   domains=["attention", "executive", "visuospatial"], ready=True),
 "arrows":    dict(cls=ArrowSums, title="g_arrows", instr="i_arrows", icon=I.EXPOSURE, color="#6A4C93",
                   domains=["executive", "calculation", "visuospatial"], ready=True),
 "attention": dict(cls=FindStars, title="g_attention", instr="i_attention", icon=I.STAR, color="#C99700",
                   domains=["attention", "executive"], ready=True),
 "recall":    dict(cls=Recall, title="g_recall", instr="i_recall", icon=I.PSYCHOLOGY, color="#1F6F8B",
                   domains=["memory", "language"], ready=True),
 "crossword": dict(cls=None, title="g_crossword", instr="", icon=I.GRID_ON, color="#999999",
                   domains=["visuospatial"], ready=False),
 "karaoke":   dict(cls=None, title="g_karaoke", instr="", icon=I.MIC, color="#999999",
                   domains=["memory", "language", "attention"], ready=False),
}
DAILY_BATTERY = ["digit_f", "digit_b", "knox", "attention", "recall"]   # hidden assessment battery (Sec. 3.2)
DOMAINS = ["memory", "attention", "language", "executive", "calculation", "visuospatial"]
