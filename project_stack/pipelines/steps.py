from __future__ import annotations
from core.schemas.case_bundle import CaseBundle, Observation, SourceRef
from core.provenance.audit import audit


def ingest(raw: dict) -> CaseBundle:
    """Build a CaseBundle from raw input, coercing all observation content to dicts."""
    audit("project_stack", "ingest_start", subject=raw.get("case_id"))
    case_id = raw.get("case_id") or "unknown"

    observations: list[Observation] = []

    # Clinical notes -> one observation with dict content
    notes = raw.get("clinical_notes")
    if isinstance(notes, str) and notes.strip():
        observations.append(
            Observation(
                id="clinical-0",
                modality="clinical",
                content={"notes": notes.strip()},
            )
        )

    # Imaging -> each top-level key becomes a dict content row
    imaging = raw.get("imaging")
    if isinstance(imaging, dict):
        for k, v in imaging.items():
            observations.append(
                Observation(
                    id=f"imaging-{k}",
                    modality="imaging",
                    content={k: v},
                )
            )

    # Omics -> whole dict as one row
    omics = raw.get("omics")
    if isinstance(omics, dict) and omics:
        observations.append(
            Observation(
                id="omics-0",
                modality="omics",
                content=omics,
            )
        )

    # Pharma -> whole dict as one row
    pharma = raw.get("pharma")
    if isinstance(pharma, dict) and pharma:
        observations.append(
            Observation(
                id="pharma-0",
                modality="pharma",
                content=pharma,
            )
        )

    # Environment -> whole dict as one row
    environment = raw.get("environment")
    if isinstance(environment, dict) and environment:
        observations.append(
            Observation(
                id="environment-0",
                modality="environment",
                content=environment,
            )
        )

    # Preserve any pre-supplied structured observations
    for o in raw.get("observations", []):
        try:
            observations.append(Observation(**o))
        except Exception:
            # Skip malformed rows instead of crashing
            continue

    # Modalities from collected observations (fallback 'clinical')
    modalities = sorted({o.modality for o in observations}) or ["clinical"]

    cb = CaseBundle(
        case_id=case_id,
        subject_id=raw.get("subject_id", "unknown"),
        modalities=modalities,
        sources=[SourceRef(**s) for s in raw.get("sources", [])],
        observations=observations,
    )
    audit("project_stack", "ingest_done", subject=cb.case_id)
    return cb


def normalize(cb: CaseBundle) -> CaseBundle:
    audit("project_stack", "normalize", subject=cb.case_id)
    cb.modalities = sorted(set(m.lower() for m in cb.modalities))
    return cb


def export(cb: CaseBundle) -> dict:
    audit("project_stack", "export", subject=cb.case_id)
    return cb.model_dump()
