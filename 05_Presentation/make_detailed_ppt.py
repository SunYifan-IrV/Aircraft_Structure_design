# -*- coding: utf-8 -*-
"""
把《飞行器结构设计报告.pptx》补充为详细版：
1. 补齐「01 结构设计」5 页内容（设计定位/总体参数/翼型与升力分布/翼面结构/中央承力框架）
2. 补齐「03 总结思考」1 页内容（关键结论 + 方法边界）
3. 为每一页写入逐页讲稿（演讲者备注）

不改动原图/原表，仅在缺失处新增内容页；输出到新文件，原文件保留。
"""
import shutil
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

SRC = "飞行器结构设计报告.pptx"
OUT = "飞行器结构设计报告_详细版.pptx"
BAK = "飞行器结构设计报告_原版备份.pptx"

# ---- 配色（与现有主题一致） ----
DARK    = "003F88"   # 标题深蓝
BLUE    = "1F4E79"   # 标签蓝
BODY    = "404040"   # 正文
GRAY    = "555555"   # 次要灰
ACC_DESIGN = "4472C4"  # 结构设计 蓝
ACC_SIM    = "ED7D31"  # 仿真分析 橙
ACC_SUM    = "70AD47"  # 总结思考 绿
LIGHT_FILL = "EEF3FA"  # 表格浅底
FONT = "等线"

# ---- 字体工具 ----
def _set_ea(run, name):
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', name)

def fmt_run(run, size, bold=False, color=BODY, name=FONT, italic=False):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.name = name
    f.color.rgb = RGBColor.from_string(color)
    _set_ea(run, name)

def add_textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tb, tf

def add_para(tf, segments, size=16, align=PP_ALIGN.LEFT, before=0, after=6,
             line=1.0, level=0, first=False):
    """segments: str 或 [(text, bold, color), ...]"""
    p = tf.paragraphs[0] if (first and not tf.paragraphs[0].runs) else tf.add_paragraph()
    p.alignment = align
    p.level = level
    if before: p.space_before = Pt(before)
    if after is not None: p.space_after = Pt(after)
    p.line_spacing = line
    if isinstance(segments, str):
        segments = [(segments, False, BODY)]
    for text, bold, color in segments:
        r = p.add_run()
        r.text = text
        fmt_run(r, size, bold, color)
    return p

def add_title(slide, text, accent=ACC_DESIGN, sub=None):
    # 标题
    _, tf = add_textbox(slide, 0.59, 0.28, 12.0, 0.7)
    add_para(tf, [(text, True, DARK)], size=27, after=0, first=True)
    # 强调线
    bar = slide.shapes.add_shape(1, Inches(0.62), Inches(1.02), Inches(2.6), Inches(0.07))
    bar.fill.solid(); bar.fill.fore_color.rgb = RGBColor.from_string(accent)
    bar.line.fill.background()
    bar.shadow.inherit = False
    if sub:
        _, tf2 = add_textbox(slide, 0.59, 1.12, 12.0, 0.4)
        add_para(tf2, [(sub, False, GRAY)], size=13, after=0, first=True)

def add_bullets(slide, x, y, w, h, items, size=15):
    """items: list of dict(type, segs/text, before)"""
    _, tf = add_textbox(slide, x, y, w, h)
    first = True
    for it in items:
        t = it.get('type', 'b')
        text = it.get('text')
        before = it.get('before', 0)
        if t == 'h':
            add_para(tf, [(text, True, BLUE)], size=size+1, before=before, after=4, first=first)
        elif t == 'b':
            segs = [("•  ", True, DARK)] + (text if isinstance(text, list) else [(text, False, BODY)])
            add_para(tf, segs, size=size, before=before, after=4, first=first)
        elif t == 's':
            segs = [("   –  ", False, GRAY)] + (text if isinstance(text, list) else [(text, False, BODY)])
            add_para(tf, segs, size=size-1, before=before, after=3, first=first)
        elif t == 'p':
            add_para(tf, text if isinstance(text, list) else [(text, False, BODY)], size=size, before=before, after=4, first=first)
        first = False

