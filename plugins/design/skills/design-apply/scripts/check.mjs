#!/usr/bin/env node
// check.mjs: measures whether a page looks generic or noisy.
//
//   node check.mjs <file.html|url> [--json] [--out report.json]
//
// Renders the page in headless Chromium at desktop (1440x900) and phone (390x844), each in
// light and dark color scheme, and measures five things:
//   colors    chromatic colors that carry no meaning (not the accent or a state color)
//   words     visible words in the first viewport
//   chips     inline code chips per screen
//   contrast  text that fails WCAG AA against its background
//   boxes     bordered or filled boxes per screen
// Exit code 0 when nothing fails (warnings allowed), 1 on any fail, 2 on error.
//
// Overrides, in the page: <meta name="design-check" content="loud,cards">
//   loud   relaxes colors to pass <= 6 (a deliberately loud brand)
//   cards  relaxes boxes to pass <= 12 (cards are the content)

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { launchBrowser } from './lib/browser.mjs';

export const MODES = [
  { id: 'desktop-light', device: 'desktop', scheme: 'light' },
  { id: 'desktop-dark', device: 'desktop', scheme: 'dark' },
  { id: 'phone-light', device: 'phone', scheme: 'light' },
  { id: 'phone-dark', device: 'phone', scheme: 'dark' },
];

export const DEVICES = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  phone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
};

// value <= pass is a pass, value <= warn is a warning, anything above fails.
export function thresholds(check, device, overrides = []) {
  switch (check) {
    case 'colors': return overrides.includes('loud') ? { pass: 6, warn: 8 } : { pass: 1, warn: 2 };
    case 'words': return device === 'phone' ? { pass: 70, warn: 110 } : { pass: 90, warn: 140 };
    case 'chips': return { pass: 3, warn: 6 };
    case 'contrast': return { pass: 0, warn: 0 };
    case 'boxes': return overrides.includes('cards') ? { pass: 12, warn: 15 } : { pass: 3, warn: 5 };
    default: throw new Error(`unknown check ${check}`);
  }
}

export const CHECKS = [
  { id: 'colors', label: 'colors without meaning' },
  { id: 'words', label: 'words in first view' },
  { id: 'chips', label: 'code chips / screen' },
  { id: 'contrast', label: 'contrast fails (AA)' },
  { id: 'boxes', label: 'boxes / screen' },
];

const RANK = { pass: 0, warn: 1, fail: 2 };

function grade(value, t) {
  if (value <= t.pass) return 'pass';
  if (value <= t.warn) return 'warn';
  return 'fail';
}

function thresholdText(check, overrides) {
  const d = thresholds(check, 'desktop', overrides);
  const p = thresholds(check, 'phone', overrides);
  if (check === 'contrast') return 'pass 0, else fail';
  const one = (t) => (t.warn === t.pass + 1 ? `pass <=${t.pass}, warn ${t.warn}, fail >=${t.warn + 1}` : `pass <=${t.pass}, warn <=${t.warn}, fail >${t.warn}`);
  if (d.pass === p.pass && d.warn === p.warn) return one(d);
  return `pass <=${d.pass}, warn <=${d.warn}, fail >${d.warn}; phone ${p.pass}/${p.warn}`;
}

