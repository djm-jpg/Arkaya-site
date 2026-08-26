# Conformance corpus, Interface and Conformance Specification v4

**Candidate.** The corpus becomes normative on adoption, on the same rule the Profile
applies to its test vectors: a corpus is authoritative because a specification adopts it,
not because a tool produced it. Until adoption the test statuses in the specification
stand unchanged, and no version of the specification is bumped for an unadopted artefact.

## What is here

`reference_reader.py` — a minimal reference reading implementation. It exists so the
corpus has something to run against and so each fixture can be shown to discriminate.
Every deviation is a named mutation or a generated perturbation on the same class rather
than a forked copy, so the reference and its broken variants cannot drift apart.

`run_fixtures.py` — the corpus and the runner, in three passes.

1. **Conformance.** Every fixture runs against the reference, which passes all of them.
2. **Named mutations.** For each requirement, a hand-written breach of that requirement
   runs against its own fixtures and must fail them. Identifiers are `M-<requirement>-NN`,
   so a mutation is traceable in the same way a requirement is.
3. **Generated mutations.** Systematic perturbations produced without reference to any
   requirement: substitute each outcome of the coverage fold with each other state, drop
   each member of each closed enumeration. This family exists because a curated mutation
   set measures the author's imagination rather than the corpus.

Identity substitutions, replacing a branch with its own outcome, are excluded from the
generated set. They change no behaviour, so surviving proves nothing.

## Result at 10 August 2026

21 requirements, 34 fixtures. All pass against the reference. 21 named mutations, all
killed. 35 generated mutations, all killed.

## What the three passes found, in the order they found it

**Three fixtures did not discriminate,** and one exposed a defect in the reference rather
than in the corpus: inadmissible records were still contributing their digests to
`inputDigests`, so R-18 was unenforced and untestable at the same time. The other two,
R-12 and R-35, had no mutation defined, which is a quieter version of the same silence.

**The first generated run reported 100 per cent discrimination and the figure was false.**
Fixtures shared one reader, and F-36-01 counts appended determinations, so it failed under
every perturbation including identity substitutions that change nothing. One badly scoped
fixture was manufacturing the score. Running each fixture against a fresh reader dropped
the honest figure to 72 per cent.

**Those eleven escapes then produced the real finding.** Eight of them said that no fixture
ever constructed `NO_CONTROL` or `EFFICACY_FAIL`. Two of the four coverage states, the two
that carry an adverse determination, were never exercised. Four fixtures were added and the
generated set now clears.

The sequence is the point. A curated mutation set said the corpus was complete. A generated
set said it was not, and then a scoping defect in the corpus briefly hid that too.

## Standing principle

Passing is not evidence unless failing was possible.

## Determinism

Nothing reads a clock. Every timestamp is fixture data and the evaluation date is an input,
per R-33. Each fixture runs against a fresh reader, so no fixture depends on the order of
those before it.
