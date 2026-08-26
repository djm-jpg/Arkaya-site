# Arkaya Layer 1 — Interface and Conformance Specification

**Version:** 4
**Dated:** 2026-08-10
**Owner:** David McKibbin
**Repository:** working copy at `20-Layer2-Commercial/14-MVP-Build-Scripts/Interface and Conformance suite/`; proposed ratified home `10-Layer1-Custodian/Specifications/Conformance Suite/`
**Status:** Pre-ratification. Content hashes pending population.
**Class:** A (institutional, normative). RFC 2119 register.
**Supersedes:** v3, 10 August 2026 (same date). See Document revisions at Section 9.

---

## 1. Purpose and positioning

This specification states what a conformant emitter emits and what a conformant reading implementation consumes, and how either party establishes that it has conformed. It is written so that an implementer who has never met the custodian can build to it from this text and the referenced test vectors alone.

The reason for a single document covering both sides is the map-once property. Where each producer publishes its own form, a party wishing to rely on the evidence must learn that form first and take the producer's word for the rest, and it pays that cost again for every further producer. A shared form removes the cost. The property holds only if the two sides of the interface are fixed together, because a record form with no stated read is a file nobody can act on, and a read with no stated record form is a private integration wearing a standard's clothes.

What passes between the parties is a directory of files. No service call to the custodian is required at any point in production, verification or reading, and no implementation of the custodian's is deployed into any other party's environment.

**What this specification homes into the suite.** The emitter-side obligations that were previously scattered across the record specification, the cryptographic profile and the build addenda: the run-level scope declaration, the by-value verification method, the anchored-time obligation and their failure states. The read-side contract: the admissibility gate, the coverage-state set, the refusal path and the reading-surface conventions. The registered acceptance tests with their thresholds.

**What it leaves to others.** Record structure, chains and genesis are the Evidence Record Specification's [1]. Canonicalisation, digest, signing and the proof are the Cryptographic Profile's [2]. Retention and entitled read are the Retention and Entitled-Read Companion's [3]. Conformance classes, criteria and assessment procedure are the Conformance Methodology's [4]. The legal-mechanical meaning of hold, privilege, insolvency and cross-border access is the Legal Access Model's. This specification references each and restates none.

Sections 3 and 4 are normative. Sections 1, 2, 5, 6, 7, 8, 9, 10 and 11 are informative except where they carry a numbered requirement. The keywords MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, MAY, REQUIRED and OPTIONAL are interpreted per RFC 2119 and RFC 8174, and only when capitalised [17].

---

## 2. Cross-cutting conventions

Inherited and referenced, not restated here.

**Serialisation.** JSON Schema Draft 2020-12; I-JSON baseline; canonical form RFC 8785 JCS, with property ordering lexicographic on names as arrays of UTF-16 code units, applied recursively, array order preserved, no whitespace between tokens, UTF-8 output, duplicate member names prohibited and no Unicode normalisation [2][6].

**Signature.** W3C Data Integrity, cryptosuite `eddsa-jcs-2022`, Ed25519 PureEdDSA per RFC 8032, proof value base58-btc multibase, exactly one `DataIntegrityProof` per record [2][7]. The house identifier previously used beside the cryptosuite is retired; see the reconciliation at 6.1.

**Digest.** SHA-256 of the canonical record content with the proof removed; chains link by `previousDigest` [1][2].

**Timestamps.** RFC 3339 UTC strings with the `Z` suffix; the RFC 9557 bracketed-suffix extension is excluded [2].

**Numbers.** Safe-range integers only; every other numeric value is a string [2].

**Identifiers.** Opaque strings at this layer. Their meaning belongs to the Data Model, not to this specification [1].

---

## 3. Normative body

### 3.0 Requirement classes

Requirements in this document bind two different objects and carry two identifier series. The distinction answers the question an external implementer asks first, which is which requirements are properties of the interchange and which are conditions on a claim.

**R-series, conformance requirements.** Binding on any implementation claiming conformance as an emitter or as a reading implementation. These are properties of the file and of the evaluation that produces a determination from it. An implementation that does not meet them does not interoperate.

**P-series, presentation requirements.** Binding only on an implementation that claims to present conformant determinations. They are conditions on that claim, not properties of the interchange. An implementation that presents nothing, or that presents without making the claim, is unaffected by them and may still be fully conformant under the R-series.

Neither series constrains what a party does with a determination once it holds one. A reader may compute, aggregate, rank or price on the facts a conformant record carries; what the P-series governs is whether the result may be presented as a conformant determination. See P-2.

### 3.1 Conformance classes and the expression of a claim

Conformance classes are GET-PRODUCER, GET-VERIFIER, GET-NODE, GET-ATTESTATION and GET-AUDITOR, defined in the Conformance Methodology [4]. Capability terms are Core and Extended, ungraded, per the Core/Extended Crosswalk [5].

**R-1.** A conformance target under this specification SHALL be expressed as the class plus the capability term, with an Extended claim naming its requirement groups, for example "GET-PRODUCER, Core" or "GET-VERIFIER, Extended (AR and AS groups)". *Maps to Crosswalk section 3.3 [5]; testable by inspection of any claim, certificate or specification citing this document.*

