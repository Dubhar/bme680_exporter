import bme680
import os
import time
from flask import Flask, Response
from flask_httpauth import HTTPBasicAuth
from prometheus_client import Counter, Gauge, start_http_server, generate_latest
from werkzeug.security import generate_password_hash, check_password_hash

# Configurable vars
i2c_address = 0x77
location = 'home'
content_type = str('text/plain; version=0.0.4; charset=utf-8')

if 'I2C_ADDRESS' in os.environ:
    i2c_address = os.environ['I2C_ADDRESS']
if 'LOCATION' in os.environ:
    location = os.environ['LOCATION']
if 'USERNAME' not in os.environ:
    os.environ['USERNAME'] = "admin"
if 'PASSWORD' not in os.environ:
    os.environ['PASSWORD'] = "password"
os.environ['PASSWORD'] = generate_password_hash(os.environ['PASSWORD'])

# setup BME680 sensor (once)
sensor = bme680.BME680(i2c_address)

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# read sensor data (repeatedly)
def get_measurements():
    response = {}
    if not sensor.get_sensor_data() or not sensor.data.heat_stable:
        time.sleep(5)

    response = {"temperature": sensor.data.temperature, "humidity": sensor.data.humidity, "pressure": sensor.data.pressure, "gas_resistance": sensor.data.gas_resistance}
    return response

# configure webapp
app = Flask(__name__)
auth = HTTPBasicAuth()

current_temperature = Gauge(
        'current_temperature',
        'current temperature in degree celsius, this is a gauge as the value can increase or decrease',
        ['location']
)

current_humidity = Gauge(
        'current_humidity',
        'current humidity as percentage, this is a gauge as the value can increase or decrease',
        ['location']
)

current_air_pressure = Gauge(
        'current_air_pressure',
        'current air pressure in hPa, this is a gauge as the value can increase or decrease',
        ['location']
)

current_gas_resistance = Gauge(
        'current_gas_resistance',
        'current gas resistance in ohm, this is a gauge as the value can increase or decrease',
        ['location']
)

@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == os.environ['USERNAME']:
            if check_password_hash(os.environ['PASSWORD'], password):
                return True
    return False

@app.route('/metrics')
@auth.login_required
def metrics():
    metrics = get_measurements()
    current_temperature.labels(location).set(metrics['temperature'])
    current_humidity.labels(location).set(metrics['humidity'])
    current_air_pressure.labels(location).set(metrics['pressure'])
    current_gas_resistance.labels(location).set(metrics['gas_resistance'])
    return Response(generate_latest(), mimetype=content_type)

@app.route('/')
def root():
    return "<html><head><title>BME680 Exporter</title><style type=\"text/css\"></style></head><body><h1>BME680 Exporter</h1><p><a href=\"/metrics\">Metrics</a></p></body></html>"

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=9100)

