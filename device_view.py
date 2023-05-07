from nicegui import ui
from nicegui.events import MouseEventArguments
import base64
import scrcpy
import cv2
import threading
from adbutils import AdbError
import numpy as np


class Device:
    def __init__(self, serial, manager) -> None:
        self.serial = serial
        self.manager = manager
        self.device = manager.adb.device(serial)

    def execute(self, script):
        def run():
            try:
                self.device.push(f"./scripts/{script}.sh", "/data/local/tmp")
                self.device.shell(f"chmod 777 /data/local/tmp/{script}.sh")
                self.device.shell(f"/data/local/tmp/{script}.sh")
            except AdbError as e:
                pass

        threading.Thread(target=run, args=()).start()

    def root(self):
        self.device.root()

    def unroot(self):
        c = self.device.open_transport()
        c.send_command("unroot:")
        c.check_okay()
        c.read_until_close()

    def run(self, command):
        self.device.shell(command)

    def install_app(self, file_path):
        print(file_path)

        def run():
            try:
                self.device.install(file_path)
            except AdbError as e:
                pass

        threading.Thread(target=run, args=()).start()

    def move_file(self, file_path):
        def run():
            try:
                self.device.push(file_path, "/storage/emulated/0/Download")
                self.device.shell(
                    "am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///storage/emulated/0 -p com.android.providers.media"
                )

            except AdbError as e:
                pass

        threading.Thread(target=run, args=()).start()


class DeviceView(Device):
    def __init__(
        self,
        serial,
        bitrate=0,
        width=0,
        label=True,
        control=False,
        master=False,
        device_list=[],
        manager=None,
    ) -> None:
        super().__init__(serial, manager)
        self.is_focused = True if manager.focused_device == serial else False

        with ui.column():
            if control == False:
                ui.tooltip(f"Select device {serial}")
            if label:
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label(serial).style("font-size:14px")

            with ui.row():
                if control == True:
                    self.screen = ui.interactive_image(
                        cross=False,
                        events=["mousedown", "mouseup", "mousemove"],
                        on_mouse=self.mouse_handler,
                    )
                else:
                    self.screen = ui.interactive_image(
                        cross=False, events=["click"], on_mouse=self.click_handler
                    )

        # self.manager = manager

        self.bitrate = self.convert_quality(bitrate)
        self.width = self.convert_size(width)
        self.control = control
        self.master = master
        self.device_list = device_list

        # screen settings

        self.screen.source = self.capture()

        self.client = scrcpy.Client(
            device=self.serial,
            bitrate=self.bitrate,
            max_fps=24,
            max_width=self.width,
            stay_awake=True,
            lock_screen_orientation=0,
        )
        self.client.start(threaded=True)
        self.client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)

        self.master = master
        self.device_list = device_list

    def master_on(self, device_list):
        self.master = True
        self.device_list = device_list

    def master_off(self):
        self.master = False
        self.device_list = []

    def slave_work(self, master_width, master_x, master_y, master_action):
        w, _ = self.client.resolution
        ratio = w / master_width
        self.client.control.touch(master_x * ratio, master_y * ratio, master_action)

    def get_action(self, e):
        if e.type == "mousedown":
            return scrcpy.ACTION_DOWN
        if e.type == "mousemove":
            return scrcpy.ACTION_MOVE
        if e.type == "mouseup":
            return scrcpy.ACTION_UP

    async def click_handler(self, e: MouseEventArguments):
        if e.type == "click":
            self.manager.focus_device(self.serial)
            await ui.run_javascript("location.reload()", respond=False)

    def mouse_handler(self, e: MouseEventArguments):
        action = self.get_action(e)
        self.client.control.touch(e.image_x, e.image_y, action)

        if self.master == True:
            w, _ = self.client.resolution
            for slave in self.device_list:
                if slave.serial != self.serial:
                    threading.Thread(
                        target=slave.slave_work,
                        args=(
                            w,
                            e.image_x,
                            e.image_y,
                            action,
                        ),
                    ).start()

    def enter_key(self, key):
        self.device.keyevent(key)

        if self.master == True:
            for slave in self.device_list:
                if slave.serial != self.serial:
                    slave.enter_key(key)

    def convert_size(self, size):
        if size == 1:
            return 480
        if size == 2:
            return 720
        if size == 3:
            return 960
        return 240

    def convert_quality(self, quality):
        if quality == 1:
            return 125000
        if quality == 2:
            return 1000000
        if quality == 3:
            return 8000000
        return 15625

    def to_base64(self, img):
        _, im_arr = cv2.imencode(".jpeg", img)
        if im_arr is not None:
            try:
                im_bytes = im_arr.tobytes()
                im_b64 = str(base64.b64encode(im_bytes), "utf-8")
                if im_b64 is not None:
                    return "data:image/png;base64," + im_b64
            except:
                pass
        return

    def capture(self, width=136):
        img = self.device.screenshot()
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w = img.shape[0:2]
        neww = width
        newh = int(neww * (h / w))
        img = cv2.resize(img, (neww, newh))

        return self.to_base64(img)

    def on_frame(self, frame):
        if frame is not None:
            self.screen.source = self.to_base64(frame)

    def get_ratio(self, width):
        w, _ = self.device.window_size()
        return width / w
