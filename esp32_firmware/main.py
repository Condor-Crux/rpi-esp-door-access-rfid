from machine import Pin, SPI
import utime
import urequests
import ujson
from mfrc522 import MFRC522
from config import (
    SDA_PIN, RST_PIN, SCK_PIN, MOSI_PIN, MISO_PIN,
    RELAY_PIN, LED_GREEN_PIN, LED_RED_PIN, BUZZER_PIN,
    RELAY_OPEN_MS, DENY_LED_MS, NONES_PARA_LIBERAR,
    SERVER_URL, ADMIN_PASSWORD,
)

# ── Hardware ──────────────────────────────────────────────────────
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
          sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
rdr = MFRC522(spi, Pin(RST_PIN, Pin.OUT), Pin(SDA_PIN, Pin.OUT))

relay     = Pin(RELAY_PIN,     Pin.OUT, value=0)
led_green = Pin(LED_GREEN_PIN, Pin.OUT, value=0)
led_red   = Pin(LED_RED_PIN,   Pin.OUT, value=0)
buzzer    = Pin(BUZZER_PIN,    Pin.OUT, value=0)


def beep(times=1, duration_ms=200, pause_ms=100):
    for i in range(times):
        buzzer.value(1)
        utime.sleep_ms(duration_ms)
        buzzer.value(0)
        if i < times - 1:
            utime.sleep_ms(pause_ms)


def grant_access():
    beep(1, 200)
    led_green.value(1)
    relay.value(1)
    utime.sleep_ms(RELAY_OPEN_MS)
    relay.value(0)
    led_green.value(0)


def deny_access(reason=""):
    if reason == "Out of Credits":
        beep(3, 200)
    else:
        beep(1, 500)
    led_red.value(1)
    utime.sleep_ms(DENY_LED_MS)
    led_red.value(0)


# ── Autenticación con el servidor ────────────────────────────────
token = None


def get_token():
    global token
    try:
        body = "username=admin&password=" + ADMIN_PASSWORD
        r = urequests.post(
            SERVER_URL + "/api/login",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5,
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            r.close()
            print("[AUTH] Token OK")
            return True
        r.close()
    except Exception as e:
        print("[AUTH] Error:", e)
    return False


def send_swipe(uid_str):
    global token
    if not token:
        if not get_token():
            return None
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }
    try:
        r = urequests.post(
            SERVER_URL + "/api/rfid/swipe",
            data=ujson.dumps({"uid": uid_str}),
            headers=headers,
            timeout=5,
        )
        if r.status_code == 401:
            r.close()
            token = None
            if get_token():
                return send_swipe(uid_str)
            return None
        result = r.json()
        r.close()
        return result
    except Exception as e:
        print("[SWIPE] Error:", e)
        return None


# ── Inicio: parpadeo de verificación ─────────────────────────────
for pin in (led_green, led_red):
    pin.value(1)
    utime.sleep_ms(150)
    pin.value(0)
beep(1, 100)

get_token()

# ── Loop principal ────────────────────────────────────────────────
tarjeta_presente   = False
nones_consecutivos = 0

while True:
    try:
        uid = rdr.read_uid()

        if uid:
            nones_consecutivos = 0
            if not tarjeta_presente:
                tarjeta_presente = True
                uid_dec = int.from_bytes(bytes(uid), "big")
                uid_str = str(uid_dec)
                print("[RFID] Tarjeta:", uid_str)

                result = send_swipe(uid_str)
                if result:
                    if result.get("status") == "granted":
                        grant_access()
                    else:
                        deny_access(result.get("reason", ""))
                else:
                    # Sin respuesta del servidor → denegar por seguridad
                    deny_access("Error")
        else:
            nones_consecutivos += 1
            if nones_consecutivos >= NONES_PARA_LIBERAR:
                tarjeta_presente   = False
                nones_consecutivos = 0

    except Exception as e:
        print("[ERR]", e)
        tarjeta_presente   = False
        nones_consecutivos = 0

    utime.sleep_ms(500)
