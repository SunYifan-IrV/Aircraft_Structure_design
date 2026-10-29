#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01 理论设计 —— 翼面气动与结构初步计算脚本
"人机合一"低空个人飞行器（固定翼滑翔型，刚性翼 + 俯卧挂载）

仅用标准库，可复现文档 01_Theory 中的全部数值。
运行： python calc_wing.py
"""
import math

# ---------------------------------------------------------------------------
# 0. 常数与需求冻结输入（来自 00_设计需求.md）
# ---------------------------------------------------------------------------
G      = 9.81        # m/s^2
RHO0   = 1.225       # 海平面标准大气密度 kg/m^3
CLMAX  = 1.5         # 设计最大升力系数（带襟副翼）
M_EMPTY   = 60.0     # 空机质量 kg
M_PILOT_N = 75.0     # 名义乘员质量 kg
M_PILOT_X = 95.0     # 结构最大乘员质量 kg（定 MTOW）
SF      = 1.5        # 安全系数（极限/限制）
N_LIM_P = 4.0        # 正过载 限制 +g
N_LIM_N = -2.0       # 负过载 限制 -g
S       = 20.0       # 机翼面积 m^2
B       = 13.0       # 翼展 m
LAMBDA  = 0.5        # 梢根比（锥度比） c_t/c_r

print("=" * 78)
print("01 理论设计计算 —— 人机合一低空个人飞行器")
print("=" * 78)

# ---------------------------------------------------------------------------
# 1. 总质量与翼面所需面积
# ---------------------------------------------------------------------------
print("\n[1] 总质量与翼面所需面积")
M_nom = M_EMPTY + M_PILOT_N
M_max = M_EMPTY + M_PILOT_X
W_nom = M_nom * G
W_max = M_max * G
print(f"  名义起飞质量 M = {M_nom:.1f} kg,  W = {W_nom:.1f} N")
print(f"  最大起飞质量 MTOW = {M_max:.1f} kg,  W = {W_max:.1f} N")

# 失速约束反算翼面积： S = 2W_max / (rho CLmax V_stall^2)
V_STALL_MAX = 9.0    # 双脚软着陆目标失速速度 m/s
S_need = 2 * W_max / (RHO0 * CLMAX * V_STALL_MAX ** 2)
print(f"  失速目标 V_stall <= {V_STALL_MAX} m/s @CLmax={CLMAX}")
print(f"  所需翼面积 S = 2*{W_max:.0f}/({RHO0}*{CLMAX}*{V_STALL_MAX}^2) = {S_need:.2f} m^2  -> 取 S = {S:.0f} m^2")
print(f"  翼载 W/S  名义 {W_nom/S:.1f} N/m^2  |  最大 {W_max/S:.1f} N/m^2")

# ---------------------------------------------------------------------------
# 2. 翼展 / 平均弦长 / 展弦比（给定锥度比 lambda=0.5 的直线梯形翼）
# ---------------------------------------------------------------------------
print("\n[2] 翼展 / 平均弦长 / 展弦比")
AR = B ** 2 / S
c_mean = S / B                      # 平均几何弦长
c_r = 2 * S / (B * (1 + LAMBDA))     # 根弦
c_t = LAMBDA * c_r                   # 梢弦
MAC = (2 / 3) * c_r * (1 + LAMBDA + LAMBDA ** 2) / (1 + LAMBDA)  # 平均气动弦长
y_mac = (B / 2) * (1 + 2 * LAMBDA) / (3 * (1 + LAMBDA))          # MAC 展向位置
print(f"  展弦比 AR = b^2/S = {AR:.2f}  (取 ~8.5)")
print(f"  平均几何弦长 c_mean = S/b = {c_mean:.3f} m")
print(f"  根弦 c_r = {c_r:.3f} m,  梢弦 c_t = {c_t:.3f} m  (lambda={LAMBDA})")
print(f"  平均气动弦长 MAC = {MAC:.3f} m  位于展向 y = {y_mac:.3f} m")

# ---------------------------------------------------------------------------
# 3. 设计飞行速度包线
# ---------------------------------------------------------------------------
print("\n[3] 设计飞行速度包线")
def v_level(CL):
    return math.sqrt(2 * W_nom / (RHO0 * S * CL))

V_stall_nom = v_level(CLMAX)
V_stall_max = math.sqrt(2 * W_max / (RHO0 * S * CLMAX))
V_cruise_lo = v_level(0.60)   # 巡航下界 CL
V_cruise_hi = v_level(0.45)   # 巡航上界 CL
V_bestld    = v_level(0.72)   # (L/D)max 附近
V_NE = 25.0
V_D  = 1.111 * V_NE
print(f"  失速 V_stall 名义 {V_stall_nom:.2f} m/s ({V_stall_nom*3.6:.0f} km/h)")
print(f"  失速 V_stall 最大 {V_stall_max:.2f} m/s ({V_stall_max*3.6:.0f} km/h)")
print(f"  巡航 V_C ~ {V_cruise_lo:.1f}-{V_cruise_hi:.1f} m/s (CL 0.45-0.60)")
print(f"  最佳滑翔 (L/D)max ~ V = {V_bestld:.1f} m/s")
print(f"  V_NE = {V_NE:.0f} m/s,  V_D = {V_D:.1f} m/s (100 km/h)")

# ---------------------------------------------------------------------------
# 4. 升力分布（Schrenk 近似）与翼根剪力 / 弯矩
# ---------------------------------------------------------------------------
print("\n[4] 升力分布与翼根剪力/弯矩")
# Schrenk： 局部升力 ∝ c_sch = (c_ell + c_plan)/2
c_ell0 = (4 / math.pi) * c_mean     # 椭圆分布等效根弦

def c_ell(eta):   return c_ell0 * math.sqrt(max(0.0, 1 - eta * eta))
def c_plan(eta):  return c_r - (c_r - c_t) * eta
def c_sch(eta):   return 0.5 * (c_ell(eta) + c_plan(eta))

def span_loads(nW):
    """给定总载荷 nW(N)，返回 (q(N/m), V(N), M(N·m)) 沿半翼展 eta 的采样函数"""
    q0 = nW / S                     # 单位弦长"升力密度" = n*(W/S)
    # 数值积分（梯形，N=2000 段）
    N = 2000
    deta = 1.0 / N
    etas = [i * deta for i in range(N + 1)]
    q = [q0 * c_sch(eta) for eta in etas]
    # 从 y 到翼尖积分： V(y) = int_y^{b/2} q dy',  M(y) = int_y^{b/2} q (y'-y) dy'
    dy = (B / 2) * deta
    V = [0.0] * (N + 1)
    M = [0.0] * (N + 1)
    # 从翼尖向根累积（剪力/弯矩的符号按"外伸段载荷"取正）
    for i in range(N - 1, -1, -1):
        # 梯形小块 [i, i+1]，其相对 y_i 的力臂
        V[i] = V[i + 1] + 0.5 * (q[i] + q[i + 1]) * dy
        M[i] = M[i + 1] + V[i + 1] * dy + 0.5 * (q[i] + q[i + 1]) * dy * (0.5 * dy) \
               + (q[i] - q[i + 1]) * dy * dy / 6.0
    def v_at(eta):
        i = int(round(eta * N)); return V[i]
    def m_at(eta):
        i = int(round(eta * N)); return M[i]
    return q, v_at, m_at, etas, N

# 限制载荷（+4g @ MTOW）与极限载荷（+6g）
nW_lim  = N_LIM_P * W_max
nW_ult  = N_LIM_P * SF * W_max
nW_lim_n= N_LIM_N * W_max
nW_ult_n= N_LIM_N * SF * W_max

q, Vat, Mat, etas, N = span_loads(nW_lim)
V_root_lim = Vat(0.0)
M_root_lim = Mat(0.0)
V_root_ult = V_root_lim * SF
M_root_ult = M_root_lim * SF

# 椭圆分布对照（解析）： V0=nW/2, M0 = (nW/S)(b^2/4)(4/(3pi) c_mean)
M_root_ell = (nW_lim / S) * (B ** 2 / 4) * (4 / (3 * math.pi)) * c_mean

print(f"  限制载荷 nW = {nW_lim:.0f} N (+{N_LIM_P:.0f}g @ MTOW)")
print(f"  单侧翼根剪力 V_root(lim) = {V_root_lim:.0f} N   (={nW_lim/2:.0f} = nW/2)")
print(f"  单侧翼根弯矩 M_root(lim) = {M_root_lim:.0f} N·m")
print(f"  极限(×1.5)   V_root(ult) = {V_root_ult:.0f} N,  M_root(ult) = {M_root_ult:.0f} N·m")
print(f"  [对照] 纯椭圆分布 M_root = {M_root_ell:.0f} N·m  (Schrenk 因梯形外移略大)")
print(f"  升力合力作用点  y_bar = M/V = {M_root_lim/V_root_lim:.3f} m "
      f"({M_root_lim/V_root_lim/(B/2)*100:.1f}% 半翼展)")

print("\n  展向剪力/弯矩表（限制 +4g，单侧翼）：")
print(f"  {'eta(2y/b)':>8} {'y(m)':>7} {'q(N/m)':>8} {'V(N)':>8} {'M(N·m)':>9}")
for eta in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
    i = int(round(eta * N))
    y = eta * B / 2
    print(f"  {eta:>8.2f} {y:>7.3f} {q[i]:>8.1f} {Vat(eta):>8.0f} {Mat(eta):>9.0f}")

# ---------------------------------------------------------------------------
# 5. 阵风校核（含缓和因子）
# ---------------------------------------------------------------------------
print("\n[5] 阵风校核（CS-23 缓和因子）")
e_osw = 0.85
a0 = 2 * math.pi
CLalpha = a0 / (1 + a0 / (math.pi * e_osw * AR))   # rad^-1
WS = W_max / S
for Vname, Vg, Ude in [("V_C 巡航", v_level(0.55), 9.0), ("V_D 俯冲", V_D, 9.0)]:
    mu = 2 * WS / (RHO0 * MAC * G * CLalpha)
    Kg = 0.88 * mu / (5.3 + mu)
    dn_un = RHO0 * Vg * Ude * CLalpha / (2 * WS)
    dn_mi = Kg * dn_un
    print(f"  {Vname} (V={Vg:.1f} m/s, Ude={Ude} m/s):")
    print(f"    CLalpha={CLalpha:.3f} rad^-1, mu_g={mu:.3f}, K_g={Kg:.3f}")
    print(f"    未缓和 Δn={dn_un:.2f}g  缓和后 Δn={dn_mi:.2f}g  -> n={1+dn_mi:.2f}g (限制)")

# ---------------------------------------------------------------------------
# 6. 翼梁 / 翼肋 / 蒙皮 初选
# ---------------------------------------------------------------------------
print("\n[6] 翼梁 / 翼肋 / 蒙皮 初选")
D_ROOT = 0.20                    # 翼梁上下缘条形心间距（根） m
SIG_C = 400e6                    # 碳纤维单向 压缩设计许用(含屈曲折减) Pa
SIG_T = 900e6                    # 碳纤维单向 拉伸设计许用 Pa
TAU   = 60e6                     # ±45 碳纤维 剪切许用 Pa
print(f"  主梁高度 d_root={D_ROOT*1000:.0f} mm（盒型梁缘条形心距，随弦长递减）")
print(f"  许用应力 压缩 {SIG_C/1e6:.0f} MPa / 拉伸 {SIG_T/1e6:.0f} MPa / 剪切 {TAU/1e6:.0f} MPa")
A_cap_req_c = M_root_ult / (D_ROOT * SIG_C)     # 受压控制
A_cap_req_t = M_root_ult / (D_ROOT * SIG_T)
print(f"  根截面缘条需面积(压/拉): {A_cap_req_c*1e6:.0f} / {A_cap_req_t*1e6:.0f} mm^2")

# 展向缘条面积需求（20mm 定宽 → 厚度）
print("  展向缘条设计（宽度 20mm 定宽，厚度随 M 递减）：")
print(f"  {'eta':>6} {'y(m)':>7} {'d(mm)':>7} {'M_ult(N·m)':>11} {'A_cap(mm^2)':>11} {'t_cap(mm)':>9}")
for eta in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
    y = eta * B / 2
    c_local = c_plan(eta)
    d = D_ROOT * (c_local / c_r)
    M_ult = Mat(eta) * SF
    A_cap = M_ult / (d * SIG_C) if d > 1e-6 else 0.0
    t = A_cap / 0.020 * 1e3 if A_cap > 0 else 0.0   # mm
    print(f"  {eta:>6.2f} {y:>7.3f} {d*1000:>7.1f} {M_ult:>11.0f} {A_cap*1e6:>11.1f} {t:>9.2f}")

# 剪切腹板
t_web = V_root_ult / (D_ROOT * TAU)
print(f"  腹板需厚度 t_web = V_ult/(d·tau) = {t_web*1e3:.2f} mm（盒型梁双侧共）")

# 蒙皮/翼肋局部载荷
q_root_lim = (nW_lim / S) * c_sch(0.0)
RIB_SPACING = 0.45
print(f"  根部单位翼展升力 q_root(lim) = {q_root_lim:.0f} N/m")
print(f"  翼肋间距 s = {RIB_SPACING:.2f} m -> 单肋承载(lim) = {q_root_lim*RIB_SPACING:.0f} N, "
      f"(ult) = {q_root_lim*RIB_SPACING*SF:.0f} N")
print(f"  肋数/侧 = 6.5/{RIB_SPACING:.2f} ≈ {int(round(6.5/RIB_SPACING))} 肋")

# ---------------------------------------------------------------------------
# 7. 人体支撑传力（接触压力校核）
# ---------------------------------------------------------------------------
print("\n[7] 人体支撑传力路径（接触压力校核）")
for label, m in [("名义 75kg", M_PILOT_N), ("最大 95kg", M_PILOT_X)]:
    for n in [1.0, N_LIM_P]:
        F = n * m * G
        for area, aname in [(0.25, "躯干托板 ~0.25 m^2"), (0.055, "仅胸+骨盆带 ~0.055 m^2")]:
            p = F / area / 1e3   # kPa
            print(f"  {label} {n:+.0f}g  F={F:.0f}N  {aname}: p={p:.1f} kPa")

print("\n" + "=" * 78)
print("计算完成")
