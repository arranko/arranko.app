"""Writes the arranko.app pages, in Spanish (main) and English, with one shared header, footer
and page head. Change a text in _src/bodies/<lang>/<page>.html (or a page's title/lead below),
then run from the repository root:
    python3 _src/build.py
and commit the regenerated pages. (_src/ is not published: Jekyll skips it.)"""
import html as htmllib
import pathlib
import re
import unicodedata

OUT = pathlib.Path(__file__).resolve().parent.parent

def version(name):
    """A short fingerprint of a file, added to its address so browsers fetch it again when it changes."""
    import hashlib
    return hashlib.sha1((OUT / name).read_bytes()).hexdigest()[:8]

BODIES = pathlib.Path(__file__).parent / "bodies"
DRAFT = False  # True shows a "waiting for approval" banner on the legal pages (founder approved them 13 Nov, ARR-32)
UPDATED = {"es": "13 de noviembre de 2026", "en": "13 November 2026"}

ISO = ('<g transform="skewX(-12) translate(22 0)" fill="currentColor">'
       '<rect class="c1" x="48" y="95" width="24" height="65" rx="11"/><rect class="c2" x="78" y="138" width="44" height="22" rx="11"/>'
       '<rect class="c3" x="78" y="95" width="44" height="22" rx="11"/><rect class="c4" x="60" y="48" width="94" height="22" rx="11"/>'
       '<rect class="c5" x="130" y="48" width="24" height="112" rx="11"/></g>')
LOGO = '<svg viewBox="34 46 134 116" aria-hidden="true" focusable="false">%s</svg>' % ISO

# Each page exists in both languages: key -> {lang: (path, title, description, head, toc)}
# head = (eyebrow, h1, lead, show the date) or None for the home page.
PAGES = {
    "home": {
        "es": ("index.html", "arranko · Calorías y macros con IA en una foto",
               "La app de nutrición con inteligencia artificial: haz una foto y conoce al instante las calorías y macros de lo que comes.", None, False),
        "en": ("en/index.html", "arranko · Calories and macros with AI, from a photo",
               "The nutrition app with artificial intelligence: take a photo and see the calories and macros of what you eat in an instant.", None, False),
    },
    "privacy": {
        "es": ("privacidad/index.html", "Política de privacidad · arranko",
               "Qué guarda arranko, para qué, quién nos ayuda y cómo ver, exportar o borrar tus datos.",
               ("Legal", "Política de privacidad",
                "arranko te ayuda a registrar lo que comes y ver tus calorías y macros. Para eso guarda algunos datos "
                "personales, incluidos datos sobre tu cuerpo. Aquí está qué guardamos, para qué, quién nos ayuda y cómo "
                "mantienes el control.", True), True),
        "en": ("privacy/index.html", "Privacy Policy · arranko",
               "What arranko keeps, why, who helps us run it, and how to see, export or delete your data.",
               ("Legal", "Privacy Policy",
                "arranko helps you log what you eat and see your calories and macros. To do that it keeps some personal data, "
                "including data about your body. Here is what we keep, why, who helps us, and how you stay in control.", True), True),
    },
    "terms": {
        "es": ("terminos/index.html", "Términos de uso · arranko", "Las normas para usar arranko.",
               ("Legal", "Términos de uso",
                "Las normas para usar arranko. Al crear una cuenta las aceptas, junto con nuestra Política de privacidad.", True), True),
        "en": ("terms/index.html", "Terms of Use · arranko", "The rules for using arranko.",
               ("Legal", "Terms of Use",
                "The rules for using arranko. By creating an account you agree to them and to our Privacy Policy.", True), True),
    },
    "support": {
        "es": ("ayuda/index.html", "Ayuda · arranko", "Consigue ayuda con arranko.",
               ("Ayuda", "Ayuda", "¿Algo no funciona o tienes una pregunta? Leemos todos los mensajes.", False), False),
        "en": ("support/index.html", "Support · arranko", "Get help with arranko.",
               ("Help", "Support", "Something not working, or a question? We read every message.", False), False),
    },
    "delete": {
        "es": ("borrar-cuenta/index.html", "Borrar tu cuenta · arranko",
               "Cómo borrar tu cuenta de arranko y todo lo que contiene, con o sin la app.",
               ("Tus datos", "Borrar tu cuenta",
                "Puedes borrar tu cuenta de arranko y todo lo que contiene cuando quieras, en la app o por correo.", False), False),
        "en": ("delete-account/index.html", "Delete your account · arranko",
               "How to delete your arranko account and everything in it, with or without the app.",
               ("Your data", "Delete your account",
                "You can delete your arranko account and everything in it at any time, in the app or by email.", False), False),
    },
    "404": {
        "es": ("404.html", "Página no encontrada · arranko", "Esta página no existe.",
               ("404", "Página no encontrada", "Esta página no existe. / This page doesn't exist.", False), False),
    },
}
BODY_FILE = {"home": "index", "privacy": {"es": "privacidad", "en": "privacy"}, "terms": {"es": "terminos", "en": "terms"},
             "support": {"es": "ayuda", "en": "support"}, "delete": {"es": "borrar-cuenta", "en": "delete-account"}, "404": "404"}

