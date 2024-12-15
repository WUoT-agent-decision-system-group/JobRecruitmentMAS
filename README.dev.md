# Tips for devs

### Aby VSC podpowiadał fajnie składnie to zrobiłem sb venva

Wersja z **virtualenv**:
1. `sudo apt install python3-virtualenv`
2. `virtualenv venv --python=/usr/bin/python3.10` - odpalenie venva z pytongiem 3.10, uwaga na ścieżke
3. `pip install -r requirements/dev.txt` - instalacja requirements w środowisku

Można wykorzystać też **condę**:
1. `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh` - pobranie pliku `.sh`
2. `bash Miniconda3-latest-Linux-x86_64.sh` - uruchomienie instalatora
3. `source ~/.bashrc` - ponowne wczytanie ustawień terminala
4. `conda create --name aasd python==3.10` - stworzenie wirtualnego środowiska o nazwie `aasd` z pytongiem 3.10
5. `conda activate aasd` - uruchomienie stworzonego środowiska
6. `pip install -r requirements/dev.txt` - instalacja requirements w środowisku

### Formatowanie

Zainstalowanie zależności z pliku `dev.txt` prócz wymaganych paczek dodaje również dwa lintery - `black` i `isort`. Jeśli Wam się nie chce ustawiać formatowania w VSC, to aby sformatować, kod wystarczy odpalić: `make format`.

### Bazowy agent - funkcjonalności

1. Czeka na inicjalizacje serwera - problem z zajęć rozwiązany. Nadpisuje bazową metodę ze spade, więc użycie agentów się nie zmienia.
2. Wczytuje z pliku `app/config.json` login i hasło do serwera, w przyszłości też pewnie konfig bazy
3. Tworzy loggera per instancja klasy agenta

   - każda instancja agenta ma swój oddzielny plik dla lepszej czytelności, pewnie kiedyś nam się przyda w szukaniu błędów
   - logi są zapisywane w folderze `logs` na głównym poziomie repo
   - wypisywane też w konsoli.
   - nigdy nie używać `print` w agentach, tylko `self.logger`

### Baza danych - MongoDB

1. Polecam pobrać sobie MongoDB Compass (gui do bazy danych).
2. Adres bazy to `mongodb://localhost:27017` - port wystawiony z kontenera (taki uri wpisać w New Connection w Compass)
3. Tam są funkcjonalności eksportu i importu kolekcji (odpowiednik tabel w sql), więc będziemy mogli się wymieniać danymi za pomocą csv

### UWAGA

1. Żeby mongo sie nie popłakało na widok enuma, operujmy zawsze na `.value` w enumach (w bazie będą zapisane inty), np.:

```
jobOffer1.status = JobOfferStatus.CLOSED.value
repository.update(jobOffer1.id, jobOffer1)
```

2. Mongo ma swój format idków, w momencie gdy czytamy go z bazy to w konstruktorach wszystkie id zamieniamy na stringi. Natomiast gdy robimy jakiś create/update to powinniśmy zawsze konwertować string do ObjectId.
   - w `BaseRepository` w `create` mamy to załatwione gdy przeciążymy metodę `to_db_format` w klasie modelowej.
   - do operacji `update` po prostu trzeba dobrze tworzyć słowniki. Pomocne metody: `map_id` i `map_ids` w `helpers`.

### Podstawowa konfiguracja bazy danych

Nasz system zakłada, że w kontenerze z mongo stworzona jest baza danych o nazie `aasd`. Również zakładamy, że w bazie znajduje się minimum jeden obiekt z ofertą pracy w kolekcji `jobOffers` (w przeciwnym przypadku kontener `spade_agent` kończy swoje działanie). Aby to uzyskać należy:
1. Przejść do folderu `scripts`
2. Wywołać skrypt: `./init_aasd_db.sh`

Po wykonaniu tego skryptu warto uruchomić `docker-compose up aasd_system`. Sprawi to, że kontener `spade_agent` zacznie ponownie działać.

### Dodawanie aplikacji do systemu (do bazy)

1. W folderze `docs` umieścić plik CV w pdfie.
2. Przejść do folderu `scripts`
3. Wywołać `./apply_for_job.sh <joboffer_id> <candidate_id> <candidate_name> <candidate_surname> <candidate_email> <cv_filename> <cv-object-id (w formacie mongo)>`.

   Skrypt wstawi plik do bazy oraz doda aplikacje do stanowiska pracy. UWAGA: powinna być max 1 aplikacja danego kandydata na dane stanowisko, uwaga na candidate_id

   Przykład: `./apply_for_job.sh 674aff48c8c935e125c43939 674aff48c8c935e125c43326 jan testowy jantestowy@gmail.com cv-template.pdf fffffffffffffffffffffff1`

### Umieszczanie w bazie nowego obiektu
Istnieją dwie możliwości:
1. Obiekt stworzony w kodzie ma już nadaną wartość atrybutu `_id`. Wtedy po prostu wystarczy przekazać ten obiekt do metody `create` z odpowiedniego repozytorium i MongoDB stworzy obiekt z podanym `_id`.
2. Stworzony obiekt nie ma wartości atrybutu `_id` i chcemy, żeby MongoDB nadało je automatycznie. Wtedy w klasie odpowiedniego modelu należy przeciążyć metodę `to_db_format` i dodać do niej linijkę `delattr(self, _id)` (bez wywoływania metody z klasy bazowej !). Chodzi o to, że metoda `to_db_format` jest wywoływana w metodzie `create` w klasie `BaseRepository` i domyślnie zamienia ona `_id` w postaci stringa na ObjectId. W tym przypadku chcemy usunąć atrybut `_id` z naszego obiektu, tak aby MongoDB samo je przydzieliło. Następnie nadane `_id` jest zwracane z metody `create`, a zatem można je ponownie przypisać do naszego obiektu.

