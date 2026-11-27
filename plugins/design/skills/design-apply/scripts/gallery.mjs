#!/usr/bin/env node
// gallery.mjs: renders the same page in several design systems and lays them side by side.
//
//   node gallery.mjs --systems a,b,c [--library <dir>] [--sample <file>] [--out <dir>]
//                    [--title "..."] [--preview]
//
// A system is a folder name in the library (default ../library) or a path to a folder with
// DESIGN.md and tokens.css. For each system it writes <out>/<name>.html (the sample dressed
// in that system), screenshots desktop light and dark and phone light into <out>/shots/,
// runs the design check, then writes <out>/gallery.html and <out>/report.json.
// --sample renders your own page instead of the shared sample; keep its
// <style id="tokens"></style> slot (without it the tokens go in as the first <style>).
// --preview also copies each desktop light shot to <system>/preview.png.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { launchBrowser } from './lib/browser.mjs';
import { checkTarget, CHECKS, DEVICES, MODES } from './check.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const a = { systems: [], library: path.join(here, '..', 'library'), sample: path.join(here, '..', 'sample', 'sample.html'), out: path.join(os.tmpdir(), 'design-gallery'), title: null, preview: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const next = () => { if (i + 1 >= argv.length) throw new Error(`${k} needs a value`); return argv[++i]; };
    if (k === '--systems') a.systems = next().split(',').map((s) => s.trim()).filter(Boolean);
    else if (k === '--library') a.library = path.resolve(next());
    else if (k === '--sample') { a.sample = path.resolve(next()); a.customSample = true; }
    else if (k === '--out') a.out = path.resolve(next());
    else if (k === '--title') a.title = next();
    else if (k === '--preview') a.preview = true;
    else if (k === '-h' || k === '--help') a.help = true;
    else throw new Error(`unknown argument: ${k}`);
  }
  return a;
}

export function frontMatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const out = {};
  if (!m) return out;
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^([A-Za-z_][\w-]*):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].replace(/\s+#.*$/, '').trim();
    const unq = (s) => s.replace(/^(["'])(.*)\1$/, '$2');
    if (/^\[.*\]$/.test(v)) v = v.slice(1, -1).split(',').map((x) => unq(x.trim())).filter(Boolean);
    else if (v === 'true' || v === 'false') v = v === 'true';
    else v = unq(v);
    out[kv[1]] = v;
  }
  return out;
}

function resolveSystem(arg, library) {
  const candidates = [];
  if (arg.includes('/') || arg.includes(path.sep) || arg.startsWith('.')) candidates.push(path.resolve(arg));
  candidates.push(path.join(library, arg));
  if (!candidates.includes(path.resolve(arg))) candidates.push(path.resolve(arg));
  for (const dir of candidates) {
    if (fs.existsSync(path.join(dir, 'tokens.css'))) {
      const mdPath = path.join(dir, 'DESIGN.md');
      const fm = fs.existsSync(mdPath) ? frontMatter(fs.readFileSync(mdPath, 'utf8')) : {};
      const name = String(fm.name || path.basename(dir)).replace(/[^\w.-]+/g, '-');
      return { dir, name, fm, tokens: fs.readFileSync(path.join(dir, 'tokens.css'), 'utf8') };
    }
  }
  throw new Error(`system "${arg}" not found (looked for tokens.css in ${candidates.join(', ')})`);
}

// Puts a system's tokens into the sample page.
export function dress(sampleHtml, system, { baseHref } = {}) {
  let html = sampleHtml;
  const block = `<style id="tokens">\n${system.tokens}\n</style>`;
  const slot = /<style\b[^>]*\bid=["']tokens["'][^>]*>[\s\S]*?<\/style>/i;
  if (slot.test(html)) html = html.replace(slot, () => block);
  else {
    const head = html.match(/<head\b[^>]*>/i);
    const headEnd = html.search(/<\/head>/i);
    const firstStyle = html.search(/<(style|link)\b[^>]*>/i);
    if (firstStyle !== -1 && (headEnd === -1 || firstStyle < headEnd)) html = html.slice(0, firstStyle) + block + '\n' + html.slice(firstStyle);
    else if (headEnd !== -1) html = html.slice(0, headEnd) + block + '\n' + html.slice(headEnd);
    else if (head) html = html.replace(head[0], (h) => `${h}\n${block}`);
    else html = block + '\n' + html;
  }
  const insertInHead = (tag) => {
    const head = html.match(/<head\b[^>]*>/i);
    html = head ? html.replace(head[0], (h) => `${h}\n${tag}`) : tag + '\n' + html;
  };
  if (system.fm.loud === true) {
    const meta = /<meta\s+name=["']design-check["']\s+content=["']([^"']*)["'][^>]*>/i;
    const found = html.match(meta);
    if (found) {
      if (!/\bloud\b/.test(found[1])) html = html.replace(meta, (_m, c) => `<meta name="design-check" content="${c ? c + ',' : ''}loud">`);
    } else insertInHead('<meta name="design-check" content="loud">');
  }
  if (baseHref && !/<base\b/i.test(html)) insertInHead(`<base href="${baseHref}">`);
  return html;
}

async function shoot(browser, url, device, scheme, file) {
  const context = await browser.newContext({ ...DEVICES[device], colorScheme: scheme, reducedMotion: 'reduce' });
  try {
    const page = await context.newPage();
    try { await page.goto(url, { waitUntil: 'load', timeout: 30000 }); } catch (e) { if (!/Timeout/i.test(String(e.message))) throw e; }
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 4000))]);
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    });
    await page.screenshot({ path: file, fullPage: false });
  } finally {
    await context.close();
  }
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const SHORT = { colors: 'Colors', words: 'Words', chips: 'Code chips', contrast: 'Contrast fails', boxes: 'Boxes' };

