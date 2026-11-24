import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
WORK = OUTPUT / "segments"
VOICE_MODEL = ROOT / "models" / "ur_PK-fasih-medium.onnx"
WIDTH, HEIGHT = 1280, 720


def run(command):
    subprocess.run(command, check=True)


def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("No usable system font was found.")


def make_card(caption, visual, index, total, destination):
    image = Image.new("RGB", (WIDTH, HEIGHT), (4, 8, 24))
    pixels = image.load()
    for y in range(HEIGHT):
        blend = y / HEIGHT
        color = (int(4 + 9 * blend), int(8 + 12 * blend), int(24 + 34 * blend))
        for x in range(WIDTH):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image)
    for i in range(220):
        x, y = (i * 197 + 43) % WIDTH, (i * 113 + 29) % HEIGHT
        radius = 1 if i % 5 else 2
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(170, 195, 230))

    # Original, copyright-safe scene illustrations (not frames from the film).
    cx, cy = 930, 340
    if visual in ("earth", "ice", "wave"):
        base = {"earth": (30, 105, 180), "ice": (130, 190, 220), "wave": (20, 95, 150)}[visual]
        draw.ellipse((cx-210, cy-210, cx+210, cy+210), fill=base, outline=(170, 210, 245), width=5)
        if visual == "earth":
            draw.polygon([(790,250),(850,210),(900,260),(870,320),(810,330)], fill=(70,145,95))
            draw.polygon([(950,360),(1030,310),(1080,380),(1020,440),(960,420)], fill=(75,150,100))
            draw.arc((cx-245,cy-245,cx+245,cy+245), 205, 335, fill=(210,225,245), width=10)
        elif visual == "ice":
            for k in range(5):
                x = 790 + k*65
                draw.polygon([(x,520),(x+35,390-k*15),(x+70,520)], fill=(190,225,240))
        else:
            draw.rectangle((0,430,WIDTH,HEIGHT), fill=(8,45,85))
            for k in range(3):
                y = 450 + k*55
                draw.arc((560-k*50,y-90,1300+k*20,y+110), 190, 350, fill=(110,190,225), width=14)
    elif visual in ("wormhole", "blackhole", "tesseract"):
        for radius, color, width in [(220,(75,115,210),10),(175,(130,100,220),8),(125,(190,145,245),6)]:
            draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius), outline=color, width=width)
        draw.ellipse((cx-78,cy-78,cx+78,cy+78), fill=(0,0,5))
        if visual == "blackhole":
            draw.ellipse((cx-245,cy-70,cx+245,cy+70), outline=(245,160,80), width=22)
            draw.ellipse((cx-95,cy-95,cx+95,cy+95), fill=(0,0,4))
        if visual == "tesseract":
            draw.line((cx-145,cy-145,cx+145,cy+145), fill=(180,205,255), width=5)
            draw.line((cx+145,cy-145,cx-145,cy+145), fill=(180,205,255), width=5)
            draw.rectangle((cx-145,cy-145,cx+145,cy+145), outline=(180,205,255), width=5)
    elif visual in ("nasa", "station"):
        draw.ellipse((cx-150,cy-150,cx+150,cy+150), outline=(90,145,220), width=5)
        draw.ellipse((cx-90,cy-90,cx+90,cy+90), outline=(90,145,220), width=3)
        draw.line((cx-260,cy,cx+260,cy), fill=(125,175,230), width=5)
        draw.line((cx,cy-220,cx,cy+220), fill=(125,175,230), width=5)
        if visual == "station":
            draw.rectangle((cx-270,cy-38,cx+270,cy+38), fill=(160,180,205), outline=(235,240,250), width=4)
            draw.rectangle((cx-360,cy-100,cx-275,cy+100), outline=(90,150,220), width=5)
            draw.rectangle((cx+275,cy-100,cx+360,cy+100), outline=(90,150,220), width=5)
    elif visual == "messages":
        for k in range(3):
            x = 650 + k*185
            draw.rounded_rectangle((x,220,x+155,430), radius=14, outline=(120,175,230), width=5, fill=(12,28,55))
            draw.ellipse((x+48,250,x+108,310), fill=(110,145,190))
            draw.rectangle((x+28,330,x+128,385), fill=(45,80,125))
    elif visual == "watch":
        draw.ellipse((cx-150,cy-150,cx+150,cy+150), outline=(220,190,115), width=16)
        draw.ellipse((cx-125,cy-125,cx+125,cy+125), outline=(220,190,115), width=4)
        draw.line((cx,cy,cx-20,cy-90), fill=(245,235,210), width=8)
        draw.line((cx,cy,cx+85,cy+25), fill=(245,235,210), width=6)
        draw.ellipse((cx-12,cy-12,cx+12,cy+12), fill=(245,235,210))
    else:
        draw.ellipse((cx-180,cy-180,cx+180,cy+180), fill=(40,75,135), outline=(170,200,240), width=5)

    font_path = find_font()
    title_font = ImageFont.truetype(font_path, 54)
    small_font = ImageFont.truetype(font_path, 25)
    words, lines, line = (caption.strip() or "Movie Teller").split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=title_font)[2] > 1080 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)

    heights = [draw.textbbox((0, 0), item, font=title_font)[3] for item in lines]
    y = (HEIGHT - sum(heights) - max(0, len(lines)-1) * 18) // 2
    for item, line_height in zip(lines, heights):
        box = draw.textbbox((0, 0), item, font=title_font)
        draw.text((64, y), item, font=title_font, fill=(245, 248, 255))
        y += line_height + 18

    draw.text((48, HEIGHT - 58), f"HANSIZAPPO  |  {index:02d}/{total:02d}",
              font=small_font, fill=(145, 170, 205))
    image.save(destination)

def make_voice(text, destination):
    if not VOICE_MODEL.exists():
        raise FileNotFoundError(f"Urdu Piper voice model missing: {VOICE_MODEL}")
    run([
        sys.executable, "-m", "piper",
        "-m", str(VOICE_MODEL),
        "-f", str(destination),
        "--", text
    ])


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/build_video.py episodes/episode-001.json")

    script_path = Path(sys.argv[1])
    if not script_path.is_absolute():
        script_path = ROOT / script_path
    data = json.loads(script_path.read_text(encoding="utf-8"))
    segments = data.get("segments", [])
    if not segments:
        raise SystemExit("The episode JSON must contain at least one segment.")

    OUTPUT.mkdir(exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    rendered = []

    for index, segment in enumerate(segments, start=1):
        narration = segment.get("text_urdu", "").strip()
        if not narration:
            raise SystemExit(
                f"Segment {index} has no text_urdu. Piper Urdu requires Urdu-script narration."
            )
        image_path = WORK / f"card-{index:03d}.png"
        audio_path = WORK / f"voice-{index:03d}.wav"
        video_path = WORK / f"part-{index:03d}.mp4"

        make_card(segment.get("caption", ""), segment.get("visual", "space"), index, len(segments), image_path)
        make_voice(narration, audio_path)
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p", "-shortest", "-r", "25", str(video_path)
        ])
        rendered.append(video_path)

    concat_file = WORK / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.as_posix()}'\n" for path in rendered),
        encoding="utf-8"
    )
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "-", data.get("title", "movie-teller")).strip("-")
    final_path = OUTPUT / f"{safe_title or 'movie-teller'}.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", str(final_path)
    ])
    print(f"VIDEO_READY={final_path}")


if __name__ == "__main__":
    main()