def set_cell(cell, text, size=12, bold=False, color=BODY, fill=None, align=PP_ALIGN.LEFT):
    cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.06)
    cell.margin_top = Inches(0.03); cell.margin_bottom = Inches(0.03)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill:
        cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor.from_string(fill)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run(); r.text = text
    fmt_run(r, size, bold, color)

def make_table(slide, x, y, w, col_widths, data, header_fill=ACC_DESIGN, size=12,
               first_col_left=True):
    rows, cols = len(data), len(data[0])
    gf = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(0.4*rows))
    table = gf.table
    for i, cw in enumerate(col_widths):
        table.columns[i].width = Inches(cw)
    for ri, row in enumerate(data):
        table.rows[ri].height = Inches(0.34)
        for ci, val in enumerate(row):
            cell = table.cell(ri, ci)
            if ri == 0:
                set_cell(cell, val, size, True, "FFFFFF", header_fill,
                         PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT)
            else:
                fill = LIGHT_FILL if ri % 2 == 0 else None
                al = PP_ALIGN.LEFT if (ci == 0 and first_col_left) else PP_ALIGN.CENTER
                set_cell(cell, val, size, False, BODY, fill, al)
    return table

def add_banner(slide, x, y, w, h, text, fill, size=15, color="FFFFFF"):
    box = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = RGBColor.from_string(fill)
    box.line.fill.background(); box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.04); tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    fmt_run(r, size, True, color)

# ======================================================================
prs = Presentation(SRC)
blank = None
for lay in prs.slide_layouts:
    if lay.name == "空白":
        blank = lay
        break
if blank is None:
    blank = prs.slide_layouts[6]

slides = list(prs.slides)
n_orig = len(slides)

# ---------- 新增内容页 A：设计定位与需求 ----------
sA = prs.slides.add_slide(blank)
add_title(sA, "01 结构设计 · 设计定位与需求", ACC_DESIGN)
add_bullets(sA, 0.6, 1.35, 7.6, 5.5, [
    dict(type='h', text='设计定位', before=2),
    dict(type='b', text=[("一根 13 m 碳纤维刚性梯形机翼 + 中央承力盒/龙骨 + 乘员俯卧挂载 + 后置折叠电推进 + 重心移动操纵 + 双腿起降", False, BODY), (" 的「无尾飞翼式单人动力滑翔机」。", False, BODY)]),
    dict(type='b', text=[("核心任务：低空个人运动/娱乐飞行 + 热气流翱翔（≤300 m AGL，翱翔可达 ~1000 m）。", False, BODY)]),
    dict(type='h', text='「人机合一」三原则', before=8),
    dict(type='b', text="人体不是乘客，而是结构—传力—操纵链中的一环；"),
    dict(type='b', text="结构既承受气动载荷，又沿明确路径把载荷传到人体；"),
    dict(type='b', text="人体质量参与重心控制（weight-shift 操纵），双腿即起落装置。"),
    dict(type='h', text='任务剖面', before=8),
    dict(type='b', text="助跑起飞(电推进辅助) → 爬升/热气流盘旋 → 巡航/翱翔(50–58 km/h) → 滑翔 flare → 双脚软着陆。"),
], size=14)
add_bullets(slide=sA, x=8.5, y=1.35, w=4.3, h=5.5, items=[
    dict(type='h', text='第一性原理硬约束'),
    dict(type='b', text=[("低失速 → 低翼载：", True, BLUE), ("V_stall=√(2W/(ρ·S·CLmax))，双脚软着陆需 8–9 m/s", False, BODY)]),
    dict(type='b', text=[("高升阻比 → 高展弦比：", True, BLUE), ("诱导阻力 ∝ 1/AR", False, BODY)]),
    dict(type='b', text=[("能量密度 → 续航：", True, BLUE), ("3 kWh 锂电 ≈ 14 kg", False, BODY)]),
    dict(type='b', text=[("人体功率 ~300 W ≪ 平飞 ~1.2 kW：", True, BLUE), ("必须有外部能量源", False, BODY)]),
    dict(type='b', text=[("固定翼 vs 扑翼：", True, BLUE), ("固定翼在功率/可靠性/操纵性全面胜出", False, BODY)]),
], size=13)

