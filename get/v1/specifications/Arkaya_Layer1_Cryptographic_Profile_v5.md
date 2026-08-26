# Arkaya Layer 1 — Cryptographic Profile

**Version:** 5
**Dated:** 2026-08-10
**Owner:** David McKibbin
**Repository:** `10-Layer1-Custodian/Specifications/Conformance Suite/`
**Status:** In review, pre-ratification. Content hashes pending population. Test vectors in candidate form, differential test passed; see Section 9.1. Compatibility class MAJOR; see Section 14A.
**Class:** A (institutional, normative). RFC 2119 register.
**Supersedes:** v4, 1 July 2026. See Document revisions at Section 15.

Layer 1, open and neutral. Pillar 3, Cryptography. The signing, canonicalisation and verification profile an engine implements to emit GET evidence.

---

## 1. Purpose and status

This document defines the cryptographic profile a GET-PRODUCER implements so that the evidence it emits is signed, hash-chained and independently verifiable with off-the-shelf tooling. It is the first foundational artefact of the Layer 1 specification set, and it is what lets a producer build against the bar before the remaining specifications are complete [1].

The profile pins the W3C Data Integrity EdDSA cryptosuite `eddsa-jcs-2022`: Ed25519 signatures over JSON canonicalised by RFC 8785 [2][3][4]. It adds the determinism and chaining constraints a hash-linked evidence record requires. Where this profile is silent, `eddsa-jcs-2022` and its normative references govern; where this profile states a constraint the cryptosuite leaves open, this profile governs for GET evidence.

The house profile identifier used through v4 is retired at this version. The Data Integrity EdDSA Cryptosuites specification defines exactly two cryptosuites and requires the `cryptosuite` property to name one of them, so a third identifier standing beside them is an alternative to alignment rather than an instance of it [2][7]. Records and bindings name the cryptosuite. The correction and its estate cascade are recorded at Section 15.

Sections 2 to 11 are normative. Section 12, Section 13, Section 14A, Section 15, Appendix A and passages marked as notes are informative. The keywords SHALL, SHALL NOT, MUST, MUST NOT, SHOULD, SHOULD NOT, MAY and OPTIONAL are to be interpreted as in RFC 2119 and RFC 8174 (BCP 14), and only when in capitals [5].

## 2. The profile in one line

A conformant producer canonicalises each evidence record with JCS, hash-chains it to its predecessor with SHA-256, signs it with Ed25519 under `eddsa-jcs-2022`, and expresses the signature as a base58-btc multibase value in a Data Integrity proof, so any third party verifies the signature and the chain without the producer in the loop.

## 3. Canonical form

Every evidence record SHALL be canonicalised using the JSON Canonicalization Scheme, RFC 8785 (JCS), before hashing or signing [3]. JCS fixes object member ordering by UTF-16 code-unit value, removes insignificant whitespace, normalises numbers through the ECMAScript number-to-string algorithm, and emits UTF-8 [3]. The following constraints harden JCS for hash-chained evidence and SHALL hold.

The record SHALL be valid I-JSON (RFC 7493): unique object member names, no NaN or Infinity, and UTF-8 throughout [6]. Because JCS serialises numbers through IEEE 754 double precision, JSON number values SHALL be limited to integers within the safe range, that is −(2^53 − 1) to (2^53 − 1). Every other numeric value, any fractional or decimal value and any integer outside that range, SHALL be encoded as a JSON string and never as a JSON number. Restricting JSON numbers to safe-range integers removes IEEE 754 rounding, exponent formatting and negative zero from the wire entirely, which is where two conformant canonicalisers could otherwise produce different bytes for the same logical value.

### 3.1 Timestamps

Timestamps SHALL be RFC 3339 UTC strings in exactly one lexical form: four-digit year, two-digit month and day, the literal uppercase `T`, two-digit hour, minute and second, a decimal point, exactly three fractional digits, and the literal uppercase `Z`. For example `2026-08-10T12:00:00.000Z`.

A timestamp SHALL NOT carry an offset in any other form, including `+00:00`. Lowercase `t` or `z` SHALL NOT be used. The bracketed-suffix extension of RFC 9557 SHALL NOT be carried.

