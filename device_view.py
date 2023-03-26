from nicegui import ui
import base64
from PIL import Image
import adbutils
import scrcpy
import io
import cv2
import threading
import os
from adbutils import AdbError
import numpy as np
from device_view import DeviceView

class DeviceView(ui.interactive_image):
    def __init__(self, serial: str, bit_rate=1000, width=300) -> None:
        super().__init__()
        self.serial = serial
        self.device = adbutils.AdbClient().device(serial)
        with self:
            self.content = f'<text x="0" y="15" fill="red">{serial}</text>'

        self.source = ""
        self.classes('border border-gray-900')

        client = scrcpy.Client(device=serial, bitrate=bit_rate, max_fps=24,
                               max_width=width, stay_awake=True, lock_screen_orientation=0)
        client.start(threaded=True)
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)

    def on_frame(self, frame):
        if frame is not None:
            _, im_arr = cv2.imencode('.jpeg', frame)
            if im_arr is not None:
                try:
                    im_bytes = im_arr.tobytes()
                    im_b64 = str(base64.b64encode(im_bytes), "utf-8")
                    if(im_b64 is not None):
                        self.source = "data:image/png;base64," + im_b64
                except:
                    pass