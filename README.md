# Symulacja krakowskiej sieci tramwajowej – checkpoint 2

## Najprostsze wyjasnienie dla prezentujacych

**Checkpoint 1:** wybieralismy godzine i otrzymywalismy jedna mape z przyblizonymi polozeniami tramwajow. Polozenia liczono po prostej miedzy przystankami.

**Checkpoint 2:** uruchamiamy zegar symulacji. Dla kazdego kursu pamietamy, czy czeka, jedzie, stoi na przystanku czy zakonczyl kurs. Rozklad GTFS okresla, kiedy nastapi odjazd i przyjazd. Zdarzenia sa uporzadkowane w kolejce wedlug godziny. Animacja pokazuje obliczona pozycje pomiedzy zdarzeniami. Tam, gdzie dopasowanie sie udaje, punkt jedzie po zakretach z `shapes.txt`, a w pozostalych przypadkach po prostej.

**DES:** to nie jest losowanie i nie musi oznaczac awarii. To sposob prowadzenia symulacji: system zmienia stan w konkretnych momentach (np. odjazd lub przyjazd), zamiast wykonywac cala logike co sekunde. Zdarzenia sa teraz w pelni wyznaczane przez rozklad; losowosc bedzie w checkpoint 3.

## 1. Co robimy w projekcie?

Chcemy zasymulowac ruch tramwajow w Krakowie na podstawie prawdziwych rozkladow jazdy ZTP. Docelowo dojdą opoznienia, blokady torowisk i liczba pasazerow w tramwajach.

Na **checkpoint 1** program wyswietlal siec tramwajowa i obliczal pozycje pojazdow **dla jednej wybranej godziny**.

Na **checkpoint 2** dodalismy **uplyw czasu i zdarzenia**. Program potrafi przejsc przez kolejne godziny rozkladu, a nie tylko policzyc pojedynczy moment.

**To wciaz symulacja zgodna z rozkladem**, a nie odtwarzanie prawdziwych pomiarow GPS. Nie ma jeszcze awarii, opoznien ani pasazerow.

## 2. Co zostalo zrobione?

- Kazdy **kurs GTFS (`trip_id`)** dostaje wlasny obiekt `Tram` ze stanem.
- Jest zegar symulacji (`Simulation.now`) liczony w sekundach.
- Zdarzenia `departure` i `arrival` sa obslugiwane po kolei.
- Tramwaj ma stany `waiting`, `moving`, `stopped`, `finished`.
- Podczas postoju tramwaj **nie znika z mapy**.
- Tramwaje poruszaja sie na mapie w animacji Matplotlib.
- Pozycje podczas jazdy sa wyliczane **wzdluz geometrii z `shapes.txt`**, z zachowaniem zakretow (jesli uda sie dopasowac trase).
- Jest licznik jadacych i stojacych pojazdow oraz opcjonalny zapis zdarzen do CSV.

W odroznieniu od checkpointu 1 tramwaje maja teraz historie stanu, a godziny przyjazdu i odjazdu sa **zdarzeniami**, ktore zmieniaja ten stan.

## 3. Uruchomienie

### Wymagania

- Python 3.10 lub nowszy.
- Polaczenie z internetem przy **pierwszym pobraniu** GTFS.
- Biblioteki `pandas`, `requests`, `matplotlib`.

W terminalu, w katalogu projektu:

```bash
pip install -r requirements.txt
```

Potem:

```bash
python main.py 08:00 2026-11-20
```

To uruchomi animacje od 08:00 do 09:00 **dla daty podanej w poleceniu**. Data musi wystepowac w pobranym GTFS. Przykladowa data powyzej moze nie byc dostepna w archiwum i wtedy trzeba wybrac inna.

Inne przyklady:

```bash
python main.py 07:30 2026-11-20 --duration 30
python main.py 08:00 2026-11-20 --duration 60 --step 60 --interval 150
python main.py 08:00 2026-11-20 --duration 60 --labels 0
python main.py 08:00 2026-11-20 --duration 60 --no-animation --log results/events.csv
```

Parametry:

