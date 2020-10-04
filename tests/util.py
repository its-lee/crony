from datetime import datetime
import os

def write_temp_crontab(lines):
    filepath = "/tmp/test-crontab-" + str(datetime.timestamp(datetime.now()))
    with open(filepath, "w") as f:
        f.write(lines.join(os.linesep))
    return filepath

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")    