import network
import utime
import webrepl

from config import WIFI_SSID, WIFI_PASSWORD, WEBREPL_PASS

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("[WiFi] Conectando a", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        utime.sleep(1)
        timeout -= 1
        print(".")

if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print("[WiFi] Conectado — IP:", ip)
    webrepl.start(password=WEBREPL_PASS)
    print("[WebREPL] ws://{}:8266  pass: {}".format(ip, WEBREPL_PASS))
else:
    print("[WiFi] FALLO — reiniciando en 5s")
    utime.sleep(5)
    import machine
    machine.reset()