| Argument | Co robi |
|---|---|
| `08:00` | Godzina rozpoczecia |
| `2026-11-20` | Data z GTFS |
| `--duration 60` | Dlugosc symulacji w **minutach** |
| `--step 30` | Ile **sekund symulacji** mija w jednej klatce |
| `--interval 100` | Co ile **milisekund rzeczywistych** wyswietla sie klatka |
| `--labels 50` | Maksymalna liczba numerow linii na mapie |
| `--no-animation` | Liczy zdarzenia bez wyswietlania okna |
| `--log results/events.csv` | Zapisuje wszystkie przetworzone zdarzenia do CSV |

Jesli uruchomienie z dzisiejsza data pokazuje brak kursow, sprawdz, jaki zakres dat obejmuje archiwum w `data/GTFS_KRK_T.zip`. **Nie wybieraj historycznej daty, jesli masz tylko aktualny plik GTFS.**

### Co jest na mapie?

- Linie – rysowane z `shapes.txt`.
- Czarne punkty – przystanki.
- Czerwone punkty – tramwaje w ruchu.
- Pomaranczowe punkty – tramwaje podczas postoju.
- Male numery obok czesci pojazdow – numery linii (limit dla czytelnosci).
- W lewym gornym rogu – data, godzina, liczba jadacych i stojacych.

Wyswietlanie wykresu wymaga srodowiska z obsluga okien (np. lokalny komputer z Pythonem). Na serwerze bez ekranu mozna uzyc `--no-animation`.

## 4. Pliki projektu

| Plik | Zadanie |
|---|---|
| `gtfs.py` | Pobranie paczki GTFS, wczytanie danych i przygotowanie tabeli rozkladu |
| `simulation.py` | Tramwaje, kolejka zdarzen i zegar symulacji – nowy plik |
| `geometry.py` | Dopasowywanie przystankow do torowiska oraz pozycja na zakretach |
| `main.py` | Argumenty, rysowanie tras i animacja – rozbudowany plik |
| `requirements.txt` | Biblioteki do instalacji |
| `data/GTFS_KRK_T.zip` | Pobierane dane ZTP – nie dodajemy do repozytorium |

### Funkcje z `gtfs.py`

- `download()` – pobiera archiwum, jesli jeszcze go nie ma. Dodalismy sprawdzenie bledu HTTP przez `raise_for_status()`.
- `read(name)` – czyta konkretny plik z ZIP bez recznego rozpakowywania.
- `to_seconds()` – zamienia `08:10:00` na sekundy; obsluguje tez godziny typu `25:10:00`.
- `services(day)` – wybiera `service_id` obowiazujace danego dnia na podstawie `calendar_dates.txt`.
- `timetable(day)` – laczy kursy, linie, przystanki i godziny w jedna tabele, posortowana po `trip_id` i `stop_sequence`.

### Co zawieraja pliki GTFS?

| Plik | Zawartosc | Czy korzystamy? |
|---|---|---|
| `routes.txt` | Linie i ich numery | Tak |
| `trips.txt` | Konkretne kursy, powiazania z linia i trasa | Tak |
| `stop_times.txt` | Kolejne przystanki kursu oraz przyjazdy i odjazdy | Tak |
| `stops.txt` | Przystanki, identyfikatory i wspolrzedne | Tak |
| `shapes.txt` | Punkty geometrii tras | Tak – do rysowania i pozycjonowania tramwajow |
| `calendar_dates.txt` | Daty dodania/wyjatkow uslug | Tak |
| `calendar.txt` | Regularny tygodniowy kalendarz kursowania | Nie w obecnym kodzie |
| `agency.txt` | Dane organizatora/operatora | Nie |
| `feed_info.txt` | Informacje o paczce danych | Nie |
| `blocks.txt` | Dane organizacyjne o obiegach/blokach, zalezne od dostawcy | Nie |

Wazne identyfikatory:

- `route_id` – identyfikator linii; `route_short_name` – numer pokazany na mapie.
- `trip_id` – identyfikator **kursu**, niekoniecznie fizycznego tramwaju.
- `stop_id` – identyfikator punktu przystankowego.
- `shape_id` – identyfikator geometrii trasy.
- `service_id` – okresla, w ktore dni kurs jest wykonywany.

## 5. Jak dziala `simulation.py`?

### `Tram`

Kazdy obiekt przechowuje:

