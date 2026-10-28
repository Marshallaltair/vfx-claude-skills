#!/usr/bin/env python3
"""CDL and EXR metadata tools. Standard library only.

  python cdl_tools.py parse <file_or_folder>            list corrections as JSON
  python cdl_tools.py exr-meta <frame.exr>              print EXR header attributes
  python cdl_tools.py match <cdl_folder> <plates_root> --key <attribute> [--json]
                                                         dry-run plan, writes nothing

Import it as a module for real tools: parse_cdl_file(), read_exr_header(),
find_sequences(), build_plan().
"""
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

# ----------------------------------------------------------------- CDL parsing


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _floats(text, n, where, problems):
    if text is None:
        return None
    if "," in text:
        problems.append(f"{where}: comma in numbers ('{text.strip()}'), check locale")
        return None
    try:
        vals = [float(v) for v in text.split()]
    except ValueError:
        problems.append(f"{where}: not numeric ('{text.strip()}')")
        return None
    if len(vals) != n:
        problems.append(f"{where}: expected {n} values, got {len(vals)}")
        return None
    return vals


def _parse_correction(el, source):
    problems = []
    cid = (el.get("id") or "").strip()
    sop = {"slope": [1.0, 1.0, 1.0], "offset": [0.0, 0.0, 0.0], "power": [1.0, 1.0, 1.0]}
    sat = 1.0
    desc = None
    for node in el.iter():
        t = _local(node.tag)
        if t in ("Slope", "Offset", "Power"):
            v = _floats(node.text, 3, f"{source}:{cid or '?'}:{t}", problems)
            if v:
                sop[t.lower()] = v
        elif t == "Saturation":
            v = _floats(node.text, 1, f"{source}:{cid or '?'}:Saturation", problems)
            if v:
                sat = v[0]
        elif t == "Description" and node.text and desc is None:
            desc = node.text.strip()
    if not cid:
        problems.append(f"{source}: correction without id, using file name")
        cid = os.path.splitext(os.path.basename(source))[0]
    return {"id": cid, "source": source, "slope": sop["slope"], "offset": sop["offset"],
            "power": sop["power"], "saturation": sat, "description": desc,
            "problems": problems}


def parse_cdl_file(path):
    """Return a list of correction dicts from a .cc, .cdl or .ccc file."""
    with open(path, "rb") as f:
        data = f.read()
    data = data.lstrip(b"\xef\xbb\xbf")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        return [{"id": None, "source": path, "problems": [f"XML error: {e}"]}]
    if _local(root.tag) == "ColorCorrection":
        return [_parse_correction(root, path)]
    found = [el for el in root.iter() if _local(el.tag) == "ColorCorrection"]
    if not found:
        return [{"id": None, "source": path, "problems": ["no ColorCorrection element"]}]
    return [_parse_correction(el, path) for el in found]


def write_cc(correction, path, overwrite=False):
    """Write one correction as a standalone .cc file. Use this instead of copying a
    .cdl/.ccc that holds many corrections. Refuses to overwrite unless told to."""
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(path)
    f3 = lambda v: " ".join(f"{x:.6f}" for x in v)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<ColorCorrection id="{correction["id"]}">\n'
           "  <SOPNode>\n"
           f'    <Slope>{f3(correction["slope"])}</Slope>\n'
           f'    <Offset>{f3(correction["offset"])}</Offset>\n'
           f'    <Power>{f3(correction["power"])}</Power>\n'
           "  </SOPNode>\n"
           "  <SatNode>\n"
           f'    <Saturation>{correction["saturation"]:.6f}</Saturation>\n'
           "  </SatNode>\n"
           "</ColorCorrection>\n")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)


def collect_cdls(folder_or_file):
    paths = []
    if os.path.isfile(folder_or_file):
        paths = [folder_or_file]
    else:
        for d, _, files in os.walk(folder_or_file):
            paths += [os.path.join(d, f) for f in files
                      if f.lower().endswith((".cc", ".cdl", ".ccc")) and not f.startswith("._")]
    out = []
    for p in sorted(paths):
        out += parse_cdl_file(p)
    return out


# ----------------------------------------------------------------- EXR header

_FIXED = {"int": "<i", "float": "<f", "double": "<d", "v2i": "<2i", "v2f": "<2f",
          "v3i": "<3i", "v3f": "<3f", "box2i": "<4i", "box2f": "<4f", "rational": "<iI",
          "timecode": "<2I", "keycode": "<7i"}
_COMPRESSION = ["none", "rle", "zips", "zip", "piz", "pxr24", "b44", "b44a", "dwaa", "dwab"]


def _read_cstr(f):
    b = bytearray()
    while True:
        c = f.read(1)
        if not c:
            raise ValueError("unexpected end of file in header")
        if c == b"\0":
            return b.decode("latin-1")
        b += c
        if len(b) > 255:
            raise ValueError("attribute name too long, file corrupt?")


