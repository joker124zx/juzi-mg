# Act II (02_s02_divergence.wav, 18.0s) — 3D Voxel + Blender + 2D MG Master Audio Engine
# Incorporates:
# - mgaudio procedural explainer bed + Foley + SFX
# - video-shotcraft S2 (Anti-machine-gun pitch/gain staircase)
# - video-shotcraft S5 (Dual-offset audio sync compensation +0.042s)
# - video-shotcraft S3 (30% restraint & pre-slam silence vacuum)
import sys, os, json
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
MG_AUDIO_LIB = os.path.abspath(os.path.join(HERE, "..", "..", "lib", "audio"))
sys.path.insert(0, MG_AUDIO_LIB)

import mgaudio as mg
from mgaudio import recipes, sfx, sync, synth, samples
from mgaudio import filters as F
from mgaudio import fx as FX

OUT_DIR = os.path.join(HERE, "out")
os.makedirs(OUT_DIR, exist_ok=True)

C = json.load(open(os.path.join(HERE, "cues.json"), encoding="utf-8"))
E = C["ev"]
DUR = float(C["duration"])
CODEC_OFFSET = float(C.get("audio_sync", {}).get("codec_offset_sec", 0.0))

# Build 18.0s Explainer Music Bed + SFX using mgaudio
m = recipes.explainer(
    duration=DUR,
    bpm=120.0,
    key="G",
    drop=E["b4_dive"],
    outro=16.50,
    music_level=-22,
    sfx_duck=3.5,
)
S = m.sfx
key_note = lambda t, i=0: m.form.chord_at(t)[i % len(m.form.chord_at(t))] + 12

def T(name, **kw):
    try:
        return m.track(name, group="sfx", **kw)
    except Exception:
        return m.track(name, **kw)

HIT = T("hit", level=-7)
HIT.insert(
    lambda x: FX.saturate(x, drive_db=8, kind="tanh"),
    lambda x: FX.compress(x, thr=-20, ratio=4, attack=0.001, release=0.08, makeup=5),
)

def slap_hit(at, gain=0, pan=0, seed=0, rr=0):
    HIT.add(sfx.sticker_slap(seed=seed), at=at, gain=gain + 3, pan=pan)
    HIT.add(samples.hit("slapstick", vel=0.88, rr=rr, maxdur=0.42), at=at, gain=gain - 1, pan=pan)

# --- BEAT 1 (0.00s - 5.45s): 现在的三大巨头早就放弃了“同质化内卷”，走上了截然不同的进化路线 ---
S(sfx.whoosh(dur=0.30, kind="air", direction=1, peak=0.45, seed=1), at=E["monolith_in"], gain=-7, pan=0.0)
S(sfx.impact(kind="punch", size=0.85, seed=2), at=E["monolith_in"] + 0.06, gain=-4, pan=0.0)
S(sfx.text_hit("pop", seed=3), at=E["title_b1"], gain=-5, pan=-0.25)

# Monolith shatters into 3 Voxel Evolution Islands!
S(sfx.riser(dur=0.55, kind="hybrid", end="cut", seed=10), at=E["monolith_shatter"] - 0.50, gain=-9)
S(sfx.impact(kind="punch", size=1.0, seed=11), at=E["monolith_shatter"], gain=-1, pan=0.0)
S(sfx.boom(dur=0.85, seed=12), at=E["monolith_shatter"], gain=-5)
S(sfx.laser("zap", seed=13), at=E["monolith_shatter"] + 0.04, gain=-8, pan=0.0)
S(sfx.whoosh(dur=0.58, kind="swish", direction=1, peak=0.45, seed=14), at=E["orbit_start"], gain=-4)

# 3 Voxel Towers build up + Blender 3D Core Cards land (S2 pitch staircase!)
pans_3 = [-0.50, 0.0, 0.50]
for i, t in enumerate(E["towers_build"]):
    # Ascending block build clicks (S2 staircase)
    for k in range(3):
        S(sfx.click("wood"), at=t + k * 0.055, gain=-9 + k, pan=pans_3[i])
    S(sfx.ding(note=key_note(t, i)), at=t + 0.14, gain=-7, pan=pans_3[i])

