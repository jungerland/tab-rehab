# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary user: Jay, a long-time software and product person, on a desktop Chrome browser. It may be shared with others later (GitHub or colleagues), so it should never depend on knowledge only the author has. No outside users are confirmed yet.

The situation: tabs pile up across several Chrome windows until there are dozens to 100+. The user sits down to deal with it.

## Product Purpose

Tab Rehab (formerly Chrome Tab Sludge-Away) shows every open Chrome tab, grouped by window, on one page so the user can clear the backlog fast.

Two main jobs, in this order:

1. **Big periodic purge:** go through a large pile of tabs and close most of them in one sitting.
2. **Reorganize windows:** move the tabs worth keeping into the right windows.

Quick find-and-jump (filter, then view one tab) is supported but secondary.

Success: a purge of 100+ tabs feels quick and low-effort, and the user ends with fewer tabs in sensibly grouped windows.

## Positioning

Undecided. Do not invent a competitive claim.

## Operating Context

- Used on a desktop computer during a dedicated cleanup session, not in passing.
- Current build: a local web page at http://127.0.0.1:8765, served by `sludge_away.py`. It reads and controls Chrome through AppleScript, so it works on macOS only today.
- The page doesn't auto-refresh. The user clicks Refresh after changing tabs elsewhere.

## Capabilities and Constraints

Current capabilities: list tabs by window, filter by title or URL, view (switch to) a tab, close a tab, copy a tab's clean URL, open web URLs, and drag a tab by its grip onto another window to move it.

Constraints:
- **Chrome only.** No other browsers.
- **Desktop only.** Chrome desktop runs on macOS, Windows, and Linux. No mobile layouts.
- **Planned direction: a Chrome extension**, which would make it work on all three desktop OSes. The current macOS/AppleScript build is a first step, not the long-term platform. Design work shouldn't rely on anything an extension page couldn't do.
- Moving a tab currently reopens its URL in the target window and closes the original, so the moved tab loses its back/forward history (an AppleScript limitation).
- The local server listens on 127.0.0.1 only, and close/move/view requests need a per-run token.
- The single-file, standard-library-only Python build is how it works today. It is not a binding constraint on future work.

## Brand Commitments

- **Name: Tab Rehab.** It replaces "Chrome Tab Sludge-Away." The code, page title, and README still use the old name until they're renamed.
- **Voice:** a little playful, with the same light humor as the old name. The humor lives in the name and the occasional line of copy. The work itself stays fast and serious.

## Evidence on Hand

None. No users, testimonials, or usage data. Don't make any up.

## Product Principles

1. **Built for the big purge.** Optimize for clearing many tabs in one sitting. Each close should be one quick action, and the page should stay scannable at 100+ tabs.
2. **Windows are the organizing unit.** Tabs are grouped and moved by window, matching how Chrome already works.
3. **Fast and trustworthy.** Actions should feel instant and do exactly what they say. When something fails or loses data (like a moved tab's history), say so plainly.
4. **Portable by design.** Prefer choices that carry over to a cross-platform Chrome extension.
5. **Light humor, zero friction.** Personality shows up in the name and a few lines of copy, never in the user's way.
