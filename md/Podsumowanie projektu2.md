Dobrze — zróbmy porządek. Dziś doprowadziłeś projekt do działającego, realnego efektu: Pico otwiera Painta, rysuje obraz z `mysz.jpg` na właściwym kanwasie, a PowerShell kopiuje skrypt, synchronizuje czas i wysyła `RUN`.

## Co już masz





## Co już mamy

- **Wybudzanie komputera:** potwierdzone na Twoim sprzęcie. Pico wysyła `Shift` kilka razy, a komputer w Modern Standby się budzi.

- **OLED i przyciski:** ekran działa, przycisk GP14 był używany w testach; docelowo menu będzie obsługiwane przyciskami.

- **Komunikacja z Windowsem:** działa przez COM13 — wysyłanie komend, synchronizacja czasu i uruchamianie skryptów.

- **Silnik skryptów:** `scriptengine.py` wykonuje pliki `.txt` z `MOVE`, `CLICK`, `TYPE`, `WAIT`, `HOTKEY`, `KEY`.

- **Nagrywanie makr:** `punkt.ps1` zapisuje pozycje myszy i akcje do pliku skryptu.

- **Generator rysunków:** `obraz2skrypt.py` zamienia obrazek w sekwencję `MOVE/DOWN/UP`.

- **Rysowanie w Paincie:** dziś działa — Pico otwiera Painta i rysuje `mysz.jpg` na kanwasie.

- **Synchronizacja czasu:** PowerShell wysyła aktualny czas do Pico, bo płytka nie ma fizycznego RTC.

- **Git:** repo w `wake-test`, z lokalnymi zmianami do uporządkowania.



- Pico 2 z CircuitPythonem wykonuje skrypty tekstowe przez `scriptengine.py` i `code.py`.

- PowerShell kopiuje skrypt na `F:\scripts`, ustawia czas i uruchamia go komendą `RUN,nazwa`.

- `punkt.ps1` pozwala nagrywać punkty myszy do skryptu.

- Generator `obraz2skrypt.py` zamienia obrazek w sekwencję rysowania.

- Działa rysowanie myszy w Paincie, z poprawną kalibracją kanwasu.

- Masz OLED i przyciski, więc urządzenie może stać się samodzielnym panelem, bez PowerShella.

## Plan na później



## Cel projektu

Pico ma działać jako samodzielny automat HID:

1. O ustawionej godzinie wybudza uśpiony komputer przez HID `Shift`.

2. Czeka ustalony czas na pełne obudzenie i ewentualne logowanie.

3. Wykonuje zapisany skrypt: otwiera programy, klika, wpisuje tekst, porusza myszą.

4. Pokazuje na OLED status, godzinę i nazwę wykonywanego zadania.

5. Nie wymaga PowerShella ani Twojej obecności w momencie startu.

Wybudzanie przez `Shift` zostało już potwierdzone: komputer obudził się dokładnie po 20 s

1. **Menu na Pico** — OLED pokazuje listę skryptów z `F:\scripts`; przyciskami wybierasz pozycję, a jednym przyciskiem odpalasz `RUN,nazwa`.

2. **Harmonogram** — w menu ustawiasz godzinę uruchomienia skryptu; Pico sam wykonuje go o wybranej porze. Najpierw prosty harmonogram jednorazowy, potem ewentualnie cykliczny.

3. **Powrót do OLX** — zrobimy bezpieczny, praktyczny scenariusz automatyzacji: otwarcie strony, przygotowanie okna i wykonanie zaplanowanej sekwencji. Ważne: nie robimy masowej automatycznej korespondencji ani działań łamiących regulamin; OLX może blokować konta za automatyzację.

4. **Projekt do publikacji** — gdy menu, harmonogram i edytor makr będą stabilne, opiszemy go jako „Pico HID Macro Station”: urządzenie do automatyzacji myszy i klawiatury z OLED-em, menu, harmonogramem i skryptami tekstowymi.

## Kolejność po powrocie

1. Commit i `.gitignore` dla wygenerowanych skryptów.

2. Menu na OLED z wyborem i uruchamianiem skryptów.

3. Harmonogram godziny startu.

4. Pierwszy realny scenariusz OLX.

5. Dopiero potem dokumentacja i publikacja.
