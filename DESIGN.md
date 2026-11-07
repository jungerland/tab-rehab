---
name: Tab Rehab
description: Every open Chrome tab on one dense page, built for a fast purge.
colors:
  utility-red: "#d7000f"
  red-ink: "#b5000c"
  red-wash: "#fff1f1"
  ink: "#16181b"
  ink-2: "#4a5059"
  ink-3: "#5f6670"
  ground: "#ffffff"
  panel: "#f3f4f6"
  row-hover: "#f7f8fa"
  rule: "#d5d9de"
  row-rule: "#eceef1"
  rule-strong: "#8a919b"
typography:
  headline:
    fontFamily: "Hiragino Sans, Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 800
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Hiragino Sans, Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 700
  body:
    fontFamily: "Hiragino Sans, Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "tnum"
  row-title:
    fontFamily: "Hiragino Sans, Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
  label:
    fontFamily: "Hiragino Sans, Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 400
rounded:
  hairline: "1px"
  sm: "2px"
spacing:
  xxs: "2px"
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "10px"
  xl: "16px"
  row: "30px"
components:
  window-tab:
    backgroundColor: "{colors.utility-red}"
    textColor: "{colors.ground}"
    typography: "{typography.title}"
    padding: "0 6px"
    width: "26px"
  window-header:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    height: "28px"
  tab-row:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.row-title}"
    height: "{spacing.row}"
  tab-row-selected:
    backgroundColor: "{colors.red-wash}"
  button-purge:
    backgroundColor: "{colors.utility-red}"
    textColor: "{colors.ground}"
    rounded: "{rounded.sm}"
    padding: "0 12px"
    height: "28px"
  button-purge-hover:
    backgroundColor: "{colors.red-ink}"
  window-chip:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    height: "26px"
  input-filter:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 8px"
    height: "28px"
    width: "280px"
  icon-button:
    backgroundColor: "transparent"
    textColor: "{colors.ink-3}"
    rounded: "{rounded.sm}"
    size: "24px"
  toast:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
    rounded: "{rounded.sm}"
    padding: "10px 12px"
---

# Design System: Tab Rehab

## Overview

**Creative North Star: "The Departure Board"**

Tab Rehab borrows the grammar of a Japanese high-density portal: white ground, near-black ink, cool gray hairlines and panel fills, and one utility red. The page exists so a 100-tab purge reads as one scan, so density is the feature. Rows are one line and 30px tall, window modules pack into columns, and every pixel of chrome either names a window, counts something, or closes something.

The system is flat and ruled. Structure comes from hairlines, a 2px ink rule under the sticky bar, and gray header bands, not from cards or shadows. Red carries meaning, never decoration: a window's letter tab, and the act of purging. Everything else is ink on white at three steps of gray.

Desktop only. There are no mobile layouts and none should be designed.

**Key Characteristics:**
- One-line, fixed-height rows (30px) with ellipsis, never wrapping.
- A red letter tab (A, B, C...) names each window everywhere it appears.
- Hairline rules and gray bands instead of shadows or rounded cards.
- Near-square corners (2px) throughout.
- Tabular numerals everywhere, since counts are the main data.

## Colors

A white-and-ink palette with three grays and a single utility red that is spent only on identity and purge.

### Primary
- **Utility Red** (`utility-red`): the window letter tab (module header, bar chips, Move-to menu, recently closed tray), the purge buttons, checkbox accent, text selection, and the filter caret. Red on hover for the trash button.
- **Pressed Red** (`red-ink`): purge button hover, the trash icon when its row is hovered, focused, or selected, and text links inside the tray.
- **Selection Wash** (`red-wash`): background of a row checked for closing.

