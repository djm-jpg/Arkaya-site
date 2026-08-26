# Arkaya Layer 1 — implementer pack

**Version 1 · 10 August 2026 · open material**

Everything here is open. The schema, the specifications, the test vectors and the reference verifier carry no fee and no licence condition, because a verification layer that charged for its own contract would not be one. Nothing in this pack requires an account with Arkaya, a call to an Arkaya service, or an Arkaya library at any point in production, verification or reading.

What is not here is the mapping library, the field sets and the covenant benchmark. Those are licensed, and they are a separate conversation.

---

## What you are building

Two roles, and most implementers need one of them.

**An emitter** produces sealed evidence records: a canonical JSON object, hash-chained to its predecessor, signed under the `eddsa-jcs-2022` cryptosuite, carrying its own verification method and a scope declaration for the run that produced it.

**A reading implementation** consumes a directory of those files and produces a determination: it runs the admissibility gate, folds coverage per obligation into four states, routes anything it could not read to a refusal path, and emits a determination that replays to the same digest on every build.

The two sides are fixed together in one document deliberately. A record form with no stated read is a file nobody can act on; a read with no stated record form is a private integration wearing a standard's clothes.

## The contract, in one line

What passes between the parties is a directory of files. There is no API, no SDK dependency, no callback and no account.

---

## Where to start

1. `specifications/Arkaya_Layer1_Cryptographic_Profile_v5.md`. How a record is canonicalised, hashed, signed and verified. Read Section 3 first; it is where interoperability is won or lost.
2. `specifications/Arkaya_Layer1_Interface_and_Conformance_Specification_v4.md`. What an emitter emits and what a reader consumes, with the registered acceptance tests.
3. `VERIFY.md`. Check a sealed record yourself, in about five minutes, with stock open-source tooling and the network switched off.
4. `vectors/vectors_v5_candidate.json`. The oracle: seven positive cases, fifteen negative. If your implementation reproduces the positives byte for byte and rejects the negatives for the stated reasons, it agrees with ours.
5. `corpus/`. The conformance corpus for a reading implementation, 34 fixtures across 21 requirements.

## The three things that most often break interoperability

Every one of them is a case where two reasonable implementations produce different bytes and neither is wrong under the underlying standard. They are the reason this profile exists on top of the cryptosuite rather than instead of it.

**Canonicalisation is not serialisation.** If you already have a JSON serialiser that sorts keys and strips whitespace, you do not have a canonicaliser. Our own reference canonicaliser passed fifty-eight adversarial checks while non-conformant to the scheme on UTF-16 code-unit sorting. Use a verified RFC 8785 library; they exist for JavaScript, Java, Go, C# and Python.

**Timestamps have exactly one lexical form.** `2026-08-10T12:00:00.000Z`, with three fractional digits, uppercase `T` and `Z`, no offset form and no leap second. RFC 3339 admits several spellings of one instant and the canonicaliser reconciles none of them: three spellings are three digests.

**Unicode composition is fixed at the point the record is created.** The scheme performs no normalisation, so two strings identical on screen and differing in composition produce different digests. No verifier can detect it afterwards.

Beyond those: no JSON null anywhere, safe-range integers only with everything else as a string, and digest references as base58-btc multibase over the multihash-prefixed digest rather than as `sha256:` hexadecimal.

---

## What is not yet settled, stated plainly

Both specifications are in review and neither is ratified. The vector set is a candidate. Version-pin what you build against and expect the pin to move once.

- The Cryptographic Profile v5 carries a compatibility class of MAJOR and a ratification act is outstanding. Records emitted under the previous version remain verifiable; they are not conformant to v5.
- The vector set becomes normative on adoption. On adoption it is hash-pinned and never edited: a change produces a new set and supersedes rather than revises, so an implementation certified against a set stays certifiable against the bytes it was tested on.
- The conformance corpus is a candidate on the same basis.

Telling you this is the point rather than a caveat. A document that looked settled and was not would be the failure mode the whole architecture exists to argue against.

---

## What we would like back

If you build to this, tell us what was ambiguous. Specifically: any place where two readings of the text were both defensible, and any vector your implementation reproduced only after a guess. Ambiguity found by a stranger is worth more to this specification than anything we can find ourselves, because two implementations written from one reading will agree even when the reading is wrong.

---

## Contents and integrity

`MANIFEST.json` lists every file with its digest, computed in the form the Profile requires at Section 3.3. Check the pack against it before you rely on anything in it, which is also a five-minute exercise of the machinery this pack describes.

`SECURITY.md` is for whoever has to approve running code from outside your organisation: what the pack contains, what the code does and does not do, the dependency versions to pin, and why you do not have to run any of it to use the specification.

---

David J McKibbin · Simon Hudson   Co-Founders
djm@arkayarisk.com · +44 (0)7972 178759 · smh@arkayarisk.com · +1 (914) 309-6397
Arkaya Risk Limited, a company registered in England and Wales (no. 17380022). Registered office: Oxford House, 15-17 Mount Ephraim Road, Tunbridge Wells, England, TN1 1EN.
