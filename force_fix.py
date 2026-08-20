#!/usr/bin/env python3
import re
import os
import shutil

file_path = "index.html"

if not os.path.exists(file_path):
    print(f"ERROR: '{file_path}' not found in the current directory!")
    exit(1)

# Create a backup
shutil.copy2(file_path, file_path + ".backup")
print(f"Backup created: {file_path}.backup")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

changes_made = 0

# 1. Tailwind Injection
if "AARISH_TAILWIND_RUNTIME_CORE_V1" not in content:
    content = re.sub(
        r'(<script src="[^"]*firebase-database-compat\.js"></script>)',
        lambda m: m.group(1) + '\n    <!-- AARISH_TAILWIND_RUNTIME_CORE_V1: restore Tailwind utility classes on cold/client-only loads -->\n    <script>\n        window.tailwind = window.tailwind || {};\n        window.tailwind.config = Object.assign({}, window.tailwind.config || {}, { darkMode: "class" });\n    </script>\n    <script src="https://cdn.tailwindcss.com"></script>',
        content,
        count=1
    )
    changes_made += 1

# 2. URL Generator Patch
if "&pmonth=" not in content:
    content = re.sub(
        r'(const link = window\.location\.origin \+ window\.location\.pathname \+ "\?phantom=" \+ encodeURIComponent\(type\) \+ "&pname=" \+ encodeURIComponent\(name\))\s*(\+ "&data=" \+ encoded;)',
        lambda m: m.group(1) + ' + "&pmonth=" + encodeURIComponent(String(selectedMonth)) + "&pyear=" + encodeURIComponent(String(selectedYear)) ' + m.group(2),
        content,
        count=1
    )
    changes_made += 1

# 3. Phantom Params Patch
if "params.get('pmonth')" not in content:
    content = re.sub(
        r'(const pData = params\.get\([\'"]data[\'"]\);)',
        lambda m: m.group(1) + '\n    const pMonth = params.get(\'pmonth\');\n    const pYear = params.get(\'pyear\');',
        content,
        count=1
    )
    changes_made += 1

# 4. Phantom Filter State & Legacy Fallback
if "AARISH_PHANTOM_FILTER_CONTEXT_CORE_V1" not in content:
    state_logic = r"""
                // AARISH_PHANTOM_FILTER_CONTEXT_CORE_V1
                const requestedMonth = Number.parseInt(pMonth, 10);
                const requestedYear = Number.parseInt(pYear, 10);
                if (Number.isInteger(requestedMonth) && requestedMonth >= 0 && requestedMonth <= 11 && Number.isInteger(requestedYear) && requestedYear >= 2000 && requestedYear <= 2100) {
                    selectedMonth = requestedMonth;
                    selectedYear = requestedYear;
                } else {
                    const snapshotRecords = Array.isArray(parsedData) ? parsedData : (parsedData && Array.isArray(parsedData.records) ? parsedData.records : (parsedData && parsedData.date ? [parsedData] : []));
                    let latestSnapshotDate = null;
                    snapshotRecords.forEach(record => {
                        const raw = String(record && record.date || '').trim();
                        const match = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
                        if (!match) return;
                        const year = Number(match[1]);
                        const month = Number(match[2]) - 1;
                        const day = Number(match[3]);
                        if (!Number.isInteger(year) || year < 2000 || year > 2100 || !Number.isInteger(month) || month < 0 || month > 11 || !Number.isInteger(day) || day < 1 || day > 31) return;
                        const score = year * 1000000 + (month + 1) * 10000 + day;
                        if (!latestSnapshotDate || score > latestSnapshotDate.score) {
                            latestSnapshotDate = { score, month, year };
                        }
                    });
                    if (latestSnapshotDate) {
                        selectedMonth = latestSnapshotDate.month;
                        selectedYear = latestSnapshotDate.year;
                    }
                }
                [['filter-month-milk', 'filter-year-milk'], ['filter-month-exp', 'filter-year-exp'], ['filter-month-salary', 'filter-year-salary']].forEach(([monthId, yearId]) => {
                    const monthEl = document.getElementById(monthId);
                    const yearEl = document.getElementById(yearId);
                    if (monthEl) monthEl.value = String(selectedMonth);
                    if (yearEl) yearEl.value = String(selectedYear);
                });

"""
    content = re.sub(
        r'(// 3\. Backend Mutators Neutered\s*window\.aarishFirebaseLaterV48 = async \(\) => false;)',
        lambda m: state_logic + m.group(1),
        content,
        count=1
    )
    changes_made += 1

# 5. TDZ (Temporal Dead Zone) Fix Patch
if "setTimeout(executePhantomJail, 0);" not in content:
    tdz_logic = """if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', executePhantomJail, { once: true });
            } else {
                setTimeout(executePhantomJail, 0);
            }"""
    content = re.sub(
        r'if\s*\(\s*document\.readyState\s*===\s*[\'"]loading[\'"]\s*\)\s*\{\s*document\.addEventListener\(\s*[\'"]DOMContentLoaded[\'"]\s*,\s*executePhantomJail\s*\);\s*\}\s*else\s*\{\s*executePhantomJail\(\s*\);\s*\}',
        lambda m: tdz_logic,
        content,
        count=1
    )
    changes_made += 1

if changes_made > 0:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS! {changes_made} patches aggressively injected into {file_path}")
else:
    print(f"No changes made. Either the file is already patched or patterns weren't found.")
