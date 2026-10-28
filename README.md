# VFX Claude Skills

Agent skills for Claude, written by a working VFX compositor. They package the things a
general-purpose model gets wrong when you ask it for real pipeline work: Nuke gizmo syntax,
ASC CDL files and EXR metadata, and shipping a small free tool on Windows without it being
treated as malware.

Each skill is a folder with a `SKILL.md` (instructions Claude loads when the task matches),
reference notes, and small standard-library Python scripts it can run.

| Skill | What it's for |
|---|---|
| [`nuke-gizmo-builder`](skills/nuke-gizmo-builder) | Writing native `.gizmo` / Group `.nk` text that loads first time: knob IDs, Link knobs, expressions, the real Grade knob names, the wiring stack, design rules. Includes `validate_nk.py`, a static checker, and an example gizmo. |
| [`vfx-cdl-pipeline`](skills/vfx-cdl-pipeline) | Parsing `.cc` / `.cdl` / `.ccc` files (with the real-world quirks), reading EXR headers without dependencies, matching plates to CDLs with a dry-run plan, writing single `.cc` files. |
| [`windows-free-tool-release`](skills/windows-free-tool-release) | Turning a script into a Windows exe people trust: PyInstaller choices, Defender vs SmartScreen, unsigned-exe disclosure, Explorer context menus and overlays on Windows 11, release checklist. |

## Install

**Claude apps (claude.ai / desktop):** zip a skill folder (e.g. `nuke-gizmo-builder/`)
and upload it as a custom skill in Settings. Skills must be enabled for your account.

**Claude Code:**

```
/plugin marketplace add Marshallaltair/vfx-claude-skills
/plugin install vfx-claude-skills
```

or copy a skill folder into `~/.claude/skills/`.

**Other agents:** the `SKILL.md` files are plain Markdown; point your agent at them.

## The scripts work on their own too

```
python skills/nuke-gizmo-builder/scripts/validate_nk.py MyTool.gizmo --no-python
python skills/vfx-cdl-pipeline/scripts/cdl_tools.py exr-meta plate.1001.exr
python skills/vfx-cdl-pipeline/scripts/cdl_tools.py match ./cdl ./plates --key reelName
```

Python 3.8+, standard library only. `match` never writes anything.

## Limits, honestly

- `validate_nk.py` checks text, not Nuke. It catches the errors that stop a gizmo loading
  and several silent ones, but it cannot verify wiring or evaluate expressions. Open the
  result in Nuke once.
- EXR metadata keys for reel/clip names are not standardised. The CDL skill makes Claude
  inspect your real frames and ask, rather than guess.
- Explorer and Defender behaviour changes with Windows updates; the notes describe
  Windows 10/11 as of 2026.

## Contributing

Issues and pull requests welcome, especially: knob IDs or syntax variants from other Nuke
versions, CDL quirks from other labs, EXR metadata keys from cameras you work with.
Please never include frames, CDLs or paths from productions under NDA.

## Author

Giovanni Ricco, VFX compositor and teacher, Rome.

## Licence

MIT, see [LICENSE](LICENSE).

---

**In italiano:** skill per Claude nate dal lavoro quotidiano in compositing: scrivere gizmo
Nuke che si caricano al primo colpo, gestire CDL e metadata EXR in pipeline, e distribuire
piccoli tool gratuiti per Windows senza che vengano scambiati per virus. Gli script
funzionano anche da soli, solo libreria standard Python.
