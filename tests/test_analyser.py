import sys
import os
from datetime import datetime

from crontab import CronTab
import unittest
from parameterized import parameterized

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

    @parameterized.expand([
        ("every minute", "* * * * *", 4),      # 00, 01, 02, 03
        ("on the hour", "0 * * * *", 1)
    ])
    def test_single_line(self, _, schedule, expected_occurrence_count):
        expected_command = "it"
        jobs = get_job_occurrences([ 
                f"{schedule} {expected_command}",
            ],
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-01 00:03:00'),
            include_disabled=False      # Gets more coverage
        )

        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual(expected_command, job.command)
        self.assertEqual(expected_occurrence_count, len(job.occurrences))