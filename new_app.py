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

from manager import AppManager

manager=AppManager()

with ui.column().classes("w-full"):
    with ui.dialog() as dialog, ui.card():
        ui.label('Hello world!')
        ui.button('Close', on_click=dialog.close)

    with ui.row().classes("w-full justify-between"):
        with ui.button(on_click=dialog.open).props('flat color=white icon=autorenew'):
            ui.tooltip('Refresh devices')
        with ui.button(on_click=dialog.open).props('flat color=white icon=apps'):
            ui.tooltip('View all devices')
        with ui.button(on_click=dialog.open).props('flat color=white icon=code'):
            ui.tooltip('Run scripts')
        with ui.button(on_click=dialog.open).props('flat color=white icon=restart_alt'):
            ui.tooltip('Reboot')
        with ui.button(on_click=dialog.open).props('flat color=white icon=shield'):
            ui.tooltip('Add proxies')
        with ui.button(on_click=dialog.open).props('flat color=white icon=schedule'):
            ui.tooltip('Set timezone')
        

    with ui.row().classes("w-full"):
        def get_state(state):
            if state == "offline":
                return "Offline"
            if state == "bootloader":
                return "boot"
            if state == "device":
                return "Online"
            
        def handle_select_devices(event):
            selected_device_serials = [device["serial"] for device in event.selection]
            manager.select_device(selected_device_serials)

        columns = [
            {'name': 'ID', 'label': 'ID', 'field': 'id', },
            {'name': 'Serial', 'label': 'Serial', 'field': 'serial', },
            {'name': 'Model', 'label': 'Model', 'field': 'model', },
            {'name': 'Device', 'label': 'Device', 'field': 'name', },
            {'name': 'Resolution', 'label': 'Resolution', 'field': 'resolution', },
            {'name': 'State', 'label': 'State', 'field': 'state', },
            {'name': 'Proxy', 'label': 'Proxy', 'field': 'proxy', },
            {'name': 'Timezone', 'label': 'Timezone', 'field': 'tz', },


        ]
        rows = [
            {"id":i+1,"proxy":'none','tz':"default",'model': manager.adb.device(d).prop.model, "name": manager.adb.device(d).prop.device,'serial': d, "resolution":f"{manager.adb.device(d).window_size()[0]}x{manager.adb.device(d).window_size()[1]}", "state":get_state(manager.adb.device(d).get_state())} for i, d in enumerate(manager.serials_list)
        ]
        ui.table(on_select=handle_select_devices,columns=columns, rows=rows,row_key='serial', selection='multiple', title=f"Connected device(s): {len(manager.serials_list)}").style('width:100%')

ui.run(dark=True,native=True)