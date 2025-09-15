
# scripts/run_batch.py
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Dict, Any
import argparse, sys, requests

from config import INPUT_DIR, OUTPUT_DIR, AUDIT_REF, API_HOST, API_PORT

def _post_job(payload: Dict[str, Any]) -> str:
    url = f"http://{API_HOST}:{API_PORT}/v0/jobs"
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()["job_id"]

def _wait_done(job_id: str, timeout_s: int = 30) -> Dict[str, Any]:
    url = f"http://{API_HOST}:{API_PORT}/v0/jobs/{job_id}"
    t0 = time.time()
    last = None
    while True:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            j = r.json()
            if j.get("state") in ("done", "blocked", "error"):
                return j
            last = j
        elif r.status_code != 404:
            r.raise_for_status()
        if time.time() - t0 > timeout_s:
            raise RuntimeError(f"timeout waiting for job {job_id}; last={last}")
        time.sleep(0.2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=str, default=str(INPUT_DIR))
    ap.add_argument("--output", type=str, default=str(OUTPUT_DIR))
    args = ap.parse_args()

    in_dir = Path(args.input); out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(in_dir.glob("*.json"))
    if not files:
        print(f"No case files in {in_dir}"); return 0

    print(f"API: http://{API_HOST}:{API_PORT}")
    print(f"Audit: {AUDIT_REF}")
    print(f"Cases: {len(files)} files" )

    for fp in files:
        payload = json.loads(fp.read_text(encoding="utf-8"))
        jid = _post_job(payload)
        j = _wait_done(jid)
        pc = j.get("protocol_card")
        if not pc:
            print(f"[WARN] job {jid} has no protocol_card"); continue
        (out_dir / f"{jid}.protocol_card.json").write_text(json.dumps(pc, indent=2), encoding="utf-8")
        import requests
        url = f"http://{API_HOST}:{API_PORT}/v0/exports/protocol_card?id={jid}&fmt=csv"
        r = requests.get(url, timeout=10); r.raise_for_status()
        (out_dir / f"{jid}.protocol_card.csv").write_text(r.text, encoding="utf-8")
        print(f"[OK] {fp.name} -> {jid}")

    print("Done."); return 0

if __name__ == "__main__":
    import sys; sys.exit(main())
