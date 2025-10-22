import dearpygui.dearpygui as dpg

def get_uuid():
    used = set(dpg.get_all_items())

    item = dpg.generate_uuid()
    while item in used:
        item = dpg.generate_uuid()

    return item