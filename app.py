from nicegui import app,ui
from nicegui.events import MouseEventArguments
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

import pyperclip as c



ui.colors(primary='#2C3333')

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
    def __init__(self, serial: str, bitrate=0, width=0, label=True) -> None:
        super().__init__()
        self.serial = serial
        self.device = adb.device(serial)

        self.bitrate = self.convert_quality(bitrate)
        self.width = self.convert_size(width)

        if label:
            with self:
                self.content = f'<text x="0" y="15" fill="red">{serial}</text>'

        self.img = self.device.screenshot()

        self.source = ""
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
            return 480
        if size == 2:
            return 720
        if size == 3:
            return 960
        return 240
    
    def convert_quality(self,quality):
        if quality == 1:
            return 125000
        if quality == 2:
            return 1000000
        if quality == 3:
            return 8000000
        return 15625

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

    def capture(self,width =720): 
        img = self.device.screenshot()
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        h, w = img.shape[0:2]
        neww = width
        newh = int(neww*(h/w))
        img = cv2.resize(img, (neww, newh))

        return self.to_base64(img)
    
    def get_ratio(self,width):
        w, h  = self.device.window_size()
        return width / w


    def on_frame(self, frame):
        if frame is not None:
            self.source =  self.to_base64(frame)

    def execute(self,script):
        def run():
            try:
                if(script in sh_scripts):
                    self.device.push( f"./scripts/{script}.sh", "/data/local/tmp")
                    self.device.shell(f"chmod 777 /data/local/tmp/{script}.sh")
                    self.device.shell(f"/data/local/tmp/{script}.sh")
                elif(script == "Install Youtube"):
                    self.device.install("./apk/yt.apk")
            except AdbError as e:
                pass
        threading.Thread(target=run, args=()).start()

    

class AppManager:
    def __init__(self):
        self.quality = 0
        self.size = 0
    def set_quality(self,quality):
        self.quality = quality
    def set_size(self,size):
        self.size = size

manager = AppManager()


@ui.page('/')  
def home():
    global manager
    device_list=[]
    def load_device_list(): 
        return [d.serial for d in adb.device_list()]

    device_list = load_device_list()
    with ui.row().style(f'width:100%'):
        device_views = [DeviceView(d,manager.quality,manager.size) for d in device_list]

    def execute_script():
        for view in device_views:
            view.execute(select_script.value)

    async def reload():
        for client in client_list():
            client.stop()
        global device_list
        device_list= load_device_list()
        await ui.run_javascript('location.reload()', respond=False)

    
    with ui.header(elevated=True).classes('items-center justify-between'):
        with ui.row().classes('items-center justify-between'):
            ui.icon('android').style('font-size:20px')
            ui.label('Overview').style('font-size:20px')
            
        
        ui.button(on_click=lambda: right_drawer.toggle()).props('flat color=white icon=menu')
    with ui.right_drawer(fixed=True).style('background-color: #2C3333').props('bordered') as right_drawer:
        with ui.column():
            with ui.row().classes('items-center my-4').style('width:100%'):
                with ui.row().classes('items-center justify-between').style('width:100%'):
                    ui.label(f'Connected devices: {len(device_list)}')
                    ui.button(on_click=reload).props('icon=autorenew')
                
                

        with ui.column().classes('w-full'):
            with ui.expansion('List', icon="list").classes('w-full my-1'):
                with ui.row().classes('my-4').style('display:flex;justify-content:center;width:100%'):
                    with ui.row().style('width:90%'):
                        columns = [
                            {'name': 'Model', 'label': 'Model', 'field': 'model', },
                            {'name': 'Serial', 'label': 'Serial', 'field': 'serial', },
                        ]
                        rows = [
                            {'model': adb.device(d).prop.model, 'serial': d} for i, d in enumerate(device_list)
                        ]
                        ui.table(columns=columns, rows=rows,row_key='serial').style('width:100%')
            
            with ui.expansion('View', icon="smartphone").classes('w-full my-1'):
                with ui.row().classes('my-4').style('display:flex;justify-content:center;width:100%'):
                    with ui.row().style('width:90%'):
                        select_device = ui.select(device_list,value = device_list[0] if len(device_list)>0 else None).classes('w-full')
                        ui.button('View',on_click=lambda:ui.open(f'/device/{select_device.value}')).style('margin-top:12px').classes('w-full')

            with ui.expansion('Scripts', icon = "code" ).classes('w-full my-1'):
                with ui.row().classes('my-4').style('display:flex;justify-content:center;width:100%'):
                    with ui.row().style('width:90%'):
                        select_script = ui.select(scripts, value = scripts[0]).classes('w-full')
                        ui.button('Execute',on_click=execute_script).classes('w-full')
            with ui.expansion('Settings', icon="settings").classes('w-full my-1'):
                async def save_settings():
                        manager.set_quality(quality_select.value)
                        manager.set_size(size_select.value)
                        await ui.run_javascript('location.reload()', respond=False)
                with ui.row().classes('my-4').style('display:flex;justify-content:center;width:100%'):
                    with ui.row().style('width:90%'):
                        with ui.column().classes('w-full my-4'):
                            with ui.row().classes('items-center'):
                                ui.icon('build')
                                ui.label('Quality')
                            quality_select = ui.slider(min=0, max=2).bind_value(manager, 'quality').style('width:100%')
                            with ui.row().classes('items-center justify-between').style('width:100%'):
                                ui.label('Low')
                                ui.label('Medium')
                                ui.label('High')

                        with ui.column().classes('w-full my-4'):
                            with ui.row().classes('items-center'):
                                ui.icon('build')
                                ui.label('Size')
                            size_select = ui.slider(min=0, max=2).bind_value(manager, 'size').style('width:100%')
                            with ui.row().classes('items-center justify-between').style('width:100%'):
                                ui.label('S')
                                ui.label('M')
                                ui.label('L')
                        ui.button('Save Settings', on_click=save_settings).classes('w-full')

