#!/usr/bin/env python3
"""Tab Rehab: local page listing Chrome tabs, with close and drag-to-move between windows.
Run, then open http://127.0.0.1:8765"""
import html
import json
import secrets
import subprocess
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = 8765
TOKEN = secrets.token_hex(16)
US, RS = "\x1f", "\x1e"

LIST_SCRIPT = '''
set us to (ASCII character 31)
set rs to (ASCII character 30)
set out to ""
tell application "Google Chrome"
  repeat with w in windows
    set wid to id of w
    set ids to id of every tab of w
    set titles to title of every tab of w
    set urls to URL of every tab of w
    repeat with i from 1 to count of ids
      set out to out & wid & us & (item i of ids) & us & (item i of titles) & us & (item i of urls) & rs
    end repeat
  end repeat
end tell
return out
'''


def osa(script):
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def friendly(err):
    """Turn an osascript error into one short sentence for the page."""
    e = str(err)
    if "-1743" in e or "Not authorized" in e:
        return "macOS blocked access to Chrome. Allow your terminal under System Settings > Privacy & Security > Automation."
    if "-600" in e or "isn’t running" in e or "isn't running" in e:
        return "Chrome isn't running."
    if "Can’t get" in e or "Can't get" in e or "Invalid index" in e:
        return "That tab or window is gone. Refresh the page."
    return e.splitlines()[-1][:160] if e else "Unknown error."


def list_tabs():
    tabs = []
    for rec in osa(LIST_SCRIPT).rstrip("\n").split(RS):
        parts = rec.split(US)
        if len(parts) == 4:
            w, t, title, url = parts
            tabs.append({"w": int(w), "t": int(t), "title": title or url, "url": url})
    return tabs


def _svg(body):
    return ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


ICONS = {
    "view": _svg('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'),
    "copy": _svg('<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'),
    "trash": _svg('<path d="M3 6h18"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>'
                  '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'),
    "move": _svg('<path d="M16 3l4 4-4 4"/><path d="M20 7H4"/><path d="M8 21l-4-4 4-4"/><path d="M4 17h16"/>'),
    "grip": ('<svg width="10" height="16" viewBox="0 0 10 16" fill="currentColor" aria-hidden="true">'
             '<circle cx="3" cy="3" r="1.4"/><circle cx="7" cy="3" r="1.4"/><circle cx="3" cy="8" r="1.4"/>'
             '<circle cx="7" cy="8" r="1.4"/><circle cx="3" cy="13" r="1.4"/><circle cx="7" cy="13" r="1.4"/></svg>'),
}


def view_tab(w, t):
    osa(f'''tell application "Google Chrome"
  set w to window id {int(w)}
  set ids to id of every tab of w
  repeat with i from 1 to count of ids
    if (item i of ids as text) is "{int(t)}" then set active tab index of w to i
  end repeat
  set index of w to 1
  activate
end tell''')


def close_tab(w, t):
    osa(f'tell application "Google Chrome" to close (every tab of window id {int(w)} whose id is {int(t)})')


def close_many(tabs):
    """Close many tabs in one osascript call. Returns the "w:t" keys that failed."""
    lines = [f'try\n close (every tab of window id {int(x["w"])} whose id is {int(x["t"])})\n'
             f'on error\n set failed to failed & "{int(x["w"])}:{int(x["t"])} "\nend try' for x in tabs]
    out = osa('set failed to ""\ntell application "Google Chrome"\n' + "\n".join(lines) + '\nend tell\nreturn failed')
    return out.split()


def applescript_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def reopen_tab(w, url):
    """Reopen a URL at the end of window w, or the front window if w is gone. Returns (window id, tab id)."""
    out = osa(f'''tell application "Google Chrome"
  try
    set win to window id {int(w)}
  on error
    if (count of windows) is 0 then make new window
    set win to front window
  end try
  set newTab to make new tab at end of tabs of win with properties {{URL:{applescript_str(url)}}}
  return ((id of win) as text) & " " & ((id of newTab) as text)
end tell''')
    win, tab = out.split()
    return int(win), int(tab)


