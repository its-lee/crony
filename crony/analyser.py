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
        begin (datetime): The begin datetime
        end (datetime): The end datetime

    Yields:
        datetime: The datetimes when the job would run
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
        begin (datetime): The datetime to start analysing at (inclusive)
        end (datetime): The datetime to end analysing at (inclusive)
        include_disabled (bool): Also analyse enabled jobs?

    Yields:
        list: A list of Jobs, one for each job found to be scheduled in the
        given time range
    """
    # 'Hacky' treatment to ensure that the passed minute is included in the schedule
    # if it were to match a crontab - python-crontab seems to not include it! 
    # E.g. if the begin time = 00:00:00 and end = 00:01:00 and the crontab is * * * * *
    # you'd only get the second minute as being in the schedule.
    #   We'll try to be as safe as possible about this to avoid weird datetimes..
    begin = datetime.datetime(begin.year, begin.month, begin.day, begin.hour, begin.minute, 0, 0)
    begin -= datetime.timedelta(seconds=1)

    for job in crontab:
        if not job.is_valid():  # pragma: no cover
            # Looking at how crontab.CronTab is written, invalid lines are
            # not included in the iteration.. still, just in case!
            #   Sadly, we can't access what's *in* the line in the python-crontab
            # package as it doesn't seem to store invalid line data
            _logger.debug("Skipping a line as it is not valid")
            continue

        if not (job.is_enabled() or include_disabled):
            _logger.debug(f"Skipping {job.command} as it is disabled")
            continue

        yield JobOccurrences(job, list(_get_occurrences(job, begin, end)))