Three further rules govern a claim and are owned elsewhere: a target is never expressed as a level number, an Extended claim includes Core, and the capability terms, the conformance classes and the verifier implementation levels are never presented as one taxonomy. All three are the Crosswalk's, at its R-2, R-3 and R-4 respectively, and this specification cites them rather than restating them [5]. Identifiers R-2 and R-3 were vacated at v3 for that reason, and the level-number sentence came out of R-1 at v4 for the same one: a restatement of a requirement another artefact owns is a second copy that can drift from the first, which is the defect the boundary rule exists to prevent.

An emitter builds to GET-PRODUCER, Core. A reading implementation builds to GET-VERIFIER, Core, and adds Extended (AR and AS groups) where it consumes an assurance read or relies on a counter-seal. The register entries that constitute each claim are the testable substrate: twelve Core entries, seven Extended, two methodology meta-requirements outside the ladder [8].

### 3.2 What a conformant emitter emits

#### 3.2.1 The record

**R-4.** Every emitted record SHALL carry the mandatory envelope members with the stated types, chained and signed per the Evidence Record Specification and the Cryptographic Profile. *Maps to register entries ER-3.1, ER-5.1, ER-6.1, CP-3.1, CP-3.2, CP-3.3, CP-4.1, CP-5.1, CP-7.1 [1][2][8].*

**R-5.** The record body SHALL contain no scalar score, grade, band, rating or premium, and no member outside the reserved extension container SHALL be used for vendor fields. *Maps to ER-8.1 and ER-9.1 [8]. This is the no-score discipline applied at the record layer; a reading implementation computes whatever scalars it computes outside the record and owns them.*

#### 3.2.2 The verification method by value

Rationale at 10.1 [12].

**R-6.** A record SHALL embed its verification method by value, so that the public key travels with the record. *Testable by test K-1.*

**R-7.** A verifier SHALL complete signature verification from the embedded verification method without network access. *Testable by tests K-1 and V-3.*

**R-8.** A verifier SHOULD additionally resolve the controller document at check time, and SHALL report a failed or changed resolution as a status lookup that is unavailable rather than as a verification failure. *Testable by test K-2. Rationale at 10.1.*

#### 3.2.3 Anchored time

**R-9.** A record SHALL carry a time-stamp token from a time-stamping authority outside the emitting platform, per RFC 3161 or an equivalent whose token is checkable with ordinary tooling [11]. *Test status: fixture-ready.*

**R-10.** Where no external authority is wired, the record SHALL carry the platform timestamp explicitly flagged as unanchored, and no document, screen or determination SHALL attach dispute-grade language to an unanchored time. *A clock belonging to the emitting platform is not independent, and an independence claim that silently rests on it is an assertion. The flag is what keeps the two cases distinguishable to a reader who was not present.* *Test status: fixture-ready.*

#### 3.2.4 The scope declaration

Absence of evidence is only interpretable if the reader knows what was looked at. Where connectors are licensed to third parties, those parties decide what is emitted, which makes a missing record ambiguous, and the whole coverage-state grammar depends on absence being interpretable.

**R-11.** Every emitting run SHALL carry a scope declaration stating the systems covered, the control identifiers in scope, the interval covered, and what the run did not look at. *Test status: fixture-ready.*

**R-12.** A record set presented without a scope declaration SHALL return REVIEW naming the omission, and SHALL NOT return a determination. *Testable by test S-1.*

**R-13.** The conformance check on a scope declaration SHALL be on its presence and shape only. *Truthfulness of a scope declaration is not testable by any party and this specification does not pretend otherwise.* *Test status: inspection.*

**R-14.** A reading implementation SHALL distinguish "no evidence, in scope" from "no evidence, out of scope", and SHALL NOT represent the second as a control gap. *Testable by test S-1.*

**R-15.** Where a record set makes a coverage claim, the claim SHALL be stated as a lower bound with completeness not claimed. A statement that a holder returned the whole of a scope overstates what the form can prove: per-record integrity is holder-independent and verifiable from the digest reference, while set completeness is bounded by the scope commitment and is not eliminated by it. *Maps to register entry AR-7.1 [8].*

#### 3.2.5 The join contract

**R-16.** The unit of exchange SHALL be a directory of sealed record files. A reading implementation SHALL require no change to its own code to accept a further emitter's directory. *No interface beyond the file set is defined by this specification, and none may be required by a conformant implementation of either side.* *Test status: fixture-ready.*

#### 3.2.6 Canonicalisation

**R-41.** An implementation SHOULD obtain canonical form from a verified RFC 8785 library rather than from authored canonicalisation, and SHALL establish agreement with another implementation by differential test rather than by inspection. *A serialiser producing sorted, whitespace-free output is not a canonicaliser, and agreement on the values two implementations happen to have tried is not conformance. See 6.3.* *Test status: fixture-blocked.*

### 3.3 What a conformant reading implementation consumes

#### 3.3.1 The admissibility gate

Admissibility asks whether the thing in hand is a record. Coverage asks what the record shows. The two questions are separate and are answered in that order.

**R-17.** A reading implementation SHALL evaluate every record against the admissibility gate before any coverage evaluation, and SHALL return exactly one of four outcomes: `admissible`, `unattributed`, `unverifiable`, `out-of-scope`. *Test status: fixture-ready.*

**R-18.** An inadmissible record SHALL NOT contribute to a determination. *Test status: fixture-ready.*

