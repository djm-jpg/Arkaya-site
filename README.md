# Arkaya-site

Source of **arkayarisk.com**. Static HTML in the live design system (Fraunces / IBM Plex), served by
Netlify from `main` with no build step.

Operating rules — what you may change, what must never be edited in place, the agent surface and the
language constraints — are in **[CLAUDE.md](CLAUDE.md)**. Read that before editing. This file is
orientation only.

## Layout

Flat. Every page sits at the repository root; `.well-known/` and `get/` are the only content
subdirectories.

```
index.html  schema.html  evidence.html  solutions.html  doctrine.html
library.html  standard.html  founder.html  ecosystem.html  infinity.html
_redirects  _headers  robots.txt  llms.txt  sitemap.xml
.well-known/governance-evidence.json     machine-readable index of the open Layer 1 material
get/index.html                           Layer 1 implementer pack page
get/v1/                                  the pack itself, hash-pinned — never edit in place
```

## Deploy

1. Branch off `main`.
2. Add file → Upload files → drag the changed and new files. Commit, open PR.
3. Check the Netlify deploy preview: every page 200 at its pretty URL; `/llms.txt`, `/robots.txt`,
   `/sitemap.xml`, `/.well-known/governance-evidence.json` and `/get/v1/MANIFEST.json` all 200; a
   PDF still serves.
4. Merge. Netlify publishes to the live domain in seconds.

There is no staging environment. The preview is the only place to look before the site is live.

## The company

Arkaya Risk Limited, registered in England and Wales, no. 17380022. Registered office: Oxford House,
15–17 Mount Ephraim Road, Tunbridge Wells, TN1 1EN. Founded by David J McKibbin and Simon Hudson.

## Where the authority sits

Site copy is governed by the Arkaya Brand Voice and the Arkaya Term Register; neither lives in this
repository, and neither is restated here. Where this file or CLAUDE.md differs from them, they
govern.
