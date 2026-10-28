# ASC CDL reference

## The math

Per channel (R, G, B):

```
out = (in * slope + offset) ** power
```

Then saturation, using Rec.709 luma weights:

```
luma = 0.2126*R + 0.7152*G + 0.0722*B
out_c = luma + saturation * (c - luma)
```

- Slope default 1, offset default 0, power default 1, saturation default 1.
- Before the power step, negative values must be handled: the ASC spec clamps the SOP
  result; float pipelines commonly clamp only negatives to 0 so highlights above 1
  survive. Nuke's OCIOCDLTransform follows OCIO's implementation; if a tool must match
  Nuke exactly, test against it rather than re-implementing.
- Order matters: SOP first, saturation second.

## .cc example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="A001C003_230512_R1AB">
  <SOPNode>
    <Slope>1.0200 0.9900 1.0100</Slope>
    <Offset>-0.0100 0.0000 0.0050</Offset>
    <Power>1.0000 1.0000 0.9800</Power>
  </SOPNode>
  <SatNode>
    <Saturation>0.9500</Saturation>
  </SatNode>
</ColorCorrection>
```

## Real-world variations a parser must accept

- XML namespace present or absent (`urn:ASC:CDL:v1.01`, `v1.2`, none). Match on local
  tag names, not on namespaced names.
- `SatNode`, `SATNode`, older `ASC_SAT`; `SOPNode` or older `ASC_SOP`.
- Missing `SatNode` entirely: saturation = 1.
- `<Description>` elements anywhere, sometimes holding the clip name when `id` is empty.
- Comma decimal separators from badly localised tools (`1,02`): flag, do not guess.
- Empty or duplicate `id`. An empty id makes matching by id impossible; fall back to the
  file name and say so.
- Byte-order mark at the start of the file; Windows line endings.

## Choosing a format to write

Write `.cc` (one correction per file, file name = id) unless the user's pipeline asks for
something else: it is the easiest to copy per shot and every tool reads it.
