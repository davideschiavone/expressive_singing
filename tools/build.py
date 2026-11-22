#!/usr/bin/env python3
"""
Build the English pages and the sitemap.

The French pages at the repository root are the source of truth (French is the
primary language and the x-default). Every user-facing string carries both
data-en and data-fr attributes (see CLAUDE.md). This script:

  1. writes en/<page>.html for every root page that declares an
     hreflang="en" alternate, swapping in the English strings;
  2. regenerates sitemap.xml (FR + EN URLs with hreflang alternates).

Run it after editing any page:

    python3 tools/build.py

Conventions understood by the generator (in the FR source pages):
  data-en="..." / data-fr="..."       text content of a text-only element
  data-alt-en / data-alt-fr           <img alt>
  data-placeholder-en / -fr           input/textarea placeholder
  data-en-<attr>="..."                value of <attr> in the EN page
                                      (e.g. data-en-href, data-en-content, data-en-src)
  <script type="application/ld+json" data-ld-lang="fr">  FR-only JSON-LD (dropped in EN)
  <script type="text/plain" data-ld-lang="en">           EN-only JSON-LD (activated in EN)
Relative asset URLs (href/src/url()) are prefixed with ../ in the EN pages;
links to other translated pages stay relative so visitors remain in English.
"""
import datetime
import html
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://expressivesinging.ch/'
EN_DIR = ROOT / 'en'

PROTECTED = re.compile(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->)', re.S | re.I)
TAG = re.compile(r'<([a-zA-Z][\w-]*)((?:\s+[^\s=>/"\']+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>"\']+))?)*)\s*(/?)>')
ATTR = re.compile(r'([^\s=>/"\']+)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>"\']+))?')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
ABSOLUTE = ('http:', 'https:', '//', '#', 'mailto:', 'tel:', 'data:', 'javascript:', '/', '../')
URL_ATTRS = ('href', 'src', 'poster')
CSS_URL = re.compile(r'url\((["\']?)(?!https?:|data:|/|\.\./)([^"\')]+)\1\)')


# ---------------------------------------------------------------- tags ---
class Tag:
    def __init__(self, name, attr_src, selfclose):
        self.name = name.lower()
        self.selfclose = selfclose
        self.attrs = []          # [name, raw_value_or_None]
        for m in ATTR.finditer(attr_src):
            raw = m.group(2)
            if raw is not None and raw[:1] in '"\'':
                raw = raw[1:-1]
            self.attrs.append([m.group(1), raw])
        self.changed = False

    def get(self, key):
        for k, v in self.attrs:
            if k.lower() == key:
                return v
        return None

    def set(self, key, value):
        for a in self.attrs:
            if a[0].lower() == key:
                if a[1] != value:
                    a[1] = value
                    self.changed = True
                return
        self.attrs.append([key, value])
        self.changed = True

    def render(self):
        parts = [self.name]
        for k, v in self.attrs:
            parts.append(k if v is None else '%s="%s"' % (k, v.replace('"', '&quot;')))
        return '<' + ' '.join(parts) + (' /' if self.selfclose else '') + '>'


def fix_url(value, en_pages):
    """Make a root-relative URL work from inside en/."""
    if not value or value.startswith(ABSOLUTE):
        return value
    page = re.match(r'^([\w-]+\.html)([#?].*)?$', value)
    if page and page.group(1) in en_pages:
        return value                      # translated sibling page
    return '../' + value


def transform_tag(tag, lang, en_pages):
    """Apply the language-specific attribute rules to one start tag."""
    if tag.name == 'html' and tag.get('lang') is not None:
        tag.set('lang', lang)
    for key in ('alt', 'placeholder'):
        v = tag.get('data-%s-%s' % (key, lang))
        if v is not None:
            tag.set(key, v)
    if lang == 'en':
        for key in URL_ATTRS:
            v = tag.get(key)
            if v is not None:
                tag.set(key, fix_url(v, en_pages))
        style = tag.get('style')
        if style and 'url(' in style:
            tag.set('style', CSS_URL.sub(lambda m: 'url(%s../%s%s)' % (m.group(1), m.group(2), m.group(1)), style))
        # explicit per-attribute overrides come last: their values are literal
        for k, v in list(tag.attrs):
            if k.startswith('data-en-') and v is not None:
                tag.set(k[len('data-en-'):], v)


def transform(src, lang, en_pages=frozenset(), page='?'):
    out = []
    pos = 0
    for seg in PROTECTED.split(src):
        if not seg:
            continue
        if PROTECTED.fullmatch(seg):
            out.append(transform_protected(seg, lang, en_pages))
        else:
            out.append(transform_markup(seg, lang, en_pages, page))
    return ''.join(out)


