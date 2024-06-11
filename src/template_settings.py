# ----------------------------------------------------------------------------
# Template for settings.py for Pi5 web-switch main.py
#
# Copy this file to settings.py and adapt to your needs.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-pi5-webswitch
#
# ----------------------------------------------------------------------------

import board

CONFIG = {
  'PIN_TOGGLE': board.GP27,               # connected to Pi5 to toggle state
  'PIN_3V3':    board.GP26,               # connected to Pi5 3V3
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
