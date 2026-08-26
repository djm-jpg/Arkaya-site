#!/usr/bin/env python3
"""Reference reading implementation for the Interface and Conformance Specification v4.

Minimal by intent. It exists so the fixture corpus has something to run against and so
each fixture can be shown to discriminate: a fixture that no mutation of this reader can
fail is a fixture that tests nothing, which is the same defect as an unverified vector.

Every deviation is expressed as a named mutation rather than a forked copy, so the
reference and the broken variants cannot drift apart.

Determinism, per R-33: no wall-clock read. The evaluation date is an input.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import base58
import jcs

# ---- closed enumerations, per the specification -------------------------------------

ADMISSIBILITY = ("admissible", "unattributed", "unverifiable", "out-of-scope")   # R-17
COVERAGE = ("NO_CONTROL", "OPERATION_GAP", "EFFICACY_FAIL", "COVERED")           # R-20, R-24
READ_STATUS = ("available", "not connected", "unauthorised", "unavailable", "stale",
               "incomplete history", "schema error", "integrity error", "unjoinable")  # R-25
TRIAGE = ("EVIDENCED", "ATTESTED", "BELOW_BENCHMARK")                            # R-28
MODES = ("config", "event", "join", "assessed")
POSITIONS = ("outside", "inside", "varies")

MUTATIONS = {
    "R-9-drop-anchor-check", "R-10-drop-unanchored-flag", "R-11-accept-partial-scope",
    "R-16-require-emitter-code", "R-17-fifth-admissibility-outcome",
    "R-18-inadmissible-contributes", "R-19-unattributed-as-no-control",
    "R-20-fifth-coverage-state", "R-21-config-only-covered", "R-22-fold-position",
    "R-24-unattributed-in-coverage-set", "R-25-eight-read-statuses",
    "R-26-stale-enters-fold", "R-27-drop-refused", "R-28-fourth-triage-outcome",
    "R-33-read-wall-clock", "R-34-omit-determination-member",
    "R-36-overwrite-determination", "R-40-natural-person-signer",
    "R-12-determine-without-scope", "R-35-nondeterministic-replay",
}


def mb58(raw: bytes) -> str:
    return "z" + base58.b58encode(raw).decode()


def digest_ref(obj) -> str:
    return mb58(bytes([0x12, 0x20]) + hashlib.sha256(jcs.canonicalize(obj)).digest())


@dataclass
class Reader:
    """A conformant reading implementation, or a deviation from one.

    Two kinds of deviation. A NAMED mutation is a hand-written breach of a stated
    requirement. A GENERATED mutation is a systematic perturbation produced without
    reference to any requirement: substitute each fold outcome, drop each member of each
    closed enumeration. The generated set exists because a curated set measures only the
    breaches its author thought of, and a discrimination figure computed against a
    curated set flatters the corpus in exactly the way a hand sweep flatters an estate.
    """
    mutation: str | None = None
    gen: tuple | None = None            # ("fold-substitute", branch, state) | ("enum-drop", name, index)
    determinations: list = field(default_factory=list)

    def m(self, name: str) -> bool:
        return self.mutation == name

    def _gen_enum(self, name: str, values: tuple) -> list:
        if self.gen and self.gen[0] == "enum-drop" and self.gen[1] == name:
            v = list(values)
            del v[self.gen[2] % len(v)]
            return v
        return list(values)

    def _gen_fold(self, branch: int, state: str) -> str:
        if self.gen and self.gen[0] == "fold-substitute" and self.gen[1] == branch:
            return self.gen[2]
        return state

    # -- R-17 to R-19: the admissibility gate ----------------------------------------

    def admissibility(self, rec: dict) -> str:
        if self.m("R-17-fifth-admissibility-outcome") and not rec.get("signatureValid", True):
            return "malformed"
        if not rec.get("inScope", True):
            return "out-of-scope"
        if not rec.get("signatureValid", True):
            return "unverifiable"
        if not rec.get("signerAttributable", True):
            return "no-control" if self.m("R-19-unattributed-as-no-control") else "unattributed"
        return "admissible"

    # -- R-9 to R-11: emitter-side obligations the reader checks ----------------------

    def anchored_time_ok(self, rec: dict) -> bool:
        if self.m("R-9-drop-anchor-check"):
            return True
        return bool(rec.get("timestampToken")) or bool(rec.get("unanchored"))

    def unanchored_flagged(self, rec: dict) -> bool:
        if self.m("R-10-drop-unanchored-flag"):
            return True
        if rec.get("timestampToken"):
            return True
        return rec.get("unanchored") is True

    SCOPE_MEMBERS = ("systemsCovered", "controlIdentifiersInScope", "interval", "notLookedAt")

    def scope_ok(self, scope) -> bool:
        if not isinstance(scope, dict):
            return False
        needed = self.SCOPE_MEMBERS[:-1] if self.m("R-11-accept-partial-scope") else self.SCOPE_MEMBERS
        return all(k in scope for k in needed)

    # -- R-40: signer identity --------------------------------------------------------

    def signer_ok(self, rec: dict) -> bool:
        signer = rec.get("signer", {})
        if self.m("R-40-natural-person-signer"):
            return "role" in signer or "name" in signer
        return "role" in signer and "name" not in signer

    # -- R-25 to R-27: read statuses and the refusal path -----------------------------

    def statuses(self) -> tuple:
        if self.m("R-25-eight-read-statuses"):
            return READ_STATUS[:-1]
        return tuple(self._gen_enum("readStatuses", READ_STATUS))

    def enters_fold(self, obs: dict) -> bool:
        if self.m("R-26-stale-enters-fold") and obs.get("readStatus") == "stale":
            return True
        return obs.get("readStatus") == "available"

    # -- R-20 to R-22: the coverage fold ----------------------------------------------

    def fold(self, obs: dict) -> str:
        if self.m("R-20-fifth-coverage-state") and obs.get("probeRun") is False and obs.get("mode") == "event":
            return "INDETERMINATE"
        if self.m("R-22-fold-position") and obs.get("position") == "inside":
            return "NO_CONTROL"
        if not obs.get("configPresent") or obs.get("controlUnconfigured"):
            return self._gen_fold(0, "NO_CONTROL")
        if obs.get("efficacyFailure"):
            return self._gen_fold(1, "EFFICACY_FAIL")
        if obs.get("mode") == "config":
            # R-21: a configuration-only obligation cannot reach COVERED on its own evidence.
            return "COVERED" if self.m("R-21-config-only-covered") else self._gen_fold(2, "OPERATION_GAP")
        if obs.get("exercisedInWindow") and not obs.get("efficacyFailure"):
            return self._gen_fold(3, "COVERED")
        return self._gen_fold(4, "OPERATION_GAP")

    # -- R-28: triage ------------------------------------------------------------------

    def triage(self, coverage: dict, attested_only: bool) -> str:
        if self.m("R-28-fourth-triage-outcome") and not coverage:
            return "NO_EVIDENCE"
        if any(v in ("NO_CONTROL", "EFFICACY_FAIL") for v in coverage.values()):
            return "BELOW_BENCHMARK"
        return "ATTESTED" if attested_only else "EVIDENCED"

    # -- R-33 to R-36: determination and replay ---------------------------------------

    DETERMINATION_MEMBERS = ("inputDigests", "benchmarkDigest", "engineVersion", "schemaVersion",
                             "perObservable", "coverage", "reasons", "unresolved", "triage", "signature")

    def determine(self, run: dict) -> dict:
        if self.m("R-16-require-emitter-code"):
            for r in run.get("records", []):
                if r.get("emitter") not in ("known-emitter",):
                    raise RuntimeError("unknown emitter: adapter code required")

        refused, coverage, per_obs, reasons = [], {}, {}, []
        admitted = []

        for rec in run.get("records", []):
            verdict = self.admissibility(rec)
            if verdict != "admissible":
                refused.append({"recordId": rec.get("id"), "admissibility": verdict})
                # R-18: an inadmissible record does not contribute to a determination. The
                # observable consequence is that its digest is absent from inputDigests.
                if self.m("R-18-inadmissible-contributes"):
                    admitted.append(rec)
                continue
            admitted.append(rec)

        for obs in run.get("observables", []):
            if not self.enters_fold(obs):
                refused.append({"observable": obs["id"], "readStatus": obs.get("readStatus"),
                                "reason": "not available; routed to the refusal path"})
                continue
            state = self.fold(obs)
            coverage[obs["id"]] = state
            per_obs[obs["id"]] = {"state": state, "mode": obs.get("mode"),
                                  "position": obs.get("position"),          # R-22: recorded, not folded
                                  "evidenceBasis": obs.get("evidenceBasis")}

        if not self.scope_ok(run.get("scopeDeclaration")) and not self.m("R-12-determine-without-scope"):
            reasons.append("scope declaration absent or incomplete; REVIEW, no determination")
            out = {"result": "REVIEW", "reasons": reasons,
                   "refused": [] if self.m("R-27-drop-refused") else refused}
            return out

        evaluation_date = run["evaluationDate"]
        if self.m("R-33-read-wall-clock"):
            import datetime
            evaluation_date = datetime.datetime.now(datetime.UTC).isoformat()

        det = {
            "inputDigests": [digest_ref(r) for r in admitted],
            "benchmarkDigest": digest_ref(run.get("benchmark", {})),
            "engineVersion": run.get("engineVersion", "reference-1"),
            "schemaVersion": run.get("schemaVersion", "1.0"),
            "evaluationDate": evaluation_date,
            "perObservable": per_obs,
            "coverage": coverage,
            "reasons": reasons,
            "unresolved": [] if self.m("R-27-drop-refused") else refused,   # R-27
            "triage": self.triage(coverage, run.get("attestedOnly", False)),
            "signature": "z-fixture-signature",
        }
        if self.m("R-34-omit-determination-member"):
            det.pop("benchmarkDigest")
        if self.m("R-35-nondeterministic-replay"):
            det["runOrdinal"] = len(self.determinations) + 1

        # R-36: determinations are append-only.
        if self.m("R-36-overwrite-determination") and self.determinations:
            self.determinations[-1] = det
        else:
            self.determinations.append(det)
        return det

    # -- R-16, R-24: declared surfaces the harness reads ------------------------------

    def declared(self) -> dict:
        return {
            "admissibilityOutcomes": self._gen_enum("admissibilityOutcomes", ADMISSIBILITY) + (
                ["malformed"] if self.m("R-17-fifth-admissibility-outcome") else []),
            "coverageStates": self._gen_enum("coverageStates", COVERAGE) + (
                ["INDETERMINATE"] if self.m("R-20-fifth-coverage-state") else []) + (
                ["unattributed"] if self.m("R-24-unattributed-in-coverage-set") else []),
            "readStatuses": list(self.statuses()),
            "triageOutcomes": self._gen_enum("triageOutcomes", TRIAGE) + (
                ["NO_EVIDENCE"] if self.m("R-28-fourth-triage-outcome") else []),
            "joinContract": "directory-of-sealed-record-files" if not self.m("R-16-require-emitter-code")
                            else "per-emitter-adapter-required",
        }
