import sys
import os
import datetime
import logging

from crontab import CronTab

def get_scheduled_jobs(crontab, begin, end, **kwargs):
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
