from machine import Pin, SoftI2C
import network
import time

import ssd1306


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

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


def main():
    connect_wifi()
    oled.text("Hello, World!", 0, 0)
    oled.text("Hello, World!", 0, 10)
    oled.text("Hello, World!", 0, 20)
    oled.text("Hello, World!", 0, 30)
    oled.show()

    time.sleep(2)


if __name__ == "__main__":
    main()
