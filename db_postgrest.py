from dataclasses import dataclass
import datetime
from dataclasses_json import dataclass_json
import requests
import json


@dataclass_json
@dataclass
class Test:
    ts: datetime.datetime
    Battery_voltage: float = None


@dataclass_json
@dataclass
class SungrowPV:
    ts: datetime.datetime
    Battery_voltage: float = None
    Battery_current: float = None
    Battery_power: float = None
    Daily_PV_Generation: float = None
    Total_PV_Generation: float = None
    Daily_battery_charge_energy_from_PV: float = None
    Total_battery_charge_energy_from_PV: float = None
    Phase_A_current: float = None
    Phase_B_current: float = None
    Phase_C_current: float = None
    Total_active_power: float = None
    Battery_level: float = None
    Daily_Charge_Energy: float = None
    Total_Charge_Energy: float = None
    Daily_export_energy_from_PV: float = None
    Total_export_energy_from_PV: float = None
    Self_consumption_of_today: float = None
    Daily_direct_Energy_Consumption: float = None
    Total_direct_Energy_Consumption: float = None
    MPPT_1_Voltage: float = None
    MPPT_1_Current: float = None
    Inside_Temperature: float = None
    MPPT_2_Voltage: float = None
    MPPT_2_Current: float = None
    Spannung_Ph_A: float = None
    Spannung_Ph_B: float = None
    Spannung_Ph_C: float = None
    Daily_export_energy: float = None
    Total_export_energy: float = None
    Grid_Frequency: float = None
    System_State: float = None
    Running_State: float = None
    Battery_state_of_health: float = None
    Battery_Temperature: float = None
    Daily_battery_discharge_Energy: float = None
    Total_battery_discharge_Energy: float = None
    Grid_state: float = None
    Daily_Import_Energy: float = None
    Total_Import_Energy: float = None


def status_auswerten(r, logger, daten):
    if not (r.status_code == 200 or r.status_code == 201):
        logger.critical(f"Statuscode: {r.status_code}\n Message: {r.text}")
        logger.critical(daten)


def sende_daten(url, table, headers, daten, logger):
    url = f"{url}{table}"
    for data in daten.values():
        data.ts = data.ts.strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f"Folgende Daten werden gesendet an {table}:\n {daten}")
    r = requests.post(url, headers=headers, json=[data.to_dict() for data in daten.values() if data is not None])
    status_auswerten(r, logger, daten)
    if r.status_code == 409:
        logger.error("Primary Key Verletzung. Beginne Datensätze einzeln zu übertragen")
        for data in daten.values():
            r = requests.post(url, headers=headers, json=data.to_dict())
            status_auswerten(r, logger, data)


def hole_letzten_ts(url, table, headers):
    query = f"select=ts&limit=1&order=ts.desc"
    url = f"{url}{table}"
    r = requests.get(url, headers=headers, params=query)
    if r.status_code == 200:
        inhalt = json.loads(r.text)
        try:
            ts_str = inhalt[0]["ts"]
            ts = datetime.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S%z")
        except IndexError:
            ts = datetime.datetime(1975, 1, 1)
        return ts
    else:
        raise TypeError(r.text)
