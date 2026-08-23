from pathlib import Path
import re
import subprocess

html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)</script>", html, re.I)
if not scripts:
    raise SystemExit("No inline JavaScript blocks found")
for index, code in enumerate(scripts, 1):
    path = Path(__file__).with_name(f".inline_script_{index}.js")
    path.write_text(code, encoding="utf-8")
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    path.unlink(missing_ok=True)
    if result.returncode:
        print(result.stderr)
        raise SystemExit(f"JavaScript syntax failed in block {index}")

required = [
    "const uniqueFile = new File(",
    "clearLoader();",
    "return { method: 'share_triggered' };",
    "PDF generated securely.",
    "Promise.resolve(sharePromise)",
]
for marker in required:
    if marker not in html:
        raise SystemExit(f"Missing patch invariant: {marker}")

deliver_start = html.find("        async function deliverFile(file, title, shareText) {")
deliver_end = html.find("        async function renderDocument(options) {", deliver_start)
deliver_body = html[deliver_start:deliver_end]
if "await navigator.share" in deliver_body:
    raise SystemExit("Blocking await navigator.share still present in deliverFile")

print(f"Validated {len(scripts)} inline JavaScript blocks and all smart-share invariants.")
  
