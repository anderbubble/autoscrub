#!/usr/bin/env python3


import argparse
import configparser
import datetime
import re
import subprocess


scan_p = re.compile(b'^ *scan: *(.*) *$', re.MULTILINE)
scan_results_p = re.compile(b'scrub repaired [^ ]+ in ([0-9]+) days ([0-9]+):([0-9]+):([0-9]+) with [0-9]+ errors on (.+)$')


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument('pools', nargs='*')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('autoscrub.ini')

    for pool in config.sections():
        if args.pools and pool not in args.pools:
            continue
        try:
            scan_time, end = zpool_status(pool)
        except NotScanned:
            zpool_scrub(pool)
            continue
        start = end - scan_time
        if config[pool]['ref'].lower() == 'start':
            period_start = start
        elif config[pool]['ref'].lower() == 'end':
            period_start = end
        else:
            raise ConfigError('unknown value: {0}: ref: {1}'.format(pool, config[pool]['ref']))
        scrub_expected = period_start + datetime.timedelta(days=int(config[pool]['days']))
        if scrub_expected <= datetime.datetime.now():
            zpool_scrub(pool)


def zpool_scrub (pool):
    args = ['zpool', 'scrub', pool]
    scrub_p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = scrub_p.communicate()
    if stderr:
        raise ZFSCommandError(stderr)


def zpool_status (pool):
    args = ['zpool', 'status', '-vp', pool]
    status_p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = status_p.communicate()
    if stderr:
        raise ZFSCommandError(stderr)
    scan_p_match = scan_p.search(stdout)
    if not scan_p_match:
        raise NotScanned('{0}: absent'.format(pool))
    scan_results = scan_p_match.group(1)
    if scan_results == b'none requested':
        raise NotScanned('{0}: {1}'.format(pool, scan_results))
    scan_results_match = scan_results_p.match(scan_results)
    if not scan_results_match:
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
    retcode = -1

class AutoscrubError (AutoscrubException):
    retcode = -2

class NotScanned (AutoscrubException): pass

class ConfigError (Exception):
    retcode = 1

class ZFSCommandError (AutoscrubError):
    retcode = 2

class ParseError (AutoscrubError):
    retcode = 3


if __name__ == '__main__':
    main()