### Neutral
- **Ink** (`ink`): primary text, the 2px rule under the sticky bar, focus outlines, drop-target outlines, and the toast background.
- **Slate** (`ink-2`): secondary text: totals, counts, the hint line, field labels, Shortcuts descriptions.
- **Pewter** (`ink-3`): tertiary text: hosts, top domains, placeholder, and resting action icons (including trash).
- **Ground** (`ground`): page and module background.
- **Panel Gray** (`panel`): the sticky bar, window header bands, and the drop-target fill.
- **Row Hover** (`row-hover`): row background on hover or focus.
- **Hairline** (`rule`): module borders and section dividers.
- **Row Hairline** (`row-rule`): the faint divider between rows.
- **Strong Rule** (`rule-strong`): input, chip, and popover borders, the grip, and the scrollbar thumb.

Site monograms are the one place other hues appear. Each host gets a hue from its name, drawn as a pale tint behind a dark letter of the same hue (`hsl(h 55% 91%)` behind `hsl(h 60% 26%)`). They stay 18px and quiet.

### Named Rules
**The Two Meanings Rule.** Red means a window's identity or the act of purging. It is not used for hover, drop targets, menu highlight, or emphasis. Drop targets and menu hover use an ink outline on Panel Gray instead.

**The Quiet Trash Rule.** The trash icon rests in Pewter. It turns red only when its row is hovered, focused, or selected, and fills red on direct hover. At 100 tabs, 100 red icons would drown the window tabs.

## Typography

**Body Font:** Hiragino Sans (with Hiragino Kaku Gothic ProN, Segoe UI, Noto Sans, system-ui)

**Character:** a compact gothic sans at small sizes, chosen for density and clean Latin and numerals. One family does all the work; hierarchy comes from weight, not size.

### Hierarchy
- **Headline** (800, 19px, -0.02em): the page title only.
- **Title** (700, 12px): window header names, window letter tabs, chip counts, purge buttons.
- **Row Title** (400, 12.5px): tab titles in rows. The only text slightly larger than body, because it is what the eye scans.
- **Body** (400, 12px, 1.4): everything else, with tabular numerals on by default.
- **Label** (400, 11px): hosts in rows and `kbd` keys.

### Named Rules
**The Weight Not Size Rule.** The ramp spans 11 to 19px. New hierarchy is made with weight (400, 600, 700) and color (Ink, Slate, Pewter), not by adding sizes.

**The Counted Rule.** Tabular numerals stay on page-wide. Counts are the data.

## Layout

A sticky Panel Gray bar sits under a short header and holds, left to right: the labeled filter, the "N of M" count, one chip per window (hidden at rest, so the bar stays quiet; the chips appear only while a tab is being dragged, as drop targets for windows that are off screen), red purge buttons when relevant (close selected, close all shown), a white "Select N duplicates" button, then the Columns picker, the recently closed tray, Shortcuts, and Refresh pushed right. Chips sit before the buttons so they never shift when one appears. A 2px Ink rule closes the bar. Below it, a one-line tips hint the user can hide (remembered), then the window modules. Duplicate rows carry a small bordered "duplicate" tag in Slate before the host; it is not red, because selecting is not purging.

Modules pack into fixed columns (at least 460px wide, 10px gap, 10px between modules), so short windows sit under each other instead of leaving holes. Each window is assigned to a column once, at page load, by shortest column first, and stays there while tabs close; the page repacks only when a window resize changes the column count. Windows are lettered by Chrome window id and keep their letter for as long as the server runs. Page padding is 16px at the sides.

Rows are a fixed grid: checkbox, grip, monogram, title (flexible, ellipsis), host (max 170px), trash. View, copy, and move appear on hover or focus as an overlay on top of the host cell, so the row never reflows.

The spacing scale is small and tight: 2, 4, 6, 8, 10, 16px, plus the 30px row unit.

## Elevation & Depth

Flat by default. Depth is drawn with rules and fills: hairline module borders, Panel Gray header bands, and the 2px Ink rule under the sticky bar. Shadows exist only on things that float over the page.

### Shadow Vocabulary
- **Float** (`box-shadow: 0 2px 6px rgba(22,24,27,.16)`): popovers (tray, Shortcuts) and the Move-to menu.
- **Toast** (`box-shadow: 0 8px 24px rgba(22,24,27,.25)`): the undo toast at bottom left.

