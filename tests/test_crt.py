import importlib.util
import os
import pathlib
import re
import sqlite3
import time

import pytest
import weecfg
import weewx
import crt


class Archive:
    table_name = 'archive'

    def __init__(self, units=weewx.METRICWX):
        self.connection = sqlite3.connect(':memory:')
        self.connection.execute('CREATE TABLE archive (dateTime INTEGER, usUnits INTEGER, interval INTEGER, windSpeed REAL, windDir REAL, windGust REAL, rain REAL, ET REAL, barometer REAL, outTemp REAL)')
        self.units = units

    def add(self, timestamp, speed, direction=0, interval=5):
        self.connection.execute('INSERT INTO archive VALUES (?,?,?,?,?,?,0,0,1000,10)',(timestamp,self.units,interval,speed,direction,speed))

    def getSql(self, sql, params=()):
        return self.connection.execute(sql,params).fetchone()

    def genSql(self, sql, params=()):
        return self.connection.execute(sql,params)


@pytest.mark.parametrize('units,speed,expected', [(weewx.METRICWX,10,3),(weewx.METRIC,36,3),(weewx.US,10,10/12)])
def test_windrun_distance_units(units,speed,expected):
    archive = Archive(units)
    archive.add(1700049600,speed)
    assert crt.calc_windrun(archive,1700049600,units) == pytest.approx(expected)


def test_recent_direction_crosses_north_and_ignores_calm():
    archive = Archive()
    end = 1700049600
    archive.add(end,10,359)
    archive.add(end-300,10,1)
    archive.add(end-100,0,180)
    archive.add(end-600,100,180)
    for average in [crt.calc_avg_winddir, crt.calc_avg_winddir_10min]:
        assert average(archive,end) % 360 == pytest.approx(0, abs=1e-10)
    calm = Archive()
    calm.add(end,0,270)
    assert crt.calc_avg_winddir_10min(calm,end) is None


@pytest.mark.parametrize('date', ['2026-03-30','2026-10-26'])
def test_yesterday_rain_follows_local_day_across_dst(monkeypatch,date):
    old_tz = os.environ.get('TZ')
    monkeypatch.setenv('TZ','Europe/Berlin')
    time.tzset()
    try:
        end = int(time.mktime(time.strptime(date+' 12:00','%Y-%m-%d %H:%M')))
        today = crt.weeutil.weeutil.startOfDay(end)
        yesterday = crt.weeutil.weeutil.startOfDay(today-1)
        archive = Archive()
        for stamp in [yesterday-1800,yesterday+1800,today-1800,today+1800]:
            archive.add(stamp,0)
            archive.connection.execute('UPDATE archive SET rain=1 WHERE dateTime=?',(stamp,))
        assert crt.calc_rain_yesterday(archive,end) == 2
    finally:
        if old_tz is None:
            os.environ.pop('TZ',None)
        else:
            os.environ['TZ'] = old_tz
        time.tzset()


def test_numeric_versions_accept_beta_of_newer_release():
    assert crt._version_key('5.2.0b1') > crt._version_key('3.5.0')
    assert crt._version_key('10.0') > crt._version_key('3.5.0')
    assert crt._version_key('3.5.0b1') < crt._version_key('3.5.0')


def test_recent_stats_fallback_and_output_positions():
    archive=Archive()
    archive.add(1700046000,1)
    service=crt.CumulusRealTime.__new__(crt.CumulusRealTime)
    service.db_us=weewx.METRICWX
    service.unit_system=None
    service.units={}
    service.latitude=50
    service.longitude=8
    service.altitude_m=100
    service.sunny_threshold=0.75
    service.location='test'
    service.forecast=type('Forecast',(),{'get_zambretti_code':lambda self:0})()
    service.nonesub='NULL'
    service.datesep='/'
    data=service.calculate({'dateTime':1700049600,'usUnits':weewx.METRICWX,'windSpeed':0,'windGust':4,'windDir':0,'outTemp':10,'barometer':1000},archive)
    fields=service.create_realtime_string(data).split()
    assert fields[5]=='0.0'
    assert fields[40]=='4.0'
    assert fields[46]=='360'
    assert data['windGust']==4


def test_realmore_has_pressure_extrema_and_sixteen_wind_bins():
    archive=Archive()
    end=1700049600
    archive.add(end,2,0)
    archive.add(end-300,3,359)
    archive.add(end-600,4,90)
    service=crt.CumulusRealTime.__new__(crt.CumulusRealTime)
    service.db_us=weewx.METRICWX
    service.pkt_us=weewx.METRICWX
    service.units={}
    service.nonesub='NULL'
    service.realmore_interval=300
    output=service.create_realmore_string({'dateTime':end},archive).split()
    assert len(output)==10
    bins=[float(v) for v in output[8].split(',')]
    assert len(bins)==16
    assert bins[0]==5
    assert bins[4]==4
    assert sum(bins)==9
    assert output[9]=='300'
    assert float(output[4])==1000


def test_module_docstring_names_the_options_and_service_group_in_use():
    source=pathlib.Path(crt.__file__).read_text()
    for option in re.findall(r'^    (\w+) = ',crt.__doc__,re.M):
        assert "'%s'"%option in source or option[:-len('_units')] in crt.UNITS, option
    installer=weecfg.get_extension_installer(str(pathlib.Path(crt.__file__).parents[2]))[1]
    groups=re.findall(r'^        (\w+_services) = .*user\.crt\.CumulusRealTime$',crt.__doc__,re.M)
    assert groups and all(group in installer for group in groups), groups
