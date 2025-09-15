# scripts/find_dangling.py
from __future__ import annotations
import os, sys, ast, pathlib, re
from typing import Dict, Set, Tuple, List

# ---- settings ----
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

# Treat ALL intended entry surfaces as roots (add/remove as needed)
ENTRY_MODULES: Set[str] = {
    "api.app",          # current FastAPI app
    "api.v0",           # router modules under api/v0/*
    "cli.main",         # CLI entrypoint (if used)
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    "dist", "build", "data", "var",
    ".pytest_cache", ".mypy_cache"
}
IGNORE_FILES_REGEX = re.compile(r"(^test_.*\.py$|conftest\.py$)")

# Allow dynamic/optional modules that may be imported indirectly at runtime
DYNAMIC_ALLOW = {
    "api.board_runners",
    "api.hooks",
    "boards",                         # if you plan local 'boards/*.py'
    "med_stack.board.roles",
    "med_stack.review.consensus",
    "med_stack.review.synthesis",
    "core.decomposer",                # your decomposer
    "validators",                     # all validator packages
    "exports.protocol_card_renderer", # renderer you plan to use
    "orchestration",                  # orchestration helpers
}


def relpath(p: pathlib.Path) -> str:
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except Exception:
        return str(p)

def module_name_from_path(p: pathlib.Path) -> str:
    """
    Convert a file path to a Python module name relative to PROJECT_ROOT.
    Handles Windows paths and __init__.py correctly.
    """
    try:
        rel = p.relative_to(PROJECT_ROOT)
    except ValueError:
        # If not inside root, skip
        return ""
    # Drop suffix; treat __init__.py as the package module
    if rel.name == "__init__.py":
        rel = rel.parent
    else:
        rel = rel.with_suffix("")
    parts = list(rel.parts)
    # Remove empty / drive-lettery oddities just in case
    parts = [seg for seg in parts if seg and seg not in (os.sep,)]
    return ".".join(parts)

def walk_py_files(root: pathlib.Path) -> List[pathlib.Path]:
    out: List[pathlib.Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored dirs
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in filenames:
            if fn.endswith(".py") and not IGNORE_FILES_REGEX.search(fn):
                out.append(pathlib.Path(dirpath) / fn)
    return out

def parse_imports(py_path: pathlib.Path) -> Set[str]:
    try:
        src = py_path.read_text(encoding="utf-8")
    except Exception:
        return set()
    try:
        tree = ast.parse(src)
    except Exception:
        return set()
    mods: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module)
    return mods

def build_graph(files: List[pathlib.Path]) -> Tuple[Dict[str, pathlib.Path], Dict[str, Set[str]]]:
    mod2path: Dict[str, pathlib.Path] = {}
    edges: Dict[str, Set[str]] = {}
    for p in files:
        mod = module_name_from_path(p)
        if not mod:
            continue
        mod2path[mod] = p
    for mod, p in mod2path.items():
        deps = set()
        for imp in parse_imports(p):
            deps.add(imp)
        edges[mod] = deps
    return mod2path, edges

def _expand_prefixes(target: str, mod2path: Dict[str, pathlib.Path]) -> Set[str]:
    """
    If 'target' is a package name, include submodules under it that exist on disk.
    """
    out = set()
    if target in mod2path:
        out.add(target)
    prefix = target + "."
    for m in mod2path:
        if m.startswith(prefix):
            out.add(m)
    return out

def resolve_reachable(mod2path: Dict[str, pathlib.Path], edges: Dict[str, Set[str]], roots: Set[str]) -> Set[str]:
    reachable: Set[str] = set()
    queue: List[str] = []

    # seed queue with roots (and their submodules)
    for r in roots:
        for m in _expand_prefixes(r, mod2path):
            if m not in reachable:
                reachable.add(m)
                queue.append(m)

    while queue:
        cur = queue.pop()
        for dep in edges.get(cur, ()):
            # Enqueue exact match or any children found on disk
            for m in _expand_prefixes(dep, mod2path):
                if m not in reachable:
                    reachable.add(m)
                    queue.append(m)
    return reachable

def main():
    files = walk_py_files(PROJECT_ROOT)
    mod2path, edges = build_graph(files)

    # Compute reachable from entry modules
    reachable = resolve_reachable(mod2path, edges, ENTRY_MODULES)

    # Always consider dynamic-allow modules reachable if they exist physically
    for dyn in DYNAMIC_ALLOW:
        for m in _expand_prefixes(dyn, mod2path):
            reachable.add(m)

    all_modules = {m for m in mod2path if not mod2path[m].name == "__init__.py"}
    dangling = sorted(all_modules - reachable)

    print("== Dangling Python files (not import-reachable from entrypoints) ==")
    for m in dangling:
        print(f"- {m:<60} [{relpath(mod2path[m])}]")
    print()
    print(f"Total .py files scanned: {len(files)}")
    print(f"Reachable modules:       {len(reachable)}")
    print(f"Dangling modules:        {len(dangling)}")

if __name__ == "__main__":
    sys.exit(main())
