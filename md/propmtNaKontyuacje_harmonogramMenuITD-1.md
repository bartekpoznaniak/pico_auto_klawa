Kontynuuj projekt „Pico HID Macro Station”.

CEL PROJEKTU:
Zbudować prosty, samodzielny automat HID na Raspberry Pi Pico 2.

Główny praktyczny cel: automatyczne wybudzenie komputera o zadanej godzinie,
otwarcie właściwego programu lub strony oraz wykonanie zapisanego makra,
np. odświeżenie ogłoszenia na OLX/Elixie bez udziału użytkownika.

Projekt ma być również uniwersalną stacją makr: użytkownik może zapisywać
własne sekwencje ruchów myszy, kliknięć i klawiszy, a następnie uruchamiać je
z poziomu Pico.

WIZJA PROJEKTU:
Projekt ma być prostą, prywatną i przewidywalną stacją automatyzacji HID.
Nie jest to agent AI z szerokim dostępem do komputera.
Pico wykonuje wyłącznie wcześniej przygotowane, ograniczone makra:
wybudza komputer, czeka i odtwarza sekwencję ruchów myszy oraz klawiszy.

Potencjalne zastosowania:

- odświeżanie ogłoszeń,
- wysyłanie wcześniej przygotowanych wiadomości,
- otwieranie programów o określonej godzinie,
- proste, powtarzalne czynności na komputerze,
- rysowanie obrazka w Paincie jako funkcja demonstracyjna i edukacyjna,
- poranna rutyna McLara: wybudzenie komputera, otwarcie sesji,
  wykonanie zrzutu ekranu i wysłanie go mailem.

Zasada produktowa:
Nie buduj funkcji zamieniających Pico w autonomicznego agenta AI.
Priorytetem jest bezpieczne, powtarzalne wykonywanie konkretnych zadań
bez szerokiego dostępu do systemu, plików i danych użytkownika.

ZASADA PODSTAWOWA:
Windows nie wykonuje ruchu myszy ani kliknięć przez pyautogui.
Wszystkie działania HID wykonuje fizycznie Raspberry Pi Pico 2.
Windows może jedynie przygotować, wysłać lub uruchomić makro.

TERMINOLOGIA:

- „makro” = plik .txt z komendami wykonywany przez Pico, np. test1.txt.
- „silnik makr” = scriptengine.py na Pico.
- „narzędzie makr” = program Windows służący do nagrywania lub tworzenia makr.
- „program pomocniczy” = Python/PowerShell na Windows.

Nie nazywaj makr „skryptami”, aby nie mylić ich z programami Python/PowerShell.

SPRZĘT I ŚRODOWISKO:

- Raspberry Pi Pico 2 (RP2350A), CircuitPython 10.3.1.
- OLED SSD1306 128x64, I2C, adres 0x3C, SDA=GP4, SCL=GP5, zasilanie 3V3(OUT).
- Przyciski: GP14 i GP15.
- Komunikacja z Windows: usb_cdc.data, COM13, komendy tekstowe zakończone \n.
- Windows: ekran 3840x2160.

AKTUALNY STAN:

- boot.py konfiguruje konsolę USB, kanał danych USB CDC, klawiaturę HID
  oraz własną mysz absolutną.
- Mysz absolutna: Report ID 7, raport 5-bajtowy:
  buttons, X 16-bit, Y 16-bit; zakres 0-32767.
- code.py v1.223 obsługuje OLED, RTC, przyciski, mysz, klawiaturę, komendy,
  wybudzanie i podstawowe menu OLED.
- Komendy USB: MOVE,x,y, CLICK, WAKE,n, QUIT, TIME,..., RUN,nazwa.
- scriptengine.py wykonuje makra z /scripts/:
  WAIT, MOVE, CLICK, DOWN, UP, TYPE, KEY, HOTKEY.
- Wybudzanie komputera działa: GP14 startuje odliczanie, potem nvm[0]=1,
  microcontroller.reset(), 3 s oczekiwania i 8x Shift co 1 s.
- MOVE, CLICK, DOWN/UP, synchronizacja czasu, menu OLED, lista makr
  i rysowanie w Paincie działają.
- punkt.ps1 pozwala nagrywać punkty myszy do makra.
- obraz2skrypt.py zamienia obrazek na sekwencję MOVE/DOWN/UP.
- Git jest już w miarę ogarnięty; nie skupiaj się teraz na porządkowaniu repo.

WAŻNE USTALENIA TECHNICZNE:

- Przy myszy absolutnej raport UP musi zachować ostatnie współrzędne X i Y.
  Zmienia się wyłącznie bajt przycisków.
- Zmienna buttons musi być zerowana w mouse_up().
- Nie zmieniaj boot.py bez potrzeby; po zmianie wymagany jest fizyczny restart USB.
- Ograniczaj print() w pętli głównej code.py, bo może blokować program,
  gdy REPL nie jest konsumowany.
- OLED pokazuje ostatni zadany cel, a nie rzeczywistą pozycję kursora Windows.

PRIORYTETY ROZWOJU — KOLEJNOŚĆ MA ZNACZENIE:

1. Dokończenie menu OLED.
   Menu ma być proste, czytelne i wygodne w obsłudze dwoma przyciskami.
   Powinno pozwalać wybrać makro, przejrzeć dostępne opcje i uruchomić zadanie 
   bez PowerShell oraz bez obecności użytkownika. 

        (chciałbym przedyswkutować kwestię powrotu do menu z listy makr 
pytanie czy jest konieczny  taki jawny punkt w menuu  czy 
wystarczy ponowne wciśnięcie 2 przycisków)