# ---------- 新增内容页 B：总体参数 ----------
sB = prs.slides.add_slide(blank)
add_title(sB, "01 结构设计 · 总体参数与翼面", ACC_DESIGN)
make_table(sB, 0.6, 1.4, 5.6, [2.6, 3.0], [
    ["质量预算", "质量"],
    ["空机（主结构30+挂架7+电推进6+电池14+操纵2+杂项1）", "60 kg"],
    ["名义乘员（范围 55–95）", "75 kg"],
    ["名义起飞质量", "135 kg"],
    ["最大乘员 / MTOW", "95 / 155 kg"],
], ACC_DESIGN, 11)
make_table(sB, 6.6, 1.4, 5.9, [2.6, 3.3], [
    ["翼面参数", "数值"],
    ["机翼面积 S", "20 m²"],
    ["翼展 b / 展弦比 AR", "13 m / 8.45"],
    ["锥度比 λ / 根弦·梢弦", "0.5 / 2.05·1.03 m"],
    ["平均气动弦长 MAC", "1.60 m"],
    ["翼载 名义/最大 W/S", "66.2 / 76.1 N/m²"],
    ["CLmax / (L/D)max", "1.5 / ≈15"],
], ACC_DESIGN, 11)
add_bullets(sB, 0.6, 4.45, 12.1, 2.6, [
    dict(type='h', text='设计要点'),
    dict(type='b', text=[("失速反推：", True, BLUE), ("S = 2W_max/(ρ·CLmax·V_stall²) = 3042/148.8 ≈ 20.4 → 取 20 m²", False, BODY)]),
    dict(type='b', text=[("速度包线：", True, BLUE), ("失速 31–33 · 巡航 48–56 · V_NE 90 · V_D 100 km/h", False, BODY)]),
    dict(type='b', text=[("材料体系：", True, BLUE), ("CFRP 主梁/蒙皮 · 7075-T6 挂架/接头 · 芳纶挂带 · Nomex/PMI 夹芯", False, BODY)]),
], size=14)

# ---------- 新增内容页 C：翼型与升力分布 ----------
sC = prs.slides.add_slide(blank)
add_title(sC, "01 结构设计 · 翼型选择与翼根内力", ACC_DESIGN)
add_bullets(sC, 0.6, 1.35, 6.6, 3.6, [
    dict(type='h', text='翼型方案'),
    dict(type='b', text=[("主翼 Wortmann FX 63-137", True, BLUE), ("（t/c 13.7%，根处厚 0.28 m 容纳 200 mm 主梁）", False, BODY)]),
    dict(type='b', text=[("翼尖 E387 过渡 + −2° 洗流", True, BLUE), ("（延迟翼尖失速，等效 CLmax≈1.5）", False, BODY)]),
    dict(type='b', text=[("Re ≈ 1–2.7×10⁶", True, BLUE), (" 低雷诺数段，高 CLmax、大结构深度、L/D 好", False, BODY)]),
    dict(type='b', text=[("升力线斜率 CLα = 4.92 rad⁻¹", True, BLUE), ("（0.0858 /°）", False, BODY)]),
], size=14)
make_table(sC, 7.5, 1.35, 5.0, [1.6, 1.6, 1.8], [
    ["工况(单侧)", "V_root", "M_root"],
    ["限制 +4g", "3.04 kN", "8.59 kN·m"],
    ["极限 +6g", "4.56 kN", "12.88 kN·m"],
    ["极限 −3g", "−2.28 kN", "−6.44 kN·m"],
], ACC_DESIGN, 11)
add_bullets(sC, 0.6, 5.15, 12.1, 1.9, [
    dict(type='h', text='升力分布与阵风校核'),
    dict(type='b', text=[("Schrenk 升力分布", True, BLUE), ("（椭圆 + 平面弦长平均），升力合力位于 43.4% 半翼展；", False, BODY), ("翼根极限 M=12.88 kN·m 为主梁主导工况。", False, BODY)]),
    dict(type='b', text=[("阵风支配工况：", True, BLUE), ("9 m/s @ V_D 未缓和 Δn≈+9.9g → 计入缓和因子 K_g=0.205 后 n≈3g < +6g → 主梁仍按机动极限设计，运行包线须限速。", False, BODY)]),
], size=13)

