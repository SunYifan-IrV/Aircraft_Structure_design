// 飞行器结构设计报告 —— 精美版 PPT 构建脚本
// 依据 pptx skill 规范：LAYOUT_WIDE、无 # 的十六进制色、不共享 options 对象、原生表格、逐页讲稿
const PptxGenJS = require("pptxgenjs");
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";   // 13.333 x 7.5 in
pptx.author = "第十二小组";
pptx.title = "飞行器结构设计分析报告";

const FONT = "DengXian";       // 等线，随 Office 附带，中文渲染一致
// 配色（航空主题，非默认蓝）
const NAVY  = "0F2A43";
const BLUE  = "2E6E9E";
const SKY   = "DCEAF4";
const CARD  = "F3F7FA";
const ORANGE= "F2653D";
const TEAL  = "1F8A70";
const INK   = "233340";
const MUTED = "63717D";
const WHITE = "FFFFFF";
const LINE  = "E3E9EE";

const FIG = "../03_FEA/figures/";
const W = 13.333, H = 7.5;

// ---------- 基础 helpers ----------
function addTxt(slide, text, o) {
  const def = { x:0.6, y:1.6, w:12.13, h:0.6, fontSize:14, color:INK, fontFace:FONT,
    align:"left", valign:"top", margin:0, lineSpacingMultiple:1.12 };
  return slide.addText(text, Object.assign(def, o));
}

// 页眉：圆圈编号 + 标题（无下划线、无色条）
function header(slide, num, title, opts) {
  opts = opts || {};
  const accent = opts.accent || ORANGE;
  slide.addShape("ellipse", { x:0.6, y:0.5, w:0.52, h:0.52, fill:{color:accent}, line:{color:accent} });
  addTxt(slide, num, { x:0.6, y:0.5, w:0.52, h:0.52, fontSize:16, color:WHITE, bold:true,
    align:"center", valign:"middle", margin:0 });
  addTxt(slide, title, { x:1.3, y:0.44, w:11.2, h:0.62, fontSize:27, color:NAVY, bold:true,
    valign:"middle", margin:0 });
  addTxt(slide, String(opts.page||""), { x:12.35, y:7.08, w:0.45, h:0.28, fontSize:10, color:MUTED, align:"right", margin:0 });
}

function sectionLabel(slide, x, y, text, color) {
  // 内容内的小节标签：色点 + 加粗小标题
  slide.addShape("ellipse", { x:x, y:y+0.07, w:0.16, h:0.16, fill:{color:color}, line:{color:color} });
  addTxt(slide, text, { x:x+0.26, y:y, w:5.5, h:0.32, fontSize:15, color:NAVY, bold:true, margin:0 });
  return y + 0.42;
}

function bullets(slide, x, y, w, items, o) {
  o = o || {};
  const arr = items.map((it, i) => {
    const last = i === items.length-1;
    return {
      text: it.text,
      options: {
        bullet: { code:"2022", indent: 14 },
        breakLine: !last,
        color: it.color || INK,
        bold: !!it.bold,
        fontSize: o.size || 13,
        paraSpaceAfter: 6,
        lineSpacingMultiple: 1.1,
      },
    };
  });
  return slide.addText(arr, { x:x, y:y, w:w, h:o.h||3, fontFace:FONT, valign:"top", margin:0 });
}

function card(slide, x, y, w, h, fill) {
  slide.addShape("roundRect", { x:x, y:y, w:w, h:h, fill:{color: fill||CARD},
    line:{color:LINE, width:1}, rectRadius:0.08 });
}

function stat(slide, x, y, w, num, label, color) {
  addTxt(slide, num, { x:x, y:y, w:w, h:0.72, fontSize:38, color: color||NAVY, bold:true,
    align:"center", valign:"middle", margin:0 });
  addTxt(slide, label, { x:x, y:y+0.76, w:w, h:0.34, fontSize:11, color:MUTED, align:"center", margin:0 });
}

function table(slide, data, o) {
  o = o || {};
  const colW = o.colW || data[0].map(() => 12/data[0].length);
  const rows = data.map((row, ri) => row.map((cell, ci) => {
    const head = ri===0;
    return { text: String(cell), options: {
      color: head ? WHITE : INK, bold: head,
      fill: head ? { color: o.headerFill||BLUE } : (ri%2===0 ? { color:CARD } : { color:WHITE }),
      align: ci===0 ? "left" : "center", valign:"middle",
      fontSize: o.size||12, fontFace:FONT, margin:0.04,
    }};
  }));
  slide.addTable(rows, { x:o.x, y:o.y, w:o.w, colW:colW, fontFace:FONT,
    border:{ type:"solid", color:LINE, pt:1 }, rowH:o.rowH||0.4, valign:"middle", margin:0.05 });
}

// 图片（浅底卡片 + 按原生比例 contain，避免变形）
function figure(slide, x, y, w, h, path, label) {
  card(slide, x, y, w, h, "EFF4F8");
  slide.addImage({ path:path, x:x+0.06, y:y+0.06, w:w-0.12, h:h-0.12,
    sizing:{ type:"contain", w:w-0.12, h:h-0.12 } });
  if (label) addTxt(slide, label, { x:x, y:y+h-0.34, w:w, h:0.3, fontSize:11, color:MUTED, align:"center", margin:0 });
}

