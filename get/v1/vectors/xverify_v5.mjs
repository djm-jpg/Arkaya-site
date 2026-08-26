// Independent JavaScript re-computation of the Arkaya Layer 1 Cryptographic Profile v5
// candidate vectors. Shares no code with the Python generator: a different canonicaliser
// (canonicalize npm vs jcs PyPI) and a different Ed25519 implementation (node:crypto vs
// python cryptography). Agreement between the two is the differential test; agreement of
// either with itself proves nothing.
import { readFileSync } from 'node:fs';
import { createHash, createPublicKey, verify as edVerify } from 'node:crypto';
import canonicalize from 'canonicalize';
import bs58 from 'bs58';

const MULTIHASH = Uint8Array.from([0x12, 0x20]);
const MULTIKEY  = Uint8Array.from([0xed, 0x01]);
const SPKI_ED25519 = Buffer.from('302a300506032b6570032100', 'hex');

const mb58 = (b) => 'z' + bs58.encode(b);
const unmb58 = (s) => { if (s[0] !== 'z') throw new Error('not multibase base58-btc: ' + s); return bs58.decode(s.slice(1)); };
const canon = (o) => Buffer.from(canonicalize(o), 'utf8');
const sha256 = (b) => createHash('sha256').update(b).digest();
const digestRef = (canonBytes) => mb58(Buffer.concat([Buffer.from(MULTIHASH), sha256(canonBytes)]));

function pubKeyFromMultikey(mk) {
  const raw = Buffer.from(unmb58(mk));
  if (raw[0] !== MULTIKEY[0] || raw[1] !== MULTIKEY[1]) throw new Error('not an ed25519 multikey');
  return createPublicKey({ key: Buffer.concat([SPKI_ED25519, raw.subarray(2)]), format: 'der', type: 'spki' });
}

const vectors = JSON.parse(readFileSync(process.argv[2], 'utf8'));
let pass = 0, fail = 0;
const report = (ok, id, what, detail) => {
  if (ok) { pass++; } else { fail++; console.log(`  FAIL ${id} ${what}${detail ? ': ' + detail : ''}`); }
};

console.log(`Differential check, JavaScript side. Profile v${vectors.profileVersion}, suite ${vectors.cryptosuite}.`);
console.log(`canonicaliser: canonicalize (npm)   signature: node:crypto Ed25519\n`);

// genesis constant
report(vectors.genesisConstant === mb58(Buffer.alloc(32)), 'genesis', 'constant recomputes',
       `${vectors.genesisConstant} vs ${mb58(Buffer.alloc(32))}`);

for (const v of vectors.positive) {
  const { proof, ...content } = v.record;
  const c = canon(content);
  report(c.toString() === v.canonicalContent, v.id, 'canonical content matches');
  const { proofValue, ...cfg } = proof;
  report(canon(cfg).toString() === v.canonicalProofConfig, v.id, 'canonical proof config matches');
  report(digestRef(c) === v.recordDigest, v.id, 'record digest matches',
         `${digestRef(c)} vs ${v.recordDigest}`);
  const hashData = Buffer.concat([sha256(canon(cfg)), sha256(c)]);
  let ok = false;
  try { ok = edVerify(null, hashData, pubKeyFromMultikey(proof.verificationMethod), Buffer.from(unmb58(proofValue))); } catch (e) { ok = false; }
  report(ok, v.id, 'Ed25519 signature verifies');
}

// chain linkage
for (let i = 1; i < vectors.positive.length; i++) {
  const prev = vectors.positive[i - 1], cur = vectors.positive[i];
  if (cur.record.sequenceNumber === prev.record.sequenceNumber + 1) {
    report(cur.record.previousDigest === prev.recordDigest, cur.id, 'chain link to predecessor');
  }
}

// negatives that are structurally checkable from the JS side
const byId = Object.fromEntries(vectors.negative.map(n => [n.id, n]));

// N-01 tamper: signature must NOT verify
{
  const n = byId['N-01']; const { proof, ...content } = n.payload;
  const { proofValue, ...cfg } = proof;
  const hashData = Buffer.concat([sha256(canon(cfg)), sha256(canon(content))]);
  let ok = true;
  try { ok = edVerify(null, hashData, pubKeyFromMultikey(proof.verificationMethod), Buffer.from(unmb58(proofValue))); } catch { ok = false; }
  report(ok === false, 'N-01', 'tampered record is rejected');
}
// N-02 broken chain link
{
  const n = byId['N-02'];
  report(n.payload.previousDigest !== vectors.positive[0].recordDigest, 'N-02', 'broken link is detectable');
}
// N-07..N-11 timestamp forms
// Shape alone does not exclude a leap second: :60 satisfies \d{2}. A conformant validator
// must constrain the seconds field to 00-59, which is why the profile states the range and
// not only the shape.
const TS = /^\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):[0-5]\d:[0-5]\d\.\d{3}Z$/;
for (const id of ['N-07','N-08','N-09','N-10','N-11']) {
  const n = byId[id];
  report(!TS.test(n.payload.occurredAt), id, `non-conformant timestamp rejected (${n.payload.occurredAt})`);
}
// N-12 null present
{
  const n = byId['N-12'];
  const hasNull = JSON.stringify(n.payload).includes(':null');
  report(hasNull, 'N-12', 'null is present and therefore non-conformant');
}
// N-13 hex digest reference
{
  const n = byId['N-13'];
  report(!n.payload.previousDigest.startsWith('z'), 'N-13', 'hexadecimal digest reference rejected');
}
// N-14 exclusion set: the two digests must differ, recomputed independently
{
  const n = byId['N-14'];
  const b = n.payload.binding;
  const wide = digestRef(canon(b));
  report(wide === n.payload.nonConformantDigest_wideExclusion, 'N-14', 'wide-exclusion digest recomputes');
  report(n.payload.conformantDigest_narrowExclusion !== n.payload.nonConformantDigest_wideExclusion,
         'N-14', 'narrow and wide exclusion produce different digests');
}
// N-15 Unicode composition
{
  const n = byId['N-15'];
  report(digestRef(canon({ text: n.payload.nfc })) === n.payload.digestNFC, 'N-15', 'NFC digest recomputes');
  report(digestRef(canon({ text: n.payload.nfd })) === n.payload.digestNFD, 'N-15', 'NFD digest recomputes');
  report(n.payload.digestNFC !== n.payload.digestNFD, 'N-15', 'composition difference changes the digest');
}

console.log(`\n${fail === 0 ? 'DIFFERENTIAL TEST PASSED' : 'DIFFERENTIAL TEST FAILED'}  checks ${pass + fail}, pass ${pass}, fail ${fail}`);
process.exit(fail === 0 ? 0 : 1);
