"""Coloured Cp contour images for the RevP wing.

Cp model: lifting line (spanwise) + thin-airfoil chordwise loading, applied to
the reconstructed OML surface.  Fast potential-flow estimate, not RANS.
"""
import numpy as np, os, struct, csv
from PIL import Image, ImageDraw, ImageFont
import importlib.util

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIG = os.path.join(ROOT, "figures")
MESH = os.path.join(ROOT, "mesh", "wing_oml.stl")
CSV_IN = (r"C:\Users\张文博\Downloads\Aircraft_Structure_design-main"
          r"\Aircraft_Structure_design-main\02_CATIA\_wing_skin_sections.csv")
FONT = r"C:\Windows\Fonts\msyh.ttc"

spec = importlib.util.spec_from_file_location("ll", os.path.join(ROOT, "scripts", "04_lifting_line.py"))
ll = importlib.util.module_from_spec(spec); spec.loader.exec_module(ll)

def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()

# ---------------------------------------------------------- section x_le
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

stn = []
for k, pts in secs.items():
    _, side, idx, y, _, _ = k.split("|")
    if side == "R":
        stn.append((float(y) / 1000.0, pts[:, 0].min() / 1000.0,
                    (pts[:, 0].max() - pts[:, 0].min()) / 1000.0,
                    pts[:, 1][np.argmin(pts[:, 0])] / 1000.0,
                    pts[:, 1][np.argmax(pts[:, 0])] / 1000.0))
stn.sort()
YS = np.array([s[0] for s in stn])
XLE = np.array([s[1] for s in stn])
CH = np.array([s[2] for s in stn])
ZLE = np.array([s[3] for s in stn])
ZTE = np.array([s[4] for s in stn])
AL0 = np.radians(np.where(YS <= 4.5, -6.0, np.where(YS >= 6.5, -2.5, -6.0 + 3.5 * (YS - 4.5) / 2.0)))

ALPHA = float(os.environ.get("CP_ALPHA", "4.0"))
rc = ll.solve(ALPHA)
_m = rc["y"] >= 0
Yll = rc["y"][_m]
CLv = rc["cl"][_m]
AIv = rc["ai"][_m]

def camber_z(y, s):
    return 1000 * ((1 - 0) * (np.interp(y, YS, ZLE) + s * (np.interp(y, YS, ZTE) - np.interp(y, YS, ZLE))))

def cp_at(y, s, upper):
    y = abs(y)
    cl = float(np.interp(y, Yll, CLv))
    ai = float(np.interp(y, Yll, AIv)) * np.pi / 180
    tw = -np.arctan2(float(np.interp(y, YS, ZTE) - np.interp(y, YS, ZLE)), float(np.interp(y, YS, CH)))
    al0 = float(np.interp(y, YS, AL0))
    a0 = np.radians(ALPHA) + tw - al0 - ai
    s = np.clip(s, 0.004, 0.996)
    th = np.arccos(1 - 2 * s)
    a1 = cl / np.pi - 2 * a0
    g = 2 * (a0 * (1 + np.cos(th)) / np.sin(th) + a1 * np.sin(th))
    cp = 1 - (1 + (g / 2 if upper else -g / 2)) ** 2
    return float(np.clip(cp, -3.0, 1.0))

def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        d = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return d[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)

def jet(t):
    t = np.clip(t, 0, 1)
    r = np.clip(1.5 - abs(4 * t - 3), 0, 1)
    g = np.clip(1.5 - abs(4 * t - 2), 0, 1)
    b = np.clip(1.5 - abs(4 * t - 1), 0, 1)
    return np.stack([r, g, b], axis=-1)

def render_cp(tri, yaw, pitch, W, H, fname, title, cmin=-3.0, cmax=1.0, reverse=False):
    cen = tri.mean(axis=1)
    y = np.abs(cen[:, 1]) / 1000.0
    c = np.interp(y, YS, CH)
    s = np.clip((cen[:, 0] / 1000.0 - np.interp(y, YS, XLE)) / c, 0, 1)
    nrm0 = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    up = nrm0[:, 2] > 0
    cp = np.array([cp_at(yy, ss, u) for yy, ss, u in zip(y, s, up)])
    col = (jet((cp - cmin) / (cmax - cmin)) * 255).astype(np.uint8)

    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    p = (tri.reshape(-1, 3) @ Rz.T @ Rx.T).reshape(-1, 3, 3)
    dep = p[:, :, 1].mean(axis=1)
    order = np.argsort(dep if reverse else -dep)
    p, col, cp = p[order], col[order], cp[order]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    nn = np.linalg.norm(n, axis=1); nn[nn == 0] = 1
    n = (n.T / nn).T
    light = np.array([0.35, -0.75, 0.55]); light /= np.linalg.norm(light)
    lam = 0.60 + 0.40 * np.clip(np.abs(n @ light), 0, 1)
    shade = np.clip(col * lam[:, None], 0, 255).astype(np.uint8)

    xs, zs = p[:, :, 0], p[:, :, 2]
    x0, x1, z0, z1 = xs.min(), xs.max(), zs.min(), zs.max()
    sc = min((W - 220) / (x1 - x0), (H - 150) / (z1 - z0))
    px = (xs - (x0 + x1) / 2) * sc + (W - 160) / 2
    py = -(zs - (z0 + z1) / 2) * sc + H / 2 + 20
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for k in range(len(p)):
        cc = tuple(int(v) for v in shade[k])
        d.polygon([(px[k, 0], py[k, 0]), (px[k, 1], py[k, 1]), (px[k, 2], py[k, 2])],
                  fill=cc, outline=cc)
    d.text((24, 14), title, fill=(20, 20, 20), font=font(21))
    cbx, cby, cbh, cbw = W - 120, 130, 320, 26
    for i in range(cbh):
        cc = (jet(np.array([1 - i / cbh]))[0] * 255).astype(int)
        d.line([(cbx, cby + i), (cbx + cbw, cby + i)], fill=tuple(cc))
    d.rectangle([cbx, cby, cbx + cbw, cby + cbh], outline=(0, 0, 0))
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        v = cmax - frac * (cmax - cmin)
        yy = cby + frac * cbh
        d.line([(cbx + cbw, yy), (cbx + cbw + 6, yy)], fill=(0, 0, 0))
        d.text((cbx + cbw + 10, yy - 8), f"{v:.1f}", fill=(0, 0, 0), font=font(13))
    d.text((cbx - 10, cby - 32), "Cp", fill=(0, 0, 0), font=font(17))
    img.save(os.path.join(FIG, fname))
    print("saved", fname, "Cp", round(float(cp.min()), 2), round(float(cp.max()), 2))

if __name__ == "__main__":
    tri = load_stl(MESH)
    print("triangles", len(tri))
    render_cp(tri, 90, -90, 1300, 760, "cp_top.png",
              f"RevP 机翼上表面 Cp 云图   α={ALPHA:.1f}°, CL={rc['CL']:.2f}", reverse=True)
    render_cp(tri, 90, 90, 1300, 760, "cp_bottom.png",
              f"RevP 机翼下表面 Cp 云图   α={ALPHA:.1f}°", reverse=False)
    render_cp(tri, -20, 35, 1300, 780, "cp_iso.png",
              f"RevP 机翼 Cp 云图（等轴测）   α={ALPHA:.1f}°, V=15 m/s")