// =====================================================================
// S1 封面（深色）
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  // 装饰：右上大圆环 + 三点
  s.addShape("ellipse", { x:9.4, y:-2.3, w:7.2, h:7.2, fill:{color:NAVY}, line:{color:"16334F", width:2} });
  s.addShape("ellipse", { x:10.5, y:-1.2, w:5.0, h:5.0, fill:{color:NAVY}, line:{color:"1D415F", width:1.5} });
  s.addShape("ellipse", { x:0.7, y:6.6, w:0.22, h:0.22, fill:{color:ORANGE}, line:{color:ORANGE} });
  s.addShape("ellipse", { x:1.05, y:6.6, w:0.22, h:0.22, fill:{color:BLUE}, line:{color:BLUE} });
  s.addShape("ellipse", { x:1.4, y:6.6, w:0.22, h:0.22, fill:{color:"3E8EC0"}, line:{color:"3E8EC0"} });

  addTxt(s, "飞行器结构设计 · 第十二组大作业汇报", { x:0.85, y:1.7, w:8, h:0.4, fontSize:14, color:ORANGE, bold:true, charSpacing:2 });
  addTxt(s, "飞行器结构设计分析报告", { x:0.82, y:2.2, w:9.5, h:1.1, fontSize:46, color:WHITE, bold:true, margin:0 });
  addTxt(s, "「人机合一」低空个人飞行器 —— 无尾飞翼式单人动力滑翔机", { x:0.85, y:3.35, w:9.2, h:0.6, fontSize:18, color:SKY, margin:0 });
  addTxt(s, "结构设计  ·  仿真分析  ·  总结思考", { x:0.85, y:4.35, w:9, h:0.4, fontSize:14, color:"9FB6C8" });
  addTxt(s, "2026 · 第十二小组", { x:0.85, y:6.75, w:5, h:0.35, fontSize:12, color:"7E95A8" });
  s.addNotes("开场：各位老师好，我们第十二小组汇报「飞行器结构设计」大作业——一型「人机合一」低空个人飞行器，一台无尾飞翼式单人动力滑翔机。下面从结构设计、仿真分析、总结思考三部分汇报。");
}

// =====================================================================
// S2 目录
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  addTxt(s, "CONTENTS", { x:0.6, y:0.55, w:6, h:0.3, fontSize:12, color:ORANGE, bold:true, charSpacing:3 });
  addTxt(s, "目  录", { x:0.6, y:0.85, w:6, h:0.8, fontSize:30, color:NAVY, bold:true, margin:0 });

  const cols = [
    { num:"01", t:"结构设计", d:"需求定位 · 总体参数 · 翼型与内力\n翼面结构 · 中央承力框架", c:BLUE },
    { num:"02", t:"仿真分析", d:"网格划分 · 应力分析\n气动仿真（极曲线 · 压力云图）", c:TEAL },
    { num:"03", t:"总结思考", d:"关键结论 · 方法边界\n设计取舍与下一步", c:ORANGE },
  ];
  const x0 = 0.6, gap = 0.4, cw = (12.13 - 2*gap)/3;
  cols.forEach((col, i) => {
    const x = x0 + i*(cw+gap);
    card(s, x, 2.1, cw, 3.9, CARD);
    slide = s;
    addTxt(s, col.num, { x:x+0.4, y:2.55, w:1.4, h:1.1, fontSize:52, color:col.c, bold:true, margin:0 });
    addTxt(s, col.t, { x:x+0.4, y:3.7, w:cw-0.8, h:0.5, fontSize:24, color:NAVY, bold:true, margin:0 });
    addTxt(s, col.d, { x:x+0.4, y:4.35, w:cw-0.8, h:1.4, fontSize:13, color:MUTED, lineSpacingMultiple:1.3, margin:0 });
  });
  s.addNotes("目录：第一部分结构设计（需求、总体参数、翼型、翼面结构、中央承力框架），第二部分仿真分析（网格、应力、气动），第三部分总结与边界。");
}

