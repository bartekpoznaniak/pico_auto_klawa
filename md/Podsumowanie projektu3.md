- Windows wysyła komendy przez `usb_cdc.data` (COM13), każda linia kończy się `\n`.
- Pico wykonuje ruchy myszy i klawiaturę przez USB HID — Windows widzi je jak fizyczne urządzenia.
- OLED pokazuje nazwę, wersję, zegar RTC, ostatnią komendę, odliczanie i status.
- Nie używamy pyautogui do ruchu myszy ani klikania — wszystko wykonuje fizycznie Pico przez USB HID.

## boot.py — konfiguracja USB

- Włączone: konsola Thonny (`console=True`) i osobny kanał danych (`data=True`) przez `usb_cdc.enable`.
- Zarejestrowane urządzenia HID: klawiatura (`usb_hid.Device.KEYBOARD`) oraz własna mysz absolutna.
- Mysz absolutna:
  - Report ID: 7.
  - Raport 5-bajtowy: bajt 0 = przyciski (3 bity + 5 bitów paddingu), bajty 1–2 = X (16 bit), bajty 3–4 = Y (16 bit).
  - X i Y są absolutne, w zakresie 0–32767.
  - `usage_page=0x01`, `usage=0x02`, `report_ids=(7,)`, `in_report_lengths=(5,)`.
- Ważne: przy każdej zmianie `boot.py` wymagany jest fizyczny restart USB Pico (odłączenie i podłączenie).

## code.py — główny program Pico (v1.223)

- Obsługuje OLED, RTC, przyciski, mysz absolutną, klawiaturę i komendy z Windows.
- Komendy przez `usb_cdc.data`:
  - `MOVE,x,y` — absolutny ruch kursora (skalowanie pikseli 3840x2160 → 0–32767).
  - `CLICK` — krótkie kliknięcie lewym przyciskiem.
  - `WAKE,n` — ustawia opóźnienie odliczania (domyślnie 1200 s).
  - `QUIT` — kończy pracę.
  - `TIME,rok,mies,dzien,godz,min,sek` — synchronizacja RTC.
  - `RUN,nazwa` — uruchamia skrypt z `/scripts/nazwa.txt` przez `scriptengine.run`.
- Sekwencja wybudzania:
  - GP14 startuje odliczanie.
  - Po odliczeniu: `nvm[0]=1`, `microcontroller.reset()`.
  - Po restarcie: 3 s przerwy, potem 8 razy Shift co 1 s przez keyboard HID.
  - Restart Pico jest KLUCZOWY dla budzenia komputera — wersja bez restartu nie budziła.
- Menu OLED:
  - GP14+GP15 jednocześnie → otwiera menu.
  - GP15 → przewijanie listy skryptów.
  - GP14 → wybór i uruchomienie skryptu (`scriptengine.run`).
  - Lista skryptów z `/scripts/` działa, przewijanie działa, wybór uruchamia skrypt.
- `move_to(x, y)`:
  - Skaluje piksele ekranu do 0–32767.
  - Ustawia `report[0] = buttons` (żeby zachować stan przycisku podczas ruchu).
  - Wysyła raport z `report_id=REPORT_ID`.
- `mouse_down()`:
  - Ustawia `buttons = 1`, `report[0] = 0x01`, wysyła raport.
- `mouse_up()` (po dzisiejszej poprawce):
  - `buttons = 0`, `report[0] = 0`, współrzędne (report[1]–[4]) zostają bez zmian.
  - Wysyła raport — poprawnie puszcza przycisk.
- `click_left()`:
  - Ustawia przycisk, zeruje współrzędne, wysyła, czeka 0.05 s, puszcza.

## scriptengine.py — silnik skryptów

- Wykonuje pliki `.txt` z katalogu `/scripts/` na Pico.
- Obsługiwane komendy (po dzisiejszej aktualizacji):
  - `WAIT,n` — pauza w sekundach.
  - `MOVE,x,y` — absolutny ruch kursora.
  - `CLICK` — kliknięcie lewym.
  - `DOWN` — wciśnięcie lewego przycisku (dodane dzisiaj).
  - `UP` — puszczenie lewego przycisku (dodane dzisiejszej aktualizacji).
  - `TYPE,tekst` — wpisanie tekstu.
  - `KEY,nazwa` — pojedynczy klawisz.
  - `HOTKEY,klawisz1 klawisz2` — skrót klawiszowy.
- Nieznana komenda → OLED pokazuje `? nazwa`, skrypt się zatrzymuje.
- Błąd w linii → OLED pokazuje `ERR numer`, skrypt się zatrzymuje.

## Skrypty PowerShell i Python po stronie Windows

