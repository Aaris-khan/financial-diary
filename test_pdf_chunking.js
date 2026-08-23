const fs = require('fs');
const assert = require('assert/strict');

const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const helperStart = html.indexOf('        function adaptiveChunkSize(rowCount) {');
const helperEnd = html.indexOf('        function updateProgress(label, processed, total) {', helperStart);
assert(helperStart >= 0 && helperEnd > helperStart, 'adaptive chunk helper boundaries must exist');
const adaptiveChunkSize = new Function(`${html.slice(helperStart, helperEnd)}; return adaptiveChunkSize;`)();

assert.equal(adaptiveChunkSize(0), 1);
assert.equal(adaptiveChunkSize(250), 250);
assert.equal(adaptiveChunkSize(251), 400);
assert.equal(adaptiveChunkSize(2500), 400);
assert.equal(adaptiveChunkSize(2501), 600);
assert.equal(adaptiveChunkSize(10000), 600);
assert.equal(adaptiveChunkSize(10001), 800);
assert.equal(adaptiveChunkSize(20000), 800);

const renderDocumentStart = html.indexOf('        async function renderDocument(options) {');
const renderDatasetStart = html.indexOf('        async function renderDataset(dataset) {');
assert(renderDocumentStart >= 0 && renderDatasetStart > renderDocumentStart, 'PDF render functions must exist');
const renderDocumentSource = html.slice(renderDocumentStart, renderDatasetStart);
const renderDatasetEnd = html.indexOf('        return { ensurePlugin,', renderDatasetStart);
assert(renderDatasetEnd > renderDatasetStart, 'renderDataset boundary must exist');
const renderDatasetSource = html.slice(renderDatasetStart, renderDatasetEnd);

for (const source of [renderDocumentSource, renderDatasetSource]) {
  assert.match(source, /adaptiveChunkSize\(/, 'renderer must choose an adaptive chunk size');
  assert.match(source, /rows\.slice\(offset, offset \+ chunkSize\)/, 'renderer must slice rows before rendering');
  assert.match(source, /await yieldToBrowser\(35\)/, 'renderer must yield between chunks');
  assert.match(source, /Finalizing PDF/, 'renderer must yield before final export');
}

assert.match(renderDatasetSource, /Number\(dataset\.rowCount\)/, 'dataset renderer must use total row count for progress');
assert.match(html, /compress: true/, 'PDF documents must keep compression enabled');
assert.match(html, /doc\.output\('blob'\)/, 'PDF delivery must use blob output');

console.log('PASS: adaptive PDF chunk sizing');
console.log('PASS: renderDocument and renderDataset yield between bounded chunks');
console.log('PASS: compressed Blob delivery remains enabled');
