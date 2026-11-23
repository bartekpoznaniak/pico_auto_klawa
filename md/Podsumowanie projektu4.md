# Podsumowanie sesji — Projekt Pico HID

## Cel sesji

Celem sesji było doprowadzenie funkcji harmonogramu w projekcie Pico HID do działającego stanu.

Projekt miał umożliwiać:

- ustawianie godziny i minuty zadania,
- zapis harmonogramu do pliku,
- wyświetlanie aktualnego stanu planu na OLED,
- wybór opcji wybudzania komputera,
- wybudzanie komputera o ustawionej godzinie,
- zapisanie zmian w projekcie do GitHuba.

## Punkt startowy

Na początku sesji zapis harmonogramu wymagał potwierdzenia. Wcześniejsze testy wskazywały, że zapis do pliku mógł nie działać poprawnie.

Problem związany był z użyciem metody `writelines()` w MicroPython. Została ona zastąpiona zapisem całej zawartości pliku za pomocą:

```python
file.write("".join(lines))
```

Dodano również wywołanie funkcji `save_schedule_entry()` w ekranie `schedule_confirm`. Dzięki temu zatwierdzenie harmonogramu powodowało faktyczny zapis danych do pliku.

## Pierwsze potwierdzenie zapisu

Po wprowadzonych poprawkach w pliku:

```text
F:\schedules\harmonogram.txt
```

pojawiła się wartość:

```text
17:39 mysz
```

To było pierwsze potwierdzenie, że zapis harmonogramu działa.

Ważny wniosek z tej części testów:

> Sam komunikat na OLED nie jest dowodem zapisu. OLED może pokazywać wartość z pamięci Pico, nawet jeśli plik na dysku pozostał niezmieniony.

## Problem z kolejną zmianą

Po ustawieniu nowej godziny `22:03` plik nadal pokazywał starszą wartość `17:39 mysz`.

Sprawdzono zawartość pliku oraz czas ostatniej modyfikacji komendami w PowerShell:

```powershell
Get-Content "F:\schedules\harmonogram.txt"
Get-Item "F:\schedules\harmonogram.txt" | Select-Object Length, LastWriteTime
```

Wynik pokazał, że zawartość pliku oraz czas ostatniego zapisu nie zmieniły się bezpośrednio po zmianie harmonogramu.

## Analiza kodu

Przeanalizowano ścieżkę obsługi przycisków i ekranów:

- `harmonogram`
- `edit_hour`
- `edit_minute`
- `schedule_wake`
- `schedule_confirm`
- `schedule_active`
- `home`

Kod odpowiedzialny za zapis po zatwierdzeniu minut wyglądał poprawnie:

```python
elif screen == "edit_minute":
    if released14:
        edit_minute = (edit_minute + 1) % 60
    elif released15:
        name = schedule_entries[schedule_index]
        new_entry = (edit_hour, edit_minute, name)
        try:
            save_schedule_entry(schedule_index, new_entry)
            schedule_entries[schedule_index] = new_entry
```

Funkcja `save_schedule_entry()` również wyglądała poprawnie. Wykonuje ona:

- odczyt pliku harmonogramu,
- znalezienie właściwego wpisu,
- utworzenie pliku tymczasowego,
- zapis zmienionej linii,
- usunięcie starego pliku,
- zmianę nazwy pliku tymczasowego na właściwy,
- wywołanie `os.sync()`.

## Dodanie testu diagnostycznego

Aby sprawdzić, czy funkcja zapisu jest faktycznie wywoływana, dodano na początku funkcji `save_schedule_entry()` komunikat:

```python
print("SAVE:", index, entry)
```

Po uruchomieniu programu i zmianie czasu pojawiło się w Thonny:

```text
SAVE: 0 (22, 4, 'mysz')
SAVE: 0 (22, 4, 'mysz')
```

Potwierdziło to, że:

- funkcja zapisu jest wywoływana,
- otrzymuje właściwy indeks wpisu,
- otrzymuje właściwą godzinę i minutę,
- zapis wykonuje się dwa razy: po zatwierdzeniu minut oraz po zatwierdzeniu wybudzania.

