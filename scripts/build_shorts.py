import subprocess
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
WORK = OUT / "shorts_work"
MODEL = ROOT / "models" / "ur_PK-fasih-medium.onnx"
W, H, FPS = 1080, 1920, 25

EPISODES = [
("01-Laapata-Train", "LAAPATA TRAIN", "Aik raat paanch dost Korea ke pahari ilaqay mein aik purani train par sawar huay. Train ke andar sirf paanch musafir thay, magar khirki mein chhay saaye nazar aa rahay thay. Jab train aglay station par ruki to platform par koi nahi tha. Darwazay khulay, lights band huin, aur announcement hui: “Chhata musafir apni seat par wapas aaye.” Paanchon ne aik doosray ko dekha… un mein se aik ka saaya ghayab tha.", "train"),
("02-Band-Jungle", "BAND JUNGLE", "Subah paanchon dost jungle ke kinare pohanchay. Wahan aik purana board laga tha: is jungle mein suraj dhalnay ke baad dakhil hona mana hai. Unhon ne socha koi mazaaq hai. Lekin andar jatay hi un ke phones par aik hi message aaya: “Peechay mat dekho.” Door se kisi ne un ke naam pukaray. Awaaz un ke apnay doston jaisi thi… halaanke sab aik saath kharay thay.", "forest"),
("03-Purana-Phone", "20 SAAL PURANA PHONE", "Jungle ke beech aik chhota sa ghar mila. Andar dhool se bhara telephone rakha tha. Phone ki taar kati hui thi, phir bhi us ki ghanti baj uthi. Aik dost ne receiver uthaya. Doosri taraf se larazti hui awaaz aayi: “Tum log yahan kyun aaye? Hum ne tumhein bees saal pehle rok diya tha.” Phir awaaz ne aik aisi baat kahi jo sirf un paanchon ko maloom thi.", "phone"),
("04-Khoon-Wala-Map", "KHOON WALA MAP", "Phone ke neeche aik purana naqsha chhupa hua tha. Naqshay par laal nishaan khud ba khud ubharne lagay. Har nishaan us jagah ka tha jahan woh aglay din janay walay thay. Aakhri nishaan un ke camp par bana. Zameen par qadamoon ki aahat sunai di, halaanke aas paas koi nahi tha. Phir naqshay par aik jumla likha: “Tum mein se aik wapas nahi jayega.”", "map"),
("05-Gumshuda-Ladki", "GUMSHUDA LADKI", "Raat ko aik chhoti si ladki darakhton ke darmiyan khari nazar aayi. Us ne puranay school uniform jaisa libaas pehna hua tha. Woh boli: “Aakhir tum aa hi gaye.” Doston ne poocha woh kaun hai. Ladki ne un mein se aik ka haath pakra aur kaha: “Main tumhein pehchanti hoon. Tumhare walid ne mujhe yahan chhora tha.” Agli hi pal woh hawa mein ghul gayi.", "girl"),
("06-Zameen-Ke-Neeche", "ZAMEEN KE NEECHE", "Ladki ke ghayab hotay hi zameen mein darar par gayi. Neechay pathar ki seedhiyan aik roshan surang tak ja rahi thin. Paanchon dost neeche utray to unhein pahaar ke andar aik poora shehar mila. Gharon mein roshni thi, ghariyan chal rahi thin, lekin koi insaan nazar nahi aata tha. Achanak loudspeaker chala: “Naye mehmaan aa chukay hain. Darwazay band kar do.”", "underground"),
("07-Aakhri-Warning", "AAKHRI WARNING", "Shehar ke markazi kamray mein aik screen jal uthi. Us par paanchon doston ki tasveer bees saal purani tareekh ke saath lagi thi. Screen par likha tha: “Aakhri warning. Subah se pehle wapas chalay jao.” Unhon ne exit dhoondna shuru kiya, magar har raasta unhein usi kamray mein la raha tha. Phir kisi ne peeche se kaha: “Tum log pehle bhi yahan mar chukay ho.”", "warning"),
("08-Dhokebaaz-Dost", "DHOKEBAAZ DOST", "Paanchon mein se aik dost achanak ruk gaya. Us ne bataya ke us ke paas is jagah ka aik purana khat tha. Us ke dada bhi isi mission ka hissa thay, aur unhon ne sach chhupaya tha. Baqi dost gussay mein us par toot paray. Tabhi shehar ki lights laal ho gayin. Deewar par aik naya paigham chamka: “Raaz jaan liya gaya. Ab qurbani do.”", "friends"),
("09-Bees-Saal-Purana-Sach", "20 SAAL PURANA SACH", "Purani files se pata chala ke bees saal pehle paanch log isi pahaar mein ghaib huay thay. Un ke naam doston ke ghar walon se miltay thay. Yeh sab ittefaq nahi tha. Un ke khandanon ne aik tajruba chhupaya tha jo waqt ke darwazay khol sakta tha. Lekin tajruba nakaam hua aur shehar doosri duniya mein phans gaya. Ab darwaza dobara khul raha tha… aur is baar koi usay band nahi kar sakta tha.", "files"),
("10-Aakhri-Darwaza", "AAKHRI DARWAZA", "Aakhri kamray mein aik bara siyah darwaza khara tha. Us ke paar un ka apna shehar nazar aa raha tha, magar aasman par do chaand thay. Aik dost ne darwaza khol diya. Hawa ka zor daar jhonka aaya aur sab kuch andheray mein doob gaya. Jab aankh khuli to woh train mein thay. Is baar seat par chhay log baithay thay. Aur announcement hui: “Agla station… tumhara ghar.”", "door")
]

