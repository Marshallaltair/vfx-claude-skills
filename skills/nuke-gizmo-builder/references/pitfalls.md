# Pitfalls checklist

Go through this before delivering a gizmo.

## Load failures

- [ ] Braces balance. Count them outside quoted strings; `validate_nk.py` does this.
- [ ] Every `Gizmo {`/`Group {` has a matching `end_group`.
- [ ] User knob values appear after their `addUserKnob` line, never before.
- [ ] Quotes inside strings are escaped (`\"`), and so are literal `[` `]` in help text.
- [ ] Exactly one `Output` node in each group.
- [ ] No two `Input` nodes share the same `number`.

## Silent failures (loads, but wrong)

- [ ] Link knob targets exist and use real knob names (`Grade1.white`, not `Grade1.gain`).
- [ ] Every `parent.xxx` in an expression refers to a knob the gizmo actually declares.
- [ ] Colour knobs linked across types: an RGBA knob (19) driving an RGB knob (18) is fine
      with per-channel expressions; a Link knob must match the target's type.
- [ ] The `mix` knob actually reaches the node doing the work (or a final Dissolve/Keymix).
- [ ] Mask input: decide what happens when it is not connected (usually: effect everywhere).
- [ ] Expressions that sample pixels are evaluated per frame; check the cost on a long shot.

## Sharing

- [ ] No absolute paths, show codes, shot names, studio drive letters or usernames.
- [ ] `help` text: what it does, inputs, author, version, licence.
- [ ] Python-free if promised: no `knobChanged`, `onCreate`, `onDestroy`, `updateUI`,
      no type-22 buttons. Run `validate_nk.py --no-python`.
- [ ] Release file name is stable (the node class is the file name).
