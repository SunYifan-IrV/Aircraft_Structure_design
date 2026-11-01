"""Build three separate reports: mesh / stress (RevN) / aerodynamics (RevP)."""
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

ROOT = r"C:\Users\张文博\Documents\deepseek-harness\default-workspace\fea_aero"
FIGDIR = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")

ll = json.load(open(os.path.join(RES, "ll_summary.json")))
st = json.load(open(os.path.join(RES, "strength_summary.json")))


def new_doc(title1, title2, sub, src):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin, s.bottom_margin = Cm(2.2), Cm(1.8)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(90)
    fs = set_font(p.add_run(title1), "微软雅黑", "Arial", 24, True, (0x1F, 0x3A, 0x5F))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(title2), "微软雅黑", "Arial", 18, True, (0x33, 0x55, 0x77))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    set_font(p.add_run(sub), "微软雅黑", "Arial", 11, False, (0x55, 0x55, 0x55))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    set_font(p.add_run("输入：" + src), size=9, color=(0x77, 0x77, 0x77))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run("2026-11-01"), size=9, color=(0x77, 0x77, 0x77))
    doc.add_page_break()
    return doc


def set_font(run, cn="宋体", en="Times New Roman", size=10.5, bold=None, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    return run


def H(doc, text, level=1):
    p = doc.add_heading(level=level)
    set_font(p.add_run(text), "微软雅黑", "Arial", {1: 15, 2: 12.5}[level], True, (0x1F, 0x3A, 0x5F))
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(5)


def P(doc, text, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74) if indent else Cm(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_font(p.add_run(text), size=10.5)


def B(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    set_font(p.add_run(text), size=10.5)


def CAP(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    set_font(p.add_run(text), size=9, color=(0x55, 0x55, 0x55))


def TABLE(doc, rows, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or j > 0) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            set_font(p.add_run(str(val)), size=9.5, bold=(i == 0))
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)


def FIG(doc, name, width=15.8):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(os.path.join(FIGDIR, name), width=Cm(width))


# =====================================================================
# 1. 网格划分报告
# =====================================================================
doc = new_doc("PersonalAircraft 机翼结构", "有限元表面网格划分报告",
              "RevN 结构网格 · RevP 外形网格 · gmsh 4.15.2",
              "Copy_of_PersonalAircraft_Structural_RevN.stp / PersonalAircraft_Structural_RevP.stp")

H(doc, "1  概述")
P(doc, "本报告记录 PersonalAircraft 两个 CATIA 版本的 STEP 几何转换为表面网格的全过程，"
       "包括几何体检、网格参数、网格统计与用途划分。网格为三角形表面网格，单位 mm，"
       "可直接导入 STAR-CCM+ / Fluent / OpenFOAM（CFD）或 Abaqus / ANSYS（结构）。")
TABLE(doc, [
    ["版本", "实体 / 曲面", "弦向覆盖", "用途"],
    ["RevN", "190 / 3 544", "38–84%（仅翼盒）", "结构分析"],
    ["RevP", "192 / 4 512", "0–100%（完整外形）", "气动分析"],
], widths=[3.0, 4.2, 4.5, 4.5])
CAP(doc, "表 1  两版几何对比")

H(doc, "2  几何体检")
P(doc, "两个 STEP 均由 CATIA V5R21 以 AP203 导出，全部为闭合实体（MANIFOLD_SOLID_BREP），无自由边。"
       "RevP 包围盒 2 565 × 13 051 × 938 mm，RevN 为 2 565 × 13 000 × 862 mm，"
       "与设计文档的 13 m 翼展、2.05 m 根弦一致。")
P(doc, "弦向切片是区分两者的关键：在 y = 3 250 mm 处，RevN 只覆盖 x = 579～1 287 mm（弦向 38–84%），"
       "RevP 覆盖 x = 124～1 684 mm（0–100%）。RevN 缺前缘 D-box 与后缘蒙皮，"
       "若直接拿它做 CFD，翼盒会被当成开缝平板，压力分布完全失真。")
FIG(doc, "view_iso.png", 15.5)
CAP(doc, "图 1  RevN 表面网格——机翼只保留翼盒段")
FIG(doc, "view_revP_iso.png", 15.5)
CAP(doc, "图 2  RevP 表面网格——前缘、后缘蒙皮齐全")
FIG(doc, "wing_oml_iso.png", 15.0)
CAP(doc, "图 3  由翼型截面重建的机翼外形（wing_oml.stl，6 528 面，水密）")

H(doc, "3  网格参数")
P(doc, "使用 gmsh 4.15.2 的 OCC 内核直接读入 STEP，按 18 mm 全局尺寸划分，最小尺寸 3.6 mm，"
       "Frontal-Delaunay 算法（Mesh.Algorithm = 1），平滑 3 次。为保证 CAD 曲面特征不丢失，"
       "按曲面边界自动加密，未使用曲率自适应（该选项在 190 个实体的模型上会导致内存异常）。")
TABLE(doc, [
    ["参数", "RevN", "RevP"],
    ["全局尺寸 / 最小尺寸", "18 mm / 3.6 mm", "18 mm / 3.6 mm"],
    ["网格算法", "Frontal-Delaunay", "Frontal-Delaunay"],
    ["节点数", "182 611", "652 646"],
    ["三角面数", "364 202", "1 303 300"],
    ["网格总面积", "38.9 m²", "—"],
    ["STL 文件", "17.4 MB", "62.2 MB"],
    ["msh 文件", "22.8 MB", "70.3 MB"],
], widths=[5.0, 5.5, 5.5])
CAP(doc, "表 2  网格统计")

H(doc, "4  网格质量与用途")
P(doc, "三角形网格平均边长约 18 mm，机翼前缘曲率较大处自动加密到 6–10 mm，"
       "机身/短舱等大曲率区域保持 18 mm。对于后续 CFD，建议在表面网格基础上追加："
       "前缘 8–10 mm 局部加密、20 层附面层（增长率 1.2、首层 0.02 mm，对应 y⁺ ≈ 1）。")
B(doc, "CFD 壁面：优先用 RevP 的 revP_surface.stl，或重建的 wing_oml.stl（水密、面数少、无内部结构）")
B(doc, "结构分析：用 RevN 的 aircraft_surface_bin.stl，翼盒、梁、肋、接头齐全")
B(doc, "若只需机翼气动外形：wing_oml.stl（6 528 面，半翼体积 1.267 m³，可直接封闭成流体域）")

H(doc, "5  交付文件")
TABLE(doc, [
    ["文件", "内容"],
    ["mesh/revP_surface.stl / .msh", "RevP 完整外形，1 303 300 面"],
    ["mesh/aircraft_surface_bin.stl / .msh", "RevN 结构，364 202 面"],
    ["mesh/wing_oml.stl", "重建机翼外形（水密，6 528 面）"],
    ["scripts/02_mesh.py / 10_mesh_revP.py / 06_oml.py", "网格生成脚本"],
], widths=[7.5, 9.5])
CAP(doc, "表 3  网格相关文件")
doc.save(os.path.join(ROOT, "01_网格划分报告.docx"))
print("saved 01")

# =====================================================================
# 2. 应力分析报告（RevN）
# =====================================================================
doc = new_doc("PersonalAircraft 主梁", "应力与刚度分析报告",
              "RevN 翼盒结构 · 6g 极限机动 · 梁理论 + 应力云图",
              "Copy_of_PersonalAircraft_Structural_RevN.stp")

H(doc, "1  概述")
P(doc, "本报告以 RevN 翼盒几何为对象，按 6g 极限机动（MTOW 155 kg）计算主梁的弯矩、缘条正应力、"
       "腹板剪应力与翼尖挠度，并给出沿展向的 von Mises 应力云图。计算采用盒型梁理论，"
       "载荷来自同一套升力线气动结果，保证与气动报告一致。")

H(doc, "2  结构与载荷")
P(doc, "主梁为盒型梁：上下缘条宽 20 mm，厚度按 8 → 6.7 → 4.8 → 2.2 → 0.6 mm 五段阶梯递减，"
       "梁高由根部 200 mm 减至翼尖 90 mm；腹板为 ±45° CFRP + 3 mm PMI 夹芯，总厚 3.5 mm。"
       "材料取 E = 120 GPa，压缩许用 400 MPa、剪切许用 60 MPa。")
P(doc, "载荷：6g 总升力 9 123 N，展向分布由升力线结果线性放大；根部单侧剪力 4 561 N、弯矩 11.33 kN·m。")
TABLE(doc, [
    ["y (m)", "梁高 d (mm)", "缘条厚 t (mm)", "弯矩 M (N·m)", "σ_vm (MPa)"],
    ["0.00", "200", "8.0", "11 327", "364"],
    ["0.65", "190", "6.7", "7 800", "340"],
    ["1.63", "175", "4.8", "5 668", "333"],
    ["3.25", "150", "2.2", "1 915", "290"],
    ["4.88", "125", "0.6", "292", "195"],
], widths=[2.6, 3.2, 3.4, 3.4, 3.2])
CAP(doc, "表 1  6g 工况主梁内力与应力")

H(doc, "3  计算方法")
P(doc, "按 Euler-Bernoulli 梁处理，截面惯性矩 I = 2·A_cap·(d/2)²，A_cap = 20 mm × t(y)。"
       "正应力 σ = M(y)·(z − z_NA)/I，腹板剪应力 τ = V(y)/(2·d·t_web)，von Mises σ_vm = √(σ² + 3τ²)。"
       "应力场逐三角面映射到从 RevN 网格中切出的主梁几何（30% 弦长，13 607 个三角面）。")
P(doc, "挠度由曲率 κ = M/(EI) 沿展向两次积分得到，边界条件取翼尖自由、翼根固支。")

H(doc, "4  应力云图")
FIG(doc, "spar_stress_iso.png", 16.0)
CAP(doc, "图 1  RevN 主梁 von Mises 应力云图（6g，155 kg）")
P(doc, "云图中沿展向的竖向色阶跳变对应缘条厚度的设计阶梯（y = 0.65 / 1.63 / 3.25 / 4.88 m），"
       "不是网格瑕疵。根部缘条呈红色（353–364 MPa），向翼尖逐渐过渡到蓝色（<100 MPa）；"
       "腹板与中性轴附近为深蓝，说明剪应力与弯曲中性层应力都很低。")

H(doc, "5  沿展向分布")
FIG(doc, "strength.png", 15.8)
CAP(doc, "图 2  缘条压应力与翼尖挠度沿展向分布（6g）")
TABLE(doc, [
    ["y (m)", "M (N·m)", "σ (MPa)", "MS", "挠度 (m)"],
    ["0.09（根）", f"{st['M_root_6g']:.0f}", f"{st['sigma_root_MPa']:.0f}", f"{st['MS_root']:.3f}", f"{abs(st['tip_deflection_m']):.3f}"],
    ["1.63", "5 668", "333", "0.20", "0.20"],
    ["3.25", "1 915", "290", "0.38", "0.06"],
    ["4.88", "292", "195", "1.05", "0.01"],
], widths=[3.4, 3.4, 3.2, 2.4, 3.2])
CAP(doc, "表 2  6g 工况强度与刚度")

H(doc, "6  讨论与结论")
P(doc, f"(1) 强度：根部缘条 {st['sigma_root_MPa']:.0f} MPa，MS = {st['MS_root']:.3f}，余量约 10%。"
       "缘条为等强度设计，内翼段应力都在 290–364 MPa，任何材料折减或缺陷都会让裕度转负。")
P(doc, "(2) 剪应力：腹板 τ ≈ 3.3 MPa，远低于 60 MPa 许用——该翼盒是正应力控制，剪应力不构成约束。")
P(doc, "(3) 刚度：6g 翼尖挠度 0.41 m（半展长 6.3%），已进入气动弹性显著区间，颤振/发散需专门校核。")
P(doc, "(4) 薄弱位置：缘条厚度阶梯处的胶接/搭接面（云图竖向条纹）需要单独做层间剪切与剥离校核；"
       "y = ±0.8 m 折叠接头的耳片承压与销剪也未包含在本模型内。")

H(doc, "7  方法边界与文件")
P(doc, "本报告为梁理论快速评估，不是三维壳单元 FEA：不含应力集中、蒙皮/腹板屈曲、接头细节与疲劳。"
       "完整校核需抽中面 + 复合材料铺层，用 Abaqus/ANSYS 求解。")
TABLE(doc, [
    ["文件", "内容"],
    ["figures/spar_stress_iso.png", "主梁应力云图"],
    ["figures/strength.png", "应力/挠度沿展向曲线"],
    ["results/strength.csv", "弯矩、应力、MS、挠度逐站数据"],
    ["results/strength_summary.json", "汇总指标"],
    ["scripts/07_strength.py / 12_spar_stress.py", "计算与绘图脚本"],
], widths=[7.5, 9.5])
CAP(doc, "表 3  相关文件")
doc.save(os.path.join(ROOT, "02_应力分析报告_RevN.docx"))
print("saved 02")

# =====================================================================
# 3. 气动仿真报告（RevP）
# =====================================================================
doc = new_doc("PersonalAircraft 机翼", "气动特性与表面压力分析报告",
              "RevP 完整外形 · 升力线 + 薄翼理论 · Cp 云图",
              "PersonalAircraft_Structural_RevP.stp")

H(doc, "1  概述")
P(doc, "以 RevP 完整外模线为几何，计算 13 m 展弦比 8.45 机翼的升力、阻力、展向载荷与表面压力分布，"
       "并给出 α = 4° 工况的 Cp 彩色云图。方法为 Prandtl 升力线 + 薄翼理论（势流），"
       "用于快速评估气动特性与载荷分布，不能替代 RANS。")

H(doc, "2  计算模型与方法")
P(doc, "展向用 Glauert 傅里叶级数（30 阶谐波、30 个配置点，含镜像半翼），剖面用薄翼理论 "
       "cl = 2π(α_eff − α_L0)。根段 FX 63-137 取 α_L0 = −6°，翼尖 E387 取 −2.5°，"
       "在 y = 4.5～6.5 m 过渡；几何扭转由 CAD 前后缘高度差直接算出（翼尖 −2° 洗出）。")
P(doc, "粘性阻力用平板摩擦 + 厚度形状因子估算：Re = 1.64×10⁶（V = 15 m/s、c = 1.6 m）时 Cf = 0.00423，"
       "取 t/c = 11.5%、形状因子 1.29，加 0.002 干扰余量，得 CD0 ≈ 0.0125。")
P(doc, "表面压力按 Cp = 1 − (1 ± γ/2V)² 合成，γ 为薄翼载荷分布；前缘 1% 弦长内的奇异值截断在 Cp = −3。")

H(doc, "3  极曲线")
FIG(doc, "fig_polar.png", 16.0)
CAP(doc, "图 1  CL(α) 与 L/D(α)，V = 15 m/s")
FIG(doc, "fig_drag.png", 10.5)
CAP(doc, "图 2  阻力极曲线 CL–CD")
TABLE(doc, [
    ["α (°)", "CL", "CDi", "CD", "L/D"],
    ["−4", "0.18", "0.0012", "0.0137", "13.0"],
    ["0", "0.53", "0.0106", "0.0231", "22.9"],
    ["4", "0.88", "0.0294", "0.0419", "21.0"],
    ["8", "1.23", "0.0576", "0.0701", "17.5"],
], widths=[2.6, 2.8, 2.8, 2.8, 2.8])
CAP(doc, "表 1  气动系数（α ≥ 6° 已偏离线性段）")
P(doc, f"升力线斜率 {ll['CLalpha_per_deg']:.4f} /deg（{ll['CLalpha_per_deg']*57.3:.2f} /rad），零迎角升力 0.53，"
       f"最大升阻比 {ll['LDmax']:.1f}（CL = {ll['CL_at_LDmax']:.2f}，α = {ll['alpha_LDmax']:.1f}°）。"
       f"135 kg、15 m/s 巡航：CL = 0.48、α = {ll['alpha_cruise']:.2f}°、L/D ≈ 22.7、下沉率 0.66 m/s。")
P(doc, "L/D 23 对滑翔机偏低（现代复合材料滑翔机 35–45），主因是 6% 弯度的高阻翼型与 0.0125 的 CD0 假设。"
       "若要提升滑翔性能，应优先重选翼型而非继续优化结构。")

H(doc, "4  展向载荷")
FIG(doc, "fig_spanload.png", 14.5)
CAP(doc, "图 3  4g 限制载荷下展向升力分布与 Schrenk 对比（归一化到同一总升力）")
P(doc, "本文分布内翼略高、翼尖明显偏低，差异来自 CAD 的 −2° 洗出。洗出让翼尖先于根部达到失速迎角，"
       "符合经典设计意图，但代价是翼尖升力损失与诱导阻力略增；也使翼根弯矩比 Schrenk 估算低约 12%。")

H(doc, "5  表面压力云图")
P(doc, "图 4–6 为 α = 4°（CL ≈ 0.82）的 Cp 云图。上表面前缘形成强吸力区（深蓝），沿弦向迅速恢复；"
       "下表面整体正压（红/黄），前缘附近为驻点高压；翼尖因洗出与三维卸载，吸力明显减弱。")
FIG(doc, "cp_iso.png", 16.0)
CAP(doc, "图 4  Cp 云图（等轴测）  α = 4°，V = 15 m/s")
FIG(doc, "cp_top.png", 16.0)
CAP(doc, "图 5  上表面 Cp 云图（俯视）")
FIG(doc, "cp_bottom.png", 16.0)
CAP(doc, "图 6  下表面 Cp 云图（仰视）")

H(doc, "6  结论与局限")
P(doc, "(1) 巡航效率：CL = 0.48 时 L/D ≈ 22.7，对应下滑角 2.5°、下沉率 0.66 m/s。")
P(doc, "(2) 载荷：展向分布因洗出而偏内翼，翼根弯矩较 Schrenk 估算低 12%，结构设计偏安全。")
P(doc, "(3) 压力分布：前缘吸力峰、弦向恢复、翼尖卸载的趋势正确，可用于定性判断与载荷提取。")
P(doc, "(4) 局限：势流方法不含粘性分离、失速、翼尖涡与压缩性；CLmax 与失速特性需 CFD 或风洞确认。"
       "本机无可用 RANS 求解器，revP_surface.stl 已备好，可在有许可证的 STAR-CCM+/Fluent 上直接计算。")

H(doc, "7  文件")
TABLE(doc, [
    ["文件", "内容"],
    ["figures/fig_polar.png, fig_drag.png", "极曲线"],
    ["figures/fig_spanload.png", "展向载荷对比"],
    ["figures/cp_iso.png, cp_top.png, cp_bottom.png", "Cp 云图"],
    ["results/ll_polar.csv, spanload_ll.csv", "数值结果"],
    ["scripts/04_lifting_line.py / 11_cp_contour.py", "计算与绘图脚本"],
], widths=[8.0, 9.0])
CAP(doc, "表 2  相关文件")
doc.save(os.path.join(ROOT, "03_气动仿真报告_RevP.docx"))
print("saved 03")


