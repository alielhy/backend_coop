from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR / 'coop_generator.db'}"

MEDIA_DIR = BASE_DIR / "media"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
GENERATED_DIR = BASE_DIR / "generated"  # temp per-request build output before zipping

LANGS = ["ar", "fr", "en"]
DIR_MAP = {"fr": "ltr", "en": "ltr", "ar": "rtl"}

TEMPLATES = {
    "classic": {"file": "index.html.j2", "stylesheet": "style.css"},
    "market":  {"file": "market.html.j2", "stylesheet": "market-style.css"},
    "story":   {"file": "story.html.j2", "stylesheet": "story-style.css"},
}
DEFAULT_TEMPLATE = "classic"

MEDIA_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)