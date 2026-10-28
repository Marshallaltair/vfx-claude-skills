# Defender and SmartScreen

Two different things, often confused by users:

- **SmartScreen** ("Windows protected your PC"): reputation check on downloaded files.
  Unsigned files from a new publisher trigger it. It is not a detection; it goes away
  as enough people run the file, or immediately with a reputable signature.
  User path: More info, then Run anyway.
- **Microsoft Defender Antivirus** detection ("Trojan:Win32/..." quarantine): the file
  matched a signature or heuristic. This is what gets the exe deleted.

## Reducing false positives (Python/PyInstaller)

1. No UPX.
2. Prefer `--onedir` (zip the folder) over `--onefile`.
3. Rebuilding PyInstaller's bootloader from source gives a unique bootloader instead of
   the shared one many malware samples also use; it helps with some engines.
4. Version resource filled in; real icon; no obfuscators or packers.
5. Do not download or execute code at runtime; do not write to startup folders or the
   registry unless the user asked for it (installers that do this are expected to).
6. Avoid behaviour that looks like a dropper: extracting executables into temp and running
   them, hidden windows, self-deleting files.

## When it is flagged anyway

1. Check the exact detection name on VirusTotal; note which engines flag it.
2. Submit the file to Microsoft as a false positive (software developer submission), with
   a short description and a link to the source or download page.
3. Write to the other vendors' false-positive addresses if needed.
4. Each new build is a new file: expect to repeat after major changes.

## What to tell users (template)

> ToolName is free and not code-signed (a certificate costs more than the tool earns).
> Windows may show "Windows protected your PC": click More info, then Run anyway.
> SHA-256 of this release: `...`. Source code: <link>.