- `uruchom.ps1` (w `ps_scripts/`):
  - Kopiuje skrypt `.txt` do `F:\scripts`.
  - Synchronizuje czas Pico.
  - Wysyła `RUN,nazwa` przez COM13.
  - Uruchamianie z innych katalogów powodowało błędy — trzeba być w `hid/`.
- `ustaw_czas_pico.ps1` — synchronizacja czasu Pico z Windows.
- `wake.ps1` — zatwierdzone `WAKE,300` (wartość 10 była tylko testem).
- `punkt.ps1` — nagrywanie pozycji myszy i akcji do pliku skryptu.
- `obraz2skrypt.py` — zamienia obrazek (np. `mysz.jpg`) w sekwencję `MOVE/DOWN/UP` do rysowania.
- `mapaint.ps1` — wspiera rysowanie w Paincie.
- `steruj_pico.py` — kontroler z Windows: wysyła `MOVE`, `CLICK`, `QUIT` przez pyserial.
- `test_hid.py` — minimalny test myszy absolutnej.

## Co już działa (potwierdzone)

- **Wybudzanie komputera:** potwierdzone na sprzęcie — Pico wysyła Shift kilka razy, komputer w Modern Standby budzi się (potwierdzone dokładnie po 20 s przy WAKE,300).
- **Mysz absolutna:** `MOVE,x,y` przesuwa kursor do wskazanych pikseli na 3840x2160 — potwierdzone.
- **Kliknięcie:** `CLICK` działa.
- **Rysowanie w Paincie:** Pico otwiera Painta i rysuje obraz z `mysz.jpg` na właściwym kanvasie — działa z poprawną kalibracją.
- **Synchronizacja czasu:** PowerShell wysyła czas, Pico odpowiada `OK`.
- **Menu OLED:** lista skryptów się pokazuje, przewijanie działa, wybór uruchamia skrypt.
- **Silnik skryptów:** wykonuje pliki `.txt` z `MOVE`, `CLICK`, `TYPE`, `WAIT`, `HOTKEY`, `KEY`, a od dzisiaj także `DOWN` i `UP`.
- **Rysowanie kreski testowej:** `test1.txt` (WAIT, MOVE, DOWN, MOVE, MOVE, UP) rysuje kreskę i poprawnie kończy ją na `UP`.

## Co zrobiliśmy dzisiaj (21.11.2026) — krok po kroku

1. **Diagnoza problemu `? DOWN`** — skrypt `test1.txt` zatrzymywał się na komendzie `DOWN`, OLED pokazywał `? DOWN`.
2. **Sprawdzenie `scriptengine.py` na Pico** — `Select-String -Pattern "DOWN"` nie zwróciło nic: silnik na Pico nie miał obsługi `DOWN` ani `UP`.
3. **Wymiana `scriptengine.py`** — wgrano nową wersję z obsługą `DOWN`, `UP`, `TYPE`, `KEY`, `HOTKEY`, `WAIT`, `MOVE`, `CLICK`.
4. **Test rysowania** — kreska zaczęła się rysować, ale początkowo trafiała w menu (za wysoko) — poprawiono współrzędne w `test1.txt`.
5. **Problem „kreska znika”** — kreska rysowała się, ale znikała natychmiast po `UP`.
6. **Pierwsza poprawka `mouse_up`** — dodano zerowanie `report[1]`, `report[2]` (współrzędnych) — nic to nie zmieniło.
7. **Test bez `UP`** — usunięto `UP` ze skryptu, dodano `WAIT 5` — kreska zostawała, czyli problem był w `UP`.
8. **Odkrycie: narzędzie Zaznaczanie** — to, co wyglądało jak „kreska”, było ramką zaznaczenia w Paincie (narzędzie Zaznacz było aktywne). Po wybraniu Pędzla problem częściowo znikł.
9. **Problem „przycisk dalej wciśnięty”** — po `UP` ruch fizycznej myszy dalej rysował — `mouse_up` zerował raport, ale nie zerował zmiennej `buttons`, którą `move_to` przywracał w `report[0]`.
10. **Poprawka `mouse_up` z `buttons = 0`** — dodano `global buttons` i `buttons = 0` w `mouse_up()`.
11. **Problem „dorysowuje do lewej”** — po `UP` kreska dorysowywała się do lewej krawędzi — wynikało z zerowania współrzędnych w raporcie puszczenia (absolutna mysz: 0,0 = lewy-górny róg).
12. **Poprawka: zachowanie współrzędnych przy `UP`** — usunięto zerowanie `report[1]`–`report[4]`, zostawiono tylko `report[0] = 0`.
13. **Test w nowym dokumencie Painta** — po otwarciu świeżego dokumentu i wybraniu Pędzla kreska rysuje się i **zostaje** po `UP`. Problem „znikania” wynikał z aktywnego zaznaczenia w starym dokumencie, nie z HID.
14. **Dodanie `scripts/test1.txt` do repo** — użytkownik zdecydował, że testy też mają być w komplecie w Gicie.
15. **Przygotowanie commita `v1.223`** — `code.py`, `scriptengine.py`, `scripts/test1.txt` — commit i push na `origin/wake-test`.

