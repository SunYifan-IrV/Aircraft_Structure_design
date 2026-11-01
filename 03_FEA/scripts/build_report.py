"""Build the Word report for the RevN wing analysis."""
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "RevN_机翼网格与气动分析报告.docx")

ll = json.load(open(os.path.join(RES, "ll_summary.json")))
st = json.load(open(os.path.join(RES, "strength_summary.json")))

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(2.0))
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
    return p

def P(text, size=10.5, indent=True, bold=False):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74) if indent else Cm(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    set_font(r, size=size, bold=bold)
    return p

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_font(r, size=10.5)
    return p

def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_font(r, size=9, color=(0x55, 0x55, 0x55))

def table(rows, widths=None, header=True, fs=9.5):
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
            r = p.add_run(str(val))
            set_font(r, size=fs, bold=(i == 0 and header))
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    return t

def figure(path, width=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(path, width=Cm(width))

# ---------------------------------------------------------------- cover
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(60)
r = p.add_run("PersonalAircraft RevN 机翼结构")
set_font(r, "微软雅黑", "Arial", 22, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("网格划分与气动 / 强度初步分析报告")
set_font(r, "微软雅黑", "Arial", 18, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("输入：Copy_of_PersonalAircraft_Structural_RevN.stp（CATIA V5R21，AP203）")
set_font(r, size=10, color=(0x66, 0x66, 0x66))
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026-10-31")
set_font(r, size=10, color=(0x66, 0x66, 0x66))

# ---------------------------------------------------------------- 1 summary
H("1  结论摘要")
P("本报告对 RevN 的 CATIA 模型完成了三件事：(1) 把 STEP 转成可用于 CFD / 结构分析的表面网格；"
  "(2) 用翼型截面数据重建了完整气动外形，并做了全机翼的升力线与展向载荷分析；"
  "(3) 用分析得到的翼根弯矩对主梁缘条做了强度与刚度初检。主要结论如下：")
table([
    ["项目", "结果", "说明"],
    ["STEP 实体 / 曲面", "190 / 3 544", "闭合实体，无自由边；单位为 mm"],
    ["表面网格", "182 611 节点 / 364 202 三角面", "h = 18 mm，总面积 38.9 m²，STL 18.2 MB"],
    ["气动外形重建", "6 528 三角面，半翼体积 1.267 m³", "由 34 个 CAD 翼型截面放样，水密"],
    ["升力线斜率 CLα", "0.0876 /deg（5.02 /rad）", "AR = 8.45，与理论值 4.5～5.0 /rad 相符"],
    ["零迎角升力 CL(0)", "0.528", "由 6% 弯度与 −6° 零升迎角给出"],
    ["最大升阻比", "22.9 @ CL = 0.57（α ≈ 0°）", "CD0 = 0.0125（估算），V = 15 m/s"],
    ["巡航状态", "CL = 0.48，α = −0.55°", "135 kg，15 m/s，Re = 1.64×10⁶"],
    ["翼根弯矩（6g）", "12.40 kN·m", "设计值 12.88 kN·m，偏差 −3.7%"],
    ["缘条压应力（6g）", "398 MPa / 许用 400 MPa", "MS = 0.004，等强度设计恰好用满"],
    ["翼尖挠度（6g）", "0.572 m（8.8% 半展长）", "柔性偏大，需关注气动弹性"],
], widths=[4.2, 6.2, 7.0])
caption("表 1  主要结果汇总")

P("需要强调的是：本报告给出的是「工程快速分析」而不是「详细有限元 + RANS」。气动部分为升力线（势流）方法，"
  "不含粘性分离与失速；结构部分为梁理论初检，不含蒙皮屈曲、接头细节与疲劳。这些内容的实施路径在第 5 章给出。",
  bold=False)

# ---------------------------------------------------------------- 2 model
H("2  输入模型与网格")
H("2.1  STEP 模型体检", 2)
P("STEP 文件 5.74 MB，由 CATIA V5R21 以 AP203 导出，包含 190 个闭合实体（MANIFOLD_SOLID_BREP）、"
  "3 544 张曲面、9 496 条边，包围盒 2 565 × 13 000 × 862 mm（x 向后、y 向右、z 向上），与设计文档的"
  "13 m 翼展、2.05 m 根弦一致。")
P("对模型做切片检查后发现一个重要问题：在 y = 3 250 mm 处，几何只覆盖 x = 579～1 287 mm，"
  "即弦长的 38%～84%；y = 1 700 mm 处覆盖 29%～75%。也就是说，该 STEP 只有主梁到后梁之间的"
  "「后翼盒」结构，前缘 D-box 蒙皮与后缘蒙皮并不在文件中（它们很可能是 CATIA 中的曲面特征，导出 STEP 时未被带上）。"
  "因此这份 STEP 适合做结构分析，但不能直接当作气动外形使用。")
figure(os.path.join(FIG, "view_iso.png"), 15.0)
caption("图 1  STEP 表面网格（18 mm）——可见机翼只保留了翼盒段，缺少前缘与后缘蒙皮")

H("2.2  网格生成", 2)
P("网格用 gmsh 4.15.2（OCC 内核）生成：直接读入 STEP，按 18 mm 全局尺寸划分三角形表面网格，"
  "共 182 611 个节点、364 202 个三角面，网格总面积 38.9 m²。导出二进制 STL 与 gmsh 2.2 格式 msh 各一份。")
table([
    ["参数", "取值"],
    ["全局尺寸 / 最小尺寸", "18 mm / 3.6 mm"],
    ["算法", "Frontal-Delaunay（Mesh.Algorithm = 1）"],
    ["节点 / 三角面", "182 611 / 364 202"],
    ["网格总面积", "38.9 m²"],
    ["输出", "aircraft_surface_bin.stl（18.2 MB）、aircraft_surface.msh"],
], widths=[6.0, 10.0])
caption("表 2  表面网格参数")

# ---------------------------------------------------------------- 3 aero
H("3  气动分析")
H("3.1  为什么不用 STEP 直接算", 2)
P("如 2.1 所述，STEP 缺少前缘与后缘蒙皮，直接拿它做 CFD 会把翼盒当成「开缝的平板」，"
  "得到完全错误的压力分布。因此本文用 _wing_skin_sections.csv 中的 34 个翼型截面（FX 63-137 过渡到 E387，"
  "含 3° 上反与翼尖 −2° 洗出）重新放样出完整机翼外形，生成 wing_oml.stl（6 528 面，水密，半翼体积 1.267 m³），"
  "作为后续 CFD 的计算外形。")
figure(os.path.join(FIG, "wing_oml_iso.png"), 15.0)
caption("图 2  由 CAD 截面重建的机翼气动外形（wing_oml.stl）")

H("3.2  计算方法", 2)
P("采用 Prandtl 升力线理论，Glauert 傅里叶级数展开（30 阶谐波、30 个配置点，全展向）。"
  "剖面特性取薄翼理论 cl = 2π(α_eff − α_L0)：根段 FX 63-137 取 α_L0 = −6°，翼尖 E387 取 −2.5°，"
  "在 y = 4.5～6.5 m 之间线性过渡；几何扭转由 CAD 截面的前后缘高度差直接算出（翼尖约 −2°）。"
  "诱导下洗由尾涡系积分得到，镜像半翼计入对称性。")
P("粘性阻力无法由势流给出，用平板摩擦 + 厚度形状因子估算：Re = 1.64×10⁶ 时 Cf = 0.00423，"
  "取 t/c = 11.5%、形状因子 1.29，并加 0.002 的干扰/粗糙度余量，得 CD0 ≈ 0.0125。")

H("3.3  结果", 2)
figure(os.path.join(FIG, "fig_polar.png"), 15.8)
caption("图 3  CL(α) 与 L/D(α)，V = 15 m/s")
figure(os.path.join(FIG, "fig_drag.png"), 9.5)
caption("图 4  阻力极曲线 CL–CD")

table([
    ["α (°)", "CL", "CDi", "CD", "L/D"],
    ["−4", "0.178", "0.0012", "0.0137", "13.0"],
    ["0", "0.528", "0.0106", "0.0231", "22.9"],
    ["4", "0.879", "0.0294", "0.0419", "21.0"],
    ["8", "1.229", "0.0576", "0.0701", "17.5"],
], widths=[2.6, 2.8, 2.8, 2.8, 2.8])
caption("表 3  气动系数（V = 15 m/s；α ≥ 6° 已超出线性段，仅作趋势参考）")

P(f"升力线斜率为 {ll['CLalpha_per_deg']:.4f} /deg（{ll['CLalpha_per_deg']*57.3:.2f} /rad），"
  f"零迎角升力 0.528，最大升阻比 {ll['LDmax']:.1f}（CL = {ll['CL_at_LDmax']:.2f}）。"
  "按 135 kg、15 m/s 巡航，所需 CL = 0.48，对应迎角 −0.55°，L/D ≈ 22.9；"
  "滑翔比约 23，下沉率约 0.66 m/s（15/22.9）。这一量级对 13 m 展弦比 8.45 的滑翔机是合理的，"
  "但明显低于现代复合材料滑翔机（L/D 35～45），主要受 CD0 与 6% 弯度的高阻翼型限制。")

H("3.4  展向载荷", 2)
figure(os.path.join(FIG, "fig_spanload.png"), 14.5)
caption("图 5  4g 限制载荷下的展向升力分布与 Schrenk 近似对比（均归一化到同一总升力）")
P("本文分布与设计文档的 Schrenk 近似整体吻合，内翼段略高、翼尖段略低——这是 CAD 中翼尖 −2° 洗出"
  "卸载翼尖的直接结果。该差异使翼根弯矩比 Schrenk 估算低约 4%，对结构是偏安全的。")

# ---------------------------------------------------------------- 4 strength
H("4  结构强度初检")
P("把 3.4 的展向载荷放大到 6g（MTOW 155 kg，总升力 9 123 N），用梁理论沿展向积分得到剪力与弯矩，"
  "再按设计文档的缘条尺寸（宽 20 mm，根部厚 8 mm，梁高 200 mm，E = 120 GPa，压缩许用 400 MPa）计算应力与挠度。")
table([
    ["y (m)", "M (N·m)", "缘条应力 (MPa)", "MS", "挠度 (m)"],
    [f"{0.085:.2f}", f"{st['M_root_6g']:.0f}", f"{st['sigma_root_MPa']:.0f}", f"{st['MS_root']:.3f}", f"{abs(st['tip_deflection_m']):.3f}"],
    ["1.63", "6 600", "388", "0.03", "0.30"],
    ["3.25", "2 516", "381", "0.05", "0.10"],
    ["4.88", "467", "311", "0.28", "0.01"],
], widths=[3.0, 3.2, 3.6, 2.6, 2.8])
caption("表 4  6g 工况主梁缘条强度与刚度（梁理论）")
figure(os.path.join(FIG, "strength.png"), 15.2)
caption("图 6  缘条压应力与翼尖挠度沿展向分布（6g）")

P(f"翼根弯矩 {st['M_root_6g']/1000:.2f} kN·m，与设计值 12.88 kN·m 相差 −3.7%；"
  f"根部缘条应力 {st['sigma_root_MPa']:.0f} MPa，安全裕度 MS = {st['MS_root']:.3f}。"
  "由于缘条厚度本就是按「等强度」逐段递减设计的，内翼段（y < 4 m）应力都贴近 400 MPa 许用值，"
  "这意味着该设计没有额外余量：材料批次、缺陷、屈曲或接头偏心任何一项折减都会使 MS 变负。")
P(f"刚性问题更值得注意：6g 时翼尖挠度 {abs(st['tip_deflection_m']):.2f} m，为半展长的 "
  f"{abs(st['tip_deflection_pct_span']):.1f}%。对 13 m 柔性翼，这已经进入气动弹性显著影响的区间，"
  "设计文档中担心的颤振/发散问题需要用梁-板耦合或全机气弹模型进一步校核，而不能只看静强度。")

# ---------------------------------------------------------------- 5 next
H("5  下一步建议")
H("5.1  要得到可用于 CFD 的网格", 2)
P("本机没有可用的 CFD 求解器（ANSYS 仅装了 Motion，STAR-CCM+ 目录不完整，缺少 starccm+.exe），"
  "所以本次只交付了网格与快速气动结果。若要在本机跑 RANS，建议：")
bullet("装 OpenFOAM（Windows 用 blueCFD-Core）或可用的 STAR-CCM+ / Fluent 许可证；")
bullet("把 wing_oml.stl 作为壁面，外部流场域：上游 10c、下游 20c、侧向与高度各 10c（c = 1.6 m）；")
bullet("表面网格 25～40 mm，前缘 8～10 mm，附面层 20 层、增长率 1.2、首层 0.02 mm（y⁺ ≈ 1）；")
bullet("不可压、稳态、k-ω SST，入口速度 15 m/s，α 从 −2° 扫到 8°，监视升力/阻力系数。")

H("5.2  要做真正的有限元", 2)
P("本次的梁理论只覆盖主梁缘条的正应力。完整的复合材料翼盒分析还需要：")
bullet("把翼盒抽中面（蒙皮、腹板、肋），用壳单元 + 铺层（CFRP 0°/±45°、Nomex 夹芯）建模；")
bullet("在 y = ±0.8 m 折叠接头处施加真实边界（双剪耳片、Ø20 销），而不是简单固支；")
bullet("补做蒙皮/腹板屈曲、胶接与螺栓连接、疲劳（阵风谱）三项校核；")
bullet("用 Nastran / Abaqus / ANSYS Mechanical 求解，本文的载荷分布可直接作为输入。")

# ---------------------------------------------------------------- appendix
H("附录  文件清单与复现")
table([
    ["文件", "内容"],
    ["mesh/aircraft_surface_bin.stl", "STEP 表面网格（18 mm，364 k 面，18.2 MB）"],
    ["mesh/aircraft_surface.msh", "同上，gmsh 2.2 格式"],
    ["mesh/wing_oml.stl", "重建的机翼气动外形（水密，6.5 k 面）"],
    ["results/ll_polar.csv", "升力线极曲线（α, CL, CDi, CD, L/D）"],
    ["results/spanload_ll.csv", "展向载荷与 Schrenk 对比"],
    ["results/strength.csv", "弯矩、缘条应力、挠度沿展向分布"],
    ["scripts/01…09_*.py", "体检 / 网格 / 升力线 / 强度 / 绘图脚本"],
], widths=[6.5, 10.5])
caption("表 5  交付文件")
P("全部脚本用 Python 3.12 + numpy 编写，网格部分依赖 gmsh 4.15.2 的 Python 包；"
  "按 02_mesh.py → 04_lifting_line.py → 07_strength.py → 09_plots.py 的顺序即可复现全部结果。", indent=False)

doc.save(OUT)
print("saved", OUT)

