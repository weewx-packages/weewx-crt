# Repair validation

Version 0.24.0. Original repository and revision are in ORIGIN.md.

* https://github.com/matthewwall/weewx-crt/issues/13: Removed distutils; numeric release gate accepts newer beta versions and rejects prereleases of the minimum release.
* https://github.com/matthewwall/weewx-crt/issues/12: Empty recent archive windows use current packet speed, gust and bearing; windGust is converted to output units. This fallback is an instantaneous sample, not a measured 10-minute average.
* https://github.com/matthewwall/weewx-crt/issues/8: METRICWX integration now converts metres to kilometres before distance conversion; US and METRIC regression cases also pass.
* https://github.com/matthewwall/weewx-crt/issues/7: Optional realmore_txt emits pressure extrema and 16 wind totals. Archive durations are weighted to realmore_interval. Original high-frequency LOOP samples cannot be reconstructed from an archive.

Tests run under WeeWX 4.10.2/5.1.0 on Python 3.10 and WeeWX 5.5.2 on Python 3.14. Local receivers and isolated install directories avoid live station changes. The tests do not establish individual external account permissions.

## Independent review, 2026-10-22

Version 0.24.1. Correct vector wind direction across north, ignore calm direction samples, and use the local calendar day for yesterday rain across DST transitions. Regression tests fail against the prior release and pass with this patch. The prior release archive is unchanged.
