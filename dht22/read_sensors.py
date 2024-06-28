import time
import adafruit_dht
import board
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import mh_z19

token ="0yaLLKtqQBccEsQp3wLN3zKiaxVq3o9V6ukFc3Oy-ToVEzKk5uXjNrNhFjzxsIGxQArk1wNy0m4DiWVWQlkt-A=="
org = "homelab"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
bucket_dht22="DHT22"
bucket_mhz19="mhz19"
write_api = write_client.write_api(write_options=SYNCHRONOUS)
co2_list = []
# Initial the dht device, with data pin connected to:
# dhtDevice = adafruit_dht.DHT22(board.D4)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

for i in range(3):
    try:
        # Read sensor 3 times, calculate the average co2 concentration and
        # write it to the influx database
        co2_value = mh_z19.read()['co2']
        co2_list.append(co2_value)
        time.sleep(1.0)
    except Exception as error:
        raise error
if len(co2_list) != 0:
    avg_co2 = sum(co2_list) / len(co2_list)
    point_co2 = (
        Point("CO2_Wohnzimmer")
        .tag("type", "CO2")
        .field("reading", avg_co2)
    )
    write_api.write(bucket=bucket_mhz19, org="homelab", record=point_co2)

temperature_list = []
humidity_list = []

# error counter
counter = 0

for i in range(3):
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        temperature_list.append(temperature_c)
        humidity_list.append(humidity)
        time.sleep(2.0)
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        counter += 1
        if counter > 15:
            break
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
if len(temperature_list) != 0:
    avg_temp = sum(temperature_list) / len(temperature_list)
    point_temperature = (
        Point("Temperatur_Wohnzimmer")
        .tag("type", "Temperatur")
        .field("reading", avg_temp)
    )
    write_api.write(bucket=bucket_dht22, org="homelab", record=point_temperature)
if len(humidity_list) != 0:
    avg_humidity = sum(humidity_list) / len(humidity_list)
    point_humidity = (
        Point("Feuchtigkeit_Wohnzimmer")
        .tag("type", "Feuchtigkeit")
        .field("reading", avg_humidity)
    )
    write_api.write(bucket=bucket_dht22, org="homelab", record=point_humidity)
