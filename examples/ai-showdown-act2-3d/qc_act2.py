import asyncio
import os
import json
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
os.makedirs(OUT_DIR, exist_ok=True)

TIMESTAMPS = [
    (0.80, "S1a: 3D FrontPanel + Keycap Hover"),
    (1.52, "S1b: Keycap Smash + 3D Flip + Bloom"),
    (3.30, "S1c: 180deg HubPanel + Comet Pipes"),
    (5.60, "S2a: 3D Terminal #1 ($60/mo Drain)"),
    (6.95, "S2b: 3D Inverse Cam Pull-Back Flight"),
    (8.60, "S2c: 3D Terminal #2 (Workflow Ready)"),
    (10.00, "S3a: 3/4 Axonometric Baseplate"),
    (12.20, "S3b: 5-Layer Z-Exploded View + Callouts"),
    (13.85, "S3c: Slam Assembly + Sheen Sweep"),
    (14.90, "S4a: PageCam 3D Card Levitation"),
    (15.60, "S4b: Dual Perimeter Laser Scan"),
    (17.10, "S4c: 3D Hero Hold + 1.5% Cam Creep"),
]

JS_AUDIT = """
() => {
  const els = Array.from(document.querySelectorAll('[data-box]'));
  const visible = [];
  for (const el of els) {
    const st = window.getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.05) continue;
    // Also check if ancestor beat-layer is hidden
    let p = el.parentElement, hiddenParent = false;
    while (p) {
      const pst = window.getComputedStyle(p);
      if (pst.display === 'none' || pst.visibility === 'hidden' || parseFloat(pst.opacity) < 0.05) {
        hiddenParent = true; break;
      }
      p = p.parentElement;
    }
    if (hiddenParent) continue;
    const r = el.getBoundingClientRect();
    if (r.width > 2 && r.height > 2) {
      visible.push({
        id: el.getAttribute('data-box'),
        left: Math.round(r.left),
        top: Math.round(r.top),
        right: Math.round(r.right),
        bottom: Math.round(r.bottom),
        width: Math.round(r.width),
        height: Math.round(r.height)
      });
    }
  }
  const issues = [];
  for (const b of visible) {
    if (b.left < 60 || b.right > 1860 || b.top < 30 || b.bottom > 1050) {
      issues.push(`Action-safe violation on ${b.id}: [${b.left},${b.top},${b.right},${b.bottom}]`);
    }
  }
  for (let i = 0; i < visible.length; i++) {
    for (let j = i + 1; j < visible.length; j++) {
      const a = visible[i], b = visible[j];
      const ix = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
      const iy = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
      if (ix * iy > 4) {
        issues.push(`Overlap between ${a.id} and ${b.id}: ${ix}x${iy}px`);
      }
    }
  }
  return { visibleCount: visible.length, issues };
}
"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            args=["--no-sandbox", "--disable-gpu-vsync", "--force-color-profile=srgb"]
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080, "device_scale_factor": 1})
        url = "http://localhost:8765/mg-act2-3d/index.html"
        await page.goto(url, wait_until="networkidle")

        frames = []
        all_passed = True
        audit_report = []

        for idx, (t_sec, label) in enumerate(TIMESTAMPS):
            await page.evaluate(f"window.setVideoTime({t_sec})")
            await page.wait_for_timeout(40)
            res = await page.evaluate(JS_AUDIT)
            audit_report.append({"t": t_sec, "label": label, **res})
            if res["issues"]:
                all_passed = False
                print(f"[WARN] t={t_sec:.2f}s ({label}): {res['issues']}")
            else:
                print(f"[PASS] t={t_sec:.2f}s ({label}): {res['visibleCount']} boxes verified, 0 overlaps, 100% Action-Safe")

            shot_path = os.path.join(OUT_DIR, f"frame_{idx:02d}.png")
            await page.screenshot(path=shot_path)
            frames.append((shot_path, f"t={t_sec:.2f}s | {label}"))

        await browser.close()

    # Build 3x4 Contact Sheet (each thumb 640x360 -> 1920x1440)
    cols, rows = 3, 4
    tw, th = 640, 360
    sheet = Image.new("RGB", (cols * tw, rows * th), (11, 15, 21))
    draw = ImageDraw.Draw(sheet)

    for i, (fp, title) in enumerate(frames):
        im = Image.open(fp).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        cx = (i % cols) * tw
        cy = (i // cols) * th
        sheet.paste(im, (cx, cy))
        draw.rectangle([cx + tw - 310, cy + th - 30, cx + tw - 6, cy + th - 4], fill=(15, 23, 42))
        draw.text((cx + tw - 302, cy + th - 24), title, fill=(251, 191, 36))

    sheet_path = os.path.join(OUT_DIR, "qc_sheet.jpg")
    sheet.save(sheet_path, quality=92)
    with open(os.path.join(OUT_DIR, "dom_audit.json"), "w", encoding="utf-8") as f:
        json.dump({"all_passed": all_passed, "frames": audit_report}, f, indent=2, ensure_ascii=False)
    print(f"Contact sheet written to {sheet_path} (All DOM assertions passed: {all_passed})")

if __name__ == "__main__":
    asyncio.run(main())
