#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge
from requests.auth import HTTPDigestAuth

import os
import time
import requests
import json

# Exporter port
listen_port = os.environ['PORT'] if 'PORT' in os.environ else '8000'

# Myenergi variables
username = os.environ['USERNAME'] if 'USERNAME' in os.environ else ''
apikey = os.environ['APIKEY'] if 'APIKEY' in os.environ else ''
server = os.environ['SERVER'] if 'SERVER' in os.environ else ''

# Enable modules
enable_eddi = os.environ['ENABLE_EDDI'].lower() if 'ENABLE_EDDI' in os.environ else 'false'
enable_harvi = os.environ['ENABLE_HARVI'].lower() if 'ENABLE_HARVI' in os.environ else 'false'
enable_zappi = os.environ['ENABLE_ZAPPI'].lower() if 'ENABLE_ZAPPI' in os.environ else 'false'
enable_libbi = os.environ['ENABLE_LIBBI'].lower() if 'ENABLE_LIBBI' in os.environ else 'false'

# Polling interval
polling_interval = os.environ['INTERVAL'] if 'INTERVAL' in os.environ else '5'

# REST API endpoints
eddi_url = f'{server}/cgi-jstatus-E'
zappi_url = f'{server}/cgi-jstatus-Z'
libbi_url = f'{server}/cgi-jstatus-L'
harvi_url = f'{server}/cgi-jstatus-H'

#all_status_url = f'{server}/cgi-jstatus-*'
# Zappi code (Z12345678) and date in YYYY-MM-DD format
#dayhour_url = f'{server}/cgi-jdayhour-Zzzzzzzzz-yyyy-mm-dd'


# HTTP request
def access_server(url_request):
    headers = {'User-Agent': 'MyEnergi Client'}
    r = requests.get(url_request, headers = headers, auth=HTTPDigestAuth(username, apikey), timeout=10)
    if (r.status_code != 200):
        print(f"REST API reply error: status {r.status_code}")
        return None

    return r.json()


# Poll Myenergi
def poll_myenergi():
  output = {}

  if enable_eddi == 'true':
    eddi_status = access_server(eddi_url)
    output['eddi'] = eddi_status['eddi'] if eddi_status != None and 'eddi' in eddi_status else {}

  if enable_harvi == 'true':
    harvi_status = access_server(harvi_url)
    output['harvi'] = harvi_status['harvi'] if harvi_status != None and 'harvi' in harvi_status else {}

  if enable_libbi == 'true':
    libbi_status = access_server(libbi_url)
    output['libbi'] = libbi_status['libbi'] if libbi_status != None and 'libbi' in libbi_status else {}

  if enable_zappi == 'true':
    zappi_status = access_server(zappi_url)
    output['zappi'] = zappi_status['zappi'] if zappi_status != None and 'zappi' in zappi_status else {}

  return output


def update_harvi_metric(harvi_json: dict):
  if 'ectt1' in harvi_json and 'ectp1' in harvi_json:
    harvi.labels(name=harvi_json['ectt1'],variable='ectp1').set(harvi_json['ectp1'])

  if 'ectt2' in harvi_json and 'ectp2' in harvi_json:
    harvi.labels(name=harvi_json['ectt2'],variable='ectp2').set(harvi_json['ectp2'])


def update_eddi_metric(eddi_json: dict):
  if 'gen' in eddi_json:
    eddi.labels(name='solar',variable='gen').set(eddi_json['gen'])

  if 'grd' in eddi_json:
    eddi.labels(name='grid',variable='grd').set(eddi_json['grd']) if

  if 'div' in eddi_json:
    eddi.labels(name='diverter',variable='div').set(eddi_json['div'])

  if 'ectp1' in eddi_json:
    eddi.labels(name='tank1',variable='ectp1').set(eddi_json['ectp1'])

  if 'che' in eddi_json:
    eddi.labels(name='tank1_total',variable='che').set(eddi_json['che'])

  if 'frq' in eddi_json:
    eddi.labels(name='frequency',variable='frq').set(eddi_json['frq'])


def update_libbi_metric(libbi_json: dict):
  # Placeholder
  return


def update_zappi_metric(zappi_json: dict):
  # Placeholder
  return


#
# Main
#

print("MyEnergi Prometheus Exporter starting")

if username == '' or apikey == '' or server == '':
  print("Username, API key or server undefined")
  quit()

# Create a Prometheus gauge metric instance
# Change the metric name, labels, and help text as per your requirements

if enable_eddi == 'true':
  eddi = Gauge('myenergi_eddi', 'Eddi data', ['name','variable'])

if enable_harvi == 'true':
  harvi = Gauge('myenergi_harvi', 'Harvi data', ['name','variable'])

if enable_libbi == 'true':
  libbi = Gauge('myenergi_libbi', 'Libbi data', ['name','variable'])

if enable_zappi == 'true':
  zappi = Gauge('myenergi_zappi', 'Zappi data', ['name','variable'])

print(f"{'** Eddi enabled' if enable_eddi == 'true' else '.. Eddi disabled'}")
print(f"{'** Harvi enabled' if enable_harvi == 'true' else '.. Harvi disabled'}")
print(f"{'** Libbi enabled' if enable_libbi == 'true' else '.. Libbi disabled'}")
print(f"{'** Zappi enabled' if enable_zappi == 'true' else '.. Zappi disabled'}")


print(f"Using server {server}")
print(f"Polling interval is {polling_interval} seconds")

# Start the Prometheus HTTP server
print(f"Starting prometheus exporter on port {listen_port}")
start_http_server(int(listen_port))

# Update the metric every 5 seconds
while True:
    myenergi = poll_myenergi()

    if myenergi is not None:
      if 'harvi' in myenergi and len(myenergi['harvi']) > 0:
        update_harvi_metric(myenergi['harvi'][0])

      if 'eddi' in myenergi and len(myenergi['eddi']) > 0:
        update_eddi_metric(myenergi['eddi'][0])

      if 'libbi' in myenergi and len(myenergi['libbi']) > 0:
        update_libbi_metric(myenergi['libbi'][0])

      if 'zappi' in myenergi and len(myenergi['zappi']) > 0:
        update_zappi_metric(myenergi['zappi'][0])

    time.sleep(int(polling_interval))
