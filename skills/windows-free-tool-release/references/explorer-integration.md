# Explorer integration on Windows 10/11

## Context menu

- **Classic verbs** (registry keys under `HKCU\Software\Classes\*\shell\YourVerb` and
  `...\Directory\shell\YourVerb`): simple, no packaging, work for files on network
  drives too. On Windows 11 they appear only under "Show more options" (Shift+F10).
- **First-level entries on Windows 11** need an `IExplorerCommand` handler (a COM DLL)
  registered through an app package with identity (MSIX, or a sparse package for an
  unpackaged app). More work, and the sparse package must be signed, even with a
  self-signed certificate the installer trusts. Promise this only if the user accepts
  the cost.
- Cascading submenus (one entry, several colours or actions): `SubCommands` /
  `ExtendedSubCommandsKey` for classic verbs; `IEnumExplorerCommand` for the modern menu.
- Register per user (HKCU) when possible: no admin prompt, clean uninstall.
- Multi-selection: classic verbs launch one process per file unless you use
  `MultiSelectModel` or a DropTarget/single-instance pattern; plan for 500 selected JPGs.

## Icon overlays

- Windows supports only about 15 overlay handlers system-wide, sorted alphabetically by
  key name; OneDrive, Dropbox, Git clients and others take most of them. Yours may simply
  not show. Users who do not use those apps are the happy case.
- Overlays are drawn by a shell extension DLL loaded into Explorer: a crash in it crashes
  Explorer. Keep it tiny and defensive.
- Alternatives that need no shell extension: folder icons via `desktop.ini` (folders only),
  NTFS alternate data streams or a sidecar database to store tags, plus the app's own view
  to sort/filter by tag.

## Storing per-file data (tags, colours)

- NTFS alternate data streams travel with the file on NTFS but are lost on FAT/exFAT,
  in zips, on many NAS shares and in cloud sync. A sidecar database keyed by path is
  robust but breaks when files are moved outside the app. State the trade-off.
- Windows' own "Tags" property exists only for some formats (JPEG, Office files),
  through the property system.

## Uninstall

Remove every registry key, scheduled task and file the installer created. Test
install, uninstall, reinstall on a clean user profile before release.
