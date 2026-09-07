import shutil
import uuid
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.core.config import TEMPLATES_DIR, GENERATED_DIR, MEDIA_DIR, LANGS, DIR_MAP, TEMPLATES, DEFAULT_TEMPLATE
from app.services.i18n import I18N
from app.models.models import Cooperative

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _template_meta(coop: Cooperative) -> dict:
    return TEMPLATES.get(coop.template_id or DEFAULT_TEMPLATE, TEMPLATES[DEFAULT_TEMPLATE])


def _t(field, lang, default=""):
    """Safely pull one language out of a {fr,en,ar} JSON field."""
    if not field:
        return default
    return field.get(lang, default)


def _copy_asset(src_path: str, dest_assets_dir: Path, subfolder: str) -> str:
    """Copy a media file into the build's assets folder, return the relative
    path to reference from a /lang/index.html file (one level down)."""
    if not src_path:
        return None
    src = MEDIA_DIR / src_path
    if not src.exists():
        return None
    dest_dir = dest_assets_dir / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / src.name
    shutil.copy(src, dest_file)
    return f"../assets/{subfolder}/{src.name}"


def build_context(coop: Cooperative, lang: str, assets_dir: Path | None, asset_prefix: str) -> dict:
    i18n = I18N[lang]

    products = []
    for p in coop.products:
        image_url = None
        if p.image_path and assets_dir is not None:
            image_url = _copy_asset(p.image_path, assets_dir, "products")
        products.append({
            "name": _t(p.name, lang),
            "description": _t(p.description, lang),
            "price": _t(p.price, lang),
            "image_url": image_url,
        })

    gallery = []
    for m in coop.media:
        if m.type != "gallery":
            continue
        image_url = None
        if assets_dir is not None:
            image_url = _copy_asset(m.file_path, assets_dir, "gallery")
        gallery.append({"image_url": image_url, "alt": _t(m.alt_text, lang)})

    contact_items = []
    if coop.address:
        contact_items.append({"label": i18n["contact_label_address"], "value": coop.address})
    if coop.phone:
        contact_items.append({"label": i18n["contact_label_phone"], "value": coop.phone})
    if coop.whatsapp:
        contact_items.append({"label": i18n["contact_label_whatsapp"], "value": coop.whatsapp})
    if coop.email:
        contact_items.append({"label": i18n["contact_label_email"], "value": coop.email})

    footer_copy = f"© {2026} {_t(coop.name, lang)}. {i18n['footer_copy_suffix']}"

    return {
        "lang": lang,
        "dir": DIR_MAP[lang],
        "asset_prefix": asset_prefix,
        "i18n": i18n,
        "lang_switch": [
            {"code": l, "url": f"../{l}/index.html", "active": l == lang}
            for l in LANGS
        ],
        "coop": {
            "name": _t(coop.name, lang),
            "tagline_short": _t(coop.tagline_short, lang),
            "eyebrow": _t(coop.eyebrow, lang),
            "tagline": _t(coop.tagline, lang),
            "founded_year": coop.founded_year or "",
            "member_count": _t(coop.member_count_label, lang),
            "province": _t(coop.province, lang),
            "hero_photo_alt": _t(coop.hero_photo_alt, lang, _t(coop.name, lang)),
            "hero_caption": _t(coop.hero_caption, lang),
            "about_paragraphs": (coop.about_paragraphs or {}).get(lang, []),
            "facts": (coop.facts or {}).get(lang, []),
            "products": products,
            "gallery": gallery,
            "contact_intro": _t(coop.contact_intro, lang),
            "contact_items": contact_items,
            "social_links": coop.social_links or [],
        },
        "footer_copy": footer_copy,
    }


def render_preview(coop: Cooperative, lang: str) -> str:
    """Render a single language, referencing live /media/ paths (no zipping) —
    used for the in-app preview iframe."""
    meta = _template_meta(coop)
    template = _env.get_template(meta["file"])
    ctx = build_context(coop, lang, assets_dir=None, asset_prefix="/")
    # preview uses live media URLs, not copied assets
    for p, orm_p in zip(ctx["coop"]["products"], coop.products):
        p["image_url"] = f"/media/{orm_p.image_path}" if orm_p.image_path else None
    gallery_media = [m for m in coop.media if m.type == "gallery"]
    for g, orm_m in zip(ctx["coop"]["gallery"], gallery_media):
        g["image_url"] = f"/media/{orm_m.file_path}"
    ctx["footer_copy"] = ctx["footer_copy"]
    html = template.render(**ctx)
    # point stylesheet at the live static mount instead of a relative ../<stylesheet>
    html = html.replace(f'href="../{meta["stylesheet"]}"', f'href="/static/{meta["stylesheet"]}"')
    return html


def generate_site(coop: Cooperative) -> Path:
    """Render fr/en/ar + copy assets + zip. Returns path to the zip file."""
    build_id = uuid.uuid4().hex[:8]
    build_dir = GENERATED_DIR / f"{coop.slug}-{build_id}"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    assets_dir = build_dir / "assets"
    meta = _template_meta(coop)
    template = _env.get_template(meta["file"])
    shutil.copy(TEMPLATES_DIR / meta["stylesheet"], build_dir / meta["stylesheet"])

    for lang in LANGS:
        lang_dir = build_dir / lang
        lang_dir.mkdir(parents=True)
        ctx = build_context(coop, lang, assets_dir=assets_dir, asset_prefix="../")
        html = template.render(**ctx)
        (lang_dir / "index.html").write_text(html, encoding="utf-8")

    (build_dir / "index.html").write_text(
        '<!DOCTYPE html><meta http-equiv="refresh" content="0; url=ar/index.html">',
        encoding="utf-8",
    )

    zip_path = GENERATED_DIR / f"{coop.slug}-{build_id}"
    archive = shutil.make_archive(str(zip_path), "zip", root_dir=str(build_dir))
    shutil.rmtree(build_dir)
    return Path(archive)