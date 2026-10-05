#!/usr/bin/env python3
"""Validate static-site metadata, structured data, links and sitemap coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import collections
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
DOMAIN = (ROOT / 'CNAME').read_text().strip()
ORIGIN = 'https://' + DOMAIN

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.meta = collections.defaultdict(list); self.canonical = []; self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta': self.meta[a.get('name', a.get('property', a.get('http-equiv', ''))).lower()].append(a.get('content', ''))
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href', ''))
        if tag == 'a': self.links.append(a.get('href', ''))

errors = []; expected = set(); titles = {}; descriptions = {}
for file in sorted(ROOT.glob('*.html')):
    source = file.read_text(); page = Page(); page.feed(source)
    if 'refresh' in page.meta:
        if len(page.canonical) != 1: errors.append(f'{file.name}: redirect needs one canonical')
        continue
    if any('noindex' in value for value in page.meta.get('robots', [])): continue
    url = ORIGIN + ('/' if file.name == 'index.html' else '/' + file.name)
    expected.add(url)
    title = re.findall(r'<title\b[^>]*>(.*?)</title>', source, re.S | re.I)
    if len(title) != 1 or not title[0].strip(): errors.append(f'{file.name}: needs one title')
    elif title[0] in titles: errors.append(f'{file.name}: duplicate title with {titles[title[0]]}')
    else: titles[title[0]] = file.name
    desc = page.meta.get('description', [])
    if len(desc) != 1 or not desc[0].strip(): errors.append(f'{file.name}: needs one description')
    elif desc[0] in descriptions: errors.append(f'{file.name}: duplicate description with {descriptions[desc[0]]}')
    else: descriptions[desc[0]] = file.name
    if page.canonical != [url]: errors.append(f'{file.name}: canonical must be {url}')
    for script in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', source, re.S | re.I):
        try: json.loads(script)
        except ValueError as e: errors.append(f'{file.name}: invalid structured data: {e}')
    for href in page.links:
        parsed = urlparse(href)
        if parsed.scheme not in ('', 'http', 'https') or (parsed.netloc and parsed.netloc != DOMAIN) or not parsed.path: continue
        target = ROOT / unquote(parsed.path.lstrip('/'))
        if parsed.path.endswith('/'): target = target / 'index.html'
        if not target.exists(): errors.append(f'{file.name}: broken internal link {href}')

urls = [entry.text for entry in ET.parse(ROOT / 'sitemap.xml').iter(NS + 'loc')]
if len(urls) != len(set(urls)): errors.append('sitemap.xml: duplicate URLs')
for url in sorted(expected - set(urls)): errors.append(f'sitemap.xml: missing {url}')
for url in sorted(set(urls) - expected): errors.append(f'sitemap.xml: noncanonical or nonindexable URL {url}')
robots = (ROOT / 'robots.txt').read_text()
if f'Sitemap: {ORIGIN}/sitemap.xml' not in robots: errors.append('robots.txt: missing correct sitemap declaration')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'{DOMAIN}: {len(expected)} indexable pages passed SEO validation.')
