# Plan: Slash Menus (generic NVDA add-on)

Status: draft for review. No code is written before approval.
Evidence: [../claude/popup_survey.md](../claude/popup_survey.md).
Name: `slashMenus` (renamed from `popupAnnouncer`).

## Goal

When `/` or `@` (and later `$`) opens a suggestion list in an AI app's composer, NVDA announces the list and reads the highlighted row as the arrows move it. Focus stays in the composer, which is how every surveyed app behaves.

## What the evidence supports

Ranked by how much NVDA itself has confirmed, because the milestones follow this order.

| Level | Apps | What is known |
|---|---|---|
| Confirmed through NVDA (IA2) | Claude desktop `/` and `@` | already working in the Claude add-on (background colour, SELECTED, focus moved to a nameless menu) |
| Confirmed through NVDA (IA2) | ChatGPT desktop `/` and `@` | the highlighted row is a `BUTTON` with `isCurrent=YES`; one buffer query on `IAccessible2::attribute_current`, filtered by distance from the composer, finds it; `@` appears only after about 1.5 s |
| Probed in NVDA, nothing found yet | OpenCode desktop, WhatsApp desktop | buffer ready, no list role, no `isCurrent`; hit-testing from the window stops at the outer `PANE` |
| DOM only (DevTools or source) | claude.ai, chatgpt.com, Gemini, WhatsApp Web, OpenCode source | roles and markers listed in the survey; not yet seen through NVDA |

Gemini's marker is `aria-activedescendant` on a wrapper, not on the focused element. Whether Chromium exposes that through IA2 is unknown, so Gemini is marked unverified, not designed for.

## Detection design

1. **Trigger.** Search only after a trigger character typed in an editable field (`TRIGGERS = ("/", "@")`, one constant), or while a list is open. Retry every 150 ms for about 1.5 s.
2. **Step A: cheap markers.** Buffer queries, in order:
   1. `IAccessible2::attribute_current` (ChatGPT);
   2. the SELECTED state (claude.ai `@`, Claude desktop `@`).
   Keep only rows next to the composer: horizontal overlap, and a vertical gap under 400 px. This filter already excluded WhatsApp's chat list and ChatGPT's `aria-current=page` sidebar link.
3. **Step B: role-less lists marked by class or colour** (OpenCode, WhatsApp, Claude `/`).
   1. Query the buffer for candidate rows by role: button, menu item, option.
   2. Keep the rows next to the composer.
   3. Group them by shared parent.
   4. Pick the odd one out: first by class (OpenCode), then by background colour, also checking the row's first child (WhatsApp marks an inner element).
4. **Reading.** Speak the row's name, then its description if it has one. Never speak a total count: lists are virtualised.

## Rules carried over from earlier failures

- **Bind the arrows only after a list is confirmed open.** Send the key first, then announce. Unbind on Escape, on focus loss, or after a timeout. A static binding broke browse mode in an earlier add-on.
- **Never walk the page tree on NVDA's main thread.** It cancelled COM calls in WhatsApp and froze NVDA in Claude. Use buffer queries, and bounded walks only inside a list already found.
- **Never write row names to the log.** Log roles, markers and name lengths only.
- **Handle a focus move to a nameless menu** (Claude desktop `/`), as the Claude add-on does.

## Coexistence with the Claude add-on (decided 2026-10-10)

The user chose to remove the Claude add-on from NVDA for the whole development period. Its source and its verified package (`../claude/dist/claudeAccessibility-0.1.0.nvda-addon`, identical to the source) stay as the stable copy and can be reinstalled at any time. The generic add-on therefore does not skip Claude: Claude becomes one of its test targets, including the `/` case where focus moves to a nameless menu.

## Milestones

Each milestone is checked live by the user before the next one starts. Nothing is released before the user confirms it works.

| # | Milestone | Live test by the user | Log lines I read |
|---|---|---|---|
| 0 | **Verify the step B query.** Reinstall `probe/` once with a buffer query for button, menu item and option rows near the composer. | In OpenCode and WhatsApp: type `@` or `/`, press Down twice | `popupProbe` lines: matched rows near the composer, with their class and background |
| 1 | Core plus step A: trigger, retry, `attribute_current`, the distance filter, dynamic arrow binding, speech | ChatGPT desktop `/` and `@`: hear the row change with each arrow; browse-mode arrows still work elsewhere | `slashMenus found` (method and time, no names) |
| 2 | SELECTED marker | claude.ai `@` in Chrome | same |
| 3 | Step B: odd class, then background colour | OpenCode `/` and `@`, then WhatsApp `@` | same |
| 4 | Claude desktop: `@` (SELECTED or background) and `/` (focus moved to a nameless menu) | Claude `/` and `@` | same |
| 5 | Gemini (only if milestone 0 or a probe shows the wrapper's active descendant is exposed) | Gemini `@` | same |

If milestone 0 shows that step B cannot find the rows, the plan stops there and step B is redesigned before any core code.

## Out of scope

- Terminals (anthropics/claude-code#100253): there is nothing in the accessibility tree to read.
- Gemini `/`: it has no popup.
- UIA-only apps and Firefox.
- Per-site JSON profiles: the markers cover the surveyed cases without them.

## Engineering

- New add-on folder `addons/slashMenus/`: `manifest.ini`, one global plugin, `scripts/build_addon.py` copied from the Claude add-on.
- `run_tests.py` tests only the pure functions (odd one out, marker order, distance filter) on fake objects.
- `ruff check --fix`, then `black`, then `flake8 --max-line-length 88`.
- The project keeps its own `task.md`, `project_state.md` and `CHANGELOG.md`, gets an entry in the workspace `AGENTS.md` index, and its `README.md` is written with the `readme-writer` skill.
- Planning, implementation and testing can be split between models by capacity, for example implementation delegated and reviewed here, with live tests by the user.
