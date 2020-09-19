import sys
import os
import datetime
import logging

from crontab import CronTab
from croniter import croniter_range

class CronTabSource:
    def __init__(self, source, **kwargs):
        self.source = source
        self.crontab = CronTab(**kwargs)

def _print_header(exclude_header, crontab, begin, end, **kwargs):
    if exclude_header:
        return

    print(f"Source: {crontab.source}")
    print(f"Begin: {begin}")
    print(f"End: {end}")
    print()

def _get_matching_jobs(crontab, begin, end, **kwargs):
    for job in crontab.crontab:
        schedule = job.schedule(date_from=begin)

        occurrences = 0
        while schedule.get_next() < end:
            occurrences += 1

        if occurrences:
            yield {
                'command': job.command,
                'occurrences': occurrences
            }

def analyse(**kwargs):
    _print_header(**kwargs)

    for job in _get_matching_jobs(**kwargs):
        s = '' if job['occurrence'] == 1 else 's'
        line = job['command'] if kwargs['exclude_occurrences'] else f"{job['command']} - ran {job['occurrence']} time{s}"
        print(line)
