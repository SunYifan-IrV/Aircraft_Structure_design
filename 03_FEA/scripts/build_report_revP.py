"""Build the RevP report (mesh + aero + Cp contours + strength)."""
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "RevP_机翼网格气动与强度分析报告.docx")

ll = json.load(open(os.path.join(RES, "ll_summary.json")))
st = json.load(open(os.path.join(RES, "strength_summary.json")))

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.8)

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
style.paragraph_format.line_spacing = 1.35
style.paragraph_format.space_after = Pt(4)

def set_font(run, cn="宋体", en="Times New Roman", size=10.5, bold=None, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def H(text, level=1):
    p = doc.add_heading(level=level)
    r = p.add_run(text)
    set_font(r, "微软雅黑", "Arial", {1: 15, 2: 12.5, 3: 11}[level], True, (0x1F, 0x3A, 0x5F))
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(5)

def P(text, size=10.5, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74) if indent else Cm(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    set_font(r, size=size)

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    set_font(p.add_run(text), size=10.5)

def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    set_font(p.add_run(text), size=9, color=(0x55, 0x55, 0x55))

def table(rows, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or j > 0) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            set_font(p.add_run(str(val)), size=9.5, bold=(i == 0))
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)

def figure(path, width=16.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(path, width=Cm(width))

# cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(50)
set_font(p.add_run("PersonalAircraft RevP 机翼"), "微软雅黑", "Arial", 22, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("网格 · 气动云图 · 强度初步分析"), "微软雅黑", "Arial", 18, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("输入：PersonalAircraft_Structural_RevP.stp（CATIA V5R21, AP203, 完整外模线）"), size=9.5, color=(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("2026-11-01"), size=9.5, color=(0x66, 0x66, 0x66))

H("1  结论摘要")
P("RevP 的 STEP 已包含完整机翼外模线（前缘到后缘弦向 0–100%），因此可以同时用于结构网格与气动分析。"
  "本报告给出：(1) 整机表面网格；(2) 升力线气动特性与表面 Cp 彩色云图；"
  "(3) 6g 工况主梁强度与刚度初检。")
table([
    ["项目", "结果", "说明"],
    ["STEP 实体 / 曲面", "192 / 4 512", "闭合实体；mm"],
    ["表面网格", "652 646 节点 / 1 303 300 三角面", "h = 18 mm，STL 62 MB"],
    ["弦向覆盖", "0 – 100%", "前缘、后缘蒙皮齐全（RevN 缺此部分）"],
    ["升力线斜率 CLα", "0.0876 /°（5.02 /rad）", "AR = 8.45"],
    ["零迎角升力", "0.53", "6% 弯度 + 2° 翼尖洗出"],
    ["最大升阻比", "22.8 @ CL = 0.60", "CD0 = 0.0125，V = 15 m/s"],
    ["巡航", "CL = 0.48，α = 0.15°", "135 kg, 15 m/s, Re = 1.64×10⁶"],
    ["翼根弯矩（6g）", "11.33 kN·m", "设计值 12.88，偏差 −12%"],
    ["缘条压应力（6g）", "364 MPa / 许用 400", "MS = 0.099"],
    ["翼尖挠度（6g）", "0.41 m（6.3% 半展长）", "需关注气动弹性"],
], widths=[4.0, 6.4, 7.0])
caption("表 1  主要结果")

H("2  模型与网格")
P("RevP 的 STEP 为 192 个闭合实体、4 512 张曲面，包围盒 2 565 × 13 051 × 938 mm，"
  "弦向切片显示 y = 3 250 mm 处几何覆盖 x = 124～1 684 mm（约 0～100% 弦长），即前缘 D-box 与后缘蒙皮已补齐，"
  "这正是 RevN 缺失、导致无法直接做 CFD 的部分。")
P("用 gmsh 4.15.2（OCC 内核）按 18 mm 全局尺寸划分三角形表面网格：652 646 个节点、1 303 300 个三角面，"
  "导出二进制 STL（62 MB）与 gmsh 2.2 格式 msh，可直接导入 STAR-CCM+ / Fluent / OpenFOAM 做进一步处理。")
table([
    ["参数", "取值"],
    ["全局 / 最小尺寸", "18 mm / 3.6 mm"],
    ["算法", "Frontal-Delaunay"],
    ["节点 / 三角面", "652 646 / 1 303 300"],
    ["输出", "revP_surface.stl（62 MB）、revP_surface.msh"],
], widths=[6.0, 11.0])
caption("表 2  网格参数")

H("3  气动分析")
H("3.1  方法", 2)
P("展向用 Prandtl 升力线（Glauert 30 阶谐波），剖面用薄翼理论 cl = 2π(α_eff − α_L0)，"
  "根段 FX 63-137 取 α_L0 = −6°，翼尖 E387 取 −2.5°，几何扭转由 CAD 前后缘高度差算出（翼尖 −2° 洗出）。"
  "表面压力系数按下式合成：")
P("Cp(x) = 1 − (1 ± γ/2V)²，其中 γ(θ)/2V = A0(1+cosθ)/sinθ + A1 sinθ 为薄翼载荷分布，"
  "A0、A1 由当地有效迎角与升力系数确定。该式给出前缘吸力峰、弦向恢复与展向卸载的正确趋势，"
  "但它仍是势流估算，不含粘性、分离与压缩性——**不是 RANS 结果**。", indent=False)

H("3.2  极曲线与展向载荷", 2)
figure(os.path.join(FIG, "fig_polar.png"), 16.0)
caption("图 1  CL(α) 与 L/D(α)，V = 15 m/s")
figure(os.path.join(FIG, "fig_spanload.png"), 14.5)
caption("图 2  4g 限制载荷下的展向升力分布与 Schrenk 对比（归一化到同一总升力）")
P(f"升力线斜率 {ll['CLalpha_per_deg']:.4f} /deg；零迎角 CL = 0.53；最大升阻比 {ll['LDmax']:.1f}"
  f"（CL = {ll['CL_at_LDmax']:.2f}，α = {ll['alpha_LDmax']:.1f}°）。135 kg、15 m/s 巡航对应 CL = 0.48、"
  f"α = {ll['alpha_cruise']:.2f}°，L/D ≈ 22.7，下沉率约 0.66 m/s。")
P("与 Schrenk 近似相比，本文分布内翼略高、翼尖明显偏低——CAD 中翼尖的 −2° 洗出把载荷向内翼转移，"
  "使翼根弯矩比设计值低约 12%。这对结构偏安全，但会使翼尖失速特性与设计假设不同，"
  "建议在气动设计中把洗出量与实际载荷分布一起复核。")

H("3.3  表面压力云图", 2)
P("图 3–5 为 α = 4°（CL = 0.88）工况下的表面 Cp 彩色云图。上表面前缘形成强吸力区（深蓝，Cp 低至 −3 以下被色标截断），"
  "沿弦向迅速恢复；下表面整体为正压（红/黄），前缘附近出现驻点高压。翼尖因洗出与三维卸载，吸力明显减弱，"
  "这与图 2 的展向载荷一致。")
figure(os.path.join(FIG, "cp_iso.png"), 16.0)
caption("图 3  机翼 Cp 云图（等轴测，上表面为主）  α = 4°，V = 15 m/s")
figure(os.path.join(FIG, "cp_top.png"), 16.0)
caption("图 4  上表面 Cp 云图（俯视）")
figure(os.path.join(FIG, "cp_bottom.png"), 16.0)
caption("图 5  下表面 Cp 云图（仰视）")
P("说明：云图基于上述势流模型逐三角形着色，颜色对应 Cp（蓝 = 吸力，红 = 压力）。"
  "由于薄翼载荷在驻点处奇异，前缘 1% 弦长内的 Cp 被截断在 −3，仅影响色标端点，不影响整体分布形态。", indent=False)

H("4  结构强度初检")
P("把 4g 展向载荷放大到 6g（MTOW 155 kg，总升力 9 123 N），按梁理论积分得到剪力与弯矩，"
  "缘条取设计表（宽 20 mm、根部厚 8 mm、梁高 200 mm、E = 120 GPa、压缩许用 400 MPa）。")
table([
    ["y (m)", "M (N·m)", "缘条应力 (MPa)", "MS", "挠度 (m)"],
    ["0.09", f"{st['M_root_6g']:.0f}", f"{st['sigma_root_MPa']:.0f}", f"{st['MS_root']:.3f}", f"{abs(st['tip_deflection_m']):.3f}"],
    ["1.63", "5 668", "333", "0.20", "0.20"],
    ["3.25", "1 915", "290", "0.38", "0.06"],
    ["4.88", "292", "195", "1.05", "0.01"],
], widths=[3.0, 3.2, 3.8, 2.6, 2.8])
caption("表 3  6g 工况主梁缘条强度与刚度")
figure(os.path.join(FIG, "strength.png"), 15.8)
caption("图 6  缘条应力与翼尖挠度沿展向分布（6g）")
P(f"翼根弯矩 {st['M_root_6g']/1000:.2f} kN·m，比设计值 12.88 kN·m 低 12%（洗出卸载翼尖所致）；"
  f"根部缘条应力 {st['sigma_root_MPa']:.0f} MPa，MS = {st['MS_root']:.3f}。由于缘条是按等强度设计的，"
  "根部应力最高，向内翼迅速下降（1.6 m 处 333 MPa、3.25 m 处 290 MPa），"
  "根部只剩约 10% 余量，材料分散性、缺陷或屈曲都可能吃掉它。")
P(f"6g 翼尖挠度 {abs(st['tip_deflection_m']):.2f} m（半展长的 {abs(st['tip_deflection_pct_span']):.1f}%）。"
  "对 13 m 柔性翼这已属显著，颤振/发散需用梁-板耦合或全机气弹模型专门校核。")

H("5  下一步")
bullet("CFD：本机没有可用的 RANS 求解器（ANSYS 仅 Motion、STAR-CCM+ 缺 starccm+.exe）。revP_surface.stl 可直接导入有许可证的 STAR-CCM+/Fluent，或装 blueCFD/OpenFOAM。")
bullet("FEA：抽翼盒中面，用壳单元 + 复合材料铺层建模，折叠接头按双剪耳片建模，补做蒙皮屈曲、胶接/螺栓、疲劳。")
bullet("气动：把洗出量、CLmax 与失速特性纳入设计迭代；当前 6% 弯度翼型在 Re = 1.6×10⁶ 下 L/D 仅 23，若目标是滑翔性能需重新选型。")

H("附录  文件清单")
table([
    ["文件", "内容"],
    ["mesh/revP_surface.stl / .msh", "RevP 整机表面网格（652 646 节点 / 1.30 M 面）"],
    ["mesh/wing_oml.stl", "重建的机翼气动外形（水密，6.5 k 面）"],
    ["figures/cp_top.png 等", "Cp 彩色云图（俯视 / 仰视 / 等轴测）"],
    ["results/ll_polar.csv", "极曲线数据"],
    ["results/strength.csv", "弯矩、应力、挠度沿展向"],
    ["scripts/10…11_*.py", "RevP 网格与云图脚本"],
], widths=[6.5, 10.5])
caption("表 4  交付文件")

doc.save(OUT)
print("saved", OUT)
