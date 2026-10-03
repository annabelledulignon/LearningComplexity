"""Builds slides.html (all slides, 1080x1350 each) from content.py."""
import html
import json
import re
from pathlib import Path

import content as C

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent


def inline(text):
    text = html.escape(text, quote=False)
    return re.sub(r"_(.+?)_", r"<em>\1</em>", text)


def stanzas(blocks):
    out = []
    for block in blocks:
        lines = "".join(f"<p>{inline(line)}</p>" for line in block)
        out.append(f'<div class="stanza">{lines}</div>')
    return "".join(out)


def he_verse(text, verse_no):
    text = html.escape(text, quote=False)
    if verse_no == 7:  # "But I am a worm" sits in Hebrew verse 7.
        words = text.split(" ")
        words[1] = f'<span class="worm">{words[1]}</span>'
        text = " ".join(words)
    return text


def en_verse(text):
    text = html.escape(text.replace("'", "\u2019"), quote=False)
    return re.sub(r"\bworm\b", '<span class="worm">worm</span>', text)


slides = []


def slide(kind, body, stelae=None):
    slides.append((kind, body, stelae))


slide("title", f"""
  <div class="content title-wrap">
    <h1>{inline(C.TITLE)}</h1>
  </div>""", {"alpha": 0.62, "camY": 6, "pitch": 0.32})

for label, blocks in C.SETTING:
    slide("text", f"""
  <div class="content fit"><div class="inner">
    <div class="label">{inline(label)}</div>
    <div class="poem">{stanzas(blocks)}</div>
  </div></div>""")

for blocks in C.POEM_BEFORE:
    slide("text", f'<div class="content fit"><div class="inner"><div class="poem">{stanzas(blocks)}</div></div></div>')

en = json.loads((SRC / "ps22_bbe.json").read_text(encoding="utf-8"))
he = dict((n, t) for n, t in json.loads((SRC / "ps22_he.json").read_text(encoding="utf-8")))
for k, (a, b) in enumerate(C.PSALM_SPLITS):
    rows = []
    if a == 1:
        rows.append(f'<div class="en sup">{inline(C.PSALM_SUPERSCRIPTION)}</div>'
                    f'<div class="he" lang="he" dir="rtl">{he_verse(he[1], 1)}</div>')
    for v in range(a, b + 1):
        text = C.PSALM_OVERRIDES.get(v, en[v - 1])
        rows.append(f'<div class="en">{en_verse(text)}</div>'
                    f'<div class="he" lang="he" dir="rtl">{he_verse(he[v + 1], v + 1)}</div>')
    head = ('<div class="ps-head"><span>Psalm 22</span>'
            '<span class="he-head" lang="he" dir="rtl">תְּהִלִּים כב</span></div>')
    foot = ""
    if k == len(C.PSALM_SPLITS) - 1:
        foot = ('<div class="ps-foot">English: <em>The Bible in Basic English</em> (1965), public domain. '
                'Hebrew: Westminster Leningrad Codex, with cantillation.</div>')
    slide("psalm", f"""
  <div class="content psfit"><div class="inner">
    {head}
    <div class="ps-rows">{''.join(rows)}</div>
    {foot}
  </div></div>""")

for blocks in C.POEM_AFTER:
    slide("text", f'<div class="content fit"><div class="inner"><div class="poem">{stanzas(blocks)}</div></div></div>')

kaddish = "".join(f"<div>{html.escape(l)}</div>" for l in C.KADDISH_HE)
slide("photo", f"""
  <div class="content photo-wrap">
    <div class="photo-top">
      <img src="src/photo-face-blurred.jpg" alt="">
      <div class="photo-cap">
        <p class="cap">{inline(C.PHOTO_CAPTION)}</p>
        <p class="credit">{inline(C.PHOTO_CREDIT)}</p>
      </div>
    </div>
    <p class="blessing">{inline(C.PHOTO_BLESSING)}</p>
    <div class="kaddish" lang="he" dir="rtl">{kaddish}</div>
  </div>""", {"alpha": 0.3})

noahide_he = "".join(f"<div>{html.escape(l)}</div>" for l in C.NOAHIDE_HE)
slide("text", f"""
  <div class="content fit"><div class="inner">
    <h2>{inline(C.NOAHIDE_TITLE)}</h2>
    <p class="sub">{inline(C.NOAHIDE_SUBTITLE)}</p>
    <div class="poem">{stanzas(C.NOAHIDE)}</div>
    <div class="noahide-he" lang="he" dir="rtl">{noahide_he}</div>
  </div></div>""")

total = len(slides)
parts = []
for n, (kind, body, stelae) in enumerate(slides, 1):
    canvas = ""
    if kind != "psalm":
        opts = {"walk": n * 5.7, "yaw": 0.36 + 0.03 * (n % 4), "alpha": 0.42}
        opts.update(stelae or {})
        canvas = f"<canvas class=\"bg\" width=\"1080\" height=\"1350\" data-opts='{json.dumps(opts)}'></canvas><div class=\"veil\"></div>"
    parts.append(f'<section class="slide {kind}" id="s{n:02d}">{canvas}<div class="frame">{body}'
                 f'<div class="counter">{n} / {total}</div></div></section>')

page = (SRC / "template.html").read_text(encoding="utf-8").replace("<!--SLIDES-->", "\n".join(parts))
(ROOT / "slides.html").write_text(page, encoding="utf-8")
print(f"{total} slides")
