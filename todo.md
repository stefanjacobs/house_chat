# TODO List

## Mandatory

- [X] Add timestamp to each user prompt -> do not do that
- [ ] Make users multi-thread safe
- [ ] When relevant, insert timestamp in tool instruction message
- [ ] Build tool server
- [ ] Make tools remote working
- [X] Call tools from server in house-app
- [ ] Research: How to use the bot with another user?
- [X] Deployment on Pi Zero

## Optional

- [ ] Research: Dynamically load dependencies for different tools
- [ ] Dynamically load tools (on the fly?)
- [ ] Document and outsource tools that can be used otherwise
- [ ] Restructure project
- [ ] When there are too many tools, use a vector database to store them and load them on the fly

## Tools

- [X] Energieverbrauch vom Haus
- [ ] Filter Energy Request for relevant data
- [X] Wallbox Steuerung
- [X] Filter Wallbox Requests for relevant data
- [ ] Auto API
- [X] Tibber API
- [X] Waschmaschine
- [X] Trockner
- [X] Sonnenaufgang & Sonnenuntergang
- [X] Wetter
- [ ] Unwettermeldungen
- [X] Müllabfuhr-Termine
- [X] TODO-Liste API/APP
- [X] Persist TODO-Liste
- [ ] Reminder App - also API mit Thread, die Erinnerungen per Telegram auslöst
  - [ ] Aufsetzend auf der Reminder App: Push-Nachrichten für ...:
  - [ ] ... Müllabfuhr-Termine
  - [ ] ... Unwettermeldungen
  - [ ] ... Tagesbericht für heute: Wetter, Müll, Sonnenaufgang/-untergang
  - [ ] ... fällige ToDo-Items
