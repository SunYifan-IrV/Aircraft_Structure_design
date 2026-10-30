#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_CATIA 整机几何 / 质量 校验脚本（可复现，仅标准库）
====================================================
作用：在写 CATScript / 建模之前，先把整机的关键几何数值、翼梁是否装得进翼型、
     各部件体积与质量、重心位置算出来并自检，保证 02_CATIA 里所有脚本与
     《建模说明.md》用到的数字彼此一致。

运行： python scripts/verify_geometry.py
"""
import math, os

# ---------------------------------------------------------------------------
# 0. 常量与设计参数（与 02_CATIA/scripts 各 CATScript 保持一致）
# ---------------------------------------------------------------------------
G = 9.81
DEG = math.pi / 180.0

# 翼面总体
WING_SPAN   = 13000.0     # 翼展 b (mm)
ROOT_CHORD  = 2051.0      # 根弦 c_r
TIP_CHORD   = 1026.0      # 梢弦 c_t
HALF_SPAN   = WING_SPAN / 2.0
DIHEDRAL    = 4.0         # 上反角 deg
WASHOUT     = -2.0        # 翼尖洗流 deg
RIB_SPACING = 450.0

# 翼梁
SPAR_CHORD_POS   = 0.30
REAR_SPAR_POS    = 0.65
SPAR_WIDTH       = 40.0    # 主梁弦向宽 (mm)
SPAR_DEPTH_ROOT  = 200.0   # 主梁高 (mm)
REAR_WIDTH       = 30.0
REAR_DEPTH_ROOT  = 80.0
WALL_T           = 3.0     # 盒梁壁厚（空腔箱梁，近似均匀）

# 翼肋 / 蒙皮
RIB_THICKNESS = 3.0
SKIN_THICKNESS = 2.0

# 中央承力盒 / 龙骨 / 折叠铰
CENTRAL_BOX_SPAN  = 1600.0   # 展向 y=-800..+800
CENTRAL_BOX_WIDTH = 160.0    # 弦向宽
CENTRAL_BOX_DEPTH = 200.0    # 深
HINGE_Y   = 800.0
KEEL_LEN  = 1800.0
KEEL_Z    = -250.0

# 动力单元
MOTOR_D = 140.0 ; MOTOR_L = 80.0
MOTOR_X = 1350.0 ; MOTOR_Z = 200.0
PROP_D  = 1500.0 ; PROP_CHORD = 120.0 ; PROP_T = 8.0 ; PROP_BLADES = 2
BATTERY = (500.0, 240.0, 100.0)      # 电池 (Lx, Ly, Lz) mm
BATTERY_XYZ = (350.0, 0.0, -320.0)   # 电池中心
ESC = (150.0, 100.0, 40.0)
ESC_XYZ = (1300.0, 0.0, 140.0)

# 人体支撑
CRADLE = (1000.0, 400.0, 10.0)       # 托板 (Lx, Ly, Lz)
CRADLE_XYZ = (700.0, 0.0, -460.0)    # 托板中心
HANG_X = 500.0 ; HANG_Z = -350.0     # 挂点

# 材料密度 (kg/m^3)
RHO_CFRP = 1550.0   # 碳纤维
RHO_AL   = 2810.0   # 7075-T6 铝
RHO_KEV  = 1440.0   # 芳纶
RHO_STEEL= 7850.0   # 高强钢（铰销）
RHO_CU   = 8940.0   # 铜（电机绕组，仅用于粗略估计）

HERE = os.path.dirname(os.path.abspath(__file__))
AIR  = os.path.join(HERE, "..", "airfoil")


def read_loop_csv(name):
    pts = []
    with open(os.path.join(AIR, name)) as f:
        for line in f:
            t = line.split(",")
            if len(t) == 2:
                try:
                    x, y = float(t[0]), float(t[1])
                except ValueError:
                    continue
                pts.append((x, y))
    return pts


def airfoil_y_at(pts, x):
    """在翼型环上按弦向 x 插值，返回该 x 处上/下表面 y（厚度方向归一化）。"""
    ups, lows = [], []
    for (px, py) in pts:
        if px < 1e-6:  # 前缘
            continue
        if py >= 0:
            ups.append((px, py))
        else:
            lows.append((px, py))
    def interp(series, x):
        series.sort()
        for i in range(len(series) - 1):
            x0, y0 = series[i]
            x1, y1 = series[i + 1]
            if x0 <= x <= x1:
                if abs(x1 - x0) < 1e-9:
                    return 0.5 * (y0 + y1)
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return series[-1][1]
    return interp(ups, x), interp(lows, x)


def chord(y):
    return ROOT_CHORD - (ROOT_CHORD - TIP_CHORD) * (y / HALF_SPAN)


def dihedral_lift(y):
    return y * math.tan(DIHEDRAL * DEG)


def washout_deg(y):
    return WASHOUT * (y / HALF_SPAN)


def main_spar_center_x(y):
    return SPAR_CHORD_POS * chord(y)


def rear_spar_center_x(y):
    return REAR_SPAR_POS * chord(y)


print("=" * 80)
print("02_CATIA 整机几何 / 质量 校验")
print("=" * 80)

fx = read_loop_csv("fx63137_loop.csv")
e387 = read_loop_csv("e387_loop.csv")
print(f"\n翼型点：FX63-137  {len(fx)} 点,  E387  {len(e387)} 点")

# ---------------------------------------------------------------------------
# 1. 翼梁是否装得进翼型（关键自检）
# ---------------------------------------------------------------------------
print("\n[1] 翼梁截面 vs 翼型厚度（30%/65% 弦处）")
print(f"  {'y(mm)':>7} {'c(mm)':>7} {'zdih':>7} {'t@30%':>7} {'mid@30%':>8} {'mainD':>6} {'fit30%':>6}")
for y in [0.0, 800.0, 1625.0, 3250.0, 4875.0, 6500.0]:
    c = chord(y)
    zd = dihedral_lift(y)
    x30 = 0.30  # 弦向站位
    yu, yl = airfoil_y_at(fx, x30)
    mid = 0.5 * (yu + yl)
    thick = (yu - yl) * c
    D = SPAR_DEPTH_ROOT * (c / ROOT_CHORD)
    half_d = D / 2.0
    ztop = (mid * c) + zd + half_d
    zbot = (mid * c) + zd - half_d
    # 翼型上/下表面（全局，含上反）
    surf_top = yu * c + zd
    surf_bot = yl * c + zd
    fit = (ztop <= surf_top + 1.0) and (zbot >= surf_bot - 1.0)
    print(f"  {y:>7.0f} {c:>7.1f} {zd:>7.1f} {thick:>7.1f} {mid*c:>8.1f} {D:>6.1f} {'OK' if fit else '!!外露':>6}")

print("\n  说明：主梁盒沿 30% 弦放置，中心对齐翼型中厚线(mid)，高度随弦长线性递减。")

# ---------------------------------------------------------------------------
# 2. 各部件体积与质量（用规则几何近似）
# ---------------------------------------------------------------------------
print("\n[2] 各部件体积 / 质量估算")
mm3 = 1e-9  # mm^3 -> m^3

def hollow_box_mass(L, w, d0, d1, wall, rho):
    """梯形锥度空心盒梁（壁厚 wall）的体积近似：外盒体积 - 内盒体积。"""
    def v(w_, d0_, d1_):
        # 线性锥度盒体积 = L * w * (d0+d1)/2  （宽 w 不变，深线性）
        return L * w_ * (d0_ + d1_) / 2.0
    Vout = v(w, d0, d1)
    Vin  = v(w - 2 * wall, d0 - 2 * wall, d1 - 2 * wall)
    return (Vout - Vin) * mm3 * rho

def solid_box_mass(L, w, d, rho):
    return (L * w * d) * mm3 * rho

def cyl_mass(D, L, rho, hollow=False, wall=3.0):
    if hollow:
        V = (math.pi / 4) * (D ** 2 - (D - 2 * wall) ** 2) * L
    else:
        V = (math.pi / 4) * D ** 2 * L
    return V * mm3 * rho

masses = {}

# 主梁（空心盒，壁厚 3mm，锥度 200->100）
m_main = hollow_box_mass(HALF_SPAN, SPAR_WIDTH, SPAR_DEPTH_ROOT,
                         SPAR_DEPTH_ROOT * TIP_CHORD / ROOT_CHORD, WALL_T, RHO_CFRP)
masses["主梁 x2 (空心盒)"] = 2 * m_main

# 后梁（空心盒，锥度 80->40）
m_rear = hollow_box_mass(HALF_SPAN, REAR_WIDTH, REAR_DEPTH_ROOT,
                         REAR_DEPTH_ROOT * TIP_CHORD / ROOT_CHORD, WALL_T, RHO_CFRP)
masses["后梁 x2 (空心盒)"] = 2 * m_rear

# 翼肋：14 肋/侧，每肋近似翼型面积*厚度。翼型面积 ~0.6 * c^2 * (t/c 平均)
# FX63-137 面积系数（单位弦长翼型截面积 ~0.62 * chord * maxthick）
FX_AREA = 0.08312          # FX63-137 翼型面积系数（单位弦长截面积，数值积分）
def rib_plate_mass(n_ribs):
    total = 0.0
    for k in range(n_ribs):
        y = RIB_SPACING * (k + 1)  # 450,900,...
        c = chord(y)
        area = FX_AREA * c * c     # 翼型截面积 = 0.08312·c²
        total += area * RIB_THICKNESS
    return total * mm3 * RHO_CFRP

masses["翼肋 x2 (14肋/侧)"] = 2 * rib_plate_mass(14)

# 蒙皮：全翼 20 m^2 * 2mm（夹芯等效密度折半，用 CFRP 密度算上界）
wing_area_m2 = WING_SPAN * (ROOT_CHORD + TIP_CHORD) / 2.0 / 1e6  # m^2
m_skin = wing_area_m2 * (SKIN_THICKNESS / 1000.0) * RHO_CFRP
masses["蒙皮 (20m^2 x 2mm)"] = m_skin

# 中央承力盒（空心盒 y=-800..800，长 1600，宽 160，深 200，壁 3）
m_cbox = hollow_box_mass(CENTRAL_BOX_SPAN, CENTRAL_BOX_WIDTH,
                         CENTRAL_BOX_DEPTH, CENTRAL_BOX_DEPTH, WALL_T, RHO_CFRP)
masses["中央承力盒 (空心)"] = m_cbox

# 龙骨：铝管 φ40 x 3mm，长 1800
m_keel = cyl_mass(40.0, KEEL_LEN, RHO_AL, hollow=True, wall=3.0)
masses["龙骨 (铝管 φ40x3)"] = m_keel

# 折叠铰（每侧 3 个铰：主梁上/下 + 后梁），每铰 2 耳片 + 1 销
def hinge_mass():
    # 耳片：2 片 60x40x8 铝板；销：钢 φ12 x 60
    lug = 2 * solid_box_mass(60.0, 40.0, 8.0, RHO_AL)
    pin = cyl_mass(12.0, 60.0, RHO_STEEL)
    return lug + pin
masses["折叠铰 x6 (3铰/侧x2)"] = 6 * hinge_mass()

# 螺旋桨塔（pylon）：两根竖管 φ25x2 + 一根横梁，铝
def pylon_mass():
    tube_v = cyl_mass(25.0, (MOTOR_Z - KEEL_Z), RHO_AL, hollow=True, wall=2.0)
    beam = cyl_mass(25.0, 260.0, RHO_AL, hollow=True, wall=2.0)
    return 2 * tube_v + beam
masses["螺旋桨塔 pylon"] = pylon_mass()

# 电机：φ140 x 80 实心铜/钢混合，取 ~5 kg 级（含磁钢），这里体积法粗估
m_motor = cyl_mass(MOTOR_D, MOTOR_L, RHO_CU) * 0.35   # 铜填充率 35%
masses["电机 (φ140x80)"] = m_motor

# 螺旋桨：2 片，每片 730x120x8 碳纤维，+ 桨毂
blade = solid_box_mass(730.0, PROP_CHORD, PROP_T, RHO_CFRP)
hub = cyl_mass(40.0, 40.0, RHO_AL)
masses["螺旋桨 (2 片+毂)"] = 2 * blade + hub

# 电池：500x240x100 箱，等效密度 ~1167 kg/m^3（3kWh@220Wh/kg ≈ 14kg 封装密度）
m_bat = (BATTERY[0] * BATTERY[1] * BATTERY[2]) * mm3 * 1167.0
masses["电池组 (3kWh 48V)"] = m_bat

# ESC
m_esc = (ESC[0] * ESC[1] * ESC[2]) * mm3 * RHO_AL * 0.3
masses["ESC 控制器"] = m_esc

# 人体支撑托板（CFRP 夹芯 1000x400x10，等效 800）
m_cradle = (CRADLE[0] * CRADLE[1] * CRADLE[2]) * mm3 * 800.0
masses["躯干托板"] = m_cradle

# 挂带（芳纶织带：4 根 50x5 x 400）
m_strap = 4 * solid_box_mass(400.0, 50.0, 5.0, RHO_KEV)
masses["载荷挂带 (4 根)"] = m_strap

total = 0.0
for k, v in masses.items():
    total += v
    print(f"  {k:<24} {v:>7.2f} kg")
print(f"  {'-'*34}")
print(f"  {'整机结构/动力合计':<24} {total:>7.2f} kg")

# 加上乘员 75/95 kg
print(f"\n  + 乘员 75 kg -> 起飞质量 {total+75:.1f} kg")
print(f"  + 乘员 95 kg -> 起飞质量 {total+95:.1f} kg")

# ---------------------------------------------------------------------------
# 3. 重心（含乘员，简化：乘员质心在挂点附近）
# ---------------------------------------------------------------------------
print("\n[3] 重心 / 挂点位置（简化）")
# 各部件质心 (x, z)（y=0 对称，略去 y）
comps = [
    (masses["主梁 x2 (空心盒)"], main_spar_center_x(HALF_SPAN/2), dihedral_lift(HALF_SPAN/2)/2),
    (masses["后梁 x2 (空心盒)"], rear_spar_center_x(HALF_SPAN/2), dihedral_lift(HALF_SPAN/2)/2),
    (masses["翼肋 x2 (14肋/侧)"], 0.45*ROOT_CHORD, 0.0),
    (masses["蒙皮 (20m^2 x 2mm)"], 0.45*ROOT_CHORD, dihedral_lift(HALF_SPAN)/2),
    (masses["中央承力盒 (空心)"], SPAR_CHORD_POS*ROOT_CHORD, 0.0),
    (masses["龙骨 (铝管 φ40x3)"], 900.0, KEEL_Z),
    (masses["折叠铰 x6 (3铰/侧x2)"], main_spar_center_x(HINGE_Y), dihedral_lift(HINGE_Y)),
    (masses["螺旋桨塔 pylon"], MOTOR_X, (MOTOR_Z+KEEL_Z)/2),
    (masses["电机 (φ140x80)"], MOTOR_X, MOTOR_Z),
    (masses["螺旋桨 (2 片+毂)"], MOTOR_X + 80.0, MOTOR_Z),
    (masses["电池组 (3kWh 48V)"], BATTERY_XYZ[0], BATTERY_XYZ[2]),
    (masses["ESC 控制器"], ESC_XYZ[0], ESC_XYZ[2]),
    (masses["躯干托板"], CRADLE_XYZ[0], CRADLE_XYZ[2]),
    (masses["载荷挂带 (4 根)"], HANG_X, (HANG_Z+CRADLE_XYZ[2])/2),
]
Mx = sum(m * x for m, x, z in comps)
Mz = sum(m * z for m, x, z in comps)
Mtot = sum(m for m, x, z in comps)
cg_x, cg_z = Mx / Mtot, Mz / Mtot
print(f"  结构(不含乘员)质心: x={cg_x:.0f} mm, z={cg_z:.0f} mm, 质量={Mtot:.1f} kg")

# 加乘员（质心约在托板中央 x=700, z=-430）
Mp = 75.0
Mx2 = Mx + Mp * 700.0
Mz2 = Mz + Mp * (-430.0)
Mtot2 = Mtot + Mp
print(f"  含乘员 75kg 整机质心: x={Mx2/Mtot2:.0f} mm, z={Mz2/Mtot2:.0f} mm")
print(f"  挂点位置: x={HANG_X} mm, z={HANG_Z} mm  (挂点应接近整机质心正上方)")

# ---------------------------------------------------------------------------
# 4. 螺旋桨 / 机翼 / 乘员 间隙自检
# ---------------------------------------------------------------------------
print("\n[4] 间隙自检")
prop_r = PROP_D / 2.0
prop_tip_z_top = MOTOR_Z + prop_r
prop_tip_z_bot = MOTOR_Z - prop_r
print(f"  桨盘半径 {prop_r:.0f} mm, 桨尖上 {prop_tip_z_top:.0f} mm / 下 {prop_tip_z_bot:.0f} mm")
# 桨盘平面在 x = MOTOR_X+80；乘员头部约在 x=1100, z=-400
print(f"  电机中心 (x={MOTOR_X}, z={MOTOR_Z}), 乘员躯干 (x~200..1200, z~-450)")
# 桨下缘是否打到乘员：桨尖下 -550 vs 乘员上表面 -450
print(f"  桨尖下缘 {prop_tip_z_bot:.0f} mm vs 乘员躯干上表面 -450 mm: " +
      ("OK（桨在乘员后方/上方）" if MOTOR_X > 1200 else "注意间隙"))

print("\n" + "=" * 80)
print("校验完成 —— 以上数字应写入 02_CATIA 各 CATScript 与《建模说明.md》保持一致")
print("=" * 80)
