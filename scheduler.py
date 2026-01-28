import schedule
import time
from fetch_attendance import fetch_attendance

schedule.every().day.at("17:01").do(fetch_attendance)

while True:
    schedule.run_pending()
    time.sleep(60)
