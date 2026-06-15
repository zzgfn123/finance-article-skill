#!/usr/bin/env python3
"""
run_evals.py — 跑 loan-article-skill 的全部 binary checks

用法:
  python3 scripts/run_evals.py            # 跑全部
  python3 scripts/run_evals.py --validate # 仅跑 binary checks(快速)
  python3 scripts/run_evals.py --json     # 输出 JSON
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SKILL_ROOT = Path(__file__).parent.parent

BINARY_CHECKS = [
    {
        "id": "BC-01",
        "description": "SKILL.md 存在且含 frontmatter",
        "command": '[ -f SKILL.md ] && head -1 SKILL.md | grep -q "^---"',
    },
    {
        "id": "BC-02",
        "description": "含 references/company-profile.md",
        "command": "[ -f references/company-profile.md ]",
    },
    {
        "id": "BC-03",
        "description": "含 references/writing-data.md",
        "command": "[ -f references/writing-data.md ]",
    },
    {
        "id": "BC-04",
        "description": "含 references/city-profiles.md",
        "command": "[ -f references/city-profiles.md ]",
    },
    {
        "id": "BC-05",
        "description": "含 assets/title-patterns.md",
        "command": "[ -f assets/title-patterns.md ]",
    },
    {
        "id": "BC-06",
        "description": "含 assets/article-template.md",
        "command": "[ -f assets/article-template.md ]",
    },
    {
        "id": "BC-07",
        "description": "count_words.py 可执行",
        "command": "python3 scripts/count_words.py --help 2>&1 | grep -q 'file'",
    },
    {
        "id": "BC-08",
        "description": "validate_article.py 可执行",
        "command": "python3 scripts/validate_article.py --help 2>&1 | grep -q 'city'",
    },
    {
        "id": "BC-09",
        "description": "触发词出现在 SKILL.md",
        "command": "grep -q '帮我写贷款文章' SKILL.md",
    },
    {
        "id": "BC-10",
        "description": "6 段式骨架在 assets",
        "command": "grep -q '6 段' assets/article-template.md",
    },
    {
        "id": "BC-11",
        "description": "含 references/model-config.md 且 SKILL.md 含写作模型确认",
        "command": "[ -f references/model-config.md ] && grep -q '写作模型确认' SKILL.md",
    },
]


def run_check(check: dict) -> dict:
    """跑单条 binary check。"""
    cmd = check["command"]
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=SKILL_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            **check,
            "pass": result.returncode == 0,
            "exit_code": result.returncode,
            "stderr": result.stderr.strip()[:200] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {**check, "pass": False, "exit_code": -1, "stderr": "timeout"}
    except Exception as e:
        return {**check, "pass": False, "exit_code": -1, "stderr": str(e)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--validate", action="store_true", help="仅跑 binary checks")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    args = p.parse_args()

    results = [run_check(c) for c in BINARY_CHECKS]
    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "checks": results,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("loan-article-skill :: Binary Checks")
        print("=" * 60)
        for r in results:
            mark = "[OK]" if r["pass"] else "[FAIL]"
            print(f"{mark} {r['id']}: {r['description']}")
            if not r["pass"] and r.get("stderr"):
                print(f"   -> {r['stderr']}")
        print("=" * 60)
        if passed == total:
            print(f"ALL PASS: {passed}/{total}  VALID")
            return 0
        else:
            print(f"FAILED: {total - passed}/{total}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