def transform_protected(seg, lang, en_pages):
    if not seg.lower().startswith('<script'):
        return seg
    m = TAG.match(seg)
    tag = Tag(m.group(1), m.group(2), m.group(3) == '/')
    ld_lang = tag.get('data-ld-lang')
    if ld_lang and ld_lang != lang:
        return ''                              # JSON-LD for the other language
    if ld_lang == lang and tag.get('type') == 'text/plain':
        tag.set('type', 'application/ld+json')
    transform_tag(tag, lang, en_pages)
    return (tag.render() if tag.changed else m.group(0)) + seg[m.end():]


def transform_markup(seg, lang, en_pages, page):
    out = []
    pos = 0
    while True:
        m = TAG.search(seg, pos)
        if not m:
            out.append(seg[pos:])
            break
        out.append(seg[pos:m.start()])
        tag = Tag(m.group(1), m.group(2), m.group(3) == '/')
        transform_tag(tag, lang, en_pages)
        text = tag.get('data-' + lang)
        rendered = tag.render() if tag.changed else m.group(0)
        if text is not None and tag.name not in VOID:
            close = seg.find('</%s>' % tag.name, m.end())
            inner = seg[m.end():close]
            if close < 0 or '<' in inner:
                sys.exit('%s: <%s data-%s="%s"> must contain plain text only' % (page, tag.name, lang, text[:40]))
            out.append(rendered + text + '</%s>' % tag.name)
            pos = close + len('</%s>' % tag.name)
        else:
            out.append(rendered)
            pos = m.end()
    return ''.join(out)


# ---------------------------------------------------------- validation ---
class Checker(HTMLParser):
    """Verify every data-<lang> element renders exactly its translation."""

    def __init__(self, lang):
        super().__init__(convert_charrefs=True)
        self.lang, self.stack, self.errors = lang, [], []

    def handle_starttag(self, name, attrs):
        if name in VOID:
            return
        want = dict(attrs).get('data-' + self.lang)
        self.stack.append([name, want, ''])

    def handle_endtag(self, name):
        while self.stack:
            n, want, got = self.stack.pop()
            if want is not None and got != want:
                self.errors.append('<%s>: %r != %r' % (n, got[:50], want[:50]))
            if n == name:
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][2] += data


def check(text, lang, page):
    c = Checker(lang)
    c.feed(text)
    if c.errors:
        sys.exit('%s (%s):\n  ' % (page, lang) + '\n  '.join(c.errors[:10]))


# ------------------------------------------------------------- sitemap ---
def lastmod(path):
    rel = str(path.relative_to(ROOT))
    dirty = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if not dirty:
        date = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', rel], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
        if date:
            return date
    return datetime.date.today().isoformat()


def url_for(page, lang):
    prefix = BASE + ('en/' if lang == 'en' else '')
    return prefix if page == 'index.html' else prefix + page


def write_sitemap(sources):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    order = ['index.html', 'cours-de-chant-geneve.html', 'classes.html', 'contact.html']
    sources = sorted(sources, key=lambda p: (order.index(p.name) if p.name in order else len(order), p.name))
    for path in sources:
        text = path.read_text(encoding='utf-8')
        if re.search(r'<meta name="robots" content="[^"]*noindex', text):
            continue
        has_en = 'hreflang="en"' in text
        mod = lastmod(path)
        for lang in (['fr', 'en'] if has_en else ['fr']):
            lines.append('  <url>')
            lines.append('    <loc>%s</loc>' % url_for(path.name, lang))
            lines.append('    <lastmod>%s</lastmod>' % mod)
            if has_en:
                for alt in ('fr', 'en'):
                    lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (alt, url_for(path.name, alt)))
                lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url_for(path.name, 'fr'))
            lines.append('  </url>')
    lines.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')


# ---------------------------------------------------------------- main ---
def main():
    sources = sorted(ROOT.glob('*.html'))
    translated = [p for p in sources if 'hreflang="en"' in p.read_text(encoding='utf-8')]
    en_pages = frozenset(p.name for p in translated)
    EN_DIR.mkdir(exist_ok=True)
    for stale in EN_DIR.glob('*.html'):
        if stale.name not in en_pages:
            stale.unlink()
    for path in translated:
        src = path.read_text(encoding='utf-8')
        check(src, 'fr', path.name)
        out = transform(src, 'en', en_pages, path.name)
        out = out.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- Generated by tools/build.py from ../%s - edit the French source, not this file. -->' % path.name, 1)
        check(out, 'en', 'en/' + path.name)
        (EN_DIR / path.name).write_text(out, encoding='utf-8')
    write_sitemap(sources)
    print('built %d EN pages + sitemap.xml' % len(translated))


if __name__ == '__main__':
    main()