# ---------- 新增内容页 D：翼面结构 ----------
sD = prs.slides.add_slide(blank)
add_title(sD, "01 结构设计 · 翼面结构（主梁/翼肋/蒙皮/翼根）", ACC_DESIGN)
add_bullets(sD, 0.6, 1.35, 6.6, 3.4, [
    dict(type='h', text='主梁与腹板'),
    dict(type='b', text=[("主梁：CFRP 盒型梁 @30% 弦", True, BLUE), ("，根部缘条形心距 d=200 mm", False, BODY)]),
    dict(type='b', text=[("缘条：单向 CFRP 定宽 20 mm", True, BLUE), ("，厚度沿展向台阶递减 8→6→4→2 mm（上下面等强，兼顾 −3g）", False, BODY)]),
    dict(type='b', text=[("腹板：双侧 ±45° CFRP 织物 + 3 mm PMI 夹芯", True, BLUE), ("（总厚 ~3.5 mm），防剪切屈曲", False, BODY)]),
], size=14)
add_bullets(sD, 7.5, 1.35, 5.2, 3.4, [
    dict(type='h', text='翼肋 / 蒙皮 / 连接'),
    dict(type='b', text=[("翼肋：泡沫夹芯 @0.45 m，14 肋/侧", True, BLUE), ("（根肋 ~274 N 限制 / 412 N 极限）", False, BODY)]),
    dict(type='b', text=[("D-box：±45° CFRP + 5 mm Nomex 夹芯", True, BLUE), ("（主抗扭闭室，抗颤振）", False, BODY)]),
    dict(type='b', text=[("翼根连接：中央承力盒 + 7075-T6 铰耳/销", True, BLUE), ("，折叠铰点 y=±0.8 m → 单段 5.7 m", False, BODY)]),
], size=14)
make_table(sD, 0.6, 4.9, 9.0, [1.6, 1.6, 1.9, 1.9, 2.0], [
    ["y (m)", "0.00", "0.65", "1.63", "3.25", "4.88"],
    ["梁高 d (mm)", "200", "190", "175", "150", "125"],
    ["极限弯矩 (N·m)", "12881", "10107", "6647", "2630", "551"],
    ["缘条厚 t (mm)", "8.0", "6.7", "4.8", "2.2", "0.6"],
], ACC_DESIGN, 11)

# ---------- 新增内容页 E：中央承力框架与人体传力 ----------
sE = prs.slides.add_slide(blank)
add_title(sE, "01 结构设计 · 中央承力框架与人体传力路径", ACC_DESIGN)
add_banner(sE, 0.6, 1.25, 12.1, 0.75,
    "气动升力 → 蒙皮剪流 → 翼肋 → 主梁(弯矩/剪力) → 中央承力盒 → 龙骨 → 挂点 → 芳纶吊带 → 躯干托板 → 人体 → 重力(惯性反力)  闭合传力环",
    DARK, 14)
