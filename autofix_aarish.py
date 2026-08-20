#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_FILE = Path("financial_diary_INDEX_HTML_20260820_071102_31062.txt")

VULNERABLE = (
    'titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`'
)

FIXED = (
    'titleEl.innerHTML = `${sanitizeHTML(pName)} '
    '<span class="phantom-badge">LIVE SNAPSHOT</span>`'
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def run_node_syntax_checks(source: str) -> None:
    matches = list(
        re.finditer(
            r"<script\b([^>]*)>(.*?)</script>",
            source,
            flags=re.IGNORECASE | re.DOTALL,
        )
    )

    if not matches:
        fail("No <script> blocks found.")

    js_blocks = []

    for index, match in enumerate(matches):
        attrs = match.group(1)
        body = match.group(2).strip()

        if not body:
            continue

        if re.search(
            r'\btype\s*=\s*["\']application/ld\+json["\']',
            attrs,
            flags=re.IGNORECASE,
        ):
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                fail(
                    f"JSON-LD syntax error in script block {index}: {exc}"
                )
            continue

        js_blocks.append((index, body))

    with tempfile.TemporaryDirectory(prefix="aarish_syntax_") as tmp:
        tmp_path = Path(tmp)

        for index, body in js_blocks:
            js_file = tmp_path / f"inline_script_{index}.js"
            js_file.write_text(body, encoding="utf-8")

            result = subprocess.run(
                ["node", "--check", str(js_file)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                fail(
                    "JavaScript syntax check failed for "
                    f"inline script {index}:\n{result.stderr.strip()}"
                )


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE

    if not target.is_file():
        fail(
            f"Target file not found: {target}\n"
            "Usage: python3 autofix_aarish.py /path/to/file"
        )

    source = target.read_text(encoding="utf-8")

    occurrences = source.count(VULNERABLE)

    if occurrences != 5:
        fail(
            "Safety assertion failed: expected exactly 5 vulnerable "
            f"snapshot title sinks, found {occurrences}. "
            "No changes were made."
        )

    if "function sanitizeHTML(" not in source:
        fail(
            "Existing sanitizeHTML() helper was not found. "
            "No changes were made."
        )

    # Preflight verification.
    run_node_syntax_checks(source)

    backup = target.with_suffix(target.suffix + ".bak")
    if backup.exists():
        backup = target.with_suffix(target.suffix + ".bak2")

    shutil.copy2(target, backup)

    patched = source.replace(VULNERABLE, FIXED)

    if patched.count(VULNERABLE) != 0:
        fail("Patch verification failed before write.")

    if patched.count(FIXED) != 5:
        fail(
            "Patch verification failed: expected exactly 5 fixed sinks, "
            f"found {patched.count(FIXED)}."
        )

    target.write_text(patched, encoding="utf-8")

    try:
        run_node_syntax_checks(patched)
    except SystemExit:
        shutil.copy2(backup, target)
        raise

    print("AARISH SURGICAL AUTOFIX: SUCCESS")
    print(f"Target : {target}")
    print(f"Backup : {backup}")
    print("Fixed  : 5 phantom snapshot HTML-injection sinks")
    print("Check  : JSON-LD valid + inline JavaScript syntax verified")
    print("Scope  : surgical change only; no wrapper/overlay architecture added")

    return 0


if __name__ == "__main__":
    sys.exit(main())
