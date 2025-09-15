from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, Tuple


def _normalize(text: str) -> str:
    # Keep normalization minimal to preserve clinical nuance
    return text.replace("\r\n", "\n").strip()


def chunk_text(
    text: str,
    target_chars: int = 4000,
    overlap_chars: int = 400,
    min_para_chars: int = 200,
) -> List[str]:
    """
    Greedy paragraph-based chunking with configurable overlap.
    Suitable for long clinical notes / reports when tokenizer isn't available.

    - target_chars: desired chunk size (approx.)
    - overlap_chars: characters from prior chunk appended as context
    - min_para_chars: avoid creating tiny tail fragments
    """
    text = _normalize(text)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []

    buf: List[str] = []
    cur_len = 0

    for p in paras:
        plen = len(p)
        if cur_len + plen + 2 <= target_chars or cur_len < min_para_chars:
            buf.append(p)
            cur_len += plen + 2
        else:
            chunk = "\n\n".join(buf).strip()
            if chunk:
                # add overlap from previous chunk tail
                tail = chunk[-overlap_chars:] if overlap_chars > 0 else ""
                chunks.append(chunk)
                buf = [tail, p] if tail else [p]
                cur_len = len("\n\n".join(buf))
            else:
                buf = [p]
                cur_len = plen

    if buf:
        chunks.append("\n\n".join(buf).strip())

    # de-duplicate possible identical chunks when overlap is large
    unique: List[str] = []
    for c in chunks:
        if len(unique) == 0 or c != unique[-1]:
            unique.append(c)
    return unique


MapFn = Callable[[str], str]
ReduceFn = Callable[[Sequence[str]], str]


def map_reduce(
    *,
    chunks: Sequence[str],
    map_fn: MapFn,
    reduce_fn: ReduceFn,
) -> Tuple[List[str], str]:
    """
    Generic map-reduce over chunks.
    Returns (map_outputs, reduced_output).
    """
    map_outputs = [map_fn(c) for c in chunks]
    reduced = reduce_fn(map_outputs)
    return map_outputs, reduced


# Example: tie provider.generate() into map/reduce without importing the provider here.
def build_default_map_fn(generate_fn: Callable[[str], str]) -> MapFn:
    def _map(chunk: str) -> str:
        prompt = (
            "You are a careful medical AI assisting Alzheimer’s research. "
            "Summarize clinically relevant facts (keep exact values/units), "
            "note contradictions, and list open questions.\n\n"
            f"=== INPUT CHUNK START ===\n{chunk}\n=== INPUT CHUNK END ==="
        )
        return generate_fn(prompt)
    return _map


def default_reduce_fn(responses: Sequence[str]) -> str:
    """
    Combine chunk summaries into a single, deduplicated synthesis with contradictions highlighted.
    """
    bullets = "\n".join(f"- {r.strip()}" for r in responses if r and r.strip())
    return (
        "SYNTHESIS OF LONG DOCUMENT (deduplicated, contradictions flagged):\n"
        f"{bullets}\n\n"
        "Provide final key risks, actionable items, and unresolved contradictions."
    )