def run(cmd):
    subprocess.run(cmd, check=True)

def font(size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)

def draw_scene(title, visual, shot, dest):
    im = Image.new("RGB", (W,H), (3,7,20))
    px = im.load()
    for y in range(H):
        t=y/H
        c=(int(4+10*t), int(8+12*t), int(22+24*t))
        for x in range(W): px[x,y]=c
    d=ImageDraw.Draw(im)
    # atmospheric stars / rain
    for i in range(240):
        x=(i*173+shot*71)%W; y=(i*317+shot*43)%H
        r=2 if i%7==0 else 1
        d.ellipse((x-r,y-r,x+r,y+r), fill=(105,145,190))
    # cinematic layered mountain silhouettes
    d.polygon([(0,920),(160,680),(310,900),(520,590),(760,920),(930,700),(1080,900),(1080,1920),(0,1920)], fill=(14,25,43))
    d.polygon([(0,1150),(210,900),(420,1190),(690,870),(900,1170),(1080,960),(1080,1920),(0,1920)], fill=(8,16,31))
    cx,cy=540,900
    if visual=="train":
        d.polygon([(210,650),(870,650),(970,1330),(110,1330)], fill=(35,52,72), outline=(150,185,210), width=8)
        for x in (280,450,630,800):
            d.rounded_rectangle((x,760,x+110,1010),25,fill=(8,20,38),outline=(125,180,220),width=7)
        d.line((540,660,540,1320),fill=(170,195,215),width=8)
        for x in (300,510,720): d.ellipse((x,1370,x+100,1470),fill=(2,5,12),outline=(110,135,160),width=5)
    elif visual=="forest":
        for i in range(11):
            x=30+i*105
            d.polygon([(x,1350),(x+65,500+(i%3)*90),(x+130,1350)],fill=(12,48+(i%3)*8,43))
            d.rectangle((x+55,1280,x+75,1640),fill=(35,28,25))
        d.ellipse((700,530,850,680),fill=(185,205,215))
    elif visual=="phone":
        d.rounded_rectangle((320,570,760,1350),55,fill=(25,28,34),outline=(170,150,115),width=12)
        d.rounded_rectangle((380,660,700,1120),25,fill=(4,10,18),outline=(100,125,145),width=5)
        d.ellipse((495,1170,585,1260),outline=(180,160,120),width=8)
        d.arc((370,500,710,850),180,350,fill=(100,185,230),width=8)
    elif visual=="map":
        d.polygon([(190,650),(870,590),(920,1300),(250,1380)],fill=(190,170,125),outline=(235,220,180),width=8)
        for i in range(6):
            x=300+i*90; y=800+(i%3)*120
            d.ellipse((x,y,x+34,y+34),fill=(160,25,35))
        d.line((340,830,520,960,700,870,770,1120),fill=(150,20,30),width=12)
    elif visual=="girl":
        d.ellipse((455,610,625,790),fill=(185,175,165))
        d.polygon([(450,780),(630,780),(760,1430),(320,1430)],fill=(40,55,85))
        d.line((470,950,300,1200),fill=(175,165,155),width=35)
        d.line((610,950,790,1200),fill=(175,165,155),width=35)
    elif visual=="underground":
        d.polygon([(0,650),(540,1050),(1080,650),(1080,1920),(0,1920)],fill=(20,28,42))
        for x in (180,450,720,930):
            d.rectangle((x,930,x+130,1330),fill=(28,55,70),outline=(110,175,195),width=6)
            d.rectangle((x+25,990,x+105,1110),fill=(125,180,205))
        d.line((0,1470,1080,1470),fill=(90,120,140),width=10)
    elif visual=="warning":
        d.rounded_rectangle((160,520,920,1150),35,fill=(12,15,24),outline=(190,40,45),width=12)
        d.polygon([(540,630),(690,940),(390,940)],outline=(240,55,55),width=14)
        d.text((455,980),"!",font=font(170),fill=(245,65,65))
    elif visual=="friends":
        for x in (170,350,530,710,890):
            d.ellipse((x-45,760,x+45,850),fill=(175,185,195))
            d.rounded_rectangle((x-60,850,x+60,1230),28,fill=(35,65,90),outline=(115,155,185),width=4)
    elif visual=="files":
        for i in range(4):
            x=180+i*185
            d.rectangle((x,650,x+150,1320),fill=(105,85,65),outline=(210,185,145),width=7)
            d.line((x+25,780,x+125,780),fill=(230,210,175),width=5)
            d.line((x+25,860,x+115,860),fill=(230,210,175),width=5)
    elif visual=="door":
        d.rounded_rectangle((280,480,800,1480),240,fill=(5,7,14),outline=(120,165,205),width=16)
        d.ellipse((700,960,750,1010),fill=(220,190,105))
        d.polygon([(520,600),(690,900),(520,1250),(350,900)],fill=(40,75,110))
    # title and shot caption bands
    d.rectangle((45,95,1035,285),fill=(4,9,20),outline=(90,125,160),width=3)
    d.text((78,145),title,font=font(55),fill=(240,245,250),stroke_width=1,stroke_fill=(5,8,15))
    d.rectangle((45,1530,1035,1815),fill=(3,7,17),outline=(80,115,150),width=3)
    d.text((78,1585),f"AAKHRI SIGNAL  |  EPISODE {shot:02d}",font=font(34),fill=(130,190,220))
    d.text((78,1660),"HANSIZAPPO  •  MOVIE TELLER",font=font(30),fill=(225,230,240))
    im.save(dest)

