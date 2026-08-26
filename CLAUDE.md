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

`ecosystem.html` and `infinity.html` are live routes with no navigation entry — deliberate.

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

Carried verbatim wherever the chain is stated — llms.txt, the discovery document, the /get page:

> Source systems emit signals; an engine produces a record against the schema; a counterparty reads
> that record as evidence; Arkaya produces neither the record nor the price.

If you edit any statement of who produces what, it must match this form exactly.

## Language constraints

Site copy is governed by the Arkaya Term Register (v8 at time of writing) and the Brand Voice
document; neither lives here, and where they differ from anything in this repository, they govern.
The three rules most often broken: no reserved word in two senses across the site ("canonical" is
RFC 8785 only, glossed at first use); no status word claiming outside recognition (everything in
`get/v1/` is **registered, not recognised** until a party Arkaya does not pay has reproduced the
outputs); and a passing signature establishes **what was sealed, not by whom**.

## Changing anything in get/v1/

`get/v1/` is the Layer 1 implementer pack, published from a hash-pinned zip whose digests are listed
in both `get/v1/MANIFEST.json` and `/.well-known/governance-evidence.json`. **Never edit a pack file
in place** — an edit silently breaks the one thing an agent can check. To change the pack: change
the pack zip, republish it whole, and update the discovery document's digests in the same commit.
`get/v1/specimen/` is site-authored, not pack material.

## Deploy

Branch, upload, PR, check the preview, merge. Quick preview checks: every page returns 200 at its
pretty URL; `/llms.txt`, `/robots.txt`, `/sitemap.xml`, `/.well-known/governance-evidence.json` and
`/get/v1/MANIFEST.json` all return 200; a PDF still serves. Confirm the production deploy log
reports header rules processed (the `_headers` file taking effect).
