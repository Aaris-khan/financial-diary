#!/usr/bin/env python3
import re, os, shutil, sys, datetime

TARGET = "index.html"

if not os.path.isfile(TARGET):
    print(f"[FAIL] '{TARGET}' is folder me nahi mila. Sahi folder me jaake chalao.")
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

backup = f"{TARGET}.bak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(TARGET, backup)

results = []

pattern1 = re.compile(
    r"if\(typeof renderProjectRecords === 'function'\) renderProjectRecords\(\);\s*\n\s*if\(typeof hideLoader === 'function'\) hideLoader\(\);"
)
replacement1 = (
    "if(typeof renderProjectRecords === 'function') renderProjectRecords();\n"
    "            }\n"
    "\n"
    "                if(typeof hideLoader === 'function') hideLoader();"
)
matches1 = len(pattern1.findall(content))
if matches1 == 1:
    content = pattern1.sub(replacement1, content, count=1)
    results.append(("initPhantomBootloader: missing '}' before hideLoader", "FIXED", None))
elif matches1 == 0:
    results.append(("initPhantomBootloader: missing '}' before hideLoader", "SKIP", "pattern nahi mila (shayad already fixed)"))
else:
    results.append(("initPhantomBootloader: missing '}' before hideLoader", "SKIP", f"{matches1} jagah match hua, manual check karo"))

pattern2 = re.compile(
    r"dataToShare = projectDB\[name\];\s*\n\s*try \{"
)
replacement2 = (
    "dataToShare = projectDB[name];\n"
    "        }\n"
    "\n"
    "    try {"
)
matches2 = len(pattern2.findall(content))
if matches2 == 1:
    content = pattern2.sub(replacement2, content, count=1)
    results.append(("aarishGeneratePenDriveSnapshotLink: missing '}' before try", "FIXED", None))
elif matches2 == 0:
    results.append(("aarishGeneratePenDriveSnapshotLink: missing '}' before try", "SKIP", "pattern nahi mila (shayad already fixed)"))
else:
    results.append(("aarishGeneratePenDriveSnapshotLink: missing '}' before try", "SKIP", f"{matches2} jagah match hua, manual check karo"))

any_fixed = any(r[1] == "FIXED" for r in results)
if any_fixed:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(content)

print(f"[BACKUP] {backup}")
print("")
for name, status, note in results:
    line = f"[{status}] {name}"
    if note:
        line += f" — {note}"
    print(line)
print("")
if any_fixed:
    print("Done — index.html update ho gaya.")
else:
    print("Koi fix apply nahi hua (upar reason dekho).")
