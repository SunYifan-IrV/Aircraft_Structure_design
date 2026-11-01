"""Build a watertight wing OML (outer mould line) STL from the CATIA sections.

The RevN STEP only contains the wing box (main spar .. rear spar); the leading
edge D-box skin and the trailing edge skin are missing, so the aerodynamic
surface is reconstructed from the section coordinate table instead.

Output: mesh/wing_oml.stl  (mm, binary), mirrored full span.
"""
import numpy as np, struct, os, csv

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
CSV_IN = (r"C:\Users\张文博\Downloads\Aircraft_Structure_design-main"
          r"\Aircraft_Structure_design-main\02_CATIA\_wing_skin_sections.csv")
OUT = os.path.join(ROOT, "mesh", "wing_oml.stl")

secs, cur, buf = {}, None, []
for ln in open(CSV_IN, encoding="utf-8"):
    ln = ln.strip()
    if not ln:
        continue
    if ln.startswith("SECTION"):
        if cur:
            secs[cur] = np.array(buf)
        cur, buf = ln, []
    elif ln == "END":
        continue
    else:
        a, b = ln.split(",")
        buf.append((float(a), float(b)))
if cur:
    secs[cur] = np.array(buf)

sta = []
for k, pts in secs.items():
    _, side, idx, y, _, _ = k.split("|")
    if side != "R":
        continue
    sta.append((float(y), pts))
sta.sort()

loops = [p for _, p in sta]          # (96,2) closed-ish loops, LE -> TE -> LE
N = loops[0].shape[0]
assert all(l.shape[0] == N for l in loops)

def tri_strip(a, b, flip=False):
    """triangulate quad strip between two equal-length loops"""
    t = []
    for i in range(N - 1):
        p0, p1 = a[i], a[i + 1]
        q0, q1 = b[i], b[i + 1]
        if flip:
            t.append((p0, q0, q1)); t.append((p0, q1, p1))
        else:
            t.append((p0, q1, q0)); t.append((p0, p1, q1))
    # close the loop
    p0, p1 = a[-1], a[0]
    q0, q1 = b[-1], b[0]
    if flip:
        t.append((p0, q0, q1)); t.append((p0, q1, p1))
    else:
        t.append((p0, q1, q0)); t.append((p0, p1, q1))
    return t

tris = []
for s in range(len(sta) - 1):
    y0, l0 = sta[s]
    y1, l1 = sta[s + 1]
    A = np.column_stack([l0[:, 0], np.full(N, y0), l0[:, 1]])
    B = np.column_stack([l1[:, 0], np.full(N, y1), l1[:, 1]])
    tris += tri_strip(A, B)

# root and tip caps (fan)
for yy, lp, flip in ((sta[0][0], sta[0][1], True), (sta[-1][0], sta[-1][1], False)):
    P = np.column_stack([lp[:, 0], np.full(N, yy), lp[:, 1]])
    c = P.mean(axis=0)
    for i in range(N):
        tris.append((c, P[i], P[(i + 1) % N]))

def write_stl(path, tris):
    with open(path, "wb") as f:
        f.write(b"wing OML from CATIA sections".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            n = n / ln if ln > 0 else np.zeros(3)
            f.write(struct.pack("<3f", *n))
            for p in (a, b, c):
                f.write(struct.pack("<3f", *p))
            f.write(b"\x00\x00")

# mirror to the left wing (y < 0)
mirror = [tuple(np.array([p[0], -p[1], p[2]]) for p in (c, b, a)) for a, b, c in tris]
allt = tris + mirror
write_stl(OUT, allt)
print("triangles", len(allt), "->", OUT)

# quick quality check: signed volume
vol = 0.0
for a, b, c in tris:
    vol += np.dot(a, np.cross(b, c)) / 6.0
print("half-wing volume (m^3):", abs(vol) / 1e9)
