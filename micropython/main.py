import gc
import inky_frame
import jpegdec
import machine
import sdcard
import time
import uasyncio
import uos
from network_manager import NetworkManager
from urllib import urequest

import config

# from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY      # 5.7"
# from picographics import PicoGraphics, DISPLAY_INKY_FRAME_4 as DISPLAY  # 4.0"
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY  # 7.3"

# Examples:  tz_offset = -7 # Pacific time (PST)
#            tz_offset =  1 # CEST (Paris)
tz_offset = 1
tz_seconds = tz_offset * 3600

inky_frame.pcf_to_pico_rtc()


def network_status_handler(mode, status, ip):
    print("NETWORK", mode, status, ip)


if inky_frame.woken_by_rtc() or inky_frame.woken_by_button():

    print("Awake!")

    graphics = PicoGraphics(DISPLAY)
    WIDTH, HEIGHT = graphics.get_bounds()

    BASE_URL = config.ENDPOINT_URL
    DISPLAY_ID = config.DISPLAY_ID
    SLEEP_MINS = config.SLEEP_MINS
    URL = "{0}/outputs/{1}?w={2}&h={3}".format(BASE_URL, DISPLAY_ID, WIDTH, HEIGHT)

    print("")
    print("DISPLAY SIZE:   {0} x {1}".format(WIDTH, HEIGHT))
    print("BASE URL:       {0}".format(BASE_URL))
    print("DISPLAY ID:     {0}".format(DISPLAY_ID))
    print("URL:            {0}".format(URL))
    print("SLEEP MINS:     {0}".format(SLEEP_MINS))
    print("")

    graphics.set_pen(1)
    graphics.clear()

    now = time.localtime(time.time() + tz_seconds)
    year = now[0]

    if year < 2030:
        connected = False
        network_manager = NetworkManager(
            config.COUNTRY, status_handler=network_status_handler, client_timeout=60
        )
        t_start = time.time()
        try:
            uasyncio.get_event_loop().run_until_complete(
                network_manager.client(config.SSID, config.PSK)
            )
            connected = True
        except RuntimeError:
            pass
        t_end = time.time()

        if connected:
            print("Network Connected!")
            inky_frame.set_time()
            # graphics.text("Setting time from network...", 0, 40)
            # graphics.text(f"Connection took: {t_end-t_start}s", 0, 60)
        else:
            graphics.text("Failed to connect!", 0, 40)

    sd_spi = machine.SPI(
        0,
        sck=machine.Pin(18, machine.Pin.OUT),
        mosi=machine.Pin(19, machine.Pin.OUT),
        miso=machine.Pin(16, machine.Pin.OUT),
    )
    sd = sdcard.SDCard(sd_spi, machine.Pin(22))
    uos.mount(sd, "/sd")
    gc.collect()

    print("Downloading image...")
    socket = urequest.urlopen(URL)

    temp_file = "/sd/image.jpg"
    data = bytearray(1024)
    with open(temp_file, "wb") as f:
        while True:
            if socket.readinto(data) == 0:
                break
            f.write(data)
    socket.close()
    gc.collect()

    jpeg = jpegdec.JPEG(graphics)
    gc.collect()

    graphics.set_pen(1)
    graphics.clear()

    jpeg.open_file(temp_file)
    jpeg.decode()

    print("Rendering Display...")
    graphics.update()

    print("Sleeping for {0} mins".format(SLEEP_MINS))
    inky_frame.sleep_for(SLEEP_MINS)
