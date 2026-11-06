from machine import Pin, SPI
import utime

class MFRC522:
    OK    = 0
    ERR   = 1
    NOTAG = 2

    PCD_IDLE       = 0x00
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F

    PICC_REQIDL   = 0x26
    PICC_ANTICOLL = 0x93

    REG_COMMAND     = 0x01
    REG_COM_IRQ     = 0x04
    REG_ERROR       = 0x06
    REG_FIFO_DATA   = 0x09
    REG_FIFO_LEVEL  = 0x0A
    REG_BIT_FRAMING = 0x0D
    REG_TX_CONTROL  = 0x14
    REG_TX_ASK      = 0x15
    REG_MODE        = 0x11
    REG_T_MODE      = 0x2A
    REG_T_PRESCALER = 0x2B
    REG_T_RELOAD_H  = 0x2C
    REG_T_RELOAD_L  = 0x2D

    def __init__(self, spi, rst, cs):
        self.spi = spi
        self.rst = rst
        self.cs  = cs
        self.reset()
        self.init()

    def _w(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytes([(reg << 1) & 0x7E, val]))
        self.cs.value(1)

    def _r(self, reg):
        self.cs.value(0)
        self.spi.write(bytes([((reg << 1) & 0x7E) | 0x80]))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0] if val else 0

    def _set_bits(self, reg, mask):
        self._w(reg, self._r(reg) | mask)

    def _clr_bits(self, reg, mask):
        self._w(reg, self._r(reg) & (~mask))

    def reset(self):
        self.rst.value(0)
        utime.sleep_ms(50)
        self.rst.value(1)
        utime.sleep_ms(50)

    def init(self):
        self._w(self.REG_COMMAND, self.PCD_RESETPHASE)
        utime.sleep_ms(50)
        self._w(self.REG_T_MODE,      0x8D)
        self._w(self.REG_T_PRESCALER, 0x3E)
        self._w(self.REG_T_RELOAD_L,  30)
        self._w(self.REG_T_RELOAD_H,  0)
        self._w(self.REG_TX_ASK,      0x40)
        self._w(self.REG_MODE,        0x3D)
        self._set_bits(self.REG_TX_CONTROL, 0x03)
        utime.sleep_ms(10)

    def _transceive(self, data, framing_bits=0):
        self._w(self.REG_COMMAND,     self.PCD_IDLE)
        self._w(self.REG_COM_IRQ,     0x7F)
        self._set_bits(self.REG_FIFO_LEVEL, 0x80)
        for b in data:
            self._w(self.REG_FIFO_DATA, b)
        self._w(self.REG_BIT_FRAMING, framing_bits)
        self._w(self.REG_COMMAND,     self.PCD_TRANSCEIVE)
        self._set_bits(self.REG_BIT_FRAMING, 0x80)

        timeout = 2000
        while timeout > 0:
            irq = self._r(self.REG_COM_IRQ)
            if irq & 0x30:
                break
            if irq & 0x01:
                self._clr_bits(self.REG_BIT_FRAMING, 0x80)
                return self.ERR, []
            timeout -= 1

        self._clr_bits(self.REG_BIT_FRAMING, 0x80)

        if timeout == 0:
            return self.ERR, []

        if self._r(self.REG_ERROR) & 0x1B:
            return self.ERR, []

        n = self._r(self.REG_FIFO_LEVEL)
        res = [self._r(self.REG_FIFO_DATA) for _ in range(n)]
        return self.OK, res

    def request(self):
        stat, res = self._transceive([self.PICC_REQIDL], framing_bits=0x07)
        if stat == self.OK and len(res) >= 2:
            return self.OK, res
        return self.NOTAG, []

    def anticoll(self):
        self._clr_bits(0x05, 0x04)
        self._clr_bits(0x02, 0x04)
        stat, uid = self._transceive([self.PICC_ANTICOLL, 0x20])
        self._set_bits(0x05, 0x04)
        self._set_bits(0x02, 0x04)

        if stat != self.OK or len(uid) < 4:
            return self.ERR, []

        # Verificar BCC
        bcc = uid[0] ^ uid[1] ^ uid[2] ^ uid[3]
        if len(uid) >= 5 and bcc != uid[4]:
            return self.ERR, []

        # Devolver 5 bytes: uid[0..3] + BCC
        # Igual que SimpleMFRC522 de la RPi
        bcc_byte = uid[4] if len(uid) >= 5 else bcc
        return self.OK, uid[:4] + [bcc_byte]

    def read_uid(self):
        """Retorna lista de 5 bytes (4 UID + BCC) o None."""
        stat, _ = self.request()
        if stat != self.OK:
            return None
        stat, uid = self.anticoll()
        if stat == self.OK:
            return uid  # 5 bytes
        return None