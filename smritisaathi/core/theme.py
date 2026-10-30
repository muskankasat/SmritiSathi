"""Elderly-friendly design tokens: warm palette, very large text and touch targets."""
import flet as ft

BG = "#FFF8EE"
INK = "#2B2118"
SAFFRON = "#E07A2F"
TEAL = "#1F6F8B"
GREEN = "#2E7D4F"
MAROON = "#9C3D54"
CARD = "#FFFFFF"
SOFT = "#F3E6D3"
GOLD = "#F2B705"

TEXT_L = 28
TEXT_XL = 40


def label(text, size=TEXT_L, color=INK, bold=False, align=ft.TextAlign.CENTER):
    return ft.Text(text, size=size, color=color, text_align=align,
                   weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL)


def big_button(text, on_click=None, icon=None, color=SAFFRON, width=None, height=76, text_size=26):
    return ft.Button(
        content=ft.Text(text, size=text_size, weight=ft.FontWeight.BOLD, color="white"),
        icon=icon, on_click=on_click, width=width, height=height,
        style=ft.ButtonStyle(bgcolor=color, color="white",
                             shape=ft.RoundedRectangleBorder(radius=22), icon_size=34),
    )


def tile(text, icon, color, on_click, subtitle=None, height=130, badge=None):
    """Large tappable home/menu tile."""
    texts = [ft.Text(text, size=30, weight=ft.FontWeight.BOLD, color="white")]
    if subtitle:
        texts.append(ft.Text(subtitle, size=20, color="white"))
    row = [ft.Icon(icon, size=56, color="white"), ft.Column(texts, spacing=2, expand=True)]
    if badge:
        row.append(ft.Container(ft.Text(str(badge), size=24, weight=ft.FontWeight.BOLD, color=color),
                                bgcolor="white", border_radius=30, width=52, height=52,
                                alignment=ft.Alignment.CENTER))
    return ft.Container(ft.Row(row, spacing=18, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=color, border_radius=26, padding=22, height=height,
                        on_click=on_click, ink=True)


def card(content, padding=20, bgcolor=CARD):
    return ft.Container(content, bgcolor=bgcolor, border_radius=24, padding=padding,
                        border=ft.Border.all(1, SOFT))
