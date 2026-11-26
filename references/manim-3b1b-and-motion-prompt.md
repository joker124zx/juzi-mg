# Manim (3Blue1Brown) 教学算子、`remotion-video-skill` 过程性动画与 `motion-prompt` 微动效词典

本文件整合了以下 4 个开源仓库的核心数学与动效逻辑：
1. [`ManimCommunity/manim`](https://github.com/ManimCommunity/manim)（`manim/utils/rate_functions.py`、`manim/animation/indication.py`、`manim/animation/transform.py`）
2. [`wshuyi/remotion-video-skill`](https://github.com/wshuyi/remotion-video-skill)（3B1B 过程性教学动画范式与 4 阶段叙事流水线）
3. [`remotion-dev/remotion`](https://github.com/remotion-dev/remotion)（纯帧时间函数确定性渲染规范）
4. [`showheyohtaki/motion-prompt`](https://showheyohtaki.github.io/motion-prompt/)（30 大微动效物理曲线与动态排版词典）

---

## 一、`Manim` (3Blue1Brown) 核心速率函数库（Ported from `rate_functions.py`）

在科普、算法与逻辑推演动画中，除了标准贝塞尔曲线，直接使用 Manim 的经典速率函数能瞬间获得 3Blue1Brown 标志性的呼吸感与强调节奏：

```javascript
// 1. Sigmoid 与 Smooth (Manim 默认平滑曲线，曲率连续)
function manimSigmoid(x) { return 1 / (1 + Math.exp(-x)); }
function manimSmooth(t, inflection = 10.0) {
  const u = Math.max(0, Math.min(1, t));
  const err = manimSigmoid(-inflection / 2);
  return Math.max(0, Math.min(1, (manimSigmoid(inflection * (u - 0.5)) - err) / (1 - 2 * err)));
}

// 2. rush_into / rush_from (前半段加速冲刺 / 后半段减速舒展)
function rushInto(t) { return 2 * manimSmooth(0.5 * Math.max(0, Math.min(1, t))); }
function rushFrom(t) { return 2 * manimSmooth(0.5 * (Math.max(0, Math.min(1, t)) + 1)) - 1; }

// 3. there_and_back (0 -> 1 -> 0 往返脉冲，Indicate / Flash / Wiggle 专用)
function thereAndBack(t) {
  const u = Math.max(0, Math.min(1, t));
  return u < 0.5 ? manimSmooth(2 * u) : manimSmooth(2 * (1 - u));
}

// 4. there_and_back_with_pause (0 -> 1 停留 pauseRatio -> 0，聚光灯高亮专用)
function thereAndBackWithPause(t, pauseRatio = 1 / 3) {
  const u = Math.max(0, Math.min(1, t));
  const a = 2 / (1 - pauseRatio);
  if (u < 0.5 - pauseRatio / 2) return manimSmooth(a * u);
  if (u < 0.5 + pauseRatio / 2) return 1;
  return manimSmooth(a - a * u);
}

// 5. running_start (先向后蓄力拉弓 pullFactor，再向前冲刺，对应 Anticipation 预备动作)
function runningStart(t, pullFactor = -0.35) {
  const u = Math.max(0, Math.min(1, t));
  // 7次Bernstein多项式近似 [0, 0, pullFactor, pullFactor, 1, 1, 1]
  const s = 1 - u;
  return (
    15 * Math.pow(s, 4) * Math.pow(u, 2) * pullFactor +
    20 * Math.pow(s, 3) * Math.pow(u, 3) * pullFactor +
    15 * Math.pow(s, 2) * Math.pow(u, 4) +
    6 * s * Math.pow(u, 5) +
    Math.pow(u, 6)
  );
}

// 6. wiggle (Manim 摇摆强调函数，适合错误报警或痛点卡片晃动)
function manimWiggle(t, wiggles = 2) {
  const u = Math.max(0, Math.min(1, t));
  return thereAndBack(u) * Math.sin(wiggles * Math.PI * u);
}
```

---

## 二、`Manim` + `remotion-video-skill` 五大教学过程性算子（Process Animations）

> **核心原则（源自 `wshuyi/remotion-video-skill`）**：
> 当口播讲到「对比、筛选、计算、推导、匹配」时，**严禁只摆一张静态表格或死卡片**！必须使用以下过程性算子把「思考与筛选的过程」可视化出来。

### 1. `SlidingWindow`（滑动高亮扫描窗）
- **适用场景**：在多个模型/选项/代码行之间依次扫描、评估并锁定胜出项。
- **实现配方**：一个带发光边框的扫描框 `<div id="scanBox">`，其 `(x, y, width, height, borderColor)` 使用 `EASE.swift` 在候选目标之间平滑插值滑动；扫描框停靠在目标 $i$ 的窗口期内，目标 $i$ 放大 `1.04x` 并点亮结论徽章。

### 2. `FocusDim` / `FocusOn`（聚光灯遮罩压暗）
- **适用场景**：画面中同时存在 3~5 个信息模块，口播正在单讲其中第 $k$ 个模块时。
- **实现配方**：非焦点模块的 `opacity` 压低至 `0.32`、`filter: grayscale(0.45) blur(1.5px)`，仅当前焦点模块保持 `opacity: 1` + 彩色发光描边，引导观众视线 100% 锁定口播焦点。

### 3. `Circumscribe`（手绘荧光圈注算子，源自 `manim/animation/indication.py`）
- **适用场景**：圈出关键结论、核心数字或胜出指标。
- **实现配方**：使用 SVG `<rect>` 或手绘椭圆 `<path pathLength="1">`，通过 `stroke-dasharray` 与 `stroke-dashoffset` 实现「一笔画出外框 $\rightarrow$ 停留强调 $\rightarrow$ 顺着笔迹尾端收起消失」的完整闭环：
```javascript
function updateCircumscribe(svgPathEl, t, tStart, dur = 0.85) {
  const u = (t - tStart) / dur;
  if (u <= 0 || u >= 1) { svgPathEl.style.opacity = '0'; return; }
  svgPathEl.style.opacity = '1';
  if (u < 0.45) {
    // 画出阶段 (0 -> 1)
    const draw = manimSmooth(u / 0.45);
    svgPathEl.setAttribute('stroke-dasharray', `${draw.toFixed(3)} 1.2`);
    svgPathEl.setAttribute('stroke-dashoffset', '0');
  } else if (u < 0.75) {
    // 保持圈住阶段
    svgPathEl.setAttribute('stroke-dasharray', '1 1.2');
    svgPathEl.setAttribute('stroke-dashoffset', '0');
  } else {
    // 顺着尾部擦除阶段
    const erase = manimSmooth((u - 0.75) / 0.25);
    svgPathEl.setAttribute('stroke-dasharray', '1 1.2');
    svgPathEl.setAttribute('stroke-dashoffset', (-erase).toFixed(3));
  }
}
```

### 4. `Indicate`（脉冲染色放大，源自 `manim/animation/indication.py`）
- **适用场景**：口播念到某个关键词或徽章时，该元素瞬间放大 `1.18x` 并染成高能金色 `#FFC62B`，随后平滑恢复原状：
```javascript
function applyIndicate(el, t, tStart, dur = 0.55, scaleFactor = 1.18) {
  const u = (t - tStart) / dur;
  const k = (u > 0 && u < 1) ? thereAndBack(u) : 0;
  el.style.transform = `scale(${(1 + (scaleFactor - 1) * k).toFixed(3)})`;
}
```

### 5. `ValueFlyIn` / `TransformMatchingTex`（跨组件数值抛物线飞入）
- **适用场景**：把痛点账单里的数字、评测表里的某项参数「拎出来」飞入右侧结论卡或汇总公式中。
- **实现配方**：飞行徽章的水平坐标走 `mix(x1, x2, u)`，垂直坐标叠加抛物线弧高 `-Math.sin(Math.PI * u) * arcHeight`，落地瞬间触发目标卡片的 `popSS` 挤压回弹。

---

## 三、`showheyohtaki/motion-prompt` 微动效力学与 Newton-Raphson 精确贝塞尔求解器

```javascript
// Newton-Raphson + 二分法精确求解三次贝塞尔 cubic-bezier(x1, y1, x2, y2)
function bezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sampleX = t => ((ax * t + bx) * t + cx) * t;
  const sampleY = t => ((ay * t + by) * t + cy) * t;
  const sampleDX = t => (3 * ax * t + 2 * bx) * t + cx;
  return function(x) {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 6; i++) {
      const dx = sampleX(t) - x, d = sampleDX(t);
      if (Math.abs(dx) < 1e-6 || Math.abs(d) < 1e-6) break;
      t -= dx / d;
    }
    return sampleY(Math.max(0, Math.min(1, t)));
  };
}

// 标准运动曲线词典
const EASE = {
  snappy:    bezier(0.2, 0.9, 0.2, 1.0),     // 干脆利落的 UI 弹入
  overshoot: bezier(0.34, 1.56, 0.64, 1.0),  // 弹性过冲徽章
  flipCubic: bezier(0.22, 1.0, 0.36, 1.0),   // 3D 面板快翻慢停
  fly:       bezier(0.62, 0.0, 0.16, 1.0),   // 3D 空间摄像机长距离巡航
  exit:      bezier(0.4, 0.0, 1.0, 1.0)      // 加速退场 (时长取入场的 50%~60%)
};
```
