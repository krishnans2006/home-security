import socket
import struct

from machine import Pin, SoftI2C, RTC, PWM
import network
import time

import ssd1306
import neopixel


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

NTP_HOST = "pool.ntp.org"
NTP_DELTA = 2208988800 - (3600 * -4)  # UTC-4
NTP_CORRECTION = 12

OLED_WIDTH = 128
OLED_HEIGHT = 64

LOOP_TICK_SEC = 0.1
CLOCK_TICK_SEC = 0.5

tick = CLOCK_TICK_SEC / LOOP_TICK_SEC

wlan = network.WLAN(network.STA_IF)

oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, SoftI2C(scl=Pin(5), sda=Pin(4)), addr=0x3c)
pir = Pin(6, Pin.IN, Pin.PULL_DOWN)
beeper = PWM(Pin(7))
pixel = neopixel.Neopixel(1, 0, 8, "RGB")

state = {
    "is_motion_now": False,
    "last_motion_detected": time.time(),
    "motion_since_start": False,
    "clock": 0,
}


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


def on_motion_change(_):
    if pir.value() == 1:
        on_motion(_)
    else:
        on_no_motion(_)


def on_motion(_):
    state["is_motion_now"] = True
    state["motion_since_start"] = True

    beeper.duty_ns(512)
    pixel.fill((255, 0, 0))
    pixel.show()


def on_no_motion(_):
    state["is_motion_now"] = False
    state["last_motion_detected"] = time.time()

    beeper.duty_ns(0)
    pixel.fill((0, 0, 0))
    pixel.show()


def setup():
    connect_wifi()
    sync_time()

    beeper.freq(440)
    beeper.duty_ns(0)

    pir.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_motion_change)

    pixel.fill((0, 0, 0))
    pixel.show()


def loop():
    # The clock tick is used for timed actions (buzzer/pixel sequences)
    state["clock"] += 1
    if state["clock"] >= tick:
        state["clock"] = 0
        clock_tick = True
    else:
        clock_tick = False

    date_now, time_now = get_datetime().split()

    oled.fill(0)
    oled.text(date_now, 0, 0)
    oled.text(time_now, 0, 10)

    if state["is_motion_now"]:
        oled.text("Motion detected", 0, 30)

        if clock_tick:
            beeper_freq = beeper.freq()
            beeper.freq(440 if beeper_freq == 330 else 330)
    elif not state["motion_since_start"]:
        oled.text(f"No motion since boot @", 0, 30)
        oled.text(f"{time.time() - state['last_motion_detected']:.1f}s ago", 0, 40)
    else:
        oled.text("No motion", 0, 30)
        oled.text(f"Last motion:", 0, 40)
        oled.text(f"{time.time() - state['last_motion_detected']:.1f}s ago", 0, 50)

    oled.show()

    print(pir.value())


def main():
    setup()

    while True:
        loop()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
    time.sleep(2)
