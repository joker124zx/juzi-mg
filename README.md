# juzi-mg (`juzi mg`)

面向 AI 编程智能体（Antigravity / Claude Code / Cursor / Codex）的**纯代码 MG 动态图形（Motion Graphics）与帧级音画同步底层引擎 Skill**。

将社区优秀的程序化动画、空间运镜与音频合成思路拆解整合，并融入实战淬炼的「反廉价 AI 俗套规则」、「确定性虚拟时钟契约」与「多帧质检门禁」，用于纯代码直出 60fps 动态图形短片、产品宣传片与科普视效。

---

## 核心模块

```text
juzi-mg/
├── SKILL.md                              # 智能体主指令与反 AI 俗套创作铁律
├── references/
│   ├── physics-and-camera.md             # 2D 大画布摄像机、弹簧物理与 Graphic Match 转场
│   ├── shotcraft-3d-recipes.md           # CSS 3D / WebGL 空间运镜公式与镜头模板
│   ├── manim-3b1b-and-motion-prompt.md   # 几何过程推导算子与缓动速率曲线
│   ├── claude-animation-base/            # p5.brush 手绘水彩晕染与 12fps 沸腾墨线参考
│   ├── pdoom-video/                      # WebGL / Canvas 高对比图版动效参考
│   ├── audio-sfx-guide.md                # 帧级拟音对齐与侧链闪避混音规范
│   └── rubric-and-qc.md                  # 纯时间函数确定性契约与多帧联排质检门禁
└── lib/
    └── audio/                            # 内置 mgaudio 合成混音库 + VCSL CC0 真实乐器无损采样 (.flac)
```

---

## 安装方式

将本仓库克隆至对应智能体的 `skills` 目录即可自动识别为 `juzi-mg`：

```bash
# Antigravity (AGY)
git clone https://github.com/joker124zx/juzi-mg.git ~/.gemini/config/skills/juzi-mg

# Claude Code
git clone https://github.com/joker124zx/juzi-mg.git ~/.claude/skills/juzi-mg
```

---

## 开源致谢与许可说明 (Credits & Licenses)

本仓库为个人实战整合与增强版 Skill 工具箱：
- 内置真实乐器无损音频采样源自 **Versilian Community Sample Library (VCSL)**（CC0 1.0 Public Domain）；
- 部分底层运镜、手绘笔刷、图版结构与 `mgaudio` 音频工具参考并整理自开源社区优秀项目（含 `mg-styles-15`、`video-shotcraft`、`ClaudeAnimationBase`、`pdoom-video` 等），各子目录保留原开源许可协议。
