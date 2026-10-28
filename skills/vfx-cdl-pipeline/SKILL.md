---
name: vfx-cdl-pipeline
description: Work with ASC CDL colour decisions (.cc, .cdl, .ccc) and EXR plate metadata in a VFX pipeline - parse and validate CDL files, read EXR headers, match each plate sequence to its CDL and copy or apply it. Use for tools or scripts that distribute dailies/plate grades to shot folders, inspect EXR metadata, or build OCIOCDLTransform setups in Nuke.
---

# VFX CDL Pipeline

A lab or DIT delivers one CDL per camera clip. Compositing needs each one next to the
plate it belongs to, and the only reliable link between the two is usually a field in
the EXR header (reel, clip or tape name). This skill covers the formats, the matching
logic, and the failure cases that make naive scripts copy the wrong grade.

## Formats in one paragraph each

- **.cc**: a single `<ColorCorrection id="...">` element with `SOPNode` (Slope, Offset,
  Power) and `SatNode` (Saturation).
- **.cdl**: a `<ColorDecisionList>` containing one or more `<ColorDecision>`, each with a
  `<ColorCorrection>`.
- **.ccc**: a `<ColorCorrectionCollection>` with many `<ColorCorrection>` elements.

Details, the math and real-world variants are in `references/asc-cdl.md`.
EXR header structure and where reel/clip names hide is in `references/exr-metadata.md`.

## Matching procedure

1. **Inventory the CDLs**: `python scripts/cdl_tools.py parse <cdl_folder>`. This lists
   every correction with its id, source file and values, and flags malformed files.
2. **Inspect one plate per sequence**: `python scripts/cdl_tools.py exr-meta <frame.exr>`.
   Find which attribute carries the name that matches CDL ids. Do not assume a key name;
   it changes between cameras, labs and conform tools. Ask the user when unclear.
3. **Dry run**: `python scripts/cdl_tools.py match <cdl_folder> <plates_root> --key <attr>`.
   It reads the first frame of every sequence, normalises names, and prints a plan:
   matched, unmatched, ambiguous. Nothing is written.
4. Show the plan to the user. Only then copy, and **never overwrite an existing CDL
   without asking** (the existing one may be a supervised correction). When the match
   came from a `.cdl`/`.ccc` holding many corrections, write just that one with
   `write_cc()` instead of copying the whole collection into the shot.
5. Write the destination path from a template the studio can change, e.g.
   `{shot_dir}/publish/cc/{plate_type}/{id}.cc`. Never hardcode a show's folder layout.

## Normalisation rules for matching

- Compare case-insensitively, after stripping extensions and surrounding whitespace.
- Camera reel names often get truncated (8 chars for some EDL/tape conventions) or get a
  suffix (`_001`, `.mov`). Try exact match first, then prefix match, and report prefix
  matches as "probable", never silently accepted.
- Several plates in one shot (main plate, extra plates, elements) each have their own CDL.
  Derive the plate type from the sequence name or folder, not from the CDL.
- One CDL id matching two different sequences is normal (same clip, two shots). Two CDL
  files with the same id but different values is a delivery error: stop and report it.

## Applying a CDL in Nuke

Use `OCIOCDLTransform`: set `slope`, `offset`, `power`, `saturation`, or point `file` at
the .cc/.cdl/.ccc and set `cccid` for collections. Apply it in the plate's working/log
space as delivered by the lab (ask which space the CDL was made in; a CDL applied in the
wrong space looks plausible and is wrong).

## Building a tool on top of this

If the user wants a standalone app (e.g. a Windows exe), keep the core logic in a module
like `cdl_tools.py` with no GUI imports, so it can be tested from the command line and
reused in Nuke. See the `windows-free-tool-release` skill for packaging.