The field ranges are normative and are stated because the lexical shape alone does not constrain them: hours 00 to 23, minutes 00 to 59, seconds 00 to 59. A leap second, that is a seconds field of 60, is therefore excluded by the range and not only by prose. A validator implementing the shape without the range accepts `2026-06-30T23:59:60.000Z`, which the differential test at Section 9 demonstrated on its first run.

This form binds every timestamp inside the signed content, including the proof's `created` member, and every timestamp inside any object this profile governs.

Note: RFC 3339 admits several spellings of one instant, and JCS preserves a timestamp as an opaque string, so it reconciles none of them. Three spellings of one instant are three strings and three digests. Fixing the form is therefore a canonicalisation constraint, not a formatting preference. Precision finer than a millisecond, where a producer requires it, travels in the record body as a string; the envelope's declared precision does not change.

### 3.2 Absent and null

A JSON null SHALL NOT be emitted in any record or in any object this profile governs. An optional member is either present with a value or absent. A record carrying a null is non-conformant.

Note: null and an absent member serialise faithfully and differently under JCS, so admitting both would let two producers sign different bytes for the same fact. Prohibition rather than a two-valued convention also preserves the estate's discipline that absence is typed: a reason is recorded in a typed member, never signalled by a value that carries no reason and no provenance.

### 3.3 Binary values and digest references

Binary values SHALL be base58-btc multibase strings.

A digest reference, wherever it appears outside the proof, SHALL take the same form: a base58-btc multibase string over the multihash-prefixed digest. This binds `previousDigest` at every position other than the first in a chain, any payload commitment by digest, and any digest carried in a determination or an assurance read.

The genesis constant is exempt. It is a reserved token rather than a digest: it is the multibase base58-btc encoding of a thirty-two-byte all-zero value, defined by the Evidence Record Specification, and it is the digest of nothing [8]. Requiring a multihash prefix on it would assert that a hash function produced it, which is false. The exemption is stated here rather than in the Evidence Record Specification because it carves out this profile's own rule; the constant itself is unchanged and its owner is untouched.

A digest reference SHALL NOT be expressed as an algorithm-prefixed hexadecimal string. Note: the multibase prefix identifies the encoding and the multihash prefix identifies the hash function, so a separate textual algorithm prefix is redundant, and a second encoding for one object obliges every reader to normalise before it can compare.

### 3.4 The exclusion set

Canonicalisation acts on an object with a defined set of members removed. The set is stated per object type, because JCS canonicalises whatever it is handed and has no view on what should have been removed first.

For every object this profile governs, the exclusion set SHALL be the signature value carried by that object, and nothing else.

- **Record.** `proofValue`, per `eddsa-jcs-2022` and Section 7.
- **Binding.** The counterparty signature value only. The signer identity, the created timestamp and the proof purpose remain inside the signed content.
- **Determination and assurance read.** The signature value only, on the same rule.
- **Chain entry.** Nothing is excluded.

Note: a wider exclusion is not a canonicalisation defect but an integrity defect. Removing a whole signature block from a binding would take the signer identity out of what the signature covers, so the binding could be re-signed by a different party with no change to the signed bytes. The cryptosuite made the narrow choice deliberately and this profile follows it for every object.

### 3.5 Unicode form

JCS performs no Unicode normalisation and requires that string data be preserved as it stands [3]. Two strings that appear identical and differ in composition therefore canonicalise to different bytes and to different digests. A producer SHALL fix the Unicode form of a string at the point the record is created. No canonicaliser will do it, and no verifier can detect it after the fact.

### 3.6 Edge cases

Because Section 3 restricts JSON numbers to safe-range integers, two whole classes of divergence are removed at source: exponent notation cannot occur, since ECMAScript renders no safe-range integer in exponent form, and negative zero cannot occur as a JSON number. The remaining cases follow RFC 8785 exactly, and the companion vectors at Section 9 exercise each, so an implementer cannot mistake them for undefined behaviour. An empty object serialises as `{}` and an empty array as `[]`. Strings are valid Unicode encoded as UTF-8; a lone surrogate is invalid and SHALL be rejected, and a valid surrogate pair is preserved as its UTF-8 encoding. A duplicate object member name is invalid under I-JSON and SHALL be rejected, not de-duplicated.