- `trip_id` i `line` – jaki to kurs i linia.
- `stops` – liste przystankow wraz z przyjazdami, odjazdami i wspolrzednymi.
- `index` – do ktorego przystanku dotarl.
- `status` – `waiting`, `moving`, `stopped` albo `finished`.
- `departure` i `arrival` – poczatek i koniec aktualnego przejazdu.

Metoda `position(now)` liczy, jaka czesc czasu przejazdu minela. Jesli kurs ma dopasowana geometrie `shapes.txt`, tramwaj przemieszcza sie **po kolejnych punktach trasy**, a nie po prostej. Jesli nie ma dopasowania, uzywany jest stary wzor:

```text
ratio = (obecny_czas - odjazd) / (przyjazd - odjazd)
pozycja = A + ratio * (B - A)
```

Osobno obliczamy `lat` i `lon` tylko w trybie awaryjnym. Gdy tramwaj stoi, zwracamy pozycje przystanku.

### `Simulation`

Korzystamy z `heapq` – wbudowanej w Pythona **kolejki priorytetowej**, czyli struktury, ktora pozwala szybko pobrac zdarzenie o najwczesniejszej godzinie. Nie potrzebujemy dodatkowej biblioteki SimPy do tak prostego modelu.

Najwazniejsze funkcje:

1. `__init__(timetable)` – tworzy obiekty kursow i pierwsze zdarzenia odjazdu.
2. `schedule(when, kind, trip_id)` – dodaje zdarzenie do kolejki.
3. `advance_to(target)` – obsluguje wszystkie zdarzenia do wskazanej sekundy.
4. `depart(tram)` – zmienia stan na jazde i planuje przyjazd.
5. `arrive(tram)` – zmienia stan na postoj albo konczy kurs; planuje nastepny odjazd.
6. `visible()` – zwraca pojazdy jadace i stojace na przystankach.
7. `stats()` – liczy tramwaje w poszczegolnych stanach.

### Przyklad jednego kursu

| Czas | Zdarzenie | Stan |
|---|---|---|
| 08:00 | Odjazd z A | `moving` |
| 08:04 | Przyjazd do B | `stopped` |
| 08:05 | Odjazd z B | `moving` |
| 08:09 | Przyjazd do C | `finished` |

Zdarzenia przyjazdu/odjazdu zapisujemy w `sim.log`. Mozna je wyeksportowac do CSV.

### Czym DES rozni sie od poprzedniego kodu?

W checkpoint 1 wpisywalismy godzine i za kazdym razem od nowa sprawdzalismy, na jakim odcinku jest kurs.

W checkpoint 2 **mamy stan pojazdu i kolejke zdarzen**. Kiedy symulowany czas dochodzi do odjazdu lub przyjazdu, zmienia sie stan odpowiedniego tramwaju. Mapa tylko pokazuje ten stan.

Wizualizacja odswieza sie co klatke, ale zdarzenia sa obslugiwane tylko wtedy, gdy rzeczywiscie wypadaja w danej chwili.

## 6. Problemy, ktore napotkalismy i jak je rozwiazalismy

### 1. Poprzednio tramwaj znikal podczas postoju

W starym `positions()` wyswietlane byly tylko kursy bedace pomiedzy odjazdem a nastepnym przyjazdem. Teraz po przyjezdzie tramwaj ma status `stopped` i pozostaje na przystanku az do odjazdu.

### 2. Nie bylo uplywu czasu

Wcześniej jedna godzina oznaczala jeden statyczny obraz. Teraz `advance_to()` przesuwa zegar i przetwarza zdarzenia z kolejki w odpowiedniej kolejnosci. `FuncAnimation` wyswietla kolejne stany.

### 3. Jak ustalic kolejnosc zdarzen?

Uzywamy `heapq`. Kazde zdarzenie ma czas i dodatkowy licznik, zeby dwa zdarzenia o tej samej godzinie nie powodowaly problemu z sortowaniem.

### 4. Zbyt duzo numerow linii na mapie

W Krakowie moze byc duzo pojazdow. Domyslnie pokazujemy numer przy maksymalnie 50 tramwajach. Parametrem `--labels 0` mozna wylaczyc opisy.

### 5. Nieudane pobranie danych

Dodano `response.raise_for_status()`, dzieki czemu blad HTTP powoduje wyrazny wyjatek zamiast zapisania niepoprawnego pliku jako ZIP. Nadal warto pozniej dodac obsluge uszkodzonego archiwum.

