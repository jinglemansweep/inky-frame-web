import gc
import inky_frame
import jpegdec
import machine
import sdcard
import time
import uasyncio
import uos
import urequests as requests
from network_manager import NetworkManager

import config
import secrets

# from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY      # 5.7"
# from picographics import PicoGraphics, DISPLAY_INKY_FRAME_4 as DISPLAY  # 4.0"
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY  # 7.3"

# SETUP TIMEZONE (0=GMT, 1=BST/CEST, -7=PST)
tz_offset = 1
tz_seconds = tz_offset * 3600

# SYNC RTC CLOCKS
inky_frame.pcf_to_pico_rtc()

# SETUP SD CARD
sd_spi = machine.SPI(
    0,
    sck=machine.Pin(18, machine.Pin.OUT),
    mosi=machine.Pin(19, machine.Pin.OUT),
    miso=machine.Pin(16, machine.Pin.OUT),
)
sd = sdcard.SDCard(sd_spi, machine.Pin(22))
uos.mount(sd, "/sd")
gc.collect()

# SETUP DISPLAY
graphics = PicoGraphics(DISPLAY)
WIDTH, HEIGHT = graphics.get_bounds()

# CONFIGURATION
BASE_URL = config.ENDPOINT_URL
DISPLAY_ID = config.DISPLAY_ID
SLEEP_MINS = config.SLEEP_MINS
URL = "{0}/outputs/{1}?w={2}&h={3}".format(BASE_URL, DISPLAY_ID, WIDTH, HEIGHT)

print("")
print("Configuration:")
print("")
print("  Display Size:   {0} x {1}".format(WIDTH, HEIGHT))
print("  Base URL:       {0}".format(BASE_URL))
print("  Display ID:     {0}".format(DISPLAY_ID))
print("  Endpoint URL:   {0}".format(URL))
print("  Sleep (Mins):   {0}".format(SLEEP_MINS))
print("")


# CALLBACKS / HELPERS
def network_status_handler(mode, status, ip):
    print(
        "Network {0} > {1}".format(
            mode, "Connected ({0})".format(ip) if status else "Connecting..."
        )
    )


# Run in a loop, although on battery, the RTC sleep actually powers off, so loop only runs once
while True:

    print("Main Loop Start!")

    woken_by_rtc = inky_frame.woken_by_rtc()
    woken_by_button = inky_frame.woken_by_button()

    if woken_by_rtc or woken_by_button:

        print("Awake! RTC: {0} | Button: {1}".format(woken_by_rtc, woken_by_button))

        # Clear display
        graphics.set_pen(1)
        graphics.clear()

        connected = False
        network_manager = NetworkManager(
            secrets.WIFI_COUNTRY,
            status_handler=network_status_handler,
            client_timeout=60,
        )
        t_start = time.time()
        try:
            uasyncio.get_event_loop().run_until_complete(
                network_manager.client(secrets.WIFI_SSID, secrets.WIFI_PSK)
            )
            connected = True
        except RuntimeError:
            pass
        t_end = time.time()

        if connected:
            print("Network Connected!")
            # Perform NTP time sync
            inky_frame.set_time()
            # graphics.text("Setting time from network...", 0, 40)
            # graphics.text(f"Connection took: {t_end-t_start}s", 0, 60)
        else:
            print("Network Connection Failed!")
            # graphics.text("Failed to connect!", 0, 40)

        print("Downloading Image...")
        try:
            temp_file = "/sd/image.jpg"

            # Fetch next image
            res = requests.get(url=URL)
            etag = res.headers["ETag"]
            print("ETag: {0}".format(etag))

            # Write image to SD cad
            with open(temp_file, "wb") as f:
                f.write(res.content)
            gc.collect()

            jpeg = jpegdec.JPEG(graphics)
            gc.collect()

            # Clear display
            graphics.set_pen(1)
            graphics.clear()

            # Decode JPEG
            jpeg.open_file(temp_file)
            jpeg.decode()

            # Update display
            print("Rendering Display...")
            graphics.update()

        except OSError:
            print("Download Failed!")
        except Exception:
            print("Something Failed!")

        # Low-power sleep
        print("Sleeping for {0} mins".format(SLEEP_MINS))
        inky_frame.sleep_for(SLEEP_MINS)
