#!/usr/bin/env python3
"""Fixture corpus and runner for the fixture-ready requirements of the
Interface and Conformance Specification v4.

Two things run here, and the second matters more than the first.

1. Conformance. Every fixture is executed against the reference reading implementation,
   which is expected to pass all of them.

2. Discrimination, by mutation. For every requirement, a named deviation from the
   reference is executed against that requirement's fixtures, and the fixtures are
   expected to FAIL. A fixture no mutation can fail tests nothing, and would sit in the
   corpus reporting a pass forever. This is the fixture-level counterpart of the
   differential test: passing is not evidence unless failing was possible.

Determinism: every timestamp is fixture data and nothing reads a clock.
"""

from __future__ import annotations

import json
import sys
import traceback

from reference_reader import Reader, digest_ref, ADMISSIBILITY, COVERAGE, READ_STATUS, TRIAGE

T = "2026-06-30T09:00:00.000Z"


def base_run(**over) -> dict:
    run = {
        "evaluationDate": T,
        "engineVersion": "reference-1",
        "schemaVersion": "1.0",
        "benchmark": {"benchmarkVersion": "b-1"},
        "scopeDeclaration": {
            "systemsCovered": ["identity_provider", "ai_gateway"],
            "controlIdentifiersInScope": ["OB-1", "OB-2"],
            "interval": {"from": T, "to": T},
            "notLookedAt": ["cloud_control_plane"],
        },
        "records": [rec("rec-1")],
        "observables": [obs("OB-1", mode="event", exercised=True)],
        "attestedOnly": False,
    }
    run.update(over)
    return run


def rec(rid, *, valid=True, attributable=True, in_scope=True, token=True,
        unanchored=False, signer=None, emitter="known-emitter") -> dict:
    r = {"id": rid, "signatureValid": valid, "signerAttributable": attributable,
         "inScope": in_scope, "emitter": emitter,
         "signer": signer if signer is not None else {"role": "accountable-manager"}}
    if token:
        r["timestampToken"] = "z-rfc3161-token"
    if unanchored:
        r["unanchored"] = True
    return r


def obs(oid, *, mode="event", status="available", config=True, unconfigured=False,
        exercised=False, efficacy=False, position="outside", probe=None, basis="appendix_b") -> dict:
    return {"id": oid, "mode": mode, "readStatus": status, "configPresent": config,
            "controlUnconfigured": unconfigured, "exercisedInWindow": exercised,
            "efficacyFailure": efficacy, "position": position, "probeRun": probe,
            "evidenceBasis": basis}


# ------------------------------------------------------------------ the corpus
# Each entry: requirement, purpose, and a check taking a Reader and returning True on
# conformant behaviour. The mutation named against the requirement must make it False.

