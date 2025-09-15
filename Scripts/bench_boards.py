# scripts/bench_boards.py
from __future__ import annotations

# --- make repo root importable ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]  # repo root (one level above /scripts)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from time import perf_counter

from project_stack.pipelines import steps
from core.schemas.case_lenient import parse_case_lenient
from med_stack.board.roles import neurology_ai, imaging_ai, genomics_ai, pharmaco_ai, env_ai


def bench_one(name, mod, data):
    t0 = perf_counter()
    try:
        out = mod.analyze(data)
    except Exception as e:
        dt = perf_counter() - t0
        print(f"{name:10s} -> {dt:.3f}s  EXC={e}")
        return
    dt = perf_counter() - t0
    notes = ""
    if isinstance(out, dict):
        notes = out.get("notes") or ""
    print(f"{name:10s} -> {dt:.3f}s  notes={notes}")


if __name__ == "__main__":
    # Minimal payload (intentionally no imaging/omics/pharma/env)
    payload = {
        "case_id": "bench-local",
        "demographics": {"sex": "1", "age": "85 yrs", "handedness": "Right"},
        "clinical_notes": "Timing probe",
    }
    coerced, _ = parse_case_lenient(payload)
    cb = steps.normalize(steps.ingest(coerced))  # normalized bundle

    # Match API usage: neurology gets 'coerced'; others get 'cb'
    bench_one("neurology", neurology_ai, coerced)
    bench_one("imaging",   imaging_ai,   cb)
    bench_one("genomics",  genomics_ai,  cb)
    bench_one("pharma",    pharmaco_ai,  cb)
    bench_one("env",       env_ai,       cb)
