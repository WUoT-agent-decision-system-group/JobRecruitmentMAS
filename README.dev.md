# Tips for devs

### Aby VSC podpowiadał składnie należy użyć venva

Wersja z **virtualenv**:
1. `sudo apt install python3-virtualenv`
2. `virtualenv venv --python=/usr/bin/python3.10` - uruchomienie venva z pythonem 3.10; Uwaga na ścieżkę!
3. `pip install -r requirements/dev.txt` - instalacja requirements w środowisku

Można wykorzystać też **condę**:
1. `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh` - pobranie pliku `.sh`
2. `bash Miniconda3-latest-Linux-x86_64.sh` - uruchomienie instalatora
3. `source ~/.bashrc` - ponowne wczytanie ustawień terminala
4. `conda create --name aasd python==3.10` - stworzenie wirtualnego środowiska o nazwie `aasd` z pytongiem 3.10
5. `conda activate aasd` - uruchomienie stworzonego środowiska
6. `pip install -r requirements/dev.txt` - instalacja requirements w środowisku

### Formatowanie

Zainstalowanie zależności z pliku `dev.txt` prócz wymaganych paczek dodaje również dwa lintery - `black` i `isort`. Aby sformatować kod wystarczy uruchomić: `make format`.

### Bazowy agent - funkcjonalności

1. Czeka na inicjalizacje serwera - problem ze zbyt szybkim uruchomieniem agentów przed serwerem rozwiązany. Zostało to zrealizowane poprzez nadpi bazową metodę ze spade, więc użycie agentów się nie zmienia.
2. Wczytuje z pliku `app/config.json` login i hasło do serwera oraz konfiguracje bazy danych.
3. Tworzy loggera per instancja klasy agenta
   - każda instancja agenta ma swój oddzielny plik dla lepszej czytelności
   - logi są zapisywane w folderze `logs` na głównym poziomie repo
   - wypisywane też w konsoli.
   - nigdy nie używać `print` w agentach, tylko `self.logger`

### Baza danych - MongoDB

1. Polecamy pobrać MongoDB Compass.
2. Adres bazy to `mongodb://localhost:27017` - port wystawiony z kontenera (taki uri wpisać w New Connection w Compass)
3. Mongo zapewnia funkcjonalności eksportu i importu kolekcji, więc można się wymieniać danymi za pomocą csv

### Enumy w MongoDB

1. Żeby mongo sie nie krzyczało na widok enuma, operujmy zawsze na `.value` w enumach (w bazie będą zapisane inty), np.:

```
jobOffer1.status = JobOfferStatus.CLOSED.value
repository.update(jobOffer1.id, jobOffer1)
```

2. Mongo ma swój format idków, w momencie gdy czytamy go z bazy to w konstruktorach wszystkie id zamieniamy na stringi. Natomiast gdy robimy jakiś create/update to powinniśmy zawsze konwertować string do ObjectId.
   - w `BaseRepository` w `create` mamy to załatwione gdy przeciążymy metodę `to_db_format` w klasie modelowej.
   - do operacji `update` po prostu trzeba dobrze tworzyć słowniki. Pomocne metody: `map_id` i `map_ids` w `helpers`.

### Umieszczanie w bazie nowego obiektu
Istnieją dwie możliwości:
1. Obiekt stworzony w kodzie ma już nadaną wartość atrybutu `_id`. Wtedy po prostu wystarczy przekazać ten obiekt do metody `create` z odpowiedniego repozytorium i MongoDB stworzy obiekt z podanym `_id`.
2. Stworzony obiekt nie ma wartości atrybutu `_id` i chcemy, żeby MongoDB nadało je automatycznie. Wtedy w klasie odpowiedniego modelu należy przeciążyć metodę `to_db_format` i dodać do niej linijkę `delattr(self, _id)` (bez wywoływania metody z klasy bazowej !). Chodzi o to, że metoda `to_db_format` jest wywoływana w metodzie `create` w klasie `BaseRepository` i domyślnie zamienia ona `_id` w postaci stringa na ObjectId. W tym przypadku chcemy usunąć atrybut `_id` z naszego obiektu, tak aby MongoDB samo je przydzieliło. Następnie nadane `_id` jest zwracane z metody `create`, a zatem można je ponownie przypisać do naszego obiektu.