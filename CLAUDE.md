# CLAUDE.md — djm-jpg/Arkaya-site

Operating instructions for anyone, human or agent, working in this repository. Read before editing.

## What this is

The source of arkayarisk.com. Netlify project `arkaya-risk`, site id
`58f0ac17-e986-4892-8cde-796b6e994ed8`, production branch `main`. Merging to `main` publishes to the
live domain. There is no staging environment; the branch deploy preview on the PR is the only place
to look before the site is live.

## The layout — flat, static, no build step. Keep it that way.

Every page sits at the repository root; `.well-known/` and `get/` are the only content
subdirectories. There is **no build command and no publish-directory setting**: Netlify serves the
repository root as-is, and the deploy takes seconds and cannot fail. `_redirects` carries the pretty
URLs and `_headers` carries the content-type and CORS rules; both are plain files Netlify reads
without any tooling.

Do not introduce a build pipeline, a `public/` or `dist/` directory, npm dependencies, or an edge
function without a decision recorded for it. An August 2026 build proposing exactly that was
red-teamed and deliberately shelved: the benefit was unevidenced and the publishing path's inability
to fail is worth more. The decision record is with the Tranche A notes; the shelved machinery is in
the v5 bundle and can be revived if measurement ever justifies it.

Pages, and whether they are in the navigation:

| In the navigation | Live, not in the navigation |
|---|---|
| `index.html` (home) | `architecture.html` — reachable only from body copy and `llms.txt`. **Open decision.** |
| `solutions.html`, `evidence.html` | `get/index.html` — same. **Open decision.** |
| `schema.html`, `doctrine.html`, `founder.html` | `ecosystem.html`, `infinity.html` — deliberate, no agent surface |
| `library.html`, `standard.html` | |

The navigation carries seven items in three groups and has not grown since the page count did. That
is a decision waiting to be taken, not an oversight: `/architecture` and `/get` are the two newest
and densest pages and a human cannot currently reach either from the header.

### Adding or retiring a page

Two files must change in step, or the page is invisible to agents and to search:

1. `sitemap.xml`
2. `llms.txt` — and the entry is locked copy, not metadata; see below

Then decide, explicitly, whether it enters the navigation. A page that enters neither the navigation
nor `llms.txt` is unreachable and should not have been built.

## The agent surface

Three files, all static, all authored:

- `/llms.txt` — the site index for agents, in the llms.txt convention. Its purpose here is **control
  of the paraphrase**: where a model reads it, Arkaya wrote the sentence the model repeats. Treat
  every line as locked copy, not as metadata. It carries the definitional invariant verbatim.
- `/robots.txt` — allows everything, carries the sitemap. Deliberately carries **no Content-Signal
  line**: as of August 2026 no crawler operator has confirmed reading one, and the file states only
  what is enforced. Do not add one without a new decision.
- `/.well-known/governance-evidence.json` — machine-readable index of the open Layer 1 material,
  with digests. It is currently an unsigned assertion, and signing it with the pack's own profile is
  queued behind the production-key decision on the trust-path track.

## The definitional invariant

Carried verbatim wherever the chain is stated — llms.txt, the discovery document, `/architecture`:

> Source systems emit signals; an engine produces a record against the schema; a counterparty reads
> that record as evidence; Arkaya produces neither the record nor the price.

If you edit any statement of who produces what, it must match this form exactly.

## Language constraints

Site copy is governed by the Arkaya Term Register (v8 at time of writing) and the Brand Voice
document; neither lives here, and where they differ from anything in this repository, they govern.

Four rules, each of which this site has broken at least once and been corrected for:

- **Custody is never unqualified.** Split it: private key control, public key publication, or record
  retention. The claim this site makes is record retention — "each hop retained in the record".
  "Chain of custody" was removed from eight places on 26 August and must not return.
- **Independence means no reliance on Arkaya, and the sentence says which reliance.** It does not
  mean insulation from commercial pressure; that sense was removed from `/schema` on 26 August.
  Note the *Schema Independence Charter* keeps its name — renaming a titled instrument is a schema-
  track act, not a website edit.
- **Verify is reserved to the allocator's third step** (observe, verify, price, allocate), glossed
  once at first use as the proof check that party runs for itself. It is never a verb for anything
  Arkaya, the schema or the software does. `/standard` said "assertions verified" until 26 August;
  it now says "checked".