## 4. Hashing and the evidence chain

The record digest is the SHA-256 hash of the canonical form of the record content, that is the record with its proof object removed. SHA-256 is the hashing function of `eddsa-jcs-2022` and is reused here for the chain so a verifier needs one hash primitive, not two [2].

Each record SHALL carry a `previousDigest` equal to the record digest of the immediately preceding record in the same chain, expressed per Section 3.3. The first record in a chain SHALL set `previousDigest` to the genesis constant, which is fixed in the Evidence Record Specification as the multibase base58-btc encoding of a thirty-two-byte all-zero value and is published in the companion vectors rather than transcribed into a normative document [8]. A verifier SHALL accept the genesis constant only at sequence position zero.

A verifier SHALL recompute each record digest and SHALL reject the chain at the first record whose `previousDigest` does not match its predecessor's recomputed digest. A gap or a reordering is therefore visible, which is the append-only guarantee the assurance read relies on [1].

Chaining is defined within a single chain. A producer MAY maintain multiple independent chains; what delimits a chain, and any aggregation across chains, is defined in the Evidence Record Specification [8]. Note: the sequential dependence within a chain is intrinsic to a tamper-evident hash chain and is the integrity property, not a defect. Throughput is obtained by partitioning into independent chains, not by weakening the link.

## 5. Signature

Records SHALL be signed with Ed25519 (PureEdDSA) as defined in RFC 8032 [4]. Ed25519 is deterministic by construction: it derives its per-signature nonce from the key and message, so signing requires no random source at issuance and the same key over the same record yields the same signature, which serves reproducibility. Public keys are 32 bytes and signatures are 64 bytes [4].

The signing input follows the `eddsa-jcs-2022` hashing algorithm, stated here so an implementer need not infer it: `hashData` SHALL be the SHA-256 digest of the canonical proof configuration concatenated with the SHA-256 digest of the canonical record content, in that order, and Ed25519 signs `hashData` [2]. This is the standard cryptosuite construction, not a house variant; a correct off-the-shelf `eddsa-jcs-2022` implementation produces the same `hashData`, and the published test vectors are the byte-level authority where any doubt arises. Ed25519ph and Ed25519ctx SHALL NOT be used.

## 6. Keys and verification methods

A signing key SHALL be expressed as an Ed25519 Multikey: the public key encoded as a base58-btc multibase string under the Multikey multicodec, which is the verification method a verifier resolves to check a signature [2]. The verification method SHALL be referenced from the proof, and its controller SHALL be the producer identifier registered with the Custodian. Private keys SHOULD be held in a hardware security module or secure enclave; key custody, rotation and revocation are specified in the Attestation Substrate Specification and are out of scope here [1].

Note: a hardware security module here means, for example, a module certified to FIPS 140-2 or FIPS 140-3 Level 3 or higher, a cloud key-management service backed by such a module, or a hardware-backed trusted execution environment; the normative acceptable bar is set in the Attestation Substrate Specification, not here.

A producer's identity is stable and independent of its signing key. A producer MAY rotate its signing key while retaining the same producer identity; the binding of keys to a producer identity is the Attestation Substrate Specification. Because a verifier resolves the verification method named in each record's proof, records signed under a rotated key remain verifiable against the key that was in force when they were signed.

Note on carriage by value: where a record embeds its verification method by value rather than by reference alone, the requirement and its failure states are the Interface and Conformance Specification's, which homes that obligation into the suite [9]. This profile governs the form of the key, not whether it travels with the record.

## 7. The proof object

Each record SHALL carry exactly one Data Integrity proof with type `DataIntegrityProof`, cryptosuite `eddsa-jcs-2022`, a `proofPurpose` of `assertionMethod`, a `created` timestamp in the form fixed at Section 3.1, a `verificationMethod` referencing the producer's Ed25519 Multikey, and a `proofValue` carrying the Ed25519 signature as a base58-btc multibase value [2].

