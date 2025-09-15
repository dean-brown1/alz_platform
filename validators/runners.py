from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from time import perf_counter
from typing import List
from core.schemas.case_bundle import CaseBundle
from validators.base import BaseValidator, ValidationResult
from core.provenance.audit import audit, audit_append_ndjson
from validators.policy import load_policy
from validators.registry import load_all_validators
from core.schemas.validation_result import (
    ValidatorOutcome,
    ValidationReport,
    Reason,
    SourceRef,
    Decision,
)

# -------------------------------------------------------------------
# Existing async runner (unchanged)
# -------------------------------------------------------------------

async def _run_one(v: BaseValidator, case) -> list[ValidationResult]:
    audit("validator", "start", subject=v.code)
    results = await asyncio.to_thread(v.run, case)
    audit("validator", "done", subject=v.code, found=len(results))
    return results


async def run_all(validators: list[BaseValidator], case) -> list[ValidationResult]:
    policy = load_policy()
    if policy.order:
        order_index = {code: i for i, code in enumerate(policy.order)}
        validators = sorted(validators, key=lambda v: order_index.get(v.code, 9999))

    sem = asyncio.Semaphore(policy.concurrency or 4)

    async def _guarded(v):
        async with sem:
            res = await _run_one(v, case)
            if policy.severity_overrides:
                for r in res:
                    if r.code in policy.severity_overrides:
                        r.severity = policy.severity_overrides[r.code]  # type: ignore
            return res

    out = await asyncio.gather(*[_guarded(v) for v in validators])
    return [r for sub in out for r in sub]


# -------------------------------------------------------------------
# Step 1: Transparent validation runner
# -------------------------------------------------------------------

_ENGINE_VERSION = "validators@0.3.0"
_ORDER = {"block": 3, "drop": 2, "warn": 1, "allow": 0}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reduce_overall(outcomes: List[ValidatorOutcome]) -> Decision:
    if not outcomes:
        return "allow"
    return max(outcomes, key=lambda o: _ORDER[o.decision]).decision


def _results_to_outcome(v: BaseValidator, results: List[ValidationResult]) -> ValidatorOutcome:
    """Collapse legacy ValidationResults into one transparent ValidatorOutcome."""
    reasons: List[Reason] = []
    worst: Decision = "allow"
    worst_sev = "info"

    for r in results:
        sev = r.severity.upper()
        if sev == "BLOCK":
            decision = "block"; sev2 = "critical"
        elif sev == "WARN":
            decision = "warn"; sev2 = "low"
        else:
            decision = "allow"; sev2 = "info"

        if _ORDER[decision] > _ORDER[worst]:
            worst = decision
            worst_sev = sev2

        reasons.append(Reason(code=r.code, message=r.message))

    if not reasons:
        reasons.append(Reason(code="OK", message="Passed"))

    return ValidatorOutcome(
        validator_name=getattr(v, "code", v.__class__.__name__),
        decision=worst,
        severity=worst_sev,
        reasons=reasons,
        source=SourceRef(component=v.__class__.__module__, version="unknown"),
        metadata=None,
    )

def run_validators_transparent(*, job_id: str, case_id: str, case: dict) -> ValidationReport:
    """
    Calls all validators via .run(case) -> List[ValidationResult].
    Adapts them into ValidatorOutcomes. Any exception = 'block'.
    Writes one line to logs/audit.ndjson.
    """
    started_at = _now_iso()
    outcomes: List[ValidatorOutcome] = []

    # ✅ Always coerce to CaseBundle
    if isinstance(case, CaseBundle):
        case_bundle: CaseBundle = case
    else:
        try:
            case_bundle = CaseBundle(**case)
        except Exception as e:
            # If construction fails, record as a block immediately
            outcomes.append(ValidatorOutcome(
                validator_name="CaseBundleInit",
                decision="block",
                severity="critical",
                reasons=[Reason(code="CASE_INIT_FAILED", message=str(e))],
                source=SourceRef(component="core.schemas.case_bundle", version="unknown"),
                duration_ms=0,
            ))
            finished_at = _now_iso()
            return ValidationReport(
                job_id=job_id,
                case_id=case_id,
                started_at=started_at,
                finished_at=finished_at,
                outcomes=outcomes,
                overall="block",
                engine_version=_ENGINE_VERSION,
            )

    for v in load_all_validators():
        t0 = perf_counter()
        try:
            results: List[ValidationResult] = v.run(case_bundle)
            outcome = _results_to_outcome(v, results)
            outcome.duration_ms = int((perf_counter() - t0) * 1000)
            outcomes.append(outcome)
        except Exception as e:
            outcomes.append(ValidatorOutcome(
                validator_name=getattr(v, "code", v.__class__.__name__),
                decision="block",
                severity="critical",
                reasons=[Reason(code="VALIDATOR_EXCEPTION", message=str(e))],
                source=SourceRef(component=v.__class__.__module__, version="unknown"),
                duration_ms=int((perf_counter() - t0) * 1000),
            ))

    finished_at = _now_iso()
    overall = _reduce_overall(outcomes)

    report = ValidationReport(
        job_id=job_id,
        case_id=case_id,
        started_at=started_at,
        finished_at=finished_at,
        outcomes=outcomes,
        overall=overall,
        engine_version=_ENGINE_VERSION,
    )
    audit_append_ndjson(report)
    return report