"""SmritiSaathi patient app (Flet).  Run:  flet run main.py   |   Android: flet build apk"""
import flet as ft
from app import App


def main(page: ft.Page):
    App(page).start()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")   # assets/audio/<lang>/*.mp3 = pre-generated spoken prompts
