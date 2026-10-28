# EXR header metadata

## Structure (what the parser in cdl_tools.py reads)

1. Magic number: bytes `76 2f 31 01`.
2. Version field (4 bytes). Bit `0x200` = tiled, `0x800` = deep data, `0x1000` = multi-part.
3. Attributes, repeated: `name\0` `type\0` `int32 size` `size bytes of value`.
4. A single `\0` ends the header (in multi-part files each part has its own header, and an
   extra `\0` ends the list).

Only the header is needed for metadata, so reading the first few kilobytes of the first
frame is fast even over a NAS. Never read the full frame for this.

## Where names hide

There is no standard attribute for "reel" or "clip". Typical places:

- Camera vendors write their own keys (often namespaced, e.g. `com.<vendor>.<...>`).
- Conform and debayer tools add keys such as reel name, clip name, tape name, source
  file name; the exact spelling depends on the tool and its version.
- Some pipelines put everything in a single `string` attribute or a `stringvector`.
- `timeCode` and `keyCode` are standard typed attributes; useful to confirm a match,
  not to make it.

Always inspect real frames from the actual delivery and pick the key with the user.
Command-line alternatives for checking: `exrheader frame.exr` (OpenEXR tools) or
`oiiotool --info -v frame.exr` (OpenImageIO).

## Sequences

- The "first frame" is the lowest frame number in the folder, not the first file the OS
  lists. Sort numerically on the frame number.
- Folders can contain several sequences (main plate plus elements). Group files by the
  name with the frame number removed (`name.####.exr`, `name_####.exr`).
- Skip hidden and partial files (`._name.exr` from macOS, `.tmp`, zero-byte files).
