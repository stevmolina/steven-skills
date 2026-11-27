// Loads Playwright and launches Chromium on any machine.
//
// Library, first that works:
//   1. playwright or playwright-core resolvable from this script's folder
//   2. the same from the global npm root (`npm root -g`)
//   3. playwright-core installed into ~/.cache/design-check (done once)
// Browser, first that works:
//   1. Playwright's own Chromium
//   2. installed Google Chrome (channel "chrome")
//   3. download Playwright's Chromium once, then retry
//
// DESIGN_CHECK_FORCE_INSTALL=1 skips steps 1 and 2 of the library list (for testing).

import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const CACHE_DIR = path.join(os.homedir(), '.cache', 'design-check');
const NAMES = ['playwright', 'playwright-core'];
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const npxCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';

function say(msg) { process.stderr.write(`design-check: ${msg}\n`); }

// Resolve `name` as if required from a file inside `dir`.
function resolveFrom(dir, name) {
  try { return createRequire(path.join(dir, '__design_check__.js')).resolve(name); }
  catch { return null; }
}

async function importResolved(file, name) {
  const mod = await import(pathToFileURL(file).href);
  const lib = mod.chromium ? mod : mod.default;
  if (!lib || !lib.chromium) throw new Error(`${name} at ${file} has no chromium export`);
  // Package folder, used later to run that package's own installer (matching version).
  let pkgDir = path.dirname(file);
  while (pkgDir !== path.dirname(pkgDir) && !fs.existsSync(path.join(pkgDir, 'package.json'))) pkgDir = path.dirname(pkgDir);
  return { lib, file, pkgDir, name };
}

function globalRoot() {
  try { return execFileSync(npmCmd, ['root', '-g'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); }
  catch { return null; }
}

let cached = null;

export async function loadPlaywright() {
  if (cached) return cached;
  const force = process.env.DESIGN_CHECK_FORCE_INSTALL === '1';
  const places = [];
  if (!force) {
    places.push(here);
    const g = globalRoot();
    // `npm root -g` is the node_modules folder itself; resolve from its parent.
    if (g) places.push(path.dirname(g));
  }
  for (const dir of places) {
    for (const name of NAMES) {
      const file = resolveFrom(dir, name);
      if (file) {
        try { return (cached = await importResolved(file, name)); } catch { /* try next */ }
      }
    }
  }
  // 3. Install playwright-core into the cache folder.
  let file = resolveFrom(CACHE_DIR, 'playwright-core');
  if (!file) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
    const pkg = path.join(CACHE_DIR, 'package.json');
    if (!fs.existsSync(pkg)) fs.writeFileSync(pkg, '{"name":"design-check-cache","private":true}\n');
    say(`installing playwright-core into ${CACHE_DIR} (one time)`);
    execFileSync(npmCmd, ['install', '--prefix', CACHE_DIR, '--no-audit', '--no-fund', '--silent', 'playwright-core'], { stdio: ['ignore', 'ignore', 'inherit'] });
    file = resolveFrom(CACHE_DIR, 'playwright-core');
    if (!file) throw new Error(`could not install playwright-core into ${CACHE_DIR}`);
  }
  return (cached = await importResolved(file, 'playwright-core'));
}

function installChromium(pw) {
  say('downloading Chromium for Playwright (one time)');
  const cli = path.join(pw.pkgDir, 'cli.js');
  if (fs.existsSync(cli)) {
    execFileSync(process.execPath, [cli, 'install', 'chromium'], { stdio: ['ignore', 'ignore', 'inherit'] });
  } else {
    execFileSync(npxCmd, ['-y', 'playwright', 'install', 'chromium'], { stdio: ['ignore', 'ignore', 'inherit'] });
  }
}

export async function launchBrowser(options = {}) {
  const pw = await loadPlaywright();
  const { chromium } = pw.lib;
  const errors = [];
  try { return await chromium.launch({ headless: true, ...options }); } catch (e) { errors.push(e); }
  try { return await chromium.launch({ headless: true, channel: 'chrome', ...options }); } catch (e) { errors.push(e); }
  try {
    installChromium(pw);
    return await chromium.launch({ headless: true, ...options });
  } catch (e) {
    errors.push(e);
  }
  const first = errors.map((e) => String(e.message || e).split('\n')[0]).join(' | ');
  const hint = process.platform === 'linux' ? ' (on Linux, system libraries may be missing: run `npx playwright install-deps chromium`)' : '';
  throw new Error(`could not launch Chromium: ${first}${hint}`);
}
