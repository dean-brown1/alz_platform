# med_stack/board/roles/neurology_ai.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import re

def _lower(s: Any) -> str:
    try:
        return str(s or "").lower()
    except Exception:
        return ""

def _clip(text: str, n: int = 160) -> str:
    t = (text or "").strip().replace("\n", " ")
    return t if len(t) <= n else t[: n - 3] + "..."

def _coerce_int_like(v: Any) -> Optional[int]:
    if v is None:
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    try:
        s = str(v)
        m = re.search(r"[+-]?\d+", s)
        if m:
            return int(m.group(0))
    except Exception:
        pass
    return None

def _get_dict(d: Any, *keys) -> Any:
    """
    Try to descend dict-like structures; ignore failures.
    """
    cur = d
    for k in keys:
        try:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        except Exception:
            return None
    return cur

def _get_attr(o: Any, name: str) -> Any:
    try:
        return getattr(o, name)
    except Exception:
        return None

def analyze(cb) -> Dict[str, Any]:
    """
    Structured clinical (neurology) board reasoning with robust CaseBundle access.
    Signals:
      - Age ≥ 80 -> +0.30 confidence
      - clinical_notes mention 'mci' or 'mild cognitive' -> +0.40 confidence
    """
    findings: List[Dict[str, Any]] = []
    notes: List[str] = []
    metrics: Dict[str, Any] = {}

    # --- Robust extraction for demographics.age ---
    age = None

    # 1) Attribute-style (pydantic/dataclass)
    if age is None:
        demo_attr = _get_attr(cb, "demographics")
        if isinstance(demo_attr, dict):
            age = _coerce_int_like(demo_attr.get("age"))
        elif demo_attr is not None:
            age = _coerce_int_like(_get_attr(demo_attr, "age"))

    # 2) cb.case (dict) → demographics.age
    if age is None:
        case_dict = _get_attr(cb, "case")
        if isinstance(case_dict, dict):
            age = _coerce_int_like(_get_dict(case_dict, "demographics", "age"))

    # 3) Fallback: cb itself might be dict-like
    if age is None and isinstance(cb, dict):
        age = _coerce_int_like(_get_dict(cb, "demographics", "age"))

    # --- Robust extraction for clinical_notes ---
    clinical_notes = None

    # 1) Attribute on cb
    if clinical_notes is None:
        clinical_notes = _get_attr(cb, "clinical_notes")

    # 2) In cb.case
    if clinical_notes is None:
        case_dict = _get_attr(cb, "case")
        if isinstance(case_dict, dict):
            clinical_notes = case_dict.get("clinical_notes")

    # 3) Dict-like cb
    if clinical_notes is None and isinstance(cb, dict):
        clinical_notes = cb.get("clinical_notes")

    lnotes = _lower(clinical_notes)

    # --- Heuristics ---
    conf = 0.0
    if isinstance(age, int) and age >= 80:
        conf += 0.30
        notes.append(f"age>=80 contributes 0.30 (age={age})")

    if "mci" in lnotes or "mild cognitive" in lnotes:
        conf += 0.40
        notes.append("clinical notes mention MCI/mild cognitive (+0.40)")

    if conf > 0.0:
        findings.append({
            "id": "F-CLN-001",
            "label": "MCI pattern suspected",
            "confidence": round(min(conf, 0.95), 2),
            "evidence": [_clip(clinical_notes)] if clinical_notes else []
        })
        # Cap contribution per-board so later boards can add too
        metrics["ri_component"] = round(min(conf, 0.40), 2)
    else:
        metrics["ri_component"] = 0.0

    return {
        "board": "clinical",
        "findings": findings,
        "notes": "; ".join(notes) if notes else "",
        "metrics": metrics,
    }
