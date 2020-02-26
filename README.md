<!-- Any copyright is dedicated to the Public Domain.
   - https://creativecommons.org/publicdomain/zero/1.0/ -->

Policy-based ZFS auto-scrubber

Inspired by syncoid, the policy-based ZFS auto-snapshotter.


## Example

autoscrub starts scrubs after a certain number of days, counting
either from the start of the previous scrub (`ref=start`) or the end
of the previous scrub (`ref=end`).

### autoscrub.ini

```
[tank]
ref=start
days=30

[bowl]
ref=end
days=7
```


## Install

In lieu of packages, the simplest way to install autoscrub is by
cloning its repository to `/opt/autoscrub`. From there, the sample
systemd unit files may be copied or linked into the appropriate
places, an a config file defined in `/etc`.

```
git clone https://github.com/anderbubble/autoscrub.git /opt/autoscrub
cp /opt/autoscrub/autoscrub-example.ini /etc/autoscrub.ini
ln -s /opt/autoscrub/autoscrub.service /etc/systemd/system/autoscrub.service
ln -s /opt/autoscrub/autoscrub.timer /etc/systemd/system/autoscrub.timer
systemctl daemon-reload
systemctl enable autoscrub.timer
systemctl start autoscrub.timer
```


## License and copyright

autoscrub is distributed under the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright 2020 Jonathon Anderson, civilfritz.net
