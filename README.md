# Slash Menus for NVDA

When you type `/` or `@` in many AI apps, a list of suggestions appears: commands, files, people to mention. You can move through it with the arrow keys, but the screen reader says nothing, because the app only changes the highlight on screen. This add-on reads that list for you.

## What it does

- When a list opens after `/` or `@`, NVDA says its name (or "Suggestions") and the highlighted item.
- When you press Up or Down arrow, NVDA reads the newly highlighted item.
- When you type more letters to filter the list, or press Backspace, NVDA reads the item that is now highlighted.
- When you press Escape, Enter or Tab, the add-on lets the key through and stops listening.
- The arrow keys are taken over only while a list is open. Everywhere else, including browse mode, they work as usual.
- No total is announced, because these apps only draw part of a long list at a time.

## Target apps

Version 0.1.0 was built for these apps, from a study of how each one marks the highlighted item. "Confirmed" means tested with NVDA; "targeted" means built for it but not yet tested.

| App | `/` | `@` |
|---|---|---|
| ChatGPT desktop | confirmed | confirmed |
| ChatGPT in a Chromium browser | confirmed | targeted |
| Claude desktop | confirmed | confirmed |
| claude.ai | confirmed | confirmed |
| OpenCode desktop | confirmed | confirmed |
| WhatsApp desktop | no list | confirmed |
| WhatsApp Web | no list | confirmed |

Other apps that build their lists the same way may work too. Apps in a terminal are not supported, because the terminal exposes nothing to read.

## Installation

1. Build the package, or take the `.nvda-addon` file from a release.
2. Open the file and let NVDA install it.
3. Restart NVDA.

To build the package yourself:

```
scons
```

The package `slashMenus-<version>.nvda-addon` is written to the project folder. Its name, version and other details are set in [buildVars.py](buildVars.py).

## Reporting a problem

If a list stays silent, NVDA's log says what happened. Open it with NVDA+F1 and look for lines starting with `slashMenus`. They name the app and the method used, and never the items, so they are safe to share. Please send those lines with your report.

## Contributing

Bug reports and pull requests are welcome. Before changing the detection rules, run the checks:

```
python run_tests.py
```

Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## بيانات المطور (Developer Details)

- **المطور:** كمال ياسر (Kamal Yaser)
- **البريد الإلكتروني:** [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- **تيليجرام:** [@kamalyaser31](https://t.me/kamalyaser31)

---

## رخصة الاستخدام (License)

يخضع هذا المشروع لشروط رخصة MIT License مفتوحة المصدر.
