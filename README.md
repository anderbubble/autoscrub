<!-- Any copyright is dedicated to the Public Domain.
   - https://creativecommons.org/publicdomain/zero/1.0/ -->

# autoscrub

A policy-based ZFS auto-scrubber.

Inspired by [syncoid](https://github.com/jimsalterjrs/sanoid), the
policy-based ZFS auto-snapshotter.


## Example

autoscrub starts scrubs after a certain number of days, counting
either from the start of the previous scrub (`previous=start`, the
default) or the end of the previous scrub (`previous=end`). The
default period is `days=30`. A pool must be defined in the config file
for autoscrub to start a scrub on it.

### autoscrub.ini

```
[tank]
previous=start
days=30

[bowl]
previous=end
days=7
```

## Rationale

> Why not just use a monthly cron job?

There are several corner-cases when running `zpool scrub` directly
from cron or a timer. We've experienced instances where DST changes
caused cron to try to start a scrub twice in two hours, or to skip a
scrub. Using autoscrub obviates this by considering scrubs frequently
and starting scrubs based on relative time records. It also prevents
errors--and/or missed scrubs--in instances where the time to complete
a scrub has crept past the cron cron interval.

Perhaps less common, but still possible with autoscrub, is to
configure a scrub to start after a period of idle; so rather than
"start a scrub every 30 days," which is the kind of thing you can do
with cron, you can "start a scrub after the pool has gone without one
for 30 days," which takes into account how long the scrub itself
takes.

In the future, it will also be possible to configure autoscrub to
limit the number of simultaneous scrubs. e.g., in a system with many
pools, it may be desirable to limit the number of scrubs that are
running at any given time. In this case, autoscrub will evaluate all
pools eligible for scrubbing against a sorting metric and start only
an allowed number of scrubs.


## autoscrub command-line options

+ --config

	Specify a location for the config file. Defaults to /etc/autoscrub.ini

+ --force

	Start scrubs on configured pools now, ignoring the schedule.

+ -v, --verbose

	Increase logging verbosity (by lowering the log level). Can be
	specified multiple times.

+ -q, --quiet

        Decrease logging verbosity (by raising the log level). Can be
        specified multiple times.

+ --help

	Show help message.


## Install

In lieu of packages, the simplest way to install autoscrub is by
cloning its repository to `/opt/autoscrub`. From there, the sample
systemd unit files may be copied or linked into the appropriate
places, and a config file defined in `/etc`.

```
git clone https://github.com/anderbubble/autoscrub.git /opt/autoscrub
cp /opt/autoscrub/autoscrub-example.ini /etc/autoscrub.ini
```


### systemd

The sample systemd unit files may be copied or linked into the appropriate
places, and a config file defined in `/etc`.

```
ln -s /opt/autoscrub/autoscrub.service /etc/systemd/system/autoscrub.service
ln -s /opt/autoscrub/autoscrub.timer /etc/systemd/system/autoscrub.timer
systemctl daemon-reload
systemctl enable autoscrub.timer
systemctl start autoscrub.timer
```

### cron

The sample cron file may be copied or linked into `cron.d`.

```
ln -s /opt/autoscrub/autoscrub-cron /etc/cron.d/autoscrub
```

## License and copyright

autoscrub is distributed under the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright 2020 Jonathon Anderson, civilfritz.net
