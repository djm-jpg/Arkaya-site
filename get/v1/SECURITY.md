# For your security review

Written for whoever in your organisation has to approve running code from outside it. Short, because the pack is small enough to check rather than to trust.

---

## The first thing worth saying

**You do not have to run any of it.** The deliverable is the two specifications and the vector file. An engineer can implement from the text and check their output against the vectors without executing a single line we wrote. The code is a convenience for anyone who would rather read a working example than a description of one, and a security team that would prefer to decline it loses nothing.

---

## What is in the pack

Ten files. No binaries, no executables, no installer, no archive, no compiled artefact. Two Markdown specifications, three Markdown notes, two JSON data files, three source files totalling 959 lines.

| File | What it is |
|---|---|
| `specifications/*.md` | Text. The normative documents |
| `vectors/vectors_v5_candidate.json` | Data. The test vectors |
| `vectors/generate_vectors_v5.py` | 269 lines. Produces the vector file |
| `vectors/xverify_v5.mjs` | 117 lines. Recomputes and checks the vectors |
| `corpus/reference_reader.py` | 252 lines. A reference reading implementation |
| `corpus/run_fixtures.py` | 321 lines. Runs the conformance corpus |
| `MANIFEST.json` | Digest of every file above |

## What the code does, and what it does not

Verified by inspection across every source file in the pack:

- **No network access of any kind.** No sockets, no HTTP client, no `fetch`, no `urllib`, no `requests`. The pack cannot phone home because there is nothing in it that can open a connection.
- **No subprocess execution.** No `subprocess`, no `child_process`, no shell invocation.
- **No dynamic evaluation.** No `eval`, no `exec`, no dynamic import.
- **One filesystem operation in the entire pack.** `xverify_v5.mjs` reads the vector file whose path you give it on the command line. Nothing writes to disk. The Python files perform no file I/O at all; they take no input and print to standard output.
- **No environment or credential access.** Nothing reads environment variables, key stores or configuration.

Those claims are checkable in about ten minutes with `grep`, which is the point of keeping the pack this small.

## Third-party dependencies

This is the only real supply-chain surface, and none of these packages is ours. Pin them.

**Python**

```
jcs==0.2.1            RFC 8785 canonicalisation
base58==2.1.1         base58 encoding
cryptography==48.0.0  Ed25519 signatures (PyCA)
```

**JavaScript**, Node 18 or later

```
canonicalize@2.0.0    RFC 8785 canonicalisation
bs58@6.0.0            base58 encoding
```

Ed25519 verification on the JavaScript side uses `node:crypto` from the standard library, so it adds no dependency.

Substitute any of these for an equivalent you already trust. The specification names algorithms and standards, never packages, and any conformant RFC 8785 and Ed25519 implementation will produce the same bytes. That is what the vectors are for.

## Integrity of the pack itself

`MANIFEST.json` carries a digest of every file, in the same form the Cryptographic Profile requires at Section 3.3. Verify the pack against it before you rely on anything in it.

The digests are also stated in the covering message, sent separately. If the two disagree, the pack has been altered in transit and you should tell us rather than run it.

## On antivirus scanning

We will run one if your process requires it, and it will find nothing, because signature-based scanning detects known malicious binaries and this pack contains no binaries. A clean scan of nine text files is not evidence about their behaviour. The checks above are, and so is reading the code, which is why it is short.

---

Questions to djm@arkayarisk.com.

Arkaya Risk Limited, a company registered in England and Wales (no. 17380022). Registered office: Oxford House, 15-17 Mount Ephraim Road, Tunbridge Wells, England, TN1 1EN.
