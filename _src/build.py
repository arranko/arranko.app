"""Writes the arranko.app pages: one shared header, footer and page head, one body per page.
Change a text in _src/bodies/<page>.html (or a page's title/lead below), then run from the
repository root:
    python3 _src/build.py
and commit the regenerated pages. (_src/ is not published: Jekyll skips it.)"""
import html as htmllib
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent.parent
BODIES = pathlib.Path(__file__).parent / "bodies"
DRAFT = True  # "waiting for approval" banner until the founder approves the texts (ARR-32)
UPDATED = "13 November 2026"

ISO = ('<g transform="skewX(-12) translate(22 0)" fill="#DBFF00">'
       '<rect class="c1" x="48" y="95" width="24" height="65" rx="11"/><rect class="c2" x="78" y="138" width="44" height="22" rx="11"/>'
       '<rect class="c3" x="78" y="95" width="44" height="22" rx="11"/><rect class="c4" x="60" y="48" width="94" height="22" rx="11"/>'
       '<rect class="c5" x="130" y="48" width="24" height="112" rx="11"/></g>')
LOGO = '<svg viewBox="34 46 134 116" aria-hidden="true" focusable="false">%s</svg>' % ISO

# file, lang, <title>, description, nav key, page head (eyebrow, h1, lead, show date), table of contents
PAGES = [
    ("index.html", "es", "arranko · Calorías y macros en una foto",
     "Haz una foto y conoce al instante las calorías y macros de lo que comes.", None, None, False),
    ("privacy/index.html", "en", "Privacy Policy · arranko",
     "What arranko keeps, why, who helps us run it, and how to see, export or delete your data.", "privacy",
     ("Legal", "Privacy Policy",
      "arranko helps you log what you eat and see your calories and macros. To do that it keeps some personal data, "
      "including data about your body. Here is what we keep, why, who helps us, and how you stay in control.", True), True),
    ("terms/index.html", "en", "Terms of Use · arranko", "The rules for using arranko.", "terms",
     ("Legal", "Terms of Use",
      "The rules for using arranko. By creating an account you agree to them and to our Privacy Policy.", True), True),
    ("support/index.html", "en", "Support · arranko", "Get help with arranko.", "support",
     ("Help", "Support", "Something not working, or a question? We read every message.", False), False),
    ("delete-account/index.html", "en", "Delete your account · arranko",
     "How to delete your arranko account and everything in it, with or without the app.", "delete",
     ("Your data", "Delete your account",
      "You can delete your arranko account and everything in it at any time, in the app or by email.", False), False),
    ("404.html", "en", "Page not found · arranko", "This page doesn't exist.", None,
     ("404", "Page not found", "This page doesn't exist.", False), False),
]
NAV = [("privacy", "/privacy/", "Privacy"), ("terms", "/terms/", "Terms"),
       ("support", "/support/", "Support"), ("delete", "/delete-account/", "Delete account")]


def nav(current):
    current_attr = ' aria-current="page"'
    return "".join(
        '<a href="%s"%s>%s</a>' % (href, current_attr if key == current else "", label)
        for key, href, label in NAV)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def with_toc(body):
    """Gives every <h2> an id and returns (body, table of contents)."""
    items = []

    def add_id(m):
        title = re.sub(r"<[^>]+>", "", m.group(1))
        items.append((slug(title), title))
        return '<h2 id="%s">%s</h2>' % (slug(title), m.group(1))

    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)
    toc = ('<nav class="toc" aria-label="On this page"><p>On this page</p><ol>%s</ol></nav>'
           % "".join('<li><a href="#%s">%s</a></li>' % (s, t) for s, t in items))
    return body, toc


SPLASH = """<div class="splash" id="splash" aria-hidden="true">
<div class="splash-mark"><svg viewBox="34 46 134 116" focusable="false">%s</svg><span>arranko</span></div>
</div>
<script>
/* Splash: once per visit, skipped when the person asked for less motion. */
(function () {
  var d = document.documentElement, seen = false;
  try { seen = sessionStorage.getItem("arranko-splash") === "1"; sessionStorage.setItem("arranko-splash", "1"); } catch (e) {}
  if (seen || window.matchMedia("(prefers-reduced-motion: reduce)").matches) d.classList.add("no-splash");
  else d.classList.add("splashing");
})();
</script>""" % ISO

for file, lang, title, desc, key, head, toc in PAGES:
    body = (BODIES / file.replace("/index.html", ".html")).read_text().replace("{{UPDATED}}", UPDATED).strip()
    banner = ('<div class="draft">Draft: these texts are waiting for approval.</div>'
              if DRAFT and file not in ("index.html", "404.html") else "")
    is_home = file == "index.html"
    if head:
        eyebrow, h1, lead, dated = head
        head_html = ('<section class="page-head"><p class="eyebrow">%s</p><h1 class="display">%s</h1>'
                     '<p class="lead">%s</p>%s</section>' % (
                         eyebrow, h1, htmllib.escape(lead, quote=False),
                         '<p class="meta">Last updated: %s</p>' % UPDATED if dated else ""))
        if toc:
            body, toc_html = with_toc(body)
            main = '%s<div class="doc">%s<article class="prose">%s</article></div>' % (head_html, toc_html, body)
        else:
            main = '%s<div class="doc single"><article class="prose">%s</article></div>' % (head_html, body)
    else:
        main = body
    body_class = ' class="home"' if is_home else ''
    splash = SPLASH if is_home else ''
    page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0C0F0A">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://arranko.app/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
<script>
/* Motion only when the script can run it; if motion.js never starts, show everything. */
(function () {{
  var d = document.documentElement;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
  d.classList.add("motion");
  setTimeout(function () {{ if (!d.classList.contains("motion-ready")) d.classList.remove("motion"); }}, 2500);
}})();
</script>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/motion.css">
</head>
<body{body_class}>
{splash}
{banner}
<div class="wrap">
<header class="top">
<a class="brand" href="/" aria-label="arranko, home"><span class="tile">{LOGO}</span><span>arranko</span></a>
<nav aria-label="Pages">{nav(key)}</nav>
</header>
<main>
{main}
</main>
<footer>
<p>© 2026 arranko · <a href="mailto:support@arranko.app">support@arranko.app</a></p>
<nav aria-label="Legal">{nav(None)}</nav>
</footer>
</div>
<script src="/motion.js" defer></script>
</body>
</html>
"""
    path = OUT / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page)
    print("wrote", path)
