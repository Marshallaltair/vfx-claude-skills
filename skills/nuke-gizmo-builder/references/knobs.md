# addUserKnob reference

Form: `addUserKnob {TYPE name [l "label"] [t "tooltip"] [R min max] [flags...]}`

## Type IDs in common use

| ID | Knob            | Example                                                        |
|----|-----------------|----------------------------------------------------------------|
| 1  | String          | `addUserKnob {1 note l note}`                                  |
| 2  | File            | `addUserKnob {2 lut_file l "LUT file"}`                        |
| 3  | Int             | `addUserKnob {3 ref_frame l "reference frame"}`                |
| 4  | Enumeration     | `addUserKnob {4 mode l mode M {average median "max value"}}`   |
| 6  | Boolean         | `addUserKnob {6 invert_mask l "invert mask" +STARTLINE}`       |
| 7  | Float (slider)  | `addUserKnob {7 mix l mix R 0 1}`                              |
| 12 | XY              | `addUserKnob {12 center l center}`                             |
| 13 | XYZ             | `addUserKnob {13 pos l position}`                              |
| 14 | WH              | `addUserKnob {14 size l size R 0 100}`                         |
| 15 | BBox            | `addUserKnob {15 area l "sample area"}`                        |
| 18 | Color (RGB)     | `addUserKnob {18 lift l lift}`                                 |
| 19 | AColor (RGBA)   | `addUserKnob {19 gain l gain}`                                 |
| 20 | Tab / group     | `addUserKnob {20 ToolName}` (tab)                              |
| 22 | Python button   | `addUserKnob {22 analyse l Analyse T "..." +STARTLINE}` (Python) |
| 26 | Text / divider  | `addUserKnob {26 "" +STARTLINE}` or `{26 credit l "" T "by Author"}` |
| 41 | Link            | `addUserKnob {41 white l gain T Grade1.white}`                  |

If unsure of an ID, create the knob in Nuke (right click > Manage User Knobs), copy the
node, and read the line Nuke wrote.

## Groups inside a tab

```
addUserKnob {20 adv l Advanced n 1}    # start collapsible group
addUserKnob {7 softness}
addUserKnob {20 endGroup n -1}          # end group
```

Every `n 1` needs a matching `n -1`. To check how your Nuke writes a group that starts
closed, collapse it in the panel and copy the node.

## Useful flags

- `+STARTLINE` / `-STARTLINE`: start a new row, or stay on the same row as the previous knob.
- `+DISABLED`, `+INVISIBLE`, `+HIDDEN`: greyed out, not shown, hidden.
- `R min max`: slider range (values outside are still allowed unless clamped).
- `l "label"`: label shown in the panel. `t "tooltip"`: hover text.
- `T target` on a Link knob: the inner knob it mirrors (`Node.knob`).
- `M {a b c}` on an Enumeration: the menu entries (quote entries with spaces).

## Default values

Set them after the declaration, at the same indentation:

```
 addUserKnob {19 gain l gain}
 gain {1 1 1 1}
 addUserKnob {7 mix l mix R 0 1}
 mix 1
```

Link knobs take the inner node's value; set the default on the inner node instead.
