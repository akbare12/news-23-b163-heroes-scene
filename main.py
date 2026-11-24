#!/usr/bin/env python3
"""NEWS-23 B163 heroes-scene entry runner (stdlib only, no PIL).

Reads the bundled entry.png next to this file, validates its PNG structure
manually (struct + zlib CRCs), and writes a byte-identical copy to
$MAKEFUN_OUTPUT_DIR/entry.png. Never writes next to this file.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "48770e39f7326cccbbc873da73a5abfcbbab4aca5512176f5267674415c3a07b"
EXPECTED_SIZE = 146387
MIN_SIZE = 10000
MAX_SIZE = 1024 * 1024


def fail(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(repo_dir, "entry.png")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not out_dir:
        fail("MAKEFUN_OUTPUT_DIR is empty")
    out_dir_abs = os.path.abspath(out_dir)
    if os.path.exists(out_dir_abs) and not os.path.isdir(out_dir_abs):
        fail("MAKEFUN_OUTPUT_DIR is a file, not a directory: " + out_dir_abs)
    # refuse to write inside the repo (grader runs with a read-only /bot)
    if os.path.commonpath([out_dir_abs, repo_dir]) == repo_dir:
        fail("MAKEFUN_OUTPUT_DIR must not be inside the repo: " + out_dir_abs)
    out_path = os.path.join(out_dir_abs, "entry.png")
    if os.path.abspath(out_path) == os.path.abspath(src):
        fail("output would overwrite the source image")

    try:
        with open(src, "rb") as f:
            data = f.read()
    except OSError as e:
        fail("cannot read source entry.png: " + str(e))

    if len(data) < MIN_SIZE:
        fail("entry.png too small: %d bytes" % len(data))
    if len(data) > MAX_SIZE:
        fail("entry.png too large: %d bytes" % len(data))
    if len(data) != EXPECTED_SIZE:
        fail("entry.png size mismatch: got %d, expected %d"
             % (len(data), EXPECTED_SIZE))

    # PNG signature
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("bad PNG signature")

    # Walk chunks: first must be a 13-byte IHDR for 1024x1024, 8-bit, type 2/6.
    pos = 8
    first = True
    idat_total = 0
    seen_iend = False
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if pos + 12 + length > len(data):
            fail("truncated chunk %r" % ctype)
        chunk_data = data[pos + 8:pos + 8 + length]
        (crc_stored,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        crc_calc = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if crc_calc != crc_stored:
            fail("CRC mismatch in chunk %r" % ctype)
        if first:
            if ctype != b"IHDR":
                fail("first chunk is not IHDR")
            if length != 13:
                fail("IHDR length is not 13")
            w, h, depth, ctype_b, comp, filt, inter = struct.unpack(
                ">IIBBBBB", chunk_data)
            if (w, h) != (1024, 1024):
                fail("IHDR dimensions are %dx%d, expected 1024x1024" % (w, h))
            if depth != 8:
                fail("bit depth is %d, expected 8" % depth)
            if ctype_b not in (2, 6):
                fail("colour type is %d, expected 2 or 6" % ctype_b)
            if comp != 0 or filt != 0 or inter != 0:
                fail("compression/filter/interlace must all be 0")
        # CRC covers chunk type + chunk data (not the length field) — this is
        # what the chunk-walk above verifies for every chunk, IHDR included.
            first = False
        if ctype == b"IDAT":
            if length == 0:
                fail("empty IDAT chunk")
            idat_total += length
        if ctype == b"IEND":
            if length != 0:
                fail("IEND must be 0 bytes")
            if pos + 12 + length != len(data):
                fail("trailing data after IEND")
            seen_iend = True
            break
        pos += 12 + length
    if first:
        fail("no IHDR found")
    if not seen_iend:
        fail("no IEND chunk found")
    if idat_total < 1000:
        fail("IDAT payload too small: %d bytes" % idat_total)

    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA256:
        fail("sha256 mismatch: got %s" % sha)

    try:
        os.makedirs(out_dir_abs, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
    except OSError as e:
        fail("cannot write output: " + str(e))

    # Re-read output and confirm byte-identical.
    with open(out_path, "rb") as f:
        out_data = f.read()
    if out_data != data:
        fail("output is not byte-identical to source")
    print("wrote %s (%d bytes)" % (out_path, len(out_data)))
    print("sha256 %s" % hashlib.sha256(out_data).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
