# obraz2skrypt.py - obrazek (czarne kreski na bialym) -> scripts\NAZWA.txt
# Uzycie: python obraz2skrypt.py mysz.jpg mysz --x0 300 --y0 250 --w 600 --h 500
# x0,y0 = lewy gorny rog obszaru rysowania na ekranie; w,h = jego rozmiar (px)
import argparse, os, cv2

a = argparse.ArgumentParser()
a.add_argument("obraz"); a.add_argument("nazwa")
a.add_argument("--x0", type=int, required=True)
a.add_argument("--y0", type=int, required=True)
a.add_argument("--w", type=int, required=True)
a.add_argument("--h", type=int, required=True)
a.add_argument("--eps", type=float, default=2.0)
a.add_argument("--min", type=float, default=30.0)
a = a.parse_args()

img = cv2.imread(a.obraz, cv2.IMREAD_GRAYSCALE)
_, bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
cs, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

ih, iw = img.shape
k = min(a.w / iw, a.h / ih)
ox = a.x0 + (a.w - iw * k) / 2
oy = a.y0 + (a.h - ih * k) / 2

lines = [f"# {a.nazwa} z {os.path.basename(a.obraz)}", "WAIT 500"]
n = 0
for c in cs:
    if cv2.arcLength(c, True) < a.min:
        continue
    p = cv2.approxPolyDP(c, a.eps, True).reshape(-1, 2)
    if len(p) < 2:
        continue
    pts = [(round(ox + x * k), round(oy + y * k)) for x, y in p]
    pts.append(pts[0])
    lines.append(f"MOVE {pts[0][0]} {pts[0][1]}")
    lines.append("DOWN")
    lines += [f"MOVE {x} {y}" for x, y in pts[1:]]
    lines.append("UP")
    n += 1

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hid", "scripts", a.nazwa + ".txt")
with open(os.path.normpath(out), "w", encoding="ascii") as f:
    f.write("\n".join(lines) + "\n")
print(f"Konturow: {n}, linii: {len(lines)} -> {os.path.normpath(out)}")