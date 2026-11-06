# Instrucciones — Integración ESP32 WiFi

## 1. Agregar endpoint al servidor (rpi-door-access-rfid)

Abrí `app/api/endpoints.py` y pegá el contenido de `nuevo_endpoint.py`
**después** de la función `rfid_swipe` (alrededor de la línea 91).

Asegurate de que `MockLedIndicator`, `MockBuzzer` y `MockDoorRelay`
estén importados al inicio del archivo:

```python
from app.infrastructure.hardware.mock_impl import (
    MockLedIndicator, MockBuzzer, MockDoorRelay,
)
```

## 2. Reiniciar la instancia existente (baño hombres, puerto 8000)

```bash
# En el Raspberry Pi
kill $(pgrep -f "uvicorn.*8000")
nohup .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

## 3. Levantar segunda instancia (baño mujeres, puerto 8001)

Copiá `.env.mujeres` al directorio del proyecto:

```bash
cp .env.mujeres ~/rpi-door-access-rfid/.env.mujeres
```

Iniciá la segunda instancia:

```bash
cd ~/rpi-door-access-rfid
nohup .venv/bin/python -m uvicorn app.main:app \
    --host 0.0.0.0 --port 8001 \
    --env-file .env.mujeres &
```

La segunda instancia crea automáticamente `rpi_door_access_mujeres.db`
en el mismo directorio. Es una base de datos completamente separada —
las tarjetas registradas en un baño no funcionan en el otro.

## 4. Acceder al panel de administración

- Baño hombres: http://172.24.207.11:8000
- Baño mujeres:  http://172.24.207.11:8001

Ambos usan la misma contraseña (`SUPER_PASSWORD` del .env correspondiente).

## 5. Flashear el ESP32

Ver `../esp32_firmware/` para los archivos MicroPython.

Usar Thonny o `ampy` / `mpremote` para copiar al ESP32:

```bash
# Con mpremote (recomendado)
mpremote cp config.py :config.py
mpremote cp mfrc522.py :mfrc522.py
mpremote cp boot.py :boot.py
mpremote cp main.py :main.py
```

Editá `config.py` antes de flashear:
- `WIFI_SSID` / `WIFI_PASSWORD`: credenciales de tu red
- `SERVER_URL`: apuntá al puerto correcto (8000 u 8001)
