#!/usr/bin/env python3


import argparse
import configparser
import datetime
import logging
import re
import subprocess
import sys


LOGGING_FORMAT = 'autoscrub: %(message)s'


scan_p = re.compile(b'^ *scan: *(.*) *$', re.MULTILINE)
scrub_in_progress_p = re.compile(b'^scrub in progress (.*)$')
scan_results_p = re.compile(b'scrub repaired [^ ]+ in ([0-9]+) days ([0-9]+):([0-9]+):([0-9]+) with [0-9]+ errors on (.+)$')


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='/etc/autoscrub.ini')
    parser.add_argument('--force', action='store_true', default=None, help='scrub regardless of the schedule')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase logging')
    parser.add_argument('-q', '--quiet', action='count', default=0, help='decrease logging')
    parser.add_argument('pools', nargs='*', help='limit the pools to scrub')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    log_level = logging.INFO - (args.verbose * 10) + (args.quiet * 10)
    logging.basicConfig(format=LOGGING_FORMAT, level=log_level)

    pools = args.pools if args.pools else config.sections()
    for pool in pools:
        if pool not in config:
            raise Unconfigured(pool)

    for pool in pools:
        if args.force or time_to_scrub(config[pool]['ref'].lower(), pool, int(config[pool]['days'])):
            zpool_scrub(pool)


def handle_exception (func):
    try:
        func()
    except AutoscrubException as ex:
        logging.error(ex)
        sys.exit(ex.retcode)


def time_to_scrub (ref, pool, days):
    try:
        scan_time, end = zpool_status(pool)
    except NotScanned as ex:
        logging.debug(ex)
        return True
    except InProgress:
        logging.debug(ex)
        return False

    start = end - scan_time

    if ref == 'start':
        period_start = start
    elif ref == 'end':
        period_start = end
    else:
        raise ConfigError('unknown value: {0}: ref: {1}'.format(pool, config[pool]['ref']))

    scrub_expected = period_start + datetime.timedelta(days=days)
    return scrub_expected <= datetime.datetime.now()


def zpool_scrub (pool):
    args = ['zpool', 'scrub', pool]
    scrub_p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = scrub_p.communicate()
    if stderr:
        raise ZFSCommandError(stderr.decode().strip())
    logging.info('scrub: {0}'.format(pool))


def zpool_status (pool):
    args = ['zpool', 'status', pool]
    status_p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = status_p.communicate()
    if stderr:
        raise ZFSCommandError(stderr.decode().strip())
    scan_p_match = scan_p.search(stdout)
    if not scan_p_match:
        raise NotScanned('{0}: absent'.format(pool))
    scan_results = scan_p_match.group(1)
    if scan_results == b'none requested':
        raise NotScanned('{0}: {1}'.format(pool, scan_results))
    scan_results_match = scan_results_p.match(scan_results)
    if not scan_results_match:
        in_progress_match = scrub_in_progress_p.match(scan_results)
        if in_progress_match:
            raise InProgress(in_progress_match.group(1).decode())
        raise ParseError('{0}: {1}'.format(pool, scan_results))
    days, hours, minutes, seconds, end = scan_results_match.groups()
    scan_td = datetime.timedelta(
        days = int(days),
        seconds = (
            (int(hours) * 60 * 60)
            + (int(minutes) * 60)
            + int(seconds)),
    )
    end_dt = datetime.datetime.strptime(end.decode(), '%a %b %d %H:%M:%S %Y')
    return (scan_td, end_dt)


class AutoscrubException (Exception):
    prefix = 'unknown'
    retcode = -1

    def __str__ (self):
        return '{0}: {1}'.format(self.prefix, super().__str__())

class AutoscrubError (AutoscrubException):
    prefix = 'error'
    retcode = -2

class NotScanned (AutoscrubException):
    prefix = 'not scanned'

class InProgress (AutoscrubException):
    prefix = 'in progress'

class ConfigError (AutoscrubException):
    prefix = 'config error'
    retcode = 1

class Unconfigured (ConfigError):
    prefix = 'unconfigured'

class ZFSCommandError (AutoscrubError):
    prefix = 'command failed'
    retcode = 2

class ParseError (AutoscrubError):
    prefix = 'parse error'
    retcode = 3


if __name__ == '__main__':
    handle_exception(main)
