from datetime import datetime

def write_temp_crontab(tab):
    filepath = "/tmp/test-crontab-" + str(datetime.timestamp(datetime.now()))
    with open(filepath, "w") as f:
        f.write(tab)
    return filepath