The `proofValue` SHALL be the only proof member excluded from the signing input, per `eddsa-jcs-2022` and Section 3.4. The canonical proof configuration, the proof object without `proofValue`, is itself canonicalised by JCS and is published in the vectors as a distinct field so a signature failure can be isolated from a canonicalisation failure.

## 8. Verification procedure

A verifier, with the record and the producer's public verification method and no contact with the producer, SHALL: canonicalise the record content with JCS; recompute the record digest and confirm the chain link against `previousDigest`; reconstruct the signing input per `eddsa-jcs-2022`; and verify the Ed25519 signature in `proofValue` against the verification method [2][4]. All four checks SHALL pass for the record to verify.

Because every primitive in this chain is a finalised public standard, verification uses off-the-shelf libraries and no Arkaya component [1].

## 9. Test vectors

The normative oracle for this profile is its test vectors, published with this specification. The vectors are normative because this specification adopts and publishes them, not because any implementation generated them; the vector-generation tooling produces candidate values, which become normative on adoption.

**Regeneration is an act of this version and is discharged in candidate form.** A candidate set of seven positive and fifteen negative vectors was generated on 10 August 2026 and re-computed independently in a second language; the differential result is at Section 9.1. The set becomes normative on adoption, not on generation. The v4 vectors were generated before the decisions at Sections 3.1 to 3.4 and do not exercise them. The v5 vector set SHALL carry: a timestamp in a non-conformant lexical form, once per prohibited variant; a record carrying a JSON null; a digest reference in the prohibited hexadecimal form; a binding with a wider exclusion set than Section 3.4 permits; and a pair of strings identical on screen and differing in Unicode composition. The companion file is renamed from its v4 house-identifier form; the new filename is registered at ratification. No value from the v4 set is carried forward without regeneration.

On adoption the vector set is hash-pinned in the Suite Version Register and SHALL NOT be edited. A change produces a new vector-set version; the adopted set is superseded and never revised, so an implementation certified against a set remains certifiable against the bytes it was tested on. This is the rule the Versioning, Compatibility and Change-Control Policy already applies to requirement identifiers at ADR-006, applied to vectors.

Each vector carries: a logical input, its JCS canonical form, the canonical proof configuration that forms part of the signing input, the SHA-256 record digest, the Ed25519 `proofValue`, and the expected verification result with a pass or fail reason. The vectors exercise every edge case at Section 3.6, a genesis record, and a key-rotation case. Negative vectors carry a deliberate fault, a reordered key, an unsafe number encoded as a number, a tampered byte, a broken chain link, a lone surrogate, and a duplicate member name, and assert the expected failure.

Illustrative example, hand-verifiable for canonicalisation only. Digest and signature values live in the companion file so that no value an implementation merely produced is presented here as authoritative.

Input, formatted for reading:

```
{ "recordType": "Signal", "id": "rec-002", "occurredAt": "2026-06-30T09:00:00.000Z",
  "amount": "100000000000000000000", "previousDigest": "z4Xy..." }
```

JCS canonical form, members sorted by UTF-16 code unit, whitespace removed, the over-2^53 value carried as a string:

```
{"amount":"100000000000000000000","id":"rec-002","occurredAt":"2026-06-30T09:00:00.000Z","previousDigest":"z4Xy...","recordType":"Signal"}
```

### 9.1 Differential result, 10 August 2026

The candidate set was generated in Python, using the `jcs` canonicaliser and the `cryptography` Ed25519 implementation, and re-computed in JavaScript, using the `canonicalize` module and the Ed25519 implementation in `node:crypto`. The two share no code. Forty-nine checks were run across canonical content, canonical proof configuration, record digest, signature verification, chain linkage, the genesis constant and every negative case, and the two implementations agree on all of them.

Two failures on the first run, both instructive and both since corrected.

The generator built four records with incrementing sequence numbers pointing at the same predecessor digest, which is a broken chain. It is the defect the chain exists to make visible, and it was invisible to the side that produced it and obvious to the side that checked it.

