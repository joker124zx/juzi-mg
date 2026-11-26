#!/usr/bin/env node
// Render 12 QC keyframes from a deterministic window.renderAt(t) page and stitch a 3x4 contact sheet.
// Usage: node scripts/qc_render.mjs <url_or_dir> [duration_sec]
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import puppeteer from 'puppeteer-core';

const targetUrl = process.argv[2] || 'http://localhost:8765/examples/ai-showdown-hook/index.html';
const outDir = path.resolve(process.argv[3] || './out/qc');
fs.mkdirSync(outDir, { recursive: true });

const exe = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
].find(p => fs.existsSync(p));

const browser = await puppeteer.launch({
  executablePath: exe,
  defaultViewport: { width: 1920, height: 1080 }
});
const page = await browser.newPage();
await page.goto(targetUrl, { waitUntil: 'networkidle0' });
await page.waitForFunction('window.__ready === true');

const demo = await page.evaluate(() => window.DEMO || { duration: 17 });
const dur = Number(demo.duration || 17);
const times = Array.from({ length: 12 }, (_, i) => Number(((i + 0.35) / 12 * dur).toFixed(2)));

for (let i = 0; i < times.length; i++) {
  await page.evaluate(t => window.renderAt(t), times[i]);
  await new Promise(r => setTimeout(r, 40));
  await page.screenshot({ path: path.join(outDir, `f_${i}.jpg`), type: 'jpeg', quality: 90 });
}
await browser.close();

const pyCode = `
import cv2, numpy as np, glob, os
out_dir = r'''${outDir}'''
files = [os.path.join(out_dir, f'f_{i}.jpg') for i in range(12)]
imgs = [cv2.resize(cv2.imread(f), (640, 360)) for f in files]
rows = [np.hstack(imgs[i:i+3]) for i in range(0, 12, 3)]
sheet_path = os.path.join(os.path.dirname(out_dir), 'qc_sheet.jpg')
cv2.imwrite(sheet_path, np.vstack(rows))
print('Saved QC sheet to:', sheet_path)
`;
spawnSync('python', ['-c', pyCode], { stdio: 'inherit' });
