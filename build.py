# -*- coding: utf-8 -*-
"""Static-site builder for the ishkuzai hub and the Eventide site.

    py -3.13 build.py            # local build: relative links, open dist\\...\\index.html
    py -3.13 build.py --prod     # production build: absolute cross-site links, hreflang

Content lives in content/<site>/<page-id>/<lang>.md.  A page may exist in any subset of
LANGS; the language switcher offers only the versions that exist.  Every file declares
its own `origin` language (the language the page was first written in).
"""
import json
import posixpath
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / 'content'
ASSETS = ROOT / 'assets'
DATA = ROOT / 'data'
DIST = ROOT / 'dist'
PROD = '--prod' in sys.argv

DOMAIN = 'ishkuzai.com'          # not yet registered; change here when decided
LANGS = ['en', 'de', 'ru', 'fr', 'fa']   # add 'hi' (and its strings) when ready
RTL = {'fa'}
LANG_LABEL = {'en': 'EN', 'de': 'DE', 'ru': 'RU', 'fr': 'FR', 'fa': 'FA', 'hi': 'HI'}
HTML_LANG = {'en': 'en-GB', 'de': 'de', 'ru': 'ru', 'fr': 'fr', 'fa': 'fa', 'hi': 'hi'}

SITES = {
    'hub':      {'host': DOMAIN,              'home': 'home',             'css': 'hub.css',      'name': 'ishkuzai'},
    'eventide': {'host': 'nychthemeron.' + DOMAIN, 'home': 'vespera', 'css': 'eventide.css', 'name': 'Eventide'},
}
# The Demiurge site is built by its own module (demiurge_site.py), from its own content and the project's documents.
DEMIURGE_HOST = 'demiurge.' + DOMAIN
# Projects that live elsewhere.  None = not yet published (rendered as plain text).
EXTERNAL = {'chrestomathia': 'https://chrestomathia.org/', 'demiurge': 'https://' + DEMIURGE_HOST + '/'}
# In a local build a link to a site built beside this one goes to that build, not to the web.
EXTERNAL_LOCAL = {'demiurge': 'demiurge/index.html'}

EVENTIDE_FONTS = {
    'en': 'family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC',
    'fr': 'family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC',
    'de': 'family=Grenze+Gotisch:wght@400;500;600&family=UnifrakturMaguntia&family=EB+Garamond:wght@400;500',
    'ru': 'family=Monomakh&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400',
    'fa': 'family=Amiri:ital,wght@0,400;0,700;1,400&family=EB+Garamond:wght@400;500',
}

STRINGS = json.loads((ROOT / 'strings.json').read_text(encoding='utf-8'))
LAWS = json.loads((ROOT / 'laws.json').read_text(encoding='utf-8'))
TRACE = json.loads((DATA / 'trace.json').read_text(encoding='utf-8-sig'))


def S(key, lang):
    d = STRINGS[key]
    return d.get(lang) or d['en']


# ------------------------------------------------------------------ helpers
def fold(text):
    """ASCII slug from a romanisation or Latin title (diacritics dropped)."""
    t = text.lower()
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'), ('æ', 'ae'), ('œ', 'oe'), ('ø', 'o')):
        t = t.replace(a, b)
    t = unicodedata.normalize('NFKD', t)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


# Russian romanisation for web ADDRESSES only (Jake's own, Slovak-like with the accents
# left off: ч→c, ш→s, щ→sc, ж→z, х→ch).  Nothing is shown on the pages.
# Deliberately nonstandard: ё ѣ → e, ѵ → y, ѳ → th, ф → ph; ъ and ь are not written.
RU_BASE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'z', 'з': 'z',
    'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'ph', 'х': 'ch', 'ц': 'c', 'ч': 'c', 'ш': 's', 'щ': 'sc',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'ju', 'я': 'ja',
    'і': 'i', 'ѣ': 'e', 'ѳ': 'th', 'ѵ': 'y',
}


