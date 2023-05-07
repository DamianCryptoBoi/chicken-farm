from nicegui import ui
from nicegui.events import MouseEventArguments
import os
import pyperclip as c
import shutil

from manager import AppManager
from device_view import Device, DeviceView

manager = AppManager()


@ui.page("/")
def dashboard():
    with ui.column().classes("w-full") as app:

        async def reload_device_list():
            manager.reload_device_list()
            await ui.run_javascript("location.reload()", respond=False)

        def execute_scripts():
            if len(manager.selected_devices) > 0:
                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).execute(select_script.value)
                select_script_dialog.close
                ui.notify(
                    f"[{select_script.value}] executed on {len(manager.selected_devices)} device(s)"
                )

            else:
                ui.notify("Select a device")

        def reboot():
            if len(manager.selected_devices) > 0:
                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).run("reboot")
                select_script_dialog.close
                ui.notify(f"Rebooted {len(manager.selected_devices)} device(s)")

            else:
                ui.notify("Select a device")

        def install_app(e):
            if len(manager.selected_devices) > 0:
                file = f"./files/{e.name}"
                os.makedirs("./files", exist_ok=True)
                with open(file, "wb") as f:
                    shutil.copyfileobj(e.content, f)
                f.close()

                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).install_app(file)

                ui.notify(
                    f"[{e.name}] installed on {len(manager.selected_devices)} device(s)"
                )

            else:
                ui.notify("Select a device")

        def move_file(e):
            if len(manager.selected_devices) > 0:
                file = f"./files/{e.name}"
                os.makedirs("./files", exist_ok=True)
                with open(file, "wb") as f:
                    shutil.copyfileobj(e.content, f)
                f.close()

                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).move_file(f"./files/{e.name}")
                ui.notify(
                    f"[{e.name}] transferred to {len(manager.selected_devices)} device(s)"
                )

            else:
                ui.notify("Select a device")

        def start_root(e):
            if len(manager.selected_devices) > 0:
                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).root()
                ui.notify(f"{len(manager.selected_devices)} device(s) changed")
            else:
                ui.notify("Select a device")

        def stop_root(e):
            if len(manager.selected_devices) > 0:
                for device_serial in manager.selected_devices:
                    Device(device_serial, manager).unroot()
                ui.notify(f"{len(manager.selected_devices)} device(s) changed")
            else:
                ui.notify("Select a device")

        def connect_remote():
            ui.notify(f"Connecting")
            addresses_list = add.value.split("\n")
            manager.connect_remote(addresses_list)
            ui.notify(f"Connected to {len(addresses_list)} device(s)")

        async def open_device_views():
            await ui.run_javascript('window.open("/devices", "_blank")')

        with ui.dialog() as dialog, ui.card():
            ui.label("Comming soon!")
            ui.button("Close", on_click=dialog.close)

        with ui.dialog() as remote_dialog, ui.card():
            add = ui.textarea(label="Enter addresses", placeholder="127.0.0.1:5555")
            ui.button("Connect", on_click=connect_remote)

        with ui.dialog() as select_script_dialog, ui.card():
            with ui.column():
                select_script = ui.select(
                    manager.scripts, value=manager.scripts[0]
                ).style("width:200px")
                ui.button("Run", on_click=execute_scripts).classes("w-full")

        with ui.dialog() as install_apk_dialog, ui.card():
            with ui.column():
                ui.upload(on_upload=install_app).classes("max-w-full")

        with ui.dialog() as move_file_dialog, ui.card():
            with ui.column():
                ui.upload(on_upload=move_file).classes("max-w-full")

        with ui.row().classes("w-full"):
            with ui.button(on_click=reload_device_list).props(
                "flat color=white icon=autorenew"
            ):
                ui.tooltip("Refresh devices")
            with ui.button(on_click=remote_dialog.open).props(
                "flat color=white icon=connect_without_contact"
            ):
                ui.tooltip("ADB remote connect")
            with ui.button(on_click=open_device_views).props(
                "flat color=white icon=apps"
            ):
                ui.tooltip("View all devices")
            with ui.button(on_click=select_script_dialog.open).props(
                "flat color=white icon=code"
            ):
                ui.tooltip("Run scripts")
            with ui.button(on_click=start_root).props(
                "flat color=white icon=admin_panel_settings"
            ):
                ui.tooltip("Root")
            with ui.button(on_click=stop_root).props(
                "flat color=white icon=no_accounts"
            ):
                ui.tooltip("Unroot")
            # with ui.button(on_click=dialog.open).props('flat color=white icon=integration_instructions'):
            #     ui.tooltip('Script builder')
            with ui.button(on_click=install_apk_dialog.open).props(
                "flat color=white icon=system_update"
            ):
                ui.tooltip("Install APK")
            with ui.button(on_click=move_file_dialog.open).props(
                "flat color=white icon=file_download"
            ):
                ui.tooltip("Move file")
            # with ui.button(on_click=dialog.open).props('flat color=white icon=pending_actions'):
            #     ui.tooltip('Schedule action')
            with ui.button(on_click=reboot).props("flat color=white icon=restart_alt"):
                ui.tooltip("Reboot")
            # with ui.button(on_click=dialog.open).props('flat color=white icon=shield'):
            #     ui.tooltip('Add proxies')
            # with ui.button(on_click=dialog.open).props('flat color=white icon=schedule'):
            #     ui.tooltip('Set timezone')

        with ui.row().classes("w-full"):

            def get_state(state):
                if state == "offline":
                    return "Offline"
                if state == "bootloader":
                    return "boot"
                if state == "device":
                    return "Online"

            def handle_select_devices(event):
                selected_device_serials = [
                    device["serial"] for device in event.selection
                ]
                manager.select_device(selected_device_serials)

            columns = [
                {
                    "name": "ID",
                    "label": "ID",
                    "field": "id",
                },
                {
                    "name": "Serial",
                    "label": "Serial",
                    "field": "serial",
                },
                {
                    "name": "Model",
                    "label": "Model",
                    "field": "model",
                },
                {
                    "name": "Device",
                    "label": "Device",
                    "field": "name",
                },
                {
                    "name": "Resolution",
                    "label": "Resolution",
                    "field": "resolution",
                },
                # {
                #     "name": "State",
                #     "label": "State",
                #     "field": "state",
                # },
                # {
                #     "name": "Proxy",
                #     "label": "Proxy",
                #     "field": "proxy",
                # },
                {
                    "name": "Timezone",
                    "label": "Timezone",
                    "field": "tz",
                },
            ]
            rows = [
                {
                    "id": i + 1,
                    # "proxy": "none",
                    "tz": "default",
                    "model": manager.adb.device(d).prop.model,
                    "name": manager.adb.device(d).prop.device,
                    "serial": d,
                    "resolution": f"{manager.adb.device(d).window_size()[0]}x{manager.adb.device(d).window_size()[1]}",
                    # "state": get_state(manager.adb.device(d).get_state()),
                }
                for i, d in enumerate(manager.serials_list)
            ]
            device_table = ui.table(
                on_select=handle_select_devices,
                columns=columns,
                rows=rows,
                row_key="serial",
                selection="multiple",
                title=f"Connected device(s): {len(manager.serials_list)}",
            ).style("width:100%")


