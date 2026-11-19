# Symulacja krakowskiej sieci tramwajowej – checkpoint 2

## Co zrobiliśmy?

W pierwszym checkpointcie program pokazywał pozycje tramwajów dla jednej wybranej godziny. Teraz dodaliśmy symulację upływu czasu i animację ruchu. Nadal korzystamy z rozkładów GTFS ZTP Kraków, a nie z pozycji GPS.

Nowe rzeczy w checkpointcie 2:
- Każdy **kurs** ma własny stan: oczekuje, jedzie, stoi na przystanku albo zakończył trasę.
- Dodaliśmy prosty **DES** (symulację zdarzeń dyskretnych). Odjazdy i przyjazdy są zdarzeniami wykonywanymi po kolei według czasu.
- Tramwaje poruszają się po trasach z `shapes.txt`, czyli uwzględniają zakręty. Jeśli nie uda się dopasować trasy, program nadal prowadzi tramwaj po prostej między przystankami.
- Tramwaje zatrzymują się na przystankach. Przyjęliśmy minimalny postój **15 sekund**, ponieważ w GTFS godzina przyjazdu i odjazdu bywa taka sama.
- Na mapie widać jadące i stojące tramwaje oraz ich liczbę. Zdarzenia można też zapisać do CSV.

## Na czym polega DES?

Program ma zegar i listę zdarzeń ułożonych od najwcześniejszego. Przykład: 08:00 – odjazd, 08:04 – przyjazd, 08:05 – kolejny odjazd. Przy każdym zdarzeniu zmienia się stan danego kursu. Animacja pokazuje, gdzie powinien być tramwaj między tymi zdarzeniami.

Zrobiliśmy to przy pomocy `heapq`, czyli kolejki dostępnej w Pythonie.

## Z czego korzystamy?

- **GTFS ZTP Kraków** – linie (`routes.txt`), kursy (`trips.txt`), przystanki (`stops.txt`), godziny (`stop_times.txt`), trasy (`shapes.txt`) i daty kursowania (`calendar_dates.txt`).
- **Python + pandas** – odczytywanie i łączenie danych.
- **requests** – pobieranie GTFS.
- **heapq** – kolejka zdarzeń DES.
- **Matplotlib** – mapa i animacja.

Główne pliki projektu: `gtfs.py` (dane), `simulation.py` (czas i zdarzenia), `geometry.py` (ruch po trasie), `main.py` (uruchamianie i mapa).

## Jakie były problemy?

1. **Tramwaje poruszały się po prostej.** Dodaliśmy wykorzystanie `shapes.txt` i dopasowanie przystanków do trasy. Przy nieudanym dopasowaniu zostaje stara metoda.
2. **Tramwaje znikały podczas postoju.** Teraz mają osobny stan `stopped` i pozostają na przystanku do odjazdu.
3. **Licznik stojących ciągle pokazywał 0.** W GTFS postój może mieć zapisane 0 sekund, więc przyjęliśmy minimum 15 sekund na przystankach pośrednich. To nasze założenie, które może przesunąć dalsze godziny względem rozkładu.
4. **Dużo pojazdów na mapie.** Ograniczyliśmy liczbę wyświetlanych numerów linii, żeby wykres był czytelniejszy.

## Jak uruchomić?

W folderze projektu:

```bash
pip install -r requirements.txt
python main.py 08:00 2026-11-20
```

Data musi być dostępna w pobranym GTFS. Program domyślnie pokazuje godzinę ruchu.

Przydatne opcje:

```bash
python main.py 08:00 2026-11-20 --duration 30
python main.py 08:00 2026-11-20 --step 5 --stop-time 20
python main.py 08:00 2026-11-20 --no-animation --log results/events.csv
```

- `--duration 30` – 30 minut symulacji.
- `--step 5` – aktualizacja obrazu co 5 sekund czasu symulacji.
- `--stop-time 20` – minimum 20 sekund postoju.
- `--no-animation --log ...` – bez mapy, z zapisem zdarzeń do CSV.

**Czerwony punkt** oznacza jazdę, **pomarańczowy** – postój na przystanku. Postój nie oznacza awarii.

## Co dalej – checkpoint 3?

Chcemy dodać losowe opóźnienia i blokady odcinków torowiska. Tramwaj, który trafi na blokadę, powinien poczekać, a powstałe opóźnienie ma przechodzić na kolejne przystanki. Potem porównamy działanie sieci bez blokady i z blokadą.