**R-19.** `unattributed` SHALL be a statement about the key and SHALL NOT be represented as a statement about the control. *A record whose signature verifies while no party can vouch for the key is neither evidenced nor not evidenced, and collapsing that into either reading is the error this outcome exists to prevent.* *Test status: fixture-ready.*

#### 3.3.2 The coverage-state set

**R-20.** Coverage SHALL be expressed per obligation as exactly one of four states, under these names: `NO_CONTROL`, `OPERATION_GAP`, `EFFICACY_FAIL`, `COVERED`. The set is closed and no fifth state is representable in the schema. *Test status: fixture-ready.*

The fold is keyed on the mode of the observable and requires no aggregation:

| State | Condition |
|---|---|
| `NO_CONTROL` | The configuration source is absent, or present and showing the control unconfigured |
| `OPERATION_GAP` | Configuration present; the event source shows no exercise inside the freshness window and no probe was run |
| `EFFICACY_FAIL` | The event source shows the control was reached and did not hold |
| `COVERED` | Configuration present, exercised inside the freshness window, no efficacy failure on the join |

**R-21.** A configuration-only obligation SHALL NOT reach `COVERED` on its own evidence. *This is the correct result and it is why the mode of each observable is carried in the record rather than in a comment.* *Test status: fixture-ready.*

**R-22.** The position of the emitting source, whether it sits outside or inside the execution path of the agent whose behaviour it evidences, SHALL be recorded beside the state and SHALL NOT enter the fold. *Folding position into the state would convert a recorded fact into a judgement and place a weighting inside the engine.* *Test status: fixture-ready.*

#### 3.3.3 The fifth result, in the checker only

**R-23.** A reference checker SHALL return "signature valid, signer unattributed" as a distinguishable result with its own exit code and its own line in its report, and SHALL NOT return it as either PASS or FAIL. *Testable by test C-1. This result corresponds to the `unattributed` outcome of the admissibility gate and is its checker-side expression.*

**R-24.** The unattributed result SHALL NOT be added to the coverage-state set. *The set is normative and a fifth state requires a ratified schema candidate carrying its own falsification condition. The checker demonstrates the need; the schema follows or does not.* *Test status: fixture-ready.*

#### 3.3.4 Refusal, and the treatment of a failed read

Rationale at 10.2 [14].

**R-25.** A reading implementation SHALL carry nine read statuses upstream of the fold: available, not connected, unauthorised, unavailable, stale, incomplete history, schema error, integrity error, unjoinable. *Test status: fixture-ready.*

**R-26.** Only evidence at status `available` SHALL enter the fold. Everything else SHALL route to a first-class refusal path carrying itemised reasons. *Test status: fixture-ready.*

**R-27.** Refused records SHALL be reported alongside the determinations they were excluded from. *Test status: fixture-ready.*

**R-28.** A read status SHALL NOT become a fourth triage outcome. The triage enumeration is closed at three values: `EVIDENCED`, `ATTESTED`, `BELOW_BENCHMARK` [16]. *Test status: fixture-ready.*

Whether a failure of a component the reading party selected may be recorded as an adverse finding against the party being evidenced is an attribution question, not a property of the interface. It turns on who selected the component, which no record carries and no determination can establish, so it is not testable at this layer and is not a requirement here. Identifier R-29 is vacated at v3 and the rule is left where it operates, in the attribution mechanics of the applicable schedule [14]. The interface obligation that survives is R-26: evidence that is not available does not enter the fold.

#### 3.3.5 Trajectory and presentation (P-series)

Requirements P-1 to P-3 are presentation requirements per 3.0. Identifiers R-30, R-31 and R-32 are vacated at this version and are not reused; the requirements formerly carried under them are restated here, P-2 with a correction.

**P-1.** Where an implementation presents trajectory, it SHALL present the component measurements under their own names, computed from recorded timestamps: loop latency, escalation responsiveness, exception resolution duration, protocol adherence variance, evidence completeness, signal decay. *Vacates R-30.* *Test status: inspection.*

**P-2.** An aggregate, weighted, normalised or ranked expression composed from the emitted facts SHALL NOT be presented as a conformant determination, SHALL NOT be required by any instrument citing this specification, and SHALL NOT be used as a condition. Such an expression is the composing party's own analysis, lies outside this specification, and SHALL be labelled as external analysis where it is presented alongside conformant determinations. *Vacates R-31 and corrects it. The v1 text opened by prohibiting a conformant implementation from producing an aggregate and closed by permitting a reader to compose one, which was a contradiction inside a single requirement. The prohibition attaches to the label, not to the arithmetic: a party may compose whatever it wishes from the facts and owns the result. Maps to the no-score discipline carried pervasively through the conformance criteria [4]. Interval values, including any time to effect, are the reader's computation from the recorded timestamps and are never emitted as composed values.* *Test status: inspection.*

**P-3.** A surface presenting conformant determinations SHALL observe six conventions: *Test status: inspection.*

1. No aggregate state across obligations.
2. The four coverage states shown under their own names.
3. Refused records shown alongside the determinations they were excluded from.
4. Provenance class and effective-time basis shown wherever a state appears.
5. Nothing shown that cannot be recomputed from the record set.
6. The whole obligation set shown by default, exceptions prominent, denominator preserved.

*Vacates R-32. A labelling rule binding any implementation claiming to present conformant determinations. It is not a control over a party's own internal screens.*

#### 3.3.7 Determination and replay

