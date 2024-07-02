from machine import Pin, SoftI2C
import network
import time

import ssd1306

print("Connecting to WiFi", end="")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")

while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.2)

print(f"Done! @ {wlan.ifconfig()[0]}")


i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 64

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text("Hello, World!", 0, 0)
oled.text("Hello, World!", 0, 10)
oled.text("Hello, World!", 0, 20)
oled.text("Hello, World!", 0, 30)
oled.show()

time.sleep(2)
