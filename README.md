# Cumulus realtime output

Write Cumulus-compatible `realtime.txt` from LOOP readings, with optional XML,
Sunbird, MX gauges and `realmore.txt` outputs. The service combines the current
packet with archive-derived rain, wind and pressure statistics. It writes local
files only; publishing them to a website is a separate step.

Independent continuation of
[matthewwall/weewx-crt](https://github.com/matthewwall/weewx-crt).
[ORIGIN.md](ORIGIN.md) records the upstream revision and
[REPAIR_NOTES.md](REPAIR_NOTES.md) describes the maintenance changes.

## Requirements

- The `wx_binding` archive database.
- Latitude, longitude and altitude of the station in `[Station]`.
- Write permission for the WeeWX user in each output directory.
- No Python package beyond WeeWX. Sunrise and sunset come from the WeeWX
  almanac, which uses PyEphem when it is installed.
- Optional: the `forecast` package with a Zambretti forecast in its
  `forecast_binding` database. Without it, the forecast fields hold no
  forecast.

## Installation

Install `crt` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/crt.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer registers `user.crt.CumulusRealTime` as a process service and
adds:

```ini
[CumulusRealTime]
    filename = /var/tmp/realtime.txt
```

After a LOOP packet, inspect the file.

## Configuration

`realtime.txt` is always written. Each other output is enabled by setting its
path:

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

`filename` takes precedence over `realtime_txt`. To use the newer name, remove
the installer's `filename` setting.

| Option | Default | Meaning |
| --- | --- | --- |
| `filename` | none | Path of `realtime.txt`. |
| `realtime_txt` | `/var/tmp/realtime.txt` | Path of `realtime.txt` when `filename` is not set. |
| `realtime_xml` | none | Path of `realtime.xml`. |
| `sunbird_txt` | none | Path of the Sunbird file. |
| `realtimegauges_txt` | none | Path of the MX gauges file. |
| `realmore_txt` | none | Path of `realmore.txt`. |
| `realmore_interval` | `300` | Sample interval in seconds used to weight the `realmore.txt` wind totals. Must be positive. |
| `binding` | `loop` | `loop` writes on every LOOP packet. Any other value, for example `archive`, writes on archive records. |
| `unit_system` | packet units | `US`, `METRIC` or `METRICWX`. |
| `wind_units` | from unit system | `meter_per_second`, `mile_per_hour`, `km_per_hour`, `knot`. |
| `temperature_units` | from unit system | `degree_C`, `degree_F`. |
| `pressure_units` | from unit system | `hPa`, `mbar`, `inHg`. |
| `rain_units` | from unit system | `mm`, `inch`. |
| `cloudbase_units` | from unit system | `foot`, `meter`. |
| `none` | `NULL` | Marker for missing values. |
| `date_separator` | `/` | Separator in the `realtime.txt` date. |
| `sunny_threshold` | `0.75` | The sunny flag is set when radiation exceeds this fraction of `maxSolarRad`. |

Archive records can give more complete output than LOOP packets when the
driver emits partial LOOP packets.

`realmore.txt` contains yesterday's and today's pressure extrema, sixteen wind
totals from the last 24 hours and `realmore_interval`. Wind totals use recorded
archive durations and the configured wind units.

The [module reference](bin/user/crt.py) describes format details and its
assumptions about the
[Cumulus realtime specification](https://cumuluswiki.org/a/Realtime.txt).

## Limitations

- The `realmore.txt` wind totals come from archive records. They cannot
  reconstruct the original high-frequency LOOP samples.
- Ten-minute wind speed, gust and bearing fall back to the current packet when
  no usable archive sample exists. That fallback is an instantaneous sample,
  not a ten-minute average.
- Partial packets and missing archive history leave some values unavailable.

## Development

Run `python -m pytest -q` in an environment with WeeWX and pytest installed.

## License

Copyright 2014-2024 Matthew Wall. Contributions from Gary Roderick.
Distributed under the terms of the [GNU GPLv3](license).