- **No status word claiming outside recognition.** Nothing on this site is certified, established,
  recognised, adopted, proven, validated or trusted. Everything in `get/v1/` is **registered, not
  recognised** until a party Arkaya does not pay has reproduced the outputs.

### Specification first, site second

Where the governing specification owns a word, the site does not correct it alone. Changing the site
while the specification keeps the word manufactures the same-word-two-senses defect the register's
fifth check exists to catch. The specification moves first.

**Establish ownership by grep, not by memory.** An earlier version of this file listed three uses as
spec-owned. One was not, and the error survived because nobody checked:

- **"cryptographically verifiable" (the SVG sub-label on `/evidence`) is NOT spec-owned.** Searched
  27 August across all 85KB of `get/v1/specifications/` — the Cryptographic Profile v5 and the
  Interface and Conformance Specification v4. The phrase appears in neither. It was a lowercase
  descriptive phrase under a diagram box, not a name, and it was corrected on 27 August to "a
  stranger can check it". **This file previously forbade that correction. This file was wrong.**
- **The ladder grades `Asserted` / `Attested` / `Evidenced` / `Verifiable`, and Field 07
  `Verification mode`, do not appear in those two specifications either.** They are presumed owned by
  the Taxonomy, which is not in the open pack and has not been checked. Treat them as spec-owned —
  but the claim is **unverified**, and it should be settled against the Taxonomy before anyone relies
  on it in either direction.

What the specifications *do* use, three times, is **"independently verifiable"** — and each instance
names the reliance that is absent: "with off-the-shelf tooling", "with standard libraries and no
Arkaya component", "holder-independent". That is the register-compliant form. `/doctrine` uses the
same phrase without naming any absent reliance, inside Principle Zero, which `/library` records as
stated and defended in Paper 1. **That one is a real breach and is Paper 1's to fix first.**

### Sweeps read the whole page, not the prose

A register sweep reads the rendered text of **every page in `sitemap.xml`** — navigation, group
labels, footers, SVG and diagram labels, `alt` text, and `<meta>` descriptions included. Body prose
is a subset of the object, not the object.

Three defects survived three sweeps in two days because the sweeps read body text and treated
everything else as chrome:

- the SVG sub-label on `/evidence`, the fifth instance of a phrase removed four times from `/schema`;
- the conformance-status claim on `/evidence`, because `/schema` had been swept for it and
  `/evidence` had not;
- the navigation group label **`Verify`**, on all ten pages, which classified the Library and the
  Production Standard *as* verification in the most-repeated text position on the site. Corrected to
  `Examine` on 27 August. Not `Check`: that word now carries a precise meaning on `/schema` and
  `/evidence` — what a counterparty does to a sealed record — and reusing it as a nav label would
  blur a word this estate spent two days making exact.

Sweep the sitemap. Sweep whole pages. A page swept for one breach is not swept.

## Changing anything in get/v1/

`get/v1/` is the Layer 1 implementer pack, published from a hash-pinned zip whose digests are listed
in both `get/v1/MANIFEST.json` and `/.well-known/governance-evidence.json`. **Never edit a pack file
in place** — an edit silently breaks the one thing an agent can check. To change the pack: change
the pack zip, republish it whole, and update the discovery document's digests in the same commit.
`get/v1/specimen/` is site-authored, not pack material.

Two pack files — `MANIFEST.json` and `vectors/vectors_v5_candidate.json` — have **no trailing
newline**, and their digests depend on it. GitHub's web *editor* appends one on every commit and
will break them; the drag-and-drop *uploader* commits raw bytes and does not. Use the uploader for
those two files.

## Deploy

**Structural change — a new page, a layout change, anything touching `_headers`, `_redirects` or
`get/v1/`:** branch, PR, check the deploy preview, merge. The preview is the only look you get.

**Small copy correction — a handful of lines, no new files, no structural change:** committing
straight to `main` is acceptable and was done for the eleven register corrections on 26 August. Know
that you are skipping the preview when you do it.

Preview checks, whichever route: every page 200 at its pretty URL; `/llms.txt`, `/robots.txt`,
`/sitemap.xml`, `/.well-known/governance-evidence.json` and `/get/v1/MANIFEST.json` all 200; a PDF
still serves. Confirm the production deploy log reports header rules processed.
