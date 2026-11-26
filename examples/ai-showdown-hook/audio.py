# AI Model Showdown (0-17s Hook) 鈥?marimba explainer bed + frame-accurate MG SFX + voiceover mix
import sys, os, json
import numpy as np
import soundfile as sf
from scipy import signal

MG_AUDIO_LIB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib", "audio"))
sys.path.insert(0, MG_AUDIO_LIB)

import mgaudio as mg
from mgaudio import recipes, sfx, sync, synth, samples
from mgaudio import filters as F
from mgaudio import fx as FX

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
os.makedirs(OUT_DIR, exist_ok=True)

C = json.load(open(os.path.join(HERE, "cues.json"), encoding="utf-8"))
E = C["ev"]
DUR = float(C["duration"])

# 1. Build 17s Explainer Music Bed + SFX using mgaudio
m = recipes.explainer(duration=DUR, bpm=118.0, key="D", drop=13.38, outro=15.85, music_level=-22, sfx_duck=3.5)
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

# --- ZONE A (0.00s - 1.84s): 姣忓ぉ閮芥湁浜洪棶鎴?---
S(sfx.swish(dur=0.18, seed=1), at=0.04, gain=-10, pan=-0.35)
slap_hit(E["host_land"], gain=-4, pan=-0.35, seed=11, rr=1)
S(sfx.click("soft"), at=E["kicker"], gain=-9, pan=0.15)
S(sfx.swish(dur=0.25, seed=2), at=E["title1"] + 0.08, gain=-8, pan=0.2)
S(sfx.swish(dur=0.25, seed=3), at=E["title2"] + 0.08, gain=-8, pan=0.2)

bubble_pans = [-0.45, -0.15, -0.4]
for i, t in enumerate(E["bubbles"]):
    S(sfx.pop("bubble", pitch=1.0 + 0.1 * i), at=t, gain=-5, pan=bubble_pans[i])
    S(sfx.blip(note=key_note(t, i), kind="sine"), at=t + 0.02, gain=-12, pan=bubble_pans[i])

S(sfx.pen("marker", dur=0.34, seed=4), at=E["marker_a"][0] + 0.05, gain=-8, pan=0.25)

# Graphic Match #1: Question badge peels and camera whips to Zone B
S(sfx.sticker_peel(dur=0.16, seed=30), at=E["q_peel"], gain=-7, pan=0.0)
S(sfx.whoosh(dur=0.52, kind="swish", direction=1, peak=0.45, seed=31), at=1.95, gain=-3)
S(sfx.paper("flip", dur=0.22, seed=32), at=1.92, gain=-7, pan=0.2)
S(sfx.click("wood"), at=E["q_land"], gain=-6, pan=0.0)

# --- ZONE B (1.84s - 8.02s): Gemini, Claude, ChatGPT 鍒板簳鍝釜鏈€寮猴紵鎴戣鍏呭摢涓€涓紵 ---
card_pans = [-0.48, 0.0, 0.48]
for i, t in enumerate(E["cards_land"]):
    slap_hit(t, gain=-3, pan=card_pans[i], seed=40 + i, rr=i + 2)
    S(sfx.ding(note=key_note(t, i)), at=t + 0.02, gain=-9, pan=card_pans[i])

for i, t in enumerate(E["leaders"]):
    S(sfx.click("switch"), at=t, gain=-10, pan=card_pans[i])
    S(sfx.blip(note=key_note(t, i + 1), kind="tri"), at=t + 0.08, gain=-12, pan=card_pans[i])

# VS lightning & Crown hops ("鍒板簳鍝釜鏈€寮猴紵")
S(sfx.laser("zap", seed=50), at=E["vs_bolt"], gain=-10, pan=0.0)
for i, t in enumerate(E["crown_hops"]):
    S(sfx.boing(pitch=1.0 + 0.12 * i), at=t, gain=-6, pan=card_pans[i])

S(sfx.text_hit("pop", seed=55), at=E["strong_title"], gain=-4, pan=0.0)

# Subscription Bill & Counter ("鎴戣鍏呭摢涓€涓紵")
S(sfx.whoosh(dur=0.32, kind="air", direction=0, peak=0.45, seed=59), at=6.52, gain=-9)
slap_hit(E["bill_land"], gain=-4, pan=-0.15, seed=60, rr=1)
for i, t in enumerate(E["bill_ticks"]):
    S(sfx.tick("hi"), at=t, gain=-7 + i, pan=-0.1)
    if i == len(E["bill_ticks"]) - 1:
        S(sfx.coin(), at=t + 0.02, gain=-6, pan=0.05)

# Hanazi pop ("閽卞寘椤朵笉浣?! 馃捀")
S(sfx.duang(pitch=1.08), at=E["hanazi_pop"], gain=-4, pan=0.38)
S(sfx.pop("cork", pitch=1.15), at=E["hanazi_pop"] + 0.03, gain=-6, pan=0.38)

# Graphic Match #2: Price tags peel and camera whips to Zone C
S(sfx.sticker_peel(dur=0.20, seed=75), at=E["tags_peel"], gain=-6, pan=0.0)
S(sfx.tape_rip(dur=0.22, seed=76), at=E["tags_peel"] + 0.03, gain=-11, pan=-0.2)
S(sfx.whoosh(dur=0.55, kind="swish", direction=1, peak=0.45, seed=77), at=8.13, gain=-3)
S(sfx.paper("flip", dur=0.22, seed=78), at=8.10, gain=-7, pan=-0.2)

