from nicegui import app,ui
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




adb = adbutils.AdbClient()


client_list = []
device_view = []
sh_scripts = []
custom_scripts = ["Install Youtube"]

for x in os.listdir("./scripts"):
    if x.endswith(".sh"):
        sh_scripts.append(x.split(".")[0])

scripts = custom_scripts + sh_scripts




class DeviceView(ui.interactive_image):
    def __init__(self, serial: str, bitrate=0, width=0) -> None:
        super().__init__()
        self.serial = serial
        self.device = adb.device(serial)

        self.bitrate = self.convert_quality(bitrate)
        self.width = self.convert_size(width)
        with self:
            self.content = f'<text x="0" y="15" fill="red">{serial}</text>'
        self.img = self.device.screenshot()

        self.source = self.capture()
        self.classes('border border-gray-900')

        self.start_client(self.bitrate,self.width)

    def start_client(self,br,w):
        client = scrcpy.Client(device=self.serial, bitrate=br, max_fps=24,
                               max_width=w, stay_awake=True, lock_screen_orientation=0)
        client.start(threaded=True)
        client.add_listener(scrcpy.EVENT_FRAME, self.on_frame)
        client_list.append(client)

    def convert_size(self,size):
        if size ==1:
            return 500
        if size == 2:
            return 1000
        return 300
    
    def convert_quality(self,quality):
        if quality == 100000:
            return 500
        if quality == 1000000:
            return 1000
        return 10000

    def to_base64(self,img):
        _, im_arr = cv2.imencode('.jpeg', img)
        if im_arr is not None:
            try:
                im_bytes = im_arr.tobytes()
                im_b64 = str(base64.b64encode(im_bytes), "utf-8")
                if(im_b64 is not None):
                    return  "data:image/png;base64," + im_b64
            except:
                pass
        return

    def capture(self,width =168): 
        img = self.device.screenshot()
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w = img.shape[0:2]
        neww = width
        newh = int(neww*(h/w))
        img = cv2.resize(img, (neww, newh))

        return self.to_base64(img)


    def on_frame(self, frame):
        if frame is not None:
            self.source =  self.to_base64(frame)

class AppManager:
    def __init__(self):
        self.quality = 0
        self.size = 0
    def set_quality(self,quality):
        self.quality = quality
    def set_size(self,size):
        self.size = size




@ui.page('/')


async def home():
    manager = AppManager()
    device_list=[]
    def load_device_list(): 
        return [d.serial for d in adb.device_list()]

    device_list = load_device_list()

    with ui.row().style(f'width:100%'):
        [DeviceView(d,manager.quality,manager.size) for d in device_list]

    async def reload():
        global device_list
        device_list= load_device_list()
        await ui.run_javascript('location.reload()', respond=False)
        


    # def update_device_list():
    #     for view in device_view_list:
    #         ui.update(view)

        # device_view_list = [DeviceView(d,manager.quality,manager.size) for d in device_list]

    # a = DeviceView(device_list[0],manager.quality,manager.size)
    # def update_device_list():
    #     client_list[0].stop()
    #     client_list=[]
    #     a.start_client(a.convert_quality(manager.quality),a.convert_size(manager.size))
    #     ui.update(a)

    
    with ui.header(elevated=True).style('background-color: #0E8388').classes('items-center justify-between'):
        with ui.row().classes('items-center justify-between'):
            ui.icon('home')
            ui.label('Overview')
        ui.button(on_click=lambda: right_drawer.toggle()).props('flat color=white icon=menu')
    with ui.right_drawer(fixed=True).style('background-color: #2C3333').props('bordered') as right_drawer:
        with ui.column():
            with ui.row().classes('items-center my-4'):
                ui.icon('list')
                with ui.row().classes('items-center justify-between').style('width:100%'):
                    ui.label(f'Connected devices: {len(device_list)}')
                    ui.button(on_click=reload).props('icon=autorenew')
                columns = [
                    {'name': 'ID', 'label': 'ID', 'field': 'id'},
                    {'name': 'Device', 'label': 'Device', 'field': 'device', },
                    {'name': 'Serial', 'label': 'Serial', 'field': 'serial', },
                ]
                rows = [
                        {'id': i+1, 'device': adb.device(d).prop.device, 'serial': d} for i, d in enumerate(device_list)
                ]
                ui.table(columns=columns, rows=rows,row_key='serial')
            # with ui.column().style('width:100%'):
            #     with ui.row().classes('items-center justify-between').style('width:100%'):
            #         with ui.row().classes('items-center'):
            #             ui.icon('settings')
            #             ui.label('Settings')
            #         ui.button('Save', on_click=update_device_list)
            #     with ui.column().style('width:100%'):
            #         ui.label('Quality')
            #         ui.slider(min=0, max=2).bind_value(manager, 'quality').style('width:100%')
            #         with ui.row().classes('items-center justify-between').style('width:100%'):
            #             ui.label('Low')
            #             ui.label('Medium')
            #             ui.label('High')

            #     with ui.column().style('width:100%'):
            #         ui.label('Size')
            #         ui.slider(min=0, max=2).bind_value(manager, 'size').style('width:100%')
            #         with ui.row().classes('items-center justify-between').style('width:100%'):
            #             ui.label('S')
            #             ui.label('M')
            #             ui.label('L')
                

                    
                

home()

ui.run(title='Chicken Farm v0.0.1',favicon="icon.png",dark=True)