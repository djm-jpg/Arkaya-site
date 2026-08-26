#!/usr/bin/env python3
"""Candidate test vectors for Arkaya Layer 1 Cryptographic Profile v5.

The vectors this produces are CANDIDATES. They become normative on adoption by the
profile, not because this tool generated them, per Profile v5 section 9.

Determinism. The signing key is derived from a fixed seed and every timestamp is fixture
data, so two runs of this file produce byte-identical output. Nothing here reads a clock.

Independence. The digests and signatures are computed here in Python and re-computed in
`xverify_v5.mjs` in JavaScript, using a different canonicaliser (`canonicalize` npm
against `jcs` PyPI) and a different Ed25519 implementation (node:crypto against
`cryptography`). Agreement between the two is the differential test Profile v5 section 11
requires; agreement of either with itself is not evidence of anything.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata

import base58
import jcs
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# --------------------------------------------------------------- primitives

SEED_A = bytes.fromhex("00" * 31 + "01")   # fixture key, never used outside vectors
SEED_B = bytes.fromhex("00" * 31 + "02")   # rotation case
MULTIHASH_SHA2_256 = bytes([0x12, 0x20])   # multicodec sha2-256, 32-byte digest
MULTIKEY_ED25519 = bytes([0xED, 0x01])     # multicodec ed25519-pub


def mb58(raw: bytes) -> str:
    """multibase base58-btc: 'z' prefix, per Profile v5 section 3.3."""
    return "z" + base58.b58encode(raw).decode()


def digest_ref(canonical: bytes) -> str:
    """Profile v5 3.3: base58-btc multibase over the multihash-prefixed SHA-256 digest."""
    return mb58(MULTIHASH_SHA2_256 + hashlib.sha256(canonical).digest())


def multikey(priv: Ed25519PrivateKey) -> str:
    raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    return mb58(MULTIKEY_ED25519 + raw)


def canon(obj) -> bytes:
    return jcs.canonicalize(obj)


# Genesis constant, per Evidence Record Specification v1 section 6: the multibase
# base58-btc encoding of a thirty-two-byte all-zero value. Note that this is NOT
# multihash-prefixed, so it does not take the section 3.3 digest-reference form. It is a
# reserved token rather than a digest, and exempt under the section 3.3 carve-out.
GENESIS = mb58(bytes(32))


def proof_config(vm: str, created: str) -> dict:
    return {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "proofPurpose": "assertionMethod",
        "created": created,
        "verificationMethod": vm,
    }


def sign(priv: Ed25519PrivateKey, document: dict, cfg: dict) -> str:
    """eddsa-jcs-2022 hashData = SHA256(JCS(proofConfig)) || SHA256(JCS(document))."""
    hash_data = hashlib.sha256(canon(cfg)).digest() + hashlib.sha256(canon(document)).digest()
    return mb58(priv.sign(hash_data))


def sealed(priv: Ed25519PrivateKey, document: dict, created: str) -> dict:
    cfg = proof_config(multikey(priv), created)
    proof = dict(cfg)
    proof["proofValue"] = sign(priv, document, cfg)
    out = dict(document)
    out["proof"] = proof
    return out


def record(seq: int, prev: str, occurred: str, body: dict, rid: str) -> dict:
    return {
        "schemaVersion": "1.0",
        "profileIdentifier": "eddsa-jcs-2022",
        "chainId": "chain-vectors-v5",
        "sequenceNumber": seq,
        "previousDigest": prev,
        "recordType": "Signal",
        "id": rid,
        "occurredAt": occurred,
        "body": body,
    }


# --------------------------------------------------------------- vector set

def build() -> dict:
    key_a = Ed25519PrivateKey.from_private_bytes(SEED_A)
    key_b = Ed25519PrivateKey.from_private_bytes(SEED_B)
    vm_a, vm_b = multikey(key_a), multikey(key_b)
    t0 = "2026-06-30T09:00:00.000Z"
    t1 = "2026-06-30T09:00:01.000Z"
    t2 = "2026-06-30T09:00:02.000Z"

    positives, negatives = [], []

    def pos(vid, purpose, section, doc, priv, created):
        s = sealed(priv, doc, created)
        content = {k: v for k, v in s.items() if k != "proof"}
        positives.append({
            "id": vid, "purpose": purpose, "profileSection": section,
            "record": s,
            "canonicalContent": canon(content).decode(),
            "canonicalProofConfig": canon(
                {k: v for k, v in s["proof"].items() if k != "proofValue"}).decode(),
            "recordDigest": digest_ref(canon(content)),
            "expected": "verify",
        })
        return positives[-1]

    def neg(vid, purpose, section, payload, reason):
        negatives.append({
            "id": vid, "purpose": purpose, "profileSection": section,
            "payload": payload, "expected": "reject", "reason": reason,
        })

    # ---- positives
    g = pos("V-01", "genesis record; previousDigest is the reserved genesis token",
            "4", record(0, GENESIS, t0, {"observation": "control-exercised"}, "rec-000"),
            key_a, t0)
    chained = pos("V-02", "chained record; previousDigest is the predecessor's record digest",
                  "4", record(1, g["recordDigest"], t1, {"observation": "control-exercised"}, "rec-001"),
                  key_a, t1)
    # The chain is built sequentially: each record links to the digest of the one before it.
    # An earlier draft of this generator pointed four records at the same predecessor while
    # incrementing sequenceNumber, which is a broken chain. The differential test caught it.
    prev = chained
    prev = pos("V-03", "ext container is signed and not interpreted", "3.6",
               {**record(2, prev["recordDigest"], t2, {"observation": "x"}, "rec-002"),
                "ext": {"acme": {"vendorField": "opaque"}}}, key_a, t2)
    prev = pos("V-04", "integer above 2^53 carried as a string, never as a JSON number", "3",
               record(3, prev["recordDigest"], t2, {"amount": "100000000000000000000"}, "rec-003"),
               key_a, t2)
    prev = pos("V-05", "key rotation; a record verifies against the key in force when signed", "6",
               record(4, prev["recordDigest"], t2, {"observation": "post-rotation"}, "rec-004"),
               key_b, t2)
    prev = pos("V-06", "empty object and empty array serialise as {} and []", "3.6",
               record(5, prev["recordDigest"], t2, {"emptyObject": {}, "emptyArray": []}, "rec-005"),
               key_a, t2)
    prev = pos("V-07", "valid surrogate pair preserved as its UTF-8 encoding", "3.6",
               record(6, prev["recordDigest"], t2, {"text": "a\U0001F600b"}, "rec-006"),
               key_a, t2)
    tail = prev

    # ---- negatives carried from v4
    tampered = json.loads(json.dumps(g["record"]))
    tampered["body"]["observation"] = "control-not-exercised"
    neg("N-01", "tampered byte after sealing", "8", tampered,
        "the signature no longer covers the content presented")

    broken = json.loads(json.dumps(tail["record"]))
    broken["previousDigest"] = digest_ref(b"not-the-predecessor")
    neg("N-02", "broken chain link", "4", broken,
        "previousDigest does not match the predecessor's recomputed digest")

    neg("N-03", "unsafe integer encoded as a JSON number", "3",
        '{"amount":100000000000000000000,"id":"rec-090"}',
        "a value outside the safe integer range must be a string")
    neg("N-04", "duplicate object member name", "3.6",
        '{"id":"rec-091","id":"rec-092"}',
        "invalid under I-JSON; rejected, never de-duplicated")
    neg("N-05", "lone surrogate", "3.6", '{"text":"\\ud800","id":"rec-093"}',
        "a lone surrogate is invalid and is rejected")
    neg("N-06", "signature computed over a non-canonical serialisation", "3",
        {"note": "proofValue produced over pretty-printed JSON rather than JCS output"},
        "canonicalisation precedes signing; a signature over other bytes does not verify")

    # ---- negatives new at v5, one per decision
    for vid, bad, why in [
        ("N-07", "2026-06-30T09:00:00Z", "no fractional digits"),
        ("N-08", "2026-06-30T09:00:00.000000Z", "six fractional digits"),
        ("N-09", "2026-06-30T09:00:00.000+00:00", "offset form other than Z"),
        ("N-10", "2026-06-30t09:00:00.000z", "lowercase t and z"),
        ("N-11", "2026-06-30T23:59:60.000Z", "leap second"),
    ]:
        neg(vid, f"timestamp in a non-conformant lexical form: {why}", "3.1",
            record(7, tail["recordDigest"], bad, {"observation": "x"}, f"rec-{vid}"),
            "exactly one lexical form is conformant: three fractional digits, uppercase T and Z")

    with_null = record(8, tail["recordDigest"], t2, {"observation": "x"}, "rec-N12")
    with_null["body"]["optionalField"] = None
    neg("N-12", "JSON null present", "3.2", with_null,
        "null is prohibited; an optional member is present with a value or absent")

    hexref = record(9, "sha256:" + hashlib.sha256(b"x").hexdigest(), t2, {"observation": "x"}, "rec-N13")
    neg("N-13", "digest reference in the prohibited hexadecimal form", "3.3", hexref,
        "a digest reference is base58-btc multibase over the multihash-prefixed digest")

    # N-14: a binding whose exclusion set is wider than section 3.4 permits.
    binding = {
        "bindingId": "bnd-001",
        "cryptosuite": "eddsa-jcs-2022",
        "createdAt": t0,
        "parties": ["party-a", "party-b"],
    }
    cfg = proof_config(vm_a, t0)
    narrow_digest = digest_ref(canon({**binding, "proof": {k: v for k, v in cfg.items()}}))
    wide_digest = digest_ref(canon(binding))
    neg("N-14", "binding canonicalised with the whole signature block excluded", "3.4",
        {"binding": binding,
         "conformantDigest_narrowExclusion": narrow_digest,
         "nonConformantDigest_wideExclusion": wide_digest},
        "excluding the whole block removes the signer identity from the signed content; "
        "the two digests differ, which is the observable consequence")

    nfc = unicodedata.normalize("NFC", "café")
    nfd = unicodedata.normalize("NFD", "café")
    neg("N-15", "two strings identical on screen, different Unicode composition", "3.5",
        {"nfc": nfc, "nfd": nfd,
         "digestNFC": digest_ref(canon({"text": nfc})),
         "digestNFD": digest_ref(canon({"text": nfd})),
         "bytesEqual": nfc == nfd},
        "JCS performs no normalisation; the producer fixes the form at record creation, "
        "and no verifier can detect the difference after the event")

    return {
        "name": "Arkaya Layer 1 Cryptographic Profile v5 test vectors",
        "status": "CANDIDATE. Normative on adoption by the profile, not because this tool produced them.",
        "profileVersion": 5,
        "vectorSetVersion": 1,
        "adopted": False,
        "adoptedOn": None,
        "immutabilityRule": "On adoption the set is hash-pinned in the Suite Version Register and is never "
                            "edited. A change produces a new vectorSetVersion; the adopted set is superseded, "
                            "never revised, so an implementation certified against a set stays certifiable "
                            "against the bytes it was tested on. Same rule as requirement identifiers under "
                            "ADR-006 of the Versioning, Compatibility and Change-Control Policy.",
        "verifiedAgainst": [
            {"implementation": "python", "canonicaliser": "jcs (PyPI)", "signature": "cryptography (PyCA)",
             "role": "generator"},
            {"implementation": "javascript", "canonicaliser": "canonicalize (npm)", "signature": "node:crypto Ed25519",
             "role": "independent verifier", "harness": "xverify_v5.mjs"},
        ],
        "cryptosuite": "eddsa-jcs-2022",
        "generatedBy": "generate_vectors_v5.py (deterministic; fixed key seeds, fixture timestamps)",
        "genesisConstant": GENESIS,
        "genesisNote": "Per Evidence Record Specification v1 section 6: multibase base58-btc over "
                       "thirty-two zero bytes. Not multihash-prefixed, and exempt from the "
                       "section 3.3 digest-reference form by that section's own carve-out: the "
                       "constant is the digest of nothing, so a multihash prefix would assert a "
                       "hash function produced it. Resolved in review at Profile v5.",
        "keys": {"fixtureKeyA": vm_a, "fixtureKeyB": vm_b,
                 "warning": "fixture keys, derived from fixed seeds, never for production use"},
        "positive": positives,
        "negative": negatives,
    }


if __name__ == "__main__":
    out = build()
    print(json.dumps(out, indent=1, ensure_ascii=False))
