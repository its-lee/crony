from datetime import datetime

def write_temp_crontab(tab):
    filepath = "/tmp/test-crontab-" + str(datetime.timestamp(datetime.now()))
    with open(filepath, "w") as f:
        f.write(tab)
    return filepath

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")    