def read_exr_header(path):
    """Return {name: value} for the first part's header. Reads only the header bytes."""
    attrs = {}
    with open(path, "rb") as f:
        if f.read(4) != b"\x76\x2f\x31\x01":
            raise ValueError(f"{path}: not an OpenEXR file")
        version = struct.unpack("<I", f.read(4))[0]
        attrs["_version_flags"] = {"tiled": bool(version & 0x200), "deep": bool(version & 0x800),
                                   "multipart": bool(version & 0x1000)}
        while True:
            name = _read_cstr(f)
            if name == "":
                break
            typ = _read_cstr(f)
            size = struct.unpack("<i", f.read(4))[0]
            raw = f.read(size)
            if typ == "string":
                val = raw.decode("utf-8", errors="replace")
            elif typ == "stringvector":
                val, i = [], 0
                while i + 4 <= len(raw):
                    n = struct.unpack_from("<i", raw, i)[0]
                    val.append(raw[i + 4:i + 4 + n].decode("utf-8", errors="replace"))
                    i += 4 + n
            elif typ in _FIXED and struct.calcsize(_FIXED[typ]) == size:
                v = struct.unpack(_FIXED[typ], raw)
                val = v[0] if len(v) == 1 else list(v)
                if typ == "timecode":
                    tc = v[0]
                    h = (tc >> 28 & 3) * 10 + (tc >> 24 & 15)
                    m = (tc >> 20 & 7) * 10 + (tc >> 16 & 15)
                    s = (tc >> 12 & 7) * 10 + (tc >> 8 & 15)
                    fr = (tc >> 4 & 3) * 10 + (tc & 15)
                    val = f"{h:02d}:{m:02d}:{s:02d}:{fr:02d}"
            elif typ == "compression" and size == 1:
                val = _COMPRESSION[raw[0]] if raw[0] < len(_COMPRESSION) else raw[0]
            else:
                val = f"<{typ}, {size} bytes>"
            attrs[name] = val
    return attrs


# ----------------------------------------------------------------- sequences

_FRAME = re.compile(r"^(?P<base>.*?)(?P<sep>[._])(?P<frame>\d+)\.exr$", re.I)


def find_sequences(root):
    """Yield (folder, sequence_base, first_frame_path) for every EXR sequence under root."""
    for d, _, files in os.walk(root):
        seqs = {}
        for fn in files:
            if fn.startswith(".") or not fn.lower().endswith(".exr"):
                continue
            p = os.path.join(d, fn)
            try:
                if os.path.getsize(p) == 0:
                    continue
            except OSError:
                continue
            m = _FRAME.match(fn)
            base, frame = (m.group("base"), int(m.group("frame"))) if m else (fn[:-4], 0)
            if base not in seqs or frame < seqs[base][0]:
                seqs[base] = (frame, p)
        for base, (_, p) in sorted(seqs.items()):
            yield d, base, p


# ----------------------------------------------------------------- matching


def _norm(s):
    s = os.path.splitext(str(s).strip())[0] if s else ""
    return s.lower()


def build_plan(cdl_folder, plates_root, key):
    cdls = collect_cdls(cdl_folder)
    by_id = {}
    conflicts = []
    for c in cdls:
        if not c.get("id"):
            continue
        k = _norm(c["id"])
        if k in by_id and (by_id[k]["slope"], by_id[k]["offset"], by_id[k]["power"],
                           by_id[k]["saturation"]) != (c["slope"], c["offset"], c["power"],
                                                       c["saturation"]):
            conflicts.append({"id": c["id"], "files": [by_id[k]["source"], c["source"]]})
        by_id.setdefault(k, c)
    plan = {"matched": [], "probable": [], "unmatched": [], "ambiguous": [],
            "cdl_conflicts": conflicts,
            "cdl_problems": [p for c in cdls for p in c.get("problems", [])]}
    for folder, base, first in find_sequences(plates_root):
        try:
            meta = read_exr_header(first)
        except (ValueError, OSError, struct.error) as e:
            plan["unmatched"].append({"sequence": base, "folder": folder, "reason": str(e)})
            continue
        value = meta.get(key)
        entry = {"sequence": base, "folder": folder, "first_frame": first, "key_value": value}
        if value is None:
            entry["reason"] = f"attribute '{key}' not in header"
            plan["unmatched"].append(entry)
            continue
        v = _norm(value)
        if v in by_id:
            entry["cdl"] = by_id[v]["source"]
            plan["matched"].append(entry)
            continue
        prefix = [c for k, c in by_id.items() if k.startswith(v) or v.startswith(k)]
        if len(prefix) == 1:
            entry["cdl"] = prefix[0]["source"]
            plan["probable"].append(entry)
        elif len(prefix) > 1:
            entry["candidates"] = [c["source"] for c in prefix]
            plan["ambiguous"].append(entry)
        else:
            entry["reason"] = "no CDL with this id"
            plan["unmatched"].append(entry)
    return plan


# ----------------------------------------------------------------- CLI


def _main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "parse":
        print(json.dumps(collect_cdls(argv[1]), indent=2))
    elif cmd == "exr-meta":
        print(json.dumps(read_exr_header(argv[1]), indent=2, ensure_ascii=False))
    elif cmd == "match" and len(argv) >= 3 and "--key" in argv:
        key = argv[argv.index("--key") + 1]
        plan = build_plan(argv[1], argv[2], key)
        if "--json" in argv:
            print(json.dumps(plan, indent=2))
        else:
            for section in ("matched", "probable", "ambiguous", "unmatched"):
                print(f"\n== {section.upper()} ({len(plan[section])})")
                for e in plan[section]:
                    extra = e.get("cdl") or e.get("candidates") or e.get("reason")
                    print(f"  {e['sequence']}  [{e.get('key_value')}]  ->  {extra}")
            for c in plan["cdl_conflicts"]:
                print(f"\n!! same id '{c['id']}' with different values: {c['files']}")
            for p in plan["cdl_problems"]:
                print(f"\n!! {p}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
