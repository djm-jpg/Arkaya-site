# Check a sealed record yourself

About five minutes. Stock open-source tooling only. No Arkaya package, no account, and it works with the network switched off.

The point of this file is narrow and worth stating before the commands: you are not being asked to trust that these records verify. You are being asked to check.

---

## What you need

One of these stacks. Both are ordinary.

**Python**

```
pip install jcs base58 cryptography
```

**JavaScript** (Node 18 or later)

```
npm install canonicalize bs58
```

Nothing on either list is ours.

---

## The check, in JavaScript

`vectors/xverify_v5.mjs` is a complete independent verifier, written against the specification rather than against our generator. Run it over the vector set:

```
node vectors/xverify_v5.mjs vectors/vectors_v5_candidate.json
```

It recomputes, for every positive vector, the canonical content, the canonical proof configuration, the record digest and the Ed25519 signature, and it checks every negative case for the reason it is meant to fail. Forty-nine checks.

## The check, offline

Disconnect the network, or block every Arkaya domain at DNS, and run it again. The result is identical. That is registered acceptance test V-3, and the claim that verification does not route through Arkaya either passes this test or comes off the exhibit.

## The check, by hand

If you would rather see the arithmetic than run someone else's script, four steps.

1. Take a record and remove its `proof` member. Canonicalise what remains with an RFC 8785 library.
2. SHA-256 that. Prefix the multihash bytes `0x12 0x20`, encode base58-btc, prefix `z`. Compare with the record digest, and with the `previousDigest` of the record that follows it in the chain.
3. Take the `proof` object, remove `proofValue`, canonicalise it. The signing input is SHA-256 of that, concatenated with SHA-256 from step 1, in that order.
4. Verify the Ed25519 signature in `proofValue` against the key in `verificationMethod`. The key travels with the record, which is why step 4 needs no network.

All four must pass. The specification states the same procedure at Section 8 of the Cryptographic Profile.

---

## What a failure means

The vector set carries fifteen negative cases, each with a stated reason. If your implementation accepts one of them, the difference is in your implementation or in our text, and either finding is worth having. If it rejects a positive case, compare canonical forms before comparing digests: a digest mismatch tells you two implementations disagree, and the canonical form tells you where.

The negative case worth running first is `N-15`. Two strings that look identical on screen, differing only in Unicode composition, produce different digests. It is the one divergence a verifier cannot detect after the event, and the one an implementer is most likely to introduce without noticing.