// Everything below runs inside the page. It must be self-contained.
function measureInPage({ vw, vh }) {
  window.scrollTo(0, 0);
  const html = document.documentElement;
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const colorCache = new Map();

  // Any CSS color string -> [r, g, b, a] with rgb 0-255 and a 0-1.
  function rgba(str) {
    if (!str) return null;
    if (colorCache.has(str)) return colorCache.get(str);
    let out = null;
    const m = str.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const a = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4]);
      out = [+m[1], +m[2], +m[3], a];
    } else if (str !== 'none' && !str.startsWith('url(')) {
      const sentinel = 'rgba(1, 2, 3, 0.5)';
      cx.fillStyle = sentinel;
      const before = cx.fillStyle;
      cx.fillStyle = str;
      if (cx.fillStyle !== before || str === sentinel) {
        cx.clearRect(0, 0, 1, 1);
        cx.fillRect(0, 0, 1, 1);
        const d = cx.getImageData(0, 0, 1, 1).data;
        out = [d[0], d[1], d[2], d[3] / 255];
      }
    }
    colorCache.set(str, out);
    return out;
  }

  const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  function oklab([r, g, b]) {
    const R = lin(r), G = lin(g), B = lin(b);
    const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B);
    const m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B);
    const s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B);
    const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
    const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
    const Bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
    const C = Math.hypot(A, Bb);
    let H = (Math.atan2(Bb, A) * 180) / Math.PI;
    if (H < 0) H += 360;
    return { L, a: A, b: Bb, C, H };
  }
  const dE = (p, q) => Math.hypot(p.L - q.L, p.a - q.a, p.b - q.b);
  const hex = ([r, g, b]) => '#' + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  const over = (top, base) => {
    const a = top[3];
    return [0, 1, 2].map((i) => top[i] * a + base[i] * (1 - a));
  };
  function luminance([r, g, b]) { return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b); }
  function ratio(f, b) {
    const L1 = luminance(f), L2 = luminance(b);
    return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
  }

  function sel(el) {
    const parts = [];
    let n = el;
    for (let i = 0; i < 3 && n && n.nodeType === 1 && n !== html; i++) {
      let s = n.tagName.toLowerCase();
      if (n.id) { parts.unshift(`${s}#${n.id}`); break; }
      const cls = [...n.classList].slice(0, 2);
      if (cls.length) s += '.' + cls.join('.');
      parts.unshift(s);
      n = n.parentElement;
    }
    return parts.join(' > ');
  }

  const csCache = new Map();
  const cs = (el) => { let c = csCache.get(el); if (!c) { c = getComputedStyle(el); csCache.set(el, c); } return c; };

  const darkCanvas = matchMedia('(prefers-color-scheme: dark)').matches && /dark/.test(getComputedStyle(html).colorScheme || '');
  const canvasBg = darkCanvas ? [18, 18, 18] : [255, 255, 255];

  // Effective background behind an element: composite its own and its ancestors' colors.
  const bgCache = new Map();
  function effBg(el) {
    if (!el) return { rgb: canvasBg, unknown: false };
    if (bgCache.has(el)) return bgCache.get(el);
    const layers = [];
    let unknown = false;
    let base = canvasBg;
    let node = el;
    while (node && node.nodeType === 1) {
      const s = cs(node);
      if (s.backgroundImage && s.backgroundImage !== 'none') { unknown = true; break; }
      const c = rgba(s.backgroundColor);
      if (c && c[3] > 0) {
        if (c[3] >= 0.999) { base = c.slice(0, 3); break; }
        layers.push(c);
      }
      node = node.parentElement;
    }
    let rgb = base;
    for (let i = layers.length - 1; i >= 0; i--) rgb = over(layers[i], rgb);
    const out = { rgb, unknown };
    bgCache.set(el, out);
    return out;
  }

  function opacityChain(el) {
    let o = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) o *= parseFloat(cs(n).opacity || '1');
    return o;
  }

  const SKIP_TAGS = new Set(['IMG', 'VIDEO', 'CANVAS', 'PICTURE', 'IFRAME', 'OBJECT', 'EMBED', 'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'META', 'LINK', 'TITLE', 'SOURCE', 'TRACK', 'BR', 'WBR']);
  const SVG_SHAPES = new Set(['path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'tspan', 'use']);
  const all = [html, ...document.querySelectorAll('body, body *')];
  const visibleOpts = { opacityProperty: true, visibilityProperty: true, contentVisibilityAuto: true };
  const isVisible = (el) => {
    if (el === html) return true;
    if (el.checkVisibility && !el.checkVisibility(visibleOpts)) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const hasText = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && /[\p{L}\p{N}]/u.test(n.textContent));
  const SIDES = ['Top', 'Right', 'Bottom', 'Left'];

  // ---- Meaning colors from :root custom properties ----
  const meaningNames = new Set(['--accent', '--accent-ink', '--accent-text', '--ok', '--warn', '--bad']);
  const meaningRe = /^--(meaning-|state-|flow-|mark)/;
  const rootCs = getComputedStyle(html);
  for (let i = 0; i < rootCs.length; i++) if (meaningRe.test(rootCs[i])) meaningNames.add(rootCs[i]);
  const scan = (rules) => {
    for (const r of rules) {
      try {
        if (r.style) for (let i = 0; i < r.style.length; i++) if (meaningRe.test(r.style[i])) meaningNames.add(r.style[i]);
        if (r.cssRules) scan(r.cssRules);
      } catch { /* ignore */ }
    }
  };
  for (const sh of document.styleSheets) { try { scan(sh.cssRules); } catch { /* cross-origin */ } }
  const wrap = document.createElement('div');
  wrap.style.cssText = 'color: rgb(1, 2, 3); position: absolute; width: 0; height: 0; overflow: hidden';
  const probe = document.createElement('span');
  wrap.appendChild(probe);
  html.appendChild(wrap);
  const meaning = [];
  const base = [];
  const resolveVar = (name) => {
    probe.style.color = '';
    probe.style.color = `var(${name})`;
    const v = getComputedStyle(probe).color;
    if (!rootCs.getPropertyValue(name).trim() || v === 'rgb(1, 2, 3)') return null;
    const c = rgba(v);
    if (!c || c[3] === 0) return null;
    return c[3] < 1 ? over(c, effBg(document.body).rgb) : c.slice(0, 3);
  };
  // The base palette (page, raised area, text, hairline) is not decoration even when tinted.
  for (const name of ['--bg', '--surface', '--ink', '--muted', '--line']) {
    const solid = resolveVar(name);
    if (solid) base.push({ name, hex: hex(solid), lab: oklab(solid) });
  }
  for (const name of meaningNames) {
    const solid = resolveVar(name);
    if (solid) meaning.push({ name, hex: hex(solid), lab: oklab(solid) });
  }
  wrap.remove();

  // ---- Painted colors ----
  const painted = new Map();
  function paint(str, el, what, baseEl) {
    const c = rgba(str);
    if (!c || c[3] <= 0.02) return;
    const solid = c[3] < 0.999 ? over(c, effBg(baseEl).rgb) : c.slice(0, 3);
    const key = hex(solid);
    const p = painted.get(key);
    if (p) p.count++;
    else painted.set(key, { hex: key, rgb: solid, count: 1, sample: `${sel(el)} (${what})` });
  }
  function borders(s, el, baseEl, pseudo = '') {
    for (const side of SIDES) {
      const w = parseFloat(s[`border${side}Width`]);
      const st = s[`border${side}Style`];
      if (w > 0 && st !== 'none' && st !== 'hidden') paint(s[`border${side}Color`], el, `border${pseudo}`, baseEl);
    }
  }
  for (const el of all) {
    if (SKIP_TAGS.has(el.tagName)) continue;
    if (!isVisible(el)) continue;
    if (el instanceof SVGElement) {
      const tag = el.tagName.toLowerCase();
      if (!SVG_SHAPES.has(tag)) continue;
      const s = cs(el);
      const host = el.closest('svg')?.parentElement || document.body;
      if (s.fill && s.fill !== 'none' && !s.fill.startsWith('url(')) paint(s.fill, el, 'fill', host);
      if (s.stroke && s.stroke !== 'none' && !s.stroke.startsWith('url(') && parseFloat(s.strokeWidth) > 0) paint(s.stroke, el, 'stroke', host);
      continue;
    }
    const s = cs(el);
    if (el !== html) paint(s.backgroundColor, el, 'background', el.parentElement);
    else paint(s.backgroundColor, el, 'background', null);
    borders(s, el, el);
    if (hasText(el)) paint(s.color, el, 'text', el);
    for (const pseudo of ['::before', '::after']) {
      const p = getComputedStyle(el, pseudo);
      if (!p.content || p.content === 'none' || p.content === 'normal' || p.display === 'none') continue;
      paint(p.backgroundColor, el, `background ${pseudo}`, el);
      borders(p, el, el, ` ${pseudo}`);
      if (/^["'].*[\p{L}\p{N}]/u.test(p.content)) paint(p.color, el, `text ${pseudo}`, el);
    }
  }
  const chromatic = [];
  const meaningful = [];
  for (const p of painted.values()) {
    const lab = oklab(p.rgb);
    if (lab.C < 0.035) continue;
    const hit = meaning.find((m) => {
      if (dE(lab, m.lab) < 0.05) return true;
      if (m.lab.C < 0.035) return false;
      let dh = Math.abs(lab.H - m.lab.H);
      if (dh > 180) dh = 360 - dh;
      return dh <= 12;
    });
    const baseHit = base.find((m) => dE(lab, m.lab) < 0.05);
    if (baseHit) { meaningful.push({ hex: p.hex, token: baseHit.name, count: p.count }); continue; }
    if (hit) meaningful.push({ hex: p.hex, token: hit.name, count: p.count });
    else chromatic.push({ ...p, lab });
  }
  chromatic.sort((a, b) => b.count - a.count);
  const clusters = [];
  for (const c of chromatic) {
    const k = clusters.find((q) => dE(q.lab, c.lab) < 0.07);
    if (k) { k.count += c.count; k.members.push(c.hex); }
    else clusters.push({ hex: c.hex, lab: c.lab, count: c.count, sample: c.sample, members: [c.hex] });
  }

  // ---- Words in the first viewport ----
  let words = 0;
  const range = document.createRange();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const t = n.textContent;
    if (!/[\p{L}\p{N}]/u.test(t)) continue;
    const p = n.parentElement;
    if (!p || SKIP_TAGS.has(p.tagName)) continue;
    if (p.checkVisibility && !p.checkVisibility(visibleOpts)) continue;
    if (opacityChain(p) < 0.05) continue;
    range.selectNodeContents(n);
    const r = range.getBoundingClientRect();
    if (r.width <= 1 || r.height <= 1) continue;
    if (r.bottom <= 0 || r.top >= vh || r.right <= 0 || r.left >= vw) continue;
    const toks = [...t.matchAll(/\S+/g)].filter((m) => /[\p{L}\p{N}]/u.test(m[0]));
    if (r.top >= 0 && r.bottom <= vh && r.left >= 0 && r.right <= vw) { words += toks.length; continue; }
    for (const m of toks) {
      range.setStart(n, m.index);
      range.setEnd(n, m.index + m[0].length);
      const q = range.getBoundingClientRect();
      if (q.width > 0 && q.top < vh && q.bottom > 0 && q.left < vw && q.right > 0) words++;
    }
  }

  // ---- Screens ----
  const docH = Math.max(html.scrollHeight, document.body ? document.body.scrollHeight : 0, vh);
  const screens = Math.max(1, Math.ceil((docH - 1) / vh));
  const perScreen = (items) => {
    const counts = new Array(screens).fill(0);
    const lists = counts.map(() => []);
    for (const it of items) {
      const h = it.bottom - it.top;
      const need = 0.5 * Math.min(h, vh);
      for (let i = 0; i < screens; i++) {
        const ov = Math.min(it.bottom, (i + 1) * vh) - Math.max(it.top, i * vh);
        if (ov > 0 && ov >= need) { counts[i]++; lists[i].push(it); }
      }
    }
    let best = 0;
    for (let i = 1; i < screens; i++) if (counts[i] > counts[best]) best = i;
    return { max: counts[best], screen: best, counts, items: lists[best] };
  };
  const docRect = (el) => {
    const r = el.getBoundingClientRect();
    return { top: r.top + scrollY, bottom: r.bottom + scrollY, w: r.width, h: r.height };
  };

  // ---- Code chips ----
  const fontMono = (rootCs.getPropertyValue('--font-mono') || '').split(',')[0].trim().replace(/["']/g, '').toLowerCase();
  const monoRe = /mono|courier|consolas|menlo|monaco|\bcode\b|fira code|jetbrains|inconsolata/i;
  const isMono = (ff) => {
    const first = ff.split(',')[0].trim().replace(/["']/g, '').toLowerCase();
    return monoRe.test(first) || (fontMono && first === fontMono);
  };
  const chips = [];
  for (const el of all) {
    if (el === html || el === document.body || el instanceof SVGElement) continue;
    const tag = el.tagName;
    let chip = false;
    if (tag === 'CODE' || tag === 'KBD' || tag === 'SAMP') {
      chip = !el.closest('pre') && !el.parentElement.closest('code, kbd, samp');
    } else {
      const s = cs(el);
      if (s.display.startsWith('inline') && hasText(el) && isMono(s.fontFamily) && !el.parentElement.closest('code, kbd, samp, pre')) {
        const own = rgba(s.backgroundColor);
        let filled = false;
        if (own && own[3] > 0.05) {
          const mine = oklab(over(own, effBg(el.parentElement).rgb));
          filled = dE(mine, oklab(effBg(el.parentElement).rgb)) > 0.01;
        }
        const sides = SIDES.filter((side) => parseFloat(s[`border${side}Width`]) >= 1 && s[`border${side}Style`] !== 'none' && (rgba(s[`border${side}Color`]) || [0, 0, 0, 0])[3] > 0.1).length;
        chip = filled || sides >= 3;
      }
    }
    if (!chip || !isVisible(el)) continue;
    chips.push({ ...docRect(el), sel: sel(el), text: el.textContent.trim().slice(0, 30) });
  }

  // ---- Contrast ----
  const fails = [];
  let unknown = 0;
  let checked = 0;
  for (const el of all) {
    if (el === html || el instanceof SVGElement || SKIP_TAGS.has(el.tagName)) continue;
    if (!hasText(el) || el.disabled) continue;
    if (el.checkVisibility && !el.checkVisibility(visibleOpts)) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 1 || r.height <= 1) continue;
    const s = cs(el);
    const fg = rgba(s.color);
    if (!fg) continue;
    const alpha = fg[3] * opacityChain(el);
    if (alpha <= 0.02) continue;
    const bg = effBg(el);
    if (bg.unknown) { unknown++; continue; }
    checked++;
    const solid = over([fg[0], fg[1], fg[2], alpha], bg.rgb);
    const ratioV = ratio(solid, bg.rgb);
    const size = parseFloat(s.fontSize);
    const weight = parseInt(s.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3 : 4.5;
    if (ratioV + 1e-9 < need) {
      const text = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
      fails.push({ sel: sel(el), text: text.slice(0, 40), ratio: Math.round(ratioV * 100) / 100, need, fg: hex(solid), bg: hex(bg.rgb) });
    }
  }
  fails.sort((a, b) => a.ratio / a.need - b.ratio / b.need);

  // ---- Boxes ----
  const BOX_SKIP = new Set(['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON', 'OPTION', 'IMG', 'VIDEO', 'CANVAS', 'PICTURE', 'IFRAME', 'OBJECT', 'EMBED', 'HR']);
  const boxes = [];
  const parseShadows = (str) => {
    if (!str || str === 'none') return [];
    const parts = [];
    let depth = 0, cur = '';
    for (const ch of str) {
      if (ch === '(') depth++;
      if (ch === ')') depth--;
      if (ch === ',' && depth === 0) { parts.push(cur); cur = ''; } else cur += ch;
    }
    parts.push(cur);
    return parts.map((p) => {
      const colorM = p.match(/(rgba?\([^)]*\)|oklch\([^)]*\)|oklab\([^)]*\)|color\([^)]*\)|#[0-9a-f]{3,8})/i);
      const nums = p.replace(colorM ? colorM[0] : '', '').match(/-?[\d.]+px/g) || [];
      const [x = 0, y = 0, blur = 0, spread = 0] = nums.map(parseFloat);
      const c = colorM ? rgba(colorM[0]) : [0, 0, 0, 1];
      return { x, y, blur, spread, alpha: c ? c[3] : 1, inset: /inset/.test(p) };
    });
  };
  for (const el of all) {
    if (el === html || el === document.body || el instanceof SVGElement) continue;
    if (BOX_SKIP.has(el.tagName) || SKIP_TAGS.has(el.tagName)) continue;
    if (el.getAttribute('role') === 'button') continue;
    if (cs(el).display === 'inline') continue;
    if (!isVisible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width * r.height < 2500) continue;
    if (el.tagName === 'A' && r.height <= 64) continue;
    const s = cs(el);
    const why = [];
    const sides = SIDES.filter((side) => {
      const st = s[`border${side}Style`];
      const c = rgba(s[`border${side}Color`]);
      return parseFloat(s[`border${side}Width`]) >= 1 && st !== 'none' && st !== 'hidden' && c && c[3] > 0.1;
    }).length;
    if (sides >= 3) why.push(`border ${sides} sides`);
    const shadows = parseShadows(s.boxShadow);
    if (shadows.some((sh) => sh.x === 0 && sh.y === 0 && sh.blur === 0 && sh.spread > 0 && sh.alpha > 0.1)) why.push('ring shadow');
    const radius = Math.max(...['TopLeft', 'TopRight', 'BottomLeft', 'BottomRight'].map((k) => parseFloat(s[`border${k}Radius`]) || 0));
    const own = rgba(s.backgroundColor);
    if (radius >= 4 && own && own[3] > 0.05 && (!s.backgroundImage || s.backgroundImage === 'none')) {
      const parentBg = effBg(el.parentElement);
      const mine = over(own, parentBg.rgb);
      if (dE(oklab(mine), oklab(parentBg.rgb)) > 0.012) why.push('filled card');
    }
    if (radius >= 4 && shadows.some((sh) => !sh.inset && (sh.blur > 0 || sh.y !== 0) && sh.alpha > 0.05)) why.push('lifted card');
    if (!why.length) continue;
    boxes.push({ ...docRect(el), sel: sel(el), why: why.join(', ') });
  }

  const meta = document.querySelector('meta[name="design-check"]');
  const overrides = meta ? (meta.getAttribute('content') || '').split(/[\s,]+/).map((x) => x.trim().toLowerCase()).filter(Boolean) : [];

  const boxStat = perScreen(boxes);
  const chipStat = perScreen(chips);
  return {
    overrides,
    screens,
    colors: {
      count: clusters.length,
      clusters: clusters.map(({ hex: h, count, sample, members }) => ({ hex: h, count, sample, members })),
      meaning: meaning.map(({ name, hex: h }) => ({ name, hex: h })),
      base: base.map(({ name, hex: h }) => ({ name, hex: h })),
      meaningful,
    },
    words,
    chips: { max: chipStat.max, screen: chipStat.screen, total: chips.length, items: chipStat.items.slice(0, 8).map(({ sel: s, text }) => ({ sel: s, text })) },
    contrast: { fails: fails.length, checked, unknown, worst: fails.slice(0, 8) },
    boxes: { max: boxStat.max, screen: boxStat.screen, counts: boxStat.counts, items: boxStat.items.slice(0, 8).map(({ sel: s, why, w, h }) => ({ sel: s, why, size: `${Math.round(w)}x${Math.round(h)}` })) },
  };
}

export function toUrl(target) {
  if (/^(https?|file|data):/i.test(target)) return target;
  const abs = path.resolve(target);
  if (!fs.existsSync(abs)) throw new Error(`no such file: ${target}`);
  return pathToFileURL(abs).href;
}

async function measureMode(browser, url, mode) {
  const dev = DEVICES[mode.device];
  const context = await browser.newContext({ ...dev, colorScheme: mode.scheme, reducedMotion: 'reduce' });
  try {
    const page = await context.newPage();
    try {
      await page.goto(url, { waitUntil: 'load', timeout: 30000 });
    } catch (e) {
      if (!/Timeout/i.test(String(e.message))) throw e;
    }
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 4000))]);
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    });
    return await page.evaluate(measureInPage, { vw: dev.viewport.width, vh: dev.viewport.height });
  } finally {
    await context.close();
  }
}

