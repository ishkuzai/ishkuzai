# -*- coding: utf-8 -*-
"""The Demiurge site (demiurge.ishkuzai.com): an introduction, a download page, and the project reference.

The introduction and the download page are written by hand in content/demiurge/*.md.  The reference is
**generated from the project's own document**, `docs/Demiurge - Project Reference.md`, so that revising the
document revises the site: each numbered section becomes a page of a small wiki, with a contents list, links
between sections ("section 12" becomes a link) and a search box.

    py -3.13 build.py                  # whole build (this site is built with the others)
    py -3.13 build.py --internal       # keep the author's working notes in the reference (contradictions,
                                       # reviews, the legend, the appendices): for reading, not for publishing

The public build leaves out what the document itself calls internal: the "How to read" legend, the notes on what
changed between versions, the blockquotes marked as contradictions or reviews, the documentation housekeeping and
the appendices.  Red "TO DO" headers stay, as honest "still to build" notes, restyled.
"""
import html as _html
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = Path(os.environ.get('DEMIURGE_DOCS', 'C:/Users/jakes/OneDrive/Documents/Demiurge/docs'))
REFERENCE = DOCS / 'Demiurge - Project Reference.md'
SITE = 'demiurge'
NAME = 'Demiurge'
HOST = 'demiurge.ishkuzai.com'
# Where the first release can be fetched from.  None until there is one: the download page then says so.
DOWNLOAD = None


# ---------------------------------------------------------------------------------------------- text helpers
def esc(s):
    return _html.escape(s, quote=False)


