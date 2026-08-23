from pathlib import Path

root = Path(__file__).parent
html = (root / 'index.html').read_text(encoding='utf-8')
assert (root / 'sw.js').is_file(), 'service worker file must exist'
assert html.count('id="party-reminder-modal"') == 1
assert html.count('id="reminder-due-badge"') == 1
assert html.count('id="reminder-limit"') == 1
assert html.count('id="reminder-notification-btn"') == 1
assert html.count('id="dashboard-reminders-container"') == 1
assert html.count('AARISH_REMINDER_CORE_V3_START') == 1
assert html.count('AARISH_REMINDER_CORE_V3_END') == 1
assert html.count('<script') == html.count('</script>'), 'script tags must remain balanced'
assert 'remindersDB: aarishReminderNormalizeDbCoreV3(raw.remindersDB)' in html
assert 'remindersDB = aarishReminderNormalizeDbCoreV3(state.remindersDB);' in html
assert 'remindersDB = {};' in html
assert 'navigator.setAppBadge' in html and 'navigator.clearAppBadge' in html
assert 'class="absolute top-3 right-3 w-14 h-14 rounded-[20px]' in html
assert 'rgba(0,122,255,0.10)' in html and '#007AFF' in html
assert 'data-reminder-party="${encodeURIComponent(name)}"' in html
assert "navigator.serviceWorker.register('./sw.js'" in html
assert 'notificationclick' in (root / 'sw.js').read_text(encoding='utf-8')
assert "if (!box) return;\n    box.querySelectorAll('[data-reminder-party]')" in html, 'ledger binding must guard a missing box before querying'
print('PASS: reminder markup IDs and script balance')
print('PASS: state persistence, logout cleanup, badge, and service-worker invariants')
