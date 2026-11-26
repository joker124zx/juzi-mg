---
name: juzi-mg
description: >-
  底层 MG 动态图形与音视频引擎参考库（juzi-mg），涵盖 WebGL/Canvas 动态图版、p5.brush 手绘水彩与沸腾墨线、
  3D 空间运镜公式、mgaudio 真实乐器采样库与 2D 大画布摄像机、Manim 过程推导算子及多帧确定性质检规范。
---

# Juzi MG Engine (`juzi-mg`)

本目录整合了程序化动态图形、手绘/WebGL 渲染参考与真实乐器音频采样库。在调用任何技术配方前，必须先遵守以下创作准则：

## 一、核心审美与叙事准则（剔除廉价 AI 俗套）

1. **具象叙事，拒绝「配图式符号」与「字面看图说话」**：
   - 屏上的主体必须叫得出具体名字、长得像它本身（禁止拿抽象的点、线、圆圈、发光方块加文字标签充当画面主体，也禁止看到“发条”就画齿轮、看到“心跳”就画心电图）。
   - 每一镜必须有一个明确的**动词**，变化本身就是叙事，不参与叙事的装饰全是噪音。
2. **彻底剔除廉价 AI 视频俗套（Banned Defaults）**：
   - **严禁**无意义的四角 HUD 边框、假状态栏、英文参数小字、扫描线与乱飞的凑数粒子；
   - **严禁**把所有 3D 场景做成“黑底 + 刺眼 Bloom 辉光 + 几个基础几何体（Box/Cylinder/Sphere）原地旋转”；
   - **严禁**把参考片或示例库里的画面直接换皮照搬（Don't reskin examples），每部作品必须提炼属于它自己的**唯一核心视觉母题（One Sayable Device）**，一以贯之。
3. **先立剧本与分镜，再写底层代码**：
   - 绝不一边算坐标一边现编故事。动手写渲染代码前，必须先明确：一句话母题、因果闭合的分镜表（遮住字幕光看画面动作也能看懂故事）、统一色盘（每种主色在全片只代表一个含义）。

---

## 二、本地内置核心模块与参考目录

按需读取对应子目录中的源码与文档，切勿生搬硬套：

```text
juzi-mg/
├── references/
│   ├── claude-animation-base/        # p5.brush 水彩晕染 + 12fps 沸腾墨线角色动画 (core.js, clawd.js, ANIMATION_GUIDE.md)
│   ├── pdoom-video/                  # WebGL/Canvas 图版引擎 (TREATMENT.md, ENGINE.md, stroke.ts 单笔画, scene_loss.ts, scene_hook.ts)
│   ├── shotcraft-3d-recipes.md       # 3D 空间运镜公式 (InverseCam, Terminal3D, ExplodedView, HubFlip, PageCam) 与帧级拟音
│   ├── physics-and-camera.md         # 2D 大画布摄像机、弹簧物理与 Graphic Match 转场
│   ├── manim-3b1b-and-motion-prompt.md # Manim 过程推导算子 (SlidingWindow, Circumscribe, FocusDim) 与速率曲线
│   ├── audio-sfx-guide.md            # mgaudio 合成器与人声侧链闪避指南
│   └── rubric-and-qc.md              # 确定性机械门禁与多帧联排视觉质检规范
└── lib/
    └── audio/                        # 内置 mgaudio 合成器 + VCSL 真实乐器采样库 (samples/ 马林巴、颤音琴、钢琴、弦乐拨奏等 .flac)
```