def move_tab(w, t, to):
    # Chrome's AppleScript "move" drops the page and leaves a blank new tab, so reopen the URL in the
    # target window, then close the original. Back/forward history for that tab is lost.
    out = osa(f'''tell application "Google Chrome"
  set src to (first tab of window id {int(w)} whose id is {int(t)})
  set u to URL of src
  set newTab to make new tab at end of tabs of window id {int(to)} with properties {{URL:u}}
  set newId to id of newTab
  if URL of newTab is "" then error "new tab did not get the URL"
  close src
  return newId
end tell''')
    return int(out.strip())


def host_of(url):
    host = urlparse(url).netloc or url.split(":")[0]
    return host[4:] if host.startswith("www.") else host


def window_code(n):
    return chr(64 + n) if n <= 26 else str(n)


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


CSS = '''
:root{
  --ink:#16181b; --ink-2:#4a5059; --ink-3:#5f6670; --ground:#fff; --panel:#f3f4f6;
  --rule:#d5d9de; --rule-strong:#8a919b; --red:#d7000f; --red-ink:#b5000c; --red-wash:#fff1f1;
  --row:30px;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{color-scheme:light;scrollbar-color:var(--rule-strong) var(--panel)}
body{margin:0;background:var(--ground);color:var(--ink);
  font:12px/1.4 "Hiragino Sans","Hiragino Kaku Gothic ProN","Segoe UI","Noto Sans",system-ui,sans-serif;
  font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
::selection{background:var(--red);color:#fff}
a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid var(--ink);outline-offset:1px}
input[type=checkbox]{accent-color:var(--red);width:14px;height:14px;margin:0;cursor:pointer}
header{display:flex;align-items:baseline;gap:12px;padding:14px 16px 10px}
h1{font-size:19px;font-weight:800;letter-spacing:-.02em;margin:0}
#total{color:var(--ink-2);font-size:12px}
#bar{position:sticky;top:0;z-index:3;background:var(--panel);border-top:1px solid var(--rule);
  border-bottom:2px solid var(--ink);padding:8px 16px;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}
#bar label{font-weight:600;color:var(--ink-2)}
#q{width:280px;height:28px;padding:0 8px;font:inherit;font-size:13px;color:var(--ink);background:#fff;
  border:1px solid var(--rule-strong);border-radius:2px;caret-color:var(--red)}
#q::placeholder{color:var(--ink-3)}
#shown{color:var(--ink-2)}
.purge{height:28px;padding:0 12px;border:0;border-radius:2px;background:var(--red);color:#fff;font:inherit;font-weight:700;cursor:pointer}
.purge:hover{background:var(--red-ink)}
.purge:disabled{opacity:.6;cursor:progress}
#chips{display:flex;gap:6px;flex:1;min-width:120px;overflow-x:auto;scrollbar-width:thin}
.chip{flex:none;display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 8px 0 0;border:1px solid var(--rule-strong);
  border-radius:2px;background:#fff;color:var(--ink);font:inherit;cursor:pointer}
.chip .tab{height:100%;border-radius:1px 0 0 1px}
.chip:hover{border-color:var(--ink)}
.chip .n{font-weight:700}
.chip.over,section.over{outline:2px solid var(--ink);outline-offset:-1px;background:var(--panel)}
#tray,#keys{position:relative}
#tray summary,#keys summary{cursor:pointer;color:var(--ink);font-weight:600;list-style:none;height:28px;display:flex;align-items:center;
  padding:0 8px;border:1px solid var(--rule-strong);border-radius:2px;background:#fff}
#tray summary::-webkit-details-marker,#keys summary::-webkit-details-marker{display:none}
#tray[open] summary,#keys[open] summary{border-color:var(--ink)}
.pop{position:absolute;right:0;top:32px;width:440px;background:#fff;border:1px solid var(--rule-strong);box-shadow:0 2px 6px rgba(22,24,27,.16)}
.pop ol{max-height:60vh;overflow:auto;margin:0;padding:0;list-style:none}
#tray li{grid-template-columns:26px 18px minmax(0,1fr) auto;padding:0 6px 0 0}
#tray li .tab{height:100%}
.note{margin:0;padding:6px 8px;color:var(--ink-2);border-bottom:1px solid var(--rule)}
#keys .pop{width:300px;padding:6px 10px}
#keys dl{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;margin:0}
#keys dd{margin:0;color:var(--ink-2)}
.linkbtn{border:0;background:none;padding:0 4px;height:24px;font:inherit;font-weight:700;color:var(--red-ink);cursor:pointer;
  text-decoration:underline;text-underline-offset:2px}
#refresh{font-weight:600;color:var(--ink);border-bottom:1px solid var(--rule-strong)}
#refresh:hover{border-color:var(--ink)}
.hint{margin:0;padding:6px 16px;color:var(--ink-2);border-bottom:1px solid var(--rule)}
main{column-width:460px;column-gap:10px;padding:10px 16px 80px}
section{border:1px solid var(--rule);background:#fff;min-width:0;break-inside:avoid;margin:0 0 10px}
section h2{display:flex;align-items:center;gap:8px;margin:0;height:28px;padding:0 8px 0 0;font-size:12px;font-weight:700;
  border-bottom:1px solid var(--rule-strong);background:var(--panel)}
.tab{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:100%;padding:0 6px;
  background:var(--red);color:#fff;font-weight:700;letter-spacing:.02em}
section h2 .count{font-weight:400;color:var(--ink-2)}
section h2 .doms{margin-left:auto;font-weight:400;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
ul{list-style:none;margin:0;padding:0}
li{position:relative;display:grid;grid-template-columns:22px 14px 18px minmax(0,1fr) auto 24px;align-items:center;gap:6px;
  height:var(--row);padding:0 4px 0 6px;border-bottom:1px solid #eceef1;background:#fff}
li:last-child{border-bottom:0}
li:hover,li:focus-within{background:#f7f8fa}
li.sel{background:var(--red-wash)}
li.moving,li.busy{opacity:.45}
.grip{display:flex;justify-content:center;color:var(--rule-strong);cursor:grab}
.grip:hover{color:var(--ink)}
.mono{width:18px;height:18px;border-radius:2px;display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:700;text-transform:uppercase}
.title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:12.5px;color:var(--ink)}
a.title:hover{text-decoration:underline;text-underline-offset:2px}
.host{max-width:170px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--ink-3);font-size:11px;text-align:right}
.host.err{max-width:320px;color:var(--ink);font-weight:700}
.more{position:absolute;right:32px;top:3px;display:flex;gap:2px;padding-left:6px;background:inherit;opacity:0}
li:hover .more,li:focus-within .more{opacity:1}
.more button,.del{width:24px;height:24px;display:flex;align-items:center;justify-content:center;padding:0;border:0;border-radius:2px;
  background:transparent;color:var(--ink-3);cursor:pointer;font:inherit;font-size:10px}
.more button:hover{background:#e6e8eb;color:var(--ink)}
.del{color:var(--ink-3)}
li:hover .del,li:focus-within .del,li.sel .del{color:var(--red-ink)}
li .del:hover{background:var(--red);color:#fff}
.more svg,.del svg{width:15px;height:15px}
#toast{position:fixed;left:16px;bottom:16px;z-index:4;display:flex;align-items:center;gap:10px;max-width:calc(100vw - 32px);
  padding:10px 12px;background:var(--ink);color:#fff;border-radius:2px;box-shadow:0 8px 24px rgba(22,24,27,.25)}
#toast .linkbtn{color:#fff}
#toast small{color:#c9cdd3}
#menu{position:fixed;z-index:5;width:240px;padding:4px 0;background:#fff;border:1px solid var(--rule-strong);
  box-shadow:0 2px 6px rgba(22,24,27,.16)}
#menu button{display:flex;align-items:center;gap:8px;width:100%;height:30px;padding:0 8px 0 0;border:0;background:none;
  font:inherit;color:var(--ink);text-align:left;cursor:pointer}
#menu button:hover,#menu button:focus-visible{background:var(--panel);outline:2px solid var(--ink);outline-offset:-2px}
#menu .note{margin:0;padding:6px 10px;color:var(--ink-2)}
kbd{font:inherit;font-size:11px;padding:0 4px;margin:0 1px;border:1px solid var(--rule-strong);border-radius:2px;background:#fff;color:var(--ink)}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.empty{padding:40px 16px;color:var(--ink-2);font-size:13px}
@media (prefers-reduced-motion:no-preference){li,.chip,.more,.more button,.del{transition:background-color .15s ease-out,opacity .15s ease-out}}
'''

