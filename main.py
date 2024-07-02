import machine
import network
import time


print("Connecting to WiFi", end="")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")

while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.2)

print(f"Done! @ {wlan.ifconfig()[0]}")

time.sleep(2)
