"""Preliminary spar strength / stiffness check using the lifting-line load."""
import numpy as np, json, os, csv

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
RES = os.path.join(ROOT, "results")
import importlib.util
spec = importlib.util.spec_from_file_location("ll", os.path.join(ROOT, "scripts", "04_lifting_line.py"))
ll = importlib.util.module_from_spec(spec); spec.loader.exec_module(ll)

# design table (04_翼面结构初步设计.md)
yd = np.array([0.0, 0.65, 1.63, 3.25, 4.88, 6.5])
dd = np.array([0.200, 0.190, 0.175, 0.150, 0.125, 0.090])       # cap separation, m
td = np.array([0.0080, 0.0067, 0.0048, 0.0022, 0.0006, 0.0006])  # cap thickness, m
W_CAP = 0.020
E = 120e9
SIG_A = 400e6

def props(y):
    d = np.interp(y, yd, dd); t = np.interp(y, yd, td)
    A = W_CAP * t
    I = 2 * A * (d / 2) ** 2
    return d, A, I

# 6 g load case
W = 155 * 9.81 * 6
rc = ll.solve(0.0)
# scale the 1 g solution to n=6
scale = W / rc["L"]
y = rc["y"][rc["y"] >= 0]
G = rc["G"][rc["y"] >= 0] * scale
q = 1.225 * 15.0 * G                     # N/m lift per unit span

def integrate_from_tip(f):
    """integral of f dy measured from the wing tip inward (0 at the tip)"""
    fs = f[::-1]
    ys = y[::-1]
    out = np.concatenate([[0.0], np.cumsum(0.5 * (fs[1:] + fs[:-1]) * np.diff(ys))])
    return out[::-1]

V = integrate_from_tip(q)          # shear, N
M = np.abs(integrate_from_tip(V))  # bending moment, N*m

# stress
d, A, I = props(y)
sig = M / (d * A)
sig_mpa = sig / 1e6
MS = SIG_A / np.maximum(sig, 1) - 1

# deflection: curvature kappa = M/(EI), double integration from the tip
kap = M / (E * I)
theta = integrate_from_tip(kap)
deflection = -integrate_from_tip(theta)

with open(os.path.join(RES, "strength.csv"), "w", newline="") as f:
    wri = csv.writer(f)
    wri.writerow(["y_m", "M_Nm", "cap_stress_MPa", "MS", "deflection_m", "shear_N"])
    for k in range(len(y)):
        wri.writerow([round(y[k], 3), round(M[k], 1), round(sig_mpa[k], 1),
                      round(MS[k], 2), round(deflection[k], 4), round(V[k], 1)])

out = dict(M_root_6g=float(M[0]), sigma_root_MPa=float(sig_mpa[0]), MS_root=float(MS[0]),
           sigma_max_MPa=float(sig_mpa.max()), y_sigma_max=float(y[np.argmax(sig_mpa)]),
           MS_min=float(MS.min()), tip_deflection_m=float(deflection[0]),
           tip_deflection_pct_span=float(deflection[0] / 6.5 * 100))
json.dump(out, open(os.path.join(RES, "strength_summary.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
