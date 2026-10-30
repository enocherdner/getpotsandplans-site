#!/usr/bin/env python3
"""Rebuild /privacy and /terms from the app repo's docs/legal markdown.

Run after editing docs/legal:  python3 build-legal.py [path/to/docs/legal]
Handles what those files use: # and ## headings, paragraphs, "- " lists, **bold**, links.
"""
import html, re, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Projects/pp-main/docs/legal")
HERE = Path(__file__).parent
PAGES = [("privacy-policy.md", "privacy", "Privacy policy"), ("terms-of-use.md", "terms", "Terms of use")]


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


def to_html(md):
    out, para, items = [], [], []

    def flush():
        if para:
            text = " ".join(para)
            cls = ' class="updated"' if text.startswith("Last updated") else ""
            out.append(f"<p{cls}>{inline(text)}</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("## "):
            flush(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "):
            flush(); out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("- "):
            if para: flush()
            items.append(s[2:])
        else:
            para.append(s)
    flush()
    return "\n      ".join(out)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Pots &amp; Plans</title>
  <meta name="description" content="The Pots &amp; Plans {lower}.">
  <meta name="theme-color" content="#c2410c">
  <link rel="icon" href="/favicon.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="/"><img src="/img/logo.svg" alt="">Pots &amp; Plans</a>
      <nav><a href="/">Home</a></nav>
    </div>
  </header>
  <main>
    <article class="legal">
      {body}
    </article>
  </main>
  <footer>
    <div class="wrap">
      <span>&copy; 2026 Pots &amp; Plans</span>
      <nav>
        <a href="/">Home</a>
        <a href="/privacy/">Privacy policy</a>
        <a href="/terms/">Terms of use</a>
      </nav>
    </div>
  </footer>
</body>
</html>
"""

for src, slug, title in PAGES:
    body = to_html((SRC / src).read_text())
    (HERE / slug).mkdir(exist_ok=True)
    (HERE / slug / "index.html").write_text(TEMPLATE.format(title=title, lower=title.lower(), body=body))
    print(f"{slug}/index.html  <-  {SRC / src}")
