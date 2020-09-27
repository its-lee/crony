import sys
import os
from datetime import datetime

import unittest
from crontab import CronTab

import crony.analyser

def to_datetime(s, fmt=None):
    return datetime.strptime(s, fmt if fmt else "%Y-%m-%d %H:%M:%S")

class AnalyserTest(unittest.TestCase):

    def test_basic(self):
        occurrences = crony.analyser.get_job_occurrences(
            crontab=CronTab(tab="
                * * * * * hiiiii
                #* * * * * byeeeee
                1 2 bad_line
            "),
            begin=to_datetime('2020-01-01 00:00:00'),
            end=to_datetime('2020-01-02 00:00:00'),
            include_disabled=True
        )
        for o in occurrences:
            o.line
            o.command
        # TODO: set up some parameterised cases, and edge cases. the only testing done so far catches exceptions
