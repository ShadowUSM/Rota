# ROTA 2.0

Aplikacja do planowania rotacji pracy, czasu w domu i podróży.

## Szybkie uruchomienie

Otwórz `dist/index.html` w przeglądarce. Ten sam plik jest przekazany osobno jako `index.html`. Nie wymaga instalowania bibliotek ani internetu do obliczeń, PDF, PNG i QR. Podgląd załącznika w komunikatorze może nie obsługiwać zapisu danych; korzystaj z pełnej przeglądarki.

Jeżeli poprzednia aplikacja działała pod stałym adresem, zastąp jej plik nową wersją pod tym samym adresem. Przy pierwszym otwarciu ROTA przenosi profile, tolerancje i notatki zapisane przez poprzednią wersję. Notatki stają się wydarzeniami. Dane w różnych przeglądarkach oraz otwierane z różnych lokalizacji pliku nie muszą korzystać z tej samej pamięci.

Najpierw pobierz kopię JSON w sekcji **Dane**. Kopia zawiera wszystkie profile, historię i ustawienia, ale nie zawiera klucza synchronizacji. Stare klucze zapisu pozostają zachowane po migracji.

## Korzystanie

1. **Ustawienia:** wybierz profil, cykl oraz datę, od której mają obowiązywać nowe zasady. Wcześniejsze dni pozostają według poprzedniego grafiku.
2. **Kalendarz:** przełącz miesiąc, pełny cykl lub rok. Kliknij dzień, aby otworzyć jego szczegóły.
3. **Rotacje / Zmień:** wskaż nowy termin. Możesz przesunąć następne rotacje, zachować kolejną zmianę albo podać ją ręcznie. W symulacji można też sprawdzić inną długość pracy i pobytu w domu. Najpierw zobaczysz wpływ zmiany; dopiero potem ją zapiszesz.
4. **Potwierdzenia:** oznacz zmianę jako planowaną, potwierdzoną lub zrealizowaną. Aby zmienić przyszły cykl obejmujący inny potwierdzony termin, najpierw zmień status tamtego terminu na planowany. Zrealizowane daty nie mogą leżeć w przyszłości.
5. **Planer:** sprawdź termin lub znajdź wolne okno. Tolerancja, podróże, wydarzenia blokujące i zapas dni są uwzględniane.
6. **Porównanie:** wybierz profile. Wynik podaje wspólne okna, weekendy i najdłuższy wspólny okres. Oś czasu pokazuje do 93 dni, podsumowanie obejmuje cały wybrany zakres.
7. **Wydarzenia:** dodaj wydarzenia, także coroczne, podróże z listą przygotowań oraz terminy ważności dokumentów. Coroczne wydarzenie 29 lutego występuje tylko w roku przestępnym.
8. **Historia:** cofnij ostatnią operację. Zachowywanych jest do 20 operacji, obejmujących wszystkie profile.
9. **Dane:** pobierz PDF, PNG, ICS lub pełną kopię JSON. Import pozwala dodać profile albo zastąpić dane.

W statystykach „zrealizowane” oznacza dni do dzisiaj z okresu, którego początek ręcznie oznaczono jako zrealizowany. Upływ daty nie jest automatycznym potwierdzeniem. „Praca” oznacza okres pobytu w pracy według rotacji, nie ewidencję przepracowanych godzin.

## Animacje

Obok licznika wyświetlana jest postać odpoczywająca na leżaku z drinkiem albo statek kołyszący się na falach. Przed zmianą i w dniu rozpoczęcia nowego okresu pojawia się pakowanie. Domyślny próg to dwa dni; można go zmienić od 0 do 14 dni. Dni podróży również pokazują przygotowania. Animacje można wyłączyć. Systemowe ustawienie ograniczenia ruchu zatrzymuje animacje i pozostawia ilustrację.

## Przypomnienia

Aplikacja sprawdza przypomnienia co minutę, po otwarciu i po powrocie do okna. Dostarczenie powiadomień wymaga zgody przeglądarki. Kiedy aplikacja jest zamknięta lub uśpiona przez telefon, nie uruchamia samodzielnie zaplanowanych powiadomień. Do takich przypomnień służy eksport ICS z alarmami i import do kalendarza telefonu. Obsługa alarmów zależy od aplikacji kalendarza.

ICS jest eksportem, nie abonamentem kalendarza. Po dużej zmianie grafiku najbezpieczniej zastąpić dedykowany kalendarz ROTA nowym eksportem, aby nie pozostawić starych wydarzeń. Identyfikatory zdarzeń zawierają profil. Wydarzenia z godziną mają czas lokalny, a domyślny czas trwania to godzina; dla zakresu kilku dni kończą się godzinę po wskazanej godzinie ostatniego dnia.