**R-33.** A determination SHALL be a pure function of its declared inputs: the sealed record set, the benchmark version, the schema version, the evaluation date supplied as an input, the emitter manifest and the applicable schedule. No wall-clock read SHALL occur in the read path. *Test status: fixture-ready.*

**R-34.** A determination SHALL carry the input digests, the benchmark digest, the engine and schema versions, the per-observable results, the per-obligation coverage states, the reasons, the unresolved evidence and a signature. *Test status: fixture-ready.*

**R-35.** Given a historic sealed record set and the benchmark version effective at the time, a conformant implementation SHALL reproduce the identical determination digest on every build. *This is a release-blocking regression test rather than a one-off acceptance exercise. The claim that the control state at the moment of loss is a fact rather than a reconstruction is implemented by this test or it is not implemented at all.* *Test status: fixture-blocked.*

**R-36.** A determination SHALL NOT be overwritten by later data or by a later rule change. Determinations are append-only. *Test status: fixture-ready.*

### 3.4 The fact and opinion boundary

**R-37.** A conformant record SHALL state a fact: an event with a time, an actor recorded by role, and a subject. Analysis, including any delta, ranking or recommendation, SHALL NOT be emitted as a record and SHALL NOT carry a coverage state. *Test status: inspection.*

**R-38.** Where a conclusion must travel tamper-evident, it SHALL be committed by digest, and the schema SHALL NOT represent, endorse or take a view on it. *No signature converts an opinion into an observation. The construction is the same as the tombstone payload commitment, which commits external content by digest so that no signed record is mutated [3].* *Test status: fixture-blocked.*

**R-39.** Terms the counterparties agree at the point of binding, including targets, deadlines and declared scope, SHALL be recorded in the binding and SHALL NOT be emitted as records. *Emitting agreed terms as records is a category error rather than a grading problem.* *Test status: inspection.*

### 3.5 Signer identity

**R-40.** Signers SHALL be recorded by role and SHALL NOT be recorded by natural-person name. *Enforced by schema validation at emission.* *Test status: fixture-ready.*

---

## 4. Registered acceptance tests

Eight tests, with thresholds fixed before any test was designed [13]. None had run at the date of this version. A test is conformant only where its fixture, procedure and threshold are reproduced as stated. Agreement between two implementations on the values they happen to have tried is not conformance; where two implementations must agree, conformance between them is established by differential test rather than by inspection.

### L-1 · Library validator

**Purpose.** The mapping library is a versioned dataset carrying provenance from first commit, not a folder of documents.
**Fixture.** The mapping-set schema; the full set of mapping files; one deliberately malformed file with its change record removed.
**Procedure.** Run the validator across every file, then across the malformed fixture.
**Threshold.** Every well-formed file passes. The malformed fixture fails, naming the missing provenance field.
**Failure meaning.** Provenance discipline is not enforced, so the record of investment on which the database right depends is not evidenced.

### V-1 · Cryptographic correctness

**Purpose.** A party checks a record with the record, the published schema at the pinned version and the signer's public key.
**Fixture.** One sealed record; the published schema at the pinned version; the signer's public key.
**Procedure.** An independent checker, using stock open-source tooling and no package published by the custodian, completes the proof check.
**Threshold.** 100 per cent.
**Failure meaning.** A single failure is a defect, not a statistic.

### V-2 · Retrievability

**Purpose.** The key and the schema can be obtained without help from the emitter or the custodian.
**Fixture.** At least 30 seeded records.
**Procedure.** A checker obtains the verification key and the schema for each record unassisted.
**Threshold.** 90 per cent.
**Failure meaning.** Statistical by design, because retrievability depends on domains and documents no party to this specification controls.

### V-3 · No call to the custodian

**Purpose.** The offline claim is tested rather than asserted.
**Fixture.** The V-1 fixture, inside a container with every custodian-operated domain blocked at DNS.
**Procedure.** Run V-1 unchanged.
**Threshold.** The check passes.
**Failure meaning.** The claim that verification does not route through the custodian comes off the exhibit. This is the cheapest honest proof of that claim available, and it either passes or the claim is withdrawn.

### S-1 · Scope declaration

**Purpose.** Absence is interpretable.
**Fixture.** Two record sets: one with no scope declaration; one declaring a narrow scope with named controls outside it.
**Procedure.** Submit each to the conformance check.
**Threshold.** The first returns REVIEW naming the omission. The second returns PASS, with the out-of-scope controls reported separately rather than as gaps.
**Failure meaning.** No evidence in scope and no evidence out of scope read the same, and every coverage state resting on absence becomes unreliable.

### K-1 · Offline verification on the embedded key

**Purpose.** The record survives ordinary key rotation.
**Fixture.** One sealed record carrying its verification method by value.
**Procedure.** Verify with the network disabled entirely.
**Threshold.** Verification succeeds using only the embedded key.
**Failure meaning.** A record checked years after sealing depends on a key state nobody undertook to preserve.

### K-2 · Changed controller document

**Purpose.** A rotation is not a tamper.
**Fixture.** One sealed record whose controller document has been changed since sealing.
**Procedure.** Verify with the network enabled.
**Threshold.** Verification succeeds and the status lookup is reported as unavailable rather than as a failure.
**Failure meaning.** Ordinary key hygiene retrospectively invalidates sound records, which is the defect R-6 to R-8 exist to remove.

### C-1 · The unattributed result

