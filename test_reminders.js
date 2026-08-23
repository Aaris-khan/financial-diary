const fs = require('fs');
const assert = require('assert/strict');

const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const start = html.indexOf('/* AARISH_REMINDER_CORE_V3_START */');
const end = html.indexOf('/* AARISH_REMINDER_CORE_V3_END */', start);
assert(start >= 0 && end > start, 'reminder engine markers must exist');

const source = html.slice(start, end);
const getTodayISO = () => '2026-08-23';
const reminder = new Function('getTodayISO', `${source}; return {
  key: aarishReminderKeyCoreV3,
  normalizeEntry: aarishReminderNormalizeEntryCoreV3,
  normalizeDb: aarishReminderNormalizeDbCoreV3,
  dueEntries: aarishReminderDueEntriesCoreV3,
  isoDate: aarishReminderIsoDateCoreV3
};`)(getTodayISO);

assert.equal(reminder.isoDate('2026-02-28'), '2026-02-28');
assert.equal(reminder.isoDate('2026-02-29'), '');
assert.equal(reminder.isoDate(''), '');
assert.equal(reminder.isoDate('2026-2-3'), '');

const aliceKey = reminder.key(' Alice ');
assert.ok(/^p_[0-9a-f]+$/.test(aliceKey));
assert.equal(aliceKey, reminder.key('Alice'));
assert.notEqual(aliceKey, reminder.key('आलिया'));

const raw = {
  [aliceKey]: { name: ' Alice ', date: '2026-08-22', note: 'Collect milk money' },
  future: { name: 'Bob', date: '2026-08-24', note: 'Not due yet' },
  invalidDate: { name: 'Charlie', date: '2026-02-31', note: 'Reject this' },
  emptyDate: { name: 'Diana', date: '', note: 'Reject this too' },
  malformed: null,
  list: []
};

const normalized = reminder.normalizeDb(raw);
assert.equal(Object.keys(normalized).length, 2, 'only valid entries should survive normalization');
assert.equal(normalized[aliceKey].name, 'Alice');
assert.equal(normalized[aliceKey].date, '2026-08-22');

const due = reminder.dueEntries(raw, '2026-08-23');
assert.deepEqual(due.map(entry => entry.name), ['Alice']);
assert.equal(reminder.dueEntries(raw, '2026-08-21').length, 0);
assert.deepEqual(reminder.dueEntries({
  a: { name: 'Today', date: '2026-08-23' },
  b: { name: 'Overdue', date: '2026-08-01' }
}, '2026-08-23').map(entry => entry.name), ['Overdue', 'Today']);

const longNote = reminder.normalizeEntry('Eve', { date: '2026-08-23', note: 'x'.repeat(500) });
assert.equal(longNote.note.length, 240);
assert.equal(reminder.normalizeEntry('Eve', { date: '2026-08-23' }).name, 'Eve');
assert.equal(reminder.normalizeEntry('Eve', { date: '2026-08-23', name: '<script>' }).name, '<script>');

console.log('PASS: reminder date validation and malformed-state normalization');
console.log('PASS: UID-safe deterministic party keys and today/overdue filtering');
console.log('PASS: note length bounded to 240 characters');

const gcWindow = {};
const gcMilkDB = { Active: { records: [] } };
const gcUdharDB = [];
const gcRemindersDB = {
  [reminder.key('Active')]: { name: 'Active', date: '2026-08-23' },
  [reminder.key('Deleted Customer')]: { name: 'Deleted Customer', date: '2026-08-23' }
};
const gcHarness = new Function('getTodayISO', 'window', 'milkDB', 'udharDB', 'remindersDB', `${source}; return { gc: aarishReminderGarbageCollectCoreV3 };`)(getTodayISO, gcWindow, gcMilkDB, gcUdharDB, gcRemindersDB);
gcHarness.gc();
setTimeout(() => {
  assert.ok(gcRemindersDB[reminder.key('Active')]);
  assert.equal(gcRemindersDB[reminder.key('Deleted Customer')], undefined);
  console.log('PASS: deleted-party reminder garbage collection');
}, 0);
