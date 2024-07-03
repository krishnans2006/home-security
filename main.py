import socket
import struct

from machine import Pin, SoftI2C, RTC
import network
import time

import ssd1306


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

NTP_HOST = "pool.ntp.org"
NTP_DELTA = 2208988800 - (3600 * -4)  # UTC-4
NTP_CORRECTION = 12

OLED_WIDTH = 128
OLED_HEIGHT = 64


wlan = network.WLAN(network.STA_IF)

i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=0x3c)


def connect_wifi():
    print("Connecting to WiFi", end="")

    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.2)

    print(f"Done! @ {wlan.ifconfig()[0]}")


def sync_time():
    print(f"Starting NTP sync with initial time {time.localtime()}")

    ntp_query = bytearray(48)
    ntp_query[0] = 0x1B

    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.settimeout(1)
        s.sendto(ntp_query, addr)
        msg = s.recv(48)
    except OSError as e:
        if e.args[0] == 110:  # ETIMEDOUT
            print("NTP request timed out")
            return
    finally:
        s.close()

    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA - NTP_CORRECTION
    tm = time.gmtime(t)
    RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

    print(f"Time synced to {time.localtime()}")


def get_datetime():
    t = RTC().datetime()
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[4]:02d}:{t[5]:02d}:{t[6]:02d}"


def loop():
    date, time = get_datetime().split()

    oled.fill(0)
    oled.text(date, 0, 0)
    oled.text(time, 0, 10)
    oled.show()


def main():
    connect_wifi()
    sync_time()

    while True:
        loop()
        time.sleep(1)


if __name__ == "__main__":
    main()
    time.sleep(2)
