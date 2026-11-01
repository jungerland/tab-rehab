# Chrome Tab Sludge-Away

A local web page that lists every open Google Chrome tab, grouped by window, so you can clear tab sludge fast.

- **View** a tab (eye icon) to bring its window to the front and switch to it.
- **Close** any tab with one click (trash icon).
- **Move** a tab to another window by dragging its grip onto that window.
- **Filter** by title or URL.
- Click a URL to open it, or use the copy icon to put the clean URL on your clipboard.

macOS only. It talks to Chrome through AppleScript. Python 3 standard library, no dependencies.

## Run

```
python3 sludge_away.py
```

Then open http://127.0.0.1:8765. The first run asks you to allow your terminal to control Google Chrome.

## Notes

- The server listens on 127.0.0.1 only, and close/move requests need a per-run token embedded in the page.
- Moving a tab reopens its URL in the target window and closes the original, because Chrome's AppleScript `move` drops the page. The moved tab loses its back/forward history.
- The page doesn't auto-refresh; click Refresh after changing tabs elsewhere.
