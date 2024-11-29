# Tips for devs

### Aby VSC podpowiadał fajnie składnie to zrobiłem sb venva

1. `sudo apt install python3-virtualenv`
2. `virtualenv venv --python=/usr/bin/python3.10` - odpalenie venva z pytongiem 3.10, uwaga na ścieżke
3. wczytać requirements

### Bazowy agent - funkcjonalności

1. Czeka na inicjalizacje serwera - problem z zajęć rozwiązany. Nadpisuje bazową metodę ze spade, więc użycie agentów się nie zmienia.
2. Wczytuje z pliku `app/config.json` login i hasło do serwera, w przyszłości też pewnie konfig bazy
3. Wczytuje z pliku `app/log-config.json` konfiguracje loggera

   - każda instancja agenta ma swój oddzielny plik dla lepszej czytelności, pewnie kiedyś nam się przyda w szukaniu błędów
   - logi są zapisywane w folderze `logs` na głównym poziomie repo
   - wypisywane też w konsoli.
   - nigdy nie używać `print` w agentach, tylko `self.logger`
