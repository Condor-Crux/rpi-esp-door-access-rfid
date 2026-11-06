"""
Endpoint a agregar en:
  rpi-door-access-rfid/app/api/endpoints.py

Pegarlo después del endpoint existente /api/rfid/last (línea ~91).
Este endpoint recibe el UID desde un ESP32 vía WiFi,
procesa el swipe en la DB y retorna JSON.
El ESP32 lee la respuesta y controla su propio hardware (relay, LEDs, buzzer).
"""

from app.infrastructure.hardware.mock_impl import (
    MockLedIndicator, MockBuzzer, MockDoorRelay,
)

# Importar también AccountModel si no está importado (ya está en el archivo)

@router.post("/api/rfid/swipe")
def rfid_swipe_esp32(
    req: RfidSwipeRequest,          # mismo modelo: { "uid": "..." }
    admin: str = Depends(get_current_admin),
):
    """
    Endpoint para nodos ESP32 WiFi.
    Procesa el swipe en la DB (descuenta crédito, registra log)
    pero NO activa GPIO local — el ESP32 controla su propio hardware
    según la respuesta JSON.
    """
    _null_green  = MockLedIndicator("green")
    _null_red    = MockLedIndicator("red")
    _null_buzzer = MockBuzzer()
    _null_relay  = MockDoorRelay()

    with SessionLocal() as db:
        result = process_swipe(
            card_id=req.uid,
            db=db,
            green_led=_null_green,
            red_led=_null_red,
            buzzer=_null_buzzer,
            relay=_null_relay,
            verbose=settings.VERBOSE,
        )
        should_notify = result.get("reason") == "Not Found"
        if not should_notify:
            account = db.query(AccountModel).filter(AccountModel.account_id == req.uid).first()
            should_notify = account is not None and account.user_id is None
    if should_notify:
        broadcaster.publish("new_card", {"uid": req.uid})
    return result
