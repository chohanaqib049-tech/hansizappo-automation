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
MARS_BROLL = ROOT / "assets" / "mars-rover-hazcam.mp4"
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

    elif visual in ("mars", "astronaut", "habitat", "storm", "rover", "farm", "rescue", "ship", "sunrise"):
        # Original illustrated Mars environments; no film stills or actor likenesses.
        mars = (150, 62, 38)
        draw.ellipse((cx-300, cy-245, cx+300, cy+355), fill=mars, outline=(225,145,105), width=6)
        draw.ellipse((cx-340, cy+185, cx+340, cy+390), fill=(92,38,30))
        for k in range(12):
            x = 610 + (k*83)%650
            y = 440 + (k*47)%220
            draw.ellipse((x,y,x+18,y+8), fill=(185,105,75))
        if visual == "mars":
            draw.ellipse((cx-90,cy-120,cx+80,cy+30), fill=(225,155,105))
            draw.arc((cx-300,cy-250,cx+300,cy+350), 205, 335, fill=(245,190,150), width=8)
        elif visual == "astronaut":
            draw.ellipse((cx-72,cy-190,cx+72,cy-46), fill=(205,215,220), outline=(245,245,245), width=7)
            draw.rounded_rectangle((cx-105,cy-55,cx+105,cy+215), radius=55, fill=(190,200,205), outline=(245,245,245), width=7)
            draw.ellipse((cx-48,cy-168,cx+48,cy-72), fill=(20,45,65))
            draw.line((cx-80,cy+10,cx-180,cy+130), fill=(210,220,225), width=28)
            draw.line((cx+80,cy+10,cx+180,cy+130), fill=(210,220,225), width=28)
        elif visual == "habitat":
            draw.polygon([(cx-245,cy+180),(cx-170,cy-25),(cx+170,cy-25),(cx+245,cy+180)], fill=(105,125,135), outline=(230,230,220))
            draw.rectangle((cx-200,cy+45,cx+200,cy+180), fill=(55,75,85), outline=(220,225,220), width=7)
            draw.ellipse((cx-55,cy+55,cx+55,cy+165), fill=(35,90,65), outline=(175,205,160), width=5)
        elif visual == "storm":
            for k in range(9):
                x = 520 + k*95
                draw.arc((x,cy-220,x+340,cy+250), 190, 350, fill=(205,115,75), width=24)
            draw.polygon([(0,430),(WIDTH,350),(WIDTH,HEIGHT),(0,HEIGHT)], fill=(125,55,35))
        elif visual == "rover":
            draw.ellipse((cx-170,cy+95,cx-65,cy+200), fill=(30,35,40), outline=(210,210,200), width=7)
            draw.ellipse((cx+65,cy+95,cx+170,cy+200), fill=(30,35,40), outline=(210,210,200), width=7)
            draw.rounded_rectangle((cx-185,cy-10,cx+185,cy+115), radius=28, fill=(175,185,175), outline=(240,240,225), width=7)
            draw.rectangle((cx-90,cy-115,cx+90,cy-10), fill=(90,135,155), outline=(230,230,220), width=6)
            draw.line((cx,cy-115,cx+85,cy-235), fill=(220,225,220), width=9)
        elif visual == "farm":
            draw.rectangle((cx-210,cy-90,cx+210,cy+200), fill=(28,65,48), outline=(180,205,170), width=8)
            for k in range(6):
                x = cx-165+k*65
                draw.line((x,cy+155,x,cy-15), fill=(90,180,95), width=12)
                draw.ellipse((x-34,cy-30,x+5,cy+18), fill=(110,195,105))
                draw.ellipse((x+3,cy+20,x+42,cy+65), fill=(85,160,85))
        elif visual == "rescue":
            draw.ellipse((cx-115,cy-115,cx+115,cy+115), fill=(75,100,135), outline=(230,230,230), width=7)
            draw.polygon([(cx-300,cy+20),(cx-80,cy-40),(cx+290,cy+35),(cx+70,cy+95)], fill=(185,195,205), outline=(245,245,245))
            draw.line((cx-280,cy-90,cx-125,cy-35), fill=(225,225,225), width=12)
        elif visual == "ship":
            draw.polygon([(cx,cy-245),(cx-95,cy+120),(cx,cy+205),(cx+95,cy+120)], fill=(190,200,210), outline=(245,245,245))
            draw.rectangle((cx-65,cy-40,cx+65,cy+55), fill=(70,125,155), outline=(245,245,245), width=6)
            draw.polygon([(cx-95,cy+100),(cx-190,cy+185),(cx-70,cy+160)], fill=(190,90,45))
            draw.polygon([(cx+95,cy+100),(cx+190,cy+185),(cx+70,cy+160)], fill=(190,90,45))
        elif visual == "sunrise":
            draw.ellipse((cx-180,cy-180,cx+180,cy+180), fill=(245,170,95))
            draw.rectangle((0,cy+80,WIDTH,HEIGHT), fill=(75,34,29))
            draw.polygon([(0,cy+100),(280,cy-30),(500,cy+100),(780,cy-20),(WIDTH,cy+90),(WIDTH,HEIGHT),(0,HEIGHT)], fill=(105,48,36))
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