def corpus():
    C = []

    seen = {}

    def case(req, mutation, purpose, fn):
        n = seen.get(req, 0) + 1
        seen[req] = n
        C.append({"id": f"F-{req.replace('R-', '')}-{n:02d}", "requirement": req,
                  "mutation": mutation,
                  "mutationId": f"M-{req.replace('R-', '')}-01" if mutation else None,
                  "purpose": purpose, "check": fn})

    # --- emitter obligations the reader enforces
    case("R-9", "R-9-drop-anchor-check",
         "a record with neither an external time-stamp token nor an unanchored flag is not accepted",
         lambda r: r.anchored_time_ok(rec("x", token=False)) is False)
    case("R-10", "R-10-drop-unanchored-flag",
         "a record without an external token carries the unanchored flag explicitly",
         lambda r: r.unanchored_flagged(rec("x", token=False)) is False
                   and r.unanchored_flagged(rec("x", token=False, unanchored=True)) is True)
    case("R-11", "R-11-accept-partial-scope",
         "a scope declaration missing what was not looked at is incomplete",
         lambda r: r.scope_ok({"systemsCovered": [], "controlIdentifiersInScope": [],
                               "interval": {}}) is False)
    case("R-11", "R-11-accept-partial-scope",
         "a complete scope declaration is accepted",
         lambda r: r.scope_ok(base_run()["scopeDeclaration"]) is True)
    case("R-12", "R-12-determine-without-scope",
         "a record set with no scope declaration returns REVIEW and no determination",
         lambda r: r.determine(base_run(scopeDeclaration=None)).get("result") == "REVIEW")
    case("R-16", "R-16-require-emitter-code",
         "a directory from an unknown emitter is read without adapter code",
         lambda r: r.determine(base_run(records=[rec("rec-1", emitter="stranger")])).get("triage") in TRIAGE)
    case("R-16", "R-16-require-emitter-code",
         "the declared join contract is a directory of sealed record files",
         lambda r: r.declared()["joinContract"] == "directory-of-sealed-record-files")

    # --- the admissibility gate
    case("R-17", "R-17-fifth-admissibility-outcome",
         "the gate returns exactly one of four outcomes and no fifth is representable",
         lambda r: set(r.declared()["admissibilityOutcomes"]) == set(ADMISSIBILITY))
    case("R-17", "R-17-fifth-admissibility-outcome",
         "each of the four outcomes is reachable from a constructed record",
         lambda r: [r.admissibility(x) for x in (
             rec("a"), rec("b", attributable=False), rec("c", valid=False), rec("d", in_scope=False))]
             == ["admissible", "unattributed", "unverifiable", "out-of-scope"])
    case("R-18", "R-18-inadmissible-contributes",
         "an inadmissible record's digest is absent from the determination's input digests",
         lambda r: len(r.determine(base_run(records=[rec("ok"), rec("bad", valid=False)]))["inputDigests"]) == 1)
    case("R-18", "R-18-inadmissible-contributes",
         "the inadmissible record still appears in the refusal path, with its outcome named",
         lambda r: any(x.get("recordId") == "bad" and x.get("admissibility") == "unverifiable"
                       for x in r.determine(base_run(records=[rec("ok"), rec("bad", valid=False)]))["unresolved"]))
    case("R-19", "R-19-unattributed-as-no-control",
         "an unresolvable signer returns unattributed, never a statement about the control",
         lambda r: r.admissibility(rec("x", attributable=False)) == "unattributed")

    # --- the coverage fold
    case("R-20", "R-20-fifth-coverage-state",
         "the coverage set is closed at four states under their own names",
         lambda r: set(r.declared()["coverageStates"]) == set(COVERAGE))
    case("R-20", "R-20-fifth-coverage-state",
         "an event observable with no exercise and no probe folds to OPERATION_GAP",
         lambda r: r.fold(obs("o", mode="event", exercised=False, probe=False)) == "OPERATION_GAP")
    case("R-20", "R-20-fifth-coverage-state",
         "an absent configuration source folds to NO_CONTROL",
         lambda r: r.fold(obs("o", mode="event", config=False)) == "NO_CONTROL")
    case("R-20", "R-20-fifth-coverage-state",
         "a configured control shown unconfigured folds to NO_CONTROL",
         lambda r: r.fold(obs("o", mode="event", config=True, unconfigured=True)) == "NO_CONTROL")
    case("R-20", "R-20-fifth-coverage-state",
         "a control reached that did not hold folds to EFFICACY_FAIL",
         lambda r: r.fold(obs("o", mode="event", exercised=True, efficacy=True)) == "EFFICACY_FAIL")
    case("R-28", "R-28-fourth-triage-outcome",
         "an efficacy failure carries the determination to BELOW_BENCHMARK",
         lambda r: r.determine(base_run(observables=[obs("OB-1", mode="event", exercised=True,
                                                         efficacy=True)]))["triage"] == "BELOW_BENCHMARK")
    case("R-21", "R-21-config-only-covered",
         "a configuration-only obligation cannot reach COVERED on its own evidence",
         lambda r: r.fold(obs("o", mode="config", exercised=True)) == "OPERATION_GAP")
    case("R-22", "R-22-fold-position",
         "emitter position is recorded beside the state and does not change it",
         lambda r: r.fold(obs("o", mode="event", exercised=True, position="inside"))
                   == r.fold(obs("o", mode="event", exercised=True, position="outside")) == "COVERED")
    case("R-22", "R-22-fold-position",
         "the determination carries the position it did not fold",
         lambda r: r.determine(base_run(observables=[obs("OB-1", mode="event", exercised=True,
                                                         position="inside")]))["perObservable"]["OB-1"]["position"] == "inside")
    case("R-24", "R-24-unattributed-in-coverage-set",
         "the unattributed result is absent from the coverage-state set",
         lambda r: "unattributed" not in r.declared()["coverageStates"])

    # --- refusal
    case("R-25", "R-25-eight-read-statuses",
         "nine read statuses are carried upstream of the fold",
         lambda r: list(r.declared()["readStatuses"]) == list(READ_STATUS))
    case("R-26", "R-26-stale-enters-fold",
         "evidence that is not available does not enter the fold",
         lambda r: "OB-1" not in r.determine(base_run(
             observables=[obs("OB-1", status="stale", exercised=True)]))["coverage"])
    case("R-27", "R-27-drop-refused",
         "refused evidence is reported alongside the determination it was excluded from",
         lambda r: any(x.get("observable") == "OB-1" for x in r.determine(base_run(
             observables=[obs("OB-1", status="unauthorised")]))["unresolved"]))
    case("R-28", "R-28-fourth-triage-outcome",
         "the triage enumeration is closed at three values",
         lambda r: set(r.declared()["triageOutcomes"]) == set(TRIAGE))
    case("R-28", "R-28-fourth-triage-outcome",
         "an empty coverage set still returns one of the three values",
         lambda r: r.determine(base_run(observables=[]))["triage"] in TRIAGE)

    # --- determination and replay
    case("R-33", "R-33-read-wall-clock",
         "the evaluation date is an input and no wall-clock read occurs",
         lambda r: r.determine(base_run())["evaluationDate"] == T)
    case("R-33", "R-33-read-wall-clock",
         "two runs of the same implementation over identical inputs are identical",
         lambda r: json.dumps(r.determine(base_run()), sort_keys=True)
                   == json.dumps(r.determine(base_run()), sort_keys=True))
    case("R-34", "R-34-omit-determination-member",
         "the determination carries every declared member",
         lambda r: all(k in r.determine(base_run()) for k in Reader.DETERMINATION_MEMBERS))
    case("R-35", "R-35-nondeterministic-replay",
         "replay of the same sealed set and benchmark reproduces the identical determination digest, "
         "however many runs have preceded it",
         lambda r: (lambda d: d(r.determine(base_run())) == d(r.determine(base_run())))(
             lambda x: digest_ref({k: v for k, v in x.items() if k != "signature"})))
    case("R-36", "R-36-overwrite-determination",
         "a later determination is appended and does not overwrite its predecessor",
         lambda r: (lambda before: (r.determine(base_run()),
                                    r.determine(base_run(engineVersion="reference-2")),
                                    len(r.determinations) == before + 2)[-1])(len(r.determinations)))

    # --- signer identity
    case("R-40", "R-40-natural-person-signer",
         "a signer recorded by natural-person name is refused",
         lambda r: r.signer_ok(rec("x", signer={"name": "A Person"})) is False)
    case("R-40", "R-40-natural-person-signer",
         "a signer recorded by role is accepted",
         lambda r: r.signer_ok(rec("x", signer={"role": "accountable-manager"})) is True)

    return C


