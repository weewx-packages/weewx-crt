# Cumulus real-time files from WeeWX

Write Cumulus-compatible `realtime.txt` from LOOP readings, with optional XML,
Sunbird, MX gauges and `realmore.txt` outputs. The service combines the current
packet with archive-derived rain, wind and pressure statistics.

This is the weewx-packages continuation, release **0.24.1**.
[Origin](ORIGIN.md) records the upstream revision; [repair notes](REPAIR_NOTES.md)
describe the maintenance changes.

The catalog archive targets WeeWX `>=5.5.2,<5.7` and Python `>=3.10,<3.15`.

## Install

Use `weectl` from the Python environment running WeeWX. With stock WeeWX 5,
install the published archive:

```sh
weectl extension install https://github.com/weewx-packages/weewx-crt/releases/download/v0.24.1/weewx-crt-0.24.1.tar.gz --config /path/to/weewx.conf
```

Replace `/path/to/weewx.conf` with your station configuration. You can also
download that URL and pass the local archive to the same command. Use elevated
permissions only when your station files require them.

## Write your first file

The installer registers `user.crt.CumulusRealTime` as a process service and adds:

```ini
[CumulusRealTime]
    filename = /var/tmp/realtime.txt
```

The WeeWX user must be able to write the directory. Restart WeeWX yourself,
then inspect the file after a LOOP packet. The service needs the `wx_binding`
archive and the station's location and altitude. No additional Python package
is required for the basic almanac. PyEphem can provide extended almanac data
when installed in WeeWX's Python environment.

To update on archive records, add `binding = archive`. This can produce more
complete output when the driver emits partial LOOP packets.

## Choose outputs and units

`filename` takes precedence over `realtime_txt`. To use the newer name, remove
the installer's `filename` setting before using this configuration:

```ini
[CumulusRealTime]
    realtime_txt = /var/tmp/realtime.txt
    realtime_xml = /var/tmp/realtime.xml
    sunbird_txt = /var/tmp/sunbird.txt
    realtimegauges_txt = /var/tmp/realtimegauges.txt
    realmore_txt = /var/tmp/realmore.txt
    realmore_interval = 300
    unit_system = METRICWX
```

Each optional path enables that output. The Sunbird setting is `sunbird_txt`.
Without an override, output follows packet units. `unit_system` accepts `US`,
`METRIC` and `METRICWX`; per-group overrides accept:

| Option | Units |
| --- | --- |
| wind_units | meter_per_second, mile_per_hour, km_per_hour, knot |
| temperature_units | degree_C, degree_F |
| pressure_units | hPa, mbar, inHg |
| rain_units | mm, inch |
| cloudbase_units | foot, meter |

`none` changes the missing-value marker, default `NULL`; `date_separator`
defaults to `/`. The [module reference](bin/user/crt.py) describes format details
and its assumptions about the [Cumulus realtime specification](https://cumuluswiki.org/a/Realtime.txt).

## Archive-derived values

`realmore.txt` contains yesterday/today pressure extrema, sixteen wind totals
and the positive `realmore_interval` in seconds. Wind totals use recorded
archive durations and configured display units. They cannot reconstruct the
original high-frequency LOOP samples.

Ten-minute wind speed, gust and bearing fall back to the current packet when
no usable archive sample exists. That fallback is instantaneous. Partial
packets and missing archive history leave some values unavailable. Forecast
fields require the separate Zambretti forecast database; publishing these
files to a website is a separate step.

Copyright 2014-2024 Matthew Wall. Contributions from Gary Roderick.
[GNU GPLv3](license).