T = {
    "es": {"legal": [("privacy", "Política de privacidad"), ("terms", "Términos de uso"), ("support", "Ayuda"), ("delete", "Borrar tu cuenta")],
           "menu": [("#como-funciona", "Cómo funciona"), ("#funciones", "Funciones"), ("#preguntas", "Preguntas")],
           "cta": "Síguenos", "draft": "Borrador: estos textos esperan aprobación.", "toc": "En esta página",
           "updated": "Última actualización", "theme": "Cambiar entre modo claro y oscuro", "other": "EN",
           "other_label": "English", "home": "arranko, inicio", "menu_label": "Menú",
           "tag": "La app de nutrición con IA: calorías y macros en una foto."},
    "en": {"legal": [("privacy", "Privacy Policy"), ("terms", "Terms of Use"), ("support", "Support"), ("delete", "Delete your account")],
           "menu": [("#how-it-works", "How it works"), ("#features", "Features"), ("#faq", "Questions")],
           "cta": "Follow us", "draft": "Draft: these texts are waiting for approval.", "toc": "On this page",
           "updated": "Last updated", "theme": "Switch between light and dark mode", "other": "ES",
           "other_label": "Español", "home": "arranko, home", "menu_label": "Menu",
           "tag": "The AI nutrition app: calories and macros from a photo."},
}
INSTAGRAM = "https://www.instagram.com/arrankoapp/"
# Social accounts (ARR-159), shown as icons in the footer.
SOCIAL = "".join(
    '<a href="%s" aria-label="%s"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg></a>' % s for s in [
        (INSTAGRAM, "Instagram @arrankoapp",
         '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/>'
         '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.3" fill="currentColor"/>'),
        ("https://www.tiktok.com/@arrankoapp", "TikTok @arrankoapp",
         '<path fill="currentColor" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>'),
        ("https://x.com/arrankoapp", "X @arrankoapp",
         '<path fill="currentColor" d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>'),
    ])


def url(key, lang):
    path = PAGES[key][lang][0]
    return "/" + path.replace("index.html", "")


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def label_tables(body):
    """Gives every table cell its column name (data-label), so on phones each row can show as a card."""
    def one_table(m):
        table = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", h) for h in re.findall(r"<th>(.*?)</th>", table, re.S)]

        def one_row(r):
            cells = iter(heads)
            return re.sub(r"<td>", lambda _: '<td data-label="%s">' % htmllib.escape(next(cells, ""), quote=True), r.group(0))
        return re.sub(r"<tr>.*?</tr>", one_row, table, flags=re.S)
    return re.sub(r"<table>.*?</table>", one_table, body, flags=re.S)


def with_toc(body, lang):
    """Gives every <h2> an id and returns (body, table of contents)."""
    items = []

    def add_id(m):
        title = re.sub(r"<[^>]+>", "", m.group(1))
        items.append((slug(title), title))
        return '<h2 id="%s">%s</h2>' % (slug(title), m.group(1))

    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)
    toc = ('<nav class="toc" aria-label="%s"><p>%s</p><ol>%s</ol></nav>'
           % (T[lang]["toc"], T[lang]["toc"], "".join('<li><a href="#%s">%s</a></li>' % (s, t) for s, t in items)))
    return body, toc


# The approved splash (final design canvas, "Splash · final", light or dark like the page): the
# capsules light clockwise every 0.15 s, the box leans back, glides left with speed lines while
# "arranko" fades up letter by letter, then everything fades into the page at about 3 s.
SPLASH = """<div class="splash" id="splash" aria-hidden="true">
<div class="splash-logo">
<span class="grp">
<span class="streak-at" style="top:18px"><span class="streak s1"></span></span>
<span class="streak-at" style="top:31px"><span class="streak s2"></span></span>
<span class="streak-at" style="top:44px"><span class="streak s3"></span></span>
<span class="sbox"><svg viewBox="34 46 134 116" focusable="false"><g transform="skewX(-12) translate(22 0)" fill="currentColor"><rect class="cap c1" x="48" y="95" width="24" height="65" rx="11"/><rect class="cap c2" x="78" y="138" width="44" height="22" rx="11"/><rect class="cap c3" x="78" y="95" width="44" height="22" rx="11"/><rect class="cap c4" x="60" y="48" width="94" height="22" rx="11"/><rect class="cap c5" x="130" y="48" width="24" height="112" rx="11"/></g></svg></span>
</span>
<span class="word"><span class="l l1">a</span><span class="l l2">r</span><span class="l l3">r</span><span class="l l4">a</span><span class="l l5">n</span><span class="l l6">k</span><span class="l l7">o</span></span>
</div>
</div>
<script>
/* Splash: once per visit, skipped when the person asked for less motion. */
(function () {
  var d = document.documentElement, seen = false;
  try { seen = sessionStorage.getItem("arranko-splash") === "1"; sessionStorage.setItem("arranko-splash", "1"); } catch (e) {}
  if (seen || window.matchMedia("(prefers-reduced-motion: reduce)").matches) d.classList.add("no-splash");
  else d.classList.add("splashing");
})();
</script>"""

