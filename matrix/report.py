"""junit XML files (one per environment) → Markdown compatibility table on stdout."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def results(path: Path) -> dict[str, str]:
    """test name → pass | fail | skip"""
    out = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        name = case.get("name", "?").split("[")[0]
        if case.find("failure") is not None or case.find("error") is not None:
            status = "fail"
        elif case.find("skipped") is not None:
            status = "skip"
        else:
            status = "pass"
        # A parametrised check fails if any parameter fails.
        if out.get(name) != "fail":
            out[name] = status
    return out


def main() -> None:
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    envs = yaml.safe_load((ROOT / "matrix/environments.yaml").read_text())["environments"]
    table = {e["name"]: results(folder / f"{e['name']}.xml") if (folder / f"{e['name']}.xml").exists() else None
             for e in envs}
    checks = sorted({c for r in table.values() if r for c in r})
    icon = {"pass": "✅", "fail": "❌", "skip": "➖", None: "?"}
    print("# Environment compatibility\n")
    print("| Check | " + " | ".join(table) + " |")
    print("|---|" + "---|" * len(table))
    for c in checks:
        print(f"| `{c}` | " + " | ".join(icon[(r or {}).get(c)] if r else "no result" for r in table.values()) + " |")
    print("\n➖ = not applicable to that environment (skipped).")
    failed = [n for n, r in table.items() if r is None or "fail" in r.values()]
    if failed:
        print(f"\n**Not passing:** {', '.join(failed)}")


if __name__ == "__main__":
    main()