def romanise_ru(text):
    return ''.join(RU_BASE.get(ch.lower(), ch) for ch in text)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def digits(s, lang):
    if lang == 'fa':
        s = s.translate(str.maketrans('0123456789,', '۰۱۲۳۴۵۶۷۸۹٬'))
    elif lang in ('de',):
        s = s.replace(',', '.')
    elif lang in ('ru', 'fr'):
        s = s.replace(',', ' ')
    return s


def inline(t):
    t = re.sub(r"(?<=\w)'(?=\w)", '’', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def table_html(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<div class="table-wrap"><table><thead><tr>'
           + ''.join(f'<th scope="col">{inline(c)}</th>' for c in head) + '</tr></thead><tbody>']
    for row in body:
        sub = ' class="sub"' if row and row[0].startswith('*—') else ''
        out.append(f'<tr{sub}>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def md(text):
    """A small markdown subset: ## ### headings, paragraphs, - lists (with indented
    continuation lines), > quotes, | tables, **bold**, *italic*, [links](url), raw HTML
    blocks (a line starting with `<`, ended by a blank line).  `---` lines are ignored."""
    out, para, items, raw, table, quote = [], [], [], [], [], []

    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()
        if items:
            out.append('<ul>' + ''.join('<li>' + inline(i) + '</li>' for i in items) + '</ul>')
            items.clear()
        if table:
            out.append(table_html(table))
            table.clear()
        if quote:
            out.append('<blockquote><p>' + inline(' '.join(quote)) + '</p></blockquote>')
            quote.clear()

    for line in text.split('\n'):
        s = line.rstrip()
        if raw:
            if s == '':
                out.append('\n'.join(raw))
                raw.clear()
            else:
                raw.append(s)
            continue
        if s.startswith('<'):
            flush()
            raw.append(s)
        elif s == '' or s.strip() == '---':
            flush()
        elif s.startswith('## '):
            flush()
            out.append('<h2>' + inline(s[3:]) + '</h2>')
        elif s.startswith('### '):
            flush()
            out.append('<h3>' + inline(s[4:]) + '</h3>')
        elif s.startswith('|'):
            if para or items or quote:
                flush()
            table.append(s)
        elif s.startswith('>'):
            if para or items or table:
                flush()
            quote.append(s[1:].strip())
        elif s.startswith('- '):
            if para or table or quote:
                flush()
            items.append(s[2:])
        elif items and s.startswith('  '):
            items[-1] += ' ' + s.strip()
        else:
            if items or table or quote:
                flush()
            para.append(s)
    flush()
    if raw:
        out.append('\n'.join(raw))
    return '\n'.join(out)

# ------------------------------------------------------------------ content
PAGES = {}   # site -> page id -> lang -> dict


def load():
    for site in SITES:
        PAGES[site] = {}
        for pdir in sorted((CONTENT / site).iterdir()):
            if not pdir.is_dir():
                continue
            for f in sorted(pdir.glob('*.md')):
                lang = f.stem
                if lang not in LANGS:
                    continue
                raw = f.read_text(encoding='utf-8').replace('\r\n', '\n')
                m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
                if not m:
                    sys.exit(f'{f}: missing front matter')
                meta = {}
                for ln in m.group(1).split('\n'):
                    k, _, v = ln.partition(':')
                    meta[k.strip()] = v.strip()
                if 'title' not in meta or 'origin' not in meta:
                    sys.exit(f'{f}: title and origin are required')
                meta['lang'] = lang
                meta['body'] = m.group(2)
                meta['id'] = pdir.name
                is_home = pdir.name == SITES[site]['home']
                if is_home:
                    slug = ''
                elif meta.get('slug'):
                    slug = meta['slug']
                elif lang == 'ru':
                    slug = fold(romanise_ru(meta['title']))
                else:
                    slug = fold(meta.get('romanised') or meta['title'])
                if not is_home and not slug:
                    sys.exit(f'{f}: needs `romanised:` (title is not Latin script)')
                meta['slug'] = slug
                base = '' if lang == 'en' else lang
                meta['path'] = '/'.join(p for p in (base, slug) if p)   # '' for site root
                PAGES[site].setdefault(pdir.name, {})[lang] = meta
    # two pages must never share an address (the accent-free scheme can merge letters)
    for site, pages in PAGES.items():
        seen = {}
        for pid, langs in pages.items():
            for lang, p in langs.items():
                key = (lang, p['slug'])
                if key in seen:
                    sys.exit(f'{site}: address clash in {lang}: "{p["slug"]}" used by {seen[key]} and {pid}')
                seen[key] = pid


def page_for(site, pid, lang):
    langs = PAGES[site][pid]
    return langs.get(lang) or langs.get('en') or next(iter(langs.values()))


def out_file(site, page):
    return posixpath.join(site, page['path'], 'index.html') if page['path'] else posixpath.join(site, 'index.html')


def link(from_site, from_page, to_site, to_page):
    """Link from one built page to another."""
    if to_site != from_site and PROD:
        p = to_page['path']
        return f"https://{SITES[to_site]['host']}/" + (p + '/' if p else '')
    src_dir = posixpath.dirname(out_file(from_site, from_page))
    dst = out_file(to_site, to_page)
    rel = posixpath.relpath(dst, src_dir)
    if PROD:
        rel = posixpath.dirname(rel)
        rel = (rel + '/') if rel else './'
    return rel


# ------------------------------------------------------------------ tracer
def stage_names(lang):
    """Engine stage name -> display name, matched by position (proto form first)."""
    lst = STRINGS['stage_names'].get(lang) or STRINGS['stage_names']['en']
    keys = ['Proto-Ahéric'] + [s['name'] for s in TRACE['stages']]
    return dict(zip(keys, lst))


def stage_dates(text, lang):
    nums = re.findall(r'−([\d,]+)', text)
    a, b = (digits(n, lang) for n in nums)
    return f'<bdi>−{a}</bdi> – <bdi>−{b}</bdi>'


def tracer(lang):
    sn = stage_names(lang)
    stages = [s['name'] for s in TRACE['stages']]
    sidx = {n: i for i, n in enumerate(stages)}
    law_data = {l['id']: l for l in TRACE['laws']}
    out = [f'<div class="tracer" data-tracer data-next="{esc(S("t_next", lang))}">']
    out.append(f'<p class="tracer-label" id="tracer-label">{S("t_choose", lang)}</p>')
    out.append('<ul class="tracer-words" aria-labelledby="tracer-label">')
    for i, w in enumerate(TRACE['words']):
        out.append(f'<li><button type="button" data-word="{w["gloss"]}" aria-pressed="{"true" if i == 0 else "false"}">'
                   f'{S("gloss_" + w["gloss"], lang)}</button></li>')
    out.append('</ul>')
    out.append(f'<div class="tracer-controls"><button type="button" data-act="next">{S("t_next", lang)}</button>'
               f'<button type="button" data-act="all">{S("t_all", lang)}</button>'
               f'<button type="button" data-act="reset">{S("t_again", lang)}</button></div>')
    for w in TRACE['words']:
        out.append(f'<article class="trace" data-word="{w["gloss"]}">')
        out.append(f'<h3>{S("gloss_" + w["gloss"], lang)}</h3>')
        out.append(f'<p class="trace-root">{S("t_root", lang)} <span dir="ltr" lang="und">{esc(w["root"])}-</span></p>')
        out.append('<ol class="steps">')
        last_stage = None
        for k, st in enumerate(w['steps']):
            if k and not st['changed']:
                continue
            si = sidx.get(st['stage'], -1)
            if k == 0:
                label, text = sn['Proto-Ahéric'], ''
                cls = 'step start stage-p'
                stage_note = ''
            else:
                ld = LAWS.get(st['law'], {})
                label = f'{st["law"]} · {ld.get("name", {}).get(lang) or ld.get("name", {}).get("en") or st["name"]}'
                text = ld.get('text', {}).get(lang) or ld.get('text', {}).get('en') or law_data[st['law']]['text']
                cls = f'step stage-{si}'
                stage_note = ''
                if st['stage'] != last_stage:
                    d = TRACE['stages'][si]['dates']
                    stage_note = (f'<p class="step-stage">{esc(sn[st["stage"]])}, '
                                  f'{stage_dates(d, lang)}</p>')
                last_stage = st['stage']
            out.append(f'<li class="{cls}">{stage_note}'
                       f'<p class="step-law">{esc(label)}</p>'
                       f'<p class="step-form" dir="ltr" lang="und">{esc(st["form"])}</p>'
                       + (f'<p class="step-text">{esc(text)}</p>' if text else '') + '</li>')
        out.append('</ol>')
        chain = [('Proto-Ahéric', w['steps'][0]['form'])] + [(s, w['stages'][s]) for s in stages]
        out.append('<div class="chain"><p class="chain-title">' + S('t_chain', lang) + '</p><ol>')
        for name, f in chain:
            out.append(f'<li><span class="chain-stage">{esc(sn[name])}</span>'
                       f'<span class="chain-form" dir="ltr" lang="und">{esc(f)}</span></li>')
        out.append('</ol></div>')
        out.append('</article>')
    out.append('</div>')
    return '\n'.join(out)


# ------------------------------------------------------------------ rendering
def resolve(site, page, body):
    lang = page['lang']

    def url(m):
        s, pid = m.group(1), m.group(2)
        if pid not in PAGES[s]:
            sys.exit(f'{site}/{page["id"]}/{lang}: unknown page {s}:{pid}')
        return link(site, page, s, page_for(s, pid, lang))

    body = re.sub(r'\{\{url:(\w+):([\w-]+)\}\}', url, body)

    def ext_a(m):
        target = EXTERNAL.get(m.group(1))
        if target and not PROD and m.group(1) in EXTERNAL_LOCAL:
            target = posixpath.relpath(EXTERNAL_LOCAL[m.group(1)], posixpath.dirname(out_file(site, page)))
        return f'<a href="{target}">{m.group(2)}</a>' if target else m.group(2)

    body = re.sub(r'<a href="\{\{ext:(\w+)\}\}">(.*?)</a>', ext_a, body)
    body = re.sub(r'\{\{t:(\w+)\}\}', lambda m: S(m.group(1), lang), body)
    if '{{tracer}}' in body:
        body = body.replace('<p>{{tracer}}</p>', '{{tracer}}').replace('{{tracer}}', tracer(lang))
    return body


def head(site, page, title):
    lang = page['lang']
    if site == 'eventide':
        fonts = EVENTIDE_FONTS.get(lang, EVENTIDE_FONTS['en'])
    else:
        fonts = 'family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400&family=Forum&family=Ruslan+Display&family=EB+Garamond:wght@400;500'
        if lang == 'fa':
            fonts += '&family=Noto+Naskh+Arabic:wght@400;700'
        # the script of the inscription on this page, and Old Persian for the Persian pages' name
        extra = {'home': 'Noto+Sans+Old+Persian', 'projects': 'Noto+Sans+Avestan', 'contact': 'Noto+Serif+Devanagari:wght@400;600'}
        for fam in {extra.get(page['id']), 'Noto+Sans+Old+Persian' if lang == 'fa' else None} - {None}:
            fonts += '&family=' + fam
    alt = ''
    if PROD:
        for lg, p in PAGES[site][page['id']].items():
            path = p['path']
            alt += (f'  <link rel="alternate" hreflang="{HTML_LANG[lg]}" '
                    f'href="https://{SITES[site]["host"]}/{path + "/" if path else ""}">\n')
    css = posixpath.relpath(posixpath.join(site, SITES[site]['css']),
                            posixpath.dirname(out_file(site, page)))
    desc = esc(page.get('summary', ''))
    return f'''<!doctype html>
<html lang="{HTML_LANG[lang]}" dir="{'rtl' if lang in RTL else 'ltr'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{desc}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
  <link rel="stylesheet" href="{css}">
{alt}</head>
'''


def switcher(site, page):
    lang = page['lang']
    items = []
    for lg in LANGS:
        p = PAGES[site][page['id']].get(lg)
        if not p:
            continue
        if lg == lang:
            items.append(f'<a href="{link(site, page, site, p)}" hreflang="{HTML_LANG[lg]}" lang="{HTML_LANG[lg]}" '
                         f'aria-current="page">{LANG_LABEL[lg]}</a>')
        else:
            items.append(f'<a href="{link(site, page, site, p)}" hreflang="{HTML_LANG[lg]}" lang="{HTML_LANG[lg]}">'
                         f'{LANG_LABEL[lg]}</a>')
    return f'<nav class="langs" aria-label="{esc(S("language", lang))}">' + ''.join(items) + '</nav>'


# The name in the top corner: the Scythians (Σκύθης) for English, French and German; the same name in the old Russian
# letters for Russian; the Old Persian for "Saka" for Persian.
HUB_NAME = {'en': ('Σκύθης', 'grc'), 'de': ('Σκύθης', 'grc'), 'fr': ('Σκύθης', 'grc'),
            'ru': ('скѵѳъ', 'ru'), 'fa': ('𐎿𐎣', 'peo')}
# What is written at the foot of each page, whatever the language: (text, language tag, direction)
INSCRIPTIONS = {
    'home': ('𐎲𐎥 𐏐 𐎺𐏀𐎼𐎣 𐏐 𐎠𐎢𐎼𐎶𐏀𐎭𐎠', 'peo', 'ltr'),
    'projects': ('𐬵𐬎𐬨𐬀𐬙𐬀 𐬵𐬏𐬑𐬙𐬀 𐬵𐬎𐬎𐬀𐬭𐬱𐬙𐬀', 'ae', 'rtl'),
    'contact': ('अहन्वृत्रं वृत्रतरं व्यंसमिन्द्रो वज्रेण महता वधेन ।<br>स्कन्धांसीव कुलिशेना विवृक्णाहिः शयत उपपृक्पृथिव्याः ॥', 'sa', 'ltr'),
}
HUB_NAV = [('home', 'nav_home'), ('projects', 'nav_projects'), ('contact', 'nav_contact')]


def inscription(page_id):
    """The line of ancient script at the foot of a hub page (the same in every language)."""
    text, tag, direction = INSCRIPTIONS.get(page_id, ('', '', 'ltr'))
    if not text:
        return ''
    return f'<p class="inscription inscription-{tag}" lang="{tag}" dir="{direction}" translate="no">{text}</p>\n'


def hub_nav(site, page):
    """The hub's three pages.  Labels are in the reader's language; a page that does not exist
    in that language is linked in English."""
    lang = page['lang']
    items = []
    for pid, key in HUB_NAV:
        if pid not in PAGES[site]:
            continue
        cur = ' aria-current="page"' if pid == page['id'] else ''
        items.append(f'<a href="{link(site, page, site, page_for(site, pid, lang))}"{cur}>{esc(S(key, lang))}</a>')
    return '<nav class="sections" aria-label="ishkuzai">' + ''.join(items) + '</nav>'


def origin_note(page):
    if page['origin'] == page['lang']:
        return ''
    name = STRINGS['langname'][page['lang']][page['origin']]
    return '<p class="origin">' + S('origin', page['lang']).replace('{lang}', name) + '</p>'


# ---- German pages: Fraktur with long s ------------------------------------------------
GERMAN_LETTERS = set('abcdefghijklmnopqrstuvwxyzäöüßABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ')
VOWELS = set('aeiouäöüyAEIOUÄÖÜY')
# In-world names stay in Antiqua inside Fraktur text, as foreign words traditionally do.
NAMES = set("""endaran kara gantumba seren sarcera thetch thetland ancora darde berland lythe azade
haldorak rhun corcas sothos romon eracas larcan anu marach halbrad caphenthes ethoras talud raphon
taldar hulden hadur fakal adranal eventide ascanian""".split())
WORD = re.compile(r"&#?\w+;|[A-Za-zÀ-ÖØ-öø-ÿĀ-ɏ’'\u0300-\u036f]+")
VOID = {'meta', 'link', 'br', 'hr', 'img', 'input'}


def long_s(w):
    """Round s at the end of a word or syllable, long s elsewhere (Fraktur practice)."""
    out, n = [], len(w)
    for i, ch in enumerate(w):
        if ch != 's':
            out.append(ch)
            continue
        nxt = w[i + 1] if i + 1 < n else ''
        prev = w[i - 1] if i else ''
        if not nxt:
            out.append('s')                       # word end
        elif nxt == 's' or prev == 's':
            out.append('ſ')                       # ss: ſſ inside a word, ſs at its end
        elif nxt == 't' and w.lower().startswith('wachst'):
            out.append('s')                       # Wachs|thum (compound boundary)
        elif nxt in 'tp' or w[i + 1:i + 3] == 'ch':
            out.append('ſ')                       # st, sp, sch
        elif nxt in VOWELS:
            out.append('ſ')
        else:
            out.append('s')                       # syllable-final before a consonant: Königs|rat
    return ''.join(out)


def fraktur_text(text, heading):
    def word(m):
        w = m.group(0)
        if w.startswith('&'):
            return w
        base = w.lower().rstrip('s') if w.lower() not in NAMES else w.lower()
        german = all(c in GERMAN_LETTERS for c in w)
        foreign = (not german) or w.lower() in NAMES or base in NAMES
        if foreign:
            if heading:
                return long_s(w) if german else w
            return f'<span class="ant">{w}</span>'
        return long_s(w)
    return WORD.sub(word, text)


def fraktur_html(html):
    """Apply long-s spelling to the text nodes of a built German page."""
    out, skip_tag, skip_depth, heading, in_body = [], None, 0, 0, False
    for tok in re.split(r'(<[^>]*>)', html):
        if tok.startswith('<'):
            m = re.match(r'</?([A-Za-z0-9]+)', tok)
            name = m.group(1).lower() if m else ''
            closing = tok.startswith('</')
            if name == 'body' and not closing:
                in_body = True
            if skip_tag:
                if name == skip_tag:
                    skip_depth += -1 if closing else 1
                    if skip_depth == 0:
                        skip_tag = None
            elif not closing and name not in VOID and (name in ('script', 'style') or 'lang="und"' in tok):
                skip_tag, skip_depth = name, 1
            if name in ('h1', 'h2', 'h3'):
                heading += -1 if closing else 1
            out.append(tok)
        elif skip_tag or not in_body:
            out.append(tok)
        else:
            out.append(fraktur_text(tok, heading > 0))
    return ''.join(out)


def render(site, page):
    lang = page['lang']
    body = resolve(site, page, md(page['body']))
    cfg = SITES[site]
    title = page['title'] if page['id'] == cfg['home'] and site == 'hub' else f"{page['title']} — {cfg['name']}"
    html = head(site, page, title)
    home_hub = link(site, page, 'hub', page_for('hub', 'home', lang))
    lead = f'<p class="lead">{inline(page["lead"])}</p>' if page.get('lead') else ''
    is_home = page['id'] == cfg['home']
    if site == 'eventide':
        nav = []
        for pid in ('vespera', 'tongues'):
            p = page_for('eventide', pid, lang)
            cur = ' aria-current="page"' if pid == page['id'] else ''
            nav.append(f'<a href="{link(site, page, site, p)}"{cur}>{esc(p.get("nav", p["title"]))}</a>')
        html += f'''<body class="eventide{' home' if is_home else ''}">
<div class="band band--key" aria-hidden="true"></div>
<div class="leaf">
<header class="running wrap">
  <a class="wordmark" href="{link(site, page, site, page_for(site, cfg['home'], lang))}">Eventide</a>
  <nav class="sections" aria-label="Eventide">{''.join(nav)}</nav>
  {switcher(site, page)}
</header>
<div class="title wrap">
  <h1>{esc(page['title'])}</h1>
  <div class="ornament" aria-hidden="true"></div>
</div>
<main class="wrap content">
{lead}
{origin_note(page)}
{body}
</main>
<footer class="foot wrap">
  <p>{S('footer_eventide', lang)}</p>
  <p><a href="{home_hub}">ishkuzai</a></p>
</footer>
<div class="band band--stitch" aria-hidden="true"></div>
</div>
<script src="{posixpath.relpath(posixpath.join(site, 'tracer.js'), posixpath.dirname(out_file(site, page)))}" defer></script>
</body>
</html>
'''
    else:
        html += f'''<body class="hub{' home' if is_home else ''}">
<header class="top">
  <div class="wrap bar">
    <a class="wordmark" lang="{HUB_NAME[lang][1]}" aria-label="ishkuzai" href="{link(site, page, site, page_for(site, cfg['home'], lang))}">{HUB_NAME[lang][0]}</a>
    {hub_nav(site, page)}
    {switcher(site, page)}
  </div>
</header>
<main class="leaf">
  <div class="leaf-in">
    <h1{' class="sr-only"' if is_home else ''}>{esc(page['title'])}</h1>
    {lead}
    {origin_note(page)}
    <div class="text">
{body}
    </div>
  </div>
</main>
<footer class="wrap foot">{inscription(page['id'])}<p>© 2026 ishkuzai</p></footer>
</body>
</html>
'''
    if site == 'eventide' and lang == 'de':
        html = fraktur_html(html)
    return html


def main():
    load()
    if DIST.exists():
        shutil.rmtree(DIST)
    count = 0
    for site in SITES:
        (DIST / site).mkdir(parents=True)
        shutil.copy(ASSETS / SITES[site]['css'], DIST / site / SITES[site]['css'])
        if site == 'hub':
            shutil.copy(ASSETS / 'hub-bg.jpg', DIST / site / 'hub-bg.jpg')
        if site == 'eventide':
            shutil.copy(ASSETS / 'tracer.js', DIST / site / 'tracer.js')
        for pid, langs in PAGES[site].items():
            for lang, page in langs.items():
                dest = DIST / out_file(site, page)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(render(site, page), encoding='utf-8')
                count += 1
    # Each site is deployed on its own: its address goes with it (GitHub Pages reads CNAME), and it is published as it is.
    for site in SITES:
        (DIST / site / 'CNAME').write_text(SITES[site]['host'] + '\n', encoding='utf-8', newline='\n')
        (DIST / site / '.nojekyll').write_text('', encoding='utf-8')
    import demiurge_site
    dm = demiurge_site.build(DIST, prod=PROD, internal='--internal' in sys.argv)
    count += dm
    print(f'  demiurge: {dm} files')
    if not PROD:
        # Local convenience only: a front door to the sites, so dist\index.html can be opened.
        rows = ''.join(
            f'<li><a href="{s}/index.html">{SITES[s]["name"]}</a></li>' for s in SITES) + '<li><a href="demiurge/index.html">Demiurge</a></li>'
        (DIST / 'index.html').write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Local preview</title>'
            '<body style="font:20px/1.6 Georgia,serif;max-width:30rem;margin:4rem auto;padding:0 1.25rem">'
            '<h1 style="font-weight:400">Local preview</h1>'
            f'<ul>{rows}</ul>'
            '<p style="font-size:.9rem;color:#555">This page exists only in local builds.</p>',
            encoding='utf-8')
    print(f'built {count} pages ({"production" if PROD else "local"}) into {DIST}')


if __name__ == '__main__':
    main()
