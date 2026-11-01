"""Render the STL and draw the aerodynamic result figures (PIL only)."""
import numpy as np, os, struct, csv
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
MESH = os.path.join(ROOT, "mesh", "aircraft_surface_bin.stl")
FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
os.makedirs(FIG, exist_ok=True)

FONT = r"C:\Windows\Fonts\msyh.ttc"
def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()

def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    tri = data[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)
    return tri

def render(tri, yaw, pitch, W=1100, H=620, sub=1, fname="view.png", title=""):
    v = tri[::sub]
    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    p = v.reshape(-1, 3) @ Rz.T @ Rx.T
    p = p.reshape(-1, 3, 3)
    # camera looks along +y after rotation; depth = y
    dep = p[:, :, 1].mean(axis=1)
    order = np.argsort(-dep)
    p = p[order]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    nn = np.linalg.norm(n, axis=1); nn[nn == 0] = 1
    n = (n.T / nn).T
    light = np.array([0.4, -0.7, 0.6]); light /= np.linalg.norm(light)
    lam = np.clip(np.abs(n @ light), 0, 1)
    xs, ys = p[:, :, 0], p[:, :, 2]
    x0, x1 = xs.min(), xs.max(); z0, z1 = ys.min(), ys.max()
    sc = min((W - 60) / (x1 - x0), (H - 80) / (z1 - z0))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    px = (xs - cx) * sc + W / 2
    py = -(ys - cz) * sc + H / 2 + 10
    img = Image.new("RGB", (W, H), (250, 250, 252))
    d = ImageDraw.Draw(img)
    cols = [(40 + int(200 * l), 55 + int(195 * l), 75 + int(175 * l)) for l in lam]
    for k in range(len(p)):
        d.polygon([(px[k, 0], py[k, 0]), (px[k, 1], py[k, 1]), (px[k, 2], py[k, 2])], fill=cols[k])
    d.text((20, 14), title, fill=(20, 20, 20), font=font(22))
    img.save(os.path.join(FIG, fname))
    print("saved", fname)

def plot_polar():
    rows = list(csv.DictReader(open(os.path.join(RES, "ll_polar.csv"))))
    al = np.array([float(r["alpha"]) for r in rows])
    cl = np.array([float(r["CL"]) for r in rows])
    cd = np.array([float(r["CD"]) for r in rows])
    ld = np.array([float(r["LD"]) for r in rows])
    W, H = 1000, 720
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    f1, f2 = font(20), font(16)
    # --- CL-alpha
    ox, oy, sx, sy = 90, 340, 380, 260
    d.line([(ox, oy), (ox + sx, oy)], fill="black", width=2)
    d.line([(ox, oy), (ox, oy - sy)], fill="black", width=2)
    for a in range(-6, 13, 3):
        x = ox + (a + 6) / 18 * sx
        d.line([(x, oy), (x, oy + 6)], fill="black")
        d.text((x - 10, oy + 10), str(a), fill="black", font=f2)
    for c in np.arange(0, 1.21, 0.3):
        y = oy - c / 1.2 * sy
        d.line([(ox - 6, y), (ox, y)], fill="black")
        d.text((ox - 45, y - 10), f"{c:.1f}", fill="black", font=f2)
    pts = [(ox + (a + 6) / 18 * sx, oy - c / 1.2 * sy) for a, c in zip(al, cl)]
    d.line(pts, fill=(200, 30, 30), width=3)
    d.text((ox + 110, oy - sy - 30), "CL – α", fill=(200, 30, 30), font=f2)
    d.text((ox + sx / 2 - 20, oy + 40), "α (deg)", fill="black", font=f2)
    # --- L/D
    ox2 = 590
    d.line([(ox2, oy), (ox2 + sx, oy)], fill="black", width=2)
    d.line([(ox2, oy), (ox2, oy - sy)], fill="black", width=2)
    for a in range(-6, 13, 3):
        x = ox2 + (a + 6) / 18 * sx
        d.line([(x, oy), (x, oy + 6)], fill="black")
        d.text((x - 10, oy + 10), str(a), fill="black", font=f2)
    for v in np.arange(0, 25, 5):
        y = oy - v / 25 * sy
        d.line([(ox2 - 6, y), (ox2, y)], fill="black")
        d.text((ox2 - 40, y - 10), str(int(v)), fill="black", font=f2)
    pts = [(ox2 + (a + 6) / 18 * sx, oy - l / 25 * sy) for a, l in zip(al, ld)]
    d.line(pts, fill=(30, 90, 200), width=3)
    d.text((ox2 + 120, oy - sy - 30), "L/D – α", fill=(30, 90, 200), font=f2)
    # --- drag polar
    ox3, oy3, sx3, sy3 = 90, 690, 380, 260
    d.line([(ox3, oy3), (ox3 + sx3, oy3)], fill="black", width=2)
    d.line([(ox3, oy3), (ox3, oy3 - sy3)], fill="black", width=2)
    for cdv in np.arange(0, 0.081, 0.02):
        x = ox3 + cdv / 0.08 * sx3
        d.line([(x, oy3), (x, oy3 + 6)], fill="black")
        d.text((x - 14, oy3 + 10), f"{cdv:.2f}", fill="black", font=f2)
    for c in np.arange(0, 1.21, 0.3):
        y = oy3 - c / 1.2 * sy3
        d.line([(ox3 - 6, y), (ox3, y)], fill="black")
        d.text((ox3 - 45, y - 10), f"{c:.1f}", fill="black", font=f2)
    pts = [(ox3 + c / 0.08 * sx3, oy3 - clv / 1.2 * sy3) for c, clv in zip(cd, cl)]
    d.line(pts, fill=(20, 140, 90), width=3)
    d.text((ox3 + 60, oy3 - sy3 - 35), "CL – CD (polar)", fill=(20, 140, 90), font=f2)
    d.text((ox3 + sx3 / 2 - 30, oy3 + 40), "CD", fill="black", font=f2)
    d.text((ox + 120, 20), "RevN wing — lifting-line results (V=15 m/s, ρ=1.225)", fill="black", font=f1)
    img.save(os.path.join(FIG, "aero_polar.png"))
    print("saved aero_polar.png")