### Flow analizy CV
`JOM` skanuje przeprocesowane aplikacje i po natrafieniu na jakieś natychmaist wysyła do `AnalyzerAgent` wiadomość o każdym z tych zgłoszeń. Instacji analizatorów jest kilka, a ich wybór podejmowany jest losowo w celu zapewnienia load balancingu. Liczbę instancji analizatora kontroluje zmienna `ANALYZER_INSTANCES` w `main.py`. 
Analizator po otrzymaniu wiadomości o potrzebie analizy CV dołączonego do aplikacji:

1. zmienia jej stan na `IN_ANALYSIS`
2. przeprowadza analizę w ramach aktywności RateCandidate (śpi minutę)
3. zmienia stan aplikacji na `ANALYZED`
4. przesyła wiadomość z randomowym wynikiem analizy do `RecruitmentManagerAgent`, który zapisuje ją w bazie

### Flow komunikacji pomiędzy RM agentem a RSM agentami
- Podczas tworzenia bazy daych (skrypt: `./init_aasd_db.sh`) tworzy się obiekt `RecruitmentInstruction`, który zawiera informacje dotyczące szczegółów przeprowadzania kolejnych etapów rekrutacji.
- Domyślnie w bazie znajduje się instrukcja, która posiada tablicę `stage_priorities` równą [1,1,2] (oznacza to, że najpierw mają wystartować 2 pierwsze agenty, a trzeci musi poczekać) oraz tablicę `stage_types` równą [1,2,3] (czyli agent pierwszy ma typ 1 itd.).
- Podczas uruchomienia systemu startują agenty o identyfikatorach 0 i 1, a agent 2 czeka, wysyłając co jakiś czas pytanie o to, czy już może wystartować.
- Aby zasymulować zakończenie wykonywania etapu należy z poziomu katalogu `scripts` wywołać skrypt `end_stage.sh` (przykładowo: `./end_stage.sh 0 45` oznacza zakończenie etapu o identyfikatorze 0 z wynikiem 45). Podczas pisania kodu przyjąłem założenie, że do stanu `DONE` mogą przejść jedynie etapy będące w statusie `IN_PROGRESS` (ma to przełożenie na rzeczywistość, bo niemożliwe jest by etap został wykonany przez rozpoczęciem jego wykonywania). Z tego względu, teoretycznie można tym skryptem zakończyć działanie etapu, który dopiero jest statusie `CREATED`, ale może to spowodować nieprawdiłowe działanie systemu.
- Jeśli dany etap kończy swoje działanie, wysyła do `RM` uzyskany rezultat.
- Obiekt typu `Recruitment` posiada atrybut `current_priority`, który jest inkrementowany o 1, jeśli wszystkie etapy o obecnym priorytecie są zakończone. Dla przykładu: jeśli powyższym skryptem zakończymy etapy o identyfikatorach 0 i 1, atrybut `current_priority` jest aktualizowany do wartości 2, co oznacza, że etap o identyfikatorze 2 może wystartować.
- Jeśli wszystkie etapy się kończą, ostateczna wartość atrybutu `current_priority` jest równa `max(stage_priorities) + 1`. Jeśli taka wartość jest osiągana, oznacza to, że należy zakończyć zachowanie `AgentCommunication`, ponieważ wszystkie RSM zakończyły swoje działanie. Próbowałem również wyłapywać warunek końcowy poprzez sprawdzanie czy wszystkie etapy mają status `DONE`. ALE to raz działało, raz nie, ponieważ zdarzały się przypadki, że zachowanie `AgentCommunication` kończyło swoje działanie przed otrzymaniem informacji o rezultacie ostatniego etapu. Wynikało to z tego, że RSM potrzebuje pewnego czasu, aby wyłapać informację o tym, że etap się zakończył i wysłać informacje do RM. Jeżeli w tym przedziale czasu (pomiędzy zakończeniem ostatniego etapu a wysłaniem rezultatu) RM uruchomił sprawdzenie czy wszystkie etapy się zakończyły, `AgentCommunication` się kończyło. A właśnie sprawdzanie sprawdzanie wartości `current_priority` jest o tyle dobre, że tutaj to nie nastąpi (wartość `max(stage_priorities) + 1` zostanie osiągnięta tylko wtedy, gdy wszystkie etapy o najwyższym możliwym priorytecie się zakończyły i WYSŁAŁY swoje rezultaty - modyfikacja `current_priority` następuje w metodzie wywoływanej przy otrzymaniu rezultatu etapu). Nawet jeśli dojdzie do sytuacji, że wszystkie etapy o najwyższym priorytecie zakończyły swoje działanie w tym samym czasie, to wtedy gdy przyjdzie wiadomość z rezultatem pierwszego z nich, wartość `current_priority` zostanie faktycznie ustawiona na `max(stage_priorities) + 1`, ALE `AgentCommunication` nie zakończy swojego działania, ponieważ sprawdzanie wartości tego atrybutu następuje w przypadku, gdy otrzymana wiadomość to `None` (a ustawiony timeout w metodzie `receive` jest 2 razy większy niż częstotliwość sprawdzania statusu etapu przez RSM).
- Jak coś, to wszystko, co przychodzi, co jest tworzone, co jest wysyłane itp. jest w logach.
