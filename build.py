#!/usr/bin/env python3
"""
build.py — genera el sitio estático a partir de /posts (Markdown + front matter)
y las plantillas Jinja2 en /templates.

Uso:
    python3 build.py            # construye el sitio en /site
    python3 build.py --serve    # construye y levanta un servidor local en :8000
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
OUTPUT_DIR = ROOT / "site"

# Configuración global del sitio — edítalo a tu gusto
SITE = {
    "title": "0xBitácora",
    "handle": "0xbitacora",
    "author": "John",
    "description": "Writeups de CTF, notas de bug bounty e infraestructura, y herramientas de seguridad ofensiva.",
    "tagline": "Notas de campo sobre infraestructura, redes y seguridad ofensiva — CTF, bug bounty y las herramientas que uso en el camino.",
    "focus_areas": ["ctf", "bug bounty", "redes & vpn", "automatización", "cloud"],
    "contact_url": "https://github.com/",
    "year": datetime.now().year,
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL)

MD_EXTENSIONS = [
    "extra",          # tablas, listas de definición, etc.
    "codehilite",     # resaltado de sintaxis vía Pygments
    "toc",            # tabla de contenidos + anchors
    "sane_lists",
    "admonition",
]
MD_EXT_CONFIG = {
    "codehilite": {"css_class": "codehilite", "guess_lang": False},
    "toc": {"anchorlink": True},
}


def read_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"{path.name}: falta el front matter (bloque --- ... ---)")

    meta = yaml.safe_load(match.group(1)) or {}
    body_md = match.group(2)

    required = {"title", "date", "category", "summary"}
    missing = required - meta.keys()
    if missing:
        raise ValueError(f"{path.name}: faltan campos en el front matter: {missing}")

    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_EXT_CONFIG)
    html = md.convert(body_md)
    toc = md.toc if getattr(md, "toc", "").strip().count("<li>") > 1 else ""

    words = len(re.findall(r"\w+", body_md))
    read_time = max(1, round(words / 200))

    slug = meta.get("slug") or slugify(meta["title"])
    category = str(meta["category"]).strip()

    return {
        "title": meta["title"],
        "date": str(meta["date"]),
        "date_sort": str(meta["date"]),
        "category": category,
        "category_slug": slugify(category),
        "tags": meta.get("tags", []),
        "summary": meta["summary"],
        "author": meta.get("author", SITE["author"]),
        "slug": slug,
        "content": html,
        "toc": toc,
        "read_time": read_time,
    }


def load_posts() -> list:
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        try:
            posts.append(read_post(path))
        except ValueError as e:
            print(f"⚠️  Saltando {path.name}: {e}", file=sys.stderr)
    posts.sort(key=lambda p: p["date_sort"], reverse=True)
    return posts


def build():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=False)

    posts = load_posts()

    # index
    index_tpl = env.get_template("index.html")
    (OUTPUT_DIR / "index.html").write_text(
        index_tpl.render(site=SITE, posts=posts, base_url=""), encoding="utf-8"
    )

    # about
    about_tpl = env.get_template("about.html")
    (OUTPUT_DIR / "about.html").write_text(
        about_tpl.render(site=SITE, base_url=""), encoding="utf-8"
    )

    # posts
    (OUTPUT_DIR / "posts").mkdir(exist_ok=True)
    post_tpl = env.get_template("post.html")
    for post in posts:
        out_path = OUTPUT_DIR / "posts" / f"{post['slug']}.html"
        out_path.write_text(
            post_tpl.render(site=SITE, post=post, base_url="../"), encoding="utf-8"
        )

    print(f"✅ Sitio generado en {OUTPUT_DIR} ({len(posts)} posts)")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import http.server
        import functools
        import socketserver

        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=str(OUTPUT_DIR)
        )
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("Sirviendo en http://localhost:8000  (Ctrl+C para detener)")
            httpd.serve_forever()
