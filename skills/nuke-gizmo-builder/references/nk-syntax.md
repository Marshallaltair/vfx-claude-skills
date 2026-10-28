# .nk / .gizmo syntax

## File skeleton

```
#! C:/Program Files/Nuke15.1v1/nuke-15.1.1.dll -nx
version 15.1 v1
Gizmo {
 inputs 1
 tile_color 0x5c8ad6ff
 help "ToolName v1.0 by Author Name\n\nWhat it does, what each input expects."
 addUserKnob {20 ToolName}
 addUserKnob {7 mix l mix t "Blend between input and result"}
 mix 1
}
 Input {
  inputs 0
  name Source
  xpos 0
  ypos 0
 }
 Grade {
  name Grade1
  mix {{parent.mix}}
  xpos 0
  ypos 80
 }
 Output {
  name Output1
  xpos 0
  ypos 160
 }
end_group
```

- The first line (`#! ...`) is a comment for the shell; Nuke ignores the path. The
  `version` line matters: a file saved with a newer version may warn when opened in an
  older Nuke. For wide compatibility, write the oldest version you actually tested.
- In a `.gizmo` the container is `Gizmo { ... }`. In a script you paste into Nuke, or
  in a Group you ship inside an `.nk`, it is `Group { ... }`. Both close with `end_group`
  after the inner nodes.
- The container's own knobs are inside its braces. **The inner nodes come after the
  closing brace**, indented by one space by convention, and the group ends with
  `end_group` on its own line. Nested groups each need their own `end_group`.
- Exactly one `Output` node per group. `Input` nodes define the gizmo's inputs.

## Input order

Each `Input` node has a `number` knob (0-based). Input 0 needs no `number` line.

```
 Input {
  inputs 0
  name mask
  number 1
 }
```

The input's `name` is the label on the arrow in the DAG. Name a mask input `mask`.

## Knob values

```
 knobname value
 knobname {r g b a}           # multi-value
 knobname {{expression}}      # expression: double braces
 knobname {{expr_r} {expr_g} {expr_b} {expr_a}}   # per-channel expressions
 knobname "string with spaces"
```

- Expressions referencing the gizmo's own knobs use `parent.knob` (or `parent.knob.r`
  for one channel). From outside a group, `GroupName.knob`.
- Tcl in string knobs: `[value parent.knob]`, `[knob parent.knob]`. In a string, escape
  literal `[` and `]` with a backslash, and literal `"` with `\"`.
- A user knob's value line must come **after** its `addUserKnob` line.

## Grade knob names (the UI labels differ)

| UI label   | Knob name    |
|------------|--------------|
| blackpoint | `blackpoint` |
| whitepoint | `whitepoint` |
| lift       | `black`      |
| gain       | `white`      |
| multiply   | `multiply`   |
| offset     | `add`        |
| gamma      | `gamma`      |

Linking `lift` to `Grade1.lift` fails silently; it must be `Grade1.black`.

## The stack (wiring)

The .nk format is a stack machine. Every node, once written, is pushed on a stack. A node
with `inputs N` takes its N inputs from the top of the stack. Helpers:

```
set N1a2b3c [stack 0]   # remember the node on top of the stack under a variable
push $N1a2b3c           # push it again later, to branch from it
push 0                  # push "nothing" (an unconnected input)
```

- A single-input chain needs nothing special: each node takes the previous node.
- `inputs 1+1` means one normal input plus a connected mask input (e.g. on Grade).
- For multi-input nodes (Merge2, Keymix, Copy...) the order in which inputs are pushed
  decides which arrow they land on. Do not guess. The reliable method: build the wiring
  once in Nuke, select the nodes, Ctrl+C, and paste into a text editor; Nuke puts the
  exact .nk text on the clipboard. Then edit knobs and expressions in text.
- If you must write multi-input wiring blind, say so to the user and ask them to check
  the arrows once in the DAG.

## Positions

`xpos`/`ypos` are optional. Leave a regular grid (80 to 100 px apart vertically) so the
inside of the gizmo is readable when the artist opens it.