# --- ZONE C (8.02s - 12.88s): 鈥滄煇涓€涓ā鍨嬪湪鎵€鏈夐鍩熷悐鎵撳叾浠栦袱涓€?-> 浼懡棰樼洊绔犵矇纰?---
S(sfx.paper("slide", dur=0.40, seed=80), at=E["myth_board"], gain=-9, pan=0.0)
S(sfx.click("hard"), at=E["tags_land"], gain=-5, pan=0.0)

for i, t in enumerate(E["myth_bars"]):
    S(sfx.click("wood"), at=t, gain=-8 + i, pan=-0.3 + 0.2 * i)
    S(sfx.blip(note=key_note(t, i), kind="sine"), at=t + 0.05, gain=-10, pan=-0.3 + 0.2 * i)
    for k in range(3):
        S(sfx.tick("hi"), at=t + 0.06 + k * 0.06, gain=-13, pan=-0.3 + 0.2 * i)

S(sfx.shimmer_hit(key_note(E["myth_claim"], 2)), at=E["myth_claim"], gain=-7, pan=0.3)

# Anticipation riser + HERO STAMP SLAM at 11.65s ("鍚婃墦鍏朵粬涓や釜")
S(sfx.riser(dur=0.85, kind="hybrid", end="cut", seed=90), at=E["stamp_slam"] - 0.07, gain=-8)
S(sfx.stamp("seal", seed=91), at=E["stamp_slam"], gain=2, pan=0.0)
S(sfx.impact(kind="punch", size=1.0, seed=92), at=E["stamp_slam"], gain=1, pan=0.0)
S(sfx.boom(dur=1.1, seed=93), at=E["stamp_slam"], gain=-4)
slap_hit(E["stamp_slam"], gain=-1, pan=0.05, seed=94, rr=3)
S(sfx.pen("marker", dur=0.35, seed=95), at=E["cross_draw"][0], gain=-6, pan=-0.2)
S(sfx.pen("marker", dur=0.32, seed=96), at=E["cross_draw"][0] + 0.14, gain=-6, pan=0.2)

# --- ZONE D (12.88s - 17.00s): 鐪熷疄宸ヤ綔娴佷笁澶ц禌閬撶煩闃?---
S(sfx.sticker_peel(dur=0.22, seed=100), at=E["orbs_peel"], gain=-6, pan=0.0)
S(sfx.whoosh(dur=0.62, kind="air", direction=0, peak=0.45, seed=101), at=13.06, gain=-3)

for i, t in enumerate(E["orbs_land"]):
    slap_hit(t, gain=-4, pan=card_pans[i], seed=110 + i, rr=i + 1)
    S(sfx.ding(note=key_note(t, i)), at=t, gain=-7, pan=card_pans[i])

for i, t in enumerate(E["workflow_badges"]):
    S(sfx.stamp("rubber", seed=120 + i), at=t, gain=-5, pan=card_pans[i])
    S(sfx.click("switch"), at=t + 0.02, gain=-9, pan=card_pans[i])

S(sfx.impact(kind="soft", size=0.9, seed=130), at=E["hero_banner"], gain=-2)
S(sfx.shimmer_hit(key_note(E["hero_banner"], 2)), at=E["hero_banner"], gain=-5)
S(sfx.pen("marker", dur=0.42, seed=131), at=E["marker_d"][0], gain=-7, pan=0.1)

# Pre-slam breath at 11.65s for dramatic punch
sl = E["stamp_slam"]
m.group("music").automate(
    "gain",
    [
        (0, 0),
        (sl - 0.10, 0),
        (sl - 0.07, -36),
        (sl - 0.005, -36),
        (sl, 0),
        (DUR, 0),
    ],
)

sfx_bgm_path = os.path.join(OUT_DIR, "sfx_bgm.wav")
res = m.export(sfx_bgm_path, lufs=-16.0, tp=-1.2, spectrogram=os.path.join(OUT_DIR, "spec.png"))
print("mgaudio bed+sfx exported:", {k: v for k, v in res.items() if k != "spectrum"})

# 2. Mix with optional clean Voiceover (`assets/voiceover.wav`)
vo_path = os.path.join(HERE, "assets", "voiceover.wav")
bed_audio, sr = sf.read(sfx_bgm_path, dtype="float64")
vo_audio, vo_sr = sf.read(vo_path, dtype="float64")

if vo_audio.ndim == 1:
    vo_audio = np.column_stack([vo_audio, vo_audio])

# Slice first DUR seconds of VO and resample to sr (48000 Hz) if needed
vo_samples_needed = int(DUR * vo_sr)
vo_slice = vo_audio[:vo_samples_needed]
if vo_sr != sr:
    vo_slice = signal.resample(vo_slice, len(bed_audio))
else:
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

# Duck bed slightly (-4.5 dB when speaking, keeping SFX transients audible)
duck_gain = 10.0 ** ((-4.5 * speaking) / 20.0)
mixed = vo_slice * 1.12 + bed_audio * duck_gain[:, None] * 0.82

# Fade out last 250ms and peak-limit safely
fade_len = int(0.25 * sr)
fade_curve = np.linspace(1.0, 0.0, fade_len)
mixed[-fade_len:] *= fade_curve[:, None]

peak = np.max(np.abs(mixed))
if peak > 0.92:
    mixed = mixed * (0.92 / peak)

final_wav = os.path.join(OUT_DIR, "audio.wav")
sf.write(final_wav, mixed, sr, subtype="PCM_24")
print(f"Final synced master audio written to {final_wav} (sr={sr}, len={len(mixed)/sr:.3f}s)")

