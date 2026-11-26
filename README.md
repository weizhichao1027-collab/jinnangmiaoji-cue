# Dictation Notes website

Updated on 2026-11-26 for the released iPhone, iPad and Watch **1.1.3** apps and the still-current Mac **1.2.3** app. This repository maintains the official product, support, privacy and terms pages in 13 languages.

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
| `shots/release-20261114/manifest.json` | Mac webpage images for the live 1.2.3 release, plus the earlier mobile set kept for existing URLs |
| `shots/release-20261126/manifest.json` | iPhone, iPad and Watch images used by the live 1.1.3 pages |
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

The site builder uses Python's standard library. Screenshot preparation additionally requires Pillow. From the complete product workspace, run `python3 prepare-release-assets.py` for the earlier 104-image set, or `python3 prepare-release-assets.py --mobile-20261126` for the live iPhone, iPad and Watch images. The mobile command reads `docs/designs/store-previews-2026-11-24/`. Originals stay in that product archive. Each manifest records relative source paths, dimensions, SHA-256 and output byte counts.

Commit generated HTML, sitemap, factual references and webpage assets with their maintained sources. `--check` compares output without writing. The verifier checks metadata, language alternatives, internal links and anchors, image dimensions, platform facts and FAQ answers against visible text.

## Release content

Current pages cover iPhone, iPad and Watch 1.1.3 and Mac 1.2.3. On iPhone and iPad, a note opens as transcript, summary and highlights. The summary is one piece that can be regenerated or edited. Highlights replay from their time. While dictating, AI can suggest a reply, explain, challenge or anticipate after the recipient is shown and the user agrees. Search marks the words the user typed. Mac 1.2.3 remains the Mac release on sale: light and dark appearance, reading notes while recording, long-transcript organization, and Recently Deleted restore within 30 days. Its cloud transcription, AI and translation trial is still 20 shared uses. Mac 1.2.4 is not described as the current store version.

iPhone and iPad 1.1.3 offer one optional 7-day Pro trial lasting 168 consecutive hours. A lifetime purchase unlocks Pro. Existing valid purchases and qualifying legacy rights remain recognized. Provider credentials and charges are supplied separately by the user. The current App Store determines local prices.

Privacy describes on-device transcripts, summaries and highlights, text the user agrees to send for a regenerated summary or a live cue, selected review text, Watch copies, Recently Deleted retention, provider consent, Apple Speech, Keychain, system backups and deletion scope. The current releases do not request location. Purchase restoration restores access. Each device keeps its own library, with Watch-to-paired-iPhone transfer described separately.

## URLs and language behavior

Simplified Chinese keeps the existing root URLs. Other languages use `/en/`, `/zh-Hant/`, `/ja/`, `/ko/`, `/es/`, `/fr/`, `/de/`, `/pt-BR/`, `/ru/`, `/ar/`, `/hi/` and `/id/`. Each has all four pages, totaling 52 static pages. Links and language navigation work without JavaScript. Explicit legacy `?lang=` links redirect to their language path and preserve fragments. Browser language does not trigger a redirect.

Fonts are self-hosted Atkinson Hyperlegible and IBM Plex Mono WOFF2 with licenses in `fonts/`. The F2 ribbon icon and light blue branding continue across all pages. iPhone, iPad and Watch images are the 2026-11-24 store artwork now shown with iOS 1.1.3. Mac images remain the live 1.2.3 set. Conversations, AI answers and displayed durations are examples. Earlier screenshot URLs stay available for existing links.

Bump `assetVersion` when shared assets change and keep `404.html` in sync. To render `og.png`, open `social-preview.html` at 1200 × 630 and capture the viewport after fonts and images load.

For browser QA, serve this checkout at the actual project path `/jinnangmiaoji-cue/`, using a temporary parent directory with a matching symlink. Check 375/768/1440px, Arabic RTL, keyboard focus, language switching, old query links and a JavaScript-disabled page.

## SEO and factual retrieval

Each page has a localized title and description, self-canonical, 13 reciprocal `hreflang` alternatives and `x-default`, social metadata and JSON-LD. Product pages describe the two software applications, current versions and device screenshots. Support and legal pages provide breadcrumbs. FAQ structured answers come from visible page content. Free-install offers describe the download price, with Pro and provider terms in visible copy.

`sitemap.xml` lists all 52 canonical URLs and their language alternatives. `app-facts.json` contains factual topics with text and matching visible source links in all 13 languages. `llms.txt` and `llms-full.txt` provide additional source-linked references. Page heads link to the sitemap and facts. The release verifier checks the iOS timed trial and Mac usage policy independently.

GitHub Pages hosts this project under a path. Crawlers use `https://weizhichao1027-collab.github.io/robots.txt` for origin policy. The project's own `robots.txt` provides a useful sitemap reference at the project URL. Submit `sitemap.xml` through a verified Search Console property when account access is available. Site publication and automated checks establish deployment and content consistency. Search engines control indexing, ranking, rich results and AI citations.

Google's guidance for AI features uses crawlable, helpful text and structured data that agrees with visible content. It requires no special AI file or schema. The source-linked files here help retrieval and factual consistency. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features), [multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites), [robots.txt location](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt).
