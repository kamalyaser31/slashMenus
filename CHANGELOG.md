# Changelog

- 2026-10-10: 0.1.0 - First version: reads the `/` and `@` suggestion lists in AI apps, finding the list through NVDA's buffer and the highlighted item by SELECTED, isCurrent, an odd class or background colour.
- 2026-10-10: From the first test round: the `aria-current` row is read directly and checked before anything else (speeds ChatGPT up and fixes its `@`), a scanned group with no marker is rejected (false positive in Claude), the marker that worked is remembered, the row scan is cut to 80, and the search starts only when `/` or `@` begins a word.
- 2026-10-10: From the second test round (NVDA froze six times): only the newest search chain runs, at most two row scans per chain each capped at 250 ms, and a per-step timing line in the log.
- 2026-10-10: From the third test round: removed the word-start condition (it most likely stopped ChatGPT and WhatsApp), one row scan per chain capped at 600 ms (the 250 ms cap was too short for OpenCode), and a log line for every trigger character, recording whether it was in a message box.
- 2026-10-10: Background colour now comes before class (fast in OpenCode), and a saved list unchanged for three polls is looked up again (Claude's slow arrows).
- 2026-10-10: Claude's `@` list is accepted when it overlaps the composer, there is no row scan while moving through a list, and a menu that has lost focus counts as closed (the arrows had been reading unrelated buttons after Claude's `/` menu closed).
- 2026-10-10: Confirmed with NVDA: ChatGPT desktop `/` and `@`, Claude desktop `/` and `@`, WhatsApp desktop `@`, OpenCode `/`; the README table updated to match.
- 2026-10-10: Speed-up: a list's rows are kept while only the arrows are pressed, the scan advances in both directions in turn, and two shorter scans (at about 0.3 and 0.9 s, 400 ms each) replace one.
- 2026-10-10: Arrow presses in OpenCode went from 300-450 ms to 63-93 ms. Also: the group check reads only the adjacent siblings, and a saved list stays alive while it is near the composer (sessions had been closing early).
- 2026-10-10: Confirmed in OpenCode: 62-78 ms per press with no early session ends. The normal background colour is learned from the first three rows instead of all of them, to speed up opening.
- 2026-10-10: Measured in OpenCode: opening 1.2 s (it was 2.3), 61-78 ms per press.
- 2026-10-10: Confirmed on the user's report: claude.ai `/` and `@`, WhatsApp Web `@`, OpenCode `@`; the README table updated.
- 2026-10-10: Scanned lists (OpenCode, WhatsApp) read their rows lazily, one sibling at a time on demand, instead of reading about 40 rows on opening; falls back to the full read if nothing is decided.
- 2026-10-10: Measured: reading the rows on opening fell from about 450 ms to 15 ms, and WhatsApp opens in 530 ms. The second scan was moved earlier (attempt 3) because OpenCode draws its list late.
- 2026-10-10: Renamed the add-on from Popup Announcer (`popupAnnouncer`) to Slash Menus (`slashMenus`); log lines now start with `slashMenus`.
- 2026-10-10: The add-on is now built with `scons` from the standard NVDA template; the code moved under `addon/` and its details live in `buildVars.py`.
