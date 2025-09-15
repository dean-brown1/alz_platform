# scripts/bench_boards_trace_sleep.py
from __future__ import annotations

# --- make repo root importable ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import time as _time
from time import perf_counter

from project_stack.pipelines import steps
from core.schemas.case_lenient import parse_case_lenient
from med_stack.board.roles import neurology_ai, imaging_ai, genomics_ai, pharmaco_ai, env_ai

SLEEPS = []

# Monkey-patch time.sleep so we can see who sleeps and how long
_time_sleep_orig = _time.sleep
def traced_sleep(sec):
    SLEEPS.append(sec)
    return _time_sleep_orig(sec)
_time.sleep = traced_sleep  # patch


def bench_one(name, mod, data):
    t0 = perf_counter()
    try:
        out = mod.analyze(data)
    except Exception as e:
        dt = perf_counter() - t0
        print(f"{name:10s} -> {dt:.3f}s  EXC={e}  sleeps={SLEEPS}")
        SLEEPS.clear()
        return
    dt = perf_counter() - t0
    notes = out.get("notes") if isinstance(out, dict) else ""
    print(f"{name:10s} -> {dt:.3f}s  sleeps={SLEEPS}  notes={notes}")
    SLEEPS.clear()


if __name__ == "__main__":
    payload = {
        "case_id": "bench-local",
        "demographics": {"sex": "1", "age": "85 yrs", "handedness": "Right"},
        "clinical_notes": "Timing probe",
    }
    coerced, _ = parse_case_lenient(payload)
    cb = steps.normalize(steps.ingest(coerced))

    bench_one("neurology", neurology_ai, coerced)
    bench_one("imaging",   imaging_ai,   cb)
    bench_one("genomics",  genomics_ai,  cb)
    bench_one("pharma",    pharmaco_ai,  cb)
    bench_one("env",       env_ai,       cb)
