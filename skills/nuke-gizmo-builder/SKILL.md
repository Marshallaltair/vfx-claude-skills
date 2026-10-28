---
name: nuke-gizmo-builder
description: Write Foundry Nuke gizmos (.gizmo) and Group nodes as native .nk text that loads first time, with no external Python. Use when asked to build, fix, extend or package a Nuke gizmo or tool, expose knobs on a Group, or turn a node tree into an installable gizmo.
---

# Nuke Gizmo Builder

Nuke reads a `.gizmo` file as plain Tcl-like text. Small syntax slips (an unbalanced brace,
a knob value written before its `addUserKnob`, a missing `end_group`) make the whole file
fail to load, often with an unhelpful error. This skill is the procedure for writing that
text correctly, and for designing a gizmo a compositor will actually want to use.

## Before writing anything

Settle these with the user, or state the assumption you took:

1. **Inputs**: names and order (e.g. `Source`, `Plate`, `mask`). Input 0 is the main pipe.
2. **Native only, or Python allowed?** Default to native only: no `knobChanged`, `onCreate`,
   `PyScript_Knob` buttons, no `menu.py` logic beyond registering the menu entry. A
   native gizmo survives every studio's Python environment and every Nuke version.
3. **Knob vocabulary**: name user-facing knobs with compositor terms the artist already
   knows (`blackpoint`, `whitepoint`, `lift`, `gain`, `gamma`, `offset`, `saturation`,
   `mix`), never generic labels like "value 1" or "pair 2".
4. **Target Nuke version** (affects the header line and which nodes exist).
5. **Credit and versioning**: author name for the help text and label; whether the file
   name carries a version (`ToolName_v003.gizmo`) during development.

## Workflow

1. Sketch the inner node tree as a list (node class, purpose, which parent knobs drive it).
2. Write the file following `references/nk-syntax.md`. Use `references/knobs.md` for
   `addUserKnob` type IDs and flags, and `references/pitfalls.md` before finishing.
3. Prefer **Link knobs** (`41`) to expose an inner knob unchanged; use **expressions**
   (`{{parent.knob}}`) when the inner value is derived (scaled, combined, clamped).
4. Keep the tree single-input-chain wherever possible. For multi-input wiring see the
   "Stack" section of `references/nk-syntax.md`, and say plainly that the wiring should be
   checked once in Nuke.
5. Run the validator: `python scripts/validate_nk.py path/to/Tool.gizmo --no-python`.
   Fix every error; read every warning.
6. Deliver the `.gizmo`, plus a 3-line install note (see below). If the user asked for a
   versioned file name, put the version in the name on every revision.

## Design rules that make a gizmo good

- One tab named after the tool, controls in the order the artist works: inputs/analysis
  first, the main grade or effect next, `mix` last. Put rarely used controls in a
  collapsible group (`addUserKnob {20 adv l Advanced n 1}` ... `{20 endGroup n -1}`).
- Every knob gets a tooltip (`t "..."`). The `help` knob on the gizmo explains purpose,
  inputs and the author credit.
- A `mix` knob and a `mask` input are expected on anything that modifies colour.
- Never bake absolute file paths, show/shot names or studio paths into a gizmo meant for
  sharing.
- Automatic analysis without Python is possible but costs render time: reduce the image
  (Reformat to a tiny box, or a large Blur) and read values with expressions. Warn that
  per-frame sampling in expressions is slow and recomputes on every frame; offer a
  "freeze at frame" knob (`FrameHold` driven by a parent knob) for static solves.
- Colour math lives in a `Grade`, `ColorMatrix`, `Expression` or `OCIOCDLTransform` node,
  not in a stack of Multiply/Add nodes.

## Install note to give the user

```
1. Copy ToolName.gizmo into your ~/.nuke folder (or any folder on NUKE_PATH).
2. Add to ~/.nuke/menu.py:
   nuke.menu('Nodes').addCommand('MyTools/ToolName', 'nuke.createNode("ToolName")')
3. Restart Nuke. The node class is the file name without .gizmo.
```

The node class equals the file name. Renaming `ToolName_v003.gizmo` to `ToolName.gizmo`
changes the class, and scripts saved with the old class will show it as missing. Release
builds should have a stable, unversioned name; track the version in a knob or the help text.
