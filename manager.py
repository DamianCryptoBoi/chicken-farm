import adbutils
import os

class AppManager:
    def __init__(self):
        self.adb =  adbutils.AdbClient()

        self.serials_list = [d.serial for d in self.adb.device_list()]

        sh_scripts = []
        custom_scripts = ["Install Youtube"]

        for x in os.listdir("./scripts"):
            if x.endswith(".sh"):
                sh_scripts.append(x.split(".")[0])
        
        self.scripts = custom_scripts + sh_scripts

        self.view_quality = 0
        
        self.view_size = 0

        self.selected_devices=[]

    def select_device(self,selected_devices):
        self.selected_devices = selected_devices
        
    def set_quality(self,quality):
        self.view_quality = quality

    def set_size(self,size):
        self.view_size = size