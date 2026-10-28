# Contributing

The most useful contributions are small, verified facts from real work:

- Nuke knob IDs, knob names or `.nk` syntax that differ between versions
- CDL / CCC files from other labs that the parser gets wrong
- EXR header keys your cameras or conform tools use for reel and clip names
- Windows Defender / SmartScreen behaviour you have actually seen

Rules:

1. Keep scripts standard-library Python 3.8+.
2. If you change `validate_nk.py`, run it on both files in
   `skills/nuke-gizmo-builder/examples/`: `ExampleGrade` must pass, `BrokenGrade` must fail.
3. Never commit frames, CDLs, scripts, shot names or paths from productions under NDA.
