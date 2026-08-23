const fs = require('fs');
const assert = require('assert/strict');

const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const start = html.indexOf('        async function deliverFile(file, title, shareText) {');
const end = html.indexOf('        async function renderDocument(options) {', start);
assert(start >= 0 && end > start, 'deliverFile boundaries must exist');
const source = html.slice(start, end).trim();
const makeDeliverFile = new Function('filename', 'text', 'clearLoader', 'safeToast', 'navigator', 'document', 'URL', 'window', `${source}; return deliverFile;`);

function makeEnvironment({ shareMode = 'unsupported' } = {}) {
  const events = [];
  let clickCount = 0;
  let revoked = 0;
  const anchors = [];
  const sharedFiles = [];
  let resolveShare;
  let rejectShare;
  const pendingShare = new Promise((resolve, reject) => {
    resolveShare = resolve;
    rejectShare = reject;
  });

  const navigatorMock = {
    canShare: () => shareMode !== 'unsupported',
    share: (payload) => {
      events.push('share-called');
      sharedFiles.push(payload.files[0]);
      if (shareMode === 'resolved') return Promise.resolve();
      if (shareMode === 'abort') return Promise.reject(Object.assign(new Error('cancelled'), { name: 'AbortError' }));
      if (shareMode === 'rejected') return Promise.reject(new Error('NotAllowedError'));
      if (shareMode === 'pending') return pendingShare;
      if (shareMode === 'throws') throw new Error('share unavailable');
      throw new Error('unexpected share mode');
    }
  };
  const documentMock = {
    body: {
      appendChild: (node) => { anchors.push(node); events.push('append'); },
    },
    createElement: () => ({
      style: {},
      click: () => { clickCount += 1; events.push('download-click'); },
      remove: () => events.push('remove'),
    }),
  };
  const urlMock = {
    createObjectURL: () => { events.push('object-url'); return 'blob:mock'; },
    revokeObjectURL: () => { revoked += 1; },
  };
  const windowMock = { open: () => { events.push('window-open'); return {}; } };
  const clearLoader = () => events.push('loader-cleared');
  const safeToast = (message) => events.push('toast:' + message);
  const filename = (value) => String(value || 'Aarish_Report.pdf').replace(/\\s+/g, '_');
  const text = (value, fallback) => String(value || fallback || '');
  return { events, navigatorMock, documentMock, urlMock, windowMock, clearLoader, safeToast, filename, text, clickCount: () => clickCount, revoked: () => revoked, sharedFiles, resolveShare, rejectShare };
}

async function run() {
  const file = new File(['pdf bytes'], 'Milk_Alice.pdf', { type: 'application/pdf' });

  // A pending native share must not hold the delivery call or loader open.
  {
    const env = makeEnvironment({ shareMode: 'pending' });
    const deliverFile = makeDeliverFile(env.filename, env.text, env.clearLoader, env.safeToast, env.navigatorMock, env.documentMock, env.urlMock, env.windowMock);
    const resultPromise = deliverFile(file, 'Alice', 'Milk report');
    const result = await Promise.race([resultPromise, new Promise((_, reject) => setTimeout(() => reject(new Error('share path blocked')), 100))]);
    assert.equal(result.method, 'share_triggered');
    assert.equal(env.sharedFiles[0].name.startsWith('Milk_Alice_'), true);
    assert.equal(env.sharedFiles[0].name.endsWith('.pdf'), true);
    assert.equal(env.events[0], 'loader-cleared');
    assert.equal(env.events.includes('share-called'), true);
    env.resolveShare();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(env.events.includes('toast:Shared successfully!'), true);
  }

  // A platform share rejection must silently fall back to a browser download.
  {
    const env = makeEnvironment({ shareMode: 'rejected' });
    const deliverFile = makeDeliverFile(env.filename, env.text, env.clearLoader, env.safeToast, env.navigatorMock, env.documentMock, env.urlMock, env.windowMock);
    const result = await deliverFile(file, 'Alice', 'Milk report');
    assert.equal(result.method, 'share_triggered');
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(env.clickCount(), 1);
    assert.equal(env.events.includes('toast:PDF generated securely.'), true);
  }

  // Explicit user cancellation must not trigger an unexpected download.
  {
    const env = makeEnvironment({ shareMode: 'abort' });
    const deliverFile = makeDeliverFile(env.filename, env.text, env.clearLoader, env.safeToast, env.navigatorMock, env.documentMock, env.urlMock, env.windowMock);
    const result = await deliverFile(file, 'Alice', 'Milk report');
    assert.equal(result.method, 'share_triggered');
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(env.clickCount(), 0);
  }

  // Unsupported or synchronously failing share must use the direct fallback.
  for (const shareMode of ['unsupported', 'throws']) {
    const env = makeEnvironment({ shareMode });
    const deliverFile = makeDeliverFile(env.filename, env.text, env.clearLoader, env.safeToast, env.navigatorMock, env.documentMock, env.urlMock, env.windowMock);
    const result = await deliverFile(file, 'Alice', 'Milk report');
    assert.equal(result.method, 'download');
    assert.equal(env.clickCount(), 1);
    assert.equal(env.events.includes('toast:PDF generated securely.'), true);
  }

  console.log('PASS: server-side smart-share harness');
  console.log('PASS: pending share returns immediately and clears loader before share call');
  console.log('PASS: rejected share falls back to download without a refresh/error path');
  console.log('PASS: AbortError does not trigger an unwanted download');
  console.log('PASS: unsupported and synchronous share failures use deterministic download');
  process.exit(0);
}

run().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
  