def plot_span():
    rows = list(csv.DictReader(open(os.path.join(RES, "spanload_ll.csv"))))
    y = np.array([float(r["y_m"]) for r in rows])
    q = np.array([float(r["lift_per_span_N_m"]) for r in rows])
    s = np.array([float(r["schrenk_N_m"]) for r in rows])
    Wd, H = 1000, 640
    img = Image.new("RGB", (Wd, H), "white"); d = ImageDraw.Draw(img)
    f1, f2 = font(20), font(16)
    ox, oy, sx, sy = 100, 520, 820, 380
    d.line([(ox, oy), (ox + sx, oy)], fill="black", width=2)
    d.line([(ox, oy), (ox, oy - sy)], fill="black", width=2)
    for yy in range(0, 7):
        x = ox + yy / 6.5 * sx
        d.line([(x, oy), (x, oy + 6)], fill="black")
        d.text((x - 8, oy + 10), str(yy), fill="black", font=f2)
    for v in range(0, 601, 100):
        yv = oy - v / 600 * sy
        d.line([(ox - 6, yv), (ox, yv)], fill="black")
        d.text((ox - 45, yv - 10), str(v), fill="black", font=f2)
    p1 = [(ox + yy / 6.5 * sx, oy - qq / 600 * sy) for yy, qq in zip(y, q)]
    p2 = [(ox + yy / 6.5 * sx, oy - ss / 600 * sy) for yy, ss in zip(y, s)]
    d.line(p1, fill=(200, 30, 30), width=3)
    d.line(p2, fill=(30, 90, 200), width=3)
    d.text((ox + 380, oy - sy - 40), "lift per unit span  q(y)", fill="black", font=f1)
    d.text((ox + 600, oy - sy - 5), "lifting line", fill=(200, 30, 30), font=f2)
    d.text((ox + 600, oy - sy + 20), "Schrenk (design doc)", fill=(30, 90, 200), font=f2)
    d.text((ox + sx / 2 - 30, oy + 44), "y (m)", fill="black", font=f2)
    d.text((15, oy - sy / 2), "N/m", fill="black", font=f2)
    img.save(os.path.join(FIG, "spanload.png"))
    print("saved spanload.png")

if __name__ == "__main__":
    tri = load_stl(MESH)
    print("triangles", len(tri))
    render(tri, -35, 18, sub=1, fname="view_iso.png", title="RevN — 整机外模线网格 (STL, 364k 三角面)")
    render(tri, 90, 0, sub=1, fname="view_top.png", title="RevN — 俯视")
    render(tri, 0, 0, sub=1, fname="view_front.png", title="RevN — 前视")
    plot_polar()
    plot_span()