## Instalacja i offline jako witryna

Na swoim hostingu HTTPS umieść wszystkie pliki z `dist/` w tym samym katalogu. Otwórz stronę raz online i poczekaj na informację „Witryna zapisana do pracy offline”. Możesz potem zainstalować ją z menu przeglądarki. Aktualizacja instalowanej wersji aktywuje się po zamknięciu wszystkich jej kart. Dane grafiku są przechowywane oddzielnie od pamięci plików aplikacji.

Sam plik HTML działa offline bez serwera, ale instalacja jako witryna i jej pamięć offline wymagają pełnego pakietu. Gdy pracujesz z plikiem lokalnym, udostępniaj profil JSON. Link i QR wymagają docelowego adresu witryny dostępnej dla odbiorcy.

## Synchronizacja telefonu i komputera

Pakiet zawiera działający serwer synchronizacji, ale nie jest wdrożony na zewnętrznym hostingu. Do stałej synchronizacji potrzebny jest serwer dostępny dla obu urządzeń.

### Próba na własnym komputerze

Wymagany Python 3.10 lub nowszy, bez dodatkowych bibliotek:

```sh
python3 server.py
```

W Windows można użyć `py server.py`. Otwórz `http://127.0.0.1:8787`.

W sekcji **Dane → Synchronizacja urządzeń** wpisz ten adres, wygeneruj klucz, wybierz **Połącz**, następnie **Synchronizuj teraz**. Drugie środowisko przeglądarki na tym komputerze może użyć tego samego adresu i klucza do testu. Sam adres localhost nie zapewnia połączenia z telefonem.

### Dostęp z telefonu i innych komputerów

Uruchom serwer za reverse proxy HTTPS na swoim hostingu/VPS. Proxy powinno przekazywać zapytania do `127.0.0.1:8787`. Przykładowa konfiguracja Caddy po wskazaniu własnej domeny:

```caddyfile
rota.twoja-domena.pl {
    reverse_proxy 127.0.0.1:8787
}
```

Ustaw `ROTA_ORIGIN=https://rota.twoja-domena.pl` w środowisku procesu serwera. Jeśli frontend jest na innym hostingu, `ROTA_ORIGIN` powinien wskazywać dokładnie jego origin, bez ścieżki. Serwer można uruchomić na innym porcie przez `--port`, a lokalizację bazy podać przez `--db`.

Na obu urządzeniach podaj ten sam adres HTTPS serwera i ten sam wygenerowany klucz. Klucz jest hasłem do wspólnego zestawu danych. Nie umieszczaj go w publicznym repozytorium ani w adresie URL. Synchronizacja odbywa się ręcznie, po naciśnięciu przycisku. Przy konflikcie możesz pobrać wersję serwera, wysłać lokalną lub zachować oba zestawy profili.

Serwer zapisuje dane w SQLite. W bazie jest skrót klucza, ale same dane nie są szyfrowane od końca do końca; administrator serwera ma do nich dostęp. Plik bazy trzeba uwzględnić w kopiach serwera. Serwer nie udostępnia bazy ani kodu źródłowego przez HTTP. Nie otwieraj publicznie portu HTTP, korzystaj z HTTPS reverse proxy. Dostęp do samego interfejsu może dodatkowo chronić uwierzytelnianie na proxy.

Po pobraniu wersji z serwera poprzedni stan lokalny można pobrać przyciskiem kopii odzyskiwania w sekcji Dane. Zwykły eksport JSON nie przenosi konfiguracji połączenia.

## Kod i testy

`src/core.js` jest wspólnym silnikiem statusu dnia. Kalendarz, planer, statystyki i eksport używają tego samego modelu. `src/app.js` zawiera interfejs, zapis i synchronizację; `src/animations.js` ilustracje SVG; `src/export.js` generatory plików.

Budowanie pojedynczego pliku po edycji źródeł:

```sh
python3 build.py
node --test tests/core.test.js
```

Dodatkowe testy przeglądarkowe w `tests/browser.test.js` wymagają Playwright i Chromium. Test serwera w `tests/sync.test.py` wymaga uruchomionego lokalnego serwera na porcie 8787. Testy nie korzystają z rzeczywistych danych użytkownika.

Wbudowane biblioteki: jsPDF 2.5.1 (MIT), qrcode-generator 1.4.4 (MIT), font Inter (SIL Open Font License). Kopie bibliotek zawierają informacje licencyjne; fonty pochodzą z oryginalnego pliku aplikacji. Brak zewnętrznych połączeń dla PDF i QR.
