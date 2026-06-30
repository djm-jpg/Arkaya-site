# Arkaya site — v3 build (Doctrine + MTP refresh)

v3 site build, 30 June 2026. Authored in the live design system (Fraunces / IBM Plex). Upload-ready to replace the matching files in `djm-jpg/Arkaya-site`. Supersedes the v2 build (20 June 2026).

## What changed (vs Site-Build v2)

- **Homepage hero, MTP-led.** A new hero band at the very top carries the Massive Transformative Purpose as the single H1: **"Make the autonomous economy governable, and therefore priceable."** above the strapline *Governability infrastructure for the autonomous economy* and a governability/priceability lede. The previous "Third Domain of Risk" headline is retained immediately beneath it, demoted from H1 to H2 so there is exactly one H1 per page.
- **Proposition line sharpened** to read "underwritten continuously against governability, the live evidence that control holds."
- **Pillar pages refreshed.** Governability, priceability and the autonomous-frontier framing woven into the opening copy of `schema`, `solutions`, `evidence` and `ecosystem`.
- **Footer legal (all 7 pages)** updated to the ratified line: *Arkaya Risk is currently being formed in the UK and is presently a trading style of Centinel 10 Ltd, a company registered in England and Wales (no. 11906608).* Status verified at Companies House (11906608, active, England and Wales).
- **Contact (all 7 pages)**: founder name corrected to **David J McKibbin**; phone normalised to **+44 (0)7972 178759**.
- **Language aligned to Brand Voice v17 to v19 increments**: the Governability Doctrine, governability state / governability index (lower case, non-score), and the priceability MTP. Insurability is retained as the first and sharpest instance of priceability; the doctrine wedge ("governability is the precondition of insurability") is unchanged.

## Upload set (8 files, replace on a branch)

`index.html` · `schema.html` · `solutions.html` · `evidence.html` · `ecosystem.html` · `standard.html` · `founder.html` · `_redirects`

`_redirects` is unchanged (no new routes — the full-refresh scope did not add a Doctrine page). `standard.html` and `founder.html` change only in the footer/contact globals. Both are included so the upload set is complete.

## QA done before handover

All seven HTML files parse with balanced section tags and exactly one H1 each. MTP hero present on the homepage; ratified legal line and corrected contact verified on every page; no new routes. The Netlify deploy-preview click-through is the final visual check before merge (this environment has no headless browser, matching the v2 handover discipline).

## Deploy (branch + PR), per the v2 process

1. New branch, e.g. `v19-doctrine-mtp`.
2. Add file, Upload files, drag the changed files from this folder (they replace the existing files of the same name).
3. Commit to the branch, open the PR.
4. On the PR, open the Netlify Deploy Preview and click through every page: confirm the MTP hero on the homepage, the governability/priceability copy on the pillar pages, and the updated footer (legal line, David J McKibbin, phone) on all pages.
5. Merge (confirm it goes purple "Merged"). Netlify auto-publishes.
