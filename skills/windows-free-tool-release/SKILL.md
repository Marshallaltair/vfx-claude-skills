---
name: windows-free-tool-release
description: Package and release a small free Windows desktop tool (Python or similar) as an exe people can trust - single exe or installer, Windows Defender and SmartScreen warnings, unsigned-exe disclosure, bilingual UI, Explorer context-menu entries, checksums, Gumroad/GitHub distribution. Use when turning a script into a Windows app for other people, or when users report "Windows protected your PC" or antivirus flags.
---

# Releasing a free Windows tool

Most of the work in shipping a small free tool is not the code: it is getting a stranger
to download an unsigned exe, run it, and not delete it when Windows complains. This skill
is the checklist for that, learned from shipping real free tools to VFX artists.

## 1. Decide the shape

| Shape | When | Notes |
|---|---|---|
| Portable exe (no install) | One-window utilities | Easiest to explain: "download, double click". |
| Installer (Inno Setup) | Anything touching Explorer (context menu, overlays, file associations) or needing an uninstaller | One `Setup.exe`; never ship `.cmd`/`.reg` files for users to run by hand. |

Ask the user which one; default to portable for tools that only open a window.

## 2. Build

- PyInstaller: prefer `--onedir` zipped, or `--onefile` if a single file matters more
  than false positives. `--onefile` unpacks itself to a temp folder at every start, which
  is exactly what malware does, so heuristics flag it more often. See
  `references/defender-smartscreen.md`.
- Do **not** compress with UPX. It is a common reason for antivirus flags.
- Add a Windows version resource (`--version-file`): product name, company/author,
  version, description. An exe with empty metadata looks anonymous to people and scanners.
- Add an `.ico` icon and a proper window title. Put the author credit in the UI.
- Build on a clean machine or venv with only the dependencies the tool imports.
- GUI toolkit licence: PyQt is GPL (or commercial); PySide6 is LGPL; Tkinter is free.
  A closed or MIT tool should not bundle PyQt.

## 3. Trust

- Without a code-signing certificate, SmartScreen will show "Windows protected your PC"
  until the file builds reputation. Say so up front, on the download page and in the
  README, with the two clicks needed (More info, Run anyway). Hiding it costs more trust
  than admitting it.
- Publish the SHA-256 of every release file next to the download.
- Upload the exe to VirusTotal before release; if Microsoft Defender flags it, submit it as
  a false positive through Microsoft's security intelligence submission portal.
- If the source can be published, publish it: an open repository answers "is it a virus?"
  better than any explanation.
- Signing options change over time (OV/EV certificates, Microsoft's cloud signing
  service); check current price and availability before recommending one.

## 4. Explorer integration

Read `references/explorer-integration.md` before promising "right-click menu" or
"coloured icons on files". Windows 11 puts classic context-menu entries under
"Show more options"; a first-level entry needs a packaged app identity. Overlay icons are
limited to a handful of slots shared with OneDrive, Dropbox and others.

## 5. Language

- Detect the system UI language at start and offer a manual switch in the app; keep all
  strings in one dictionary per language, not scattered in code.
- Write release notes and the store page in English if the audience is international,
  with the local language as a second section if useful.

## 6. Distribution

- GitHub Releases for the files and checksums; a Gumroad (or similar) page with a
  "$0+" price if the author wants an email list or optional tips.
- Release asset names include the version: `ToolName-1.2.0-win64.zip`.
- A 30-second screen recording of the tool doing its job sells it better than any text.
- Before publishing anything, sweep the build and every screenshot for real project
  names, client names, file paths and usernames (`references/release-checklist.md`).
