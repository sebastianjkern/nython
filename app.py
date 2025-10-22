from core.ui.editor import NodeEditor

from core.ui.theming import get_theme, load_font

import dearpygui.dearpygui as dpg

# Redirect all print statements to a log file
log_file = open("app.log", "a")
# sys.stdout = log_file

# Start DearPyGUI
dpg.create_context()
dpg.configure_app(docking=False, docking_space=False)
dpg.create_viewport(title='Nython Editor', width=1280, height=720, decorated=True)

load_font()

with NodeEditor() as editor:
    theme = get_theme()
    dpg.bind_theme(theme)

    dpg.set_primary_window(editor._center_window, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()