home()
mouse_click_count = 0
gen_script="#!/bin/sh\n"
@ui.page('/device/{serial}')
def page(serial: str):
    device_list=[]
    def load_device_list(): 
        return [d.serial for d in adb.device_list()]

    device_list = load_device_list()

    def screenshot():
        dialog.open()

        ui.update(dialog)

    
    def mouse_handler(e: MouseEventArguments):
        global gen_script
        global mouse_click_count
        ii.content += f'<circle cx="{e.image_x}" cy="{e.image_y}" r="10" fill="black"></circle>'
        ii.content += f'<text x="{e.image_x}" y="{e.image_y+4}" fill="red" font-size="10px" text-anchor="middle">{mouse_click_count}</text>'
        # ui.notify(
        #     f'{int(e.image_x/ratio)}, {int(e.image_y/ratio)}')
        
        log.push(f"x: {int(e.image_x/ratio)} y:{int(e.image_y/ratio)}")
        shell_log.push(f"input tap {int(e.image_x/ratio)} {int(e.image_y/ratio)}")
        shell_log.push(f"sleep 1;")
        gen_script+=f"input tap {int(e.image_x/ratio)} {int(e.image_y/ratio)}\n"
        gen_script+=f"sleep 1;\n"



        mouse_click_count +=1

    def get_capture():
        return view.capture(width=360)
    
    def update_screenshot():
        global mouse_click_count
        global gen_script

        log.clear()
        shell_log.clear()

        mouse_click_count = 0
        ii.source = get_capture()
        ii.content=""

        gen_script=""

    def copy_script():
        global gen_script
        c.copy(gen_script)
        ui.notify('Script copied')


        
    with ui.row().style('width:100%; display:flex'):
        with ui.column():
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center'):
                    with ui.switch('Master device'):
                        ui.tooltip('Every device will mimic this device')

                with ui.button(on_click=screenshot).props('icon=screenshot') as screenshot_btn:
                    ui.tooltip('Screenshot')
                    

            view = DeviceView(serial,3,2,False)
            with ui.dialog() as dialog, ui.card():
                with ui.row():
                    with ui.column():
                        ratio = view.get_ratio(width=360)
                        img = get_capture()
                        
                        with ui.row():
                            ui.button(on_click=update_screenshot).props('icon=refresh')

                            

                        ii = ui.interactive_image(img, on_mouse=mouse_handler, events=['mousedown'], cross=True)
                    with ui.column():

                        with ui.column().style('width:120px; '):
                            with ui.row().classes('w-full items-center'):
                                ui.label("Touch").style('font-size:18px')
                            log=ui.log(max_lines=100).classes('w-full').style('font-size:12px;height:100px')

                        with ui.column().style('width:120px'):
                            with ui.row().classes('w-full items-center justify-between'):
                                ui.label("Script").style('font-size:18px')
                                ui.button(on_click=copy_script).props('flat color=white icon=content_copy')
                            shell_log=ui.log(max_lines=100).classes('w-full').style('font-size:12px;height:480px')
                        
                                
                    
        with ui.row().style('flex:1'):
            device_views = [DeviceView(d) for d in device_list]
    

        
    def screenshot():
        dialog.open()
        
    with ui.header(elevated=True).classes('items-center justify-between').style('background-color:#2C3333'):
        with ui.row().classes('items-center').style('gap:100px'):  
            with ui.row().classes('items-center justify-between'):
                ui.button(on_click=lambda: ui.open('/')).props('flat color=white icon=arrow_back_ios_new')
                ui.icon('smartphone').style('font-size:20px')
                ui.label(f'Serial: {serial}').style('font-size:20px')
                ui.label(f'Model: {view.device.prop.model}').style('font-size:20px')
                ui.label(f'Device: {view.device.prop.device}').style('font-size:20px')


            
        


ui.run(title='Chicken Farm v0.0.1',favicon="icon.png",dark=True)

# def on_close():
#     for client in client_list():
#         client.stop()

# app.on_shutdown(on_close)