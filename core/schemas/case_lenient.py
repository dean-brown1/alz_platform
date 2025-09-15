from __future__ import annotations
from typing import Any, Dict, List, Tuple

Issue = Dict[str, Any]

def _coerce_int(v: Any) -> Tuple[Any, Issue | None]:
    if v is None or isinstance(v, int):
        return v, None
    if isinstance(v, float) and v.is_integer():
        out = int(v)
        return out, {"reason": "float_to_int", "raw": v, "coerced": out}
    if isinstance(v, str):
        s = v.strip()
        digits = "".join(ch for ch in s if ch.isdigit() or ch in "+-")
        if digits and digits.lstrip("+-").isdigit():
            out = int(digits)
            return out, {"reason": "coerced_str_to_int", "raw": v, "coerced": out}
    return v, {"reason": "uncoerced_int_like", "raw": v, "coerced": v}

def _norm_map(val: Any, mapping: Dict[str, str], tag: str) -> Tuple[Any, Issue | None]:
    if val is None:
        return None, None
    raw = str(val).strip().lower()
    if raw in mapping:
        out = mapping[raw]
        return out, None if out == val else {"reason": f"normalized_{tag}", "raw": val, "coerced": out}
    return val, {"reason": f"unrecognized_{tag}", "raw": val, "coerced": val}

def parse_case_lenient(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Issue]]:
    """Never raises. Coerces obvious fields; returns (coerced_case, issues)."""
    case = dict(payload)  # shallow copy
    issues: List[Issue] = []

    # --- demographics coercions ---
    demo = dict((case.get("demographics") or {}))
    # age
    age, e = _coerce_int(demo.get("age"))
    demo["age"] = age
    if e: issues.append({"path": "demographics.age", **e, "level": "WARN"})
    # sex
    sex, e = _norm_map(demo.get("sex"),
                       {"m": "male", "male": "male", "1": "male", "f": "female", "female": "female", "0": "female"},
                       "sex")
    demo["sex"] = sex
    if e: issues.append({"path": "demographics.sex", **e, "level": "INFO" if e["reason"].startswith("normalized") else "WARN"})
    # handedness
    hand, e = _norm_map(demo.get("handedness"),
                        {"l": "left", "left": "left", "r": "right", "right": "right"},
                        "handedness")
    demo["handedness"] = hand
    if e: issues.append({"path": "demographics.handedness", **e, "level": "INFO" if e["reason"].startswith("normalized") else "WARN"})

    if demo:
        case["demographics"] = demo

    return case, issues