## 7. Ruch po torowisku – `geometry.py`

W starym kodzie pozycja byla liczona na prostej miedzy przystankami A i B. Teraz uzywamy rzeczywistej geometrii trasy zapisanej w `shapes.txt`.

Jak to dziala:

1. `timetable()` dolacza do kazdego kursu `shape_id` z `trips.txt`.
2. `Simulation()` odczytuje punkty tej trasy, uporzadkowane po `shape_pt_sequence`.
3. `build_path()` oblicza przyblizone odleglosci wzdluz kolejnych punktow trasy (w metrach).
4. `match_stops()` szuka miejsc na tej trasie najblizszych kolejnym przystankom kursu, idac tylko do przodu.
5. `Tram.position()` oblicza udzial uplywu czasu przejazdu i przesuwa tramwaj o taki sam udzial **dlugosci torowiska**, a nie odleglosci w linii prostej.
6. `ShapePath.at()` zwraca wspolrzedne na odpowiednim fragmencie trasy.

Przyklad: tramwaj jedzie A -> zakret -> B przez 10 minut. Po 5 minutach wskaznik jest w polowie **dlugosci drogi po torach**, a nie w polowie prostej A–B.

Dopasowanie jest przyblizone. Jezeli ktorys przystanek jest oddalony od trasy o ponad 200 metrow lub brakuje jej geometrii, caly taki kurs uzywa starej interpolacji liniowej. Informacja jest wypisywana przy starcie:

```text
Trasy GTFS: 100, po prostej (awaryjnie): 2
```

To **przykladowe liczby**, nie wynik sprawdzenia aktualnych danych Krakowa. Warto sprawdzic, czy liczba kursow awaryjnych nie jest duza, a na mapie zweryfikowac petle i kursy specjalne.

## 8. Co jeszcze NIE jest zrobione?

- **Brak opoznien i awarii** – przejazdy odbywaja sie zgodnie z GTFS.
- **Brak pasazerow i napelnienia** – dojdzie pozniej.
- **Nie kazda trasa musi sie dopasowac** – dla brakujacych lub zbyt odleglych `shape_id` pozycja liczona jest po prostej. W terminalu pokazujemy liczbe takich kursow.
- **Nie znamy rzeczywistej predkosci** – zakladamy rowny postep wzdluz odcinka torowiska miedzy przystankami.
- **Zlozone petle i nietypowe przebiegi** – proste dopasowanie kolejnych przystankow moze sie mylic na trasach z petlami; wymaga to weryfikacji na realnej paczce GTFS.
- **Brak dzielenia fizycznego taboru** – na razie kazdy `trip_id` jest osobnym obiektem. Jeden fizyczny tramwaj moze w rzeczywistosci obslugiwac kilka kursow.
- **Brak wspolnego grafu torowisk** – nie ma jeszcze ograniczen zajetosci torow, sygnalizacji ani kolizji.
- **Kursy nocne** – godziny powyzej 24 sa czytane, ale symulacja wybranej daty nie dolacza automatycznie kursow poprzedniego dnia.
- **Aktualnosc archiwum** – raz pobrana paczka nie aktualizuje sie sama.
- **Kalendarz** – bazujemy tylko na `calendar_dates.txt` i `exception_type == 1`, co odpowiada podejsciu ze starego projektu, ale nie jest uniwersalna obsluga calego standardu GTFS.
- **Dodatkowy czas postoju** – jeszcze nie ma dynamicznego czasu wynikajacego z liczby pasazerow.

Nie udajemy, ze system umie te rzeczy. To bedzie robione w nastepnych etapach.

## 9. Co pokazac na checkpoint 2?

Demonstracja na 2–3 minuty:

1. Przypominamy, ze na checkpoint 1 pokazywalismy tramwaje tylko dla jednej godziny.
2. Wyjasniamy DES: zegar i kolejne zdarzenia odjazdu i przyjazdu zmieniaja stan kazdego kursu.
3. Uruchamiamy animacje na GTFS i pokazujemy ruch w czasie.
4. Zwracamy uwage na ruch po zakretach `shapes.txt` oraz postoj na przystankach.
5. Mowimy, ze nadal jest to ruch zgodny z rozkladem, bez GPS i losowych opoznien.
6. Zapowiadamy awarie i blokady na checkpoint 3.