JS = '''
const TOKEN = __TOKEN__;
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const rows = () => $$('main li');
const plural = (n, w) => n + ' ' + w + (n === 1 ? '' : 's');
async function call(path, body) {
  try {
    const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json','X-Token':TOKEN}, body: JSON.stringify(body)});
    const data = r.status === 204 ? {} : await r.json().catch(() => ({}));
    return r.ok ? {ok: true, data} : {ok: false, error: data.error || ('Error ' + r.status)};
  } catch (e) {
    return {ok: false, error: 'Tab Rehab server is not running. Restart it and refresh.'};
  }
}
function announce(msg) { const l = $('#live'); l.textContent = ''; setTimeout(() => l.textContent = msg, 30); }
const visible = () => rows().filter(li => !li.hidden);
function neighbor(lis) {
  // The row the keyboard should land on after these rows leave: the next visible one, else the previous.
  const vis = visible(), gone = new Set(lis);
  const last = Math.max(...lis.map(li => vis.indexOf(li)));
  return vis.slice(last + 1).find(li => !gone.has(li)) || vis.slice(0, last).reverse().find(li => !gone.has(li)) || null;
}
function focusRow(li, sel) {
  if (!li) { $('#q').focus(); return; }
  (li.querySelector(sel || '.del') || li.querySelector('.del')).focus({preventScroll: false});
}
function rowError(li, msg) {
  announce(msg);
  const h = li.querySelector('.host');
  if (!h.dataset.text) h.dataset.text = h.textContent;
  h.textContent = msg; h.title = msg; h.classList.add('err');
  clearTimeout(h._t);
  h._t = setTimeout(() => { h.textContent = h.dataset.text; h.title = ''; h.classList.remove('err'); }, 5000);
}
function flash(btn, msg) {
  if (!btn.dataset.icon) btn.dataset.icon = btn.innerHTML;
  btn.textContent = msg;
  setTimeout(() => btn.innerHTML = btn.dataset.icon, 1500);
}
async function viewTab(btn) {
  const li = btn.closest('li');
  const r = await call('/view', {w: +li.dataset.w, t: +li.dataset.t});
  if (!r.ok) rowError(li, r.error);
}
async function copyUrl(btn) {
  try { await navigator.clipboard.writeText(btn.closest('li').dataset.url); flash(btn, 'Copied'); announce('URL copied.'); }
  catch (e) { rowError(btn.closest('li'), 'Copy blocked by the browser.'); }
}

/* Closing, undo */
const closed = [];          // newest last: {li, w, url, title}
async function closeRows(lis) {
  if (!lis.length) return;
  lis.forEach(li => li.classList.add('busy'));
  const r = lis.length === 1
    ? await call('/close', {w: +lis[0].dataset.w, t: +lis[0].dataset.t})
    : await call('/close-many', {tabs: lis.map(li => ({w: +li.dataset.w, t: +li.dataset.t}))});
  if (!r.ok) { lis.forEach(li => { li.classList.remove('busy'); rowError(li, r.error); }); return; }
  const hadFocus = lis.some(li => li.contains(document.activeElement)) || document.activeElement.classList.contains('purge');
  const next = neighbor(lis);
  const failed = new Set(r.data.failed || []);
  const done = [];
  lis.forEach(li => {
    li.classList.remove('busy');
    if (failed.has(li.dataset.w + ':' + li.dataset.t)) { rowError(li, "Couldn't close. Refresh the page."); return; }
    setSel(li, false);
    done.push({li, w: +li.dataset.w, code: li.closest('section').dataset.code, url: li.dataset.url, title: li.querySelector('.title').textContent});
    li.remove();
  });
  if (!done.length) return;
  closed.push(...done);
  updateCounts(); renderTray();
  if (hadFocus) focusRow(next && !next.hidden ? next : null);
  const codes = [...new Set(done.map(d => d.code))];
  toast('Closed ' + plural(done.length, 'tab') + (codes.length === 1 ? ' from window ' + codes[0] : '') + '.', () => reopen(done));
}
function closeTab(btn) { return closeRows([btn.closest('li')]); }
function closeSelected() { return closeRows(rows().filter(li => li.classList.contains('sel') && !li.hidden)); }
function closeShown() { return closeRows(rows().filter(li => !li.hidden)); }
async function reopen(entries) {
  let lost = 0;
  for (const e of entries) {
    const r = await call('/reopen', {w: e.w, url: e.url});
    if (!r.ok) { toast("Couldn't reopen: " + r.error); return; }
    closed.splice(closed.indexOf(e), 1);
    const sec = $('section[data-w="' + r.data.w + '"]');
    if (sec) { e.li.dataset.w = r.data.w; e.li.dataset.t = r.data.t; sec.querySelector('ul').appendChild(e.li); }
    else lost++;
  }
  updateCounts(); renderTray();
  toast('Reopened ' + plural(entries.length, 'tab') + '.' + (lost ? ' Refresh to see ' + (lost === 1 ? 'it' : 'them') + '.' : ''));
}
function renderTray() {
  const tray = $('#tray');
  tray.hidden = !closed.length;
  tray.querySelector('summary').textContent = 'Recently closed (' + closed.length + ')';
  const ol = tray.querySelector('ol');
  ol.innerHTML = '';
  closed.slice().reverse().forEach(e => {
    const li = document.createElement('li');
    li.innerHTML = '<span class="tab"></span><span class="mono"></span><span class="title"></span><button class="linkbtn">Reopen</button>';
    li.querySelector('.tab').textContent = e.code;
    const m = e.li.querySelector('.mono');
    li.querySelector('.mono').replaceWith(m.cloneNode(true));
    li.querySelector('.title').textContent = e.title;
    li.querySelector('.title').title = e.url;
    li.querySelector('button').onclick = () => reopen([e]);
    ol.appendChild(li);
  });
}
let toastTimer;
function toast(msg, undo) {
  const t = $('#toast');
  t.innerHTML = '';
  const s = document.createElement('span'); s.textContent = msg; t.appendChild(s);
  if (undo) {
    const b = document.createElement('button'); b.className = 'linkbtn'; b.textContent = 'Undo';
    b.onclick = () => { t.hidden = true; undo(); };
    t.appendChild(b);
    const n = document.createElement('small'); n.textContent = 'Reopens without back/forward history'; t.appendChild(n);
  }
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.hidden = true, undo ? 8000 : 4000);
}

/* Selection */
let lastPick = null;
function setSel(li, on) { li.classList.toggle('sel', on); li.querySelector('.pick').checked = on; }
function pick(e) {
  const box = e.target, li = box.closest('li');
  if (e.shiftKey && lastPick && lastPick !== li) {
    const vis = rows().filter(r => !r.hidden);
    const a = vis.indexOf(lastPick), b = vis.indexOf(li);
    if (a >= 0 && b >= 0) vis.slice(Math.min(a, b), Math.max(a, b) + 1).forEach(r => setSel(r, box.checked));
  }
  setSel(li, box.checked);
  lastPick = li;
  updateBar();
}
function updateBar() {
  const sel = rows().filter(li => li.classList.contains('sel') && !li.hidden).length;
  const shown = rows().filter(li => !li.hidden).length;
  const q = $('#q').value.trim();
  $('#closeSel').hidden = !sel;
  $('#closeSel').textContent = 'Close ' + sel + ' selected';
  $('#closeShown').hidden = !!sel || !q || !shown;
  $('#closeShown').textContent = 'Close all ' + shown + ' shown';
}

/* Moving */
let dragged = null;
function dragStart(e) {
  dragged = e.target.closest('li');
  e.dataTransfer.setDragImage(dragged.querySelector('.title'), 10, 10);
  dragged.classList.add('moving');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', dragged.dataset.t);
}
function dragEnd() {
  if (dragged) dragged.classList.remove('moving');
  $$('.over').forEach(s => s.classList.remove('over'));
  dragged = null;
}
function dragOver(e) {
  const s = e.currentTarget;
  if (!dragged || s.dataset.w === dragged.dataset.w) return;
  e.preventDefault();
  s.classList.add('over');
}
async function moveRow(li, w) {
  if (w === li.dataset.w) return;
  li.classList.add('busy');
  const r = await call('/move', {w: +li.dataset.w, t: +li.dataset.t, to: +w});
  li.classList.remove('busy');
  if (!r.ok) { rowError(li, 'Move failed: ' + r.error); return false; }
  li.dataset.w = w; li.dataset.t = r.data.t;
  const sec = $('section[data-w="' + w + '"]');
  sec.querySelector('ul').appendChild(li);
  updateCounts();
  announce('Moved to window ' + sec.dataset.code + '.');
  return true;
}

/* Keyboard move menu */
let menuFor = null;
function openMove(btn) {
  const li = btn.closest('li'), m = $('#menu');
  m.innerHTML = '';
  const targets = $$('main section').filter(s => s.dataset.w !== li.dataset.w && s.querySelector('li'));
  m.innerHTML = '<p class="note">' + (targets.length ? 'Moving reloads the page. Back/forward history is lost.' : 'No other windows. Open one in Chrome, then refresh.') + '</p>';
  targets.forEach(s => {
    const b = document.createElement('button');
    b.setAttribute('role', 'menuitem');
    b.innerHTML = '<span class="tab"></span><span></span>';
    b.firstChild.textContent = s.dataset.code;
    b.lastChild.textContent = 'Window ' + s.dataset.code + ', ' + s.querySelector('.count').textContent;
    b.onclick = async () => {
      const next = neighbor([li]);
      closeMenu(false);
      if (await moveRow(li, s.dataset.w)) focusRow(next, '.mv'); else focusRow(li, '.mv');
    };
    m.appendChild(b);
  });
  const r = btn.getBoundingClientRect();
  m.style.top = Math.min(r.bottom + 4, innerHeight - 40 - 30 * targets.length) + 'px';
  m.style.left = Math.max(8, r.right - 240) + 'px';
  m.hidden = false; menuFor = btn;
  btn.setAttribute('aria-expanded', 'true');
  (m.querySelector('button') || m).focus();
}
function closeMenu(refocus) {
  const m = $('#menu');
  if (m.hidden) return;
  m.hidden = true;
  if (menuFor) { menuFor.setAttribute('aria-expanded', 'false'); if (refocus !== false) menuFor.focus(); }
  menuFor = null;
}
document.addEventListener('mousedown', e => { if (!e.target.closest('#menu, .mv')) closeMenu(false); });
addEventListener('scroll', () => closeMenu(false), {passive: true});

/* Shortcuts */
document.addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const a = document.activeElement, inMenu = a && a.closest && a.closest('#menu');
  if (inMenu) {
    const items = $$('#menu button'), i = items.indexOf(a);
    if (e.key === 'Escape') { e.preventDefault(); closeMenu(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    return;
  }
  if (a && a.id === 'q') {
    if (e.key === 'Escape') { a.value = ''; filter(); a.blur(); }
    if (e.key === 'ArrowDown') { e.preventDefault(); focusRow(visible()[0], '.pick'); }
    return;
  }
  const li = a && a.closest && a.closest('main li');
  if (e.key === '/') { e.preventDefault(); $('#q').focus(); $('#q').select(); return; }
  if (!li) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'j' || e.key === 'k') {
    e.preventDefault();
    const vis = visible(), i = vis.indexOf(li) + (e.key === 'ArrowDown' || e.key === 'j' ? 1 : -1);
    if (vis[i]) {
      const cls = [...a.classList].find(c => ['pick', 'title', 'vw', 'cp', 'mv', 'del'].includes(c)) || 'pick';
      focusRow(vis[i], '.' + cls);
    }
  } else if (e.key === 'x' || (e.key === ' ' && !a.matches('button, input'))) {
    e.preventDefault();
    const box = li.querySelector('.pick');
    box.checked = !box.checked; setSel(li, box.checked); lastPick = li; updateBar();
  } else if (e.key === 'Delete' || e.key === 'Backspace') {
    e.preventDefault();
    const sel = visible().filter(r => r.classList.contains('sel'));
    closeRows(sel.length ? sel : [li]);
  } else if (e.key === 'm') {
    e.preventDefault(); openMove(li.querySelector('.mv'));
  }
});
function drop(e) {
  e.preventDefault();
  const w = e.currentTarget.dataset.w, li = dragged;
  e.currentTarget.classList.remove('over');
  if (li) moveRow(li, w);
}
function jump(chip) {
  $('section[data-w="' + chip.dataset.w + '"]').scrollIntoView({block: 'start'});
}

/* Counts and filter */
function updateCounts() {
  $$('main section').forEach(s => {
    const n = s.querySelectorAll('li').length;
    const chip = $('.chip[data-w="' + s.dataset.w + '"]');
    s.querySelector('.count').textContent = plural(n, 'tab');
    if (chip) { chip.querySelector('.n').textContent = n; chip.hidden = !n; }
  });
  const wins = $$('main section').filter(s => s.querySelector('li')).length;
  $('#total').textContent = plural(rows().length, 'tab') + ' in ' + plural(wins, 'window');
  filter();
}
function filter() {
  const q = $('#q').value.trim().toLowerCase();
  let shown = 0;
  $$('main section').forEach(s => {
    let any = false;
    s.querySelectorAll('li').forEach(li => {
      const hit = !q || li.dataset.find.includes(q);
      li.hidden = !hit; if (hit) { any = true; shown++; }
    });
    s.hidden = !any;
  });
  $('#shown').textContent = q ? shown + ' of ' + plural(rows().length, 'tab') : '';
  const none = $('#none');
  none.hidden = shown > 0;
  none.textContent = rows().length ? 'No tabs match "' + $('#q').value.trim() + '". Press Esc to clear the filter.' : 'No tabs left. Open some in Chrome, then refresh.';
  updateBar();
}
function refresh(a) {
  const q = $('#q').value.trim();
  a.href = q ? '/?q=' + encodeURIComponent(q) : '/';
}
(() => {
  const q = new URLSearchParams(location.search).get('q');
  if (q) { $('#q').value = q; filter(); }
})();
'''

