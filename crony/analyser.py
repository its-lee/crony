import sys
import os
import datetime
import logging

from crontab import CronTab

_logger = logging.getLogger(__name__)

class JobOccurrences:
    def __init__(self, job, occurrences):
        self.job = job
        self.occurrences = occurrences

    @property
    def command(self):
        return self.job.command

    @property
    def line(self):
        try:
            return self.job.render()
        except:
            _logger.warn(
                f"Failed to render the job with command {self.job.command} as a crontab line")
        return ''

def _get_occurrences(job, begin, end):
    """Yield all occurrences between a begin and end datetime for a job

    Args:
        job (crontab.CronItem): The job to analyse
        begin (datetime.datetime): The begin datetime
        end (datetime.datetime): The end datetime

    Yields:
        datetime.datetime: The datetimes when the job would run
    """
    schedule = job.schedule(date_from=begin)

    while True:
        occurrence = schedule.get_next()
        if occurrence > end
            break
        yield occurrence

def get_job_occurrences(crontab=None, begin=None, end=None, include_disabled=True, **kwargs):
    """Find crontab jobs scheduled within the given time range

    Args:
        crontab (crontab.CronTab): A parsed crontab
        begin (datetime.datetime): The datetime to start analysing at
        end (datetime.datetime): The datetime to end analysing at
        include_disabled (bool): Also analyse enabled jobs?

    Yields:
        list: A list of Jobs, one for each job found to be scheduled in the
        given time range
    """
    for job in crontab:
        if not job.is_valid():
            # Sadly, we can't access what's *in* the line in the python-crontab
            # package as it doesn't seem to store invalid line data
            _logger.debug(f"Skipping a line as it is not valid")
            continue

        if not (job.is_enabled() or include_disabled):
            _logger.debug(f"Skipping {job.command} as it is disabled")
            continue

        occurrences = list(_get_occurrences(job, begin, end))

        # Don't bother yielding jobs which haven't occurred, that's just garbo
        if occurrences:
            yield JobOccurrences(job, occurrences)
