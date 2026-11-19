"""Write the 19 November 2026 world-news poster to /output/entry.png.

Stdlib plus the bundled draw.py, deterministic, no network. The poster
is rendered by draw.py from the day's verified stories; this program
just places it where the judge expects it and checks it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import draw

OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = draw.render()
    img.save(DST, "PNG")
    with open(DST, "rb") as f:
        magic = f.read(8)
    assert magic == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
    assert img.size == (1024, 1024), f"unexpected size {img.size}"
    size = os.path.getsize(DST)
    assert size <= 1048576, f"entry.png is {size} bytes, over 1 MiB"
    print("wrote", DST, size, "bytes")


if __name__ == "__main__":
    main()
