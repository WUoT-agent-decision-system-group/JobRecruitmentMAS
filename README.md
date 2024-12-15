## Projekt: Wirtualny Rekruter
Wszystkie opisy dotyczące architektury rozwiązania oraz komunikacji w systemie znajdują się w sprawozdaniu. 

### Uruchomienie
Uwaga: Jeżeli poniższe kroki nie będą działać to najprawdopodobniej użytkownik nie nie ma odpowiednich uprawnień i 
jest niezbędne wykonanie komendy `sudo usermod -aG docker $USER` i zrestartowanie komputera.

#### Podstawowa konfiguracja bazy danych

Nasz system zakłada, że w kontenerze z mongo stworzona jest baza danych o nazie `aasd`. Aby to uzyskać należy:
1. W pierwszym terminalu uruchomić komendę 
   `sudo docker-compose up aasd_mongodb` 
2. W drugim terminalu przejść do folderu `scripts`
3. W drugim terminalu wywołać skrypt: `./init_aasd_db.sh`
4. Zakończyć działanie bazy danych w pierwszym terminalu.

Alternatywnym rozwiązaniem innym niż uruchomienie przygotowanego skrytpu jest samodzielne stworzenie bazy danych. 

#### Uruchamianie 
Aby uruchomić cały system należy:
1. Wykonać komendę `sudo docker-compose build`
2. Wykonać komendę `sudo docker-compose up`


### Interakcja z systemem
Interakcja z systemem wymaga otwarcia drugiego terminala.

#### Dodawanie aplikacji do systemu 

1. W folderze `docs` umieścić plik CV w pdfie. (przykładowy plik już tam jest)
2. Przejść do folderu `scripts`
3. Wywołać `./apply_for_job.sh <joboffer_id> <candidate_id> <candidate_name> <candidate_surname> <candidate_email> <cv_filename> <cv-object-id (w formacie mongo)>`.

   Skrypt wstawi plik z cv do bazy danych oraz doda aplikacje do danego stanowiska pracy. UWAGA: Powinna być maksymalnie 1 aplikacja danego kandydata na dane stanowisko, więc uprasza się o pilnowanie właściowości candidate_id

   Przykład: `./apply_for_job.sh 674aff48c8c935e125c43939 674aff48c8c935e125c43326 jan testowy jantestowy@gmail.com cv-template.pdf fffffffffffffffffffffff1`


#### Symulacja kończenia etapu rekrutacji 

1. Przejść do folderu `scripts`
2. Wywołać `./end_stage.sh  <recruitmentStage_id> <result>`.

   Skrypt zasymuluje wykonanie etapu. Aby wiedzieć skąd wziąć prawidłowe recruitmentStage_id należy albo sprawdzić to w bazie danych lub wziąć odpowiednie id z logów. 

   Przykład: `./end_stage.sh  675ef49657dca5987881d893 20`


### Logi 
W logach widoczna jest komunikacja między agentami. Kolejne logi są doklejane do istniejącego pliku. Należy więc o usuwaniu logów w razie potrzeby. 

