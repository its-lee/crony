import sys
import os
import datetime
import logging

from crontab import CronTab

def get_scheduled_jobs(crontab=None, begin=None, end=None, include_disabled=True, **kwargs):
    """Find crontab jobs scheduled within the given time range

    Args:
        crontab (crontab.CronTab): A parsed crontab
        begin (datetime.datetime): The datetime to start analysing at
        end (datetime.datetime): The datetime to end analysing at
        include_disabled (bool): Also analyse enabled jobs?

    Yields:
        list: A list of dicts, one for each job found to be scheduled in the
        given time range
    """
    for job in crontab.crontab:
        if not job.is_valid():
            continue

        if job.is_enabled() or include_disabled:
            continue

        schedule = job.schedule(date_from=begin)

        occurrences = 0
        while schedule.get_next() < end:
            occurrences += 1

        if occurrences:
            yield {
                'command': job.command,
                'occurrences': occurrences
            }