The leap-second exclusion was stated in prose and not in the lexical constraint, so a validator built from the shape at Section 3.1 accepted a seconds field of 60. Section 3.1 now states the field ranges. This is a specification finding rather than a test defect: the prose was correct and unimplementable.

Neither would have been found by reading. This is the first evidence in the estate that two independent implementations produce identical bytes from the same record, and the claim that any implementer can build to this profile and interoperate rests on it.

## 10. Algorithm agility

This profile fixes Ed25519, JCS and SHA-256 by pinning `eddsa-jcs-2022`. Cryptographic evolution is handled by a new whole-integer version of this profile pinning a different cryptosuite, not by revising the constraints of this one.

Each record identifies the cryptosuite under which it was signed through the proof's `cryptosuite` member, and each binding names the same identifier per Section 14. A verifier therefore selects the correct verification procedure from the object itself, and objects signed under different cryptosuites remain independently verifiable side by side, which is what makes a future migration additive rather than a break.

Note: v4 handled agility through a house profile identifier registered with the Custodian. That mechanism is withdrawn with the identifier. A successor suite, post-quantum or hybrid, will in any case require a whole-integer version of this profile and a re-signing exercise, so the house register bought less than it cost.

## 11. Conformance

A GET-PRODUCER conforms to this profile when it canonicalises per Section 3, chains per Section 4, signs per Sections 5 to 7, and reproduces every positive test vector byte-for-byte and fails every negative vector.

A GET-VERIFIER conforms when it performs Section 8 and returns the expected result for every vector.

An implementation SHOULD obtain canonical form from a verified RFC 8785 library rather than from authored canonicalisation, and conformance between two implementations SHALL be established by differential test rather than by inspection. Note: a serialiser producing sorted, whitespace-free output is not a canonicaliser. The reference implementation's own canonicaliser passed fifty-eight adversarial checks while non-conformant to JCS on UTF-16 code-unit sorting, so agreement on tested values is not conformance [7].

Conformance to this profile is necessary but not sufficient for engine recognition, which is established through the lifecycle and the full harness [1].

## 12. Security considerations

The profile protects integrity, not confidentiality or the truth of inputs [1]. A signature over false content is still a valid signature over false content. A compromised private key signs repudiable records, which is why custody belongs in a hardware security module and why the independent counter-seal at the Evidence node exists; the Attestation Substrate Specification is therefore a hard dependency before any production deployment. Deterministic Ed25519 removes nonce-reuse failure but makes key custody the whole of the signing-side risk.

The number-as-string constraint at Section 3 closes the canonicalisation-divergence attack, in which two implementations disagree on the bytes of a large number and a record verifies for one verifier and not another. Sections 3.1 to 3.5 close the same attack on four further surfaces: the timestamp form, null, the digest reference and the exclusion set are each a place where two conformant-looking implementations could sign different bytes for the same fact, and the Unicode-composition case is the one a verifier cannot detect after the event.

## 13. What this is not

This is not the record schema; the field set, the record types and the genesis constant are the Evidence Record Specification [8]. It is not key management; trust anchors, rotation and revocation are the Attestation Substrate Specification. It is not the interface; what a conformant emitter emits at run level and what a conformant reader consumes are the Interface and Conformance Specification's [9]. It is not a scoring function; it signs evidence and carries no score. It is not a new cryptographic primitive; it pins finalised public standards so verification needs no Arkaya code.

## 14. What a binding names

A binding SHALL name the cryptosuite, `eddsa-jcs-2022`, and SHALL NOT name a separate canonicalisation identifier beside it. The cryptosuite entails the canonicalisation, the hash and the signature, so one identifier governs all three and a record and its binding are checkable against each other by string comparison.

Note: two identifiers can disagree. A binding naming a canonicalisation scheme while the proof it governs names a cryptosuite implying another would not be caught by the four checks at Section 8, which never read the binding, and the conflict would then be a matter of interpretation. The Covenant Agent Specification's binding member 1 takes this correction at its next whole-integer version, which that artefact and the Canonicalisation Requirement Note both already record [7].

## 14A. Compatibility class

