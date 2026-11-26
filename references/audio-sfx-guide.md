# 真实商用采样库 + MGAudio 帧级拟音混音指南

> [!IMPORTANT]
> **优先使用真实乐器无损采样与真实影视 Foley 拟音（严禁使用廉价 `np.sin()` 正弦波冒充真实乐器）**：
> - **内置真实乐器采样库（VCSL CC0 48kHz FLAC）**：位于本技能目录 `lib/audio/samples/`（含真实定音鼓 `timpani`、鞭板 `slapstick`、木鱼 `woodblock`、大钢琴 `piano`、马林巴 `marimba`、铁琴 `glock` 等 103 个真实采样）。
> - **本地扩展拟音/BGM 目录（可选）**：若宿主环境配置了本地音效库目录（如 `$LOCAL_SFX_DIR`），优先从中选用无版权商用 BGM 与转场/气泡/弹簧/冲击真实采样。

---

## 1. 核心原则

1. **同步点即视觉事件发生时刻 (`at = event_time`)**：
   - `mgaudio` 中每个音效对象 `Sound` 自带内部 `sync` 锚点：
     - 冲击/贴纸类（`sticker_slap`, `impact`, `stamp`, `pop`, `click`）：同步点在瞬态起音处。
     - 甩镜风声（`whoosh(dur, kind, peak=0.45)`）：同步点自动对齐在**风声能量最高峰（即镜头运动速度最快的中点）**！
     - 蓄力上升（`riser(dur, kind, end='cut')`）：同步点自动对齐在**上升结束的那一帧（即重击落点）**！
2. **和声锁调 (`m.form.chord_at(t)`)**：
   - 所有带音高的 UI 提示音（`ding`, `blip`, `shimmer_hit`）必须通过 `key_note = lambda t, i=0: m.form.chord_at(t)[i % len(m.form.chord_at(t))] + 12` 取音，确保全片音效与 BGM 严丝合缝处在同一调性内。

---

## 2. 常用 MG 视觉动作与 `mgaudio.sfx` 映射表

| 视觉动作类型 | 推荐 `mgaudio` 调用组合 |
| :--- | :--- |
| **粗白边贴纸 / 2.5D 卡片拍落 (`slap`)** | `sfx.sticker_slap(seed=k)` + `samples.hit('slapstick', vel=0.88, rr=k, maxdur=0.42)` |
| **贴纸/徽章剥离起飞 (`Graphic Match Peel`)** | `sfx.sticker_peel(dur=0.18, seed=k)` + （可选）`sfx.tape_rip(dur=0.22, seed=k)` |
| **摄像机快速甩镜 (`Camera Whip Pan`)** | `sfx.whoosh(dur=0.52, kind='swish', direction=1, peak=0.45)` + `sfx.paper('flip', dur=0.22)` |
| **大标题遮罩弹起 (`Mask Title Rise`)** | `sfx.swish(dur=0.25, seed=k)` |
| **荧光马克笔划重点 (`Highlighter Sweep`)** | `sfx.pen('marker', dur=0.35, seed=k)` |
| **气泡/标签弹性弹出 (`popSS`)** | `sfx.pop('bubble', pitch=1.0 + 0.1*i)` + `sfx.blip(note=key_note(t, i), kind='sine')` |
| **王冠/角色卡通弹跳 (`Hopping / Bounce`)** | `sfx.boing(pitch=1.0 + 0.12*i)` |
| **综艺花字炸裂弹出 (`Hanazi Burst`)** | `sfx.duang(pitch=1.08)` + `sfx.pop('cork', pitch=1.15)` |
| **账单/柱状图数字滚动 (`Counter Roll`)** | 循环触发 `sfx.tick('hi')` 或 `sfx.click('wood')`，收尾加 `sfx.coin()` 或 `sfx.ding()` |
| **巨型印章粉碎暴击 (`Hero Stamp Slam`)** | 落点前 3 帧将音乐拉至 `-36 dB`，落点同时触发：`sfx.stamp('seal')` + `sfx.impact('punch')` + `sfx.boom(dur=1.1)` |

---

## 3. 口播语音自动包络闪避混音模板 (Voiceover Sidechain Ducking)

```python
import numpy as np
import soundfile as sf
from scipy import signal

bed_audio, sr = sf.read(sfx_bgm_path, dtype="float64")
vo_audio, vo_sr = sf.read(vo_path, dtype="float64")
if vo_audio.ndim == 1:
    vo_audio = np.column_stack([vo_audio, vo_audio])

# 截取对应时长并重采样至 48000 Hz
vo_slice = vo_audio[int(start_sec * vo_sr) : int((start_sec + dur_sec) * vo_sr)]
if vo_sr != sr:
    vo_slice = signal.resample(vo_slice, len(bed_audio))

# 计算人声包络，人声说话时自动将底乐压低 4.5 dB
mono_vo = np.mean(np.abs(vo_slice), axis=1)
env = np.convolve(mono_vo, np.ones(int(0.06 * sr)) / int(0.06 * sr), mode="same")
speaking = np.clip((env - 0.008) / 0.04, 0.0, 1.0)
speaking = np.convolve(speaking, np.ones(int(0.18 * sr)) / int(0.18 * sr), mode="same")

duck_gain = 10.0 ** ((-4.5 * speaking) / 20.0)
mixed = vo_slice * 1.12 + bed_audio * duck_gain[:, None] * 0.82
```
