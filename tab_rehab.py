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


def list_tabs():
    tabs = []
    for rec in osa(LIST_SCRIPT).rstrip("\n").split(RS):
        parts = rec.split(US)
        if len(parts) == 4:
            w, t, title, url = parts
            tabs.append({"w": int(w), "t": int(t), "title": title or url, "url": url})
    return tabs


def _svg(body):
    return ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


ICONS = {
    "view": _svg('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'),
    "copy": _svg('<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'),
    "trash": _svg('<path d="M3 6h18"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>'
                  '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>'),
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
html{color-scheme:light}
body{margin:0;background:var(--ground);color:var(--ink);
  font:12px/1.4 "Hiragino Sans","Hiragino Kaku Gothic ProN","Segoe UI","Noto Sans",system-ui,sans-serif;
  font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
::selection{background:var(--red);color:#fff}
a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid var(--ink);outline-offset:1px}
header{display:flex;align-items:baseline;gap:12px;padding:14px 16px 10px}
h1{font-size:18px;font-weight:700;letter-spacing:-.01em;margin:0}
#total{color:var(--ink-2);font-size:12px}
#bar{position:sticky;top:0;z-index:2;background:var(--panel);border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule-strong);padding:8px 16px;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}
#bar label{font-weight:600;color:var(--ink-2)}
#q{width:280px;height:28px;padding:0 8px;font:inherit;font-size:13px;color:var(--ink);background:#fff;
  border:1px solid var(--rule-strong);border-radius:2px}
#q::placeholder{color:var(--ink-3)}
#shown{color:var(--ink-2);min-width:90px}
#chips{display:flex;flex-wrap:wrap;gap:6px;flex:1}
.chip{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 8px 0 0;border:1px solid var(--rule-strong);
  border-radius:2px;background:#fff;color:var(--ink);font:inherit;cursor:pointer}
.chip .tab{height:100%;border-radius:1px 0 0 1px}
.chip:hover{border-color:var(--ink)}
.chip.over,section.over{outline:2px solid var(--red);outline-offset:-1px;background:var(--red-wash)}
#refresh{font-weight:600;color:var(--ink);border-bottom:1px solid var(--rule-strong)}
#refresh:hover{border-color:var(--ink)}
.hint{margin:0;padding:6px 16px;color:var(--ink-2);border-bottom:1px solid var(--rule)}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(460px,1fr));gap:10px;padding:10px 16px 40px;align-items:start}
section{border:1px solid var(--rule);background:#fff;min-width:0}
section h2{display:flex;align-items:center;gap:8px;margin:0;height:28px;padding:0 8px 0 0;font-size:12px;font-weight:600;
  border-bottom:1px solid var(--rule);background:var(--panel)}
.tab{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:100%;padding:0 6px;
  background:var(--red);color:#fff;font-weight:700;letter-spacing:.02em}
section h2 .count{font-weight:400;color:var(--ink-2)}
section h2 .doms{margin-left:auto;font-weight:400;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
ul{list-style:none;margin:0;padding:0}
li{display:grid;grid-template-columns:14px 18px minmax(0,1fr) auto auto;align-items:center;gap:6px;
  height:var(--row);padding:0 4px 0 2px;border-bottom:1px solid #eceef1}
li:last-child{border-bottom:0}
li:hover,li:focus-within{background:#f7f8fa}
li.moving{opacity:.4}
.grip{display:flex;justify-content:center;color:var(--rule-strong);cursor:grab}
.grip:hover{color:var(--ink)}
.mono{width:18px;height:18px;border-radius:2px;display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:700;text-transform:uppercase}
.title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:12.5px;color:var(--ink)}
a.title:hover{text-decoration:underline;text-underline-offset:2px}
.host{max-width:170px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--ink-3);font-size:11px;text-align:right}
.acts{display:flex;gap:2px}
.acts button{width:24px;height:24px;display:flex;align-items:center;justify-content:center;padding:0;border:0;border-radius:2px;
  background:transparent;color:var(--ink-3);cursor:pointer;font:inherit;font-size:10px}
.acts button:hover{background:#e6e8eb;color:var(--ink)}
.acts .soft{opacity:0}
li:hover .soft,li:focus-within .soft{opacity:1}
.acts .del{color:var(--red-ink)}
.acts .del:hover{background:var(--red);color:#fff}
.acts button:disabled{cursor:progress;opacity:.6}
.acts svg{width:15px;height:15px}
.empty{padding:40px 16px;color:var(--ink-2);font-size:13px}
@media (prefers-reduced-motion:no-preference){li,.chip,.acts button{transition:background-color .15s ease-out,opacity .15s ease-out}}
'''

JS = '''
const TOKEN = __TOKEN__;
const TOTAL = () => document.querySelectorAll('main li').length;
function flash(btn, msg, ms) {
  if (!btn.dataset.icon) btn.dataset.icon = btn.innerHTML;
  btn.textContent = msg;
  setTimeout(() => btn.innerHTML = btn.dataset.icon, ms || 1500);
}
async function post(path, body) {
  return fetch(path, {method:'POST', headers:{'Content-Type':'application/json','X-Token':TOKEN}, body: JSON.stringify(body)});
}
async function viewTab(btn) {
  const li = btn.closest('li');
  const r = await post('/view', {w: +li.dataset.w, t: +li.dataset.t});
  if (!r.ok) flash(btn, 'Failed');
}
async function closeTab(btn) {
  const li = btn.closest('li');
  btn.disabled = true; flash(btn, '...', 60000);
  const r = await post('/close', {w: +li.dataset.w, t: +li.dataset.t});
  if (r.ok) { li.remove(); updateCounts(); } else { btn.disabled = false; flash(btn, 'Failed'); }
}
async function copyUrl(btn) {
  await navigator.clipboard.writeText(btn.closest('li').dataset.url);
  flash(btn, 'Copied');
}
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
  document.querySelectorAll('.over').forEach(s => s.classList.remove('over'));
  dragged = null;
}
function dragOver(e) {
  const s = e.currentTarget;
  if (!dragged || s.dataset.w === dragged.dataset.w) return;
  e.preventDefault();
  s.classList.add('over');
}
async function drop(e) {
  e.preventDefault();
  const w = e.currentTarget.dataset.w, li = dragged;
  e.currentTarget.classList.remove('over');
  if (!li || w === li.dataset.w) return;
  const r = await post('/move', {w: +li.dataset.w, t: +li.dataset.t, to: +w});
  if (!r.ok) { alertRow(li, 'Move failed'); return; }
  const {t} = await r.json();
  li.dataset.w = w; li.dataset.t = t;
  document.querySelector('section[data-w="' + w + '"] ul').appendChild(li);
  updateCounts();
}
function alertRow(li, msg) {
  flash(li.querySelector('button.del'), msg, 2000);
}
function jump(chip) {
  document.querySelector('section[data-w="' + chip.dataset.w + '"]').scrollIntoView({block: 'start'});
}
const plural = (n, w) => n + ' ' + w + (n === 1 ? '' : 's');
function updateCounts() {
  document.querySelectorAll('main section').forEach(s => {
    const n = s.querySelectorAll('li').length;
    const chip = document.querySelector('.chip[data-w="' + s.dataset.w + '"]');
    if (!n) { s.remove(); if (chip) chip.remove(); return; }
    s.querySelector('.count').textContent = plural(n, 'tab');
    if (chip) chip.querySelector('.n').textContent = n;
  });
  document.getElementById('total').textContent = plural(TOTAL(), 'tab') + ' in ' +
    plural(document.querySelectorAll('main section').length, 'window');
  filter();
}
function filter() {
  const q = document.getElementById('q').value.trim().toLowerCase();
  let shown = 0;
  document.querySelectorAll('main section').forEach(s => {
    let any = false;
    s.querySelectorAll('li').forEach(li => {
      const hit = !q || li.dataset.find.includes(q);
      li.hidden = !hit; if (hit) { any = true; shown++; }
    });
    s.hidden = !any;
  });
  document.getElementById('shown').textContent = q ? shown + ' of ' + plural(TOTAL(), 'tab') : '';
}
'''


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
                f'<span class="grip" draggable="true" ondragstart="dragStart(event)" ondragend="dragEnd()" '
                f'title="Drag onto another window">{ICONS["grip"]}</span>'
                f'<span class="mono" style="background:hsl({hue} 55% 91%);color:hsl({hue} 60% 26%)" aria-hidden="true">'
                f'{html.escape(host[:1] or "?")}</span>'
                f'{title_el}<span class="host">{html.escape(host)}</span>'
                f'<span class="acts">'
                f'<button class="soft" onclick="viewTab(this)" title="Switch to this tab in Chrome" aria-label="View tab">{ICONS["view"]}</button>'
                f'<button class="soft" onclick="copyUrl(this)" title="Copy URL" aria-label="Copy URL">{ICONS["copy"]}</button>'
                f'<button class="del" onclick="closeTab(this)" title="Close tab" aria-label="Close tab">{ICONS["trash"]}</button>'
                f'</span></li>'
            )
        doms = ", ".join(h for h, _ in Counter(host_of(t["url"]) for t in wtabs).most_common(2))
        drop = 'ondragover="dragOver(event)" ondragleave="this.classList.remove(\'over\')" ondrop="drop(event)"'
        sections.append(
            f'<section data-w="{w}" {drop}>'
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
<span id="shown"></span><div id="chips">{"".join(chips)}</div><a id="refresh" href="/">Refresh</a></div>
<p class="hint">Drag a tab by its grip onto a window or a window chip to move it. Moving reopens the page there, so its back/forward history is lost.</p>
<main>{body}</main>
<script>{JS.replace("__TOKEN__", json.dumps(TOKEN))}</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            return self.send_error(404)
        try:
            body = render(list_tabs()).encode()
        except RuntimeError as e:
            return self.send_error(500, str(e))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path not in ("/close", "/move", "/view") or self.headers.get("X-Token") != TOKEN:
            return self.send_error(403)
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        try:
            if self.path in ("/close", "/view"):
                (close_tab if self.path == "/close" else view_tab)(data["w"], data["t"])
                self.send_response(204)
                self.end_headers()
            else:
                new_id = move_tab(data["w"], data["t"], data["to"])
                body = json.dumps({"t": new_id}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)
        except (RuntimeError, ValueError) as e:
            self.send_error(500, str(e))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Open http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
