import schedule
import time
import connect

def job():
    connect.put_data()


schedule.every(6).hour.do(job)
schedule.run_pending()
    time.sleep(1)