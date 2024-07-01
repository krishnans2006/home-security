#include <Arduino.h>

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <NTPClient.h>
#include <WiFiUdp.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const char *ssid = "SSID";
const char *password = "PASSWORD";

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");


void setup() {
    Serial1.begin(115200);
    Serial1.println("Hello World");

    // Address 0x3D for 128x64
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial1.println(F("SSD1306 allocation failed"));
        for(;;);
    }

    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.display();

    Serial1.print("Connecting to WiFi");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial1.println(".");
    }

    timeClient.begin();
    timeClient.setTimeOffset(-3600 * 4);  // UTC -4
}

void loop() {
    delay(1);
}
