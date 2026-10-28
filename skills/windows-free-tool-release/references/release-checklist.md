# Release checklist

## Content sweep (do this first)
- [ ] No real project, show, client or shot names in UI, defaults, sample files,
      screenshots, tutorial images or videos. Replace them with neutral ones ("movie",
      "sh010").
- [ ] No absolute paths with usernames or studio drives in defaults or logs.
- [ ] Author name appears as the author wants it (and only that).

## Build
- [ ] Version number bumped in the code, the version resource and the file name.
- [ ] Built without UPX; version resource and icon present.
- [ ] Tested on a clean Windows user account, without Python installed.
- [ ] Tested with paths containing spaces, accented letters and UNC/NAS paths.
- [ ] First-run language matches the system; manual switch works.

## Trust
- [ ] VirusTotal scan done; false positives submitted if any.
- [ ] SHA-256 computed: `certutil -hashfile ToolName.zip SHA256` (Windows) or
      `sha256sum` (Linux/macOS).
- [ ] README/download page says it is unsigned and how to get past SmartScreen.

## Publish
- [ ] GitHub Release with notes (what's new, known issues), assets and checksums.
- [ ] Store page (Gumroad or other) links to the same version.
- [ ] Short demo video or GIF.
- [ ] LICENSE file and third-party licences of bundled libraries included.
