# Tab Rehab

A local web page that lists every open Google Chrome tab, grouped by window, so you can kick the tab habit fast.

- **Switch** to a tab by clicking its title (or the eye icon). Cmd-click opens the URL as a new tab instead.
- **Close** any tab with one click (trash icon), or check several (one window at a time with its header checkbox) and close them together.
- **Close duplicates** keeps the first copy of each page and closes the rest.
- **Undo** reopens what you just closed (press `u`), without back/forward history.
- **Move** a tab to another window by dragging its grip, or with the move button (`m`).
- **Filter** by title or URL. Press "Shortcuts" on the page for every shortcut.

macOS only. It talks to Chrome through AppleScript. Python 3 standard library, no dependencies.

## Run

```
python3 tab_rehab.py
```

Then open http://127.0.0.1:8765. The first run asks you to allow your terminal to control Google Chrome.

## Notes

- The server listens on 127.0.0.1 only, and close/move requests need a per-run token embedded in the page.
- Moving a tab reopens its URL in the target window and closes the original, because Chrome's AppleScript `move` drops the page. The moved tab loses its back/forward history.
- The page doesn't auto-refresh; click Refresh after changing tabs elsewhere.