def main():
    if not MODEL.exists(): raise FileNotFoundError("Piper Urdu voice model was not downloaded.")
    OUT.mkdir(exist_ok=True); WORK.mkdir(parents=True,exist_ok=True)
    for ep,(slug,title,narration,visual) in enumerate(EPISODES,1):
        audio=WORK/f"{slug}.wav"
        run([sys.executable,"-m","piper","-m",str(MODEL),"-f",str(audio),"--",narration])
        # Split into short narration-led shots and give each shot its own illustrated scene.
        parts=[p.strip() for p in narration.split(". ") if p.strip()]
        duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],text=True))
        total=sum(max(1,len(p)) for p in parts); elapsed=0; clips=[]
        for sn,part in enumerate(parts,1):
            sec=duration-elapsed if sn==len(parts) else duration*max(1,len(part))/total
            elapsed+=sec
            still=WORK/f"{slug}-{sn:02d}.png"; clip=WORK/f"{slug}-{sn:02d}.mp4"
            draw_scene(title,visual,sn,still)
            frames=max(1,round(sec*FPS))
            run(["ffmpeg","-y","-loop","1","-framerate",str(FPS),"-i",str(still),"-frames:v",str(frames),
                 "-vf",f"zoompan=z='min(zoom+0.001,1.09)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
                 "-an","-c:v","libx264","-preset","veryfast","-crf","23",str(clip)])
            clips.append(clip)
        concat=WORK/f"{slug}.txt"
        concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips),encoding="utf-8")
        silent=WORK/f"{slug}-silent.mp4"; final=OUT/f"AAKHIR_SIGNAL_{ep:02d}_{slug}.mp4"
        run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
        run(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(final)])
        print(f"SHORT_READY={final}")
    print("BATCH_READY=10")

if __name__=="__main__": main()
