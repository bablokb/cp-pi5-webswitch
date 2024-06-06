# ----------------------------------------------------------------------------
# Access-Point with webserver for Pi5 web-switch
#
# Wiring:
#  PIN_TOGGLE to header next to USB-C (USB-C side)  (yellow)
#  GND        to header next to USB-C (HDMI side)   (black)
#  PIN_3V3    to Pi5 3V3 (pin 1 or 17, use 10K in series for protection) (blue)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-pi5-webswitch
#
# ----------------------------------------------------------------------------

import board
import gc
import time
import wifi
import mdns
import socketpool
import json

from digitalio import DigitalInOut, Pull, DriveMode
from ehttpserver import Server, Response, FileResponse, route

try:
  from settings import CONFIG
except:
  CONFIG = {
    'debug': False,
    'cache': True,
    'ap_mode': False,
    'desktop': False,                        # no desktop system
    'ap_ssid': 'ap_pi5_switch',              # for ap_mode == True
    'ap_password': '12345678',               # for ap_mode == True
    'ap_hostname': 'pi5switch',              # for ap_mode == True
    'wlan_ssid': 'my_wlan_ssid',             # for ap_mode == False
    'wlan_password': 'my_wlan_password'      # for ap_mode == False
  }

PIN_TOGGLE = board.GP27    # connected to Pi5 to toggle state
PIN_3V3    = board.GP26    # connected to Pi5 3V3

class MyServer(Server):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._pi5_toggle = DigitalInOut(PIN_TOGGLE)
    self._pi5_toggle.switch_to_output(True,drive_mode=DriveMode.OPEN_DRAIN)
    self._pi5_3v3    = DigitalInOut(PIN_3V3)
    self._pi5_3v3.switch_to_input(pull=Pull.DOWN)

    super().__init__(debug=CONFIG["debug"])
    self.debug("Initializing web-server")

  # --- request-handler for /   ----------------------------------------------

  @route("/","GET")
  def _handle_main(self,path,query_params, headers, body):
    """ handle request for main-page """
    self.debug("handle request for /")
    return FileResponse("/www/index.html")

  # --- request-handler for static files   -----------------------------------

  @route("/[^.]*\.(js|css|html)","GET")
  def _handle_static(self,path,query_params, headers, body):
    """ handle request for static-files """
    if CONFIG["cache"]:
      headers = {
        "Cache-Control": "max-age=2592000"
      }
    else:
      headers = {}
    self.debug(f"serving /www/{path}")
    return FileResponse(f"/www/{path}",headers=headers)

  # --- request-handler for /get_status   ------------------------------------

  @route("/get_status","GET")
  def _handle_get_status(self,path,query_params, headers, body):
    """ handle request for /get_status """
    self.debug(f"processing /get_status")
    status = {"pi5_state": self._pi5_3v3.value}
    self.debug(f"status: {status}")
    return Response(json.dumps(status),
                    content_type="application/json")

  # --- request-handler for /toggle_power   ----------------------------------

  @route("/toggle_power","GET")
  def _handle_toggle_power(self,path,query_params, headers, body):
    """ handle request for /toggle_power """

    self.debug(f"processing /toggle_power")
    self._pi5_toggle.value = False
    time.sleep(0.1)
    self._pi5_toggle.value = True
    if CONFIG["desktop"]:
      # wait and toggle again to simulate second push
      time.sleep(1)
      self._pi5_toggle.value = False
      time.sleep(0.1)
      self._pi5_toggle.value = True
    return Response(json.dumps({"rc": True}),
                    content_type="application/json")

  # --- run as AP   ----------------------------------------------------------

  def start_ap(self):
    """ start AP-mode """

    wifi.radio.stop_station()
    try:
      wifi.radio.start_ap(ssid=CONFIG["ap_ssid"],
                          password=CONFIG["ap_password"])
    except NotImplementedError:
      # workaround for older CircuitPython versions
      pass

  # --- run as station   -----------------------------------------------------

  def start_station(self):
    """ start station-mode """

    wifi.radio.stop_ap()
    wifi.radio.connect(CONFIG["wlan_ssid"],
                       CONFIG["wlan_password"])

  # --- run server   ---------------------------------------------------------

  def run_server(self):

    server = mdns.Server(wifi.radio)
    server.hostname = CONFIG["ap_hostname"]
    server.advertise_service(service_type="_http",
                             protocol="_tcp", port=80)
    pool = socketpool.SocketPool(wifi.radio)
    if CONFIG["ap_mode"]:
      self._address =  wifi.radio.ipv4_address_ap
    else:
      self._address = wifi.radio.ipv4_address
    print(f"starting {server.hostname}.local ({self._address})")
    with pool.socket() as server_socket:
      yield from self.start(server_socket)

  # --- run AP and server   --------------------------------------------------

  def run(self):
    """ start AP or connect and then run server """

    if CONFIG["ap_mode"]:
      self.start_ap()
    else:
      self.start_station()
    started = False
    for _ in self.run_server():
      if not started:
        print(f"Listening on http://{self._address}:80")
        started = True
      gc.collect()

myserver = MyServer()
myserver.run()
