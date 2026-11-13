"""Writes the arranko.app pages: one shared header and footer, one body per page.
Change a text in _src/bodies/<page>.html, then run from the repository root:
    python3 _src/build.py
and commit the regenerated pages. (_src/ is not published: Jekyll skips it.)"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent
BODIES = pathlib.Path(__file__).parent / "bodies"
DRAFT = True  # banner until the founder approves the texts (ARR-32)
UPDATED = "13 November 2026"

LOGO = ('<svg viewBox="34 46 134 116" aria-hidden="true" focusable="false"><g transform="skewX(-12) translate(22 0)" fill="#DBFF00">'
        '<rect x="48" y="95" width="24" height="65" rx="11"/><rect x="78" y="138" width="44" height="22" rx="11"/>'
        '<rect x="78" y="95" width="44" height="22" rx="11"/><rect x="60" y="48" width="94" height="22" rx="11"/>'
        '<rect x="130" y="48" width="24" height="112" rx="11"/></g></svg>')

PAGES = [
    # file, lang, <title>, description, nav key
    ("index.html", "es", "arranko · Calorías y macros en una foto",
     "Haz una foto y conoce al instante las calorías y macros de lo que comes.", None),
    ("privacy/index.html", "en", "Privacy Policy · arranko",
     "What arranko keeps, why, who helps us run it, and how to see, export or delete your data.", "privacy"),
    ("terms/index.html", "en", "Terms of Use · arranko", "The rules for using arranko.", "terms"),
    ("support/index.html", "en", "Support · arranko", "Get help with arranko.", "support"),
    ("delete-account/index.html", "en", "Delete your account · arranko",
     "How to delete your arranko account and everything in it, with or without the app.", "delete"),
    ("404.html", "en", "Page not found · arranko", "This page doesn't exist.", None),
]
NAV = [("privacy", "/privacy/", "Privacy"), ("terms", "/terms/", "Terms"),
       ("support", "/support/", "Support"), ("delete", "/delete-account/", "Delete account")]


def nav(current):
    current_attr = ' aria-current="page"'
    return "".join(
        '<a href="%s"%s>%s</a>' % (href, current_attr if key == current else "", label)
        for key, href, label in NAV)


for file, lang, title, desc, key in PAGES:
    body = (BODIES / file.replace("/index.html", ".html")).read_text().replace("{{UPDATED}}", UPDATED)
    banner = ('<div class="draft">Draft: these texts are waiting for approval.</div>'
              if DRAFT and file != "index.html" else "")
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0C0F0A">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
</head>
<body>
{banner}
<div class="wrap">
<header class="top">
<a class="brand" href="/" aria-label="arranko, home">{LOGO}<span>arranko</span></a>
<nav aria-label="Pages">{nav(key)}</nav>
</header>
<main>
{body.strip()}
</main>
<footer>
<nav aria-label="Legal">{nav(None)}</nav>
<p>arranko · <a href="mailto:support@arranko.app">support@arranko.app</a></p>
</footer>
</div>
</body>
</html>
"""
    path = OUT / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print("wrote", path)
