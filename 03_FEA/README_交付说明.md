# PersonalAircraft 仿真分析交付包

日期：2026-11-01　｜　几何：CATIA V5R21 STEP（RevN 翼盒结构 / RevP 完整外形）
单位：mm　｜　坐标系：x 向后、y 向右翼、z 向上

---

## 1. 这个包里有什么

| 目录 | 内容 |
|---|---|
| `*.docx` | 分析报告（汇总版 + 两份分册） |
| `mesh/` | 两版表面网格（STL / gmsh msh）+ 重建的机翼气动外形 |
| `results/` | 全部数值结果（极曲线、展向载荷、弯矩/应力/挠度） |
| `figures/` | 报告用图（网格视图、极曲线、展向载荷、Cp 云图、应力云图） |
| `scripts/` | 生成以上全部结果的 Python 脚本 |

### 1.1 报告（三份，各自独立）

| 文件 | 内容 | 页数/图 |
|---|---|---|
| `01_网格划分报告.docx` | 几何体检、网格参数、两版网格统计与用途 | 约 4 页，3 图 3 表 |
| `02_应力分析报告_RevN.docx` | 6g 载荷、梁模型、主梁应力云图与挠度 | 约 5 页，2 图 3 表 |
| `03_气动仿真报告_RevP.docx` | 升力线方法、极曲线、展向载荷、Cp 云图 | 约 6 页，6 图 2 表 |

### 1.2 网格

| 文件 | 大小 | 说明 |
|---|---|---|
| `mesh/aircraft_surface_bin.stl` | 17.4 MB | RevN 结构网格，364 202 三角面，18 mm |
| `mesh/aircraft_surface.msh` | 22.8 MB | 同上，gmsh 2.2 格式 |
| `mesh/revP_surface.stl` | 62.2 MB | RevP 完整外形网格，1 303 300 三角面，18 mm |
| `mesh/revP_surface.msh` | 70.3 MB | 同上，gmsh 2.2 格式 |
| `mesh/wing_oml.stl` | 0.3 MB | 由翼型截面重建的机翼外形（水密，6 528 面），可直接做 CFD 壁面 |

### 1.3 数值结果

| 文件 | 内容 |
|---|---|
| `results/ll_polar.csv` | 极曲线：α, CL, CDi, CD0, CD, L/D |
| `results/spanload_ll.csv` | 展向载荷：y, 弦长, 局部 cl, 单位展长升力, 下洗角, Schrenk 对比 |
| `results/strength.csv` | 6g 工况：弯矩、缘条应力、MS、挠度、剪力 |
| `results/ll_summary.json` | 气动汇总（CLα、L/Dmax、巡航点、翼根弯矩） |
| `results/strength_summary.json` | 强度汇总（根部应力、MS、翼尖挠度） |
| `results/volumes.csv` | STEP 每个实体的包围盒与面积（模型体检） |

### 1.4 图片

| 文件 | 内容 |
|---|---|
| `figures/view_iso.png` | RevN 结构网格等轴测 |
| `figures/view_revP_iso.png` | RevP 完整外形网格等轴测 |
| `figures/wing_oml_iso.png` | 重建机翼外形 |
| `figures/fig_polar.png` | CL(α) 与 L/D(α) |
| `figures/fig_drag.png` | 阻力极曲线 CL–CD |
| `figures/fig_spanload.png` | 展向升力分布 vs Schrenk |
| `figures/cp_iso.png` | Cp 云图（等轴测） |
| `figures/cp_top.png` | Cp 云图（上表面） |
| `figures/cp_bottom.png` | Cp 云图（下表面） |
| `figures/spar_stress_iso.png` | 主梁 von Mises 应力云图 |
| `figures/strength.png` | 缘条应力与挠度沿展向 |

### 1.5 脚本（按编号顺序执行）

```
01_inspect.py      STEP 体检（实体包围盒、面积）
02_mesh.py         RevN 网格（STL/msh）
04_lifting_line.py 升力线气动（极曲线、展向载荷）
07_strength.py     梁模型强度/刚度
08_plot_strength.py 应力-挠度曲线
09_plots.py        极曲线与展向载荷图
10_mesh_revP.py    RevP 网格
11_cp_contour.py   Cp 云图
12_spar_stress.py  主梁应力云图
06_oml.py          由翼型截面重建机翼外形
05_figures.py      网格视图渲染
build_full_report.py / build_report_revP.py / build_report.py  生成 docx
```

依赖：Python 3.12 + numpy + python-docx + Pillow + gmsh 4.15.2（Python 包）。
脚本内为绝对路径，换机器需改 `ROOT`。

---

## 2. 关键结果

| 项目 | 数值 |
|---|---|
| 升力线斜率 | 0.0876 /°（5.02 /rad） |
| 零迎角升力 | 0.53 |
| 最大升阻比 | 22.8 @ CL = 0.60 |
| 巡航（135 kg, 15 m/s） | CL = 0.48，α = 0.15°，L/D ≈ 22.7，下沉率 0.66 m/s |
| 翼根弯矩（6g, 155 kg） | 11.33 kN·m（设计 12.88，−12%） |
| 缘条应力（6g） | 364 MPa / 许用 400，MS = 0.10 |
| 腹板剪应力（6g） | ≈ 3.3 MPa（许用 60） |
| 翼尖挠度（6g） | 0.41 m（6.3% 半展长） |

---

## 3. 方法边界（重要）

- **气动**：Prandtl 升力线 + 薄翼理论，势流，**不是 RANS**。无粘性分离、无失速、无翼尖涡细节。
- **结构**：盒型梁理论（σ = M·z/I、τ = V/(2dt)），**不是三维壳单元 FEA**。无应力集中、无屈曲、无接头细节。
- **云图**：Cp 与 von Mises 都是上述解析场映射到网格逐面着色，颜色代表物理量，但分辨率受解析模型限制。
- 本机无可用 CFD/Fea 求解器（ANSYS 仅 Motion；STAR-CCM+ 缺 `starccm+.exe`），故未做 RANS/三维 FEA。

需要更真实的结果时：把 `mesh/revP_surface.stl` 导入有许可证的 STAR-CCM+/Fluent 跑 RANS；
把 `aircraft_surface_bin.stl` 导入 Abaqus/ANSYS 抽中面 + 铺层做壳单元 FEA。

---

## 4. 几何差异备忘

- **RevN**：只含主梁到后梁的后翼盒，y = 3 250 处弦向覆盖 38–84%，缺前缘 D-box 与后缘蒙皮 → 只能做结构。
- **RevP**：补齐外形，同站位覆盖 0–100% 弦长 → 可做气动。
- 两版载荷同源，报告中所有气动与结构结果都由同一套升力线分布导出。
