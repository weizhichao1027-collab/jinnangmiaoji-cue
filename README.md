# Dictation Notes website

Official GitHub Pages for the released **听写笔记 / Dictation Notes** Mac and iPhone apps. Updated 2026-10-13 for Mac 1.1.0 (macOS 14+, Apple Silicon / Intel) and iPhone 1.0.1 (iOS 17+).

- [Product](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/)
- [Support](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/support.html)
- [Privacy](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/privacy.html)
- [Terms](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/terms.html)
- [Mac download](https://apps.apple.com/app/id6783130548?platform=mac) / [iPhone download](https://apps.apple.com/app/id6783130548?platform=iphone)

## Content and generation

This is a separate repository, `weizhichao1027-collab/jinnangmiaoji-cue`; the app repository ignores `store-site/`. Commit and push each repository separately. GitHub Pages publishes `main` from the repository root; `.nojekyll` keeps these generated files intact.

Edit the maintained sources:

| Source | Purpose |
| --- | --- |
| `templates/*.html` | Product, support, privacy and terms layouts |
| `i18n/*.json` | Complete copy in all 13 languages, including page titles and descriptions |
| `site-config.json` | Public URLs, platform versions, requirements, publisher and update date |
| `styles.css` | Responsive light/blue brand, focus styles and RTL layout |
| `site.js` | Compatibility for old explicit `?lang=` links and Escape on the language menu |
| `PRODUCT.md` | Brand, factual and accessibility requirements |

Run from this directory with Python 3 and Node.js:

```sh
python3 build-i18n.py
python3 build-i18n.py --check
python3 verify-site.py
node --check site.js
git diff --check
```

The build uses only Python's standard library. Commit the generated HTML, sitemap and facts along with their sources. `--check` compares output without writing. `verify-site.py` checks metadata, language alternatives, local links and anchors, image dimensions, product facts, and FAQ answers against visible text. It does not certify search indexing or complete accessibility conformance.

Simplified Chinese keeps the existing root URLs. Other languages use `/en/`, `/zh-Hant/`, `/ja/`, `/ko/`, `/es/`, `/fr/`, `/de/`, `/pt-BR/`, `/ru/`, `/ar/`, `/hi/` and `/id/`. Each has all four pages, totaling 52 static pages. Links and language navigation work without JavaScript. The former `?lang=en-US` and other regional language tags redirect only when explicitly requested in the URL; the fragment is preserved. There is no browser-language redirect, preference storage or client-side translation payload.

When publishing a new app version, also update version references in localized copy, policy dates where appropriate, screenshots and the app's handoff. Requirements in `site-config.json` describe the app; visible platform comparison copy must agree.

## Assets

`shots/mac/<locale>/` contains three 1280 × 800 JPEGs per language, derived from the application's real localized Mac screenshot sources in `docs/mac-store-artwork/v1/raw/`. `shots/iphone/<locale>/` contains three 660 × 1434 JPEGs per language from the corresponding retained App Store previews. The displayed conversations and AI responses are demonstration content. Older screenshot URLs remain available for compatibility.

Fonts are self-hosted WOFF2: Atkinson Hyperlegible (400/700) and IBM Plex Mono (400), with a system sans-serif display. Their OFL licenses are in `fonts/`. No fonts, analytics or tracking scripts load from a third party.

`social-preview.html` is a non-indexed 1200 × 630 sharing artwork source; render it at that viewport to update `og.png`. The artwork uses the same light palette and a real Mac image.

For local browser QA, serve this checkout at the real project path `/jinnangmiaoji-cue/`, for example with a temporary parent directory containing a `jinnangmiaoji-cue` symlink to this checkout. Opening files directly does not emulate Pages paths. Check 375/768/1440px, Arabic RTL, keyboard focus, language switching and old query links.

## SEO and assistant facts

Each page has a localized title and description, a self-canonical URL, 13 reciprocal `hreflang` alternatives plus `x-default`, social metadata and JSON-LD. Software applications describe the two released platform versions. The zero-price offer describes free installation; cloud/AI unlocking and provider fees remain explicit in visible copy. There are no fabricated ratings, reviews or usage statistics. Homepage/support FAQ data matches the displayed answers.

`sitemap.xml` lists all 52 canonical URLs and language alternatives. GitHub Pages hosts this project under a path: the project's `robots.txt` is **not** the origin-root crawler policy. Crawlers look for `https://weizhichao1027-collab.github.io/robots.txt`; use a verified Search Console property to submit the sitemap if desired. No Search Console verification or submission was performed by this update.

`llms.txt`, `llms-full.txt` and `app-facts.json` give linked, consistent product facts. They distinguish Mac controls from iPhone foreground restrictions, purchase restoration from history sync, Apple processing from selected providers, and app purchase from provider charges. These files support accurate retrieval; publication does not guarantee indexing, rich results or AI citations.

Guidance: [Google multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites), [robots.txt location](https://developers.google.com/search/docs/crawling-indexing/robots/intro).