Propozycja wypowiedzi:

> Wczesniej program obliczal polozenie tramwajow tylko dla jednej godziny. Teraz zrobilismy prosty silnik DES: kazdy kurs ma swoj stan, a odjazdy i przyjazdy sa zdarzeniami zapisanymi w kolejce. Dzieki temu mozemy symulowac uplyw czasu, pokazywac jazde i postoje oraz zapisac liste wykonanych zdarzen. To nadal ruch zgodny z rozkladem. Kolejny etap to losowe opoznienia i blokowanie odcinkow torowiska.

## 10. Co planujemy na checkpoint 3?

**Cel: zaklocenia, ktore realnie wplywaja na przebieg symulacji.**

- Dodac losowa zmiennosc czasu przejazdu (parametry zapisane w konfiguracji).
- Przygotowac wspolny model odcinkow torowiska – rozne linie korzystaja czasem z tych samych torow.
- Umiec recznie zablokowac wskazany odcinek na np. 15 minut.
- Sprawic, ze tramwaje czekaja przed blokada, a opoznienie przechodzi na kolejne przystanki.
- Porownac przejazd normalny i przejazd z blokada.

Na razie **bez automatycznych objazdow i bez losowych wykolejen**. Najpierw jedna blokada musi prawidlowo dzialac, zeby mozna bylo zobaczyc wplyw na pozostale tramwaje.

### Publikacje, na ktorych mozna oprzec dalsze założenia

- Drabicki, Islam, Szarata (2021), badanie zaklocen transportu w Krakowie: https://www.mdpi.com/1996-1073/14/16/4889
- Su i in. (2023), symulacja sieci transportowej przy przerwach ruchu: https://doi.org/10.1007/s40864-023-00188-z
- Christoforou, Chandakas, Kaparias (2020), zaleznosc postoju od wymiany pasazerow: https://link.springer.com/article/10.1007/s40864-020-00128-1

Publikacje beda **podstawa do uzasadnienia modeli**, ale parametry nie zostaly jeszcze skalibrowane dla Krakowa.

## 11. Najwazniejsze rzeczy do zapamietania

- **GTFS** – planowany ruch, a nie prawdziwy GPS.
- **Kurs (`trip_id`)** – jeden przejazd z rozkladu, niekoniecznie fizyczny tramwaj.
- **DES** – zegar symulacji i zdarzenia zmieniajace stan.
- **`heapq`** – wbudowana kolejka, ktora wybiera najwczesniejsze zdarzenie.
- **`Tram`** – obiekt przechowujacy informacje i stan kursu.
- **`FuncAnimation`** – odswieza mape, ale nie steruje logika przejazdow.
- **Interpolacja po trasie** – w zwyklym przypadku pozycja lezy na geometrii `shapes.txt`; po prostej tylko gdy nie da sie dopasowac trasy.
- **Checkpoint 3** – opoznienia i blokady torowiska.


## Poprawka postojów na przystankach

W pierwotnej wersji checkpointu 2 stan `stopped` mógł trwać zero sekund, jeżeli godzina przyjazdu i odjazdu w GTFS była taka sama. W nowej wersji każdy **pośredni** przystanek wymaga minimum 15 sekund postoju. To **nasze założenie**, a nie rzeczywisty pomiar ani informacja z GTFS.

Uruchomienie z domyślnym postojem:

```bash
python main.py 08:00 2026-11-20
```

Aby lepiej zobaczyć pomarańczowe tramwaje, można zmniejszyć krok animacji do 5 sekund:

```bash
python main.py 08:00 2026-11-20 --step 5 --stop-time 20
```

`--stop-time 20` wymusza minimum 20 sekund postoju. `--step 5` pokazuje kolejną klatkę co 5 sekund czasu symulacji. Dłuższy postój może przesunąć kolejne przyjazdy i odjazdy względem GTFS. To zachowanie jest celowe, żeby symulacja uwzględniała rzeczywisty upływ czasu i propagację opóźnienia, ale nie należy go przedstawiać jako odwzorowania rzeczywistych postojów ZTP. Przystanek końcowy kończy kurs i nie ma stanu `stopped`.
