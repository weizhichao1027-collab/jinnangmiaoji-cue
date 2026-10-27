#!/usr/bin/env python3
"""Check crawlability, metadata, linked assets and visible structured answers."""
import argparse
import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'build-i18n.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def image_dimensions(path):
    """Read PNG/JPEG dimensions without adding a site-build dependency."""
    data = path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')
    if data.startswith(b'\xff\xd8'):
        position = 2
        while position < len(data):
            assert data[position] == 0xFF, f'{path}: malformed JPEG marker'
            while data[position] == 0xFF:
                position += 1
            marker = data[position]
            position += 1
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            length = int.from_bytes(data[position:position + 2], 'big')
            assert length >= 2, f'{path}: malformed JPEG segment'
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return int.from_bytes(data[position + 5:position + 7], 'big'), int.from_bytes(data[position + 3:position + 5], 'big')
            position += length
    raise ValueError(f'{path}: unsupported or invalid image')


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
    faq_answers = 0
    checked_dimensions = 0
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
            ids = [node['@id'] for node in graph]
            assert len(ids) == len(set(ids)), f'{path}: duplicate structured entities'
            assert not any('aggregateRating' in node or 'review' in node for node in graph), f'{path}: unmaintained rating/review'
            apps = [node for node in graph if node['@type'] == 'SoftwareApplication']
            assert len(apps) == (len(config['platforms']) if page == 'home' else 0), f'{path}: app schema belongs on product page'
            visible = ' '.join(' '.join(doc.text).split())
            for app in apps:
                platform = app['@id'].removeprefix(base + '#').removesuffix('-app')
                platform_facts = config['platforms'][platform]
                assert app['softwareVersion'] == platform_facts['version']
                assert app['operatingSystem'] == platform_facts['operatingSystem']
                assert app['downloadUrl'] == app['installUrl'] == app['offers']['url'] == platform_facts['storeUrl']
                assert app['offers']['price'] == '0'
                assert all(' '.join(feature.split()) in visible for feature in app['featureList']), f'{path}: feature not visible'
            webpage = next(node for node in graph if node['@id'] == url + '#page')
            assert webpage['dateModified'] == config['updated'] and webpage['inLanguage'] == code
            crumbs = [node for node in graph if node['@type'] == 'BreadcrumbList']
            assert len(crumbs) == (0 if page == 'home' else 1)
            if crumbs:
                assert [entry['item'] for entry in crumbs[0]['itemListElement']] == [builder.page_url(config, 'home', code), url]
            faqs = [node for node in graph if node['@type'] == 'FAQPage']
            if page in ('home', 'support'):
                pairs = builder.faq_pairs(page)
                assert len(faqs) == 1 and len(faqs[0]['mainEntity']) == len(pairs)
                assert webpage['hasPart']['@id'] == faqs[0]['@id']
                for question in faqs[0]['mainEntity']:
                    assert ' '.join(question['name'].split()) in visible
                    assert ' '.join(question['acceptedAnswer']['text'].split()) in visible, f'{path}: FAQ differs from visible answer'
                    faq_answers += 1
            else:
                assert not faqs
            if page in ('privacy', 'terms'):
                assert config['updated'] in visible, f'{path}: policy date'
            for tag, attrs in doc.nodes:
                if tag == 'img':
                    assert 'alt' in attrs and attrs.get('width') and attrs.get('height'), f'{path}: image dimensions/alt'
                    image_url = urlsplit(urljoin(url, attrs['src']))
                    image_path = ROOT / unquote(image_url.path).removeprefix(config['basePath'])
                    width, height = image_dimensions(image_path)
                    declared = int(attrs['width']), int(attrs['height'])
                    assert width * declared[1] == height * declared[0], f'{path}: image aspect ratio {attrs["src"]}'
                    if 'shots/' in attrs['src']:
                        assert (width, height) == declared, f'{path}: screenshot intrinsic dimensions {attrs["src"]}'
                    checked_dimensions += 1

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
    assert len(urls) == len(documents) and {node.find('s:loc', ns).text for node in urls} == set(documents)
    for node in urls:
        location = node.find('s:loc', ns).text
        assert node.find('s:lastmod', ns).text == config['updated']
        page = next(page for page in builder.PAGES if any(builder.page_url(config, page, code) == location for code in builder.LOCALES))
        expected = {lang: builder.page_url(config, page, lang) for lang in builder.LOCALES}
        expected['x-default'] = builder.page_url(config, page, 'zh-Hans')
        actual = {link.attrib['hreflang']: link.attrib['href'] for link in node.findall('x:link', ns)}
        assert actual == expected, f'{location}: sitemap hreflang'
    facts = json.loads((ROOT / 'app-facts.json').read_text())
    assert facts['historySync'] is False and facts['lifetimeUnlock']['trialUses'] == 20
    assert facts['platforms'] == config['platforms']
    assert facts['updated'] == config['updated'] and facts['appStoreId'] == '6783130548'
    assert set(facts['summary']) == set(builder.LOCALES)
    source_links = 0
    for topic in facts['topics']:
        for code, reference in topic['sources'].items():
            parsed = urlsplit(reference)
            canonical = parsed._replace(fragment='', query='').geturl()
            assert canonical in documents, f'unknown fact source: {reference}'
            document = documents[canonical]
            assert not parsed.fragment or parsed.fragment in document.ids, f'unknown fact anchor: {reference}'
            assert ' '.join(topic['text'][code].split()) in ' '.join(' '.join(document.text).split()), f'fact differs from source: {reference}'
            source_links += 1
    for filename in ('llms.txt', 'llms-full.txt'):
        content = (ROOT / filename).read_text(encoding='utf-8')
        assert config['updated'] in content
        assert f'Mac {config["platforms"]["mac"]["version"]}' in content
        assert f'iPhone {config["platforms"]["iphone"]["version"]}' in content
        for reference in re.findall(r'\]\((https://[^)]+)\)', content):
            parsed = urlsplit(reference)
            if parsed.netloc != urlsplit(base).netloc:
                continue
            canonical = parsed._replace(fragment='', query='').geturl()
            if canonical in documents:
                assert not parsed.fragment or parsed.fragment in documents[canonical].ids, f'{filename}: bad source anchor'
            else:
                assert (ROOT / parsed.path.removeprefix(config['basePath'])).is_file(), f'{filename}: missing source'
            source_links += 1
    assert f'Sitemap: {base}sitemap.xml' in (ROOT / 'robots.txt').read_text()
    assert image_dimensions(ROOT / 'og.png') == (1200, 630), 'social sharing image dimensions'
    assert (ROOT / '.nojekyll').exists()
    return {'status': 'passed', 'pages': len(documents), 'locales': len(tables),
            'translationKeysPerLocale': len(tables['en']), 'linksAndAssets': checked_links,
            'sitemapUrls': len(urls), 'faqAnswersMatched': faq_answers, 'factSourceLinks': source_links,
            'imageDimensionsChecked': checked_dimensions,
            'checks': ['static content', 'canonical and reciprocal hreflang', 'local links and anchors',
                       'page-specific JSON-LD and visible FAQ agreement', 'image dimensions and alt',
                       'sitemap language alternatives and modification dates', 'source-linked product facts', 'dynamic platform versions']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