**Purpose.** The fifth result is distinguishable in the checker without entering the schema.
**Fixture.** One record signed with a key that cannot be resolved.
**Procedure.** Run the reference checker.
**Threshold.** The checker returns the unattributed result with its own exit code and its own report line, and returns neither PASS nor FAIL.
**Failure meaning.** An unresolvable key is silently read as either evidence or absence of evidence, and the reader cannot tell which.

---

## 5. What this is not

- Not a regulatory replacement, and not an audit opinion.
- Not a continuous-compliance certification.
- Not a governance score, band or maturity assignment. The capability terms name what an implementation conforms to, never how well any party governs itself.
- Not an adjudication of law. Hold validity, privilege, insolvency, corporate transition and cross-border access are the Legal Access Model's.
- Not a restatement of cryptography. Canonicalisation, digest, signing, the proof and the tombstone mechanics are the Cryptographic Profile's.
- Not the Data Model. What a Protocol requires, what a Signal observes and how the core vocabulary relates are the Data Model's; this specification treats them as opaque typed structure.
- Not a pricing method. The interface makes a determination legible; whether a party accepts a risk, and on what terms, is that party's decision.
- Not a software delivery. No implementation of the custodian's is deployed into any other party's environment under this specification.
- Not applicable to verifier implementation levels, which belong to the Verifier Specification's separate taxonomy.

---

## 6. Open items and reconciliations

**6.1 Reconciliation, the profile identifier.** The suite envelope carries a mandatory `profileIdentifier` member whose illustrative value in the Evidence Record Specification is the retired house identifier, and whose text requires consistency with the proof's cryptosuite member [1]. The adopted position is the cryptosuite `eddsa-jcs-2022`, on the ground that the Data Integrity EdDSA Cryptosuites specification defines exactly two suites and a third identifier beside them is an alternative to alignment rather than an instance of it [6][7]. Live artefacts carrying the house identifier take the correction at their next whole-integer version; frozen artefacts are not edited. Carriers were counted rather than recalled at v4. A mechanical scan of the current Layer 1 estate on 10 August 2026 found the retired identifier in twenty artefacts, among them the Cryptographic Profile that owns it, the suite envelope, the parent Evidence Record Specification, the Conformance Methodology at v3 and v4, the Assurance Read Schema, the Attestation Substrate Specification, the Versioning Policy, the Document Map, the Spec Build Map and the reference implementation. Two had been recalled by hand before the scan ran, which is the argument for scanning. The Cryptographic Profile takes the correction first, because a dependant corrected against a parent that still says otherwise is pinned to a contradiction; the remaining artefacts reconcile at their own next whole-integer versions. Resolves at the Cryptographic Profile's next version, which owns the identifier. The current version of every artefact named in this document was read from the Suite Version Register in the same turn as it was written [10].

**6.2 Open decisions, canonicalisation, D-8 to D-13.** Six decisions the cryptosuite does not reach gate conformant emission for every producer: the exclusion set per object type; the timestamp lexical form; the digest reference form used outside the proof; absent against null; decimal handling; and what the binding names [6]. They are the Cryptographic Profile owner's to resolve and this specification cites them as open. No requirement above fixes any of the six, and an implementer should read no example in this document as settling one. Until they are settled, two conformant-looking implementations can sign different bytes from the same record and neither is wrong.

**6.3 Note to implementers, canonicalisation is not serialisation.** A team holding a JSON serialiser that produces sorted, whitespace-free output will reasonably believe it has a canonicaliser and does not. A reference canonicaliser in this estate passed fifty-eight adversarial checks while non-conformant to the scheme on UTF-16 code-unit sorting. An implementation should use a verified RFC 8785 library, which exists for JavaScript, Java, Go, C# and Python, rather than authored canonicalisation [6].

**6.4 Open decision, Unicode form at the point of creation.** Two strings that appear identical and differ in composition canonicalise to different bytes, and therefore to different digests, because the scheme performs no normalisation [6]. The producer fixes the form when the record is created. Whether this specification should carry a normative form requirement, or leave it to the Profile, is open.

**6.5 Open item, skew tolerance.** Six joins in the current source map carry no stated tolerance between clocks in different systems [15]. An obligation resting on such a join cannot be falsified, and an obligation that cannot be falsified cannot be adjudicated. Setting the tolerance now costs a drafting decision; setting it after a disputed adjustment means setting it against a known fact pattern, with one party's loss already on the table.

**6.6 Open item, the evidence floor and its source footprint.** On the current source map, sixteen obligations carry forty-eight observables across sixteen source classes, of which a four-source instrumented set connects fifteen observables and a five-source set connects twenty; two of the five floor obligations are fully sourced on either set [15]. This specification does not resolve where the floor sits. It states the consequence, which is that a floor whose source footprint exceeds the connected set produces determinations through the remediation path as the normal case rather than as the exception.

**6.7 Open item, the fifth-result schema candidate.** The unattributed result exists in the checker under R-23 and is deliberately absent from the coverage-state set under R-24. A schema candidate introducing it would carry its own falsification condition and would reconcile to the existing four states rather than overriding them.

**6.8 Reconciliation, envelope status.** The suite envelope carries no first-class status or lifecycle member. Any lifecycle status an implementation needs rides the retention-event chain and is an interim home. A first-class status member is a schema-major-version candidate that, on introduction, reconciles to the historical chain rather than overriding it [1][3].