// =====================================================================
// S3 设计定位与需求
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "01", "设计定位与需求", { page:3 });

  // 左：一句话定位 + 三原则
  let y = sectionLabel(s, 0.6, 1.35, "一句话定位", BLUE);
  addTxt(s, "一根 13 m 碳纤维刚性梯形机翼 + 中央承力盒/龙骨 + 乘员俯卧挂载 + 后置折叠电推进 + 重心移动操纵 + 双腿起降 —— 无尾飞翼式单人动力滑翔机。",
    { x:0.6, y:y, w:6.9, h:1.0, fontSize:14, color:INK, lineSpacingMultiple:1.25 });
  y = sectionLabel(s, 0.6, 2.85, "「人机合一」三原则", BLUE);
  bullets(s, 0.6, y, 6.9, [
    { text:"人体不是乘客，而是结构—传力—操纵链中的一环；", bold:false },
    { text:"结构既承受气动载荷，又沿明确路径把载荷传到人体；", bold:false },
    { text:"人体质量参与重心控制（weight-shift），双腿即起落装置。", bold:false },
  ], { size:13 });

  // 右：第一性原理硬约束（卡片 + 四行）
  card(s, 7.8, 1.35, 4.93, 4.55, CARD);
  sectionLabel(s, 8.05, 1.55, "第一性原理硬约束", ORANGE);
  const rows = [
    ["低失速 → 低翼载", "双脚软着陆需 V_stall ≈ 8–9 m/s"],
    ["高升阻比 → 高展弦比", "诱导阻力 ∝ 1/AR，取 AR≈8.45"],
    ["能量密度 → 续航", "3 kWh 锂电 ≈ 14 kg，平飞 25–30 min"],
    ["人体功率 ~300 W", "≪ 平飞 ~1.2 kW，必须外部能源"],
  ];
  rows.forEach((r, i) => {
    const ry = 2.05 + i*0.94;
    slide = s;
    s.addShape("ellipse", { x:8.05, y:ry+0.04, w:0.3, h:0.3, fill:{color:SKY}, line:{color:SKY} });
    addTxt(s, String(i+1), { x:8.05, y:ry+0.04, w:0.3, h:0.3, fontSize:12, color:BLUE, bold:true, align:"center", valign:"middle", margin:0 });
    addTxt(s, r[0], { x:8.5, y:ry, w:4.1, h:0.32, fontSize:13, color:NAVY, bold:true, margin:0 });
    addTxt(s, r[1], { x:8.5, y:ry+0.33, w:4.1, h:0.55, fontSize:11.5, color:MUTED, lineSpacingMultiple:1.15, margin:0 });
  });

  // 底部：任务剖面流程
  y = 6.25;
  addTxt(s, "任务剖面", { x:0.6, y:y, w:2, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  const steps = ["助跑起飞", "爬升 / 盘旋", "巡航 / 翱翔", "滑翔 flare", "双脚软着陆"];
  let fx = 2.5;
  steps.forEach((st, i) => {
    const bw = 1.85;
    s.addShape("roundRect", { x:fx, y:y-0.02, w:bw, h:0.42, fill:{color: i===3?SKY:CARD}, line:{color:LINE, width:1}, rectRadius:0.08 });
    addTxt(s, st, { x:fx, y:y-0.02, w:bw, h:0.42, fontSize:11.5, color:NAVY, bold:true, align:"center", valign:"middle", margin:0 });
    if (i < steps.length-1) addTxt(s, "→", { x:fx+bw, y:y-0.06, w:0.3, h:0.4, fontSize:13, color:ORANGE, bold:true, align:"center", valign:"middle", margin:0 });
    fx += bw + 0.3;
  });
  s.addNotes("设计定位：低空个人运动/娱乐飞行 + 热气流翱翔。三原则：人体不是乘客而是结构—传力—操纵链的一环；结构沿明确路径把气动载荷传到人体；人体质量参与重心控制、双腿即起落架。第一性原理硬约束：低失速→低翼载、高升阻比→高展弦比、能量密度决定续航；人体功率约300瓦远小于平飞约1.2千瓦，所以必须有外部能量源。任务剖面：助跑起飞、爬升/盘旋、巡航/翱翔、滑翔flare双脚软着陆。");
}

// =====================================================================
// S4 总体参数
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "01", "总体参数与翼面", { page:4 });

  // 四个大数字
  const stats = [
    ["20 m²", "机翼面积 S"],
    ["13 m", "翼展 b"],
    ["8.45", "展弦比 AR"],
    ["155 kg", "最大起飞质量 · 名义 135 kg"],
  ];
  const sw = 12.13/4;
  stats.forEach((st, i) => stat(s, 0.6+i*sw, 1.5, sw, st[0], st[1], i===0?BLUE:NAVY));

  // 左表：质量预算
  addTxt(s, "质量预算", { x:0.6, y:2.95, w:4, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  table(s, [
    ["项目", "质量"],
    ["空机质量", "60 kg"],
    ["名义乘员（范围 55–95）", "75 kg"],
    ["名义起飞质量", "135 kg"],
    ["最大乘员 / MTOW", "95 / 155 kg"],
  ], { x:0.6, y:3.35, w:6.3, colW:[4.2,2.1], size:11.5, rowH:0.42 });

  // 右表：翼面与速度
  addTxt(s, "翼面与速度包线", { x:7.25, y:2.95, w:4, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  table(s, [
    ["参数", "数值"],
    ["锥度比 λ / 根弦·梢弦", "0.5 / 2.05·1.03 m"],
    ["平均气动弦长 MAC", "1.60 m"],
    ["翼载 名义/最大", "66.2 / 76.1 N/m²"],
    ["失速 / 巡航 / 极限", "31–33 / 48–56 / 90 km/h"],
    ["材料体系", "CFRP · 7075-T6 · 芳纶"],
  ], { x:7.25, y:3.35, w:5.48, colW:[2.3,3.18], size:11.5, rowH:0.42 });

  // 底部要点
  addTxt(s, "空机 60 kg = 主结构30 + 挂架7 + 电推进6 + 电池14 + 操纵2 + 杂项1",
    { x:0.6, y:5.85, w:12.13, h:0.4, fontSize:12.5, color:MUTED });
  addTxt(s, "失速反推 S≈20.4 → 取 20 m²；低失速（8–9 m/s 双脚软着陆）→ 低翼载 66–76 N/m² → 高展弦比 8.45",
    { x:0.6, y:6.3, w:12.13, h:0.4, fontSize:13, color:BLUE, bold:true });
  s.addNotes("总体参数：空机60公斤、名义乘员75公斤，名义起飞135、最大155公斤。机翼面积20平方米由失速约束反推（双脚软着陆需要失速8–9米/秒），翼展13米、展弦比8.45、锥度比0.5、MAC 1.60米，翼载66–76牛/平方米。速度包线：失速31–33、巡航48–56、极限90公里/小时。材料以碳纤维主梁蒙皮为主，7075-T6挂架、芳纶挂带。");
}

// =====================================================================
// S5 翼型与翼根内力
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "01", "翼型选择与翼根内力", { page:5 });

  let y = sectionLabel(s, 0.6, 1.35, "翼型方案", BLUE);
  bullets(s, 0.6, y, 6.6, [
    { text:"主翼 Wortmann FX 63-137（t/c 13.7%，根处厚 0.28 m 容纳 200 mm 主梁）" },
    { text:"翼尖 E387 过渡 + −2° 洗流（延迟翼尖失速，等效 CLmax≈1.5）" },
    { text:"Re ≈ 1–2.7×10⁶ 低雷诺数段，高 CLmax、大结构深度、L/D 好" },
    { text:"升力线斜率 CLα = 4.92 rad⁻¹（0.0858 /°）" },
  ], { size:13 });

  y = sectionLabel(s, 0.6, 3.9, "升力分布与阵风校核", BLUE);
  bullets(s, 0.6, y, 6.6, [
    { text:"Schrenk 升力分布（椭圆 + 平面弦长平均），合力位于 43.4% 半翼展" },
    { text:"阵风支配：9 m/s @ V_D 未缓和 Δn≈+9.9g → 缓和因子 K_g=0.205 后 n≈3g < +6g" },
    { text:"→ 主梁仍按机动极限设计，运行包线须限速" },
  ], { size:13 });

  // 右侧：内力表 + 大数字
  table(s, [
    ["工况（单侧）", "V_root", "M_root"],
    ["限制 +4g", "3.04 kN", "8.59 kN·m"],
    ["极限 +6g", "4.56 kN", "12.88 kN·m"],
    ["极限 −3g", "−2.28 kN", "−6.44 kN·m"],
  ], { x:7.6, y:1.5, w:5.13, colW:[1.9,1.6,1.63], size:11.5, rowH:0.42 });

  card(s, 7.6, 3.75, 5.13, 2.5, CARD);
  addTxt(s, "12.88 kN·m", { x:7.6, y:4.05, w:5.13, h:0.7, fontSize:34, color:ORANGE, bold:true, align:"center", margin:0 });
  addTxt(s, "翼根极限弯矩（+6g @ MTOW）—— 主梁主导工况", { x:7.6, y:4.85, w:5.13, h:0.4, fontSize:12, color:MUTED, align:"center", margin:0 });
  addTxt(s, "纯椭圆分布 8.39 kN·m，Schrenk 因梯形升力外移 +2.4%（偏保守）", { x:7.6, y:5.4, w:5.13, h:0.6, fontSize:11.5, color:INK, align:"center", lineSpacingMultiple:1.2, margin:0 });

  s.addNotes("翼型：主翼选Wortmann FX 63-137，13.7%厚度在根弦2.05米下给出0.28米最大厚度，正好容纳200毫米主梁；翼尖向E387过渡并施加−2°洗流以延迟翼尖失速。升力分布用Schrenk近似。翼根极限内力：+6g时单侧剪力4.56千牛、弯矩12.88千牛·米。阵风是支配工况：9米/秒阵风在V_D下未缓和约10g，缓和因子0.205后降到3g，所以主梁仍按机动极限设计、运行包线限速。");
}

// =====================================================================
// S6 翼面结构
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "01", "翼面结构（主梁 / 翼肋 / 蒙皮 / 翼根）", { page:6 });

  const items = [
    ["主梁", "CFRP 盒型梁 @30% 弦，根部缘条形心距 d=200 mm；缘条单向 CFRP 定宽 20 mm，厚度台阶递减 8→6→4→2 mm（上下等强，兼顾 −3g）"],
    ["腹板", "双侧 ±45° CFRP 织物 + 3 mm PMI 夹芯（总厚 ~3.5 mm），防止深 200 mm 薄腹板剪切屈曲"],
    ["翼肋", "泡沫夹芯 @0.45 m，14 肋/侧；根肋载荷仅 ~274 N（限制）/ 412 N（极限）"],
    ["D-box / 翼根", "前缘 ±45° CFRP + 5 mm Nomex 夹芯构成主抗扭闭室（抗颤振）；翼根中央承力盒 + 7075-T6 铰耳/销，折叠铰点 y=±0.8 m → 单段 5.7 m"],
  ];
  const gx = 0.6, gy = 1.4, cw = (12.13-0.4)/2, ch = 1.95;
  items.forEach((it, i) => {
    const x = gx + (i%2)*(cw+0.4);
    const y = gy + Math.floor(i/2)*(ch+0.25);
    card(s, x, y, cw, ch, CARD);
    s.addShape("ellipse", { x:x+0.28, y:y+0.28, w:0.42, h:0.42, fill:{color:BLUE}, line:{color:BLUE} });
    addTxt(s, String(i+1), { x:x+0.28, y:y+0.28, w:0.42, h:0.42, fontSize:16, color:WHITE, bold:true, align:"center", valign:"middle", margin:0 });
    addTxt(s, it[0], { x:x+0.85, y:y+0.28, w:cw-1.1, h:0.4, fontSize:16, color:NAVY, bold:true, valign:"middle", margin:0 });
    addTxt(s, it[1], { x:x+0.3, y:y+0.82, w:cw-0.6, h:ch-0.95, fontSize:11.5, color:INK, lineSpacingMultiple:1.2, margin:0 });
  });

  // 底部：缘条递减表
  addTxt(s, "主梁缘条沿展向递减", { x:0.6, y:5.75, w:6, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  table(s, [
    ["展向位置 y (m)", "0.00", "0.65", "1.63", "3.25", "4.88"],
    ["梁高 d (mm)", "200", "190", "175", "150", "125"],
    ["极限弯矩 (N·m)", "12881", "10107", "6647", "2630", "551"],
    ["缘条厚 t (mm)", "8.0", "6.7", "4.8", "2.2", "0.6"],
  ], { x:0.6, y:6.15, w:10.2, colW:[2.6,1.5,1.5,1.5,1.5,1.5], size:11, rowH:0.38 });

  s.addNotes("翼面结构：主梁为碳纤维盒型梁，位于30%弦，根部缘条形心距200毫米；缘条单向碳纤维定宽20毫米、厚度沿展向8→6→4→2毫米台阶递减。腹板用±45°织物加3毫米PMI泡沫夹芯防剪切屈曲。翼肋泡沫夹芯间距0.45米、每侧14肋。前缘D-box用±45°碳纤维加5毫米Nomex夹芯，是主抗扭闭室、抗颤振关键。翼根用中央承力盒加7075-T6铰耳销折叠，铰点y=±0.8米，折叠后单段5.7米。");
}

// =====================================================================
// S7 中央承力框架与人体传力
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "01", "中央承力框架与人体传力路径", { page:7 });

  // 传力路径流程
  addTxt(s, "传力路径（闭合传力环）", { x:0.6, y:1.32, w:6, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  const flow = ["气动升力", "主梁", "中央承力盒", "挂点 / 吊带", "躯干托板·人体"];
  let fx = 0.6;
  flow.forEach((f, i) => {
    const bw = 2.05;
    s.addShape("roundRect", { x:fx, y:1.75, w:bw, h:0.52, fill:{color: i===2?SKY:CARD}, line:{color:LINE, width:1}, rectRadius:0.08 });
    addTxt(s, f, { x:fx, y:1.75, w:bw, h:0.52, fontSize:12.5, color:NAVY, bold:true, align:"center", valign:"middle", margin:0 });
    if (i < flow.length-1) addTxt(s, "→", { x:fx+bw, y:1.72, w:0.28, h:0.5, fontSize:14, color:ORANGE, bold:true, align:"center", valign:"middle", margin:0 });
    fx += bw + 0.28;
  });
  addTxt(s, "人体重力（惯性反力）反作用于机翼 → 闭合传力环；推力 / 起降冲击走同一套结构的逆路径",
    { x:0.6, y:2.38, w:12.13, h:0.35, fontSize:11.5, color:MUTED });

  // 左：四大部件表
  addTxt(s, "中央承力四大部件", { x:0.6, y:2.95, w:6, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  table(s, [
    ["部件", "形式 / 功能"],
    ["中央承力盒", "CFRP 盒型梁 1.6 m，汇合两侧翼根弯矩 12.9 kN·m"],
    ["龙骨", "铝 7075-T6 纵向梁 1.8 m，挂点/电池/pylon 载体"],
    ["挂点 / 吊带", "可调挂耳 + 芳纶织带，兼作重心移动操纵机构"],
    ["螺旋桨塔", "后置管架，5 kW 电机 + 折叠桨，推力传入龙骨"],
  ], { x:0.6, y:3.35, w:7.0, colW:[1.5,5.5], size:11, rowH:0.46 });

  // 右：接触压力对比（关键）
  addTxt(s, "人体支撑接触压力校核（关键）", { x:7.95, y:2.95, w:5, h:0.35, fontSize:14, color:NAVY, bold:true, margin:0 });
  // 差方案
  card(s, 7.95, 3.4, 2.35, 2.5, "FBEEE9");
  addTxt(s, "窄带方案", { x:7.95, y:3.55, w:2.35, h:0.3, fontSize:11.5, color:MUTED, bold:true, align:"center", margin:0 });
  addTxt(s, "67.8", { x:7.95, y:3.85, w:2.35, h:0.7, fontSize:34, color:ORANGE, bold:true, align:"center", margin:0 });
  addTxt(s, "kPa @ +4g", { x:7.95, y:4.6, w:2.35, h:0.3, fontSize:12, color:MUTED, align:"center", margin:0 });
  addTxt(s, "✕ 不可接受", { x:7.95, y:5.15, w:2.35, h:0.35, fontSize:13, color:"C0504D", bold:true, align:"center", margin:0 });
  // 好方案
  card(s, 10.55, 3.4, 2.18, 2.5, "E9F4EC");
  addTxt(s, "躯干托板", { x:10.55, y:3.55, w:2.18, h:0.3, fontSize:11.5, color:MUTED, bold:true, align:"center", margin:0 });
  addTxt(s, "14.9", { x:10.55, y:3.85, w:2.18, h:0.7, fontSize:34, color:TEAL, bold:true, align:"center", margin:0 });
  addTxt(s, "kPa @ +4g", { x:10.55, y:4.6, w:2.18, h:0.3, fontSize:12, color:MUTED, align:"center", margin:0 });
  addTxt(s, "✓ 满足限值", { x:10.55, y:5.15, w:2.18, h:0.35, fontSize:13, color:"3B8A5E", bold:true, align:"center", margin:0 });

  addTxt(s, "结论：必须用大面积躯干托板（胸板 + 骨盆板 + 大腿），把集中力扩散为 <15 kPa 的大面积接触压力（限值 20–30 kPa 短时）。",
    { x:0.6, y:6.35, w:12.13, h:0.45, fontSize:12.5, color:INK, bold:true });

  s.addNotes("中央承力框架：中央承力盒贯穿翼根1.6米，是两侧翼根弯矩的汇合枢纽；龙骨纵向1.8米承载挂点、电池、螺旋桨塔。传力路径：气动升力→主梁→承力盒→挂点→芳纶吊带→躯干托板→人体→重力闭合。关键是接触压力：窄带方案+4g达67.8千帕不可接受，大面积躯干托板把压力降到14.9千帕，满足生物力学限值——这是把人体安全纳入结构链的先决条件。");
}

// =====================================================================
// S8 网格划分
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "02", "仿真分析 · 网格划分", { accent:TEAL, page:8 });

  figure(s, 0.6, 1.4, 6.0, 3.55, FIG+"view_iso.png", "RevN · 结构翼盒网格");
  figure(s, 6.95, 1.4, 5.78, 3.55, FIG+"view_revP_iso.png", "RevP · 完整外形网格");

  // 关键数字
  const stats = [
    ["36.4 万", "RevN 三角面数"],
    ["130 万", "RevP 三角面数"],
    ["18 / 3.6 mm", "全局 / 最小尺寸"],
    ["Delaunay", "网格算法（Frontal-Delaunay）"],
  ];
  const sw = 12.13/4;
  stats.forEach((st, i) => stat(s, 0.6+i*sw, 5.25, sw, st[0], st[1], i===1?TEAL:NAVY));

  addTxt(s, "两版共用同一套升力线载荷源：RevN（结构翼盒）用于应力，RevP（补齐前缘 D-box 与后缘蒙皮，0–100% 弦长）用于气动。",
    { x:0.6, y:6.5, w:12.13, h:0.4, fontSize:12.5, color:MUTED });

  s.addNotes("网格划分：几何分RevN（结构翼盒）和RevP（完整外形）两版，都采用18毫米全局、3.6毫米最小尺寸、Frontal-Delaunay算法。RevN约36万三角面用于结构，RevP约130万三角面补齐前缘与后缘蒙皮用于气动。");
}

// =====================================================================
// S9 应力分析
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "02", "仿真分析 · 应力分析", { accent:TEAL, page:9 });

  figure(s, 0.6, 1.4, 6.1, 3.9, FIG+"spar_stress_iso.png", "主梁 von Mises 应力云图（+6g）");

  // 关键数字
  card(s, 7.0, 1.4, 5.73, 2.1, CARD);
  const st = [
    ["364 MPa", "缘条最大应力（许用 400）"],
    ["0.10", "安全裕度 MS"],
    ["0.41 m", "翼尖挠度（6.3% 半展长）"],
  ];
  const sw2 = 5.73/3;
  st.forEach((x, i) => { addTxt(s, x[0], { x:7.0+i*sw2, y:1.6, w:sw2, h:0.6, fontSize:24, color: i===0?ORANGE:NAVY, bold:true, align:"center", margin:0 });
    addTxt(s, x[1], { x:7.0+i*sw2, y:2.3, w:sw2, h:0.8, fontSize:10.5, color:MUTED, align:"center", lineSpacingMultiple:1.1, margin:0 }); });

  table(s, [
    ["y (m)", "M (N·m)", "σ (MPa)", "MS", "挠度 (m)"],
    ["0.09（根）", "11327", "364", "0.099", "0.408"],
    ["1.63", "5668", "333", "0.20", "0.20"],
    ["3.25", "1915", "290", "0.38", "0.06"],
    ["4.88", "292", "195", "1.05", "0.01"],
  ], { x:7.0, y:3.85, w:5.73, colW:[1.2,1.3,1.2,0.95,1.08], size:11, rowH:0.42 });

  addTxt(s, "6g 翼根弯矩 11.33 kN·m（设计 12.88，−12%）；腹板剪应力 ≈3.3 MPa（许用 60）；结构满足强度与刚度要求。",
    { x:0.6, y:6.4, w:12.13, h:0.4, fontSize:12.5, color:INK, bold:true });

  s.addNotes("应力分析：在+6g极限载荷下用盒型梁模型计算。翼根弯矩11.33千牛·米，较设计值12.88低12%；缘条最大应力364兆帕、许用400兆帕，安全裕度0.10；腹板剪应力仅3.3兆帕；翼尖挠度0.41米，约为半展长的6.3%。结构满足强度与刚度要求。");
}

