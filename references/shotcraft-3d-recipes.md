# 3D 空间运镜与高光镜头源码配方库

本文件提炼整合了最核心的 **CSS 3D `preserve-3d` 空间摄像机数学公式、3D-2D 同构透视投影算子、5 大王牌 3D 镜头模板，以及 R1–R8 铁律与 S1–S5 声音哲学**。

---

## 一、核心理念：为什么这套 3D 运镜极具大片感？

- **禁止用粗糙的低模 WebGL 几何体（`BoxGeometry`）充数**：真正的科技发布会/产品大片 3D，是将**高分辨率、排版极度精致的完整 UI 面板、终端窗口与多层仪表盘（`1140×590` 至 `1600×1000`）直接放进 CSS `perspective` + `transform-style: preserve-3d` 空间**。
- **原生 1:1 矢量光栅化**：面板按真实大尺寸（如 `1240×700`）布局，再由 3D 空间矩阵整体缩放旋转，杜绝小卡片放大导致的字体模糊。

---

## 二、五大王牌 3D 镜头源码级配方

### 配方 1：逆矩阵 3D 空间摄像机 + 透视网格地面巡航（源自 `Basic3DScene.tsx` & `Terminal3D.tsx`）

- **适用文稿场景**：多终端命令行切换、多痛点工位对比、多步骤产品工作流巡航。
- **核心数学公式**：
  1. **工位空间位姿（Station Pose）**：每个 3D 窗口放在弧形空间坐标 `POSES[i] = { x, y, z, ry, rx }`。
  2. **逆矩阵摄像机（Inverse Camera Transform）**：摄像机对准某工位等价于整个 `#world` 执行该工位矩阵的**严格逆变换**，并在两工位飞行途中叠加**正弦高空拉远跃迁弧（Pull-Back Hop）**：
     $$\text{hop}(u) = \sin(\pi \cdot u^{0.85}) \times 1100\text{px}$$
  3. **3D 世界到 2D 屏幕 SVG 的同构透视投影（`project() -> toScreen()`）**：让 SVG 透视地面网格线、地面发光池与 3D DOM 窗口严丝合缝咬合。

```javascript
// 1. 逆矩阵 3D 空间摄像机计算 (源自 Terminal3D.tsx lines 69-108)
const PERSP = 1850, FLOOR_Y = 460, TILT = -4;
const POSES = [
  { x: -1350, y: -10, z: -180, ry: 22 },
  { x:  1350, y:  10, z:  180, ry: -20 }
];
const VIEW_OFFSET = [8, -8];

function camAt(t, tFlyStart, flyDur) {
  const uFly = ramp(t, tFlyStart, flyDur, EASE.swift);
  const rawFly = clamp01((t - tFlyStart) / flyDur);
  // 飞行途中拉远 1100px 形成高空俯瞰弧线 (One Dive / Pull-Back Hop)
  const hopPull = Math.sin(Math.PI * Math.pow(rawFly, 0.85)) * 1100;
  const a = POSES[0], b = POSES[1];
  const pose = {
    x: mix(a.x, b.x, uFly),
    y: mix(a.y, b.y, uFly),
    z: mix(a.z, b.z, uFly),
    ry: mix(a.ry, b.ry, uFly)
  };
  const view = mix(VIEW_OFFSET[0], VIEW_OFFSET[1], uFly);
  return { s: uFly, pull: hopPull, pose, yaw: view - pose.ry };
}

// 2. 应用到 #world (Inverse Transform)
worldEl.style.transform =
  `translateZ(${(-cam.pull).toFixed(1)}px) rotateX(${TILT}deg) rotateY(${cam.yaw.toFixed(2)}deg) ` +
  `translate3d(${(-cam.pose.x).toFixed(1)}px, ${(-cam.pose.y).toFixed(1)}px, ${(-cam.pose.z).toFixed(1)}px)`;

// 3. 3D -> 2D 屏幕同构投影 (用于绘制 SVG 透视地网与 3D 锚点连线)
function project3D(cam, p) {
  const x0 = p[0] - cam.pose.x, y0 = p[1] - cam.pose.y, z0 = p[2] - cam.pose.z;
  const ty = (cam.yaw * Math.PI) / 180, tx = (TILT * Math.PI) / 180;
  const x1 = x0 * Math.cos(ty) + z0 * Math.sin(ty);
  const z1 = -x0 * Math.sin(ty) + z0 * Math.cos(ty);
  const y2 = y0 * Math.cos(tx) - z1 * Math.sin(tx);
  const z2 = y0 * Math.sin(tx) + z1 * Math.cos(tx) - cam.pull;
  const k = PERSP / Math.max(120, PERSP - z2);
  return { x: 960 + x1 * k, y: 540 + y2 * k, z: z2, k };
}
```

---

### 配方 2：3/4 轴测五层 Z 轴爆炸分解图 + 逆序砸落合体（源自 `ExplodedView.tsx`）

- **适用文稿场景**：抛开表面看底层架构、五维评测体系拆解、技术栈分层剖析、复杂产品内部模块关系。
- **核心动作编排**：
  1. 底板以 `rotateX(52deg) rotateZ(-30deg)` 呈 3/4 轴测俯视并缓慢环绕运镜（`orbit`）；
  2. 5 个 UI 图层按 `spring(t - stagger)` 沿法线方向弹射到 `z = 120, 230, 340, 450, 560px`；
  3. 底板保留对应位置的彩色虚线插槽（Dashed Slot），且每个悬浮层在底板上投射随高度 `z` 动态扩散的模糊阴影（`blur = 10 + z * 0.08`）；
  4. 用 `project3()` 将每个悬浮层侧边中点的 3D 坐标实时投射为 2D 屏幕坐标，拉出 **SVG 折线标注（Elbow Callout Leader Lines）** 连接至左右两侧的水平标注卡（标注卡保持 2D 正交清晰可读，不随 3D 变形）；
  5. 收尾时 5 个图层按**从顶层到底层的逆序（`4 - i`）**高速砸回底板，触发 `thud = 10 * exp(-dt*9) * cos(dt*26)` 阻尼震动与 `<Sheen>` 对角高光扫掠。