// Runs every mode on one target. Pass an open `browser` to reuse it (the gallery does).
export async function checkTarget(target, { browser } = {}) {
  const url = toUrl(target);
  const own = !browser;
  const b = browser || (await launchBrowser());
  try {
    const modes = {};
    for (const mode of MODES) modes[mode.id] = await measureMode(b, url, mode);
    return summarize(target, url, modes);
  } finally {
    if (own) await b.close();
  }
}

const VALUE = {
  colors: (m) => m.colors.count,
  words: (m) => m.words,
  chips: (m) => m.chips.max,
  contrast: (m) => m.contrast.fails,
  boxes: (m) => m.boxes.max,
};

function summarize(target, url, modes) {
  const overrides = [...new Set(Object.values(modes).flatMap((m) => m.overrides))].filter((o) => o === 'loud' || o === 'cards');
  const checks = {};
  let verdict = 'pass';
  for (const { id, label } of CHECKS) {
    const cells = {};
    let worst = 'pass';
    for (const mode of MODES) {
      const value = VALUE[id](modes[mode.id]);
      const g = grade(value, thresholds(id, mode.device, overrides));
      cells[mode.id] = { value, grade: g };
      if (RANK[g] > RANK[worst]) worst = g;
    }
    checks[id] = { label, verdict: worst, threshold: thresholdText(id, overrides), cells };
    if (RANK[worst] > RANK[verdict]) verdict = worst;
  }
  const relaxed = [];
  if (overrides.includes('loud')) relaxed.push('colors (loud)');
  if (overrides.includes('cards')) relaxed.push('boxes (cards)');
  return { target, url, verdict, overrides, relaxed, checks, modes };
}

