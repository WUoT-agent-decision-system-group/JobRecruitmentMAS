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
2. Stworzony obiekt nie ma wartości atrybutu `_id` i chcemy, żeby MongoDB nadało je automatycznie. Wtedy w klasie odpowiedniego modelu należy przeciążyć metodę `to_db_format` i dodać do niej linijkę `delattr(self, _id)`. Chodzi o to, że metoda `to_db_format` jest wywoływana w metodzie `create` w klasie `BaseRepository` i domyślnie zamienia ona `_id` w postaci stringa na ObjectId. W tym przypadku chcemy usunąć atrybut `_id` z naszego obiektu, tak aby MongoDB samo je przydzieliło. Następnie nadane `_id` jest zwracane z metody `create`, a zatem można je ponownie przypisać do naszego obiektu.
