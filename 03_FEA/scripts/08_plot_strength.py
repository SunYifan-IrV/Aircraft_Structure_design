"""Plot spar stress and deflection along the span (6 g case)."""
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

rows = list(csv.DictReader(open(os.path.join(RES, "strength.csv"))))
y = np.array([float(r["y_m"]) for r in rows])
s = np.array([float(r["cap_stress_MPa"]) for r in rows])
d = np.array([abs(float(r["deflection_m"])) for r in rows])

W, H = 1000, 640
img = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(img)
f1, f2 = font(20), font(15)
ox, oy, sx, sy = 100, 300, 820, 230
dr.line([(ox, oy), (ox + sx, oy)], fill="black", width=2)
dr.line([(ox, oy), (ox, oy - sy)], fill="black", width=2)
for v in range(0, 7):
    x = ox + v / 6.5 * sx
    dr.line([(x, oy), (x, oy + 6)], fill="black")
    dr.text((x - 8, oy + 10), str(v), fill="black", font=f2)
for v in range(0, 501, 100):
    yy = oy - v / 500 * sy
    dr.line([(ox - 6, yy), (ox, yy)], fill="black")
    dr.text((ox - 42, yy - 9), str(v), fill="black", font=f2)
dr.line([(ox + 0.0 / 6.5 * sx, oy - 400 / 500 * sy), (ox + sx, oy - 400 / 500 * sy)],
        fill=(220, 120, 120), width=2)
dr.text((ox + sx - 150, oy - 400 / 500 * sy - 24), "许用 400 MPa", fill=(200, 60, 60), font=f2)
pts = [(ox + yy / 6.5 * sx, oy - ss / 500 * sy) for yy, ss in zip(y, s)]
dr.line(pts, fill=(200, 30, 30), width=3)
dr.text((ox + 20, oy - sy - 30), "缘条压应力 σ(y) — 6g 工况", fill=(200, 30, 30), font=f2)

oy2 = 620
dr.line([(ox, oy2), (ox + sx, oy2)], fill="black", width=2)
dr.line([(ox, oy2), (ox, oy2 - sy)], fill="black", width=2)
for v in range(0, 7):
    x = ox + v / 6.5 * sx
    dr.line([(x, oy2), (x, oy2 + 6)], fill="black")
    dr.text((x - 8, oy2 + 10), str(v), fill="black", font=f2)
for v in np.arange(0, 0.61, 0.1):
    yy = oy2 - v / 0.6 * sy
    dr.line([(ox - 6, yy), (ox, yy)], fill="black")
    dr.text((ox - 42, yy - 9), f"{v:.1f}", fill="black", font=f2)
pts = [(ox + yy / 6.5 * sx, oy2 - dd / 0.6 * sy) for yy, dd in zip(y, d)]
dr.line(pts, fill=(30, 90, 200), width=3)
dr.text((ox + 20, oy2 - sy - 30), "垂直挠度 w(y) — 6g 工况 (m)", fill=(30, 90, 200), font=f2)
dr.text((ox + sx / 2 - 30, oy2 + 34), "y (m)", fill="black", font=f2)
img.save(os.path.join(FIG, "strength.png"))
print("saved strength.png")