// =====================================================================
// S10 气动仿真 · 极曲线
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "02", "仿真分析 · 气动仿真（极曲线）", { accent:TEAL, page:10 });

  figure(s, 0.6, 1.4, 4.1, 3.1, FIG+"fig_drag.png", "阻力极曲线 CL–CD");
  figure(s, 4.95, 1.4, 4.1, 3.1, FIG+"fig_spanload.png", "展向载荷分布");

  // 关键数字
  card(s, 9.3, 1.4, 3.43, 3.1, CARD);
  addTxt(s, "22.8", { x:9.3, y:1.75, w:3.43, h:0.8, fontSize:38, color:TEAL, bold:true, align:"center", margin:0 });
  addTxt(s, "最大升阻比 L/D @ CL=0.60", { x:9.3, y:2.65, w:3.43, h:0.5, fontSize:11, color:MUTED, align:"center", margin:0 });
  addTxt(s, "0.66 m/s", { x:9.3, y:3.25, w:3.43, h:0.6, fontSize:22, color:NAVY, bold:true, align:"center", margin:0 });
  addTxt(s, "巡航下沉率（135 kg, 15 m/s）", { x:9.3, y:3.9, w:3.43, h:0.4, fontSize:10.5, color:MUTED, align:"center", margin:0 });

  table(s, [
    ["α (°)", "CL", "CDi", "CD", "L/D"],
    ["−4", "0.18", "0.0012", "0.0137", "13.0"],
    ["0", "0.53", "0.0106", "0.0231", "22.9"],
    ["4", "0.88", "0.0294", "0.0419", "21.0"],
    ["8", "1.23", "0.0576", "0.0701", "17.5"],
  ], { x:0.6, y:4.85, w:6.0, colW:[1.0,1.0,1.3,1.3,1.4], size:11, rowH:0.4 });

  addTxt(s, "Prandtl 升力线 + 薄翼理论（势流）：升力线斜率 0.0876/°，巡航点 CL=0.48、α=0.15°、L/D≈22.7。展向载荷与 Schrenk 近似吻合。",
    { x:7.0, y:5.05, w:5.73, h:0.9, fontSize:12, color:MUTED, lineSpacingMultiple:1.25 });

  s.addNotes("气动仿真：用Prandtl升力线方法得到极曲线。升力线斜率0.0876每度，最大升阻比22.8对应CL=0.60；巡航点（135公斤、15米/秒）CL=0.48、迎角0.15°、升阻比约22.7、下沉率0.66米/秒。展向载荷与Schrenk近似吻合。");
}

