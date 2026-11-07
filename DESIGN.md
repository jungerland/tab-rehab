---
name: Tab Rehab
description: Every open Chrome tab on one page, grouped by window or site, built for a fast purge.
colors:
  ink: "#202124"
  ink-2: "#5f6368"
  ink-3: "#6b6f75"
  ground: "#ffffff"
  panel: "#f4f4f4"
  hover: "#f2f2f2"
  rule: "#e0e0e0"
  rule-strong: "#c4c4c4"
  blue: "#1a73e8"
  blue-ink: "#1765cc"
  blue-wash: "#e8f0fe"
  error: "#c5221f"
  snackbar: "#323232"
  snackbar-action: "#8ab4f8"
typography:
  headline:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, sans-serif"
    fontSize: "20px"
    fontWeight: 600
  title:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, sans-serif"
    fontSize: "13px"
    fontWeight: 600
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "tnum"
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 400
rounded:
  badge: "4px"
  control: "6px"
  card: "8px"
  pill: "15px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  row: "32px"
components:
  window-card:
    backgroundColor: "{colors.ground}"
    border: "1px solid {colors.rule}"
    rounded: "{rounded.card}"
  card-header:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    height: "40px"
  tab-row:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    height: "{spacing.row}"
  tab-row-hover:
    backgroundColor: "{colors.hover}"
  tab-row-selected:
    backgroundColor: "{colors.blue-wash}"
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.ground}"
    rounded: "{rounded.control}"
    height: "32px"
  button-secondary:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.blue}"
    border: "1px solid {colors.rule-strong}"
    rounded: "{rounded.control}"
    height: "32px"
  input-filter:
    backgroundColor: "{colors.ground}"
    border: "1px solid {colors.rule-strong}"
    rounded: "{rounded.control}"
    height: "32px"
    width: "300px"
  icon-button:
    backgroundColor: "transparent"
    textColor: "{colors.ink-2}"
    rounded: "50%"
    size: "28px"
  window-badge:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.badge}"
    size: "20px"
  toast:
    backgroundColor: "{colors.snackbar}"
    textColor: "{colors.ground}"
    rounded: "{rounded.control}"
---

# Design System: Tab Rehab

## Overview

**Direction: the category standard, played straight.** Tab Rehab looks the way Chrome's own tab search, OneTab, and Tab Manager Plus look: a plain list grouped by window, neutral grays, one blue accent, nothing extra. It should sit beside Chrome's settings pages without standing out. Brand lives in the name and in the craft of the details, not in a visual world.

This replaced the High-Density Grid look (white, ink, utility red) on 2026-11-07. The owner's monitors run a warm color tone, which turned the cool gray fills pink and made the red harsh. The fix is fewer fills and no red.

**Key characteristics:**
- White everywhere. Gray appears only as hover, small badges, and the duplicate pill.
- One accent: blue, for primary actions, selection, focus, and links.
- No red anywhere except error text.
- Rounded, Material-like controls: 6px buttons and fields, 8px cards, round icon buttons.
- One-line 32px rows in fixed columns.

## Colors

- **Blue** (`#1a73e8`): primary buttons (Close N selected, Close all N shown), secondary button text (Select duplicates, Refresh), checkbox accent, focus ring, the filter's focus border, drop target outline, "Hide tips" link.
- **Blue Wash** (`#e8f0fe`): selected rows, drop target fill, secondary button hover.
- **Ink** (`#202124`): titles and primary text. **Ink 2** (`#5f6368`): counts, hosts, labels, icons at rest.
- **Rule** (`#e0e0e0`): card borders and the bar's bottom line. **Rule Strong** (`#c4c4c4`): control borders.
- **Hover** (`#f2f2f2`) and **Panel** (`#f4f4f4`): row hover, window badges, the duplicate pill, `kbd`. These are true neutrals (equal RGB), never blue-tinted, so a warm screen doesn't turn them pink.
- **Error** (`#c5221f`): inline row errors only.
- Site monograms keep their per-host hue tints. They stand in for favicons.

### Named Rules
**The One Accent Rule.** Blue is the only accent. Closing tabs uses the same blue primary button as any other main action, the way Chrome's own dialogs do. Undo is the safety net, not color.

**The No Pink Rule.** No blue-tinted grays and no filled gray bands. Structure comes from white cards with a light border.

## Typography

The platform system font (San Francisco on Mac, Segoe UI on Windows, Roboto on Linux). Body and rows 13px, page title 20px/600, card headers 13px/600, hosts and labels 12px. Tabular numerals for counts.

## Layout

A short header (title and running total), then a sticky white bar with a bottom rule: the labeled filter, the "N of M" count, the window chips (hidden at rest, shown only while dragging, as drop targets), primary purge buttons when relevant, Select duplicates, the Group by menu (Window or Site), Columns, the Recently closed tray, Shortcuts, and Refresh. Below it, a one-line tips line the user can hide.

Window cards pack into fixed columns (Columns picker: Auto or 1 to 4, default 2; 16px gaps). Each window is assigned a column once, at load, by shortest column first, and stays there while tabs close. Windows are lettered by Chrome window id and keep their letter while the server runs. In Group by Site, cards are websites, biggest first, with single-tab sites sharing a "Sites with one tab" card at the end.

## Components

- **Window card:** white, 1px Rule border, 8px corners. Header 40px: select-all checkbox, "Window A" in 600, count in Ink 2, top two sites right-aligned. In Site view the header leads with the site monogram.
- **Tab row:** 32px, no dividers. Checkbox, drag grip (visible on hover or focus only), site monogram, title (ellipsis; click switches to the tab), host, then a round trash button. View, copy, and move appear on hover or focus over the host. Hover is Hover gray, selected is Blue Wash. In Site view the monogram is swapped for a window badge.
- **Window badge:** 20px, 4px corners, Panel gray with Ink letter. Used in chips, the Move-to menu, the Recently closed tray, and Site-view rows.
- **Buttons:** primary is filled Blue with white text; secondary is white with a Rule Strong border and Blue text, Blue Wash on hover. Icon buttons are 28px circles, gray on hover.
- **Duplicate pill:** "duplicate" in 11px Ink 2 on Panel gray, 8px radius, before the host.
- **Popovers and Move-to menu:** white, 1px Rule border, 8px corners, soft shadow (`0 4px 16px rgba(0,0,0,.12)`). They close on any outside click.
- **Toast:** Material snackbar, `#323232` with white text and a light-blue Undo.

## Do's and Don'ts

- **Do** keep every surface white; use borders, not fills, for structure.
- **Do** use standard controls (native select, checkbox, buttons) styled lightly.
- **Don't** add a second accent color, red, or tinted grays.
- **Don't** add decoration, textures, or a visual theme. The category standard is the point.
- **Don't** design mobile layouts.
