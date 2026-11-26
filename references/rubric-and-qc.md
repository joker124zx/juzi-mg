# 确定性引擎契约与双层质检规范 (F1–F5 / X1–X8 & 12 帧截图自检)

本规范定义了纯时间函数确定性渲染准则、机械硬性门禁与 7 维多帧视觉评审体系。

---

## 一、确定性渲染引擎双协议契约（Explainer MG Engine）

每一个生成的 `index.html` 必须同时暴露以下两个无副作用的纯时间函数接口，确保无头浏览器逐帧截屏与交互式预览器任意拖拽进度条时 100% 像素级复现：

```javascript
window.DEMO = { width: 1920, height: 1080, fps: 30, duration: 18.0 };
window.setVideoTime = function(tSec) {
  // 纯函数：所有 DOM / SVG / Canvas / Three.js 状态仅由 tSec 唯一决定
};
window.renderAt = async function(tSec) {
  window.setVideoTime(tSec);
};
window.__ready = true;
```

### F1–F5 机械硬性准则（Mechanical Gate）
- **F1（禁用自发播放动画）**：严禁使用不受 `tSec` 控制的 CSS `transition`、`@keyframes`、`setInterval` 或自由运行的 `requestAnimationFrame`。
- **F2（确定性随机数）**：严禁在帧循环中调用 `Math.random()` 或 `Date.now()`；所有粒子/星空/噪点坐标必须在初始化阶段使用确定性哈希 `hash(seed)` 预计算。
- **F3（90% Action-Safe 安全框）**：`1920×1080` 画布下，所有携带 `data-box` 的核心信息卡片、标题、字幕胶囊在静止可读态时，屏幕包围盒必须严格落在 `x ∈ [60, 1860], y ∈ [30, 1050]` 内。
- **F4（零包围盒碰撞）**：同一时刻处于可见态（`opacity >= 0.05` 且非 3D 堆叠子层）的同级 `data-box` 元素之间，2D 屏幕投影包围盒交集面积必须为 `0`。
- **F5（零外部遥测与零 CDN 阻塞）**：安全沙盒铁律——禁用任何外发遥测，所有渲染通过本地 Playwright + `ffmpeg` 离线完成。

---

## 二、X1–X8 视觉逐帧审计标准（Visual Frame Audit）

在运行 Playwright 采样 12 张关键帧并生成 `out/qc_sheet.jpg` 后，必须调用 `read_file` 肉眼逐格检查以下 8 项：

| 编号 | 审查项 | 一票否决红线 | 修复手段 |
| :--- | :--- | :--- | :--- |
| **X1** | **首帧即封面 (`Frame 0 Thumbnail`)** | `t = 0.0s` 或 `t = 0.5s` 一片空白/全黑 | 首帧必须已呈现主舞台或初始英雄面板 |
| **X2** | **文字防裁切与防溢出 (`No Clipping`)** | 卡片内标题/副标题最右侧字符被边框切掉或意外掉字换行 | 标题加 `white-space: nowrap`，核算 `width - padding - iconWidth >= charCount * fontSize` |
| **X3** | **3D 标注正交可读 (`Orthogonal Callouts`)** | 文字贴在 3D 大角度倾斜平面上导致透视压缩看不清 | 用 `project3D()` 将 3D 锚点投射到 2D 屏幕，拉出折线连接水平正交的 2D 标注卡 |
| **X4** | **主次视觉焦点 (`Single Hero Focus`)** | 满屏元素同时剧烈跳动，观众不知道看哪 | 运用 Manim `FocusDim` 压暗非焦点项，或用 `SceneOpen` 激光束聚焦当前口播项 |
| **X5** | **对比度与描边 (`Stroke & Contrast`)** | 浅色背景上的浅色卡片边缘糊成一片 | 浅色卡片必须配深色粗描边（`3~6px solid #1E293B`）与硬投影 |
| **X6** | **转场中点姿态 (`Mid-Transition Pose`)** | 采样转场中点帧（如 3D 翻转 `90°`、高空跃迁中点）出现穿模或乱码 | 为双面 3D 面板设置 `backface-visibility: hidden` + `90°` 刀锋高光遮罩 |
| **X7** | **音画重音咬合 (`Audio-Visual Lock`)** | 配音已经念到下一句，画面才迟迟切换 | 所有转场与重击时间戳必须从 `cues.json`（配音真实断句秒数）读取 |
| **X8** | **收尾定格留白 (`R1 Hero Hold`)** | 最后一秒还在忙乱弹卡片，观众来不及看清结论就结束了 | 最后 `1.5s–1.8s` 冻结卡片弹出，仅保留 `1.5%` 缓慢推镜 |
