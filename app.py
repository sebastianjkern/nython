from ui.editor import NodeEditor

from ui.theming import get_theme, load_font

from _runtime.events import RuntimeEvents
from _runtime.node import NodeData, Connector, ConnectorType

import dearpygui.dearpygui as dpg
import time

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

editor = NodeEditor(center_window)
with dpg.window(label="Nython Editor", tag=center_window, no_collapse=True, no_close=True, no_title_bar=True, no_move=True):
    editor.startup()

# Create Node Pop Up
with dpg.window(label="Create Node", modal=True, show=False, tag=create_node_popup, no_resize=True, no_collapse=True, no_move=True):
    dpg.add_input_text(tag=create_node_input, default_value="Node 1")

    def _create_node_cb(sender, app_data):
        name = dpg.get_value(create_node_input)

        input_tag = "input_" + str(dpg.generate_uuid())
        output_tag = "output_" + str(dpg.generate_uuid())

        node_tag = "node_" + str(dpg.generate_uuid())
        data = NodeData(node_tag, "")

        in_conn = Connector(input_tag, data)
        in_conn.type = ConnectorType.INPUT

        out_conn = Connector(output_tag, data)
        out_conn.type = ConnectorType.OUTPUT

        data.inputs = [in_conn]
        data.outputs = [out_conn]

        # Request runtime to create the node via command event; GUI will be created from the runtime event
        try:
            # send serialized node so runtime can recreate it exactly
            editor._flow.events.emit_sync(RuntimeEvents.CREATE_NODE, {"node": data.to_dict(), "label": name})
        except Exception:
            pass

        # Close the Popup in case the node was created sucessfully
        dpg.configure_item(create_node_popup, show=False)

    # Close popup immediately; the GUI node will be created when the runtime emits the event
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
        # help static type checkers: assert values are not None
        assert main_w is not None and main_h is not None and modal_w is not None and modal_h is not None and main_pos is not None

        rel_x = int(main_w / 2 - modal_w / 2)
        rel_y = int(main_h / 2 - modal_h / 2)
        abs_x = int(main_pos[0] + rel_x)
        abs_y = int(main_pos[1] + rel_y)
        # setze die absolute Position im Koordinatensystem des Viewports
        dpg.set_item_pos(create_node_popup, [rel_x, rel_y])
        
        dpg.focus_item(create_node_input)

    # Delete selected nodes
    if app_data == dpg.mvKey_Delete:
        nodes = dpg.get_selected_nodes(editor._editor_tag) or []

        # Dann die selektierten Nodes löschen
        for node in nodes:
            try:
                # Prefer removing via runtime Flow so GUI and runtime stay in sync.
                lut = getattr(editor, "_node_lut", None)
                if lut and str(node) in lut:
                    # ask runtime to remove; runtime will emit NODE_REMOVED -> GUI updates
                    try:
                        editor._flow.events.emit_sync(RuntimeEvents.REM_NODE, {"uuid": str(node)})
                    except Exception:
                        # fallback: delete GUI item directly if runtime path fails
                        try:
                            dpg.delete_item(node)
                        except Exception:
                            pass
                else:
                    # no runtime mapping available, delete GUI item
                    try:
                        dpg.delete_item(node)
                    except Exception:
                        pass
            except Exception:
                # keep loop robust but log in future
                pass

    if app_data == dpg.mvKey_S and dpg.is_key_down(dpg.mvKey_LControl):
        try:
            editor._flow.events.emit_sync(RuntimeEvents.SAVE, None)
        except Exception:
            print("Could not be saved")

with dpg.handler_registry() as fff:
    dpg.add_key_press_handler(callback=key_handler)

theme = get_theme()
dpg.bind_theme(theme)

# dpg.show_style_editor()

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window(center_window, True)

try:
    # Main loop: render frames and poll runtime events in main thread
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        try:
            editor._flow.events.poll()
        except Exception:
            # avoid stopping the loop on poll errors; log if needed
            pass
        # small sleep to be cooperative; adjust as needed
        time.sleep(0.001)
finally:
    # ensure background worker (if any) is stopped and context torn down
    try:
        editor._flow.events.stop()
    except Exception:
        pass
    dpg.destroy_context()
    log_file.close()