def probe_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True
    )
    return float(result.stdout.strip())


def choose_visual(sentence, fallback):
    rules = [
        (("طوفان", "گرد", "دھول", "آندھی"), "storm"),
        (("خلائی جہاز", "راکٹ", "جہاز", "لانچ"), "ship"),
        (("آلو", "فصل", "پود", "کھاد", "کھیتی", "خوراک"), "farm"),
        (("ناسا", "سائنس دان", "زمین", "دنیا"), "nasa"),
        (("روور", "کیمرہ", "رابطہ", "پیغام", "تصویر"), "rover"),
        (("ہیبی ٹیٹ", "رہائشی مرکز", "مرکز", "گھر"), "habitat"),
        (("بچاؤ", "بچانے", "امداد", "ساتھی", "عملے", "کمانڈر"), "rescue"),
        (("خلا باز", "مارک", "لباس", "زخم", "اکیلا"), "astronaut"),
        (("مریخ", "سیارہ", "صحرا", "سرخ مٹی"), "mars"),
    ]
    for words, visual in rules:
        if any(word in sentence for word in words):
            return visual
    return fallback if fallback in {"mars", "astronaut", "habitat", "storm", "rover", "farm", "rescue", "ship", "sunrise"} else "mars"


def scene_label(visual):
    return {
        "mars": "MARS KA MANZAR", "astronaut": "AKELA ASTRONAUT",
        "habitat": "REHAISHI MARKAZ", "storm": "MARS KA TOOFAN",
        "rover": "ROVER AUR RABTA", "farm": "MARS PAR KHETI",
        "rescue": "BACHAO KA MISSION", "ship": "KHALAI JAHAAZ",
        "sunrise": "UMEED KI KIRAN",
    }.get(visual, "MOVIE TELLER")


def render_visual_story(segment, index, total, narration, audio_path):
    # Split the narration into sentence-led shots so the image changes with the spoken story.
    sentences = [part.strip() for part in re.split(r"(?<=[۔!?؟])\s*", narration) if part.strip()]
    if not sentences:
        sentences = [narration]
    duration = probe_duration(audio_path)
    weights = [max(1, len(part)) for part in sentences]
    total_weight = sum(weights)
    shot_paths = []
    elapsed = 0.0

    for shot_no, sentence in enumerate(sentences, start=1):
        shot_duration = duration - elapsed if shot_no == len(sentences) else duration * weights[shot_no-1] / total_weight
        elapsed += shot_duration
        visual = choose_visual(sentence, segment.get("visual", "mars"))
        image_path = WORK / f"shot-{index:03d}-{shot_no:02d}.png"
        video_path = WORK / f"shot-{index:03d}-{shot_no:02d}.mp4"

        # Genuine NASA Curiosity rover-camera footage is used only for rover scenes.
        # It is labelled on screen and is not presented as footage from The Martian.
        if visual == "rover" and MARS_BROLL.exists():
            font_path = find_font()
            video_filter = (
                f"scale=1280:720:force_original_aspect_ratio=increase,"
                f"crop=1280:720,"
                f"drawtext=fontfile={font_path}:text='REAL MARS ROVER CAMERA':"
                "fontcolor=white:fontsize=38:box=1:boxcolor=black@0.55:"
                "boxborderw=14:x=48:y=42,"
                f"drawtext=fontfile={font_path}:text='NASA/JPL-Caltech':"
                "fontcolor=white:fontsize=22:box=1:boxcolor=black@0.45:"
                "boxborderw=8:x=48:y=h-62"
            )
            run([
                "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(MARS_BROLL),
                "-t", f"{shot_duration:.3f}", "-vf", video_filter,
                "-an", "-r", "25", "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "22", "-pix_fmt", "yuv420p", str(video_path)
            ])
            shot_paths.append(video_path)
            continue

        make_card(scene_label(visual), visual, index, total, image_path)
        frames = max(1, round(shot_duration * 25))
        run([
            "ffmpeg", "-y", "-loop", "1", "-framerate", "25", "-i", str(image_path),
            "-frames:v", str(frames),
            "-vf", "zoompan=z='min(zoom+0.0008,1.07)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1280x720:fps=25,format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(video_path)
        ])
        shot_paths.append(video_path)

    concat_file = WORK / f"shots-{index:03d}.txt"
    concat_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in shot_paths), encoding="utf-8")
    silent_path = WORK / f"silent-{index:03d}.mp4"
    segment_path = WORK / f"part-{index:03d}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c", "copy", str(silent_path)])
    run(["ffmpeg", "-y", "-i", str(silent_path), "-i", str(audio_path),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(segment_path)])
    return segment_path

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
        audio_path = WORK / f"voice-{index:03d}.wav"

        make_voice(narration, audio_path)
        video_path = render_visual_story(segment, index, len(segments), narration, audio_path)
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
