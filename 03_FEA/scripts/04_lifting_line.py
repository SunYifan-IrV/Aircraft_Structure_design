"""Prandtl lifting-line (Glauert Fourier form) for the RevN wing.

Planform & twist from the CATIA sections; section zero-lift angles from
published data for FX 63-137 (root) and E387 (tip).
"""
import numpy as np, json, os, csv

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
CSV_IN = (r"C:\Users\张文博\Downloads\Aircraft_Structure_design-main"
          r"\Aircraft_Structure_design-main\02_CATIA\_wing_skin_sections.csv")
RES = os.path.join(ROOT, "results")
os.makedirs(RES, exist_ok=True)

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

st = []
for k, pts in secs.items():
    _, side, idx, y, _, _ = k.split("|")
    if side != "R":
        continue
    y = float(y) / 1000.0
    x = pts[:, 0] / 1000.0
    z = pts[:, 1] / 1000.0
    st.append(dict(y=y, c=float(x.max() - x.min()),
                   zle=float(z[np.argmin(x)]), zte=float(z[np.argmax(x)])))
st.sort(key=lambda s: s["y"])
Y = np.array([s["y"] for s in st])
CH = np.array([s["c"] for s in st])
TW = -np.arctan2(np.array([s["zte"] - s["zle"] for s in st]), CH)

AL0 = np.radians(np.where(Y <= 4.5, -6.0, np.where(Y >= 6.5, -2.5,
                                                  -6.0 + 3.5 * (Y - 4.5) / 2.0)))

B, S = 13.0, 20.0
AR = B * B / S
NH = 30
th_c = np.arange(1, NH + 1) * np.pi / (NH + 1)
yc = -0.5 * B * np.cos(th_c)
ay = np.abs(yc)
C = np.interp(ay, Y, CH)
TWc = np.interp(ay, Y, TW)
AL0c = np.interp(ay, Y, AL0)
A0 = 2 * np.pi

def solve(alpha_deg, V=15.0):
    a = np.radians(alpha_deg)
    n = np.arange(1, NH + 1)
    M = np.zeros((NH, NH)); rhs = np.zeros(NH)
    for i in range(NH):
        s = np.sin(th_c[i])
        M[i, :] = 2 * B * np.sin(n * th_c[i]) + 0.5 * A0 * C[i] * n * np.sin(n * th_c[i]) / s
        rhs[i] = 0.5 * A0 * C[i] * (a + TWc[i] - AL0c[i])
    A = np.linalg.solve(M, rhs)
    rho = 1.225
    CL = np.pi * AR * A[0]
    CDi = np.pi * AR * np.sum(n * A ** 2)
    th = np.linspace(1e-5, np.pi - 1e-5, 241)
    y = -0.5 * B * np.cos(th)
    G = 2 * B * V * sum(A[k] * np.sin((k + 1) * th) for k in range(NH))
    idx = y >= 0
    L = rho * V * np.trapezoid(G, y)
    Mroot = float(rho * V * np.trapezoid((G * y)[idx], y[idx]))
    ai = np.degrees(np.sum([(k + 1) * A[k] * np.sin((k + 1) * th) for k in range(NH)],
                           axis=0) / np.sin(th))
    c_loc = np.interp(np.abs(y), Y, CH)
    return dict(alpha=alpha_deg, CL=float(CL), CDi=float(CDi), L=float(L),
                Mroot=Mroot, A=A, th=th, y=y, G=G, ai=ai,
                cl=2 * G / (V * c_loc), chord=c_loc)

if __name__ == "__main__":
    alphas = np.arange(-6, 12.01, 0.5)
    res = [solve(a) for a in alphas]
    Re = 15.0 * 1.6 / 1.46e-5
    Cf = 0.074 / Re ** 0.2
    CD0 = 2 * Cf * (1 + 2 * 0.115 + 60 * 0.115 ** 4) + 0.002
    rows = [dict(alpha=r["alpha"], CL=r["CL"], CDi=r["CDi"], CD0=round(CD0, 5),
                 CD=r["CDi"] + CD0, LD=r["CL"] / (r["CDi"] + CD0)) for r in res]
    with open(os.path.join(RES, "ll_polar.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    W = 135 * 9.81
    CLc = W / (0.5 * 1.225 * 225 * 20)
    ac = float(np.interp(CLc, [r["CL"] for r in rows], [r["alpha"] for r in rows]))
    rc = solve(ac)
    with open(os.path.join(RES, "spanload_ll.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["y_m", "chord_m", "cl_local", "lift_per_span_N_m", "alpha_i_deg", "schrenk_N_m"])
        cr, ct, cbar = 2.05, 1.03, S / B
        for k in range(len(rc["y"])):
            eta = 2 * abs(rc["y"][k]) / B
            c_ell = (4 / np.pi) * cbar * np.sqrt(max(0.0, 1 - eta ** 2))
            c_loc = cr - (cr - ct) * eta
            sch = (W / S) * 0.5 * (c_ell + c_loc)
            w.writerow([round(rc["y"][k], 4), round(float(rc["chord"][k]), 4),
                        round(float(rc["cl"][k]), 4),
                        round(1.225 * 15.0 * float(rc["G"][k]), 2),
                        round(float(rc["ai"][k]), 3), round(sch, 2)])

    LD = [o["LD"] for o in rows]
    best = int(np.argmax(LD))
    summary = dict(CD0=round(CD0, 5), Re=Re, CL_cruise=CLc, alpha_cruise=ac,
                   Mroot_1g=rc["Mroot"], Mroot_6g=rc["Mroot"] * 6,
                   CLalpha_per_deg=(rows[-1]["CL"] - rows[0]["CL"]) / (rows[-1]["alpha"] - rows[0]["alpha"]),
                   LDmax=LD[best], alpha_LDmax=rows[best]["alpha"], CL_at_LDmax=rows[best]["CL"],
                   cl_max_local=float(rc["cl"].max()),
                   stall_speed_ms=float(np.sqrt(2 * W / (1.225 * 20 * 1.5))))
    json.dump(summary, open(os.path.join(RES, "ll_summary.json"), "w"), indent=2)
    print(json.dumps(summary, indent=2))

