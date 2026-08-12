"""Verify a qrencode-produced QR SVG encodes the expected string.

No decoder: re-encode with the same tool and compare module matrices. The
comparison is normalised so a different quiet-zone margin cannot cause a false
mismatch — the published files use margin 3, qrencode defaults to 4.
"""
import re, subprocess, sys, pathlib

def modules(svg: str):
    box = int(re.search(r'viewBox="0 0 (\d+) ', svg).group(1))
    off = re.search(r'translate\((\d+),(\d+)\)', svg)
    ox, oy = (int(off.group(1)), int(off.group(2))) if off else (0, 0)
    n = box - 2 * ox                       # QR side in modules
    cells = set()
    for r in re.finditer(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"([^>]*)>', svg):
        x, y, w, h, rest = int(r.group(1)), int(r.group(2)), int(r.group(3)), int(r.group(4)), r.group(5)
        if "#ffffff" in rest or (w >= box and h >= box):
            continue
        for dx in range(w):
            for dy in range(h):
                cells.add((x + dx, y + dy))   # already QR-relative inside the <g>
    return n, frozenset(cells)

def check(path, data):
    want_n, want = modules(pathlib.Path(path).read_text())
    for level in ("L", "M", "Q", "H"):
        out = subprocess.run(["qrencode", "-t", "SVG", "-l", level, "-m", "3", "-o", "-", data],
                             capture_output=True, text=True)
        if out.returncode:
            continue
        got_n, got = modules(out.stdout)
        if (got_n, got) == (want_n, want):
            return f"MATCH (ecc={level}, {want_n}x{want_n})"
    return f"NO MATCH ({want_n}x{want_n} modules, {len(want)} dark)"

if __name__ == "__main__":
    print(check(sys.argv[1], sys.argv[2]))
