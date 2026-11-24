# obraz2skrypt.py - obrazek (czarne kreski na bialym) -> ..\hid\scripts\NAZWA.txt
#
# DZIALANIE:
#   1. Wczytuje obraz w skali szarosci, progowanie 128 (ciemne = linia).
#   2. Znajduje kontury (cv2.findContours) i upraszcza je (approxPolyDP).
#   3. Skaluje obraz z zachowaniem proporcji i centruje w obszarze rysowania.
#   4. Dla kazdego konturu generuje: MOVE (start) -> DOWN -> MOVE... -> UP.
#      Kontur jest domykany (ostatni punkt = pierwszy).
#
# WYMAGANIA:
#   pip install opencv-python
#
# UZYCIE:
#   python obraz2skrypt.py mis.jpg mis --x0 300 --y0 250 --w 600 --h 500
#
# ARGUMENTY:
#   obraz   plik wejsciowy (jpg/png/bmp), np. mysz.jpg
#   nazwa   nazwa skryptu wyjsciowego (bez .txt), np. mysz
#   --x0    X lewego gornego rogu pola rysowania na ekranie [px]
#   --y0    Y lewego gornego rogu pola rysowania na ekranie [px]
#   --w     szerokosc pola rysowania [px]
#   --h     wysokosc pola rysowania [px]
#   --eps   tolerancja upraszczania konturu [px obrazu], domyslnie 2.0
#           (wieksza = mniej punktow, bardziej kanciaste; mniejsza = dokladniej, dluzszy skrypt)
#   --min   minimalna dlugosc konturu [px obrazu], domyslnie 30
#           (odrzuca drobny szum i kropki)
#
# WYJSCIE:
#   ..\hid\scripts\NAZWA.txt (wzgledem polozenia tego pliku), kodowanie ASCII.
#   Folder hid\scripts musi istniec, inaczej wyrzuci blad.
#
# FORMAT SKRYPTU:
#   # komentarz
#   WAIT 500        pauza 500 ms na start
#   MOVE x y        przesun kursor na wspolrzedne ekranu (px)
#   DOWN / UP       wcisnij / zwolnij przycisk myszy
#
# WSKAZOWKI:
#   - Najpierw zmierz pole rysowania (np. w Paincie), potem wpisz x0,y0,w,h.
#   - Obraz moze miec dowolny rozmiar; --w i --h to tylko ramka,
#     do ktorej sie wpisze (zachowane proporcje, wycentrowany).
#   - Przy grubych kreskach kazda kreska daje 2 kontury (zewnetrzny
#     i wewnetrzny), czyli linia bedzie narysowana podwojnie.
#     Najlepiej uzyc cienkich linii albo wyskeletonizowac obraz.
#   - Zacznij od malego testu: duze --eps (np. 3-5) daje krotki skrypt.
#   - Kolejnosc konturow jest dowolna, bez optymalizacji trasy
#     (dlugie przeskoki MOVE sa robione z UP, wiec nic nie rysuja).
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

lines = [f"# {a.nazwa} z {os.path.basename(a.obraz)}", "WAIT 1"]
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