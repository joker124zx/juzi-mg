# MG 物理引擎、大画布摄像机与核心视觉组件代码库

本文档提供 `juzi-mg` 的核心数学函数与可复用组件实现，所有动画均基于纯函数 `renderAt(t)`。

---

## 1. 核心缓动与 AE 物理弹性函数库

```javascript
const clamp = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, u) => a + (b - a) * u;
const P = (t, a, d) => clamp((t - a) / d);
const oC = u => 1 - Math.pow(1 - u, 3);
const oQ = u => 1 - Math.pow(1 - u, 4);
const oX = u => u >= 1 ? 1 : 1 - Math.pow(2, -10 * u);
const iQ = u => u * u;
const ioC = u => u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
const ioS = u => -(Math.cos(Math.PI * u) - 1) / 2;
const oB = (u, s = 1.70158) => 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2);

// 牛顿迭代求解精确三次贝塞尔缓动
function bez(x1, y1, x2, y2) {
  return u => {
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    let t = u;
    for (let i = 0; i < 8; i++) {
      const cx = 3 * x1 * t * (1 - t) ** 2 + 3 * x2 * t * t * (1 - t) + t ** 3 - u;
      const d = 3 * x1 * (1 - t) ** 2 + 6 * (x2 - x1) * t * (1 - t) + 3 * (1 - x2) * t * t;
      if (Math.abs(d) < 1e-6) break;
      t = clamp(t - cx / d);
    }
    return 3 * y1 * t * (1 - t) ** 2 + 3 * y2 * t * t * (1 - t) + t ** 3;
  };
}
const eFly = bez(0.62, 0, 0.18, 1);     // 摄像机甩镜长尾曲线
const ePop = bez(0.34, 1.56, 0.64, 1);  // MG 经典过冲曲线

// 阻尼余振冲击响应 (Impulse Wobble)
const wob = (dt, f = 4.8, k = 10.5) => dt < 0 ? 0 : Math.exp(-k * dt) * Math.cos(2 * Math.PI * f * dt);

// 闭式弹簧与瞬时速度驱动的 Squash & Stretch (挤压与拉伸)
function spring(t, f = 2.6, z = 0.38) {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * f, a = z * w, b = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-a * t) * (Math.cos(b * t) + (a / b) * Math.sin(b * t));
}
function springV(t, f = 2.6, z = 0.38) {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * f, a = z * w, b = w * Math.sqrt(1 - z * z);
  return Math.exp(-a * t) * (w * w / b) * Math.sin(b * t);
}
function popSS(t, t0, f = 2.6, z = 0.38, amt = 0.14) {
  const dt = t - t0;
  if (dt <= 0) return { s: 0, sx: 0, sy: 0, o: 0 };
  const s = spring(dt, f, z);
  const k = clamp(springV(dt, f, z) / (2 * Math.PI * f) * amt * 2, -0.28, 0.28);
  return { s, sx: s * (1 - k * 0.65), sy: s * (1 + k), o: clamp(dt * 12) };
}

// 模切贴纸拍落物理 (悬空放大倾斜 + 深投影 -> 拍紧画布 -> 阻尼回弹)
function slap(t, land, dur = 0.18, amp = 0.34, tilt = 7) {
  const p = (t - (land - dur)) / dur;
  if (p < 0) return { o: 0, s: 1 + amp, sx: 1 + amp, sy: 1 + amp, r: tilt, lift: 1 };
  if (p < 1) {
    const L = 1 - iQ(p);
    return { o: clamp(p * 5), s: 1 + amp * L, sx: 1 + amp * L, sy: 1 + amp * L, r: tilt * L, lift: L };
  }
  const w = wob(t - land, 4.6, 10);
  return { o: 1, s: 1 - 0.04 * w, sx: 1 + 0.045 * w, sy: 1 - 0.055 * w, r: -0.9 * w, lift: 0 };
}

const shadow = (lift, base = 0.26) =>
  `drop-shadow(0 ${(7 + 32 * lift).toFixed(1)}px ${(12 + 34 * lift).toFixed(1)}px rgba(18, 28, 40, ${(base - 0.07 * lift).toFixed(3)}))`;
```

---

## 2. 大画布摄像机矩阵、落版震屏与方向性动态模糊

```javascript
function cam(t) {
  if (t <= CAM[0].t) return { ...CAM[0] };
  for (let i = 1; i < CAM.length; i++) {
    const a = CAM[i - 1], b = CAM[i];
    if (t <= b.t) {
      const u = clamp((t - a.t) / (b.t - a.t));
      const e = b.move === 'fly' ? eFly(u) : ioS(u);
      return {
        x: lerp(a.x, b.x, e),
        y: lerp(a.y, b.y, e),
        z: Math.exp(lerp(Math.log(a.z), Math.log(b.z), e)),
        r: lerp(a.r || 0, b.r || 0, e)
      };
    }
  }
  return { ...CAM[CAM.length - 1] };
}

function worldM(t, C, joltVal = 0) {
  const k = C.z, a = (C.r || 0) * Math.PI / 180;
  const cos = Math.cos(a), sin = Math.sin(a);
  const bx = -C.x * k * cos + C.y * k * sin;
  const by = -C.x * k * sin - C.y * k * cos;
  return {
    m: [k * cos, k * sin, -k * sin, k * cos, 960 + bx, 540 + by + joltVal],
    J: joltVal
  };
}

// 速度驱动的 SVG 高斯动态模糊 (绑定 #mbf 滤镜)
function camBlur(t, camEl, mbg, duration) {
  const h = 1 / 60;
  const A = cam(Math.max(0, t - h)), B = cam(Math.min(duration, t + h));
  const vx = Math.abs((A.x - B.x) * B.z) * 0.22;
  const vy = Math.abs((A.y - B.y) * B.z) * 0.22;
  if (vx + vy < 1.2) {
    camEl.style.filter = 'none';
  } else {
    mbg.setAttribute('stdDeviation', `${Math.min(5, vx).toFixed(2)} ${Math.min(14, vy).toFixed(2)}`);
    camEl.style.filter = 'url(#mbf)';
  }
}
```

---

## 3. 图形匹配转场 (Graphic Match Flight) 标准写法

当镜头从 Zone $k$ 甩向 Zone $k+1$ 时，提取 Zone $k$ 的一个徽章/标签沿抛物线飞往 Zone $k+1$：

```javascript
const uFly = eFly(P(t, tPeel, tLand - tPeel));
const arc = Math.sin(Math.PI * uFly);
const x = lerp(startX, targetX, uFly) + arc * 150;
const y = lerp(startY, targetY, uFly);
const w = wob(t - tLand, 4.8, 11) * (t >= tLand ? 1 : 0);
const sc = lerp(1.0, 1.15, arc) * (1 + 0.08 * w);
badge.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) rotate(${(arc * 12).toFixed(2)}deg) scale(${sc.toFixed(4)})`;
badge.style.filter = shadow(arc * 0.9 + 0.15);
```
