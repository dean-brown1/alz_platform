from __future__ import annotations
import yaml, os
from dataclasses import dataclass
from typing import Dict, List
@dataclass
class Policy:
    order: List[str]
    concurrency: int
    severity_overrides: Dict[str, str]
def load_policy(path: str = "validators/policy.yaml") -> Policy:
    if not os.path.exists(path):
        return Policy(order=[], concurrency=4, severity_overrides={})
    data = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
    return Policy(
        order=data.get("order", []),
        concurrency=int(data.get("concurrency", 4)),
        severity_overrides=data.get("severity_overrides", {}) or {},
    )
