# arranko.app

The public website of arranko: home page, privacy policy, terms, support and account deletion.
Plain HTML and one stylesheet, published by GitHub Pages from `master`. No cookies, no analytics, fonts self-hosted.

## Change a text

1. Edit the page body in `_src/bodies/<page>.html` (shared header and footer live in `_src/build.py`).
2. Run `python3 _src/build.py` from this folder.
3. Commit everything and push; GitHub Pages publishes in about a minute.

When the privacy policy or terms change, update `UPDATED` in `_src/build.py`.

## Domain

Namecheap DNS for arranko.app: four `A` records for `@` (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and `CNAME www → arranko.github.io`. The MX and SPF records belong to the email forwarding; leave them.

Font: Archivo (Omnibus-Type), SIL Open Font License, see `fonts/OFL.txt`.