```javascript
// ExplodedView.tsx 3D 层级锚点 -> 2D 屏幕折线标注投影公式
function projectAxonometric(cam, px, py, pz, W = 1360, H = 780, PERSP = 2400) {
  const X = px - W / 2, Y = py - H / 2;
  const a = (cam.rz * Math.PI) / 180, b = (cam.rx * Math.PI) / 180;
  const x1 = X * Math.cos(a) - Y * Math.sin(a);
  const y1 = X * Math.sin(a) + Y * Math.cos(a);
  const y2 = y1 * Math.cos(b) - pz * Math.sin(b);
  const z2 = y1 * Math.sin(b) + pz * Math.cos(b);
  const x4 = x1 * cam.s + cam.cx, y4 = y2 * cam.s + cam.cy;
  const k = PERSP / Math.max(200, PERSP - z2);
  return { x: 960 + x4 * k, y: 486 + y4 * k };
}
```

---

### 配方 3：3D 机械键帽重砸 + 180° 双面 3D 面板翻转 + 彩虹彗星流光管道（源自 `KeycapSmashCut.tsx` + `IntegrationHubMap.tsx`）

- **适用文稿场景**：「旧时代 vs 新范式」颠覆性反转、核心中枢分流出多条赛道/生态插件。
- **核心动作编排**：
  1. **键帽重砸（`KeycapSmashCut`）**：3D 键帽在 `0.12s`（约 3~4 帧）内急促下压 `14px`，侧面厚度阴影 `box-shadow` 从 `14px` 压缩至 `3px`，同时炸开直径 `90px -> 760px` 的脉冲冲击波环；
  2. **180° 快翻慢停（`IntegrationHubMap`）**：中央双面 `preserve-3d` 面板（正面 `rotateY(0deg)` + 背面 `rotateY(180deg)`，`backface-visibility: hidden`）使用 `EASE.flipCubic = bezier(0.22, 1, 0.36, 1)` 执行 `0° -> 180°` Y 轴翻转，并在经过 `rotY = 90°` 侧立刀锋瞬间触发 2 帧白炽边缘闪光（Edge Bloom）；
  3. **两拍式生态连通**：翻转落定后，外围能力瓷砖先弹性弹出，紧接着三层 SVG 光纤管道（发光底线 + 白色核心线 + `stroke-dashoffset` 连续流动的彗星脉冲）从瓷砖射向中央中枢。

---

### 配方 4：3D 悬浮抽卡 + 双圈周长激光扫描（源自 `SceneOpen.tsx` / `PageCam`）

- **适用文稿场景**：多选一终极选型指南、重点功能逐一高亮检视。
- **核心动作编排**：
  1. 舞台带初始 3D 倾角（`rotateX(18deg) rotateY(-12deg)`）推入正视；
  2. 被点名的卡片从虚线插槽中沿 Z 轴向上悬浮 `translateZ(75~110px)`，阴影随高度同步加深扩散；
  3. 卡片外框的 `<rect pathLength="1" stroke-dasharray="0.28 0.72">` 沿周长飞速跑过两圈高能激光束。

---

## 三、`video-shotcraft` R1–R8 动效铁律与 S1–S5 声音哲学

### R1–R8 动效铁律
- **R1（Hero Hold 落版定格）**：全片或章节收尾必须留出 `1.5s–2.0s` 的定格阅读期，期间冻结所有卡片微动，仅保留摄像机 `1.5%` 的极缓慢推镜（Camera Creep）。
- **R2（Spring Physics 弹簧优先）**：UI 组件入场优先使用二阶欠阻尼弹簧或 Newton-Raphson 精确贝塞尔曲线，禁止生硬线性插值。
- **R3（Choreographed Stagger 编排错峰）**：并列元素入场错峰间隔控制在 `0.06s–0.14s`（2~4 帧），严禁所有元素同一帧齐刷刷出现。
- **R4（Camera-First 运镜驱动）**：「一次深潜胜过十次转弯（One Dive Is Worth Ten Turns）」，用连续的 3D 空间摄像机推拉取代零碎切页。

### S1–S5 声音与音画同步铁律
- **S1（Sync Point Alignment 峰值对齐）**：`whoosh` 甩镜音效的音量峰值（而非起点）必须对齐画面运动速度最快的时刻（`peak = 0.45`）。
- **S2（Anti-Machine-Gun 防机关枪阶梯）**：连续出现的同类元素（如 3 张卡片依次弹出、5 层结构依次弹射），音效必须做音高递增（`key_note(t, i)`）与增益递增（`gain = -6 + i * 0.8`），严禁同一个采样原样连放 3 次以上。
- **S3（30% Restraint & Silence Vacuum 克制留白与暴击前抽空）**：持续背景微动保持静音；在全片最重磅的砸落/翻转前 `80~120ms`（约 3 帧），将背景音乐瞬间抽空至 `-36 dB`（Pre-slam Suck-out），制造极致的听觉冲击。
- **S5（Dual-Offset Sync Compensation 编码延迟补偿）**：AAC 编码与浏览器音频管线存在约 `1.28 帧 @ 30fps`（`+0.042s`）的启动偏移，混音导出时可通过 `codec_offset_sec: 0.042` 精确对齐。
