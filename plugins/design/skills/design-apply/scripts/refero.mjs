#!/usr/bin/env node
// Read Refero Styles (styles.refero.design), a public library of real website styles.
//
//   node refero.mjs list                 styles on the home page: title and link
//   node refero.mjs get <link>           one style as markdown: colors, type, radius,
//                                        spacing, gradients and the written notes
//
// The site has no API. Each style page embeds its data in the Next.js payload; this
// script decodes that payload. If the site changes, open the page in a browser instead.

const BASE = 'https://styles.refero.design';

async function fetchText(url) {
  const res = await fetch(url, { headers: { 'user-agent': 'design-find/1.0' }, signal: AbortSignal.timeout(20000) });
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.text();
}

function payload(html) {
  const out = [];
  const re = /self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)/g;
  let m;
  while ((m = re.exec(html))) out.push(JSON.parse(`"${m[1]}"`));
  return out.join('');
}

function textChunks(full) {
  const buf = Buffer.from(full, 'utf8');
  const s = buf.toString('latin1');
  const re = /([0-9a-f]{1,4}):T([0-9a-f]+),/g;
  const out = [];
  let m;
  while ((m = re.exec(s))) {
    const start = m.index + m[0].length;
    const n = parseInt(m[2], 16);
    const text = buf.subarray(start, start + n).toString('utf8');
    if (!text.startsWith('{')) out.push(text);
  }
  return out;
}

function rawData(full) {
  const i = full.indexOf('"raw":{');
  if (i < 0) return null;
  let depth = 0;
  for (let j = i + 6; j < full.length; j++) {
    const c = full[j];
    if (c === '"') { j++; while (full[j] !== '"') { if (full[j] === '\\') j++; j++; } continue; }
    if (c === '{') depth++;
    if (c === '}' && --depth === 0) return JSON.parse(full.slice(i + 6, j + 1));
  }
  return null;
}

function title(html) {
  const m = html.match(/<title>([^<]*)<\/title>/);
  return m ? m[1].replace(/\s*\|\s*Refero Styles\s*$/, '').replace(/&amp;/g, '&') : '';
}

async function list() {
  const html = await fetchText(BASE + '/');
  const ids = [...new Set([...html.matchAll(/href="(\/style\/[0-9a-f-]+)"/g)].map((m) => m[1]))];
  const rows = await Promise.all(ids.map(async (id) => {
    try {
      const page = await fetchText(BASE + id);
      return `${title(page).padEnd(40)} ${BASE}${id}`;
    } catch {
      return `${'?'.padEnd(40)} ${BASE}${id}`;
    }
  }));
  console.log(rows.join('\n'));
}

async function get(link) {
  const url = link.startsWith('http') ? link : `${BASE}/style/${link}`;
  const html = await fetchText(url);
  const full = payload(html);
  const raw = rawData(full) || {};
  const lines = [`# ${title(html)}`, '', `Source: ${url}`, ''];
  const colors = (raw.colors?.tokens || []).slice(0, 14);
  if (colors.length) {
    lines.push('## Colors (most used first)');
    for (const c of colors) lines.push(`- ${c.hex}  ${(c.properties || []).slice(0, 3).join(', ')}  in ${(c.contexts || []).slice(0, 4).join(', ')}`);
    lines.push('');
  }
  const ty = raw.typography;
  if (ty) {
    lines.push('## Type');
    for (const f of ty.fonts || []) lines.push(`- ${f.family} (${f.source}), weights ${(f.weights || []).join('/')}`);
    if (ty.scale) lines.push(`- scale: base ${ty.scale.base}px, ${ty.scale.name} (${ty.scale.ratio})`);
    for (const s of (ty.steps || []).slice(0, 10)) lines.push(`- ${s.size}px ${s.family} ${s.weight}${s.lineHeight ? ` lh ${s.lineHeight}` : ''}${s.letterSpacing ? ` ls ${s.letterSpacing}` : ''}  ${(s.contexts || []).slice(0, 3).join(', ')}`);
    lines.push('');
  }
  const radii = raw.shapes?.radii || [];
  if (radii.length) lines.push('## Radius', radii.map((r) => `- ${r.value}px in ${(r.contexts || []).join(', ')}`).join('\n'), '');
  const shadows = raw.shapes?.shadows || [];
  if (shadows.length) lines.push('## Shadows', shadows.slice(0, 5).map((s) => `- ${s.value || JSON.stringify(s)}`).join('\n'), '');
  const sp = (raw.spacing?.tokens || []).map((t) => t.value);
  if (sp.length) lines.push('## Spacing', `- ${[...new Set(sp)].sort((a, b) => a - b).join(', ')} px`, '');
  const gr = raw.gradients || [];
  if (gr.length) lines.push('## Gradients', gr.slice(0, 4).map((g) => `- ${g.value}`).join('\n'), '');
  const notes = textChunks(full);
  if (notes.length) lines.push('## Notes from the style page', '', ...notes.map((n) => n.trim() + '\n'));
  console.log(lines.join('\n'));
}

const [cmd, arg] = process.argv.slice(2);
try {
  if (cmd === 'list') await list();
  else if (cmd === 'get' && arg) await get(arg);
  else { console.error('usage: node refero.mjs list | get <link>'); process.exit(2); }
} catch (e) {
  console.error(String(e.message || e));
  process.exit(2);
}
