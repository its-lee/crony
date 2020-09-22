import sys
import os
import datetime
import logging

from crontab import CronTab

_logger = logging.getLogger(__name__)

class JobOccurrences:
    """The representation of a cronjob which has occurred in a period of interest.
    """

    def __init__(self, job, occurrences):
        """Initialiser

        Args:
            job (crontab.CronItem): The occurring job
            occurrences (list): The occurrence datetimes
        """
        self.job = job
        self.occurrences = occurrences

    @property
    def command(self):
        """The command text

        Returns:
            str: The command text
        """
        return self.job.command

    @property
    def line(self):
        """A generated cron job line representing the job

        Returns:
            str: A representation of the cron job line
        """
        # Looking at the source for python-crontab, this can rarely raise an error, which we'll
        # propagate up, rather than returning a lie like '' / None or something we've made
        # which may not be correct..
        #
        # It seems to only be able to fail when using the system user's crontab, where each command
        # has a user name, and no current user exists. The error is:
        #     ValueError("Job to system-cron format, no user set!")
        #
        # We don't provide the ability to open the system user's crontab with the set of options
        # crony supports, so this won't happen, but if it did, this is at least the most honest
        # way to deal with it.
        return self.job.render()

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
        if occurrence > end:
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