**6.9 Reconciliation, conformance class definitions.** The five conformance classes are named here and defined in the Conformance Methodology. Where the register entries constituting a Core or Extended claim change, Table 1 of the Crosswalk is re-verified and R-1's mapping is re-read [5][8].

**6.10 Open item, the issue date.** The milestone table of the current draft heads of terms places the issue of this specification on 12 September 2026. That date falls on a Saturday, and a milestone expressed on a day the parties do not work can be neither met nor missed cleanly. The working position adopted at this version is issue in draft alongside the heads of terms, so that the deliverable is visible at signature rather than promised.

**6.11 Open item, requirement testability.** Every requirement carries a test status, generated from this document and checked by the validator rather than asserted. At v3 the thirty-eight surviving requirements sort as follows: six exercised by a registered acceptance test, three by a corpus vector through the requirement register, seven testable by inspection only, nineteen fixture-ready, and three fixture-blocked.

*Fixture-ready* means the fixture can be built today, because the test asserts an enumeration, a shape or an exclusion and does not depend on a byte-level canonicalisation decision. Nineteen requirements sit here and they are the next body of work: the admissibility gate at R-17 to R-19, the coverage fold at R-20 to R-22 and R-24, the refusal path at R-25 to R-28, determination shape at R-33, R-34 and R-36, and the emitter obligations at R-9, R-10, R-11, R-16 and R-40.

*Fixture-blocked* means the test asserts byte-level identity and therefore cannot be authored before D-8 to D-13 are answered. R-35 compares determination digests, R-38 compares a payload commitment, R-41 is a differential test between two canonicalisers. A fixture written for any of the three today would fix a timestamp form, a digest reference form or an absent-against-null convention by accident, and would then declare non-conformant every implementation that had passed against it once the decision landed the other way. The canonicalisation decisions gate test authoring as well as emission, which is the stronger of the two reasons to answer them.

*Inspection only* means no fixture is possible at this layer and the requirement is verified by reading. Seven sit here, and each states why in its own text: truthfulness of a scope declaration is not testable by any party (R-13), whether a proposition is a fact rather than analysis is not decidable from its serialisation (R-37), whether content was an agreed term is not visible in the record that carries it (R-39), and the three presentation requirements bind a surface rather than a file.

A normative requirement with no test is either under-specified or misplaced. Applying that test rather than restating it removed three requirements at v3, which is recorded at Section 9.

---

## 7. Coverage discharge

This specification claims no material-loss discharge. Coverage QA remains the single register for material-loss status and this document maintains no second one [9].

Two candidates sit adjacent to its subject matter and are named so that a later reader does not mistake adjacency for discharge. ML-13, the maturity-calibration rule, requires that a reading implementation resolve any calibration to an externally owned matrix or to an explicit null and never assign the level itself; P-2 and P-3 are consistent with that requirement and do not discharge it. ML-15, the insurer application track, was deliberately re-scoped out of the parent and its content is orphaned; this specification homes the read contract and does not home the pricing moments, the warranty language or the legal character of covenants, all of which remain outside the suite.

Any discharge claim arising from this specification is made in Coverage QA at ratification, not here.

---

## 8. Versioning

Whole-integer versions only.

Major-version triggers: any change to the coverage-state set or its names; any change to the admissibility-gate outcomes or their names; any addition, removal or renumbering of a requirement in Section 3; any change to a registered acceptance test's threshold; any change to the join contract at R-16; any change to the mandatory content of the scope declaration at R-11.

Not a major-version trigger: correction of a reference version pin; population of content hashes at ratification; editorial reconciliation that alters no requirement.

A registered acceptance-test threshold is not renegotiated during a build. A threshold changed after a test has run is a new test.

A vacated identifier is not reused. Six identifiers are vacated to date: R-30 to R-32 at v2, and R-2, R-3 and R-29 at v3. No identifier is vacated at v4. Where a requirement moves between series, its former identifier is recorded as vacated with a pointer to its successor, so that a citation made against an earlier version resolves rather than silently redirecting.

---

## 9. Document revisions

**v4, 10 August 2026.** Two corrections, both produced by the estate checker on its first run rather than by a reading. R-1 restated the Crosswalk's level-number prohibition verbatim, which is the defect that removed R-2 and R-3 at v3, one requirement above them and unnoticed at the time; the sentence is now cited rather than restated and R-1 carries the expression rule alone. The known-carriers list at 6.1 is replaced by a measured one: a scan of the current Layer 1 estate found the retired cryptosuite identifier in twenty artefacts where a hand sweep had recalled two, and the correction order is stated, the Cryptographic Profile first because it owns the identifier. No requirement vacated at this version and no identifier renumbered.

**v3, 10 August 2026.** Every requirement carries a generated test status, so testability is a property the validator checks rather than a claim the author makes. Applying the rule that a normative requirement with no test is under-specified or misplaced removed three requirements. R-2 and R-3 vacated: both restated requirements the Core/Extended Crosswalk owns at its R-3 and R-4, and a restatement is a second copy that can drift from the first. R-29 vacated: whether a component failure attributable to the reading party may be recorded against the party being evidenced turns on who selected the component, which no record carries, so it is not a property of the interface and is left with the attribution mechanics where it operates. No identifier renumbered and none reused. Open item 6.11 rewritten from the generated classification: six registered-test, three corpus-vector, seven inspection-only, nineteen fixture-ready, three fixture-blocked on the canonicalisation decisions. The fixture-blocked finding is the substantive one, because it establishes that D-8 to D-13 gate test authoring as well as conformant emission. Driver: external review of v2, 10 August 2026, whose remaining challenge was testability; the classification answers it and shows that the right target is not zero untested but a specification with nothing misplaced in it.