## Rozwiązanie zagadki opóźnienia

Po pierwszym teście plik w Windows nadal pokazywał starszą wartość. Po krótkim czasie okazało się jednak, że plik faktycznie został zaktualizowany.

Wniosek:

> Windows może przez chwilę pokazywać nieaktualną wersję pliku po zapisie przez Pico, szczególnie bezpośrednio po operacji zapisu lub odświeżeniu widoku pliku.

Dodatkowo dodano testowy odczyt pliku bezpośrednio po zapisie:

```python
with open(path, "r") as check_file:
    print("PO ZAPISIE:", check_file.read())
```

Test potwierdził, że:

- bezpośrednio po pierwszym zapisie odczyt mógł jeszcze pokazać starszą wartość,
- po drugim zapisie Pico widziało już poprawną, nową wartość,
- Windows również ostatecznie widział poprawną zawartość pliku.

## Potwierdzenie działania zapisu

Ostatecznie w pliku pojawiła się wartość:

```text
22:30 mysz
```

A w Thonny:

```text
SAVE: 0 (22, 30, 'mysz')
PO ZAPISIE: 22:30 mysz
```

Potwierdziło to pełną zgodność między:

- wartością ustawioną na Pico,
- zawartością pliku widzianą przez Pico,
- zawartością pliku widzianą przez Windows,
- stanem pokazywanym przez OLED.

## Test wybudzania

Ustawiono harmonogram na:

```text
22:31 mysz
```

Na ekranie `WYBUDZANIE` wybrano opcję:

```text
TAK
```

O godzinie `22:31` komputer został wybudzony przez Pico.

Potwierdziło to działanie pełnego łańcucha:

```text
harmonogram → zapis do pliku → zatwierdzenie → wybudzenie PC
```

## Repozytorium Git i GitHub

Projekt miał już istniejące repozytorium oraz zdalne repozytorium `origin/main`.

Sprawdzono zawartość pliku `.gitignore`:

```text
scripts/kalibracja.txt
scripts/mysz.txt
__pycache__/
```

Użytkownik zdecydował, że katalog `schedules/` ma zostać w repozytorium, ponieważ zawiera małe pliki i ma być częścią kompletnego projektu.

Wykonano komendy:

```powershell
git add boot.py code.py "bmp2txtHID/Instrukcja.txt" schedules/
git commit -m "Dodaje zapis harmonogramu i poprawki wybudzania"
git push
```

Wynik commita:

```text
[main 9e77c2c] Dodaje zapis harmonogramu i poprawki wybudzania
5 files changed, 326 insertions(+), 34 deletions(-)
```

W repozytorium znalazły się m.in.:

- `boot.py`
- `code.py`
- `bmp2txtHID/Instrukcja.txt`
- `schedules/harmonogram.txt`
- `schedules/harmonogram.txt.bak`

Push zakończył się sukcesem:

```text
5f67453..9e77c2c  main -> main
```

Repozytorium GitHub:

```text
[https://github.com/bartekpoznaniak/pico_auto_klawa.git](https://github.com/bartekpoznaniak/pico_auto_klawa.git)
```

Po pushu komenda:

```powershell
git status
```

pokazała:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## Aktualny stan projektu

Projekt został zawieszony w stanie w pełni działającym.

Działają:

- zapis harmonogramu do pliku,
- odczyt harmonogramu przez Pico,
- zgodność OLED z plikiem,
- zatwierdzanie planu,
- wybór opcji wybudzania,
- wybudzanie komputera o ustawionej godzinie,
- zapis zmian w GitHubie.

## Najważniejszy wniosek

Największym osiągnięciem sesji było ustalenie, że problem nie polegał na tym, że Pico nie zapisuje pliku, lecz na tym, że Windows mógł chwilowo pokazywać nieaktualną wersję pliku.

Po dodaniu komunikatów `SAVE:` oraz `PO ZAPISIE:` udało się jednoznacznie potwierdzić, że zapis harmonogramu działa poprawnie.

Projekt można wznowić od punktu dalszych testów harmonogramu, wybudzania komputera oraz rozbudowy interfejsu urządzenia.
