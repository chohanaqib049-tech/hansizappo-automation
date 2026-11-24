import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
SCRIPT = ROOT / "content" / "narration_ur.txt"
VOICE = os.getenv("TTS_VOICE", "ur-PK-AsadNeural")
WIDTH, HEIGHT = 1920, 1080


def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    return None


def make_original_space_art(path: Path):
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        blend = y / HEIGHT
        color = (
            int(4 + 5 * blend),
            int(9 + 8 * blend),
            int(25 + 25 * blend),
        )
        for x in range(WIDTH):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image, "RGBA")
    # Original abstract star field and planet artwork; no movie footage or posters.
    import random
    random.seed(42)
    for _ in range(420):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        radius = random.choice([1, 1, 2, 3])
        alpha = random.randrange(90, 220)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                     fill=(210, 225, 255, alpha))

    draw.ellipse((1180, 180, 2050, 1050), fill=(35, 54, 105, 170))
    draw.ellipse((1280, 250, 1960, 930), fill=(8, 13, 34, 255))
    draw.ellipse((1100, 490, 2040, 700), outline=(115, 160, 230, 170), width=10)
    draw.ellipse((1120, 510, 2020, 680), outline=(70, 110, 195, 100), width=4)

    font_path = find_font()
    if font_path:
        title_font = ImageFont.truetype(font_path, 92)
        small_font = ImageFont.truetype(font_path, 34)
    else:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((110, 380), "INTERSTELLAR", font=title_font, fill=(245, 248, 255, 255))
    draw.text((118, 500), "THE HUMAN FUTURE BEYOND EARTH",
              font=small_font, fill=(170, 195, 235, 255))
    draw.text((118, 930), "HANSIZAPPO  |  ORIGINAL STORY COMMENTARY",
              font=small_font, fill=(150, 170, 205, 230))
    image.save(path, quality=95)


async def make_voice(text: str, output: Path):
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%", volume="+0%")
    await communicate.save(str(output))


def run():
    if not SCRIPT.exists():
        raise FileNotFoundError(f"Missing narration: {SCRIPT}")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg/FFprobe are required on the runner.")

    narration = SCRIPT.read_text(encoding="utf-8").strip()
    if len(narration) < 100:
        raise ValueError("Narration is too short. Add at least 100 characters.")

    audio_path = OUT / "narration.mp3"
    image_path = OUT / "original_space_art.png"
    video_path = OUT / "hansizappo_sample.mp4"

    asyncio.run(make_voice(narration, audio_path))
    make_original_space_art(image_path)

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        check=True, capture_output=True, text=True
    )
    duration = max(1, float(probe.stdout.strip()))

    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-framerate", "25", "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", "scale=1920:1080,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast",
        "-crf", "24", "-c:a", "aac", "-b:a", "160k",
        "-t", str(duration), "-shortest", "-movflags", "+faststart",
        str(video_path)
    ], check=True)

    metadata = {
        "title": "Interstellar Ki Kahani Ka Aaghaz | Roman Urdu Movie Teller",
        "description": (
            "HansiZappo par ek original Urdu-language story commentary sample. "
            "Visuals are original abstract artwork; no movie clips are used."
        ),
        "voice": VOICE,
        "duration_seconds": round(duration, 2),
        "video_file": str(video_path),
        "note": "Review voice pronunciation and video quality before enabling scheduled publishing."
    }
    (OUT / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
