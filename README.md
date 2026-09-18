# Dictation Notes site

Static GitHub Pages for the launched App Store product **听写笔记 / Dictation Notes**.

- Marketing: `index.html`
- Support: `support.html`
- Privacy: `privacy.html`
- Terms: `terms.html`
- Assistant facts: `llms.txt`, `llms-full.txt`

Public URLs:

- https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/
- https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/support.html
- https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/privacy.html
- https://weizhichao1027-collab.github.io/jinnangmiaoji-cue/terms.html

App Store: https://apps.apple.com/app/id6783130548

After changing copy, edit `i18n/*.json` (English is the master; `zh-Hans` must cover every key), then run:

```bash
python3 build-i18n.py
```

Commit and push this folder’s own git remote (`jinnangmiaoji-cue`). Do not nest this `.git` inside the parent app repo.
