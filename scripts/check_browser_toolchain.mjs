// Check the installed artifact, not only npm's dependency graph: ws is bundled inside Playwright.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const expectedNode = fs.readFileSync(path.join(root, '.node-version'), 'utf8').trim();
assert.equal(process.versions.node, expectedNode, `Use Node ${expectedNode} from .node-version`);
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const expectedPlaywright = manifest.devDependencies.playwright;
assert.equal(require('playwright/package.json').version, expectedPlaywright);
const core = require.resolve('playwright-core/package.json');
assert.equal(require(core).version, expectedPlaywright);
const notices = fs.readFileSync(path.join(path.dirname(core), 'lib/utilsBundle.js.LICENSE'), 'utf8');
const match = notices.match(/^- ws@(\d+)\.(\d+)\.(\d+) /m);
assert.ok(match, 'Bundled ws version missing from Playwright notices; inspect the upgraded artifact');
const [major, minor] = match.slice(1).map(Number);
// GHSA-96hv-2xvq-fx4p is fixed in 8.21.0, which also includes GHSA-58qx-3vcg-4xpx.
assert.ok(major === 8 && minor >= 21, 'Bundled ws must be patched (8.21.0+)');
console.log(`Node ${expectedNode}; Playwright/core ${expectedPlaywright}; bundled ws ${match.slice(1).join('.')}`);
