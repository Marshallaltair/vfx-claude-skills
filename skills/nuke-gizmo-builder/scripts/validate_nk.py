#!/usr/bin/env python3
"""Static checks for Nuke .gizmo / .nk text. Pure standard library, no Nuke needed.

Usage:
    python validate_nk.py Tool.gizmo [--no-python]

Exit code 0 = no errors (warnings may still be printed), 1 = errors found.
This catches the mistakes that stop a gizmo from loading or silently break it.
It does not run Nuke, so it cannot verify node wiring or that expressions evaluate.
"""
import re
import sys

KNOWN_KNOB_IDS = {1, 2, 3, 4, 6, 7, 12, 13, 14, 15, 18, 19, 20, 22, 26, 41}
PYTHON_KNOBS = ("knobChanged", "onCreate", "onDestroy", "updateUI", "autolabel",
                "beforeRender", "afterRender", "beforeFrameRender", "afterFrameRender")
GRADE_UI_TO_KNOB = {"lift": "black", "gain": "white", "offset": "add"}


def strip_strings(line):
    """Remove the content of double-quoted strings, honouring backslash escapes."""
    out, in_str, esc = [], False, False
    for ch in line:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
                out.append('"')
            continue
        if ch == '"':
            in_str = True
            out.append('"')
            continue
        out.append(ch)
    return "".join(out), in_str


def main(path, no_python):
    errors, warnings = [], []
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()

    # 1. brace balance (outside strings)
    depth, open_string_line = 0, None
    for i, raw in enumerate(lines, 1):
        clean, unterminated = strip_strings(raw)
        if unterminated and open_string_line is None:
            # multi-line strings are legal in .nk; only remember where it started
            open_string_line = i
        for ch in clean:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    errors.append(f"line {i}: closing brace without opening brace")
                    depth = 0
    if depth != 0:
        errors.append(f"unbalanced braces: {depth} more '{{' than '}}'")

    # 2. group / end_group pairing
    opens = [i for i, l in enumerate(lines, 1) if re.match(r"^\s*(Gizmo|Group|LiveGroup)\s*\{", l)]
    closes = [i for i, l in enumerate(lines, 1) if l.strip() == "end_group"]
    if len(opens) != len(closes):
        errors.append(f"{len(opens)} Gizmo/Group blocks but {len(closes)} end_group lines")
    if path.lower().endswith(".gizmo") and not any(re.match(r"^\s*Gizmo\s*\{", l) for l in lines):
        warnings.append("a .gizmo file normally has a top-level 'Gizmo {' block")

    # 3. user knobs: ids, declaration before value, link targets
    declared, value_before_decl = {}, []
    node_names = set(re.findall(r"^\s*name\s+(\S+)", text, re.M))
    for i, l in enumerate(lines, 1):
        m = re.match(r"^\s*addUserKnob\s*\{\s*(\d+)\s+(\S+)(.*)\}", l)
        if m:
            kid, kname, rest = int(m.group(1)), m.group(2).strip('"'), m.group(3)
            if kid not in KNOWN_KNOB_IDS:
                warnings.append(f"line {i}: knob type {kid} not in the common list, check it")
            if kid == 22 and no_python:
                errors.append(f"line {i}: Python button knob '{kname}' in a no-Python gizmo")
            if kid == 41:
                t = re.search(r"\bT\s+(\S+?)\.(\w+)", rest)
                if t:
                    tnode, tknob = t.group(1), t.group(2)
                    if tnode not in node_names:
                        errors.append(f"line {i}: link '{kname}' targets missing node '{tnode}'")
                    if tknob in GRADE_UI_TO_KNOB:
                        warnings.append(f"line {i}: link to '{tnode}.{tknob}' - on a Grade the "
                                        f"knob is '{GRADE_UI_TO_KNOB[tknob]}'")
            if kid not in (20, 26):
                declared[kname] = i
            continue
        v = re.match(r"^\s*(\w+)\s+\S", l)
        if v and v.group(1) not in declared:
            # a value for a knob that is declared later in the same node block
            rest_of_file = "\n".join(lines[i:])
            later = re.search(r"addUserKnob\s*\{\s*\d+\s+" + re.escape(v.group(1)) + r"\b",
                              rest_of_file)
            if later and not re.search(r"^\s*\}", rest_of_file[:later.start()], re.M):
                value_before_decl.append((i, v.group(1)))
    for i, k in value_before_decl:
        errors.append(f"line {i}: value for '{k}' appears before its addUserKnob line")

    # 4. parent.xxx references
    for i, l in enumerate(lines, 1):
        for ref in re.findall(r"parent\.(\w+)", l):
            if ref not in declared:
                errors.append(f"line {i}: expression uses parent.{ref} but no user knob '{ref}'")

    # 5. Output and Input checks (top level only is enough for most gizmos)
    if "Output {" not in text and not re.search(r"^\s*Output\s*\{", text, re.M):
        errors.append("no Output node")
    numbers = []
    for block in re.findall(r"^\s*Input\s*\{(.*?)^\s*\}", text, re.M | re.S):
        n = re.search(r"^\s*number\s+(\d+)", block, re.M)
        numbers.append(int(n.group(1)) if n else 0)
    if len(numbers) != len(set(numbers)):
        errors.append(f"Input nodes share a number: {sorted(numbers)}")

    # 6. Python callbacks
    if no_python:
        for i, l in enumerate(lines, 1):
            for k in PYTHON_KNOBS:
                if re.match(rf"^\s*{k}\s", l):
                    errors.append(f"line {i}: '{k}' is a Python callback in a no-Python gizmo")
            if "[python" in l:
                errors.append(f"line {i}: [python ...] Tcl call in a no-Python gizmo")

    # 7. sharing hygiene
    for i, l in enumerate(lines[2:], 3):
        if re.search(r"[A-Za-z]:[\\/]|/Users/|/home/|/mnt/|\\\\\w", l):
            warnings.append(f"line {i}: looks like an absolute path, remove before sharing")

    for w in warnings:
        print("WARNING", w)
    for e in errors:
        print("ERROR  ", e)
    print(f"{path}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(max(main(p, "--no-python" in sys.argv) for p in args))