// =====================================================================
// S11 气动仿真 · 压力云图
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "02", "仿真分析 · 气动仿真（表面压力）", { accent:TEAL, page:11 });

  figure(s, 0.6, 1.5, 5.9, 4.1, FIG+"cp_top.png", "上表面压力系数 Cp");
  figure(s, 6.8, 1.5, 5.93, 4.1, FIG+"cp_bottom.png", "下表面压力系数 Cp");

  addTxt(s, "上表面负压区是主要升力来源；把升力线解析场映射到网格着色。注意：此为势流解析场映射，非 RANS 结果。",
    { x:0.6, y:6.0, w:12.13, h:0.5, fontSize:13, color:INK, bold:true });
  addTxt(s, "下一步可将 RevP 表面网格导入 STAR-CCM+ / Fluent 做 RANS 复核，把结构网格导入 Abaqus / ANSYS 做三维壳单元 FEA。",
    { x:0.6, y:6.55, w:12.13, h:0.4, fontSize:12, color:MUTED });

  s.addNotes("表面压力云图：把升力线解析场映射到网格着色，展示上下表面Cp分布，上表面负压区对应主要升力来源。注意这是势流解析场映射，不是RANS结果。");
}

// =====================================================================
// S12 总结与边界
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  header(s, "03", "总结思考 · 关键结论与设计边界", { accent:ORANGE, page:12 });

  let y = sectionLabel(s, 0.6, 1.35, "关键结论", BLUE);
  const concl = [
    ["低失速（8–9 m/s 双脚软着陆）", "强制出大翼面积 20 m²、低翼载 66–76 N/m²、高展弦比 8.45"],
    ["主梁按 +4g/+6g 机动极限设计", "翼根 M=12.9 kN·m；阵风缓和后 n≈3g 不超机动极限，运行包线须限速"],
    ["人体必须用大面积躯干托板", "（非窄带）+4g 接触压力 14.9 kPa 才满足生物力学限值"],
    ["中央承力盒是汇合枢纽", "气动载荷、人体反力、螺旋桨推力、起降冲击四类载荷在此汇合"],
  ];
  concl.forEach((c, i) => {
    s.addShape("ellipse", { x:0.6, y:y, w:0.4, h:0.4, fill:{color: i===2?ORANGE:BLUE}, line:{color: i===2?ORANGE:BLUE} });
    addTxt(s, String(i+1), { x:0.6, y:y, w:0.4, h:0.4, fontSize:15, color:WHITE, bold:true, align:"center", valign:"middle", margin:0 });
    addTxt(s, c[0], { x:1.2, y:y-0.02, w:6.3, h:0.4, fontSize:15, color:NAVY, bold:true, valign:"middle", margin:0 });
    addTxt(s, c[1], { x:1.2, y:y+0.4, w:6.3, h:0.5, fontSize:12, color:MUTED, lineSpacingMultiple:1.1, margin:0 });
    y += 1.12;
  });

  // 右：方法边界
  card(s, 7.9, 1.5, 4.83, 5.2, CARD);
  addTxt(s, "方法边界（诚实声明）", { x:8.15, y:1.7, w:4.3, h:0.4, fontSize:15, color:NAVY, bold:true, margin:0 });
  const bound = [
    ["气动", "Prandtl 升力线 + 薄翼理论（势流），非 RANS —— 无粘性分离 / 失速细节"],
    ["结构", "盒型梁理论（σ=Mz/I、τ=V/(2dt)），非三维壳 FEA —— 无应力集中 / 屈曲 / 接头细节"],
    ["云图", "解析场映射着色；本机无 CFD / FEA 求解器（ANSYS 仅 Motion）"],
    ["下一步", "STL 导入 STAR-CCM+ / Abaqus 复核，铺层壳单元精细化"],
  ];
  bound.forEach((b, i) => {
    const by = 2.3 + i*1.05;
    addTxt(s, b[0], { x:8.15, y:by, w:4.3, h:0.32, fontSize:13, color:ORANGE, bold:true, margin:0 });
    addTxt(s, b[1], { x:8.15, y:by+0.34, w:4.3, h:0.66, fontSize:11, color:INK, lineSpacingMultiple:1.18, margin:0 });
  });

  s.addNotes("总结：四个关键结论——低失速强制出大翼面积与高展弦比；主梁按机动极限设计、阵风缓和后不超限；人体必须用大面积躯干托板控制接触压力；中央承力盒是四类载荷汇合枢纽。同时诚实声明方法边界：气动是升力线势流非RANS，结构是盒型梁理论非三维壳FEA，后续可用STAR-CCM+/Abaqus复核。");
}

