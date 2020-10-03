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
    @parameterized.expand([
        ("every minute",            "* * * * *", 31),      # 00, 01, ... , 30
        ("on the hour",             "0 * * * *", 1),
        ("on begin boundary",       "0 0 * * *", 1),
        ("before begin boundary",   "59 23 * * *", 0),
        ("on end boundary",         "30 0 * * *", 1),        
        ("after end boundary",      "31 0 * * *", 0),
        ("really out of schedule",  "59 11 0 0 0", 0)

    ])
    def test_single_line(self, _, schedule, expected_occurrence_count):
        expected_command = "it"
        jobs = get_job_occurrences([ 
                f"{schedule} {expected_command}",
            ],
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-01 00:30:00'),
            include_disabled=False      # Gets more coverage
        )

        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual(expected_command, job.command)
        self.assertEqual(expected_occurrence_count, len(job.occurrences))

    def test_multi_line(self):
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
        # TODO: finish this test, and edge cases. the only testing done so far catches exceptions
