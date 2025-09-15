from __future__ import annotations
from typing import Dict, List, Any
import csv
import io

# Minimal expected structure:
# {
#   "case_id": "patient-123",
#   "stage": "MCI",
#   "resilience_index": 0.67,
#   "expected_life_expectancy_delta": -0.4,
#   "candidate_protocols": [
#       {"title": "Baseline Cognitive Support", "steps": ["...","..."], "rationale": "why", "risk_notes": "notes"}
#   ],
#   "evidence": [
#       {"modality": "clinical", "source": "note-2024-03", "summary": "MoCA 20/30", "confidence": 0.7}
#   ],
#   "limitations": ["Heuristic; boards not yet model-merged"],
#   "reproducibility": {"modalities": ["clinical","imaging"], "hash": "abc123", "model": "meta-8b-longread"}
# }

def _safe(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)

def render_qrc_markdown(card: Dict[str, Any]) -> str:
    """Quick Review Card (markdown) — medical-first, skim-friendly."""
    lines: List[str] = []
    lines.append(f"# Protocol Card — Case {card.get('case_id','')}")
    lines.append("")
    # Top-line scores
    lines.append("## Summary")
    lines.append(f"- Stage: **{_safe(card.get('stage')) or '—'}**")
    lines.append(f"- Resilience Index: **{_safe(card.get('resilience_index')) or '—'}**")
    lines.append(f"- Expected Life Expectancy Δ (yrs): **{_safe(card.get('expected_life_expectancy_delta')) or '—'}**")
    lines.append("")
    # Candidate protocols
    cps = card.get("candidate_protocols", []) or []
    lines.append("## Candidate Protocols")
    if not cps:
        lines.append("- _(none)_")
    else:
        for i, cp in enumerate(cps, 1):
            title = cp.get("title") or f"Protocol {i}"
            lines.append(f"### {i}. {title}")
            steps = cp.get("steps") or []
            if steps:
                for s in steps:
                    lines.append(f"- [ ] {s}")
            rationale = cp.get("rationale")
            if rationale:
                lines.append(f"> **Rationale:** {rationale}")
            risk = cp.get("risk_notes")
            if risk:
                lines.append(f"> **Risk Notes:** {risk}")
            lines.append("")
    # Evidence
    ev = card.get("evidence", []) or []
    lines.append("## Key Evidence (selected)")
    if not ev:
        lines.append("- _(none)_")
    else:
        for e in ev[:12]:  # keep QRC short
            mod = _safe(e.get("modality"))
            src = _safe(e.get("source"))
            summ = _safe(e.get("summary"))
            conf = _safe(e.get("confidence"))
            lines.append(f"- **{mod}** | {src} — {summ} (confidence: {conf})")
    # Limitations
    lim = card.get("limitations", []) or []
    if lim:
        lines.append("")
        lines.append("## Limitations")
        for l in lim:
            lines.append(f"- {l}")
    # Reproducibility
    rep = card.get("reproducibility", {}) or {}
    if rep:
        lines.append("")
        lines.append("## Reproducibility")
        mods = ", ".join(rep.get("modalities", []) or [])
        if mods:
            lines.append(f"- Modalities: {mods}")
        if rep.get("model"):
            lines.append(f"- Model: {rep['model']}")
        if rep.get("hash"):
            lines.append(f"- Hash: `{rep['hash']}`")
    return "\n".join(lines).strip() + "\n"

def render_evidence_csv(card: Dict[str, Any]) -> str:
    """CSV table for evidence — judge-friendly spreadsheet export."""
    ev = card.get("evidence", []) or []
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["modality", "source", "summary", "confidence"])
    for e in ev:
        w.writerow([
            _safe(e.get("modality")),
            _safe(e.get("source")),
            _safe(e.get("summary")),
            _safe(e.get("confidence")),
        ])
    return buf.getvalue()