make_table(sE, 0.6, 2.25, 6.4, [1.5, 4.9], [
    ["部件", "形式 / 功能"],
    ["中央承力盒", "CFRP 盒型梁 1.6 m，汇合两侧翼根弯矩 12.9 kN·m"],
    ["龙骨", "铝 7075-T6 纵向梁 1.8 m，挂点/电池/pylon 载体"],
    ["挂点/吊带", "可调挂耳 + 芳纶织带，兼作重心移动操纵机构"],
    ["螺旋桨塔", "后置管架，5 kW 电机 + 折叠桨，推力传入龙骨"],
], ACC_DESIGN, 11)
make_table(sE, 7.4, 2.25, 5.3, [1.9, 1.7, 1.7], [
    ["支撑形式", "+1g", "+4g"],
    ["仅胸带+骨盆带(0.055 m²)", "16.9 kPa", "67.8 kPa ✕"],
    ["躯干托板(0.25 m²)", "3.7 kPa", "14.9 kPa ✓"],
], ACC_DESIGN, 11)
add_bullets(sE, 0.6, 4.9, 12.1, 2.0, [
    dict(type='b', text=[("接触压力结论：", True, BLUE), ("必须用大面积躯干托板（胸板+骨盆板+大腿），+4g 时 14.9 kPa < 20–30 kPa 短时限值；窄带方案 67.8 kPa 不可接受。", False, BODY)]),
    dict(type='b', text=[("挂点极限载荷：", True, BLUE), ("+6g → 5.6 kN；中央承力盒是气动载荷、人体反力、螺旋桨推力、起降冲击四类载荷的汇合枢纽。", False, BODY)]),
], size=13)

# ---------- 新增内容页 F：总结思考 ----------
sF = prs.slides.add_slide(blank)
add_title(sF, "03 总结思考 · 关键结论与设计边界", ACC_SUM)
add_bullets(sF, 0.6, 1.35, 6.9, 5.4, [
    dict(type='h', text='关键结论'),
    dict(type='b', text=[("低失速(8–9 m/s 双脚软着陆) ", True, BLUE), ("强制出大翼面积 20 m²、低翼载 ~66–76 N/m²、高展弦比 8.45；", False, BODY)]),
    dict(type='b', text=[("主梁按 +4g/+6g 机动极限设计", True, BLUE), ("（翼根 M=12.9 kN·m），阵风缓和后 n≈3g 不超机动极限，运行包线须限速；", False, BODY)]),
    dict(type='b', text=[("人体必须用大面积躯干托板", True, BLUE), ("（非窄带），+4g 接触压力 14.9 kPa 才满足生物力学限值；", False, BODY)]),
    dict(type='b', text=[("中央承力盒", True, BLUE), ("是气动载荷、人体反力、螺旋桨推力、起降冲击四类载荷的汇合枢纽。", False, BODY)]),
], size=14)
add_bullets(sF, 7.8, 1.35, 4.9, 5.4, [
    dict(type='h', text='方法边界（诚实声明）'),
    dict(type='b', text=[("气动：", True, BLUE), ("Prandtl 升力线 + 薄翼理论（势流），非 RANS——无粘性分离/失速细节", False, BODY)]),
    dict(type='b', text=[("结构：", True, BLUE), ("盒型梁理论（σ=Mz/I、τ=V/(2dt)），非三维壳 FEA——无应力集中/屈曲/接头细节", False, BODY)]),
    dict(type='b', text=[("云图：", True, BLUE), ("解析场映射着色；本机无 CFD/FEA 求解器", False, BODY)]),
    dict(type='b', text=[("下一步：", True, BLUE), ("STL 导入 STAR-CCM+/Abaqus 复核", False, BODY)]),
], size=13)

new_slides = [sA, sB, sC, sD, sE, sF]

# ---------- 重排：把新增内容页插入正确位置 ----------
# 原始顺序: 0 标题 1 目录 2 结构设计(节) 3 网格 4 应力 5 气动极曲线 6 压力云图 7 导航 8 结束
# 目标顺序: [0,1,2, A,B,C,D,E, 3,4,5,6, 7, F, 8]
sldIdLst = prs.slides._sldIdLst
sldIds = list(sldIdLst)
for s in sldIds:
    sldIdLst.remove(s)
order = [0, 1, 2, 9, 10, 11, 12, 13, 3, 4, 5, 6, 7, 14, 8]
for idx in order:
    sldIdLst.append(sldIds[idx])

