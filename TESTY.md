# Weryfikacja ROTA 2.0

Przeprowadzono testy silnika obliczeń oraz działającej aplikacji w Chromium.

## Wyniki

• 16 testów automatycznych logiki rotacji i eksportu ICS: zakończone poprawnie.
• Zmiana pojedynczej rotacji, wariant zachowania kolejnego terminu, podgląd i cofanie: poprawnie.
• Symulacja innej długości cyklu: poprawnie.
• Dodawanie wydarzeń, podróży, dokumentów i odhaczanie listy przygotowań: poprawnie.
• Planer uwzględniający tolerancję i porównanie profili: poprawnie.
• Pobieranie PDF, PNG, ICS oraz JSON: poprawnie. Zweryfikowano polskie znaki w PDF.
• Import kopii jako nowych profili oraz cofnięcie importu: poprawnie.
• Generowanie QR na urządzeniu i import udostępnionego profilu w osobnej przeglądarce: poprawnie.
• Synchronizacja dwóch niezależnych kontekstów przeglądarki i połączenie konfliktujących wersji: poprawnie.
• Serwer: zapis i odczyt, izolacja kluczy, odrzucanie błędnych danych i niedozwolonego origin, konflikt wersji, równoczesny zapis: poprawnie.
• Widoki 390 px i 320 px: brak poziomego przepełnienia strony, wszystkie sekcje dostępne.
• Animacje domu, statku i pakowania, wyłączenie animacji oraz systemowe ograniczenie ruchu: poprawnie.
• Motyw ciemny i zachowanie ustawień po ponownym uruchomieniu: poprawnie.
• Ponowne otwarcie witryny po odłączeniu internetu: poprawnie.
• Samodzielny plik HTML i generowanie PDF bez internetu: poprawnie.
• Automatyczna migracja profili i notatek ze starego zapisu: poprawnie.
• Symulowany brak miejsca w pamięci przeglądarki: widoczna informacja o niezapisanych zmianach, bez fałszywego potwierdzenia.
• Brak błędów JavaScript w głównym teście interfejsu.

## Zakres

Synchronizację zweryfikowano z dołączonym serwerem lokalnym, bez wdrożenia na publiczny hosting. Nie testowano na fizycznym telefonie. Dostarczanie systemowych powiadomień i alarmów po imporcie ICS zależy od uprawnień oraz używanego kalendarza; test sprawdza poprawność zapisu alarmów w pliku.
