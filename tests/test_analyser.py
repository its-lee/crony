import sys
import os
from datetime import datetime

import unittest
from crontab import CronTab

import crony.analyser

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")

def get_job_occurrences(lines, **kwargs):
    return list(crony.analyser.get_job_occurrences(
        CronTab(tab="\n".join(lines)), 
        **kwargs
        ))

class AnalyserTest(unittest.TestCase):

    def test_basic(self):
        jobs = get_job_occurrences([
                '* * * * * enabled',
                '#* * * * * disabled',
                'invalid_line'
            ],
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-01 00:30:00'),
            include_disabled=False      # Gets more coverage
        )

        for job in jobs:
            job.line
            job.command
            for o in job.occurrences:
                str(o)
        # TODO: set up some parameterised cases, and edge cases. the only testing done so far catches exceptions

    def test_even_more_basic(self):
        jobs = get_job_occurrences([
                '* * * * * enabled',
            ],
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-01 00:03:00'),
            include_disabled=False      # Gets more coverage
        )

        self.assertEquals(1, len(jobs))
        job = jobs[0]
        self.assertEquals('enabled', job.command)
        self.assertEquals(3, len(list(job.occurrences)))
        print(list(job.occurrences))