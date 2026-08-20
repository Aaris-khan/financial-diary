import re
import sys

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("Error: index.html not found.")
    sys.exit(1)

# 1. UPGRADE BOOTLOADER (Receiver Side UI Routing)
if "pType === 'salary'" not in content:
    bootloader_addition = r"""} else if (pType === 'salary') {
                window.salaryDB = {};
                window.salaryDB[pName] = parsedData;
                window.activeSalaryPerson = pName;
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById('salary-detail-screen').classList.add('active');
                const titleEl = document.getElementById('salary-detail-title');
                if(titleEl) titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`;
                if(typeof renderSalaryRecords === 'function') renderSalaryRecords();
            } else if (pType === 'expense') {
                window.expenseDB = parsedData;
                window.activeExpenseCategory = pName;
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById('expense-detail-screen').classList.add('active');
                const titleEl = document.getElementById('expense-detail-title');
                if(titleEl) titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`;
                if(typeof renderExpenseRecords === 'function') renderExpenseRecords();
            } else if (pType === 'diary') {
                window.diaryDB = [parsedData];
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById('diary-detail-screen').classList.add('active');
                const title = document.getElementById('diary-view-title');
                const date = document.getElementById('diary-view-date');
                const content = document.getElementById('diary-view-content');
                if (title) title.textContent = parsedData.title || 'Untitled';
                if (date) date.textContent = (typeof diaryFormatDateCoreV1 === 'function') ? diaryFormatDateCoreV1(parsedData.date) : parsedData.date;
                if (content) content.textContent = parsedData.content || '';
            } else if (pType === 'projects') {
                window.projectDB = {};
                window.projectDB[pName] = parsedData;
                window.activeProject = pName;
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById('project-detail-screen').classList.add('active');
                const titleEl = document.getElementById('project-detail-title');
                if(titleEl) titleEl.innerHTML = `${pName} <span class="phantom-badge">LIVE SNAPSHOT</span>`;
                if(typeof renderProjectRecords === 'function') renderProjectRecords();
            """
    content = re.sub(r'(\}\s*else if\s*\(\s*pType === \'udhar\'\s*\)\s*\{[\s\S]*?renderUdharRecords\(\);\s*\})', r'\1' + '\n            ' + bootloader_addition, content)

# 2. UPGRADE LINK GENERATOR (Sender Side Data Extraction)
if "type === 'salary'" not in content:
    link_addition = r"""} else if (type === 'salary') {
            if (!salaryDB[name] || !salaryDB[name].records || salaryDB[name].records.length === 0) {
                return showToast("No records found to generate snapshot!");
            }
            dataToShare = salaryDB[name];
        } else if (type === 'expense') {
            const records = (typeof expenseDB !== 'undefined' ? expenseDB : []).filter(e => String(e.category || '').trim() === String(name || '').trim());
            if (records.length === 0) {
                return showToast("No expense records found to generate snapshot!");
            }
            dataToShare = records;
        } else if (type === 'diary') {
            const entry = (typeof diaryFindEntryCoreV1 === 'function') ? diaryFindEntryCoreV1(name) : (typeof diaryDB !== 'undefined' ? diaryDB : []).find(d => String(d.id) === String(name));
            if (!entry) {
                return showToast("Diary page not found!");
            }
            dataToShare = entry;
        } else if (type === 'projects') {
            if (!projectDB[name] || !projectDB[name].records || projectDB[name].records.length === 0) {
                return showToast("No records found to generate snapshot!");
            }
            dataToShare = projectDB[name];
        """
    content = re.sub(r'(dataToShare = records;\s*\})', r'\1' + '\n        ' + link_addition, content, count=1)

# 3. FIX SALARY UI (Replace old delete-toast hold with universal snapshot hold)
content = re.sub(
    r'ontouchstart="startSalaryLongPress\([^)]+\)"\s*ontouchend="cancelSalaryLongPress\(\)"\s*ontouchmove="cancelSalaryLongPress\(\)"\s*onmousedown="startSalaryLongPress\([^)]+\)"\s*onmouseup="cancelSalaryLongPress\(\)"\s*onmouseleave="cancelSalaryLongPress\(\)"\s*onclick="(try\{haptic\(\)\}catch\(e\)\{\};\s*openSalaryDetail\(([^)]+)\))"',
    r'ontouchstart="aarishStartCardHold(\'salary\', \2)" ontouchend="aarishCancelCardHold()" ontouchmove="aarishCancelCardHold()" onmousedown="aarishStartCardHold(\'salary\', \2)" onmouseup="aarishCancelCardHold()" onmouseleave="aarishCancelCardHold()" onclick="if(window.__aarishIsLongPressActive){ window.__aarishIsLongPressActive=false; return; } \1"',
    content
)

# 4. FIX DIARY UI
content = re.sub(
    r'onclick="(try\{haptic\(\)\}catch\(e\)\{\};\s*openDiaryDetail\(([^)]+)\))"',
    r'ontouchstart="aarishStartCardHold(\'diary\', \2)" ontouchend="aarishCancelCardHold()" ontouchmove="aarishCancelCardHold()" onmousedown="aarishStartCardHold(\'diary\', \2)" onmouseup="aarishCancelCardHold()" onmouseleave="aarishCancelCardHold()" onclick="if(window.__aarishIsLongPressActive){ window.__aarishIsLongPressActive=false; return; } \1"',
    content
)

# 5. FIX ALL OTHER UI CARDS DYNAMICALLY (Expense, Udhar, Business)
def universal_injector(match):
    full_onclick = match.group(0)
    action_code = match.group(1)
    func_name = match.group(2)
    arg = match.group(3)

    if 'window.__aarishIsLongPressActive' in full_onclick: return full_onclick

    module_map = {'Udhar': 'udhar', 'Expense': 'expense', 'Project': 'projects'}
    mod = module_map.get(func_name, '')
    if not mod: return full_onclick

    new_attrs = f'ontouchstart="aarishStartCardHold(\'{mod}\', {arg})" ontouchend="aarishCancelCardHold()" ontouchmove="aarishCancelCardHold()" onmousedown="aarishStartCardHold(\'{mod}\', {arg})" onmouseup="aarishCancelCardHold()" onmouseleave="aarishCancelCardHold()" '
    new_onclick = f'onclick="if(window.__aarishIsLongPressActive){{ window.__aarishIsLongPressActive=false; return; }} {action_code}"'
    return new_attrs + new_onclick

content = re.sub(
    r'onclick="(try\{haptic\(\)\}catch\(e\)\{\};\s*open(Udhar|Expense|Project)Detail\(([^)]+)\))"',
    universal_injector,
    content
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ SUCCESS: Snapshot Share Logic has been successfully wired into Salary, Expense, Diary, and Business Modules!")