1. Harmonogram jednorazowy.
   To jest najważniejsza funkcja użytkowa projektu.
   W menu użytkownik wybiera makro oraz godzinę startu.
   Pico zapamiętuje ustawienie, o wybranej godzinie wybudza komputer,
   odczekuje ustalony czas na pełne uruchomienie i wykonuje wybrane makro.
   Najpierw jeden alarm, dopiero później ewentualny harmonogram cykliczny.

2. Uproszczenie tworzenia makr.
   Przejrzeć punkt.ps1 i zaproponować prosty, bezpieczny sposób nagrywania makr:
   MOVE przed kliknięciem, CLICK, ewentualnie WAIT, DOWN i UP.
   Makro powinno być łatwe do zapisania, sprawdzenia i uruchomienia.
   Testować najpierw na Notatniku lub pulpicie, nie na OLX.

3. Pierwszy realny scenariusz OLX/Elixa.
   Dopiero po stabilnym menu, harmonogramie i makrach:
   wybudzenie komputera, otwarcie właściwej strony lub programu,
   przygotowanie okna i wykonanie prostej sekwencji odświeżenia ogłoszenia.
   Nie robić masowej automatycznej korespondencji ani działań łamiących regulamin.

4. Wykrywanie rozdzielczości monitora.
   Obecnie ekran 3840x2160 jest stałym założeniem.
   Docelowo Windows powinien przekazywać Pico aktualną rozdzielczość,
   np. komendą RES,W,H przez USB CDC, aby MOVE,x,y działało także
   po zmianie monitora lub rozdzielczości.
   To ważne dla przenośności, ale nie blokuje obecnej pracy na Twoim komputerze.

5. Podstawowa obsługa błędów.
   Czytelny komunikat na OLED, zatrzymanie makra po nieznanej komendzie
   i możliwość bezpiecznego przerwania. Nie budować jeszcze rozbudowanego
   systemu logowania ani pełnej obsługi wyjątków.

6. Rozszerzenie sprzętowe: RTC.
   Docelowo dodać RTC po I2C, najlepiej współdzieląc magistralę z OLED-em.
   RTC ma pozwolić Pico znać aktualną godzinę bez synchronizacji z Windows,
   co jest ważne dla harmonogramu i pełnej autonomii.
   To jest plan na później, po dopracowaniu menu i harmonogramu.

7. Rozszerzenie sprzętowe: karta microSD.
   Docelowo dodać kartę microSD przez SPI, nie przez I2C.
   SD ma służyć do przechowywania większej liczby makr, logów
   albo konfiguracji. Nie jest potrzebna do podstawowej wersji projektu.
   To jest plan na później, po RTC i stabilnym harmonogramie.

8. Dokumentacja i publikacja.
   Dopiero na końcu, gdy funkcje będą stabilne i użyteczne.

NAJWAŻNIEJSZY CEL BLIŻSZY:
Dokończ menu OLED i harmonogram jednorazowy tak, aby użytkownik mógł
z poziomu Pico wybrać makro, ustawić godzinę startu i pozwolić urządzeniu
samodzielnie wybudzić komputer oraz wykonać makro.

Zacznij od zaproponowania minimalnej, bezpiecznej wersji menu i harmonogramu.
Nie zmieniaj boot.py i nie ruszaj działającego mechanizmu wybudzania.
Pokaż najpierw plan zmian, a dopiero po mojej akceptacji przygotuj kod.

ZASADY LOGOWANIA I BEZPIECZEŃSTWA:
Jeśli Windows wymaga logowania po wybudzeniu, Pico ma wpisywać PIN
lub hasło automatycznie, aby zachować pełną autonomię.

Nie przechowywać głównego hasła Windows jawnie na Pico.
Rozważyć osobny PIN przeznaczony wyłącznie do logowania automatyzacji.

PIN może być przechowywany na Pico w formie zaszyfrowanej.
Nie używać Base64, XOR ani własnych prostych algorytmów jako zabezpieczenia.
Jeśli stosowane jest szyfrowanie, użyć AES i nie zapisywać klucza
w tym samym pliku co zaszyfrowany PIN.

Pico wpisuje PIN tylko po wybudzeniu komputera przez harmonogram.
Nie zapisywać PIN-u w makrach .txt ani w plikach konfiguracyjnych.

Zaakceptowane ograniczenie:
szyfrowanie z kluczem na Pico nie chroni w pełni przed atakującym,
który przejął Windows i ma dostęp do plików CIRCUITPY.
Jest to świadomy kompromis na rzecz autonomii urządzenia.

ZASADY BEZPIECZEŃSTWA SIECIOWEGO:
Pico nie ma Wi‑Fi, Ethernetu ani Bluetooth i nie przyjmuje połączeń z internetu.
Nie dodawać funkcji zdalnego sterowania przez sieć w pierwszej wersji produktu.

Pico komunikuje się wyłącznie przez USB z komputerem użytkownika.
Hasła, tokeny i dane logowania nie mogą być zapisywane jawnie na Pico,
ponieważ przy przejęciu komputera Windows mogą być odczytane z dysku CIRCUITPY.

Pico wykonuje wyłącznie akcje HID.
Dane logowania pozostają w Windows Credential Managerze
albo są wprowadzane przez użytkownika.

ZASADY PRACY:

- Pracuj po polsku.
- Proponuj jeden konkretny krok naraz.
- Przed zmianą pliku zrób kopię lub użyj Gita.
- Nie zmieniaj boot.py bez wyraźnej potrzeby.
- Nie używaj pyautogui do ruchu myszy ani klikania.
- Nie ruszaj jeszcze automatyzacji OLX ani płatności.
- Najpierw zaproponuj plan menu i harmonogramu,
  a dopiero po mojej akceptacji przygotuj kod.
