import requests
import subprocess

data = requests.get("http://worldtimeapi.org/api/timezone/America/Argentina/Cordoba").json()

aux_datetime = data["datetime"].split("T")

#18-11-2022
_date = aux_datetime[0].split("-")
_date.reverse()
date = "-".join(_date)

#09:41:30
time = aux_datetime[1].split(".")[0]

cmd = "cmd /c "

commands = [
    f"date {date}",
    f"time {time}",
]

for c in commands:
    subprocess.run(cmd + c)
    