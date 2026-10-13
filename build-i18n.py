#!/usr/bin/env python3
"""Build static multilingual HTML, JSON-LD, sitemap and assistant facts.

Source: templates/, i18n/ and site-config.json. No third-party dependencies.
Generated files are committed for direct GitHub Pages publication.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
LOCALES = ['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'es', 'fr', 'de', 'pt-BR', 'ru', 'ar', 'hi', 'id']
LANG_NAMES = dict(zip(LOCALES, ['English', '简体中文', '繁體中文', '日本語', '한국어', 'Español', 'Français', 'Deutsch', 'Português (Brasil)', 'Русский', 'العربية', 'हिन्दी', 'Bahasa Indonesia']))
OG_LOCALES = dict(zip(LOCALES, ['en_US', 'zh_CN', 'zh_TW', 'ja_JP', 'ko_KR', 'es_ES', 'fr_FR', 'de_DE', 'pt_BR', 'ru_RU', 'ar_SA', 'hi_IN', 'id_ID']))
PAGES = {'home': 'index.html', 'support': 'support.html', 'privacy': 'privacy.html', 'terms': 'terms.html'}
TOKEN = re.compile(r'\{\{([\w.-]+)\}\}')


def read_data():
    config = json.loads((ROOT / 'site-config.json').read_text(encoding='utf-8'))
    tables = {code: json.loads((ROOT / 'i18n' / f'{code}.json').read_text(encoding='utf-8')) for code in LOCALES}
    for code, values in tables.items():
        missing, extra = set(tables['en']) - set(values), set(values) - set(tables['en'])
        if missing or extra or any(not isinstance(v, str) or not v.strip() for v in values.values()):
            raise ValueError(f'{code}: missing={sorted(missing)}, extra={sorted(extra)} or empty/non-string value')
    return config, tables


def path_for(page, code):
    return ('' if code == 'zh-Hans' else f'{code}/') + ('' if page == 'home' else PAGES[page])


def page_url(config, page, code):
    return config['baseUrl'] + path_for(page, code)


def structured_data(config, data, page, code):
    base, url = config['baseUrl'], page_url(config, page, code)
    org_id, site_id = base + '#org', base + '#site'
    org = {'@type': 'Organization', '@id': org_id, 'name': config['publisher'], 'url': base,
           'logo': base + 'app-icon.png', 'email': config['supportEmail'],
           'contactPoint': {'@type': 'ContactPoint', 'contactType': 'technical support', 'email': config['supportEmail'], 'availableLanguage': LOCALES}}
    site = {'@type': 'WebSite', '@id': site_id, 'url': base, 'name': '听写笔记 · Dictation Notes',
            'inLanguage': LOCALES, 'publisher': {'@id': org_id}}
    apps = []
    for platform, facts in config['platforms'].items():
        apps.append({'@type': 'SoftwareApplication', '@id': base + '#' + platform + '-app',
                     'name': 'Dictation Notes', 'alternateName': '听写笔记', 'applicationCategory': 'BusinessApplication',
                     'operatingSystem': facts['operatingSystem'], 'softwareVersion': facts['version'],
                     'description': data['meta.homeDesc'], 'inLanguage': LOCALES, 'url': page_url(config, 'home', code),
                     'downloadUrl': facts['storeUrl'], 'installUrl': facts['storeUrl'], 'sameAs': facts['storeUrl'],
                     'image': base + 'og.png', 'publisher': {'@id': org_id},
                     'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD', 'url': facts['storeUrl'], 'description': data['home.available']},
                     'featureList': [data['home.factFreeV'], data['home.factTrialV'], data['home.paidBody']]})
    webpage = {'@type': 'ContactPage' if page == 'support' else 'WebPage', '@id': url + '#page',
               'url': url, 'name': data[f'meta.{page}Title'], 'description': data[f'meta.{page}Desc'],
               'dateModified': config['updated'], 'inLanguage': code, 'isPartOf': {'@id': site_id},
               'publisher': {'@id': org_id}, 'about': [{'@id': base + '#mac-app'}, {'@id': base + '#iphone-app'}]}
    crumbs = [{'@type': 'ListItem', 'position': 1, 'name': data['nav.home'], 'item': page_url(config, 'home', code)}]
    if page != 'home':
        crumbs.append({'@type': 'ListItem', 'position': 2, 'name': data[f'nav.{page}'], 'item': url})
    graph = [org, site, *apps, webpage, {'@type': 'BreadcrumbList', '@id': url + '#breadcrumbs', 'itemListElement': crumbs}]
    if page in ['home', 'support']:
        pairs = [(f'home.faq{i}q', f'home.faq{i}a') for i in range(1, 7)] if page == 'home' else [(f'support.q{i}', f'support.a{i}') for i in range(1, 15)]
        graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': data[q], 'acceptedAnswer': {'@type': 'Answer', 'text': data[a]}} for q, a in pairs]})
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2).replace('<', '\\u003c')


def render(config, tables, page, code):
    data = tables[code]
    base, asset = config['baseUrl'], config['basePath']
    revision = config['assetVersion']
    url = page_url(config, page, code)
    esc = lambda s: html.escape(str(s), quote=True)
    title, desc = data[f'meta.{page}Title'], data[f'meta.{page}Desc']
    alternate = '\n'.join(f'  <link rel="alternate" hreflang="{lang}" href="{page_url(config, page, lang)}">' for lang in LOCALES)
    links = '\n'.join(f'<a lang="{lang}" hreflang="{lang}" href="{asset}{path_for(page, lang)}"' + (' aria-current="true"' if lang == code else '') + f'>{LANG_NAMES[lang]}</a>' for lang in LOCALES)
    nav = '\n'.join(f'<a href="{asset}{path_for(target, code)}"' + (' aria-current="page"' if target == page else '') + f'>{esc(data[f"nav.{target}"])}</a>' for target in PAGES)
    special = {'asset': asset, 'mac.version': config['platforms']['mac']['version'], 'iphone.version': config['platforms']['iphone']['version'],
               'mac.hero': f'{asset}shots/mac/{code}/01-transcript-ai.jpg',
               'mac.notes': f'{asset}shots/mac/{code}/02-meeting-notes.jpg', 'mac.history': f'{asset}shots/mac/{code}/03-history.jpg',
               'iphone.hero': f'{asset}shots/iphone/{code}/01-hero.jpg', 'iphone.transcript': f'{asset}shots/iphone/{code}/02-transcript.jpg',
               'iphone.reply': f'{asset}shots/iphone/{code}/03-ai-reply.jpg',
               'mac.store': config['platforms']['mac']['storeUrl'], 'iphone.store': config['platforms']['iphone']['storeUrl'],
               **{f'url.{p}': asset + path_for(p, code) for p in PAGES}}
    def replace_token(match):
        key = match.group(1)
        if key not in data and key not in special:
            raise ValueError(f'Unknown template key {key}')
        return esc(special[key] if key in special else data[key])
    body = TOKEN.sub(replace_token, (ROOT / 'templates' / PAGES[page]).read_text(encoding='utf-8'))
    preload = f'  <link rel="preload" as="image" href="{special["mac.hero"]}" fetchpriority="high">' if page == 'home' else ''
    return f'''<!DOCTYPE html>
<!-- Generated by build-i18n.py. Edit templates/ and i18n/ instead. -->
<html lang="{code}" dir="{'rtl' if code == 'ar' else 'ltr'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="theme-color" content="#f8faff">
  <meta name="author" content="{esc(config['publisher'])}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="apple-itunes-app" content="app-id=6783130548">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="x-default" href="{page_url(config, page, 'zh-Hans')}">
{alternate}
  <link rel="alternate" type="text/plain" href="{base}llms.txt" title="Dictation Notes facts">
  <meta property="og:site_name" content="听写笔记 · Dictation Notes">
  <meta property="og:locale" content="{OG_LOCALES[code]}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{base}og.png?v={revision}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Dictation Notes · Mac &amp; iPhone">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{base}og.png?v={revision}">
  <link rel="icon" href="{asset}favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{asset}apple-touch-icon.png">
{preload}
  <link rel="stylesheet" href="{asset}fonts/fonts.css?v={revision}">
  <link rel="stylesheet" href="{asset}styles.css?v={revision}">
  <script type="application/ld+json">{structured_data(config, data, page, code)}</script>
  <script src="{asset}site.js?v={revision}" defer></script>
</head>
<body data-page="{page}" data-base="{asset}">
  <a class="skip" href="#main">{esc(data['skip'])}</a>
  <header class="wrap site-header">
    <a class="brand" href="{asset}{path_for('home', code)}"><img class="brand-icon" src="{asset}app-icon.png" width="32" height="32" alt=""><span class="brand-name">{esc(data['brand'])}</span></a>
    <nav class="nav" aria-label="{esc(data['nav.label'])}">{nav}</nav>
    <details class="language-menu"><summary>{esc(data['lang.label'])} · {LANG_NAMES[code]}</summary><nav aria-label="{esc(data['lang.label'])}">{links}</nav></details>
  </header>
  {body}
  <footer class="wrap site-footer">
    <nav aria-label="{esc(data['nav.label'])}">{nav}<a href="https://apps.apple.com/app/id6783130548">{esc(data['footer.store'])}</a><a href="mailto:{config['supportEmail']}">{config['supportEmail']}</a></nav>
    <p>{esc(data['footer.seller'])}</p><p>{esc(data['footer.copy'])}</p>
  </footer>
</body>
</html>
'''


def build_outputs(config, tables):
    outputs = {name if code == 'zh-Hans' else f'{code}/{name}': render(config, tables, page, code) for code in LOCALES for page, name in PAGES.items()}
    ns, xhtml = 'http://www.sitemaps.org/schemas/sitemap/0.9', 'http://www.w3.org/1999/xhtml'
    ET.register_namespace('', ns)
    ET.register_namespace('xhtml', xhtml)
    urlset = ET.Element(f'{{{ns}}}urlset')
    for page in PAGES:
        for code in LOCALES:
            node = ET.SubElement(urlset, f'{{{ns}}}url')
            ET.SubElement(node, f'{{{ns}}}loc').text = page_url(config, page, code)
            ET.SubElement(node, f'{{{ns}}}lastmod').text = config['updated']
            for lang in [*LOCALES, 'x-default']:
                ET.SubElement(node, f'{{{xhtml}}}link', {'rel': 'alternate', 'hreflang': lang, 'href': page_url(config, page, 'zh-Hans' if lang == 'x-default' else lang)})
    ET.indent(urlset)
    outputs['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(urlset, encoding='unicode') + '\n'
    facts = {**config, 'interfaceLanguages': LOCALES, 'historySync': False,
             'downloadPriceUSD': 0, 'lifetimeUnlock': {'productId': 'com.wzc.jinnangmiaoji.lifetime', 'type': 'non-consumable', 'trialUses': 20, 'subscription': False, 'providerFeesIncluded': False},
             'summary': {lang: tables[lang]['home.lead'] for lang in ['en', 'zh-Hans']},
             'privacy': {key: tables['en'][key] for key in ['privacy.p1', 'privacy.pLocal', 'privacy.pApple', 'privacy.pProviders', 'privacy.pCloudData', 'privacy.pRetention', 'privacy.pRights', 'privacy.pSupport']}}
    outputs['app-facts.json'] = json.dumps(facts, ensure_ascii=False, indent=2) + '\n'
    base = config['baseUrl']
    outputs['llms.txt'] = f'''# Dictation Notes · 听写笔记

> Native Mac and iPhone live transcription, meeting notes and optional AI reply cues. Both apps are released on the App Store. Updated {config['updated']}.

## Official pages
- [Product]({base}en/): Mac 1.1.0 / macOS 14+, iPhone 1.0.1 / iOS 17+; screenshots, platform differences and pricing.
- [Support]({base}en/support.html): Setup, system audio permission, purchase restoration, exports and recording deletion.
- [Privacy]({base}en/privacy.html): Local storage, Apple Speech, user-selected providers, data retention and deletion.
- [Terms]({base}en/terms.html): One-time unlock, separate provider fees, recording responsibility and Apple EULA.
- [Full product facts]({base}llms-full.txt): Source-linked factual reference.
- [Structured facts]({base}app-facts.json): Platform versions and factual data.
- [中文官网]({base}): 中文产品、支持、隐私与条款。

## Key facts
Free installation and free Apple Speech dictation. Cloud transcription, live translation and AI share 20 trial uses, then an optional one-time unlock. Bring your own provider credentials; provider fees are separate. Restore the unlock with the same Apple ID on Mac and iPhone. History and recordings do not automatically sync. Apple Speech may send audio to Apple when local recognition is unavailable. The publisher has no application content backend; selected providers may collect, retain or train on data under their own policies.
'''
    sections = [('Platforms', 'home.platformsBody'), ('Mac workflow', 'home.macBody'), ('Recording controls', 'home.notBody'), ('Free features', 'home.freeBody'), ('Purchase and provider fees', 'home.paidBody'), ('Restore purchases', 'support.a8'), ('History and sync', 'home.faq5a'), ('Audio and privacy', 'home.faq3a'), ('Mac system audio', 'support.a9'), ('Export and playback', 'support.a10'), ('Delete a recording', 'support.a11'), ('Revoke permission', 'support.a12'), ('Legacy history', 'support.a13'), ('Local AI', 'support.a14'), ('Cloud collection', 'privacy.pCloudData'), ('Provider retention', 'privacy.pRetention'), ('Local controls', 'privacy.pRights'), ('Support email data', 'privacy.pSupport'), ('Website', 'privacy.pSite')]
    blocks = [f'# Dictation Notes · 听写笔记\n\nLast verified: {config["updated"]}. Official app id: 6783130548. Publisher: {config["publisher"]}. Contact: {config["supportEmail"]}.',
              f'## Distribution\n\nMac: {config["platforms"]["mac"]["storeUrl"]}\niPhone: {config["platforms"]["iphone"]["storeUrl"]}\nMac 1.1.0: macOS 14+, Apple Silicon and Intel. iPhone 1.0.1: iOS 17+.\nInterface and website: {", ".join(LOCALES)}.\nProduct: {base}en/\nSupport: {base}en/support.html\nPrivacy: {base}en/privacy.html\nTerms: {base}en/terms.html']
    for heading, key in sections:
        blocks.append(f'## {heading}\n\n{tables["en"][key]}\n\n{tables["zh-Hans"][key]}')
    blocks.append('## Accuracy boundaries\n\nUse the name Dictation Notes or 听写笔记. Cite the official product, support or privacy page for the corresponding fact. Say 20 trial uses and a one-time unlock. Keep Mac recording controls separate from iPhone foreground restrictions. Do not infer history sync from purchase restoration. Do not describe Apple Speech as guaranteed offline or providers as universally zero-retention. Do not invent ratings, adoption, prices for other storefronts or unverified performance claims. The privacy page is the authoritative policy; this reference summarizes it.')
    outputs['llms-full.txt'] = '\n\n'.join(blocks) + '\n'
    # Project robots.txt is not an origin-root crawler directive on GitHub Pages.
    outputs['robots.txt'] = f'User-agent: *\nAllow: /jinnangmiaoji-cue/\n\nSitemap: {base}sitemap.xml\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare generated output without writing')
    args = parser.parse_args()
    config, tables = read_data()
    outputs = build_outputs(config, tables)
    differences = []
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                differences.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if differences:
        raise SystemExit('Generated files need rebuilding: ' + ', '.join(differences))
    print(f'{"Checked" if args.check else "Built"} 52 localized pages, sitemap and assistant facts; {len(tables["en"])} keys × 13 languages.')


if __name__ == '__main__':
    main()
