"""Re-draw the aerodynamic figures with a clean layout."""
import numpy as np, os, csv
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
FONT = r"C:\Windows\Fonts\msyh.ttc"

def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()

def axes(d, box, xr, yr, xlab, ylab, f2, xticks=None, yticks=None):
    x0, y0, x1, y1 = box
    d.line([(x0, y0), (x1, y0)], fill="black", width=2)
    d.line([(x0, y0), (x0, y1)], fill="black", width=2)
    for v in (xticks if xticks is not None else np.linspace(xr[0], xr[1], 6)):
        x = x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0)
        d.line([(x, y0), (x, y0 + 6)], fill="black")
        d.text((x - 10, y0 + 9), f"{v:g}", fill="black", font=f2)
    for v in (yticks if yticks is not None else np.linspace(yr[0], yr[1], 6)):
        y = y0 - (v - yr[0]) / (yr[1] - yr[0]) * (y0 - y1)
        d.line([(x0 - 6, y), (x0, y)], fill="black")
        d.text((x0 - 46, y - 9), f"{v:g}", fill="black", font=f2)
    d.text(((x0 + x1) / 2 - 30, y0 + 32), xlab, fill="black", font=f2)
    d.text((x0 + 6, y1 - 22), ylab, fill="black", font=f2)

def curve(d, box, xr, yr, x, y, color, width=3):
    x0, y0, x1, y1 = box
    pts = [(x0 + (a - xr[0]) / (xr[1] - xr[0]) * (x1 - x0),
            y0 - (b - yr[0]) / (yr[1] - yr[0]) * (y0 - y1)) for a, b in zip(x, y)]
    d.line(pts, fill=color, width=width)

rows = list(csv.DictReader(open(os.path.join(RES, "ll_polar.csv"))))
al = np.array([float(r["alpha"]) for r in rows])
cl = np.array([float(r["CL"]) for r in rows])
cd = np.array([float(r["CD"]) for r in rows])
ld = np.array([float(r["LD"]) for r in rows])

# ---------- figure 1: CL(alpha) + L/D(alpha)
W, H = 1000, 430
img = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(img)
f1, f2 = font(19), font(14)
axes(dr, (80, 350, 470, 90), (-6, 12), (0, 1.3), "α (°)", "CL", f2, np.arange(-6, 13, 3), np.arange(0, 1.31, 0.2))
curve(dr, (80, 350, 470, 90), (-6, 12), (0, 1.3), al, cl, (200, 30, 30))
axes(dr, (580, 350, 960, 90), (-6, 12), (0, 25), "α (°)", "L/D", f2, np.arange(-6, 13, 3), np.arange(0, 26, 5))
curve(dr, (580, 350, 960, 90), (-6, 12), (0, 25), al, ld, (30, 90, 200))
dr.text((330, 12), "CL(α)  与  L/D(α)      V = 15 m/s, 135 kg", fill="black", font=f1)
img.save(os.path.join(FIG, "fig_polar.png"))

# ---------- figure 2: drag polar
W, H = 640, 500
img = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(img)
axes(dr, (90, 420, 590, 70), (0.010, 0.070), (0, 1.1), "CD", "CL", f2, np.arange(0.01, 0.071, 0.01), np.arange(0, 1.21, 0.2))
curve(dr, (90, 420, 590, 70), (0.010, 0.070), (0, 1.1), cd, cl, (20, 140, 90))
img.save(os.path.join(FIG, "fig_drag.png"))

# ---------- figure 3: span load at 4 g limit (design comparison)
sl = list(csv.DictReader(open(os.path.join(RES, "spanload_ll.csv"))))
y = np.array([float(r["y_m"]) for r in sl])
q1 = np.array([float(r["lift_per_span_N_m"]) for r in sl])
sch = np.array([float(r["schrenk_N_m"]) for r in sl])
fac = 4 * 135 * 9.81 / (q1.sum() * (y[1] - y[0]) * 0.5 if False else 1.0)
# normalise both to the same total lift (4 g, 135 kg)
target = 4 * 135 * 9.81
q1 = q1 * target / np.trapezoid(q1, y)
sch = sch * target / np.trapezoid(sch, y)
W, H = 900, 520
img = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(img)
axes(dr, (100, 440, 860, 80), (0, 6.5), (0, 2600), "y (m)", "q (N/m)", f2,
     np.arange(0, 6.6, 1), np.arange(0, 2601, 500))
curve(dr, (100, 440, 860, 80), (0, 6.5), (0, 2600), y, q1, (200, 30, 30))
curve(dr, (100, 440, 860, 80), (0, 6.5), (0, 2600), y, sch, (30, 90, 200), 2)
dr.line([(620, 120), (660, 120)], fill=(200, 30, 30), width=4)
dr.text((670, 111), "升力线 (本文)", fill="black", font=f2)
dr.line([(620, 150), (660, 150)], fill=(30, 90, 200), width=2)
dr.text((670, 141), "Schrenk (设计文档)", fill="black", font=f2)
dr.text((100, 34), "展向升力分布 — 4g 限制载荷, 135 kg", fill="black", font=f1)
img.save(os.path.join(FIG, "fig_spanload.png"))
print("ok")