The compatibility class of this version is **MAJOR**, on the Versioning, Compatibility and Change-Control Policy's own test: a record that was conformant under v4 is not necessarily conformant under v5. A record carrying `2026-06-30T09:00:00Z`, a JSON null, or a hexadecimal digest reference satisfied v4 and does not satisfy Sections 3.1 to 3.3. Existing records still verify, since a signature covers the bytes actually signed; what changes is conformance, not integrity.

The migration window is empty, and empty as a matter of fact rather than of convenience. No conformant production emission exists. The demonstration corpus is synthetic and is regenerated under Section 9 in any case. This is the reasoning the Core/Extended Crosswalk applied to certificates when it retired the level ladder: grandfathering and migration are empty classes where there is nothing to grandfather, and the honest response is to say so rather than to draft a window nobody will use.

A MAJOR increment is a reserved matter under the Custodian Charter and requires the two-thirds supermajority the Charter sets. That is a board act. This section states the class; it does not confer the approval.

## 15. Document revisions

**v5, 10 August 2026.** Six canonicalisation decisions closed and the house identifier retired.

- **The identifier.** `ArkayaEd25519-v1` is retired. The profile pins `eddsa-jcs-2022` and objects name the cryptosuite. Section 10 is rewritten, since agility was carried by the retired identifier. A mechanical scan of the current Layer 1 estate on 10 August 2026 found the retired identifier in twenty artefacts, where a hand sweep had recalled two; the cascade is parent-first from this version and is set out in the correction order.
- **D-8, the exclusion set,** at Section 3.4. Settled for records at v4 §7; now stated per object type, narrow in every case.
- **D-9, the timestamp lexical form,** at Section 3.1. Settled as UTC at v4 §3; now a single lexical form with three fractional digits.
- **D-10, the digest reference form,** at Section 3.3. Base58-btc multibase over multihash, consistent with the binary-value rule the profile already carried. The reference implementation's `sha256:` and hexadecimal form is a non-conformance and is corrected there.
- **D-11, absent against null,** at Section 3.2. Null prohibited. One parent-side use survives outside this profile's reach and is recorded as a reconciliation below.
- **D-12, decimal handling.** Already settled at v4 §3 and carried unchanged. It required no decision and was recorded as open in error.
- **D-13, what the binding names,** at Section 14. The cryptosuite, and nothing beside it.

Corrections made in the same pass: Section 3.1 states the field ranges, since the lexical shape alone admits a leap second and the prohibition had been carried in prose a validator cannot implement; Section 4's statement that the genesis constant was not yet fixed is withdrawn, the Evidence Record Specification having fixed it at its §6; Section 3.5 states the Unicode-composition consequence, which the profile had not carried; Section 11 carries the differential-test rule and the sorted-serialiser trap.

Resolved in review, after the candidate vectors surfaced it. The genesis constant does not take the digest-reference form at Section 3.3, and the exemption is now stated in that section: the constant is the digest of nothing, so requiring a multihash prefix on it would assert a hash function produced it. The exemption carves out this profile's own rule and leaves the Evidence Record Specification untouched, so no version of that specification is required.

The compatibility class is assigned at Section 14A: MAJOR, with an empty migration window, pending the board supermajority a reserved matter requires. The maturity-calibration field requires an explicit occupancy-pending null and lies with the Data Model, not with this profile; Section 3.2 does not reach it and a typed sentinel is proposed to its owner rather than imposed. The vectors exist in candidate form and have passed a two-implementation differential test, so no implementation can claim v5 conformance until they are adopted, which is a board act rather than an engineering one.

## 16. References

