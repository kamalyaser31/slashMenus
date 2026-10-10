# Slash Menus for NVDA

In many AI apps, typing `/` or `@` opens a short list: commands you can run, files you can attach, or people you can mention. You can move through this list with the arrow keys, but NVDA usually says nothing. This add-on makes NVDA read the list.

## Problems it solves

- **Silent command lists.** Typing `/` in ChatGPT, Claude or OpenCode opened a list of commands, but NVDA did not read it. You had to remember each command or type it in full.
- **Choosing without hearing.** Typing `@` to pick a file, or a person in a WhatsApp group, gave no speech. You could not know what you were choosing before you pressed Enter.
- **Silence while typing.** When you typed more letters to shorten the list, NVDA said nothing, so you could not tell if your item was still there.
- **Searching the screen by hand.** To find the selected item, you had to leave the message box and explore the screen, and the list often closed.

These problems are reported to the app makers on GitHub. Until the apps fix them, this add-on lets you use the lists:

- Claude: [anthropics/claude-code#94353](https://github.com/anthropics/claude-code/issues/94353)
- ChatGPT and Codex: [openai/codex#32375](https://github.com/openai/codex/issues/32375)
- OpenCode: [anomalyco/opencode#43771](https://github.com/anomalyco/opencode/issues/43771) (the add-on helps with the `/` and `@` lists only)
- WhatsApp: [nvaccess/nvda#18964](https://github.com/nvaccess/nvda/issues/18964)

## How to use it

There is nothing to set up and no new keys to learn. Just type as usual:

1. In the message box, type `/` or `@`.
2. NVDA says the name of the list (or "Suggestions") and the selected item.
3. Press Up Arrow or Down Arrow. NVDA reads each item you move to.
4. Type more letters to shorten the list, or press Backspace. NVDA reads the selected item again.
5. Press Enter or Tab to choose the item, or Escape to close the list.

The arrow keys work as normal everywhere else. The add-on only uses them while one of these lists is open.

NVDA does not say how many items the list has, because these apps only show part of a long list at a time.

## Supported apps

- ChatGPT: the desktop app, and the website in Chrome or Edge.
- Claude: the desktop app and the claude.ai website.
- OpenCode: the desktop app.
- WhatsApp: the desktop app and WhatsApp Web, for the `@` list in groups. WhatsApp has no `/` list.

Other apps that build their lists in the same way may also work. Apps that run inside a command window (terminal) are not supported.

## Installing

1. Download the `.nvda-addon` file from the [releases page](https://github.com/kamalyaser31/slashMenus/releases).
2. Open the file. NVDA asks if you want to install the add-on. Choose Yes.
3. Restart NVDA when asked.

## If a list stays silent

Please tell us, and include a few lines from the NVDA log:

1. Open the app and type `/` or `@` so the list opens.
2. Press NVDA+F1 to open the log.
3. Find the lines that start with `slashMenus` and copy them.
4. Open a new issue on the [issues page](https://github.com/kamalyaser31/slashMenus/issues) and paste the lines there, with the name of the app.

These lines never contain your messages or the names in the list, so they are safe to share.

## For developers

To build the add-on, run `scons` in the project folder. To run the checks, run `python run_tests.py`. All changes are listed in the [changelog](https://github.com/kamalyaser31/slashMenus/blob/main/CHANGELOG.md).

## Developer

- **Developer:** Kamal Yaser
- **Email:** [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- **Telegram:** [@kamalyaser31](https://t.me/kamalyaser31)

## License

This add-on is released under the GNU General Public License, version 2 (GPL v2).