for i, t in enumerate(E["cards_b1"]):
    slap_hit(t, gain=-3 + i * 0.8, pan=pans_3[i], seed=20 + i, rr=i + 1)
    S(sfx.blip(note=key_note(t, i + 1), kind="sine"), at=t + 0.03, gain=-9, pan=pans_3[i])

# --- BEAT 2 (5.45s - 10.25s): 选错工具，不仅浪费订阅费，还会让你在工作流里多走弯路 ---
S(sfx.sticker_peel(dur=0.18, seed=30), at=E["b2_transition"] - 0.10, gain=-6, pan=0.0)
S(sfx.whoosh(dur=0.50, kind="swish", direction=-1, peak=0.45, seed=31), at=E["b2_transition"], gain=-3)

# Coins dropping into Lava Hopper (descending ominous blips + coin clinks)
for i, t in enumerate(E["coins_drop"]):
    S(sfx.coin(), at=t, gain=-6 + i * 0.5, pan=-0.38)
    S(sfx.pop("bubble", pitch=1.18 - i * 0.09), at=t + 0.06, gain=-7, pan=-0.38)

S(sfx.duang(pitch=0.92), at=E["waste_alarm"], gain=-3, pan=-0.35)
S(sfx.stamp("rubber", seed=40), at=E["waste_alarm"] + 0.03, gain=-4, pan=-0.35)

# Voxel Redstone Maze Detour vs Direct Shortcut Bridge
S(sfx.paper("slide", dur=0.35, seed=41), at=E["maze_detour"], gain=-7, pan=0.30)
for i, t in enumerate(E["maze_barriers"]):
    S(sfx.click("hard"), at=t, gain=-5 + i * 0.6, pan=0.25 + i * 0.08)
    S(sfx.boing(pitch=0.88 + i * 0.08), at=t + 0.02, gain=-8, pan=0.25 + i * 0.08)

# Golden Voxel Bridge snaps across!
S(sfx.whoosh(dur=0.35, kind="air", direction=1, peak=0.45, seed=48), at=E["shortcut_snap"] - 0.08, gain=-5, pan=0.30)
S(sfx.shimmer_hit(key_note(E["shortcut_snap"], 2)), at=E["shortcut_snap"], gain=-4, pan=0.30)
S(sfx.ding(note=key_note(E["shortcut_snap"], 0) + 12), at=E["shortcut_snap"] + 0.03, gain=-6, pan=0.30)

# --- BEAT 3 (10.25s - 14.68s): 今天我们就抛开枯燥的跑分榜单，直接从真实生产力场景出发 ---
S(sfx.whoosh(dur=0.48, kind="swish", direction=1, peak=0.45, seed=50), at=E["b3_transition"], gain=-3)
S(sfx.paper("flip", dur=0.25, seed=51), at=E["leaderboard_in"], gain=-6, pan=-0.25)

# HERO STAMP SLAM at 11.48s ("抛开枯燥的跑分榜单" -> 抛弃纸面跑分！)
sl = E["stamp_slam"]
S(sfx.riser(dur=0.75, kind="hybrid", end="cut", seed=60), at=sl - 0.08, gain=-7)
S(sfx.stamp("seal", seed=61), at=sl, gain=2.5, pan=0.0)
S(sfx.impact(kind="punch", size=1.0, seed=62), at=sl, gain=1.5, pan=0.0)
S(sfx.boom(dur=1.0, seed=63), at=sl, gain=-4)
slap_hit(sl, gain=-1, pan=0.0, seed=64, rr=2)

# 3B1B Process Animation: SlidingWindow + ValueFlyIn
S(sfx.paper("slide", dur=0.38, seed=70), at=E["matrix_unfold"], gain=-6, pan=0.0)
for i, t in enumerate(E["scan_steps"]):
    S(sfx.click("switch"), at=t, gain=-6 + i * 0.8, pan=pans_3[i])
    S(sfx.blip(note=key_note(t, i), kind="tri"), at=t + 0.02, gain=-8, pan=pans_3[i])

for i, t in enumerate(E["value_fly"]):
    S(sfx.swish(dur=0.20, seed=75 + i), at=t - 0.06, gain=-7, pan=pans_3[i])
    slap_hit(t, gain=-3 + i * 0.7, pan=pans_3[i], seed=80 + i, rr=i + 1)
    S(sfx.ding(note=key_note(t, i) + 12), at=t + 0.02, gain=-7, pan=pans_3[i])

