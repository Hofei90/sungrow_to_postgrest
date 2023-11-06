import sql_models as db
import toml
import pathlib
import datetime
import db_postgrest
import setup_logging

SKRIPTPFAD = pathlib.Path(__file__).parent
CONFIGPFAD = SKRIPTPFAD / "config.toml"
CONFIG = toml.load(CONFIGPFAD)
LOGGER = setup_logging.create_logger("sungrow_export", CONFIG["loglevel"])
SENDELIMIT = 1


def to_timestamp(ts):
    return int(ts.timestamp() * 1000)


def get_sourceid():
    return db.Sources.get(db.Sources.name == CONFIG["iobroker"]["sources_name"])


def get_rawdata(sourceid, letzter_ts_server):
    letzter_ts_server = to_timestamp(letzter_ts_server)
    return db.TsNumber.select().where(
        (db.TsNumber.ts > letzter_ts_server) & db.TsNumber.id == sourceid).order_by(db.TsNumber.ts)


def get_rawname_from_dataid(dataid):
    return db.Datapoints.get(dataid).name


def get_name_from_dataid(dataid):
    name = get_rawname_from_dataid(dataid)
    index = name.find("_") + 1
    if name.endswith("_"):
        return name[index:-1]
    return name[index:]


def round_time(dt=None, round_to=10):
    """
    Round a datetime object to any time-lapse in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt is None:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)


def get_timezone():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo


def change_ts_to_utc(ts):
    tz = get_timezone()
    ts_utc = ts.replace(tzinfo=tz).utcnow()
    ts_utc = ts_utc.replace(tzinfo=datetime.timezone.utc)
    return ts_utc


def change_ts_to_locale_time(ts):
    tz = get_timezone()
    ts_local = ts.astimezone(tz)
    return ts_local


def daten_aufbereiten(data):
    daten = {}
    for datum in data:
        ts = change_ts_to_utc(round_time(datetime.datetime.fromtimestamp(datum.ts / 1000)))
        if ts not in daten:
            daten[ts] = db_postgrest.SungrowPV(ts=ts)
        daten[ts].__setattr__(get_name_from_dataid(datum.id), datum.val)
    return daten


def delete_old_data(letzter_ts_server):
    letzter_ts_server = to_timestamp(letzter_ts_server)
    db.TsNumber.delete().where(db.TsNumber.ts < letzter_ts_server).execute()


def main():
    headers = {f"Authorization": "Bearer {token}".format(token=CONFIG["zieldb"]["postgrest_token"])}
    url = CONFIG["zieldb"]["url"]
    if not url.endswith("/"):
        url = f"{url}/"

    letzter_ts_server_utc = db_postgrest.hole_letzten_ts(url, CONFIG["zieldb"]["tabellenname"], headers)
    letzter_ts_server_local = change_ts_to_locale_time(letzter_ts_server_utc)
    source_id = get_sourceid()
    rawdata = get_rawdata(source_id, letzter_ts_server_local)
    daten = daten_aufbereiten(rawdata)
    if daten:
        db_postgrest.sende_daten(url, CONFIG["zieldb"]["tabellenname"], headers, daten, LOGGER)
    delete_old_data(letzter_ts_server_local)


if __name__ == "__main__":
    main()