## Ważne wnioski z dzisiejszej sesji

- Przy myszy absolutnej raport puszczenia przycisku musi zachować ostatnie współrzędne — zmienia się tylko bajt przycisków.
- Zmienna `buttons` musi być zerowana w `mouse_up()`, inaczej kolejny `MOVE` przywraca wciśnięty przycisk.
- „Znikanie kreski” w Paincie może wynikać z aktywnego narzędzia Zaznaczanie, nie z błędu HID.
- Przed testowaniem rysowania warto otwierać nowy dokument w Paincie i wybierać Pędzel.

## Git — stan i historia

- Repozytorium: `C:\Users\Bartek\Documents\projects\zrodla\hid`, gałąź `wake-test`, wypchnięta na `origin`.
- Ważniejsze commity:
  - `1737bb9` — v1.16 (wcześniejszy stan).
  - `c0869e4` — v1.21: menu OLED i obsługa przycisków GP14/GP15.
  - `v1.223` (dzisiejszy) — obsługa DOWN/UP, poprawne puszczenie myszy, test rysowania.
- Pliki robocze (`code.py.bk1`, `code_1.105_tymczasowy.py`, `code_1.14.py`) są nieśledzone — ukryte przez `.git/info/exclude`.
- Problem do rozwiązania: cała biblioteka `adafruit-circuitpython-bundle-10.x-mpy-20261119` jest śledzona w repozytorium — docelowo `git rm --cached` + `.gitignore`.

## Pułapki, na które trafiliśmy

- `receive_time()` początkowo połykało komendy `MOVE` — czytało wszystkie dane z portu i odrzucało linie niebędące `TIME,...`. Rozwiązanie: przekazywanie takich linii do obsługi komend.
- Właściwy port COM: jeden port to konsola REPL, drugi to `usb_cdc.data` — port używany przez działający skrypt synchronizacji czasu jest właściwym portem danych (COM13).
- Blokujące `print()` przy rozłączonym/niekonsumowanym REPL-u potrafiło zatrzymywać pętlę — usunięcie zbędnych printów przy ruchu rozwiązało zawieszanie zegara.
- PowerShell 5.1: przekierowanie `>` zapisuje UTF-16, a CircuitPython zgłasza wtedy `SyntaxError` w linii 1. Poprawny zapis: `cmd /c "git show HASH:code.py > code.py"`.
- Błąd Thonny `TclError ... is not managed by ...editornotebook` to błąd edytora, nie programu — pomaga otwarcie lokalnej kopii zamiast pliku z Pico.
- Skróty w Thonny: komentowanie `Ctrl+3`, nie `Ctrl+/`.
- Zawsze rób kopię przed nadpisaniem i sprawdzaj `git status`.

## Ważne ustalenia i zasady

- Ekran: 3840 × 2160, współrzędne `MOVE,x,y` w pikselach.
- Wartości HID skalowane do 0–32767, Report ID myszy to 7.
- `Cel:` na OLED pokazuje ostatni cel zadany Pico, nie rzeczywistą pozycję kursora Windows.
- Nie zmieniać `boot.py` bez potrzeby — przy każdej zmianie wymagany fizyczny restart USB.
- Zachować architekturę: Windows wysyła komendy, Pico wykonuje HID.
- Nie ruszać jeszcze automatyzacji OLX ani płatności.
- Ograniczać `print()` w pętli głównej `code.py`.

## Plan na później

1. **Commit i `.gitignore`** — uporządkowanie repo, przestać śledzić bibliotekę Adafruit.
2. **Menu na Pico** — dopracować OLED: wybór i uruchamianie skryptów w pełni z poziomu urządzenia.
3. **Harmonogram** — w menu ustawiać godzinę uruchomienia skryptu; najpierw jednorazowy, potem cykliczny.
4. **Pierwszy realny scenariusz OLX/Elixa** — otwarcie strony, przygotowanie okna, wykonanie zaplanowanej sekwencji.
5. **Dokumentacja i publikacja** — gdy menu, harmonogram i edytor makr będą stabilne, opisać projekt jako „Pico HID Macro Station”.

## Prompt otwierający dla kolejnej sesji

