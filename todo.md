# TODO List

## Mandatory

- [X] Add timestamp to each user prompt -> do not do that
- [ ] Make users multi-thread safe
- [X] When relevant, insert timestamp in tool instruction message
- [ ] Build tool server
- [ ] Make tools remote working
- [X] Call tools from server in house-app
- [X] Research: How to use the bot with another user?
- [X] Deployment on Pi Zero
- [X] Buggy, when schedule fires during chat, or two schedules fire at the same time. Collision in tool calls
- [X] Schedule calls should be done in separate chat - but main chat has to be informed regarding result
- [ ] User-Data Object is not well done - handle better and more efficient

## Optional

- [ ] Research: Dynamically load dependencies for different tools
- [ ] Dynamically load tools (on the fly?)
- [ ] Document and outsource tools that can be used otherwise
- [ ] Restructure project
- [ ] When there are too many tools, use a vector database to store them and load them on the fly
- [ ] Find solution for stupid imports in ai_responses and toolbox -> should work with some inits

## Tools

- [X] Energieverbrauch vom Haus
- [X] Filter Energy Request for relevant data
- [X] Energiekosten pro kwh pro Stunde
- [X] Filtere die Energiekosten auf die noch kommenden Stunden
- [X] Wallbox Steuerung
- [X] Filter Wallbox Requests for relevant data
- [X] Auto API
- [X] Tibber API
- [X] Waschmaschine
- [X] Trockner
- [X] Sonnenaufgang & Sonnenuntergang
- [X] Wetter
- [X] Unwettermeldungen
- [X] Müllabfuhr-Termine
- [X] TODO-Liste API/APP
- [X] Persist TODO-Liste
- [X] Reminder App - also API mit Thread, die Erinnerungen per Telegram auslöst
  - [X] Aufsetzend auf der Reminder App: Push-Nachrichten für ...:
  - [X] ... Müllabfuhr-Termine
  - [X] ... Unwettermeldungen
  - [X] ... Tagesbericht für heute: Wetter, Müll, Sonnenaufgang/-untergang
  - [X] ... fällige ToDo-Items
- [X] Neuigkeiten aus dem Web
- [ ] Zusammenfassung einer Webseite
- [ ] PodCast auf Basis einer Webseite
