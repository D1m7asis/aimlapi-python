"""Generate proxy modules in aimlapi mirroring openai's package structure."""
from __future__ import annotations

from pathlib import Path


def build_proxy_content(module: str) -> str:
    return (
        "from __future__ import annotations\n\n"
        f"from {module} import *  # noqa: F401, F403\n"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    openai_root = repo_root / "src" / "openai"
    aimlapi_root = repo_root / "src" / "aimlapi"

    if not openai_root.is_dir():
        raise SystemExit(f"Missing openai package at {openai_root}")

    for src_path in sorted(openai_root.rglob("*.py")):
        rel_path = src_path.relative_to(openai_root)

        # Skip the manually maintained aimlapi.__init__ equivalent.
        if rel_path == Path("__init__.py"):
            continue

        target_path = aimlapi_root / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.name == "__init__.py":
            rel_dir = rel_path.parent
            if rel_dir == Path(""):
                # Should not happen because we skipped the root __init__.
                continue
            module = f"openai.{rel_dir.as_posix().replace('/', '.')}" if rel_dir.parts else "openai"
        else:
            module_path = rel_path.with_suffix("")
            module = f"openai.{module_path.as_posix().replace('/', '.')}"

        content = build_proxy_content(module)

        if target_path.exists() and target_path.read_text() == content:
            continue

        target_path.write_text(content)


if __name__ == "__main__":
    main()
