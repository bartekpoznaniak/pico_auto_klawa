## Podsumowanie projektu

**Sprzęt i środowisko**

- Pico 2 (RP2350A) z CircuitPython 10.3.1, nie MicroPython, więc nie ma modułu `machine`. Restart robi się przez `microcontroller.reset()`.

- Ekran OLED 128x64 (SSD1306, I²C, adres 0x3C). W kodzie jest podłączony pod `SCL=GP5`, `SDA=GP4`.

- Zasilanie ekranu musi być z 3V3(OUT) (pin 36). Przy napięciu około 4,5 V pojawiało się zwarcie, a przy 3,3 V działa.

- Przyciski: GP14 (start odliczania), GP15 (obecnie nieużywany).

**Funkcje programu (v1.16)**

- Komendy przez port danych `usb_cdc.data` (u Ciebie COM13), zakończone znakiem nowej linii: `MOVE,x,y`, `CLICK`, `WAKE,n`, `QUIT`, `TIME,rok,mies,dzien,godz,min,sek`.

- `WAKE,n` tylko ustawia opóźnienie. Odliczanie rusza po naciśnięciu GP14. Domyślnie jest 1200 s.

- Wybudzanie komputera: po odliczeniu Pico ustawia flagę `nvm[0]=1`, robi `microcontroller.reset()`, po starcie czeka 3 s i wysyła 8 razy Shift (co 1 s). **Restart Pico jest kluczowy**, bo wersja 1.14 (ruch myszą bez restartu) nie budziła komputera.

- Ekran pokazuje nazwę, wersję, zegar RTC, ostatnią komendę, odliczanie i status.

## Co zrobiliśmy w Gicie

- Repozytorium: `C:\Users\Bartek\Documents\projects\zrodla\hid`, gałąź `wake-test`. Wypchnięta na serwer, status czysty poza trzema plikami roboczymi.

- Znalezione commity `code.py`: `4d7cb30` (v1.14), `217e17c` (v1.105 tymczasowy), `1737bb9`. Ostatni ma opis „v1.15”, a w katalogu i w historii jest już kod 1.16. Treści `1737bb9` nie sprawdziliśmy komendą, ale `git status` pokazuje zgodność z plikiem lokalnym.

- Pliki robocze `code.py.bk1`, `code_1.105_tymczasowy.py`, `code_1.14.py` są nieśledzone. Ukryj je przez `.git\info\exclude`.

- W `wake.ps1` zatwierdzone jest `WAKE,300`. Wartość `10` była tylko lokalnym testem.

- Problem do rozwiązania: cała biblioteka `adafruit-circuitpython-bundle-10.x-mpy-20261119` jest śledzona w repozytorium.

## Pułapki, na które trafiliśmy

- PowerShell 5.1: przekierowanie `>` zapisuje UTF-16, a CircuitPython zgłasza wtedy `SyntaxError` w linii 1. Poprawny zapis to `cmd /c "git show HASH:code.py > code.py"`.

- Błąd Thonny `TclError ... is not managed by ...editornotebook` to błąd edytora, nie programu. Pomaga otwarcie lokalnej kopii zamiast pliku z Pico.

- Skróty w Thonny: komentowanie `Ctrl+3`, nie `Ctrl+/`.

- Zawsze rób kopię przed nadpisaniem i sprawdzaj `git status`.

## Prompt otwierający na jutro

text

`Pracuję nad projektem Pico HID na Raspberry Pi Pico 2 (RP2350A) z CircuitPython 10.3.1 (nie MicroPython). Piszę po polsku, lubię jeden krok / jedną komendę naraz, ostrożnie z nieodwracalnymi zmianami (najpierw kopia zapasowa). Sprzęt: OLED SSD1306 128x64 I2C 0x3C na GP4 (SDA) / GP5 (SCL), zasilanie 3V3(OUT). Przyciski GP14 (start odliczania) i GP15 (nieużywany). Komunikacja komendami przez usb_cdc.data (COM13), każda linia kończy się \n: MOVE,x,y | CLICK | WAKE,n | QUIT | TIME,rok,mies,dzien,godz,min,sek.  Aktualna wersja: code.py v1.16. WAKE,n ustawia tylko opóźnienie w sekundach, odliczanie rusza po GP14 (domyślnie 1200 s). Po odliczeniu: nvm[0]=1, microcontroller.reset(), po starcie 3 s przerwy i 8x Shift co 1 s przez keyboard HID. Restart Pico jest KLUCZOWY dla budzenia komputera, nie usuwać. Ruch myszą absolutną (move_to) służy tylko do komend MOVE/CLICK i nie budzi komputera.  Git: repo C:\Users\Bartek\Documents\projects\zrodla\hid, gałąź wake-test, wypchnięta na origin. Ostatni commit kodu to 1737bb9 (opis "v1.15", w środku 1.16). Wcześniejsze: 4d7cb30 (v1.14), 217e17c (v1.105). Nieśledzone pliki robocze: code.py.bk1, code_1.105_tymczasowy.py, code_1.14.py. Problem: biblioteka adafruit-circuitpython-bundle-10.x-mpy-20261119 jest śledzona w repozytorium.  Pułapki: używam PowerShella (nie CMD); przekierowanie > w PS 5.1 daje UTF-16, więc pliki z gita odtwarzam przez cmd /c "git show HASH:plik > plik". Błąd Thonny "TclError ... not managed by editornotebook" to błąd edytora.  Do zrobienia: (1) przestać śledzić bibliotekę Adafruit w gicie (git rm --cached, bez kasowania plików) i dodać ją do .gitignore; (2) sprawdzić zawartość commita 1737bb9 komendą git show 1737bb9:code.py | Select-String "^VERSION"; (3) zdecydować, co zrobić z GP15; (4) dalsze usprawnienia kodu. Zacznij od kroku (1), po jednej komendzie.`




