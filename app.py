from ui.editor import NodeEditor

from ui.theming import get_theme, load_font

import sys

import dearpygui.dearpygui as dpg

# Redirect all print statements to a log file
log_file = open("app.log", "a")
# sys.stdout = log_file

# Start DearPyGUI
dpg.create_context()
dpg.configure_app(docking=False, docking_space=False)
dpg.create_viewport(title='Nython Editor', width=800, height=600, decorated=True)

load_font()

center_window = dpg.generate_uuid()
settings_window = dpg.generate_uuid()
node_editor = "editor_" + str(dpg.generate_uuid())

create_node_popup = dpg.generate_uuid()
create_node_input = dpg.generate_uuid()

def print_me(sender):
    print(f"Menu Item: {sender}")

editor = NodeEditor(center_window)
# flow.load_flow()
with dpg.window(label="Nython Editor", tag=center_window, no_collapse=True, no_close=True, no_title_bar=True, no_move=True):
    editor.startup()

    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", callback=print_me)
            dpg.add_menu_item(label="Save As", callback=print_me)

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
                dpg.add_menu_item(label="Setting 2", callback=print_me)

                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
                    dpg.add_menu_item(label="Setting 2", callback=print_me)

        dpg.add_menu_item(label="Help", callback=print_me)
        
        with dpg.menu(label="Widget Items"):
            dpg.add_checkbox(label="Pick Me", callback=print_me)
            dpg.add_button(label="Press Me", callback=print_me)
            dpg.add_color_picker(label="Color Me", callback=print_me)

# Create Node Pop Up
with dpg.window(label="Create Node", modal=True, show=False, tag=create_node_popup, no_resize=True, no_collapse=True, no_move=True):
    dpg.add_text("Name des neuen Nodes:")
    dpg.add_input_text(tag=create_node_input, default_value="Node 1")

    def _create_node_cb(sender, app_data):
        name = dpg.get_value(create_node_input)
        editor.create_node(name)
        dpg.configure_item(create_node_popup, show=False)

    with dpg.group(horizontal=True):
        dpg.add_button(label="Create", callback=_create_node_cb)
        dpg.add_button(label="Cancel", callback=lambda s,a: dpg.configure_item(create_node_popup, show=False))

def key_handler(sender, app_data):
    # Provide a functionality for adding a new node
    if app_data == dpg.mvKey_N and dpg.is_key_down(dpg.mvKey_LShift):
        # Item-Größen und -Positionen im Bezug auf die Viewport/Applikation abfragen
        dpg.configure_item(create_node_popup, show=True)

        main_w = dpg.get_viewport_width()
        main_h = dpg.get_viewport_height()
        modal_w = dpg.get_item_width(create_node_popup)
        modal_h = dpg.get_item_height(create_node_popup)
        main_pos = dpg.get_viewport_pos()  # absolute Position des Viewports

        if any(v is None for v in (main_w, main_h, modal_w, modal_h, main_pos)):
            return

        # Berechne Position, damit das Modal im Zentrum des Hauptfensters sitzt
        rel_x = int(main_w / 2 - modal_w / 2)
        rel_y = int(main_h / 2 - modal_h / 2)
        abs_x = int(main_pos[0] + rel_x)
        abs_y = int(main_pos[1] + rel_y)
        # setze die absolute Position im Koordinatensystem des Viewports
        dpg.set_item_pos(create_node_popup, [rel_x, rel_y])
        
        dpg.focus_item(create_node_input)

    # Delete selected nodes
    if app_data == dpg.mvKey_Delete:
        print("Received node delete command")
        
        nodes = dpg.get_selected_nodes(editor._editor_tag) or []

        # Dann die selektierten Nodes löschen
        for node in nodes:
            try:
                dpg.delete_item(node)
            except Exception:
                pass

    if app_data == dpg.mvKey_S and dpg.is_key_down(dpg.mvKey_LControl):
        print("Saving")
        editor._flow.save()

with dpg.handler_registry() as fff:
    dpg.add_key_press_handler(callback=key_handler)

theme = get_theme()
dpg.bind_theme(theme)

# dpg.show_style_editor()

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window(center_window, True)

dpg.start_dearpygui()
dpg.destroy_context()