# ---------- 逐页讲稿（演讲者备注） ----------
NOTES = {
    0: "开场：各位老师好，我们第十二小组汇报的是「飞行器结构设计」大作业——一型「人机合一」低空个人飞行器，一台无尾飞翼式单人动力滑翔机。下面从结构设计、仿真分析、总结思考三部分汇报。",
    1: "目录：第一部分讲结构设计（需求、总体参数、翼型、翼面结构、中央承力框架），第二部分讲仿真分析（网格、应力、气动），第三部分是总结与边界。",
    2: "进入第一部分——结构设计。我们的核心定位一句话：一根 13 米碳纤维刚性梯形机翼 + 中央承力盒/龙骨 + 乘员俯卧挂载 + 后置折叠电推进 + 重心移动操纵 + 双腿起降。",
    # A
    9: "设计定位：低空个人运动/娱乐飞行 + 热气流翱翔。「人机合一」三原则是：人体不是乘客而是结构—传力—操纵链的一环；结构沿明确路径把气动载荷传到人体；人体质量参与重心控制、双腿即起落架。第一性原理给出的硬约束：低失速→低翼载，高升阻比→高展弦比，能量密度决定续航；人体功率约300瓦远小于平飞所需约1.2千瓦，所以必须有外部能量源。任务剖面：助跑起飞、爬升/热气流盘旋、巡航/翱翔、滑翔flare双脚软着陆。",
    # B
    10: "总体参数：空机60公斤、名义乘员75公斤，名义起飞135公斤、最大155公斤。机翼面积20平方米由失速约束反推（双脚软着陆需要失速8–9米/秒），翼展13米、展弦比8.45、锥度比0.5、MAC 1.60米，翼载66–76牛/平方米。速度包线：失速31–33、巡航48–56、极限90公里/小时。材料以碳纤维主梁蒙皮为主，7075-T6挂架、芳纶挂带、Nomex/PMI夹芯。",
    # C
    11: "翼型：主翼选用Wortmann FX 63-137，13.7%厚度在根弦2.05米下给出0.28米最大厚度，正好容纳200毫米主梁；翼尖向E387过渡并施加−2°洗流以延迟翼尖失速。升力分布用Schrenk近似（椭圆与平面弦长平均）。翼根极限内力：+6g时单侧剪力4.56千牛、弯矩12.88千牛·米。阵风是支配工况：9米/秒阵风在V_D下未缓和约10g，缓和因子0.205后降到3g，所以主梁仍按机动极限设计、运行包线限速。",
    # D
    12: "翼面结构：主梁为碳纤维盒型梁，位于30%弦，根部缘条形心距200毫米；缘条单向碳纤维定宽20毫米、厚度沿展向8→6→4→2毫米台阶递减。腹板用±45°织物加3毫米PMI泡沫夹芯防剪切屈曲。翼肋泡沫夹芯间距0.45米、每侧14肋。前缘D-box用±45°碳纤维加5毫米Nomex夹芯，是主抗扭闭室、抗颤振关键。翼根用中央承力盒加7075-T6铰耳销折叠，铰点y=±0.8米，折叠后单段5.7米。",
    # E
    13: "中央承力框架：中央承力盒贯穿翼根1.6米，是两侧翼根弯矩的汇合枢纽；龙骨纵向1.8米承载挂点、电池、螺旋桨塔。传力路径：气动升力→蒙皮→翼肋→主梁→承力盒→龙骨→挂点→芳纶吊带→躯干托板→人体→重力闭合。关键是接触压力：窄带方案+4g达67.8千帕不可接受，大面积躯干托板把压力降到14.9千帕，满足生物力学限值——这是把人体安全纳入结构链的先决条件。",
    # 网格
    3: "网格划分：几何分RevN（结构翼盒）和RevP（完整外形）两版，都采用18毫米全局、3.6毫米最小尺寸、Frontal-Delaunay算法。RevN约36万三角面用于结构，RevP约130万三角面补齐前缘与后缘蒙皮用于气动。",
    # 应力
    4: "应力分析：在+6g极限载荷下用盒型梁模型计算。翼根弯矩11.33千牛·米，较设计值12.88低12%；缘条最大应力364兆帕、许用400兆帕，安全裕度0.10；腹板剪应力仅3.3兆帕；翼尖挠度0.41米，约为半展长的6.3%。结构满足强度与刚度要求。",
    # 气动极曲线
    5: "气动仿真：用Prandtl升力线方法得到极曲线。升力线斜率0.0876每度，最大升阻比22.8对应CL=0.60；巡航点（135公斤、15米/秒）CL=0.48、迎角0.15°、升阻比约22.7、下沉率0.66米/秒。展向载荷与Schrenk近似吻合。",
    # 压力云图
    6: "表面压力云图：把升力线解析场映射到网格着色，展示上下表面Cp分布，上表面负压区对应主要升力来源。注意这是势流解析场映射，不是RANS结果。",
    # 导航
    7: "以上是仿真分析部分。下面进入第三部分——总结思考。",
    # F
    14: "总结：四个关键结论——低失速强制出大翼面积与高展弦比；主梁按机动极限设计、阵风缓和后不超限；人体必须用大面积躯干托板控制接触压力；中央承力盒是四类载荷汇合枢纽。同时诚实声明方法边界：气动是升力线势流非RANS，结构是盒型梁理论非三维壳FEA，后续可用STAR-CCM+/Abaqus复核。",
    # 结束
    8: "以上就是我们的汇报，恳请各位老师批评指正。分工：建模与统筹孙一凡、结构分析冯异、气动/有限元张文博、总结报告翁丁恺。本作业使用Claude辅助设计分析与文档草拟，结论经人工复核，由本组负责。谢谢！",
}

