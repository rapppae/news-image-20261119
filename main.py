"""Entry point: render the 19 November 2026 news poster to a PNG file.

Reads MAKEFUN_OUTPUT_DIR (falls back to /output), asks draw.compose()
for the finished sheet, saves it, then sanity-checks the file on disk:
it must start with the PNG signature, measure exactly 1024 by 1024,
and stay under one mebibyte. Anything off fails loudly instead of
silently shipping a broken image.
"""

import hashlib
import os
from pathlib import Path

from PIL import Image

import draw

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
    with Image.open(path) as shot:
        assert shot.size == (EDGE, EDGE), f"wrong size: {shot.size}"
        dims = f"{shot.size[0]}x{shot.size[1]}"
    assert len(blob) <= BYTE_LIMIT, f"too big: {len(blob)} bytes"
    return blob, dims


def main():
    here = Path(__file__).resolve().parent
    sheet = draw.compose(str(here / "assets"))
    target = destination()
    sheet.save(target, format="PNG", optimize=True)
    blob, dims = sanity_check(target)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({dims}, {len(blob)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