def fold(text):
    t = unicodedata.normalize('NFKD', text.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def inline(t):
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f'\x00{len(codes) - 1}\x00'

    t = re.sub(r'`([^`]+)`', keep, t)
    t = esc(t)
    t = re.sub(r"(?<=\w)'(?=\w)", '’', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: '<code>' + esc(codes[int(m.group(1))]) + '</code>', t)


def plain(t):
    """Text with the markup taken out (for descriptions and the search index)."""
    t = re.sub(r'<[^>]+>', ' ', t)
    t = _html.unescape(t)
    t = re.sub(r'[*`]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


# ---------------------------------------------------------------------------------------------- markdown
LIST_RE = re.compile(r'^(\s*)([*\-]|\d+\.)\s+(.*)$')


def parse_list(lines):
    """Lines of a list (items, their continuations and nested lists) -> an HTML list."""
    first = LIST_RE.match(lines[0])
    base = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    items = []
    for ln in lines:
        m = LIST_RE.match(ln)
        if m and len(m.group(1)) == base:
            items.append([m.group(3)])
        elif items:
            items[-1].append(ln)
    out = []
    for it in items:
        text, nested = [it[0]], []
        for r in it[1:]:
            if nested or LIST_RE.match(r):
                nested.append(r)
            elif r.strip():
                text.append(r.strip())
        body = inline(' '.join(text))
        if nested:
            body += parse_list(nested)
        out.append(f'<li>{body}</li>')
    tag = 'ol' if ordered else 'ul'
    return f'<{tag}>' + ''.join(out) + f'</{tag}>'


def table_html(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in head) + '</tr></thead><tbody>']
    for row in body:
        out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def heading_id(text):
    m = re.match(r'(\d+(?:\.\d+)*)\.?\s', text)
    return 's' + m.group(1).replace('.', '-') if m else fold(text)


def todo_heading(level, raw):
    """`<h3 style="color:#c62828">Galaxy generation (TO DO, in part)</h3>` -> a heading with a 'still to build' tag."""
    text = re.sub(r'<[^>]+>', '', raw).strip()
    text = re.sub(r'\s*\(TO DO(?:,\s*([^)]*))?\)', lambda m: f' ({m.group(1)})' if m.group(1) else '', text).strip()
    return f'<h{level} class="todo" id="{fold(text)}"><span class="tag">Still to build</span> {esc(text)}</h{level}>'


def md(text, internal=False):
    """The subset of Markdown the documents use: headings, paragraphs, lists (nested), tables, blockquotes, rules."""
    lines = text.split('\n')
    out, i = [], 0
    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()
        if not s or s == '---':
            i += 1
            continue
        if s.startswith('```'):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('```'):
                j += 1
            out.append('<pre><code>' + esc('\n'.join(lines[i + 1:j])) + '</code></pre>')
            i = j + 1
            continue
        mh = re.match(r'^<h([23]) style="color:#c62828">(.*)</h\1>$', s)
        if mh:
            out.append(todo_heading(int(mh.group(1)), mh.group(2)))
            i += 1
            continue
        m = re.match(r'^(#{2,4})\s+(.*)$', s)
        if m:
            lvl, t = len(m.group(1)), m.group(2)
            out.append(f'<h{lvl} id="{heading_id(t)}">{inline(t)}</h{lvl}>')
            i += 1
            continue
        if s.startswith('|'):
            j = i
            while j < len(lines) and lines[j].strip().startswith('|'):
                j += 1
            out.append(table_html(lines[i:j]))
            i = j
            continue
        if s.startswith('>'):
            j = i
            while j < len(lines) and lines[j].strip().startswith('>'):
                j += 1
            inner = [re.sub(r'^\s*>\s?', '', l) for l in lines[i:j]]
            first = next((l for l in inner if l.strip()), '')
            noted = first.lstrip().startswith(('**⚠', '**⚑'))
            if not noted or internal:
                label = ''
                if noted:
                    label = '<p class="note-label">' + ('Contradiction' if '⚠' in first[:6] else 'Review') + '</p>'
                out.append('<blockquote' + (' class="note"' if noted else '') + '>' + label + md('\n'.join(inner), internal) + '</blockquote>')
            i = j
            continue
        if LIST_RE.match(ln):
            j = i
            while j < len(lines) and lines[j].strip() and (LIST_RE.match(lines[j]) or lines[j].startswith(' ')):
                j += 1
            out.append(parse_list(lines[i:j]))
            i = j
            continue
        j = i
        para = []
        while (j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(('|', '>', '#', '---', '<h'))
               and not LIST_RE.match(lines[j])):
            para.append(lines[j].strip())
            j += 1
        if not para:
            para, j = [s], i + 1
        text_p = ' '.join(para)
        ms = re.match(r'^\*\*Status:\s*(.*?)\*\*\s*(.*)$', text_p)
        if ms:
            label, rest = ms.group(1).rstrip('.'), ms.group(2)
            cls = 'partial' if any(k in label.lower() for k in ('partial', 'gaps', 'review')) else 'built'
            out.append(f'<p class="status-line"><span class="pill {cls}">{esc(label[:1].upper() + label[1:])}</span> {inline(rest)}</p>')
        else:
            out.append(f'<p>{inline(text_p)}</p>')
        i = j
    return '\n'.join(out)


# ---------------------------------------------------------------------------------------------- the reference, from the document
class Section:
    def __init__(self, number, title, body):
        self.number, self.title, self.body = number, title, body
        self.slug = fold(re.sub(r'^the\s+', '', re.sub(r'^appendix\s+\w\.\s*', '', title, flags=re.I), flags=re.I))
        m = re.search(r'\*\*Status:\s*(.*?)\*\*', body)
        self.status = m.group(1).rstrip('.') if m else ''

    @property
    def label(self):
        return f'{self.number}. {self.title}' if self.number else self.title


def read_reference(internal=False):
    raw = REFERENCE.read_text(encoding='utf-8').replace('\r\n', '\n')
    head_m = re.search(r'^\*Version (\d+), (\d+ \w+ \d{4})', raw, re.M)
    version = f'Version {head_m.group(1)}, {head_m.group(2)}' if head_m else ''
    sections, extras = [], []
    for part in re.split(r'(?m)^## ', raw)[1:]:
        title, _, body = part.partition('\n')
        title = title.strip()
        m = re.match(r'^(\d+)\.\s+(.*)$', title)
        if m and int(m.group(1)) <= 19:
            sections.append(Section(int(m.group(1)), m.group(2).strip(), body))
        elif internal:
            extras.append(Section(0, title, body))
    return version, sections, extras


def link_sections(html_text, by_number, current):
    """'section 12' and 'section 18.1' become links to that section's page."""
    def link(m):
        n = int(m.group(2))
        if n == current or n not in by_number:
            return m.group(0)
        sub = m.group(3) or ''
        frag = f'#s{n}-{sub[1:]}' if sub else ''
        return f'{m.group(1)}<a href="../{by_number[n].slug}/{frag}">section {n}{sub}</a>'
    return re.sub(r'(?<![\w/])(\(|\s|;)section (\d+)(\.\d+)?(?![\w.]*\d)', link, html_text)


# ---------------------------------------------------------------------------------------------- the picture and the dress
MARK = ('<svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false"><ellipse cx="14" cy="14" rx="12" ry="5" '
        'fill="none" stroke="currentColor" stroke-width="1.3" transform="rotate(-24 14 14)"/>'
        '<circle cx="14" cy="14" r="3.4" fill="currentColor"/><circle cx="23" cy="9.4" r="1.9" fill="currentColor"/></svg>')


LOCALES = json.loads((ROOT / 'content' / SITE / 'locales.json').read_text(encoding='utf-8'))['locales']
PAGE_PATH = {'home': '', 'download': 'download/', 'reference': 'reference/'}


def page_html(title, body, *, depth, current, prod, description='', search=False, home=False, wide=False, locale=None, path=None):
    """One page.  `depth` is how many folders it sits below the site's root; `current` is home, download or reference;
    `path` (for the three main pages) is its address in the language, and lets the menu and the head name the others."""
    loc = locale or LOCALES[0]
    up = '../' * depth
    prefix = loc['dir'] + '/' if loc['dir'] else ''
    base = f'{up}{prefix}' or './'
    hub = 'https://ishkuzai.com/' if prod else f'{up}../hub/'
    labels = loc.get('nav') or ['Introduction', 'Download', 'Reference']
    nav = ''.join(f'<a href="{href}"' + (' aria-current="page"' if key == current else '') + f'>{esc(label)}</a>'
                  for label, href, key in [(labels[0], base, 'home'), (labels[1], f'{up}{prefix}download/', 'download'),
                                           (labels[2], f'{up}{prefix}reference/', 'reference')])
    box = ('<form class="search" role="search" onsubmit="return false"><input id="q" type="search" placeholder="Search the reference" '
           'aria-label="Search the reference" autocomplete="off"><div id="hits"></div></form>') if search else ''
    items = []
    for L in LOCALES:
        pfx = L['dir'] + '/' if L['dir'] else ''
        href = f'{up}{pfx}{PAGE_PATH[current]}' or './'
        cur = ' aria-current="true"' if L is loc else ''
        items.append(f'<li><a href="{href}" lang="{L["html"]}" hreflang="{L["html"]}"{cur}>{esc(L["name"])}</a></li>')
    menu = (f'<details class="langmenu"><summary aria-label="Language"><span lang="{loc["html"]}">{esc(loc["name"])}</span></summary>'
            f'<ul>{"".join(items)}</ul></details>')
    scripts = f'<script src="{up}menu.js" defer></script>'
    if search:
        scripts += f'<script src="{up}search.js" defer data-index="{up}search.json" data-base="{up}"></script>'
    here = path if path is not None else ''
    alts = ''
    if path is not None and (current != 'reference' or path.endswith('reference/')):
        alts = ''.join(f'  <link rel="alternate" hreflang="{L["html"]}" href="https://{HOST}/{(L["dir"] + "/") if L["dir"] else ""}{PAGE_PATH[current]}">\n'
                       for L in LOCALES)
    return f'''<!doctype html>
<html lang="{loc['html']}"{' dir="rtl"' if loc['rtl'] else ''}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="https://{HOST}/{here}">
{alts}  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Forum&family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400&display=swap">
  <link rel="stylesheet" href="{up}demiurge.css">
</head>
<body class="{'home' if home else 'inner'}{' wide' if wide else ''}">
<header class="top">
  <div class="wrap bar">
    <a class="wordmark" href="{base}">{MARK}<span>{NAME}</span></a>
    <nav class="sections" aria-label="{NAME}">{nav}</nav>
    {box}
    {menu}
  </div>
</header>
{body}
<footer class="wrap foot">
  <p><a href="{hub}">ishkuzai</a> &nbsp;·&nbsp; © 2026</p>
</footer>
{scripts}
</body>
</html>
'''


def localise(html_text):
    """For a build opened from disk: a link to a folder names its index.html (a web server does that itself)."""
    def fix(m):
        path, frag = m.group(1), m.group(2) or ''
        return f'href="{path}index.html{frag}"'
    return re.sub(r'href="((?!https?:|mailto:|#)(?:\.{1,2}/)*(?:[\w-]+/)*)(#[^"]*)?"', fix, html_text)


# ---------------------------------------------------------------------------------------------- the build
def read_page(name):
    raw = (ROOT / 'content' / SITE / f'{name}.md').read_text(encoding='utf-8').replace('\r\n', '\n')
    m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
    meta = {}
    for ln in m.group(1).split('\n'):
        k, _, v = ln.partition(':')
        meta[k.strip()] = v.strip()
    return meta, m.group(2)


def leaf(meta, body, extra='', hide_title=False):
    return ('<main class="leaf"><div class="leaf-in">'
            f'<h1{" class=\'sr-only\'" if hide_title else ""}>{inline(meta["title"])}</h1><p class="lead">{inline(meta["lead"])}</p>{extra}'
            f'<div class="text">{md(body)}</div></div></main>')


def build(dist, prod=False, internal=False):
    out = dist / SITE
    out.mkdir(parents=True, exist_ok=True)
    (out / 'demiurge.css').write_text((ROOT / 'assets' / 'demiurge.css').read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    shutil.copyfile(ROOT / 'assets' / 'demiurge-bg.jpg', out / 'background.jpg')
    for js in ('search.js', 'menu.js'):
        (out / js).write_text((ROOT / 'assets' / js).read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    count = 0

    def write(rel, text):
        nonlocal count
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text if prod or not rel.endswith('.html') else localise(text), encoding='utf-8', newline='\n')
        count += 1

    meta, body = read_page('home')
    write('index.html', page_html(f'{NAME}: {plain(meta["lead"])}', leaf(meta, body, hide_title=True), depth=0, current='home', prod=prod,
                                  description=meta.get('summary', ''), home=True, path=''))

    meta, body = read_page('download')
    dl_meta, dl_body = meta, body
    button = (f'<p class="get"><a class="button" href="{DOWNLOAD}">Download Demiurge</a></p>' if DOWNLOAD
              else '<p class="get"><span class="button off">Not yet available</span></p>')
    write('download/index.html', page_html(f'{meta["title"]} — {NAME}', leaf(meta, body, button), depth=1, current='download',
                                           prod=prod, description=meta.get('summary', ''), path='download/'))

    index = []
    if REFERENCE.exists():
        version, sections, extras = read_reference(internal)
        pages = sections + extras
        by_number = {s.number: s for s in sections}
        rendered = {}
        for s in pages:
            rendered[s.slug] = link_sections(md(s.body, internal), by_number, s.number)

        def toc(current):
            rows = ''.join(f'<li><a href="../{s.slug}/"' + (' aria-current="page"' if s is current else '') + f'>{esc(s.label)}</a></li>'
                           for s in pages)
            return f'<nav class="toc" aria-label="Sections of the reference"><p class="toc-title"><a href="../">The reference</a></p><ol>{rows}</ol></nav>'

        for k, s in enumerate(pages):
            prev, nxt = (pages[k - 1] if k else None), (pages[k + 1] if k + 1 < len(pages) else None)
            pager = ('<nav class="pager" aria-label="Neighbouring sections">'
                     + (f'<a class="prev" href="../{prev.slug}/">{esc(prev.label)}</a>' if prev else '<span></span>')
                     + (f'<a class="next" href="../{nxt.slug}/">{esc(nxt.label)}</a>' if nxt else '<span></span>') + '</nav>')
            article = f'<article class="doc"><h1>{esc(s.label)}</h1>{rendered[s.slug]}{pager}</article>'
            first_p = re.search(r'<p>(.*?)</p>', rendered[s.slug], re.S)
            write(f'reference/{s.slug}/index.html',
                  page_html(f'{s.label} — {NAME} reference', f'<main class="docs"><div class="docs-grid">{toc(s)}{article}</div></main>',
                            depth=2, current='reference', prod=prod, description=plain(first_p.group(1))[:180] if first_p else '',
                            search=True, wide=True))
            index.append({'t': s.label, 'u': f'reference/{s.slug}/' + ('' if prod else 'index.html'),
                          'x': plain(re.sub(r'</(p|li|h\d|tr)>', ' ', rendered[s.slug]))[:7000]})

        rows = []
        for s in pages:
            first = re.search(r'<p>(.*?)</p>', rendered[s.slug], re.S)
            blurb = plain(first.group(1))[:170] if first else ''
            pill = ''
            if s.status:
                cls = 'partial' if any(w in s.status.lower() for w in ('partial', 'gaps', 'review')) else 'built'
                pill = f'<span class="pill {cls}">{esc(s.status[:1].upper() + s.status[1:])}</span>'
            num = f'<span class="n">{s.number}</span>' if s.number else '<span class="n"></span>'
            rows.append(f'<li><a class="sec" href="{s.slug}/">{num}<span class="t">{esc(s.title)}</span>{pill}</a><p>{esc(blurb)}</p></li>')
        meta, body = read_page('reference')
        extra = f'<p class="version">{esc(version)}</p>' if version else ''
        html_body = ('<main class="leaf"><div class="leaf-in">'
                     f'<h1>{inline(meta["title"])}</h1><p class="lead">{inline(meta["lead"])}</p>'
                     f'<div class="text">{md(body)}</div>{extra}<ol class="contents">{"".join(rows)}</ol></div></main>')
        write('reference/index.html', page_html(f'{meta["title"]} — {NAME}', html_body, depth=1, current='reference', prod=prod,
                                                description=meta.get('summary', ''), search=True, path='reference/'))
    else:
        print(f'  (no reference: {REFERENCE} not found)')

    # The other languages (the project's locales) are not written yet: the introduction and the reference say so, and the
    # download page stays, with a note that the language is not yet supported and the English text beneath it.
    for L in LOCALES[1:]:
        d = L['dir']

        def wip(depth, current, home):
            english = '../' * depth + PAGE_PATH[current]
            inner = (f'<main class="leaf"><div class="leaf-in"><h1>{esc(L["wip"])}</h1><p class="lead">{esc(L["soon"])}</p>'
                     f'<p class="text center"><a href="{english or "./"}" lang="en-GB" hreflang="en-GB">{esc(L["english"])}</a></p></div></main>')
            return page_html(f'{NAME}: {L["wip"]}', inner, depth=depth, current=current, prod=prod, home=home, locale=L,
                             path=f'{d}/{PAGE_PATH[current]}')

        write(f'{d}/index.html', wip(1, 'home', True))
        write(f'{d}/reference/index.html', wip(2, 'reference', False))
        english_dl = (f'<div class="english" lang="en-GB" dir="ltr"><p class="lead">{inline(dl_meta["lead"])}</p>{button}'
                      f'<div class="text">{md(dl_body).replace(chr(34) + "../reference/", chr(34) + "../../reference/")}</div></div>')
        inner = (f'<main class="leaf"><div class="leaf-in"><h1>{esc(L["nav"][1])}</h1>'
                 f'<p class="notice" role="note">{esc(L["unsupported"])}</p>{english_dl}</div></main>')
        write(f'{d}/download/index.html', page_html(f'{L["nav"][1]} — {NAME}', inner, depth=2, current='download', prod=prod,
                                                    locale=L, path=f'{d}/download/', description=dl_meta.get('summary', '')))

    write('search.json', json.dumps(index, ensure_ascii=False))
    (out / 'CNAME').write_text(HOST + '\n', encoding='utf-8', newline='\n')
    (out / '.nojekyll').write_text('', encoding='utf-8')
    return count