def set_notes(slide, text):
    """可靠地写入演讲者备注（兼容缺失 body 占位符的备注页）。"""
    ns = slide.notes_slide
    tf = ns.notes_text_frame
    if tf is not None:
        tf.text = text
        return
    # 备注页缺 body 占位符：手动补一个（结构与自动创建的一致）
    notes_el = ns._element
    cSld = notes_el.find(qn('p:cSld'))
    spTree = cSld.find(qn('p:spTree'))
    sp = notes_el.makeelement(qn('p:sp'), {})
    nvSpPr = etree.SubElement(sp, qn('p:nvSpPr'))
    cNvPr = etree.SubElement(nvSpPr, qn('p:cNvPr'))
    cNvPr.set('id', '3'); cNvPr.set('name', 'Notes Placeholder 2')
    cNvSpPr = etree.SubElement(nvSpPr, qn('p:cNvSpPr'))
    spLocks = etree.SubElement(cNvSpPr, qn('a:spLocks')); spLocks.set('noGrp', '1')
    nvPr = etree.SubElement(nvSpPr, qn('p:nvPr'))
    ph = etree.SubElement(nvPr, qn('p:ph'))
    ph.set('type', 'body'); ph.set('idx', '3'); ph.set('sz', 'quarter')
    etree.SubElement(sp, qn('p:spPr'))
    txBody = etree.SubElement(sp, qn('p:txBody'))
    etree.SubElement(txBody, qn('a:bodyPr'))
    etree.SubElement(txBody, qn('a:lstStyle'))
    a_p = etree.SubElement(txBody, qn('a:p'))
    a_r = etree.SubElement(a_p, qn('a:r'))
    a_t = etree.SubElement(a_r, qn('a:t')); a_t.text = text
    spTree.append(sp)

# 按「幻灯片对象」绑定讲稿（备注随 slide part 走，与重排顺序无关）
note_pairs = []
for i, s in enumerate(slides):          # slides = 原始 0..8
    note_pairs.append((s, NOTES.get(i, "")))
for j, s in enumerate(new_slides):      # 新增 A..F = 索引 9..14
    note_pairs.append((s, NOTES.get(9 + j, "")))

for slide, text in note_pairs:
    set_notes(slide, text)

shutil.copyfile(SRC, BAK)
prs.save(OUT)
print(f"完成：新增 {len(new_slides)} 页内容页，总计 {len(prs.slides)} 页。")
print(f"输出：{OUT}")
print(f"原文件已备份为：{BAK}")
