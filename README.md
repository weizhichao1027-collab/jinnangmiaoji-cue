# Dictation Notes website

Updated on 2026-11-14 for the released Mac **1.2.2** and iOS **1.1.1** apps. The mobile app supports iPhone, iPad and companion Apple Watch recording. This repository maintains the official product, support, privacy and terms pages in 13 languages.

- [Product](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/)
- [Support](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/support.html)
- [Privacy](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/privacy.html)
- [Terms](https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/terms.html)
- [Mac download](https://apps.apple.com/app/id6783130548?platform=mac) and [iPhone / iPad download](https://apps.apple.com/app/id6783130548?platform=iphone)

## Maintained sources

This is the independent repository `weizhichao1027-collab/jinnangmiaoji-cue`. The product repository ignores `store-site/`. Commit and push the website separately. GitHub Pages publishes `main` from the repository root. Preserve `.nojekyll` for the static output.

| Source | Purpose |
| --- | --- |
| `templates/*.html` | Product, support, privacy and terms layouts |
| `i18n/*.json` | All 13 localized texts and metadata |
| `site-config.json` | Public URLs, released versions, requirements, publisher and date |
| `build-i18n.py` | HTML, JSON-LD, sitemap and source-linked factual references |
| `styles.css`, `site.js` | Responsive layout, RTL, focus and legacy language links |
| `prepare-release-assets.py` | Reproducible conversion of approved promotional PNGs |
| `shots/release-20261114/manifest.json` | Provenance and output hashes for 104 current JPEGs |
| `social-preview.html` | 1200 × 630 sharing-image source, rendered to `og.png` |

Run from this directory with Python 3 and Node.js.

```sh
python3 build-i18n.py
python3 build-i18n.py --check
python3 verify-site.py
python3 test-site-builder.py
node --check site.js
git diff --check
```

The site builder uses Python's standard library. Screenshot preparation additionally requires Pillow. From the complete product workspace, run `python3 prepare-release-assets.py`. From a standalone site checkout, pass `--source-root` pointing to the product workspace's `docs/designs/store-previews-2026-11-12/` directory. Originals stay in that product archive. The manifest records relative source paths, dimensions, SHA-256 and output byte counts.

Commit generated HTML, sitemap, factual references and webpage assets with their maintained sources. `--check` compares output without writing. The verifier checks metadata, language alternatives, internal links and anchors, image dimensions, platform facts and FAQ answers against visible text.

## Release content

The current pages cover mobile recording, pause/resume, later transcription, precise playback, daily reviews, highlight collections, passage-based AI work and source checking. Watch help covers Pro activation on the paired iPhone, transfers, safe receipt and retained originals. iPad receives Watch material through manual backup transfer from the paired iPhone. Mac retains its native microphone/system-audio workflow, save recovery, transcript search, audio export and verified library migration.

iOS offers one optional 7-day Pro trial lasting 168 consecutive hours. Mac has 20 shared cloud transcription, AI and translation trial uses. A lifetime purchase unlocks Pro. Existing valid purchases and qualifying legacy rights remain recognized. Provider credentials and charges are supplied separately by the user. The current App Store determines local prices.

Privacy describes selected text and titles sent for review, local source snapshots, Watch copies, provider consent, Apple Speech, Keychain, system backups and deletion scope. Purchase restoration restores access. Each device keeps its own library, with Watch-to-paired-iPhone transfer described separately.

## URLs and language behavior

Simplified Chinese keeps the existing root URLs. Other languages use `/en/`, `/zh-Hant/`, `/ja/`, `/ko/`, `/es/`, `/fr/`, `/de/`, `/pt-BR/`, `/ru/`, `/ar/`, `/hi/` and `/id/`. Each has all four pages, totaling 52 static pages. Links and language navigation work without JavaScript. Explicit legacy `?lang=` links redirect to their language path and preserve fragments. Browser language does not trigger a redirect.

Fonts are self-hosted Atkinson Hyperlegible and IBM Plex Mono WOFF2 with licenses in `fonts/`. The F2 ribbon icon and light blue branding continue across all pages. Current device screenshots come from the approved November 12–13 artwork. Their conversations, AI answers and displayed durations are examples. Earlier screenshot URLs stay available for existing links.

Bump `assetVersion` when shared assets change and keep `404.html` in sync. To render `og.png`, open `social-preview.html` at 1200 × 630 and capture the viewport after fonts and images load.

For browser QA, serve this checkout at the actual project path `/jinnangmiaoji-cue/`, using a temporary parent directory with a matching symlink. Check 375/768/1440px, Arabic RTL, keyboard focus, language switching, old query links and a JavaScript-disabled page.

## SEO and factual retrieval

Each page has a localized title and description, self-canonical, 13 reciprocal `hreflang` alternatives and `x-default`, social metadata and JSON-LD. Product pages describe the two software applications, current versions and device screenshots. Support and legal pages provide breadcrumbs. FAQ structured answers come from visible page content. Free-install offers describe the download price, with Pro and provider terms in visible copy.

`sitemap.xml` lists all 52 canonical URLs and their language alternatives. `app-facts.json` contains 42 factual topics with text and matching visible source links in all 13 languages. `llms.txt` and `llms-full.txt` provide additional source-linked references. Page heads link to the sitemap and facts. The release verifier checks the iOS timed trial and Mac usage policy independently.

GitHub Pages hosts this project under a path. Crawlers use `https://weizhichao1027-collab.github.io/robots.txt` for origin policy. The project's own `robots.txt` provides a useful sitemap reference at the project URL. Submit `sitemap.xml` through a verified Search Console property when account access is available. Site publication and automated checks establish deployment and content consistency. Search engines control indexing, ranking, rich results and AI citations.

Google's guidance for AI features uses crawlable, helpful text and structured data that agrees with visible content. It requires no special AI file or schema. The source-linked files here help retrieval and factual consistency. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features), [multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites), [robots.txt location](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt).
