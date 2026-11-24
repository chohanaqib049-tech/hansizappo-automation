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


def make_card(caption, index, total, destination):
    image = Image.new("RGB", (WIDTH, HEIGHT), (5, 10, 28))
    pixels = image.load()
    for y in range(HEIGHT):
        blend = y / HEIGHT
        color = (int(5 + 8 * blend), int(10 + 10 * blend), int(28 + 30 * blend))
        for x in range(WIDTH):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image)
    for i in range(180):
        x, y = (i * 197 + 43) % WIDTH, (i * 113 + 29) % HEIGHT
        radius = 1 if i % 5 else 2
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(190, 210, 240))

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
        x = (WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), item, font=title_font, fill=(245, 248, 255))
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

        make_card(segment.get("caption", ""), index, len(segments), image_path)
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
