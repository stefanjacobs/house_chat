from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

def job():
    print("Diese Aufgabe wird jeden Montag um 8 Uhr ausgeführt.")

scheduler = BackgroundScheduler()
trigger = CronTrigger(day_of_week='mon', hour=22, minute=5)
scheduler.add_job(job, trigger)
scheduler.start()

# Hauptprogramm läuft weiter
while True:
    time.sleep(5)