ERROR_PAGE = '''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Tab Rehab</title>
<style>body{font:14px/1.5 "Hiragino Sans",system-ui,sans-serif;color:#16181b;max-width:640px;margin:48px auto;padding:0 16px}
h1{font-size:18px;margin:0 0 12px}.box{border:1px solid #d5d9de;border-top:3px solid #16181b;padding:12px 16px}
code{font-size:12px;color:#4a5059}</style></head><body><h1>Tab Rehab can't read your Chrome tabs</h1>
<div class="box"><p><b>{reason}</b></p><p>Check that Google Chrome is open. The first run asks to let your terminal control Chrome.
If you declined, turn it on under System Settings &gt; Privacy &amp; Security &gt; Automation, then <a href="/">try again</a>.</p>
<p><code>{detail}</code></p></div></body></html>'''


def render(tabs):
    windows = {}
    for tab in tabs:
        windows.setdefault(tab["w"], []).append(tab)
    sections, chips = [], []
    for n, (w, wtabs) in enumerate(windows.items(), 1):
        code = window_code(n)
        rows = []
        for tab in wtabs:
            host = host_of(tab["url"])
            hue = sum(map(ord, host)) * 37 % 360
            title = html.escape(tab["title"])
            url = html.escape(tab["url"])
            tip = f'{title}&#10;{url}'
            # Only web URLs get a link; a page can't open chrome:// or file:// links anyway.
            if urlparse(tab["url"]).scheme in ("http", "https"):
                title_el = f'<a class="title" href="{url}" target="_blank" rel="noopener" title="{tip}">{title}</a>'
            else:
                title_el = f'<span class="title" title="{tip}">{title}</span>'
            find = html.escape(f'{tab["title"]} {tab["url"]}'.lower())
            rows.append(
                f'<li data-w="{w}" data-t="{tab["t"]}" data-url="{url}" data-find="{find}">'
                f'<input type="checkbox" class="pick" onclick="pick(event)" aria-label="Select: {title}">'
                f'<span class="grip" draggable="true" ondragstart="dragStart(event)" ondragend="dragEnd()" '
                f'title="Drag onto another window" aria-hidden="true">{ICONS["grip"]}</span>'
                f'<span class="mono" style="background:hsl({hue} 55% 91%);color:hsl({hue} 60% 26%)" aria-hidden="true">'
                f'{html.escape(host[:1] or "?")}</span>'
                f'{title_el}<span class="host">{html.escape(host)}</span>'
                f'<span class="more">'
                f'<button class="vw" onclick="viewTab(this)" title="Switch to this tab in Chrome" aria-label="View in Chrome: {title}">{ICONS["view"]}</button>'
                f'<button class="cp" onclick="copyUrl(this)" title="Copy URL" aria-label="Copy URL: {title}">{ICONS["copy"]}</button>'
                f'<button class="mv" onclick="openMove(this)" title="Move to another window (M)" aria-haspopup="menu" aria-expanded="false" '
                f'aria-label="Move to window: {title}">{ICONS["move"]}</button>'
                f'</span><button class="del" onclick="closeTab(this)" title="Close tab (Delete)" aria-label="Close: {title}">{ICONS["trash"]}</button></li>'
            )
        doms = ", ".join(h for h, _ in Counter(host_of(t["url"]) for t in wtabs).most_common(2))
        drop = 'ondragover="dragOver(event)" ondragleave="this.classList.remove(\'over\')" ondrop="drop(event)"'
        sections.append(
            f'<section data-w="{w}" data-code="{code}" aria-label="Window {code}" {drop}>'
            f'<h2><span class="tab">{code}</span>Window {code} <span class="count">{plural(len(wtabs), "tab")}</span>'
            f'<span class="doms">{html.escape(doms)}</span></h2><ul>{"".join(rows)}</ul></section>'
        )
        chips.append(
            f'<button class="chip" data-w="{w}" {drop} onclick="jump(this)" title="Jump to window {code}, or drop a tab here">'
            f'<span class="tab">{code}</span><span class="n">{len(wtabs)}</span></button>'
        )
    body = "".join(sections) or '<p class="empty">No Chrome tabs are open.</p>'
    total = f'{plural(len(tabs), "tab")} in {plural(len(windows), "window")}'
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Tab Rehab</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style></head><body>
<header><h1>Tab Rehab</h1><span id="total">{total}</span></header>
<div id="bar"><label for="q">Filter</label><input id="q" placeholder="Title or URL" oninput="filter()" autocomplete="off">
<span id="shown"></span><button id="closeSel" class="purge" onclick="closeSelected()" hidden></button>
<button id="closeShown" class="purge" onclick="closeShown()" hidden></button>
<div id="chips">{"".join(chips)}</div>
<details id="tray" hidden><summary></summary><div class="pop"><p class="note">Reopening loads the page fresh. Back/forward history is not kept.</p><ol></ol></div></details>
<details id="keys"><summary>Keys</summary><div class="pop"><dl><dt><kbd>/</kbd></dt><dd>Filter</dd><dt><kbd>Esc</kbd></dt><dd>Clear filter</dd><dt><kbd>&uarr;</kbd><kbd>&darr;</kbd> <kbd>j</kbd><kbd>k</kbd></dt><dd>Move between tabs</dd><dt><kbd>x</kbd></dt><dd>Select tab</dd><dt><kbd>Delete</kbd></dt><dd>Close selected, or this tab</dd><dt><kbd>m</kbd></dt><dd>Move to another window</dd></dl></div></details><a id="refresh" href="/" onclick="refresh(this)">Refresh</a></div>
<p class="hint">Check tabs to close them together (shift-click for a range). Drag a grip onto a window or chip to move a tab; its back/forward history is lost.</p>
<p id="none" class="empty" hidden></p><main>{body}</main><div id="menu" role="menu" aria-label="Move to window" tabindex="-1" hidden></div>
<div id="toast" role="status" hidden></div><div id="live" class="sr-only" aria-live="polite"></div>
<script>{JS.replace("__TOKEN__", json.dumps(TOKEN))}</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        if body:
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path != "/":
            return self.send_error(404)
        try:
            body = render(list_tabs()).encode()
        except RuntimeError as e:
            page = ERROR_PAGE.replace("{reason}", html.escape(friendly(e))).replace("{detail}", html.escape(str(e)))
            return self.reply(500, page.encode(), "text/html; charset=utf-8")
        self.reply(200, body, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path not in ("/close", "/close-many", "/move", "/view", "/reopen") or self.headers.get("X-Token") != TOKEN:
            return self.send_error(403)
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        try:
            if self.path in ("/close", "/view"):
                (close_tab if self.path == "/close" else view_tab)(data["w"], data["t"])
                return self.reply(204)
            if self.path == "/close-many":
                out = {"failed": close_many(data["tabs"])}
            elif self.path == "/reopen":
                w, t = reopen_tab(data["w"], str(data["url"]))
                out = {"w": w, "t": t}
            else:
                out = {"t": move_tab(data["w"], data["t"], data["to"])}
            self.reply(200, json.dumps(out).encode())
        except (RuntimeError, ValueError, KeyError) as e:
            self.reply(500, json.dumps({"error": friendly(e)}).encode())

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Open http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
