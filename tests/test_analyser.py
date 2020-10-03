import sys
import os
from datetime import datetime, timedelta

from crontab import CronTab
import unittest
from parameterized import parameterized, param

import crony.analyser

# A reminder on the cron format:
#
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command to execute>

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")

def get_job_occurrences(lines, **kwargs):
    return list(crony.analyser.get_job_occurrences(
        CronTab(tab="\n".join(lines)), 
        **kwargs
        ))

class AnalyserTest(unittest.TestCase):
    @parameterized.expand([
        param("every minute",               "* * * * *",   31),      # 00, 01, ... , 30
        param("on the hour",                "0 * * * *",   1),
        param("on the hour, non-standard",  "@hourly",     1),
        param("on begin boundary",          "0 0 * * *",   1),
        param("before begin boundary",      "59 23 * * *", 0),
        param("on end boundary",            "30 0 * * *",  1),        
        param("after end boundary",         "31 0 * * *",  0),
        param("really out of schedule",     "59 11 1 1 0", 0),
        param("disabled",                   "#* * * * *",  0,   expected_job_count=0),
        param("disabled, but included",     "#* * * * *",  31,  expected_job_count=1, include_disabled=True),
        # Note that python-crontab logs when it encounters an invalid cron line - 
        # which shows up in the unit tests. It's not a problem as it's a handled
        # error internally, so don't bother investigating it!
        #   Invalid as 0 in position 3 isn't a valid Day Of Month
        param("invalid cron syntax",        "59 11 0 0 0", 0,   expected_job_count=0),
        param("empty line",                 "",            0,   expected_job_count=0, command="")
    ])
    def test_single_line(self, 
        _, 
        schedule, 
        expected_occurrence_count,
        command="it",
        begin="2020-01-01 00:00:00",
        end="2020-01-01 00:30:00",
        include_disabled=False,
        expected_job_count=1,
        ):
        jobs = get_job_occurrences([ 
                f"{schedule} {command}",
            ],
            begin=to_datetime(begin),
            end=to_datetime(end),
            include_disabled=include_disabled
        )

        self.assertEqual(expected_job_count, len(jobs))
        
        if expected_job_count:
            job = jobs[0]
            self.assertEqual(command, job.command)
            self.assertEqual(expected_occurrence_count, len(job.occurrences))

    def test_multi_line(self):
        begin = to_datetime('2020-01-01 00:00:00')
        end = to_datetime('2020-01-01 00:30:00')

        jobs = get_job_occurrences([
                '* * * * * /Users/dog/scan-dog-files > /dev/null 2 > &1 # Check dog files for erroars',
                '#@hourly /Users/dog/full-barkup - abc > /dev/null 2 > &1  # Full hourly barkup',
                'invalid_line'
            ],
            begin=begin,
            end=end,
            include_disabled=False      # Gets more coverage
        )

        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual('/Users/dog/scan-dog-files > /dev/null 2 > &1', job.command)
        self.assertEqual('* * * * * /Users/dog/scan-dog-files > /dev/null 2 > &1 # Check dog files for erroars', job.line)
        self.assertEqual(31, len(job.occurrences))

        cur = begin
        expected = []
        while cur <= end:
            expected.append(cur)
            cur += timedelta(minutes=1)

        # Badly named, this asserts on list length and per-item equality without looking at the order
        self.assertCountEqual(expected, job.occurrences)