# ------------------------------------------------------------------ the runner

def evaluate(case, mutation=None, gen=None) -> bool:
    """Each fixture runs against a FRESH reader.

    An earlier version shared one reader across the corpus. F-36-01 counts appended
    determinations, so by the time it ran the count was already wrong and it failed under
    every mutation, including identity substitutions that change no behaviour at all. The
    result was a 100 per cent discrimination figure produced by one badly scoped fixture
    rather than by the corpus. Isolation is not hygiene here; without it the metric lies.
    """
    try:
        return bool(case["check"](Reader(mutation, gen)))
    except Exception:
        return False


def generated_mutations():
    """Systematic perturbations, produced without reference to any requirement.

    Two families. Substitute each outcome of the coverage fold with each other state, and
    drop each member of each closed enumeration. Neither family knows what the corpus
    tests, which is the point: a discrimination figure computed only against hand-written
    breaches measures the author's imagination rather than the corpus.
    """
    identity = {0: "NO_CONTROL", 1: "EFFICACY_FAIL", 2: "OPERATION_GAP", 3: "COVERED", 4: "OPERATION_GAP"}
    out = []
    for branch in range(5):
        for state in COVERAGE:
            if identity[branch] == state:
                continue          # substituting a branch for itself changes no behaviour
            out.append((f"G-fold-{branch}-{state}", ("fold-substitute", branch, state)))
    for name, values in (("admissibilityOutcomes", ADMISSIBILITY), ("coverageStates", COVERAGE),
                         ("readStatuses", READ_STATUS), ("triageOutcomes", TRIAGE)):
        for i in range(len(values)):
            out.append((f"G-drop-{name}-{i}", ("enum-drop", name, i)))
    return out