**v2, 10 August 2026.** Requirement series split into R-series (conformance) and P-series (presentation) at 3.0, answering the question of which requirements are properties of the interchange and which are conditions on a claim. R-31 corrected: its v1 text prohibited a conformant implementation from producing an aggregate and permitted a reader to compose one, in one requirement; the prohibition now attaches to the label rather than to the arithmetic, at P-2. R-30, R-31 and R-32 vacated and restated as P-1 to P-3; no other identifier renumbered. References tagged Normative or Informative. Design rationale running past two sentences moved to Section 10. Traceability emitted as a machine-readable file with a validator, so requirement, register entry and acceptance test agree by test rather than by reading; generating it immediately exposed that twenty-nine of forty-one requirements carry no test, recorded as open item 6.11. Driver: external review of v1, 10 August 2026, whose fourth challenge and red-team question are both answered by the series split.

**v1, 10 August 2026.** Initial issue. Forty-one requirements, eight registered acceptance tests, ten open items.

---

## 10. Design rationale (informative)

Longer rationale is held here rather than inside the normative body, on the convention that reasoning running past two sentences leaves the requirement it explains. The Evidence Record Specification carries the same convention at its own Appendix A [1].

### 10.1 Why the verification method travels with the record

Under the controlled-identifiers model a referenced verification method absent from the latest controller document is treated as invalid or revoked, and a verification method's controller field is an assertion rather than necessarily true [12]. A record sealed today and checked at a claim four years out therefore fails because a key rotated in the ordinary course, not because anything was tampered with. The remedy is to make the record self-sufficient and to resolve the controller document as well, rather than instead of, the embedded method. The trade is recorded rather than hidden: embedding buys long-term checkability and gives up revocation reach, and resolving in addition is what recovers the reach where the network permits it. R-6 to R-8 carry the requirement; K-1 and K-2 test the two halves.

### 10.2 Why a failed read is not an adverse finding

A failure of the evidence pipeline is the pipeline's failure [14]. Converting it into an adverse finding against the party being evidenced is wrong in design, because it prices an outcome the evidenced party did not cause, and where an attribution rule governs it is wrong in law as well. The consequence for the interface is that the read statuses sit upstream of the coverage fold rather than inside it, and that the refusal path is first-class rather than an error branch. R-25 to R-29 carry it.

### 10.3 Why the requirement series were split at v2

An external implementer reading v1 asked, in effect, which requirements are properties of the interchange and which are conditions on a claim about a surface. The question exposed a contradiction in the v1 R-31, which prohibited a conformant implementation from producing an aggregate in its first sentence and permitted a reader to compose one in its second. The correction is structural rather than editorial: the interchange requirements and the presentation requirements bind different objects, so they carry different identifiers and different scopes of application. The prohibition that survives attaches to the label rather than to the arithmetic, which is the position the conformance criteria have always taken.

---

## 11. References

Each reference is tagged Normative or Informative. A normative reference must be read to build a conformant implementation; an informative reference supplies provenance, context or the estate record behind a decision. Content hashes are marked pending under the pre-ratification discipline. The Ratification Manifest is the signed hash source of truth for the pack instruments and the dependency register, and this specification defers to it rather than duplicating it.

1. **Arkaya Layer1 Evidence Record Specification v1**, Normative. 30 June 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/`, content hash pending population at ratification. The suite envelope this specification builds on: ten mandatory members, three optional members including the `scope` declaration and the reserved `ext` container, the chain and genesis rules, and the reader obligations on major and minor version handling. Its §3 illustrative `profileIdentifier` value is the carrier of the reconciliation at 6.1, and its §10 conformance statement is the emitter-side floor that R-4 restates in interface terms.

2. **Arkaya Layer1 Cryptographic Profile v4**, Normative. 1 July 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/`, content hash pending population at ratification. Owns canonicalisation, the SHA-256 record digest, signing, the proof and the tombstone mechanics, none of which this specification restates. It is the highest fan-in node in the Layer 1 estate and therefore the one where a version bump propagates furthest; the six open canonicalisation decisions route to its owner.

