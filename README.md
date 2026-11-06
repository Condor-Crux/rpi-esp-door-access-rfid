# rpi-esp-door-access-rfid

Sistema de control de acceso RFID con **Raspberry Pi como servidor** y **ESP32 como nodos de hardware** conectados por WiFi.

## Arquitectura

```
┌─────────────────────────────────┐
│  Raspberry Pi (servidor)        │
│  FastAPI + SQLite               │
│  :8000 → baño hombres           │
│  :8001 → baño mujeres           │
└────────────┬────────────────────┘
             │ WiFi (HTTP/JSON)
     ┌───────┴───────┐
     │               │
┌────▼────┐     ┌────▼────┐
│ ESP32 #1│     │ ESP32 #2│
│ Hombres │     │ Mujeres │
│ MFRC522 │     │ MFRC522 │
│ Relay   │     │ Relay   │
│ LEDs    │     │ LEDs    │
│ Buzzer  │     │ Buzzer  │
└─────────┘     └─────────┘
```

Cada ESP32 lee una tarjeta RFID, envía el UID al servidor vía WiFi y controla su propio hardware (relay, LEDs, buzzer) según la respuesta JSON.

## Contenido

```
esp32_firmware/      # MicroPython para los nodos ESP32
  config.py          # Configuración (WiFi, pines, servidor)
  boot.py            # Arranque: WiFi + WebREPL
  main.py            # Loop principal
  mfrc522.py         # Driver SPI para MFRC522
  webrepl_cfg.py     # Configuración de WebREPL

server_patch/        # Cambios al servidor rpi-door-access-rfid
  nuevo_endpoint.py  # Endpoint /api/rfid/swipe para ESP32
  .env.mujeres       # .env para la segunda instancia (puerto 8001)
  INSTRUCCIONES.md   # Cómo aplicar los cambios
```

## Configuración del ESP32

Editá [`esp32_firmware/config.py`](esp32_firmware/config.py) antes de flashear:

```python
WIFI_SSID      = "tu_red"
WIFI_PASSWORD  = "tu_clave"
SERVER_URL     = "http://<IP_RPi>:8000"   # :8000 u :8001 según el baño
ADMIN_PASSWORD = "tu_super_password"
WEBREPL_PASS   = "tu_webrepl_pass"
```

Actualizá también `webrepl_cfg.py` con el mismo valor de `WEBREPL_PASS`.

## Flashear al ESP32

```bash
mpremote cp esp32_firmware/config.py      :config.py
mpremote cp esp32_firmware/webrepl_cfg.py :webrepl_cfg.py
mpremote cp esp32_firmware/mfrc522.py     :mfrc522.py
mpremote cp esp32_firmware/boot.py        :boot.py
mpremote cp esp32_firmware/main.py        :main.py
```

## WebREPL

Una vez conectado a WiFi, cada ESP32 expone WebREPL en el puerto 8266.  
Accedé desde https://micropython.org/webrepl/ con `ws://<IP_ESP32>:8266`.

## Pines por defecto (ESP32 38 pines)

| Función | Pin |
|---------|-----|
| MFRC522 SDA (CS) | 5 |
| MFRC522 SCK | 18 |
| MFRC522 MOSI | 23 |
| MFRC522 MISO | 19 |
| MFRC522 RST | 22 |
| Relay | 4 |
| LED verde | 2 |
| LED rojo | 15 |
| Buzzer | 13 |

## Servidor — instrucciones de despliegue

Ver [`server_patch/INSTRUCCIONES.md`](server_patch/INSTRUCCIONES.md).

El servidor base es [rpi-door-access-rfid](https://github.com/Condor-Crux/rpi-door-access-rfid).