dashboard()


@ui.page("/devices")
def device_views():
    async def save_settings():
        manager.set_quality(quality_select.value)
        manager.set_size(size_select.value)
        await ui.run_javascript("location.reload()", respond=False)

    def toggle_sync_control():
        manager.toggle_sync_control()
        if manager.sync_control == True:
            sync_control_btn.props(remove="color=white", add="color=primary")
            ui.notify("Sync control on")
            view.master_on(device_views)

        else:
            sync_control_btn.props(remove="color=primary", add="color=white")
            ui.notify("Sync control off")
            view.master_off()

        sync_control_btn.update()

    async def change_focus_device(e):
        if e.value != manager.focused_device:
            manager.focus_device = e.value
            await ui.run_javascript("location.reload()", respond=False)

    def execute_scripts():
        view.execute(select_script.value)
        select_script_dialog.close

    def open_dev_mode():
        dialog.open()
        ui.update(dialog)

    with ui.dialog() as select_script_dialog, ui.card():
        with ui.column():
            select_script = ui.select(manager.scripts, value=manager.scripts[0]).style(
                "width:200px"
            )
            ui.button("Run", on_click=execute_scripts).classes("w-full")

    with ui.dialog() as settings_dialog, ui.card():
        with ui.column().classes("w-full"):
            with ui.row().classes("items-center"):
                ui.icon("app_shortcut").style("font-size:24px")
                ui.label("Quality").style("font-size:24px")
                quality_select = (
                    ui.slider(min=0, max=2)
                    .bind_value(manager, "view_quality")
                    .style("width:100%")
                )
                with ui.row().classes("items-center justify-between").style(
                    "width:100%"
                ):
                    ui.label("Low")
                    ui.label("Medium")
                    ui.label("High")

        with ui.column().classes("w-full my-4"):
            with ui.row().classes("items-center"):
                ui.icon("photo_size_select_large").style("font-size:24px")
                ui.label("Size").style("font-size:24px")
            size_select = (
                ui.slider(min=0, max=2)
                .bind_value(manager, "view_size")
                .style("width:100%")
            )
            with ui.row().classes("items-center justify-between").style("width:100%"):
                ui.label("S")
                ui.label("M")
                ui.label("L")
        ui.button("Save Settings", on_click=save_settings).classes("w-full")

    with ui.column().classes("w-full"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.button(on_click=lambda: ui.open("/")).props(
                "flat color=white icon=arrow_back_ios_new"
            )
            ui.button(on_click=settings_dialog.open).props(
                "flat color=white icon=settings"
            )
        with ui.row().classes("w-full").style("display:flex"):
            with ui.column().bind_visibility_from(manager, "is_focused").style(
                " height:100%; padding-right:16px;"
            ):
                with ui.row():
                    with ui.column():
                        ui.select(
                            manager.serials_list, on_change=change_focus_device
                        ).classes("w-full").bind_visibility_from(
                            manager, "is_focused"
                        ).bind_value_from(
                            manager, "focused_device"
                        )
                        if manager.focused_device != None:
                            view = DeviceView(
                                manager.focused_device,
                                2,
                                1,
                                label=False,
                                control=True,
                                manager=manager,
                            )

                            ############################# developer mode #############################
                            def mouse_handler(e: MouseEventArguments):
                                ii.content += f'<circle cx="{e.image_x}" cy="{e.image_y}" r="10" fill="black"></circle>'
                                ii.content += f'<text x="{e.image_x}" y="{e.image_y+4}" fill="white" font-size="10px" text-anchor="middle">{manager.mouse_click_count}</text>'

                                log.push(
                                    f"x: {int(e.image_x/ratio)} y:{int(e.image_y/ratio)}"
                                )
                                shell_log.push(
                                    f"input tap {int(e.image_x/ratio)} {int(e.image_y/ratio)}"
                                )
                                shell_log.push(f"sleep 1;")
                                manager.gen_script += f"input tap {int(e.image_x/ratio)} {int(e.image_y/ratio)}\n"
                                manager.gen_script += f"sleep 1;\n"
                                manager.mouse_click_count += 1

                            def get_capture():
                                return view.capture(width=360)

                            def copy_script():
                                c.copy(manager.gen_script)
                                ui.notify("Script copied")

                            def update_screenshot():
                                log.clear()
                                shell_log.clear()

                                manager.mouse_click_count = 0
                                ii.source = get_capture()
                                ii.content = ""

                                manager.gen_script = ""

                            with ui.dialog() as dialog, ui.card():
                                with ui.row():
                                    with ui.column():
                                        ratio = view.get_ratio(width=360)
                                        img = get_capture()

                                        with ui.row():
                                            ui.button(on_click=update_screenshot).props(
                                                "icon=refresh"
                                            )
                                        ii = ui.interactive_image(
                                            img,
                                            on_mouse=mouse_handler,
                                            events=["mousedown"],
                                            cross=True,
                                        )
                                    with ui.column():
                                        with ui.column().style("width:120px; "):
                                            with ui.row().classes(
                                                "w-full items-center"
                                            ):
                                                ui.label("Touch").style(
                                                    "font-size:18px"
                                                )
                                                log = (
                                                    ui.log(max_lines=100)
                                                    .classes("w-full")
                                                    .style(
                                                        "font-size:12px;height:100px"
                                                    )
                                                )

                                            with ui.column().style("width:120px"):
                                                with ui.row().classes(
                                                    "w-full items-center justify-between"
                                                ):
                                                    ui.label("Script").style(
                                                        "font-size:18px"
                                                    )
                                                    ui.button(
                                                        on_click=copy_script
                                                    ).props(
                                                        "flat color=white icon=content_copy"
                                                    )
                                                shell_log = (
                                                    ui.log(max_lines=100)
                                                    .classes("w-full")
                                                    .style(
                                                        "font-size:12px;height:480px"
                                                    )
                                                )
                            ############################# developer mode #############################

                        with ui.row().classes("w-full justify-between"):
                            ui.button(on_click=lambda: view.enter_key("BACK")).props(
                                "flat color=white icon=arrow_back_ios_new"
                            )
                            ui.button(on_click=lambda: view.enter_key("HOME")).props(
                                "flat color=white icon=circle"
                            )
                            ui.button(on_click=lambda: view.enter_key("187")).props(
                                "flat color=white icon=crop_din"
                            )

                    with ui.column():
                        # ui.button(on_click=lambda: ui.open('/')).props('flat color=white icon=screenshot').tooltip('Screenshot')
                        # ui.button(on_click=lambda: ui.open('/')).props('flat color=white icon=videocam').tooltip('Record')
                        # ui.button(on_click=lambda: ui.open('/')).props('flat color=white icon=screen_rotation').tooltip('Rotate screen')
                        sync_control_btn = (
                            ui.button(on_click=toggle_sync_control)
                            .props("flat color=white icon=hub")
                            .tooltip("Sync control")
                        )
                        ui.button(on_click=execute_scripts).props(
                            "flat color=white icon=code"
                        ).tooltip("Run script")
                        ui.button(on_click=open_dev_mode).props(
                            "flat color=white icon=developer_mode"
                        ).tooltip("Developer mode")

            with ui.column():
                with ui.row():
                    device_views = [
                        DeviceView(
                            serial,
                            manager.view_quality,
                            manager.view_size,
                            manager=manager,
                        )
                        for serial in manager.serials_list
                    ]


ui.run(
    title="Chicken Farm v0.0.3a",
    favicon="icon.png",
    dark=True,
    native=True,
)

# manager.adb.server_kill()
