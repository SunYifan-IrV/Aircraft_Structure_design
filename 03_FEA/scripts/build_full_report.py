"""Consolidated report: mesh + stress + aero, all figures."""
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "PersonalAircraft_结构网格应力与气动分析报告.docx")

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
    set_font(p.add_run(text), size=size)
    return p

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

def table(rows, widths=None, fs=9.5):
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
            set_font(p.add_run(str(val)), size=fs, bold=(i == 0))
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

def footer_pagenum():
    from docx.oxml import OxmlElement
    p = doc.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for el, attr, txt in (("w:fldChar", "w:fldCharType", "begin"),):
        e = OxmlElement(el); e.set(qn(attr), txt); run._r.append(e)
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    run._r.append(instr)
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); run._r.append(e)
    set_font(run, size=9, color=(0x77, 0x77, 0x77))

# ------------------------------------------------------------------ cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(70)
set_font(p.add_run("PersonalAircraft 结构网格、"), "微软雅黑", "Arial", 22, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("应力分析与气动仿真报告"), "微软雅黑", "Arial", 22, True, (0x1F, 0x3A, 0x5F))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(10)
set_font(p.add_run("RevN（翼盒结构） / RevP（完整外形）"), "微软雅黑", "Arial", 12, False, (0x44, 0x44, 0x44))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(40)
set_font(p.add_run("输入：Copy_of_PersonalAircraft_Structural_RevN.stp / PersonalAircraft_Structural_RevP.stp"),
         size=9.5, color=(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("CATIA V5R21 · AP203 · 单位 mm"), size=9.5, color=(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(6)
set_font(p.add_run("2026-11-01"), size=9.5, color=(0x66, 0x66, 0x66))

doc.add_page_break()

# ------------------------------------------------------------------ 1
H("1  摘要")
P("本报告汇总了 PersonalAircraft 的两轮分析：以 RevN（翼盒结构）做有限元网格与主梁应力分析，"
  "以 RevP（完整外模线）做表面网格、气动特性与压力云图。两版几何同源、载荷同源，可以互相对照。")
table([
    ["项目", "结果", "说明"],
    ["RevN 结构", "190 实体 / 3 544 面", "翼盒段，弦向 29–75%"],
    ["RevP 结构", "192 实体 / 4 512 面", "完整外形，弦向 0–100%"],
    ["结构网格", "182 611 节点 / 364 202 面", "18 mm，RevN"],
    ["外形网格", "652 646 节点 / 1 303 300 面", "18 mm，RevP"],
    ["主梁根部应力（6g）", "364 MPa / 许用 400", "MS = 0.10，正应力控制"],
    ["腹板剪应力（6g）", "≈ 3.3 MPa", "远低于许用，不控制"],
    ["翼根弯矩（6g）", "11.33 kN·m", "设计值 12.88，偏差 −12%"],
    ["翼尖挠度（6g）", "0.41 m（6.3% 半展长）", "柔性翼，需气弹校核"],
    ["升力线斜率", "0.0876 /°（5.02 /rad）", "AR = 8.45"],
    ["最大升阻比", "22.8 @ CL = 0.60", "CD0 ≈ 0.0125，V = 15 m/s"],
    ["巡航状态", "CL = 0.48，α = 0.15°", "135 kg，15 m/s，Re = 1.64×10⁶"],
], widths=[4.2, 6.2, 7.0])
caption("表 1  主要结果汇总")

P("方法边界需要先说明：结构部分用梁理论（不是三维壳单元 FEA），气动部分用升力线 + 薄翼理论（不是 RANS）。"
  "两者都是工程快速评估方法，给出的是量级与趋势，细节（应力集中、屈曲、分离、翼尖涡）需用三维求解器复核。")

# ------------------------------------------------------------------ 2
H("2  模型与有限元网格")
H("2.1  RevN 与 RevP 的差异", 2)
P("RevN 的 STEP 只包含主梁到后梁之间的“后翼盒”：在 y = 3 250 mm 处几何覆盖 x = 579～1 287 mm（弦向 38–84%），"
  "前缘 D-box 蒙皮与后缘蒙皮缺失。它适合做结构分析，但不能直接当作气动外形。")
P("RevP 补齐了外模线，同一站位覆盖 x = 124～1 684 mm（弦向 0–100%）。因此本报告的分工是："
  "**RevN 做结构网格与应力**，**RevP 做外形网格与气动**。")
figure(os.path.join(FIG, "view_iso.png"), 15.5)
caption("图 1  RevN 表面网格（18 mm）——可见机翼只保留翼盒段")
figure(os.path.join(FIG, "view_revP_iso.png"), 15.5)
caption("图 2  RevP 完整外形网格（18 mm，130 万三角面）")

H("2.2  网格参数", 2)
P("两版网格均用 gmsh 4.15.2（OCC 内核）直接读入 STEP，按 18 mm 全局尺寸划分三角形表面网格，"
  "最小尺寸 3.6 mm，Frontal-Delaunay 算法，导出二进制 STL 与 gmsh 2.2 格式 msh，"
  "可直接导入 STAR-CCM+ / Fluent / OpenFOAM 或 Abaqus / ANSYS Mechanical。")
table([
    ["", "RevN（结构）", "RevP（外形）"],
    ["实体 / 曲面", "190 / 3 544", "192 / 4 512"],
    ["节点", "182 611", "652 646"],
    ["三角面", "364 202", "1 303 300"],
    ["全局 / 最小尺寸", "18 / 3.6 mm", "18 / 3.6 mm"],
    ["STL 大小", "18.2 MB", "62 MB"],
], widths=[4.5, 5.5, 5.5])
caption("表 2  两版网格对比")

# ------------------------------------------------------------------ 3
H("3  结构应力分析")
H("3.1  载荷与模型", 2)
P("载荷取 6g 极限机动（MTOW 155 kg，总升力 9 123 N），展向分布由 4g 升力线结果线性放大得到。"
  "结构按盒型梁处理：缘条宽 20 mm、厚 8→6.7→4.8→2.2→0.6 mm 分五段阶梯递减，梁高 200→90 mm，"
  "腹板厚 3.5 mm（±45° CFRP + PMI 夹芯），E = 120 GPa，压缩许用 400 MPa。")
P("应力场按 σ = M(y)·(z−z_NA)/I(y)、τ = V(y)/(2·d·t_web) 计算，再合成 von Mises，"
  "映射到从 RevN 网格中切出的主梁几何上（30% 弦长附近，共 13 607 个三角面）。")
figure(os.path.join(FIG, "spar_stress_iso.png"), 16.0)
caption("图 3  RevN 主梁 von Mises 应力云图（6g，155 kg）——颜色跳变为缘条厚度设计阶梯")

H("3.2  沿展向分布", 2)
figure(os.path.join(FIG, "strength.png"), 15.8)
caption("图 4  缘条压应力与翼尖挠度沿展向分布（6g）")
table([
    ["y (m)", "M (N·m)", "σ_vm (MPa)", "MS", "挠度 (m)"],
    ["0.09（根）", f"{st['M_root_6g']:.0f}", f"{st['sigma_root_MPa']:.0f}", f"{st['MS_root']:.3f}", f"{abs(st['tip_deflection_m']):.3f}"],
    ["1.63", "5 668", "333", "0.20", "0.20"],
    ["3.25", "1 915", "290", "0.38", "0.06"],
    ["4.88", "292", "195", "1.05", "0.01"],
], widths=[3.4, 3.4, 3.6, 2.4, 2.8])
caption("表 3  6g 工况主梁强度与刚度")

H("3.3  结果讨论", 2)
P(f"翼根弯矩 {st['M_root_6g']/1000:.2f} kN·m，比设计文档的 12.88 kN·m 低 12%，原因是 CAD 中翼尖有 −2° 洗出，"
  "把升力向内翼转移。这对根部结构偏安全，但意味着翼尖实际承担的载荷低于设计假设，"
  "失速特性与设计意图会有偏差，建议在气动设计里复核洗出量。")
P(f"根部缘条应力 {st['sigma_root_MPa']:.0f} MPa、MS = {st['MS_root']:.3f}。缘条本就是等强度设计，"
  "根部只剩约 10% 余量；云图上缘条厚度阶梯处的应力台阶（图 3 中的竖条纹）是胶接/搭接的薄弱位置，"
  "需要单独校核层间剪切与剥离。")
P("腹板剪应力仅约 3.3 MPa（许用 60 MPa），说明该翼盒是**正应力控制**，剪应力不构成约束——"
  "这与 13 m 展弦比、翼载仅 76 N/m² 的轻型滑翔机特征一致。")

# ------------------------------------------------------------------ 4
H("4  气动分析")
H("4.1  方法", 2)
P("展向用 Prandtl 升力线（Glauert 30 阶谐波、30 个配置点，含对称镜像），剖面用薄翼理论 cl = 2π(α_eff − α_L0)："
  "根段 FX 63-137 取 α_L0 = −6°，翼尖 E387 取 −2.5°，几何扭转由 CAD 前后缘高度差算出（翼尖 −2° 洗出）。"
  "粘性阻力用平板摩擦 + 厚度形状因子估算：Re = 1.64×10⁶ 时 Cf = 0.00423，CD0 ≈ 0.0125。")
P("表面压力云图按 Cp = 1 − (1 ± γ/2V)² 合成，γ 为薄翼载荷分布。它给出前缘吸力峰、弦向恢复与展向卸载的正确趋势，"
  "但不含粘性分离、失速与翼尖涡。")

H("4.2  极曲线", 2)
figure(os.path.join(FIG, "fig_polar.png"), 16.0)
caption("图 5  CL(α) 与 L/D(α)，V = 15 m/s，135 kg")
figure(os.path.join(FIG, "fig_drag.png"), 10.5)
caption("图 6  阻力极曲线 CL–CD")
table([
    ["α (°)", "CL", "CDi", "CD", "L/D"],
    ["−4", "0.18", "0.0012", "0.0137", "13.0"],
    ["0", "0.53", "0.0106", "0.0231", "22.9"],
    ["4", "0.88", "0.0294", "0.0419", "21.0"],
    ["8", "1.23", "0.0576", "0.0701", "17.5"],
], widths=[2.6, 2.8, 2.8, 2.8, 2.8])
caption("表 4  气动系数（α ≥ 6° 已偏离线性段，仅作趋势参考）")

P(f"升力线斜率 {ll['CLalpha_per_deg']:.4f} /deg，零迎角升力 0.53，最大升阻比 {ll['LDmax']:.1f}"
  f"（CL = {ll['CL_at_LDmax']:.2f}，α = {ll['alpha_LDmax']:.1f}°）。135 kg、15 m/s 巡航时 CL = 0.48、"
  f"α = {ll['alpha_cruise']:.2f}°，L/D ≈ 22.7，下滑角约 2.5°，下沉率 0.66 m/s。"
  "对滑翔机而言 L/D 23 偏低（现代复合材料滑翔机 35–45），主因是 6% 弯度的高阻翼型与 0.0125 的 CD0。")

H("4.3  展向载荷", 2)
figure(os.path.join(FIG, "fig_spanload.png"), 14.5)
caption("图 7  4g 限制载荷下的展向升力分布与 Schrenk 对比（归一化到同一总升力）")
P("本文分布内翼略高、翼尖明显偏低，差异来自 CAD 的 −2° 洗出；这也解释了翼根弯矩比设计值低 12% 的原因。"
  "洗出使翼尖先于根部达到失速迎角的经典设计意图成立，但代价是翼尖升力损失与诱导阻力略增。")

H("4.4  表面压力云图", 2)
P("图 8–10 为 α = 4°（CL ≈ 0.82）工况的表面 Cp 云图。上表面前缘形成强吸力区（深蓝，Cp 低于 −3 被色标截断），"
  "沿弦向迅速恢复；下表面整体为正压，前缘附近出现驻点高压；翼尖因洗出与三维卸载吸力明显减弱。")
figure(os.path.join(FIG, "cp_iso.png"), 16.0)
caption("图 8  Cp 云图（等轴测）  α = 4°，V = 15 m/s")
figure(os.path.join(FIG, "cp_top.png"), 16.0)
caption("图 9  上表面 Cp 云图（俯视）")
figure(os.path.join(FIG, "cp_bottom.png"), 16.0)
caption("图 10  下表面 Cp 云图（仰视）")

# ------------------------------------------------------------------ 5
H("5  结论与建议")
P("(1) 几何：RevN 缺前缘/后缘蒙皮，只能做结构；RevP 完整，可做气动。若后续要“结构-气动一体”分析，"
  "应以 RevP 为唯一几何源。", indent=False)
P("(2) 强度：6g 下主梁根部 364 MPa，MS = 0.10，正应力控制；缘条阶梯处需补做胶接层间校核；"
  "腹板剪应力可忽略。", indent=False)
P("(3) 刚度：6g 翼尖挠度 0.41 m（6.3% 半展长），已进入气动弹性显著区间，颤振/发散必须专门校核。", indent=False)
P("(4) 气动：L/D 22.8 偏低，若以滑翔性能为目标，应重新评估翼型（6% 弯度 vs 低阻层流翼型）与 CD0 假设。", indent=False)
P("(5) 下一步：三维壳单元 + 复合材料铺层 FEA（屈曲、接头、疲劳）；有许可证时用 STAR-CCM+/Fluent 跑 RANS，"
  "以本文网格为壁面、按第 4 章工况设置边界条件。", indent=False)

# ------------------------------------------------------------------ appendix
H("附录  文件清单")
table([
    ["文件", "内容"],
    ["mesh/aircraft_surface_bin.stl", "RevN 结构网格（364 k 面，18.2 MB）"],
    ["mesh/revP_surface.stl / .msh", "RevP 外形网格（1.30 M 面，62 MB）"],
    ["mesh/wing_oml.stl", "重建的机翼气动外形（水密，6.5 k 面）"],
    ["results/ll_polar.csv", "极曲线数据"],
    ["results/spanload_ll.csv", "展向载荷与 Schrenk 对比"],
    ["results/strength.csv", "弯矩、应力、挠度沿展向"],
    ["figures/*.png", "本报告全部图片"],
    ["scripts/01…12_*.py", "网格 / 升力线 / 强度 / 云图脚本"],
], widths=[6.5, 10.5])
caption("表 5  交付文件")
P("全部脚本为 Python 3.12 + numpy，网格部分依赖 gmsh 4.15.2；按 02 → 04 → 07 → 09 → 10 → 11 → 12 的顺序可复现全部结果。", indent=False)

footer_pagenum()
doc.save(OUT)
print("saved", OUT)
