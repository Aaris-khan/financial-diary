const fs = require('fs');
const assert = require('assert/strict');

const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const start = html.indexOf('    function installTapLayer() {');
const end = html.indexOf('    function wrapFunction(name, wrapper) {', start);
assert(start >= 0 && end > start, 'installTapLayer boundaries must exist');
const source = html.slice(start, end).trim();

function createHarness(cardType, cardKey) {
  const listeners = {};
  let exportCalls = 0;
  const classes = new Set();
  const card = {
    dataset: { aarishExportType: cardType, aarishExportKey: cardKey },
    isConnected: true,
    style: {},
    classList: {
      add: value => classes.add(value),
      remove: value => classes.delete(value),
      contains: value => classes.has(value),
    },
    closest: selector => selector === '.aarish-no-ripple' ? null : null,
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 300, height: 80 }),
    appendChild: () => {},
  };
  const target = {
    closest: selector => {
      if (selector === '.glass-card') return card;
      if (selector.includes('[data-aarish-export-card="true"]')) return card;
      return null;
    },
  };
  const documentMock = {
    addEventListener: (type, handler) => { listeners[type] = handler; },
  };
  const qs = () => null;
  const qsa = () => [];
  const promote = () => {};
  const ripple = () => {};
  const safeHaptic = () => {};
  const release = () => {};
  const bounce = () => {};
  const isDeleteButton = () => false;
  const ambient = () => {};
  const aarishExportCardToPremiumPdfCoreV1 = () => {
    exportCalls += 1;
    assert.equal(card.dataset.aarishExportType, cardType);
    assert.equal(card.dataset.aarishExportKey, cardKey);
    return Promise.resolve({ method: 'mocked-pdf' });
  };

  const install = new Function(
    'document', 'qs', 'qsa', 'promote', 'ripple', 'safeHaptic', 'release', 'bounce',
    'isDeleteButton', 'ambient', 'aarishExportCardToPremiumPdfCoreV1', `${source}; return installTapLayer;`
  )(documentMock, qs, qsa, promote, ripple, safeHaptic, release, bounce, isDeleteButton, ambient, aarishExportCardToPremiumPdfCoreV1);
  install();
  return { listeners, card, target, getExportCalls: () => exportCalls };
}

function event(target, pointerId, x, y) {
  return { target, pointerId, pointerType: 'touch', button: 0, clientX: x, clientY: y };
}

async function wait(ms) {
  await new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
  // Use realistic entry-card metadata for the same types rendered by the app.
  for (const [type, key] of [['milk', 'Alice'], ['udhar', 'Bob'], ['diary', 'd1']]) {
    const h = createHarness(type, key);
    h.listeners.pointerdown(event(h.target, 1, 100, 100));
    assert.equal(h.card.classList.contains('aarish-longpress-active-v1'), true);
    await wait(760);
    assert.equal(h.getExportCalls(), 1);
    assert.equal(h.card.classList.contains('aarish-longpress-active-v1'), true);
    h.listeners.pointerup(event(h.target, 1, 100, 100));
    assert.equal(h.card.classList.contains('aarish-longpress-active-v1'), false);
  }

  // A short tap must never export.
  {
    const h = createHarness('milk', 'Alice');
    h.listeners.pointerdown(event(h.target, 2, 100, 100));
    h.listeners.pointerup(event(h.target, 2, 100, 100));
    await wait(760);
    assert.equal(h.getExportCalls(), 0);
    assert.equal(h.card.classList.contains('aarish-longpress-active-v1'), false);
  }

  // Moving beyond the configured tolerance must cancel the pending export.
  {
    const h = createHarness('milk', 'Alice');
    h.listeners.pointerdown(event(h.target, 3, 100, 100));
    h.listeners.pointermove(event(h.target, 3, 120, 100));
    await wait(760);
    assert.equal(h.getExportCalls(), 0);
    assert.equal(h.card.classList.contains('aarish-longpress-active-v1'), false);
  }

  console.log('PASS: server-side long-press handler integration harness');
  console.log('PASS: milk, credit, and diary entry cards export once after the 720 ms hold');
  console.log('PASS: pointerup cleanup removes pressed state');
  console.log('PASS: short tap and >14 px movement cancel export');
  process.exit(0);
}

run().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
  
