# Arkaya site — v3 build (Doctrine + MTP refresh)

v3 site build, 30 June 2026. Authored in the live design system (Fraunces / IBM Plex). Upload-ready to replace the matching files in `djm-jpg/Arkaya-site`. Supersedes the v2 build (20 June 2026).

## What changed (vs Site-Build v2)

- **New page: the Doctrine** (`doctrine.html`, route `/doctrine`). Presents the five principles, the priceability chain (evidence to governability to pricing confidence to capital allocation to applications to enterprise value), the two theorems, the insurance-first-instance nesting, and the "what this is not" boundaries. Built in the live design system, reusing the existing chrome and section classes.
- **Nav, every page:** `Doctrine` added as the first nav item, so it reads Doctrine · Schema · Solutions · Ecosystem · Evidence · Standard. The doctrine is the root the rest derives from.
- **Homepage hero, MTP-led.** New hero band carrying the MTP as the single H1: **"Make the autonomous economy governable, and therefore priceable."** above the strapline *Governability infrastructure for the autonomous economy*. The previous "Third Domain of Risk" headline is retained beneath it, demoted to H2 so there is exactly one H1 per page.
- **Proposition line sharpened** to "underwritten continuously against governability, the live evidence that control holds."
- **Pillar pages refreshed.** Governability, priceability and the autonomous-frontier framing woven into the opening copy of `schema`, `solutions`, `evidence` and `ecosystem`.
- **Footer legal (all pages)** updated to the ratified line: *Arkaya Risk is currently being formed in the UK and is presently a trading style of Centinel 10 Ltd, a company registered in England and Wales (no. 11906608).* Verified at Companies House.
- **Contact (all pages)**: founder name corrected to **David J McKibbin**; phone normalised to **+44 (0)7972 178759**.
- **Language aligned to Brand Voice v17 to v19 increments.** Insurability retained as the first and sharpest instance of priceability; the doctrine wedge ("governability is the precondition of insurability") unchanged.

## Upload set (9 files, replace/add on a branch)

`index.html` · `doctrine.html` (new) · `schema.html` · `solutions.html` · `evidence.html` · `ecosystem.html` · `standard.html` · `founder.html` · `_redirects`

`_redirects` now carries `/doctrine /doctrine.html 200`. `standard.html` and `founder.html` change only in the footer/contact globals and the added Doctrine nav item.

## QA done before handover

All eight HTML files parse with balanced `<section>` tags and exactly one `<h1>` each. MTP hero present on the homepage; the Doctrine nav item, the ratified legal line and the corrected contact verified on every page; the `/doctrine` route present in `_redirects`. The Netlify deploy-preview click-through is the final visual check before merge (this environment has no headless browser).

## Deploy (branch + PR), per the v2 process

1. New branch, e.g. `v19-doctrine-mtp`.
2. Add file → Upload files → drag the changed and new files from this folder (`doctrine.html` is an add; the rest replace).
3. Commit, open PR.
4. On the PR, open the Netlify Deploy Preview and click through every page: confirm the MTP hero on the homepage, the new `/doctrine` page and its nav link on every page, the governability/priceability copy on the pillar pages, and the updated footer on all pages.
5. Merge (confirm it goes purple "Merged"). Netlify auto-publishes.
