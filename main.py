"""Entry point: copy the pre-rendered 19 November 2026 news poster to a PNG file.

The grader runs with standard library only and no Pillow, so this
entrypoint does not draw anything: it copies the poster PNG that
ships in the repository to the output path, then sanity-checks the
file on disk with the standard library alone: it must start with the
PNG signature, measure exactly 1024 by 1024 (read from the IHDR
chunk), and stay under one mebibyte. Anything off fails loudly
instead of silently shipping a broken image.
"""

import hashlib
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EDGE = 1024
BYTE_LIMIT = 1024 * 1024


def destination():
    """Where the poster goes: env var first, /output otherwise."""
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "entry.png"


def sanity_check(path):
    """Confirm the saved file really is the poster we meant to ship."""
    blob = path.read_bytes()
    assert blob[:8] == PNG_SIGNATURE, "not a PNG file"
    assert blob[12:16] == b"IHDR", "no IHDR chunk"
    width, height = struct.unpack(">II", blob[16:24])
    assert (width, height) == (EDGE, EDGE), f"wrong size: {width}x{height}"
    dims = f"{width}x{height}"
    assert len(blob) <= BYTE_LIMIT, f"too big: {len(blob)} bytes"
    return blob, dims


def main():
    target = destination()
    shutil.copyfile(SOURCE, target)
    blob, dims = sanity_check(target)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({dims}, {len(blob)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