# --- BEAT 4 (14.68s - 18.00s): 看看这三位顶流到底该怎么选 (One Dive Is Worth Ten Turns + R1 Hold) ---
S(sfx.whoosh(dur=0.65, kind="air", direction=1, peak=0.45, seed=90), at=E["b4_dive"], gain=-2)
S(sfx.impact(kind="soft", size=0.95, seed=91), at=E["compass_lock"], gain=-1, pan=0.0)
S(sfx.shimmer_hit(key_note(E["compass_lock"], 2)), at=E["compass_lock"], gain=-4, pan=0.0)

for i, t in enumerate(E["pillars_lock"]):
    S(sfx.click("hard"), at=t, gain=-5 + i * 0.8, pan=pans_3[i])
    S(sfx.ding(note=key_note(t, i)), at=t + 0.02, gain=-6, pan=pans_3[i])

S(sfx.pen("marker", dur=0.40, seed=99), at=E["final_hold_start"], gain=-6, pan=0.0)
# R1 Hold (16.15s - 18.00s): Zero noisy SFX! Only warm musical tail & voiceover resonance.

# Pre-slam breath at 11.48s for dramatic punch (video-shotcraft S3)
m.group("music").automate(
    "gain",
    [
        (0, 0),
        (sl - 0.12, 0),
        (sl - 0.08, -36),
        (sl - 0.005, -36),
        (sl, 0),
        (DUR, 0),
    ],
)

sfx_bgm_path = os.path.join(OUT_DIR, "sfx_bgm.wav")
res = m.export(sfx_bgm_path, lufs=-16.0, tp=-1.2, spectrogram=os.path.join(OUT_DIR, "spec.png"))
print("mgaudio bed+sfx exported:", {k: v for k, v in res.items() if k != "spectrum"})

# Mix with 02_s02_divergence.wav + S5 Dual-Offset Compensation
vo_path = os.path.abspath(os.path.join(HERE, C["voiceover"]))
bed_audio, sr = sf.read(sfx_bgm_path, dtype="float64")
vo_audio, vo_sr = sf.read(vo_path, dtype="float64")

if vo_audio.ndim == 1:
    vo_audio = np.column_stack([vo_audio, vo_audio])

if vo_sr != sr:
    target_vo_len = int(round(len(vo_audio) * sr / vo_sr))
    vo_slice = signal.resample(vo_audio, target_vo_len)
else:
    vo_slice = vo_audio

# Apply video-shotcraft S5 codec priming offset compensation if positive
offset_samples = int(round(CODEC_OFFSET * sr))
if offset_samples > 0:
    vo_slice = np.vstack([np.zeros((offset_samples, 2)), vo_slice])

if len(vo_slice) < len(bed_audio):
    pad = np.zeros((len(bed_audio) - len(vo_slice), 2))
    vo_slice = np.vstack([vo_slice, pad])
else:
    vo_slice = vo_slice[: len(bed_audio)]

# Compute voice envelope for smooth sidechain ducking of the bed
mono_vo = np.mean(np.abs(vo_slice), axis=1)
win = int(0.06 * sr)
env = np.convolve(mono_vo, np.ones(win) / win, mode="same")
speaking = np.clip((env - 0.008) / 0.04, 0.0, 1.0)
win2 = int(0.18 * sr)
speaking = np.convolve(speaking, np.ones(win2) / win2, mode="same")

duck_gain = 10.0 ** ((-4.5 * speaking) / 20.0)
mixed = vo_slice * 1.14 + bed_audio * duck_gain[:, None] * 0.82

# Fade out last 280ms and peak-limit safely
fade_len = int(0.28 * sr)
fade_curve = np.linspace(1.0, 0.0, fade_len)
mixed[-fade_len:] *= fade_curve[:, None]

peak = np.max(np.abs(mixed))
if peak > 0.92:
    mixed = mixed * (0.92 / peak)

final_wav = os.path.join(OUT_DIR, "audio.wav")
sf.write(final_wav, mixed, sr, subtype="PCM_24")
print(f"Final synced master audio written to {final_wav} (sr={sr}, len={len(mixed)/sr:.3f}s)")
