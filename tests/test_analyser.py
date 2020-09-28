import sys
import os
from datetime import datetime

import unittest
from crontab import CronTab

import crony.analyser

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")

def get_job_occurrences(lines, **kwargs):
    return crony.analyser.get_job_occurrences("\n".join(lines), **kwargs)

class AnalyserTest(unittest.TestCase):

    def test_basic(self):
        jobs = get_job_occurrences([
            '* * * * * hiiiii',
            '#* * * * * byeeeee',
            '1 2 bad_line'
            ],
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-02 00:00:00'),
            include_disabled=True
        )
        for job in jobs:
            job.line
            job.command
            for o in job.occurrences:
                str(o)
        # TODO: set up some parameterised cases, and edge cases. the only testing done so far catches exceptions