function worstCell(check) {
  const rank = { pass: 0, warn: 1, fail: 2 };
  let best = null;
  for (const m of MODES) {
    const c = check.cells[m.id];
    if (!best || rank[c.grade] > rank[best.grade] || (rank[c.grade] === rank[best.grade] && c.value > best.value)) best = c;
  }
  return best;
}

function verdictLine(check) {
  if (!check) return 'Not checked';
  const grades = CHECKS.map(({ id }) => check.checks[id].verdict);
  const fails = grades.filter((g) => g === 'fail').length;
  const warns = grades.filter((g) => g === 'warn').length;
  if (!fails && !warns) return 'Passes';
  return [fails && `${fails} ${fails === 1 ? 'fail' : 'fails'}`, warns && `${warns} ${warns === 1 ? 'warning' : 'warnings'}`].filter(Boolean).join(', ');
}

export function galleryHtml({ title, items, generated }) {
  const cols = items.length === 1 ? 1 : items.length === 2 || items.length === 4 ? 2 : 3;
  const cards = items.map((it) => {
    const fm = it.fm;
    const rows = it.check
      ? CHECKS.map(({ id }) => {
          const c = worstCell(it.check.checks[id]);
          return `<li><span>${SHORT[id]}</span><span class="v ${c.grade}"><i aria-hidden="true"></i>${c.value}<span class="sr"> ${c.grade}</span></span></li>`;
        }).join('')
      : '';
    const relaxed = it.check && it.check.relaxed.length ? `<p class="note">Relaxed: ${esc(it.check.relaxed.join(', '))}</p>` : '';
    const source = fm.source ? `<a href="${esc(fm.source)}" rel="noopener">Source</a>` : '';
    const meta = [`<a class="open" href="${esc(it.html)}">Open live</a>`, source].filter(Boolean).join('<span class="sep" aria-hidden="true"> / </span>');
    return `
    <article class="cand">
      <div class="head"><h2>${esc(it.name)}</h2><p class="verdict ${it.check ? it.check.verdict : ''}">${esc(verdictLine(it.check))}</p></div>
      <p class="mood">${esc(fm.mood || '')}</p>
      <p class="meta">${meta}</p>
      <figure class="shot" data-shot>
        <img src="${esc(it.shots.desktopLight)}" alt="${esc(it.name)}, desktop, light" width="1440" height="900" loading="lazy">
        <figcaption class="seg" role="group" aria-label="Color scheme">
          <button type="button" aria-pressed="true" data-src="${esc(it.shots.desktopLight)}" data-alt="${esc(it.name)}, desktop, light">Light</button>
          <button type="button" aria-pressed="false" data-src="${esc(it.shots.desktopDark)}" data-alt="${esc(it.name)}, desktop, dark">Dark</button>
        </figcaption>
      </figure>
      <div class="lower">
        <img class="phone" src="${esc(it.shots.phoneLight)}" alt="${esc(it.name)}, phone, light" width="390" height="844" loading="lazy">
        <div class="side">
          <ul class="checks" aria-label="Check results">${rows}</ul>
          ${relaxed}
        </div>
      </div>
      <p class="pick">To pick: tell the agent <b>'pick ${esc(it.name)}'</b></p>
    </article>`;
  }).join('\n');

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<style>
  :root{--bg:#f6f5f1;--surface:#ecebe6;--ink:#1b1a17;--muted:#5c5952;--line:#dedbd3;
    --accent:#3343c8;--accent-ink:#ffffff;--ok:#1e7448;--warn:#8f5600;--bad:#b3261e;
    --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
    --serif:ui-serif,"New York","Iowan Old Style",Charter,Georgia,serif;
    --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;--ease:cubic-bezier(.2,.7,.2,1)}
  @media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121211;--surface:#1c1c1a;--ink:#edebe5;
    --muted:#a29f97;--line:#2c2b28;--accent:#9ba7ff;--accent-ink:#10142e;--ok:#6fd39f;--warn:#f0b65b;--bad:#ff8a80}}
  :root[data-theme="dark"]{--bg:#121211;--surface:#1c1c1a;--ink:#edebe5;--muted:#a29f97;--line:#2c2b28;
    --accent:#9ba7ff;--accent-ink:#10142e;--ok:#6fd39f;--warn:#f0b65b;--bad:#ff8a80}
  *{box-sizing:border-box}
  html,body{background:var(--bg)}
  body{margin:0;color:var(--ink);font:15px/1.55 var(--sans);-webkit-font-smoothing:antialiased}
  .wrap{max-width:1400px;margin:0 auto;padding:56px 40px 72px}
  .kicker{font:500 12px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0}
  h1{font:500 clamp(34px,4.2vw,54px)/1.04 var(--serif);letter-spacing:-.02em;margin:14px 0 10px}
  .intro{color:var(--muted);max-width:60ch;margin:0;font-size:16px}
  .grid{display:grid;grid-template-columns:repeat(${cols},minmax(0,1fr));gap:64px 40px;margin-top:44px}
  .cand{display:flex;flex-direction:column;gap:14px;padding-top:20px;border-top:1px solid var(--line);min-width:0}
  .head{display:flex;align-items:baseline;justify-content:space-between;gap:16px}
  .cand h2{font:500 30px/1.05 var(--serif);letter-spacing:-.015em;margin:0;overflow-wrap:anywhere}
  .verdict{font-size:13px;font-weight:600;margin:0;white-space:nowrap;color:var(--ok)}
  .verdict.warn{color:var(--warn)} .verdict.fail{color:var(--bad)}
  .mood{color:var(--muted);margin:-4px 0 0;min-height:3.1em}
  .meta{font-size:13px;color:var(--muted);margin:0}
  .sep{color:var(--line)}
  a{color:var(--ink);text-underline-offset:3px;text-decoration-color:var(--line);transition:text-decoration-color .15s var(--ease)}
  a:hover{text-decoration-color:currentColor}
  a.open{color:var(--accent);text-decoration-color:currentColor}
  figure{margin:0}
  .shot img,.phone{display:block;width:100%;height:auto;background:var(--surface);
    box-shadow:0 0 0 1px var(--line),0 18px 40px -26px rgba(0,0,0,.45);transition:transform .25s var(--ease)}
  .shot img{aspect-ratio:1440/900;border-radius:8px}
  .shot img:hover{transform:translateY(-2px)}
  .seg{display:flex;gap:16px;margin-top:10px}
  .seg button{font:500 12px/1 var(--mono);letter-spacing:.04em;background:none;border:0;padding:4px 0;
    color:var(--muted);cursor:pointer;border-bottom:1.5px solid transparent;transition:color .15s var(--ease)}
  .seg button:hover{color:var(--ink)}
  .seg button[aria-pressed="true"]{color:var(--ink);border-bottom-color:var(--accent)}
  button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}
  .lower{display:grid;grid-template-columns:38% 1fr;gap:22px;align-items:end;margin-top:6px}
  .phone{aspect-ratio:390/844;border-radius:14px}
  .checks{list-style:none;margin:0;padding:0;font-size:13px}
  .checks li{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px solid var(--line)}
  .checks li>span:first-child{color:var(--muted)}
  .v{font-family:var(--mono);display:inline-flex;align-items:center;gap:8px}
  .v i{width:7px;height:7px;border-radius:50%;display:inline-block;background:var(--ok)}
  .v.warn i{background:var(--warn)} .v.fail i{background:var(--bad)}
  .v.warn{color:var(--warn)} .v.fail{color:var(--bad)}
  .note{font-size:12px;color:var(--muted);margin:8px 0 0}
  .pick{font-size:13px;color:var(--muted);margin:4px 0 0}
  .pick b{font:500 13px var(--mono);color:var(--ink)}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  footer{margin-top:72px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}
  @media (max-width:1100px){.grid{grid-template-columns:repeat(${Math.min(cols, 2)},minmax(0,1fr))}}
  @media (max-width:720px){.wrap{padding:36px 16px 56px}.grid{grid-template-columns:1fr;gap:48px}
    .cand h2{font-size:26px}.mood{min-height:0}}
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="kicker">Design candidates</p>
    <h1>${esc(title)}</h1>
    <p class="intro">The same page in ${items.length === 1 ? 'one system' : `${items.length} systems`}.</p>
  </header>
  <main class="grid">${cards}
  </main>
  <footer>Made by gallery.mjs on ${esc(generated)}. Numbers are the worst of desktop and phone, light and dark.</footer>
</div>
<script>
  document.querySelectorAll('[data-shot]').forEach(function (fig) {
    var img = fig.querySelector('img');
    var buttons = fig.querySelectorAll('button');
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        img.src = b.dataset.src; img.alt = b.dataset.alt;
        buttons.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      });
    });
    // Start on the viewer's own scheme.
    if (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches) buttons[1].click();
  });
