# scripts/profile_board.py
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cProfile, pstats, io
from time import perf_counter

from project_stack.pipelines import steps
from core.schemas.case_lenient import parse_case_lenient
from med_stack.board.roles import imaging_ai

def profile_one(name, mod, data, sort='cumtime', limit=30):
    pr = cProfile.Profile()
    pr.enable()
    t0 = perf_counter()
    try:
        mod.analyze(data)
    except Exception:
        pass
    dt = perf_counter() - t0
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats(sort).print_stats(limit)
    print(f"\n=== {name} total {dt:.3f}s ===")
    print(s.getvalue())

if __name__ == "__main__":
    payload = {
        "case_id": "bench-prof",
        "demographics": {"sex": "1", "age": "85 yrs", "handedness": "Right"},
        "clinical_notes": "Timing probe",
    }
    coerced, _ = parse_case_lenient(payload)
    cb = steps.normalize(steps.ingest(coerced))
    profile_one("imaging", imaging_ai, cb)