// =====================================================================
// S13 结束（深色）
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape("ellipse", { x:-2.0, y:-2.6, w:6.5, h:6.5, fill:{color:NAVY}, line:{color:"16334F", width:2} });
  s.addShape("ellipse", { x:10.6, y:4.4, w:5.2, h:5.2, fill:{color:NAVY}, line:{color:"1D415F", width:1.5} });

  addTxt(s, "恳请老师批评指正", { x:0.6, y:2.3, w:12.13, h:1.0, fontSize:40, color:WHITE, bold:true, align:"center", margin:0 });
  addTxt(s, "谢谢聆听 · 第十二小组", { x:0.6, y:3.4, w:12.13, h:0.5, fontSize:16, color:SKY, align:"center", margin:0 });

  // 分工 + AI 说明
  addTxt(s, "分工：建模与统筹 孙一凡 · 结构分析 冯异 · 气动/有限元 张文博 · 总结报告 翁丁恺",
    { x:0.6, y:5.9, w:12.13, h:0.4, fontSize:12, color:"9FB6C8", align:"center", margin:0 });
  addTxt(s, "AI 说明：使用 Claude（Claude Code / Opus 5.5）辅助设计分析与文档草拟，结论经人工复核，由本组负责。",
    { x:0.6, y:6.4, w:12.13, h:0.4, fontSize:11, color:"7E95A8", align:"center", margin:0 });

  s.addNotes("以上就是我们的汇报，恳请各位老师批评指正。分工：建模与统筹孙一凡、结构分析冯异、气动/有限元张文博、总结报告翁丁恺。本作业使用Claude辅助设计分析与文档草拟，结论经人工复核，由本组负责。谢谢！");
}

// 输出
pptx.writeFile({ fileName: "飞行器结构设计报告_完美版.pptx" }).then(() => {
  console.log("已生成：飞行器结构设计报告_完美版.pptx");
});
