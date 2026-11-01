"""Spar stress contour for the RevN structure (6 g load case).

Beam model of the box spar (cap area / depth from the design table), stress
field evaluated on the actual spar geometry extracted from the STEP mesh.
"""
import numpy as np, os, struct, csv
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIG = os.path.join(ROOT, "figures")
MESH = os.path.join(ROOT, "mesh", "aircraft_surface_bin.stl")
CSV_IN = (r"C:\Users\张文博\Downloads\Aircraft_Structure_design-main"
          r"\Aircraft_Structure_design-main\02_CATIA\_wing_skin_sections.csv")
FONT = r"C:\Windows\Fonts\msyh.ttc"

def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()

# ---------------- sections (planform) ----------------
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
                    pts[:, 1][np.argmin(pts[:, 0])] / 1000.0))
stn.sort()
YS = np.array([s[0] for s in stn]); XLE = np.array([s[1] for s in stn])
CH = np.array([s[2] for s in stn]); ZLE = np.array([s[3] for s in stn])

# ---------------- beam model ----------------
yd = np.array([0.0, 0.65, 1.63, 3.25, 4.88, 6.5])
dd = np.array([0.200, 0.190, 0.175, 0.150, 0.125, 0.090])
td = np.array([0.0080, 0.0067, 0.0048, 0.0022, 0.0006, 0.0006])
W_CAP, T_WEB = 0.020, 0.0035

def spar_props(y):
    d = np.interp(y, yd, dd); t = np.interp(y, yd, td)
    A = W_CAP * t
    I = 2 * A * (d / 2) ** 2
    return d, A, I

# load distribution: 6 g at 155 kg, from the lifting-line results
strength = {r["y_m"]: r for r in csv.DictReader(open(os.path.join(ROOT, "results", "strength.csv")))}
ys = np.array(sorted(float(k) for k in strength))
M = np.array([float(strength[f"{y:.3f}"]["M_Nm"]) if f"{y:.3f}" in strength else 0.0 for y in ys])
V = np.array([abs(float(strength[f"{y:.3f}"]["shear_N"])) if f"{y:.3f}" in strength else 0.0 for y in ys])

def M_of(y):
    return np.interp(y, ys, M, left=M[0], right=0.0)

def V_of(y):
    return np.interp(y, ys, V, left=V[0], right=0.0)

def sigma_vm(y, z_m):
    """z_m: height (m) above the wing reference plane at that station"""
    d, A, I = spar_props(y)
    z_le = float(np.interp(y, YS, ZLE))
    z_na = z_le + d / 2
    lever = np.clip(z_m - z_na, -d / 2, d / 2)      # keep within the design box depth
    sig = M_of(y) * lever / I
    tau = V_of(y) / (2 * d * T_WEB)
    return float(np.sqrt(sig ** 2 + 3 * tau ** 2) / 1e6)

# ---------------- mesh ----------------
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

tri = load_stl(MESH)
cen = tri.mean(axis=1)
y = np.abs(cen[:, 1]) / 1000.0
c = np.interp(y, YS, CH)
xle = np.interp(y, YS, XLE)
s = (cen[:, 0] / 1000.0 - xle) / c
zle = np.interp(y, YS, ZLE)
z = cen[:, 2] / 1000.0

mask = (y > 0.45) & (y < 6.55) & (s > 0.265) & (s < 0.335) & (z > zle - 0.03) & (z < zle + 0.33)
sel = tri[mask]
print("spar triangles:", len(sel), "of", len(tri))
cen = sel.mean(axis=1)
y = np.abs(cen[:, 1]) / 1000.0
z = cen[:, 2] / 1000.0
sv = np.array([sigma_vm(yy, zz) for yy, zz in zip(y, z)])
print("stress range MPa", round(sv.min(), 1), round(sv.max(), 1))

cmin, cmax = 0.0, 380.0
col = (jet((sv - cmin) / (cmax - cmin)) * 255).astype(np.uint8)

def render(tri, col, yaw, pitch, W, H, fname, title, cmin=0, cmax=380):
    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    p = (tri.reshape(-1, 3) @ Rz.T @ Rx.T).reshape(-1, 3, 3)
    dep = p[:, :, 1].mean(axis=1)
    order = np.argsort(-dep)
    p, col2 = p[order], col[order]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    nn = np.linalg.norm(n, axis=1); nn[nn == 0] = 1
    n = (n.T / nn).T
    light = np.array([0.35, -0.75, 0.55]); light /= np.linalg.norm(light)
    lam = 0.62 + 0.38 * np.clip(np.abs(n @ light), 0, 1)
    shade = np.clip(col2 * lam[:, None], 0, 255).astype(np.uint8)
    xs, zs = p[:, :, 0], p[:, :, 2]
    x0, x1, z0, z1 = xs.min(), xs.max(), zs.min(), zs.max()
    sc = min((W - 240) / (x1 - x0), (H - 150) / (z1 - z0))
    px = (xs - (x0 + x1) / 2) * sc + (W - 170) / 2
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
        d.text((cbx + cbw + 10, yy - 8), f"{v:.0f}", fill=(0, 0, 0), font=font(13))
    d.text((cbx - 30, cby - 32), "von Mises (MPa)", fill=(0, 0, 0), font=font(15))
    img.save(os.path.join(FIG, fname))
    print("saved", fname)

render(sel, col, -28, 12, 1300, 720, "spar_stress_iso.png",
       "RevN 主梁应力云图（6g, 155 kg）— von Mises")
render(sel, col, 0, 0, 1300, 720, "spar_stress_side.png",
       "RevN 主梁应力云图（侧视，沿展向）")