### Named Rules
**The Only-What-Floats Rule.** If it sits in the page flow, it has no shadow. Only popovers, menus, and the toast lift.

## Shapes

Near-square everywhere: 2px corners on buttons, chips, inputs, monograms, `kbd`, and the toast. Modules and popovers are square-cornered with a 1px border. The window letter tab is a solid red block that fills the full height of its header or chip, flush left, which makes it read like a file tab.

## Components

### Window Letter Tab (signature)
A solid red block, white bold letter, at least 26px wide, full height of its container. It names a window in the module header, the bar chip, the Move-to menu, and each row of the recently closed tray. Any new surface that refers to a window uses it.

### Window Module
- **Border:** 1px Hairline, square corners, white ground.
- **Header:** 28px Panel Gray band with a Strong Rule underline. Letter tab, "Window A" in bold, tab count in Slate, top two domains in Pewter pushed right with ellipsis.
- **Drop target:** 2px Ink outline (inset) and Panel Gray fill while a tab is dragged over.

### Tab Row
- **Shape:** 30px, one line, Row Hairline divider, no last-row divider.
- **States:** hover or focus gets Row Hover; selected gets Selection Wash; moving or busy drops to 45% opacity.
- **Actions:** view, copy, move as 24px icon buttons (15px stroked SVG, 1.6 stroke) overlaying the host cell on hover or focus. Trash is always present (see The Quiet Trash Rule).
- **Error:** a row error replaces the host text inline, in bold Ink (not red). The error page uses an Ink top rule. Red stays reserved for window identity and purge.

### Buttons
- **Purge (primary):** Utility Red, white bold text, 28px tall, 12px side padding, 2px corners. Hover deepens to Pressed Red. Only purge actions use it.
- **Bar controls (Tray, Shortcuts, Select duplicates, Refresh, Columns):** white, 1px Strong Rule border, 28px, 2px corners; border goes Ink on hover or when open.
- **Refresh:** a text link with a Strong Rule underline that turns Ink on hover.
- **Icon buttons:** transparent, Pewter, 24px; hover gets a light gray fill and Ink.

### Chips
- **Style:** white, 1px Strong Rule border, 26px tall, 2px corners, letter tab flush left, bold count.
- **State:** hover turns the border Ink. Same Ink-outline drop-target treatment as modules.

### Inputs / Fields
- **Style:** 280px by 28px, white, 1px Strong Rule border, 2px corners, 13px text, Pewter placeholder, red caret. Always paired with a visible label.
- **Focus:** the global 2px Ink outline, 1px offset.

### Popovers and Menu
White, 1px Strong Rule border, Float shadow. The Move-to menu lists windows by letter tab; hover and keyboard focus use Panel Gray with an inset 2px Ink outline.

### Toast
Ink background, white text, 2px corners, Toast shadow, bottom left. Its action (Undo) is a white underlined text button.

## Do's and Don'ts

### Do:
- **Do** use the red letter tab whenever a window is named, on any surface.
- **Do** keep rows one line at 30px and truncate with ellipsis.
- **Do** show drop targets and menu highlight with a 2px Ink outline on Panel Gray.
- **Do** theme browser surfaces from the palette: scrollbars in Strong Rule on Panel Gray, red selection and caret, Ink focus outlines.
- **Do** keep row actions as overlays so revealing them never shifts the row.

### Don't:
- **Don't** use red for hover, emphasis, drop targets, or decoration (The Two Meanings Rule).
- **Don't** give in-flow elements shadows or rounded card corners above 2px.
- **Don't** add type sizes to create hierarchy; use weight and the three grays.
- **Don't** design mobile layouts.

## Open (not yet decided)

These were considered in the finish review and deliberately not taken. They are open questions, not decisions.

- **Display face.** The page title is set in the platform sans. A self-hosted condensed face would suit the world but means shipping a font file inside a single-file tool.
- **DIN-style numerals** for counts and chips.
- **Tag badges** on rows.
