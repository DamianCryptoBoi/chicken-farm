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


adb = adbutils.AdbClient()


client_list = []
device_view = []
sh_scripts = []
custom_scripts = ["Install Youtube"]

for x in os.listdir("./scripts"):
    if x.endswith(".sh"):
        sh_scripts.append(x.split(".")[0])

scripts = custom_scripts + sh_scripts




class DeviceView():

    def __init__(self,serial,bitrate=0,width=0,label=True,control=False,master=False,device_list=[]) -> None:


        with ui.column():
            if(label):
                with ui.row().classes('items-center justify-between w-full'):
                    ui.label(serial).style('font-size:10px')
                    ui.link('See Detail',f'/device/{serial}').style('font-size:10px; text-decoration:none')
            with ui.row():
                if control == True:
                    self.screen = ui.interactive_image(cross=False,events = ['mousedown', 'mouseup', "mousemove"],on_mouse= self.mouse_handler )
                else:
                    self.screen = ui.interactive_image()


        self.serial = serial
        self.device = adb.device(serial)
        self.bitrate = self.convert_quality(bitrate)
        self.width = self.convert_size(width)
        self.control = control
        self.master = master
        self.device_list = device_list

        # screen settings

        self.screen.source = self.capture()

        self.client = scrcpy.Client(device=self.serial, bitrate=self.bitrate, max_fps=24,
                               max_width=self.width, stay_awake=True, lock_screen_orientation=0)
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

    def slave_work(self,master_width,master_x,master_y,master_action):
        w,_ = self.client.resolution
        ratio = w/master_width
        self.client.control.touch(master_x*ratio,master_y*ratio,master_action)


    def get_action(self,e):
        if(e.type=="mousedown"):
            return scrcpy.ACTION_DOWN
        if(e.type == "mousemove"):
            return scrcpy.ACTION_MOVE
        if(e.type =="mouseup"):
            return scrcpy.ACTION_UP

    def mouse_handler(self,e: MouseEventArguments):
        action = self.get_action(e)
        self.client.control.touch(e.image_x, e.image_y, action)

        if self.master == True:
            w, _  = self.client.resolution
            for slave in self.device_list:
                threading.Thread(target=slave.slave_work, args=(w,e.image_x,e.image_y,action,)).start()

    def enter_key(self,key):
        self.device.keyevent(key)

        if self.master == True:
            for slave in self.device_list:
                slave.enter_key(key)
                
                
    
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
            self.screen.source =  self.to_base64(frame)

    def get_ratio(self,width):
            w, _  = self.device.window_size()
            return width / w
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

    def toggle_master_mode(e):
        if e.value == True:
            view.master_on(device_views)
        elif e.value == False:
            view.master_off()
            


        
    with ui.row().style('width:100%; display:flex'):
        with ui.column():
            current_device=ui.select(device_list, value=serial,on_change=lambda:ui.open(f'/device/{current_device.value}')).classes('w-full')
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center'):
                    with ui.switch('Master mode',on_change=toggle_master_mode):
                        ui.tooltip('Every other devices will follow this device')

                with ui.button(on_click=screenshot).props('icon=screenshot') as screenshot_btn:
                    ui.tooltip('Screenshot')
                    
            with ui.column():
                view = DeviceView(serial,2,1,label=False,control=True)
                with ui.row().classes("w-full justify-between"):
                    ui.button(on_click=lambda:view.enter_key("BACK")).props('flat color=white icon=arrow_back_ios_new')
                    ui.button(on_click=lambda:view.enter_key("HOME")).props('flat color=white icon=circle')
                    ui.button(on_click=lambda:view.enter_key("187")).props('flat color=white icon=crop_din')
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
            device_views = [DeviceView(d,) for d in filter(lambda device: device != current_device.value,device_list)]
    

        
    def screenshot():
        dialog.open()
        
    with ui.header(elevated=True).classes('items-center justify-between').style('background-color:#2C3333'):
        with ui.row().classes('items-center').style('gap:100px'):
            
            with ui.row().classes('items-center justify-between'):
                ui.button(on_click=lambda: ui.open('/')).props('flat color=white icon=arrow_back_ios_new')
                ui.icon('smartphone').style('font-size:20px')
                ui.label(f'Serial: {serial}').style('font-size:20px')
                # ui.label(f'Model: {view.device.prop.model}').style('font-size:20px')
                # ui.label(f'Device: {view.device.prop.device}').style('font-size:20px')


            
        


ui.run(title='Chicken Farm v0.0.1',favicon="icon.png",dark=True,reload=False,native=True)

adb.server_kill()