3. **Arkaya_Layer1_W3_Retention_and_EntitledRead_Companion_v9**, Normative. 13 July 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/`, content hash pending population at ratification. Homes the reserved retention and access namespaces and owns the tombstone construction, which commits external payload by digest so that no signed record is mutated. R-38's commit-by-digest construction cites that mechanism as its parallel, which is the point an engineer asks about first.

4. **Arkaya_Conformance_Methodology_v4**, Normative. 4 August 2026, David McKibbin, `10-Layer1-Custodian/Specifications/`, content hash pending population at ratification. Defines the conformance classes, the Core and Extended capability terms and the assessment criteria, under the criterion namespace CM-C-n-x. Its no-score discipline, that no conformance output is summed, weighted or ranked into a single number, is what R-5 and R-31 carry into the record and the read respectively.

5. **Arkaya_Layer1_W3_Core_Extended_Crosswalk_v1**, Normative. 6 July 2026, David McKibbin, `10-Layer1-Custodian/Specifications/`, content hash pending population at ratification. Ratified and hash-pinned, and normative for the resolution of retired-ladder language. Its §3.3 is the source of R-1's expression rule and its R-4 vocabulary firewall is the source of R-3. This is the reference that stops a specification of this kind quietly reintroducing a graded ladder from build material that still carries one.

6. **Arkaya Layer 1 Canonicalisation Requirement Note v2**, Normative. 9 August 2026, David McKibbin, proposed `10-Layer1-Custodian/Specifications/Conformance Suite/`, pre-ratification, content hash pending population at ratification. Records the cryptosuite adoption reasoning behind Section 2 and the reconciliation at 6.1, the six open decisions cited at 6.2, the seven decisions the scheme does answer and which are inherited on adoption, the no-normalisation consequence at 6.4, and the measured non-conformance that makes 6.3 a worked example rather than a caution.

7. **W3C, Data Integrity EdDSA Cryptosuites v1.0**, Normative. W3C Recommendation, 15 May 2025, `w3.org/TR/vc-di-eddsa`. Defines exactly two cryptosuites and requires the `cryptosuite` property to name one of them, which is the ground on which the house identifier is retired rather than profiled. Anchoring to a finalised Recommendation is also what lets a stranger verify with a stock library, so the standing of the underlying canonicalisation document is carried through the suite rather than asserted directly.

8. **GET Layer 1 requirement register** (`requirements.json`), 30 June 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/test-vectors/`, content hash pending population at ratification. Twenty-one stable requirement identifiers, level-tagged Core (twelve), Extended (seven) and n/a (two), each naming the specification, the section and the corpus vectors that exercise it. Every requirement in Section 3 maps to entries in this register rather than minting a parallel identifier set, which is what keeps the claim testable against vectors that already exist.

9. **Arkaya_Layer1_W3_Coverage_QA_v1**, Informative. 3 July 2026, David McKibbin, `10-Layer1-Custodian/Specifications/`, content hash pending population at ratification. The material-loss register, ML-1 to ML-19, and the single source of truth for material-loss status. Section 7 checks against it rather than maintaining a second register; ML-13 and ML-15 are the two entries adjacent to this specification's subject matter and neither is discharged here.

10. **Arkaya Layer 1 Suite Version Register v13**, Informative. 4 August 2026, David McKibbin, `10-Layer1-Custodian/_SuiteVersionRegister.md`. The currency authority every version pin above was checked against in the same turn it was written. It also records the correction of the cryptosuite pin away from the house identifier, which is the estate-level fact behind this reconciliation, and carries the reverse-dependency edges that determine which artefacts a bump to any reference above obliges a reader to re-check.

11. **RFC 3161, Time-Stamp Protocol.** A time-stamping authority binds a hash to an authoritative time and returns a signed token checkable with ordinary tooling. Cited because the independence claim otherwise rests silently on a clock, and a clock belonging to the emitting platform is not independent, which is what R-9 and R-10 keep separate.

12. **W3C, Controlled Identifiers v1.0**, Normative. W3C Recommendation, 15 May 2025, sections 2.1.2, 2.2, 2.3 and 3.3. A referenced verification method absent from the latest controller document is treated as invalid or revoked, and a verification method's controller field is an assertion rather than necessarily true. This is the whole reason for R-6 to R-8: without the embedded method, an ordinary rotation retrospectively invalidates a record nobody touched.

13. **OPS_MVP_Scoping_Addendum_v1**, Informative. 7 August 2026, David McKibbin, `20-Layer2-Commercial/14-MVP-Build-Scripts/`. The source of the eight registered acceptance tests and their thresholds, registered before any test was designed. It carries the retired cryptosuite identifier at its item 4 and takes the correction at its next whole-integer version per 6.1.

14. **OPS ReadLayer ArchitectureDecision v2**, Informative. 30 July 2026, David McKibbin, `20-Layer2-Commercial/14-MVP-Build-Scripts/`. The source of the nine read statuses at R-25, the connector-failure principle at R-29, and the determination and replay discipline at R-33 to R-36. Its rule that a failed read is the programme's evidence failure rather than an adverse finding is the one most likely to be lost in an implementation written to a happy path.

15. **OPS CovenantEvidenceSourceMap v3**, Informative. 31 July 2026, David McKibbin, `20-Layer2-Commercial/14-MVP-Build-Scripts/`. The count of record: sixteen obligations, forty-eight observables and sixteen source classes, with the mode-keyed coverage fold at its §8 that R-20 and R-21 carry, and the emitter-position rule at its §4.1 that R-22 carries. Its §6 join register is the open item at 6.5 and its §12 arithmetic is the open item at 6.6.

16. **OPS_TrackB_TriageGlide_BuildSpec_v1**, Informative. 29 July 2026, David McKibbin, `20-Layer2-Commercial/14-MVP-Build-Scripts/`. The closed three-value triage enumeration at R-28, and the determinism constraints at R-33: no model in the read path, no network access, no wall-clock read, byte-identical output on repeat runs. Its acceptance test A2 is why a read status can never become a fourth outcome.

17. **RFC 2119 and RFC 8174 (BCP 14).** The requirement-keyword interpretation, in force only where the keywords are capitalised. Cited because a specification that uses the words without adopting the interpretation invites an implementer to read emphasis where a test was intended.

---

*Internal · Class A · AKR AIPS · pre-ratification · v4*
