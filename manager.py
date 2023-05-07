import adbutils
import os


class AppManager:
    def __init__(self):
        self.adb = adbutils.AdbClient()

        self.serials_list = [d.serial for d in self.adb.device_list()]

        self.sh_scripts = []
        self.custom_scripts = []

        self.apk_list = []

        try:
            for x in os.listdir("./scripts"):
                if x.endswith(".sh"):
                    self.sh_scripts.append(x.split(".")[0])
        except:
            pass

        self.scripts = self.custom_scripts + self.sh_scripts

        # self.apk_list = []

        # for x in os.listdir("./apk"):
        #     if x.endswith(".apk") or x.endswith(".xapk") :
        #         self.apk_list.append(x.split(".")[0])

        self.view_quality = 0

        self.view_size = 0

        self.selected_devices = []

        self.is_focused = False
        self.focused_device = None

        self.sync_control = False

        self.mouse_click_count = 0
        self.gen_script = "#!/bin/sh\n"

    def connect_remote(self, addresses):
        for address in addresses:
            self.adb.connect(address)

    def toggle_sync_control(self):
        self.sync_control = True if self.sync_control == False else False

    def focus_device(self, serial):
        if self.focused_device == serial:
            self.is_focused = False
            self.focused_device = None
        else:
            self.focused_device = serial
            self.is_focused = True

    def select_device(self, selected_devices):
        self.selected_devices = selected_devices

    def reload_device_list(self):
        self.serials_list = [d.serial for d in self.adb.device_list()]

    def set_quality(self, quality):
        self.view_quality = quality

    def set_size(self, size):
        self.view_size = size
