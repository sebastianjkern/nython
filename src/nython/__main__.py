from nython.core.ui.editor import NodeEditor
from nython.core.ui.theming import get_theme, load_font

from pathlib import Path

import dearpygui.dearpygui as dpg

# Redirect all print statements to a log file
log_file = open("app.log", "a")
# sys.stdout = log_file

dpg.create_context()
dpg.configure_app(docking=False, docking_space=False)
dpg.create_viewport(title='Nython Editor', width=1280, height=720, decorated=True)

path = Path(__file__).parent / "/res/OpenSans-Regular.ttf"
print("Import font from", path)

load_font(path)

with NodeEditor() as editor:
    theme = get_theme()
    dpg.bind_theme(theme)

    dpg.set_primary_window(editor.window_tag, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()