```text
Kontynuuj projekt "Pico HID Automation" na Raspberry Pi Pico 2 (RP2350A), CircuitPython 10.3.1.

Stan: działający automat HID — Windows widzi Pico jako fizyczną mysz absolutną (Report ID 7, 5-bajtowy raport: buttons, X 16-bit, Y 16-bit, 0–32767) i klawiaturę.

boot.py: USB CDC (console + data), klawiatura HID + własna mysz absolutna.
code.py v1.223: OLED SSD1306 (SDA=GP4, SCL=GP5, 0x3C), RTC, przyciski GP14/GP15, mysz absolutna, komendy MOVE/CLICK/WAKE/QUIT/TIME/RUN, sekwencja wybudzania (GP14 → odliczanie → nvm=1 → reset → 3 s → 8x Shift), menu OLED (GP14+GP15 → menu, GP15 → przewijanie, GP14 → wybór/uruchomienie).
scriptengine.py: wykonuje /scripts/*.txt — WAIT, MOVE, CLICK, DOWN, UP, TYPE, KEY, HOTKEY.
PowerShell: uruchom.ps1 (kopiowanie skryptu, sync czasu, RUN), ustaw_czas_pico.ps1, wake.ps1 (WAKE,300), punkt.ps1 (nagrywanie punktów), obraz2skrypt.py (obraz → skrypt rysowania).

Działa: wybudzanie komputera (potwierdzone), MOVE absolutne na 3840x2160, CLICK, rysowanie w Paincie (mysz.jpg), synchronizacja czasu, menu OLED z listą i uruchamianiem skryptów, DOWN/UP w scriptengine, poprawne puszczenie przycisku po UP.

Git: repo hid, gałąź wake-test, ostatni commit v1.223 (code.py, scriptengine.py, scripts/test1.txt).

Ważne zasady:
- Nie używaj pyautogui do ruchu/klikania — wszystko przez Pico HID.
- Nie zmieniaj boot.py bez potrzeby; po zmianie wymagany restart USB.
- Zachowaj ekran 3840x2160, skalowanie 0–32767, Report ID 7.
- Przy myszy absolutnej raport puszczenia zachowuje współrzędne, zmienia tylko bajt przycisków.
- Zmienna `buttons` zerowana w mouse_up().
- Ograniczaj print() w pętli głównej.
- Przy testach rysowania w Paincie: nowy dokument + Pędzel (nie Zaznaczanie).
- sprawdźmy czy jesteśmy w stanie wykryć rozdzielczość monitora np odpalając PS i wpisując komendę
Następny krok: menu OLED (dopracowanie wyboru skryptów), potem harmonogram wybudzenia, potem pierwszy scenariusz OLX/Elixa.
```

Kontynuuj projekt "Pico HID Automation" na Raspberry Pi Pico 2 (RP2350A), CircuitPython 10.3.1.

Stan: działający automat HID — Windows widzi Pico jako fizyczną mysz absolutną (Report ID 7, 5-bajtowy raport: buttons, X 16-bit, Y 16-bit, 0–32767) i klawiaturę.

boot.py: USB CDC (console + data), klawiatura HID + własna mysz absolutna.
code.py v1.223: OLED SSD1306 (SDA=GP4, SCL=GP5, 0x3C), RTC, przyciski GP14/GP15, mysz absolutna, komendy MOVE/CLICK/WAKE/QUIT/TIME/RUN, sekwencja wybudzania (GP14 → odliczanie → nvm=1 → reset → 3 s → 8x Shift), menu OLED (GP14+GP15 → menu, GP15 → przewijanie, GP14 → wybór/uruchomienie).
scriptengine.py: wykonuje /scripts/*.txt — WAIT, MOVE, CLICK, DOWN, UP, TYPE, KEY, HOTKEY.
PowerShell: uruchom.ps1 (kopiowanie skryptu, sync czasu, RUN), ustaw_czas_pico.ps1, wake.ps1 (WAKE,300), punkt.ps1 (nagrywanie punktów), obraz2skrypt.py (obraz → skrypt rysowania).

Działa: wybudzanie komputera (potwierdzone), MOVE absolutne na 3840x2160, CLICK, rysowanie w Paincie (mysz.jpg), synchronizacja czasu, menu OLED z listą i uruchamianiem skryptów, DOWN/UP w scriptengine, poprawne puszczenie przycisku po UP.

Git: repo hid, gałąź wake-test, ostatni commit v1.223 (code.py, scriptengine.py, scripts/test1.txt).

Ważne zasady:

- Nie używaj pyautogui do ruchu/klikania — wszystko przez Pico HID.
- Nie zmieniaj boot.py bez potrzeby; po zmianie wymagany restart USB.
- Zachowaj ekran 3840x2160, skalowanie 0–32767, Report ID 7.
- Przy myszy absolutnej raport puszczenia zachowuje współrzędne, zmienia tylko bajt przycisków.
- Zmienna `buttons` zerowana w mouse_up().
- Ograniczaj print() w pętli głównej.
- Przy testach rysowania w Paincie: nowy dokument + Pędzel (nie Zaznaczanie).
- 

Następny krok: menu OLED (dopracowanie wyboru skryptów), potem harmonogram wybudzenia, potem pierwszy scenariusz OLX/Elixa.
