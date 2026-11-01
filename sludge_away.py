#!/usr/bin/env python3
"""Chrome Tab Sludge-Away: local page listing Chrome tabs, with close and drag-to-move between windows.
Run, then open http://127.0.0.1:8765"""
import html
import json
import secrets
import subprocess
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


def render(tabs):
    windows = {}
    for tab in tabs:
        windows.setdefault(tab["w"], []).append(tab)
    sections = []
    for n, (w, wtabs) in enumerate(windows.items(), 1):
        rows = []
        for tab in wtabs:
            host = urlparse(tab["url"]).netloc or tab["url"].split(":")[0]
            rows.append(
                f'<li draggable="true" ondragstart="dragStart(event)" ondragend="dragEnd()" data-w="{tab["w"]}" data-t="{tab["t"]}">'
                f'<span class="grip" title="Drag to another window">&#8942;&#8942;</span>'
                f'<button onclick="closeTab(this)">Close</button>'
                f'<div><div class="title">{html.escape(tab["title"])}</div>'
                f'<div class="url"><b>{html.escape(host)}</b> &middot; {html.escape(tab["url"])}</div></div></li>'
            )
        sections.append(
            f'<section data-w="{w}" ondragover="dragOver(event)" ondragleave="this.classList.remove(\'over\')" ondrop="drop(event)">'
            f'<h2>Window {n} <span class="count">({len(wtabs)} tabs)</span></h2><ul>{"".join(rows)}</ul></section>'
        )
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>Chrome Tab Sludge-Away</title>
<style>
body{{font:14px -apple-system,system-ui,sans-serif;margin:24px auto;max-width:1000px;color:#222;padding:0 16px}}
h1{{margin:0 0 8px}} h2{{font-size:15px;margin:20px 0 6px;color:#555}} .count{{font-weight:normal}}
ul{{list-style:none;padding:0;margin:0}}
li{{display:flex;gap:12px;align-items:flex-start;padding:8px;border-bottom:1px solid #eee}}
li:hover{{background:#f7f7f7}}
.title{{font-weight:600}} .url{{color:#777;font-size:12px;word-break:break-all}}
button{{flex:none;cursor:pointer;border:1px solid #c33;color:#c33;background:#fff;border-radius:4px;padding:3px 10px}}
button:hover{{background:#c33;color:#fff}}
#bar{{position:sticky;top:0;background:#fff;padding:8px 0;display:flex;gap:12px;align-items:center}}
#q{{flex:1;padding:6px 8px;font-size:14px}}
section{{border:2px dashed transparent;border-radius:6px;padding:0 6px}}
body.dragging section{{border-color:#ddd}}
section.over{{border-color:#36c;background:#f0f5ff}}
li.moving{{opacity:.4}}
.grip{{flex:none;cursor:grab;color:#bbb;letter-spacing:-3px;padding-top:3px;user-select:none}}
.hint{{color:#888;margin:0 0 8px}}
</style></head><body>
<h1>Chrome Tab Sludge-Away</h1>
<p class="hint">Drag a tab onto another window to move it there (it lands at the end of that window).</p>
<div id="bar"><input id="q" placeholder="Filter by title or URL" oninput="filter()"><span id="total">{len(tabs)} tabs</span>
<a href="/">Refresh</a></div>
{"".join(sections)}
<script>
const TOKEN = {json.dumps(TOKEN)};
async function closeTab(btn) {{
  const li = btn.closest('li');
  btn.disabled = true; btn.textContent = '...';
  const r = await fetch('/close', {{method:'POST', headers:{{'Content-Type':'application/json','X-Token':TOKEN}},
    body: JSON.stringify({{w: +li.dataset.w, t: +li.dataset.t}})}});
  if (r.ok) {{ li.remove(); updateCounts(); }} else {{ btn.disabled = false; btn.textContent = 'Failed'; }}
}}
let dragged = null;
function dragStart(e) {{
  dragged = e.target.closest('li');
  dragged.classList.add('moving');
  document.body.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', dragged.dataset.t);
}}
function dragEnd() {{
  if (dragged) dragged.classList.remove('moving');
  document.body.classList.remove('dragging');
  document.querySelectorAll('section.over').forEach(s => s.classList.remove('over'));
}}
function dragOver(e) {{
  const s = e.currentTarget;
  if (!dragged || s.dataset.w === dragged.dataset.w) return;
  e.preventDefault();
  s.classList.add('over');
}}
async function drop(e) {{
  e.preventDefault();
  const s = e.currentTarget, li = dragged;
  s.classList.remove('over');
  if (!li || s.dataset.w === li.dataset.w) return;
  const r = await fetch('/move', {{method:'POST', headers:{{'Content-Type':'application/json','X-Token':TOKEN}},
    body: JSON.stringify({{w: +li.dataset.w, t: +li.dataset.t, to: +s.dataset.w}})}});
  if (!r.ok) {{ alertRow(li, 'Move failed'); return; }}
  const {{t}} = await r.json();
  li.dataset.w = s.dataset.w; li.dataset.t = t;
  s.querySelector('ul').appendChild(li);
  updateCounts();
}}
function alertRow(li, msg) {{
  const b = li.querySelector('button'); b.textContent = msg;
  setTimeout(() => b.textContent = 'Close', 2000);
}}
function updateCounts() {{
  document.querySelectorAll('section').forEach(s => {{
    const n = s.querySelectorAll('li').length;
    if (!n) s.remove(); else s.querySelector('.count').textContent = '(' + n + ' tabs)';
  }});
  document.getElementById('total').textContent = document.querySelectorAll('li').length + ' tabs';
}}
function filter() {{
  const q = document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('li').forEach(li => li.style.display = li.textContent.toLowerCase().includes(q) ? '' : 'none');
}}
</script></body></html>'''


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
        if self.path not in ("/close", "/move") or self.headers.get("X-Token") != TOKEN:
            return self.send_error(403)
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        try:
            if self.path == "/close":
                close_tab(data["w"], data["t"])
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