</script>
</body>
</html>
`;
}

async function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exit(2); }
  if (args.help || !args.systems.length) {
    console.error('usage: node gallery.mjs --systems a,b,c [--library <dir>] [--sample <file>] [--out <dir>] [--title "..."] [--preview]');
    process.exit(args.help ? 0 : 2);
  }
  let browser;
  try {
    const systems = args.systems.map((s) => resolveSystem(s, args.library));
    const sample = fs.readFileSync(args.sample, 'utf8');
    // A custom sample may load relative files (images, scripts); keep them resolving.
    const usesRelative = args.customSample && /\b(?:src|href)=["'](?![a-z]+:|#|\/\/|data:)[^"']+["']/i.test(sample);
    const baseHref = usesRelative ? pathToFileURL(path.dirname(args.sample) + path.sep).href : null;
    fs.mkdirSync(path.join(args.out, 'shots'), { recursive: true });
    browser = await launchBrowser();
    const items = [];
    for (const sys of systems) {
      const htmlName = `${sys.name}.html`;
      const htmlPath = path.join(args.out, htmlName);
      fs.writeFileSync(htmlPath, dress(sample, sys, { baseHref }));
      const url = pathToFileURL(htmlPath).href;
      const shots = {
        desktopLight: `shots/${sys.name}-desktop-light.png`,
        desktopDark: `shots/${sys.name}-desktop-dark.png`,
        phoneLight: `shots/${sys.name}-phone-light.png`,
      };
      await shoot(browser, url, 'desktop', 'light', path.join(args.out, shots.desktopLight));
      await shoot(browser, url, 'desktop', 'dark', path.join(args.out, shots.desktopDark));
      await shoot(browser, url, 'phone', 'light', path.join(args.out, shots.phoneLight));
      const check = await checkTarget(htmlPath, { browser });
      if (args.preview) {
        const dest = path.join(sys.dir, 'preview.png');
        const own = sys.fm.scheme === 'dark' ? shots.desktopDark : shots.desktopLight;
        fs.copyFileSync(path.join(args.out, own), dest);
        const kb = Math.round(fs.statSync(dest).size / 1024);
        if (kb > 400) console.error(`note: ${dest} is ${kb} KB (target under 400 KB)`);
      }
      items.push({ name: sys.name, dir: sys.dir, fm: sys.fm, html: htmlName, shots, check });
      const nums = CHECKS.map(({ id }) => `${id} ${worstCell(check.checks[id]).value}`).join(', ');
      console.log(`${sys.name.padEnd(22)} ${check.verdict.toUpperCase().padEnd(5)} ${nums}`);
    }
    const generated = new Date().toISOString().slice(0, 10);
    const title = args.title || (items.length === 1 ? 'One candidate' : `${['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six'][items.length] || items.length} candidates`);
    const galleryPath = path.join(args.out, 'gallery.html');
    fs.writeFileSync(galleryPath, galleryHtml({ title, items, generated }));
    const galleryCheck = await checkTarget(galleryPath, { browser });
    const report = {
      generated,
      title,
      sample: args.sample,
      out: args.out,
      gallery: { file: 'gallery.html', verdict: galleryCheck.verdict },
      systems: items.map((it) => ({
        name: it.name,
        dir: it.dir,
        mood: it.fm.mood ?? null,
        fits: it.fm.fits ?? [],
        family: it.fm.family ?? null,
        loud: it.fm.loud === true,
        source: it.fm.source ?? null,
        html: it.html,
        shots: it.shots,
        preview: args.preview ? path.join(it.dir, 'preview.png') : null,
        verdict: it.check.verdict,
        relaxed: it.check.relaxed,
        checks: Object.fromEntries(CHECKS.map(({ id }) => [id, { verdict: it.check.checks[id].verdict, threshold: it.check.checks[id].threshold, cells: it.check.checks[id].cells }])),
        details: it.check.modes,
      })),
    };
    fs.writeFileSync(path.join(args.out, 'report.json'), JSON.stringify(report, null, 2));
    console.log(`gallery check: ${galleryCheck.verdict.toUpperCase()}`);
    console.log(`gallery: ${galleryPath}`);
  } catch (e) {
    console.error(`gallery error: ${e.message}`);
    process.exitCode = 2;
  } finally {
    if (browser) await browser.close();
  }
}

// Run main() only when this file is the entry point. Compare real paths, so a run through a
// symlinked skill folder (the usual install) is still recognised.
function isEntry() {
  if (!process.argv[1]) return false;
  try { return fs.realpathSync(process.argv[1]) === fs.realpathSync(fileURLToPath(import.meta.url)); } catch { return false; }
}
if (isEntry()) main();
