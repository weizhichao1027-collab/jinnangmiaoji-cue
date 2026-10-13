#!/usr/bin/env python3
"""Check crawlability, metadata, linked assets and visible structured answers."""
import argparse
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'build-i18n.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes, self.ids, self.text, self.jsonld = [], [], [], []
        self.script = None
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.nodes.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'script':
            self.script = [] if attrs.get('type') == 'application/ld+json' else False

    def handle_endtag(self, tag):
        if tag == 'script':
            if isinstance(self.script, list):
                self.jsonld.append(json.loads(''.join(self.script)))
            self.script = None

    def handle_data(self, data):
        if isinstance(self.script, list):
            self.script.append(data)
        elif self.script is None:
            self.text.append(data)


def verify():
    config, tables = builder.read_data()
    base = config['baseUrl']
    documents = {}
    for code in builder.LOCALES:
        for page, filename in builder.PAGES.items():
            path = ROOT / (filename if code == 'zh-Hans' else f'{code}/{filename}')
            source = path.read_text(encoding='utf-8')
            assert '{{' not in source and 'data-i18n=' not in source, f'{path}: unresolved copy'
            doc = Document(source)
            url = builder.page_url(config, page, code)
            documents[url] = doc
            assert len(doc.ids) == len(set(doc.ids)), f'{path}: duplicate IDs'
            assert sum(tag == 'h1' for tag, _ in doc.nodes) == 1, f'{path}: h1'
            root = next(attrs for tag, attrs in doc.nodes if tag == 'html')
            assert root['lang'] == code and root['dir'] == ('rtl' if code == 'ar' else 'ltr')
            canonicals = [attrs['href'] for tag, attrs in doc.nodes if tag == 'link' and attrs.get('rel') == 'canonical']
            assert canonicals == [url], f'{path}: canonical'
            alternates = {attrs['hreflang']: attrs['href'] for tag, attrs in doc.nodes if tag == 'link' and 'hreflang' in attrs}
            expected = {lang: builder.page_url(config, page, lang) for lang in builder.LOCALES}
            expected['x-default'] = builder.page_url(config, page, 'zh-Hans')
            assert alternates == expected, f'{path}: hreflang'
            meta = {attrs.get('name', attrs.get('property')): attrs.get('content') for tag, attrs in doc.nodes if tag == 'meta'}
            assert meta['description'] == tables[code][f'meta.{page}Desc']
            assert meta['og:url'] == url and meta['twitter:card'] == 'summary_large_image'
            assert meta['robots'].startswith('index,follow')
            assert len(doc.jsonld) == 1, f'{path}: JSON-LD'
            graph = doc.jsonld[0]['@graph']
            apps = [node for node in graph if node['@type'] == 'SoftwareApplication']
            assert len(apps) == 2
            assert {node['softwareVersion'] for node in apps} == {facts['version'] for facts in config['platforms'].values()}
            assert all(node['offers']['price'] == '0' for node in apps)
            visible = ' '.join(' '.join(doc.text).split())
            faqs = [node for node in graph if node['@type'] == 'FAQPage']
            if page in ('home', 'support'):
                assert len(faqs) == 1 and len(faqs[0]['mainEntity']) == (6 if page == 'home' else 14)
                for question in faqs[0]['mainEntity']:
                    assert ' '.join(question['name'].split()) in visible
                    assert ' '.join(question['acceptedAnswer']['text'].split()) in visible, f'{path}: FAQ differs from visible answer'
            else:
                assert not faqs
            if page in ('privacy', 'terms'):
                assert config['updated'] in visible, f'{path}: policy date'
            for tag, attrs in doc.nodes:
                if tag == 'img':
                    assert 'alt' in attrs and attrs.get('width') and attrs.get('height'), f'{path}: image dimensions/alt'

    checked_links = 0
    for url, doc in documents.items():
        for tag, attrs in doc.nodes:
            reference = attrs.get('href') if tag in ('a', 'link') else attrs.get('src') if tag in ('img', 'script') else None
            if not reference:
                continue
            resolved = urlsplit(urljoin(url, reference))
            if resolved.netloc != urlsplit(base).netloc:
                continue
            path = unquote(resolved.path)
            assert path.startswith(config['basePath']), f'{url}: link outside site {reference}'
            relative = path[len(config['basePath']):]
            target = ROOT / relative
            if path.endswith('/'):
                target /= 'index.html'
            assert target.is_file(), f'{url}: missing target {reference}'
            if resolved.fragment:
                target_doc = documents.get(resolved._replace(fragment='', query='').geturl()) or Document(target.read_text())
                assert resolved.fragment in target_doc.ids, f'{url}: broken anchor {reference}'
            checked_links += 1

    sitemap = ET.parse(ROOT / 'sitemap.xml').getroot()
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
    urls = sitemap.findall('s:url', ns)
    assert len(urls) == 52 and {node.find('s:loc', ns).text for node in urls} == set(documents)
    assert all(len(node.findall('x:link', ns)) == 14 for node in urls)
    facts = json.loads((ROOT / 'app-facts.json').read_text())
    assert facts['historySync'] is False and facts['lifetimeUnlock']['trialUses'] == 20
    assert facts['platforms'] == config['platforms']
    assert (ROOT / '.nojekyll').exists()
    return {'status': 'passed', 'pages': len(documents), 'locales': len(tables),
            'translationKeysPerLocale': len(tables['en']), 'linksAndAssets': checked_links,
            'sitemapUrls': len(urls), 'faqAnswersMatched': 13 * (6 + 14),
            'checks': ['static content', 'canonical and reciprocal hreflang', 'local links and anchors',
                       'JSON-LD and visible FAQ agreement', 'image dimensions and alt', 'sitemap', 'product facts']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
