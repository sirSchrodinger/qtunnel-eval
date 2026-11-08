#!/usr/bin/env python3
"""Build the walkthrough video: slides (HTML -> PNG with a headless browser) + narration (Piper TTS) -> MP4 (ffmpeg).
Usage: python build_video.py slides.json out.mp4   (slides.json: [{"html": "<div>..</div>", "say": "narration"}, ...])
Needs: piper-tts voice file at $PIPER_VOICE, a Chromium-based browser at $BROWSER, ffmpeg."""
import json, os, subprocess, sys, tempfile, wave
sys.path.insert(0, "/usr/lib/python3/dist-packages")
from playwright.sync_api import sync_playwright
from piper import PiperVoice

CSS = """
html,body{margin:0;width:1280px;height:720px;background:#0f1720;color:#e8eef4;font-family:'DejaVu Sans',Arial,sans-serif}
.s{box-sizing:border-box;width:1280px;height:720px;padding:54px 70px;position:relative}
h1{font-size:52px;line-height:1.15;margin:0 0 22px;color:#fff} h2{font-size:40px;margin:0 0 24px;color:#7cc4ff}
p,li{font-size:29px;line-height:1.38;margin:8px 0} ul{padding-left:30px;margin:6px 0}
.sub{color:#9fb3c8;font-size:26px} .acc{color:#ffd166} .bad{color:#ff7b7b} .ok{color:#7be0a0}
table{border-collapse:collapse;font-size:25px;margin-top:10px} td,th{border-bottom:1px solid #2c3b4d;padding:8px 16px;text-align:left}
th{color:#7cc4ff} code,pre{font-family:'DejaVu Sans Mono',monospace;background:#18232f;border-radius:6px;padding:2px 8px;font-size:23px}
pre{padding:14px 18px;font-size:22px;line-height:1.35;white-space:pre-wrap}
.foot{position:absolute;left:70px;bottom:26px;color:#6f8399;font-size:20px}
"""

def main():
    slides = json.load(open(sys.argv[1])); out = os.path.abspath(sys.argv[2])
    voice = PiperVoice.load(os.environ.get("PIPER_VOICE", "/tmp/voices/en_US-lessac-medium.onnx"))
    tmp = tempfile.mkdtemp(prefix="vid.")
    parts = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get("BROWSER", "/opt/brave.com/brave/brave"), headless=True,
                               args=["--no-sandbox", "--disable-gpu"])
        pg = br.new_page(viewport={"width": 1280, "height": 720})
        for i, s in enumerate(slides):
            pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='s'>{s['html']}"
                           f"<div class='foot'>QTunnel-Eval &middot; micro1 Eval Hackathon &middot; {i+1}/{len(slides)}</div></div></body></html>")
            png = f"{tmp}/s{i:02d}.png"; pg.screenshot(path=png)
            wav = f"{tmp}/s{i:02d}.wav"
            with wave.open(wav, "wb") as w:
                voice.synthesize_wav(s["say"], w)
            dur = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]).decode().strip()
            seg = f"{tmp}/seg{i:02d}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "5", "-i", png, "-i", wav,
                            "-af", "apad=pad_dur=0.6", "-t", str(float(dur) + 0.6), "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "128k", seg], check=True)
            parts.append(seg); print(f"slide {i+1}: {float(dur):.1f}s narration")
        br.close()
    lst = f"{tmp}/list.txt"; open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    tot = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).decode().strip()
    print("video:", out, f"{float(tot):.0f}s", f"{os.path.getsize(out)/1e6:.1f} MB")

if __name__ == "__main__":
    main()
