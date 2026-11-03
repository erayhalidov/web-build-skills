#!/usr/bin/env node
/**
 * Mobile/desktop overflow + layout check for any page, with no npm dependencies.
 * Drives the Playwright-cached Chromium over CDP (Node >= 22 has WebSocket built in).
 *
 *   node mobile-overflow-check.mjs 390 https://site.tld/category/x/ https://site.tld/
 *   node mobile-overflow-check.mjs 414 https://site.tld/delivery/ --selector ".ship-table"
 *
 * Prints one JSON line per URL:
 *   { vw, scrollWidth, offenders, cellLayout: {...} }
 * Pass criteria: offenders === 0 and documentElement.scrollWidth === width.
 * With --selector it also reports whether a wide table has switched to the stacked-card layout
 * (thead display:none, rows display:block, first cell display:flex + its ::before label).
 *
 * Set CHROME=/path/to/chrome if the Playwright cache path differs.
 */
import { spawn } from 'node:child_process';

const CHROME = process.env.CHROME
  || (await import('node:fs')).readdirSync('/root/.cache/ms-playwright')
      .filter(d => d.startsWith('chromium-'))
      .sort().reverse().map(d => `/root/.cache/ms-playwright/${d}/chrome-linux64/chrome`)[0];

const args = process.argv.slice(2);
const WIDTH = parseInt(args[0] || '390', 10);
const selIdx = args.indexOf('--selector');
const SELECTOR = selIdx >= 0 ? args[selIdx + 1] : null;
const URLS = args.slice(1).filter((a, i) => a && !a.startsWith('--') && (selIdx < 0 || i !== selIdx));
const PORT = 9333 + Math.floor(Math.random() * 200);
const sleep = ms => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', '--no-sandbox', '--disable-gpu',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=/tmp/cdp-overflow-${Date.now()}`, 'about:blank'],
  { stdio: 'ignore' });

async function wsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch (e) { /* not up yet */ }
    await sleep(250);
  }
  throw new Error('chrome devtools not reachable');
}

function cdp(ws) {
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { resolve, reject } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
    }
  });
  return (method, params = {}) => new Promise((resolve, reject) => {
    const mid = ++id;
    pending.set(mid, { resolve, reject });
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
}

const DIAG = `(() => {
  const vw = document.documentElement.clientWidth;
  const out = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.visibility === 'hidden' || cs.display === 'none') return;
    if (r.right > vw + 1) {
      let s = el.tagName.toLowerCase();
      if (el.className && typeof el.className === 'string') s += '.' + el.className.trim().split(/\\s+/).slice(0, 3).join('.');
      out.push({ sel: s, w: Math.round(r.width), right: Math.round(r.right),
                 text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 60) });
    }
  });
  return JSON.stringify({ vw, scrollWidth: document.documentElement.scrollWidth,
                          count: out.length, offenders: out.slice(0, 20) });
})()`;

const LAYOUT = sel => `(() => {
  const t = document.querySelector('${sel}');
  if (!t) return JSON.stringify({ found: false });
  const head = t.querySelector('thead'), row = t.querySelector('tbody tr'), cell = row && row.querySelector('td');
  const wrap = t.closest('.table-wrap') || t.parentElement;
  return JSON.stringify({ found: true,
    thead: head ? getComputedStyle(head).display : null,
    row: row ? getComputedStyle(row).display : null,
    cell: cell ? getComputedStyle(cell).display : null,
    cellLabel: cell ? getComputedStyle(cell, '::before').content : null,
    tableWidth: Math.round(t.getBoundingClientRect().width),
    wrapScroll: wrap.scrollWidth, wrapClient: wrap.clientWidth });
})()`;

(async () => {
  const ws = new WebSocket(await wsUrl());
  await new Promise(r => ws.addEventListener('open', r));
  const send = cdp(ws);
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: WIDTH, height: 900, deviceScaleFactor: 1, mobile: WIDTH < 500 });

  for (const url of URLS) {
    await send('Page.navigate', { url });
    await sleep(3500);
    const diag = await send('Runtime.evaluate', { expression: DIAG, returnByValue: true });
    const result = JSON.parse(diag.result.value);
    if (SELECTOR) {
      const lay = await send('Runtime.evaluate', { expression: LAYOUT(SELECTOR), returnByValue: true });
      result.cellLayout = JSON.parse(lay.result.value);
    }
    console.log(url, JSON.stringify(result));
  }
  ws.close();
  chrome.kill();
  process.exit(0);
})().catch(e => { console.error('ERR', e.message); chrome.kill(); process.exit(1); });