def main() -> int:
    C = corpus()
    reqs = sorted({c["requirement"] for c in C}, key=lambda r: int(r.split("-")[1]))
    print(f"Conformance corpus: {len(C)} fixtures across {len(reqs)} requirements\n")

    print("Pass 1, conformance. The reference implementation runs every fixture.")
    conf_fail = [c for c in C if not evaluate(c)]
    for c in conf_fail:
        print(f"  FAIL {c['id']} {c['requirement']}: {c['purpose']}")
    print(f"  {len(C) - len(conf_fail)}/{len(C)} pass\n")

    print("Pass 2, named mutations. Each requirement's stated breach must fail its own fixtures.")
    rows, escaped_named = [], []
    for req in reqs:
        cases = [c for c in C if c["requirement"] == req]
        mut = next((c["mutation"] for c in cases if c["mutation"]), None)
        mid = next((c["mutationId"] for c in cases if c["mutationId"]), None)
        if not mut:
            rows.append((req, mid or "-", "none defined", "NOT MEASURED"))
            escaped_named.append((req, "no mutation defined"))
            continue
        killed = [c for c in cases if not evaluate(c, mutation=mut)]
        if killed:
            rows.append((req, mid, f"killed by {len(killed)}/{len(cases)}", "killed"))
        else:
            rows.append((req, mid, "survives", "ESCAPED"))
            escaped_named.append((req, mut))
    w = max(len(r[1]) for r in rows)
    for req, mid, res, verdict in rows:
        print(f"  {req:<6} {mid:<{w}}  {res:<22} {verdict}")
    named_killed = sum(1 for r in rows if r[3] == "killed")
    print(f"\n  named mutations {len(rows)}, killed {named_killed}, escaped {len(rows) - named_killed}\n")

    print("Pass 3, generated mutations. Systematic perturbations the corpus never saw.")
    gen = generated_mutations()
    survivors = []
    for gid, spec in gen:
        if all(evaluate(c, gen=spec) for c in C):
            survivors.append((gid, spec))
    print("  identity substitutions are excluded: replacing a branch with its own outcome")
    print("  changes no behaviour, so surviving proves nothing about the corpus.")
    print(f"  generated {len(gen)}, killed {len(gen) - len(survivors)}, "
          f"escaped {len(survivors)}  ({100 * (len(gen) - len(survivors)) / len(gen):.0f}% discrimination)")
    for gid, spec in survivors[:12]:
        print(f"    ESCAPED {gid}  {spec}")
    if len(survivors) > 12:
        print(f"    ... and {len(survivors) - 12} more")

    print()
    print("An escaped generated mutation is not necessarily a defect in the corpus. It may")
    print("mean the specification does not distinguish the two behaviours, in which case the")
    print("finding belongs to the specification and not to the tests. Each one is read, not")
    print("counted.")
    print()
    ok = not conf_fail and not escaped_named
    print(f"{'CORPUS PASSED' if ok else 'CORPUS FAILED'}  requirements {len(reqs)}, fixtures {len(C)}, "
          f"named mutations killed {named_killed}/{len(rows)}, "
          f"generated mutations killed {len(gen) - len(survivors)}/{len(gen)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