// The mode where a check scores worst, for listing offenders.
function worstMode(result, id) {
  let best = MODES[0].id;
  for (const m of MODES) if (result.checks[id].cells[m.id].value > result.checks[id].cells[best].value) best = m.id;
  return best;
}

export function formatReport(result) {
  const out = [];
  const pad = (s, n) => String(s).padEnd(n);
  const lpad = (s, n) => String(s).padStart(n);
  out.push(`design check: ${result.target}`);
  if (result.relaxed.length) out.push(`relaxed by <meta name="design-check">: ${result.relaxed.join(', ')}`);
  out.push('');
  const cols = MODES.map((m) => m.id);
  out.push(pad('check', 24) + cols.map((c) => lpad(c, 14)).join('') + '   verdict');
  for (const { id } of CHECKS) {
    const c = result.checks[id];
    const cells = cols.map((m) => {
      const cell = c.cells[m];
      const mark = cell.grade === 'fail' ? ' !' : cell.grade === 'warn' ? ' *' : '  ';
      return lpad(cell.value + mark, 14);
    });
    out.push(pad(c.label, 24) + cells.join('') + `   ${c.verdict.toUpperCase().padEnd(4)}  (${c.threshold})`);
  }
  out.push(`${' '.repeat(24)}* warn  ! fail`);
  out.push('');
  out.push(`overall: ${result.verdict.toUpperCase()}`);

  const lines = [];
  const colorsMode = worstMode(result, 'colors');
  const col = result.modes[colorsMode].colors;
  if (col.count > 0) {
    lines.push(`colors without meaning (${colorsMode}):`);
    for (const k of col.clusters.slice(0, 8)) lines.push(`  ${k.hex}  x${k.count}  e.g. ${k.sample}`);
    if (!col.meaning.length) lines.push('  (no --accent / --ok / --warn / --bad found on :root, so no color counts as meaningful)');
  }
  const seen = new Map();
  const cf = [];
  for (const m of MODES) {
    for (const f of result.modes[m.id].contrast.worst) {
      const key = `${f.sel}|${f.fg}|${f.bg}|${f.need}`;
      const prev = seen.get(key);
      if (prev) { if (!prev.modes.includes(m.id)) prev.modes.push(m.id); continue; }
      const item = { ...f, modes: [m.id] };
      seen.set(key, item);
      cf.push(item);
    }
  }
  cf.sort((a, b) => a.ratio / a.need - b.ratio / b.need);
  if (cf.length) {
    lines.push('contrast fails (worst first):');
    for (const f of cf.slice(0, 8)) {
      const where = f.modes.length === MODES.length ? 'all modes' : f.modes.join(', ');
      lines.push(`  ${f.ratio.toFixed(2)}:1 (need ${f.need})  ${f.sel}  "${f.text}"  ${f.fg} on ${f.bg}  [${where}]`);
    }
  }
  const unknown = Math.max(...MODES.map((m) => result.modes[m.id].contrast.unknown));
  if (unknown) lines.push(`contrast: ${unknown} text elements skipped (background image or gradient behind them)`);
  if (result.checks.boxes.verdict !== 'pass') {
    const bm = worstMode(result, 'boxes');
    const b = result.modes[bm].boxes;
    lines.push(`boxes: ${b.max} on screen ${b.screen + 1} (${bm}):`);
    for (const it of b.items) lines.push(`  ${it.sel}  ${it.size}  ${it.why}`);
  }
  if (result.checks.chips.verdict !== 'pass') {
    const cm = worstMode(result, 'chips');
    const c = result.modes[cm].chips;
    lines.push(`code chips: ${c.max} on screen ${c.screen + 1} (${cm}):`);
    for (const it of c.items) lines.push(`  ${it.sel}  "${it.text}"`);
  }
  if (result.checks.words.verdict !== 'pass') {
    const wm = worstMode(result, 'words');
    lines.push(`words: ${result.modes[wm].words} visible in the first view (${wm}); cut copy or push detail below the fold`);
  }
  if (lines.length) out.push('', ...lines);
  return out.join('\n');
}

function parseArgs(argv) {
  const args = { json: false, out: null, target: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--out') args.out = argv[++i];
    else if (a === '-h' || a === '--help') args.help = true;
    else if (!args.target) args.target = a;
    else throw new Error(`unexpected argument: ${a}`);
  }
  return args;
}

async function main() {
  let args;
  try { args = parseArgs(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exit(2); }
  if (args.help || !args.target) {
    console.error('usage: node check.mjs <file.html|url> [--json] [--out report.json]');
    process.exit(args.help ? 0 : 2);
  }
  try {
    const result = await checkTarget(args.target);
    if (args.out) fs.writeFileSync(args.out, JSON.stringify(result, null, 2));
    console.log(args.json ? JSON.stringify(result, null, 2) : formatReport(result));
    process.exit(result.verdict === 'fail' ? 1 : 0);
  } catch (e) {
    console.error(`design-check error: ${e.message}`);
    process.exit(2);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main();
