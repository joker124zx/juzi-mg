#!/usr/bin/env node
// Deterministic Frame-by-Frame 1080p MP4 Exporter (window.renderAt(t) -> ffmpeg + audio.wav)
// Usage: node scripts/render_mp4.mjs <http_url_to_index_html> <path_to_audio_wav> <output_mp4_path>
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import puppeteer from 'puppeteer-core';

const url = process.argv[2] || 'http://localhost:8765/examples/ai-showdown-hook/index.html';
const audioPath = process.argv[3] || './examples/ai-showdown-hook/out/audio.wav';
const outMp4 = process.argv[4] || './out/video.mp4';

const exe = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
].find(p => fs.existsSync(p));

const browser = await puppeteer.launch({
  executablePath: exe,
  defaultViewport: { width: 1920, height: 1080 }
});
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'networkidle0' });
await page.waitForFunction('window.__ready === true');

const demo = await page.evaluate(() => window.DEMO || { width: 1920, height: 1080, fps: 30, duration: 17 });
const fps = demo.fps || 30;
const totalFrames = Math.round(demo.duration * fps);

const ffArgs = [
  '-y',
  '-f', 'image2pipe',
  '-vcodec', 'mjpeg',
  '-r', String(fps),
  '-i', '-',
  ...(fs.existsSync(audioPath) ? ['-i', audioPath, '-c:a', 'aac', '-b:a', '192k'] : []),
  '-c:v', 'libx264',
  '-pix_fmt', 'yuv420p',
  '-crf', '16',
  '-preset', 'fast',
  outMp4
];

const ff = spawn('ffmpeg', ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });

for (let f = 0; f < totalFrames; f++) {
  const t = f / fps;
  await page.evaluate(time => window.renderAt(time), t);
  const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
  ff.stdin.write(buf);
  if (f % 30 === 0) console.log(`Rendered frame ${f}/${totalFrames} (${t.toFixed(2)}s)`);
}

ff.stdin.end();
await new Promise(res => ff.on('close', res));
await browser.close();
console.log(`MP4 export complete: ${outMp4}`);
