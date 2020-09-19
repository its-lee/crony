import sys
import os

#import croniter
from crontab import CronTab

class CronTabSource:
    def __init__(self, source, **kwargs):
        self.source = source
        self.crontab = CronTab(**kwargs)

def _print_metadata(**kwargs):
    if kwargs['exclude_metadata']:
        return

    print(f"Source: {kwargs['crontab'].source}")
    print(f"Begin: {kwargs['begin']}")
    print(f"End: {kwargs['end']}")
    print()

def analyse(**kwargs):
    _print_metadata(**kwargs)

    