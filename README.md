Policy-based ZFS auto-scrubber

Inspired by syncoid, the policy-based ZFS auto-snapshotter.


## Example

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

```
git clone https://github.com/anderbubble/autoscrub.git /opt/autoscrub
cp /opt/autoscrub/autoscrub-example.ini /etc/autoscrub.ini
ln -s /opt/autoscrub/autoscrub.service /etc/systemd/system/autoscrub.service
ln -s /opt/autoscrub/autoscrub.timer /etc/systemd/system/autoscrub.timer
systemctl daemon-reload
systemctl enable autoscrub.timer
systemctl start autoscrub.timer
```