HEAD_SCRIPT = """<script>
/* Light or dark: the person's choice from the switch, else the phone's setting. */
(function () {
  var d = document.documentElement;
  try { var t = localStorage.getItem("arranko-theme"); if (t === "light" || t === "dark") d.setAttribute("data-theme", t); } catch (e) {}
  /* Motion only when the script can run it; if motion.js never starts, show everything. */
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
  d.classList.add("motion");
  setTimeout(function () { if (!d.classList.contains("motion-ready")) d.classList.remove("motion"); }, 2500);
})();
</script>"""

THEME_ICON = ('<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
              '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')

for key, langs in PAGES.items():
    for lang, (path, title, desc, head, toc) in langs.items():
        t = T[lang]
        name = BODY_FILE[key] if isinstance(BODY_FILE[key], str) else BODY_FILE[key][lang]
        body = label_tables((BODIES / lang / (name + ".html")).read_text().strip())
        is_home = key == "home"
        other = "en" if lang == "es" else "es"
        other_url = url(key, other) if other in langs else url("home", other)
        home_url = url("home", lang)
        if head:
            eyebrow, h1, lead, dated = head
            head_html = ('<section class="page-head"><p class="eyebrow">%s</p><h1 class="display">%s</h1>'
                         '<p class="lead">%s</p>%s</section>' % (
                             eyebrow, h1, htmllib.escape(lead, quote=False),
                             '<p class="meta">%s: %s</p>' % (t["updated"], UPDATED[lang]) if dated else ""))
            if toc:
                body, toc_html = with_toc(body, lang)
                main = '%s<div class="doc">%s<article class="prose">%s</article></div>' % (head_html, toc_html, body)
            else:
                main = '%s<div class="doc single"><article class="prose">%s</article></div>' % (head_html, body)
        else:
            main = body
        banner = '<div class="draft">%s</div>' % t["draft"] if DRAFT and key in ("privacy", "terms", "support", "delete") else ""
        menu = "".join('<a href="%s%s">%s</a>' % ("" if is_home else home_url, href, label) for href, label in t["menu"])
        legal = "".join('<a href="%s">%s</a>' % (url(k, lang), label) for k, label in t["legal"])
        alternates = "".join('<link rel="alternate" hreflang="%s" href="https://arranko.app%s">' % (l, url(key, l)) for l in langs)
        body_class = "home" if is_home else "inner"
        splash = SPLASH if is_home else ""
        page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#F4F5F0" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0C0F0A" media="(prefers-color-scheme: dark)">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://arranko.app/og.png">
<meta name="twitter:card" content="summary_large_image">
{alternates}
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
{HEAD_SCRIPT}
<link rel="stylesheet" href="/style.css?v={version('style.css')}">
<link rel="stylesheet" href="/motion.css?v={version('motion.css')}">
</head>
<body class="{body_class}">
{splash}
{banner}
<header class="top-wrap">
<div class="top">
<a class="brand" href="{home_url}" aria-label="{t['home']}"><span class="tile">{LOGO}</span><span>arranko</span></a>
<nav class="menu" id="site-menu" aria-label="Menu">{menu}</nav>
<div class="actions">
<button class="theme" type="button" aria-label="{t['theme']}">{THEME_ICON}</button>
<a class="lang" href="{other_url}" hreflang="{other}" lang="{other}" aria-label="{t['other_label']}">{t['other']}</a>
<a class="cta" href="{INSTAGRAM}">{t['cta']}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="{t['menu_label']}"><span></span><span></span></button>
</div>
</div>
</header>
<main class="wrap">
{main}
</main>
<footer class="foot">
<div class="wrap">
<div class="foot-top">
<div class="foot-brand"><span class="tile">{LOGO}</span><p>{t['tag']}</p></div>
<div class="foot-links">
<nav aria-label="Legal">{legal}</nav>
<div class="social">{SOCIAL}</div>
</div>
</div>
<p class="foot-word" aria-hidden="true">arranko</p>
<p class="foot-copy">© 2026 arranko</p>
</div>
</footer>
<script src="/motion.js?v={version('motion.js')}" defer></script>
</body>
</html>
"""
        out = OUT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
        print("wrote", out)
