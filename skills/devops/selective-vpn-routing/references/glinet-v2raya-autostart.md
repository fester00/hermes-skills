# GL.iNet v2rayA autostart after reboot

Stock GL.iNet / OpenWrt firmware with the `v2raya` package installed from OpenWrt repos (or GL.iNet SDK 4.x+). The goal is to make v2rayA (and the xray-core it manages) start automatically after a router reboot.

## What gets persisted

Two UCI boolean flags control startup:

```bash
uci set v2raya.config.enabled=1      # v2rayA daemon
uci set xray.enabled.enabled=1      # separate /etc/init.d/xray service, if installed
uci commit v2raya
uci commit xray
```

The init scripts `/etc/init.d/v2raya` and `/etc/init.d/xray` and their `S99` rc.d links are normally created by the package install; if they are missing, reinstall the packages.

## Check current state

```bash
uci show v2raya | grep enabled
uci show xray | grep enabled
ls -la /etc/rc.d/ | grep -E 'v2ray|xray'
```

## Start manually after enabling

```bash
/etc/init.d/xray restart
/etc/init.d/v2raya restart
sleep 5
ss -tlnp | grep 2017
```

## Expected first-start behaviour

When `v2raya` has not run before (or after a factory reset), it may log:

```
failed to start v2ray-core: cannot find GFWList files. update GFWList and try again
```

This is harmless on startup: v2rayA automatically downloads `geoip.dat`, `geosite.dat`, and its GFWList/PAC files within a few seconds, then restarts xray-core. The web UI on `http://ROUTER_IP:2017` becomes available anyway.

## Autoconnect caveat

Enabling the service only makes v2rayA **start** at boot. It does **not** automatically press the **Connect** button in the web UI. If you need the VPN tunnel to come up without manual intervention:

1. Open `http://ROUTER_IP:2017`.
2. Select the active server / subscription node.
3. Look for an **Auto connect** / **开机自动连接** / **Start on boot** toggle in the v2rayA settings and enable it.

Without that toggle, the daemon will be running after reboot but traffic will stay direct until you connect manually.

## SSH verification recipe

```bash
ssh root@ROUTER_IP

# should print enabled=1
uci show v2raya.config.enabled

# should show v2raya listening on 2017
ss -tlnp | grep 2017

# should show v2raya process
ps | grep v2raya | grep -v grep
```

## Rollback

If v2rayA breaks the router web UI or LAN internet:

```bash
uci set v2raya.config.enabled=0
uci commit v2raya
/etc/init.d/v2raya stop
/etc/init.d/xray stop 2>/dev/null
```

Router returns to direct routing immediately.
