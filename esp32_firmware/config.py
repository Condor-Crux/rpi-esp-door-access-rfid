# ================================================================
#  config.py — ESP32 RFID Node Configuration
#  Editá estas variables antes de flashear al ESP32
# ================================================================

# --- WiFi ---
WIFI_SSID     = "TU_RED_WIFI"
WIFI_PASSWORD = "TU_CLAVE_WIFI"

# --- Servidor FastAPI en Raspberry Pi ---
# Baño hombres → puerto 8000 | Baño mujeres → puerto 8001
SERVER_URL    = "http://172.24.207.11:8000"
ADMIN_PASSWORD = "TU_SUPER_PASSWORD"  # mismo valor que SUPER_PASSWORD en el .env del servidor

# --- Pines MFRC522 (SPI) ---
SDA_PIN  = 5
RST_PIN  = 22
SCK_PIN  = 18
MOSI_PIN = 23
MISO_PIN = 19

# --- Pines de salida ---
RELAY_PIN     = 4
LED_GREEN_PIN = 2
LED_RED_PIN   = 15
BUZZER_PIN    = 13

# --- Comportamiento ---
RELAY_OPEN_MS    = 5000   # tiempo de apertura en milisegundos
DENY_LED_MS      = 1000   # tiempo LED rojo encendido al denegar
NONES_PARA_LIBERAR = 5    # lecturas vacías consecutivas para liberar tarjeta

# --- WebREPL (acceso inalámbrico al REPL del ESP32) ---
WEBREPL_PASS = "TU_WEBREPL_PASS"   # contraseña para conectarse via WebREPL
