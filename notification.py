import datetime
from plyer import notification

time1="10:00"
timetest=datetime.now()
if timetest==time1:
    notification.notify(
        title = "Reminder",
        message = "It's Time to take your medicine",
        timeout = 2
    )