"""Check a sealed record with stock open-source libraries only: jcs (RFC 8785), base58, cryptography (PyCA).
Nothing from Arkaya is in the path. The procedure is the four steps in VERIFY.md and section 8 of Cryptographic Profile v5.
Usage: python3 check_record.py record.json [expectedRecordDigest]"""
import json, hashlib, sys
import jcs, base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def multihash_b58(b: bytes) -> str:
    return "z" + base58.b58encode(b"\x12\x20" + hashlib.sha256(b).digest()).decode()

def multikey_to_ed25519(mk: str) -> bytes:
    raw = base58.b58decode(mk[1:])           # strip multibase 'z'
    assert raw[:2] == b"\xed\x01", "not an Ed25519 multikey"
    return raw[2:]

record = json.load(open(sys.argv[1]))
expected_digest = sys.argv[2] if len(sys.argv) > 2 else None

# 1. content digest
content = {k: v for k, v in record.items() if k != "proof"}
canon_content = jcs.canonicalize(content)
h_content = hashlib.sha256(canon_content).digest()
record_digest = multihash_b58(canon_content)
print("canonical content :", canon_content.decode())
print("record digest     :", record_digest)
if expected_digest:
    print("matches published :", record_digest == expected_digest)

# 3. proof config digest, signing input
proof = dict(record["proof"]); proof_value = proof.pop("proofValue")
canon_proof = jcs.canonicalize(proof)
h_proof = hashlib.sha256(canon_proof).digest()
signing_input = h_proof + h_content

# 4. Ed25519 signature check against the key carried in the record
pub = Ed25519PublicKey.from_public_bytes(multikey_to_ed25519(record["proof"]["verificationMethod"]))
sig = base58.b58decode(proof_value[1:])
try:
    pub.verify(sig, signing_input)
    print("signature         : CHECKS (Ed25519 over SHA-256(proofConfig) || SHA-256(content))")
except Exception as e:
    print("signature         : FAILS", e); sys.exit(1)