1. **GET Conformance and Assurance v4**, 29 June 2026, David McKibbin, `10-Layer1-Custodian/Specifications/`, content hash pending population at ratification. Sections 2, 3 and 5: the conformance object, the assurance read's integrity properties, and the GET-PRODUCER, GET-VERIFIER and GET-ATTESTATION classes this profile serves. Establishes that integrity, not confidentiality or input truth, is the property in scope.
2. **W3C, Data Integrity EdDSA Cryptosuites v1.0**, W3C Recommendation, 15 May 2025, `w3.org/TR/vc-di-eddsa`. The cryptosuite this profile pins: Ed25519 over JCS, SHA-256 hashing, `DataIntegrityProof` with a base58-btc multibase `proofValue`, and the Multikey verification method. It defines exactly two suites and requires the `cryptosuite` property to name one of them, which is the ground on which the house identifier is retired rather than profiled.
3. **RFC 8785, JSON Canonicalization Scheme (JCS).** Fixes member ordering by UTF-16 code unit, number normalisation through the ECMAScript number-to-string algorithm, whitespace removal and UTF-8 output, including the negative-zero, exponent, empty-container and surrogate behaviour Section 3.6 relies on. It also states that a scheme depending on it must preserve string data as it stands, which is the basis of Section 3.5. Verified at `datatracker.ietf.org/doc/rfc8785`.
4. **RFC 8032, Edwards-Curve Digital Signature Algorithm (EdDSA).** Ed25519 PureEdDSA, 32-byte keys, 64-byte signatures, deterministic nonce derivation. The signature primitive, chosen because determinism removes nonce-reuse risk and aids reproducibility.
5. **RFC 2119 and RFC 8174 (BCP 14).** The requirement-keyword interpretation, in force only when the keywords are capitalised.
6. **RFC 7493, The I-JSON Message Format.** Unique member names, finite numbers, UTF-8. The interoperability baseline JCS assumes and this profile makes explicit, including the safe-integer constraint that forces exact large values to strings.
7. **Arkaya Layer 1 Canonicalisation Requirement Note v2**, 9 August 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/`, pre-ratification, content hash pending population at ratification. Raised the six decisions this version closes, recorded the cryptosuite adoption reasoning, and measured the reference canonicaliser's non-conformance that Section 11 cites. Its account of D-12 as open, and its two-artefact carrier list, are both corrected here, which is a finding about hand sweeps rather than about the note.
8. **Arkaya Layer1 Evidence Record Specification v1**, 30 June 2026, David McKibbin, `10-Layer1-Custodian/Specifications/Conformance Suite/`, content hash pending population at ratification. The envelope, the record types, the chain and partition model, and the genesis constant this profile's Section 4 previously described as unfixed. Its illustrative `profileIdentifier` value carries the retired house identifier and takes the correction in the cascade.
9. **Arkaya Layer 1 Interface and Conformance Specification v4**, 10 August 2026, David McKibbin, `20-Layer2-Commercial/14-MVP-Build-Scripts/Interface and Conformance suite/`, pre-ratification, content hash pending population at ratification. Homes the run-level scope declaration, the by-value verification method, the anchored-time obligation and the read-side contract. It references this profile and does not restate it; this profile references it for the carriage obligations at Section 6 and does not restate those.

## Appendix A. Design rationale (informative)

Ed25519 (RFC 8032) for a small, fast, widely implemented signature with deterministic nonces, which removes the nonce-reuse failure mode and makes signing reproducible. JCS (RFC 8785) because byte-determinism across independent implementations is the property a conformance suite needs, and JCS is a finalised standard rather than a bespoke scheme. SHA-256 because it is the hashing step of `eddsa-jcs-2022`, so reusing it for the chain means a verifier loads one hash primitive, not two. Base58-btc multibase because it is the encoding the W3C Data Integrity and Multikey ecosystem uses, so proofs and keys verify with off-the-shelf tooling; the modest encoding cost is the price of that interoperability, taken deliberately. W3C Data Integrity because it makes the evidence verifiable with standard libraries and no Arkaya component, which is what lets a partner and later a competitor rely on the bar. Deterministic signatures so that the same record under the same key yields the same bytes, on which the test vectors depend.

On the six decisions closed at v5. Each of them is a place where JCS produces a well-formed result from either of two inputs and has no view about which the producer should have handed it. That is not a weakness in JCS, which canonicalises what it is given; it is the boundary between a canonicalisation scheme and a profile. A profile that pins a cryptosuite and stops has done half the work, and the missing half is invisible until two implementations exist, which is why the decisions sat open for as long as there was only one.

---

*Internal · Class A · AKR AIPS · pre-ratification · v5*
