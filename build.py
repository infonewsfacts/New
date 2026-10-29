"""FactCues Post Maker - build helper (GitHub Actions mein chalta hai).
python3 build.py prepare   -> www folder + fonts
python3 build.py android   -> icon, native save bridge, minSdk
"""
import os, re, shutil, sys, urllib.request
from PIL import Image, ImageChops, ImageDraw

def prepare():
    os.makedirs("www/fonts", exist_ok=True)
    shutil.copy("index.html", "www/index.html")
    base = "https://github.com/google/fonts/raw/main/ofl/"
    fonts = [
        ("Poppins", "500", "Poppins-Medium.ttf", "poppins/Poppins-Medium.ttf"),
        ("Poppins", "700", "Poppins-Bold.ttf", "poppins/Poppins-Bold.ttf"),
        ("Poppins", "800", "Poppins-ExtraBold.ttf", "poppins/Poppins-ExtraBold.ttf"),
        ("Poppins", "900", "Poppins-Black.ttf", "poppins/Poppins-Black.ttf"),
        ("Noto Sans Devanagari", "100 900", "NotoSansDevanagari.ttf",
         "notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"),
    ]
    css = []
    for fam, w, name, path in fonts:
        try:
            req = urllib.request.Request(base + path, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) < 10000:
                raise Exception("file too small")
            open("www/fonts/" + name, "wb").write(data)
            css.append('@font-face{font-family:"%s";font-weight:%s;font-style:normal;'
                       'font-display:block;src:url("fonts/%s") format("truetype");}' % (fam, w, name))
            print("ok  ", name)
        except Exception as e:
            print("WARN", name, "download nahi hua:", e)
    open("www/fonts.css", "w").write("\n".join(css) + "\n")

def android():
    res = "android/app/src/main/res"
    dens = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
            "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}
    full = Image.open("icon-full.png").convert("RGBA")
    fg = Image.open("icon-fg.png").convert("RGBA")
    for d, (l, f) in dens.items():
        out = "%s/mipmap-%s" % (res, d)
        os.makedirs(out, exist_ok=True)
        sq = full.resize((l, l), Image.LANCZOS)
        sq.save(out + "/ic_launcher.png")
        m = Image.new("L", (l * 4, l * 4), 0)
        ImageDraw.Draw(m).ellipse([0, 0, l * 4 - 1, l * 4 - 1], fill=255)
        m = m.resize((l, l), Image.LANCZOS)
        rd = sq.copy()
        rd.putalpha(ImageChops.multiply(sq.getchannel("A"), m))
        rd.save(out + "/ic_launcher_round.png")
        fg.resize((f, f), Image.LANCZOS).save(out + "/fc_icon_foreground.png")

    os.makedirs(res + "/mipmap-anydpi-v26", exist_ok=True)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
           '    <background android:drawable="@color/fc_icon_bg"/>\n'
           '    <foreground android:drawable="@mipmap/fc_icon_foreground"/>\n'
           '</adaptive-icon>\n')
    for n in ("ic_launcher.xml", "ic_launcher_round.xml"):
        open(res + "/mipmap-anydpi-v26/" + n, "w").write(xml)
    os.makedirs(res + "/values", exist_ok=True)
    open(res + "/values/fc_colors.xml", "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="fc_icon_bg">#16301C</color>\n</resources>\n')

    jdir = "android/app/src/main/java/com/factcues/postmaker"
    os.makedirs(jdir, exist_ok=True)
    for j in ("MainActivity.java", "SaveBridge.java"):
        shutil.copy(j, jdir + "/" + j)

    p = "android/variables.gradle"
    s = open(p).read()
    s = re.sub(r"minSdkVersion = \d+", "minSdkVersion = 29", s)
    open(p, "w").write(s)
    print("Android customization done.")

if __name__ == "__main__":
    {"prepare": prepare, "android": android}[sys.argv[1]]()
