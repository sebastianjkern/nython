from nython.core.ui.editor import NodeEditor
from nython.core.ui.theming import get_theme, load_font

from inspect import getsourcefile
from os.path import abspath

from pathlib import Path
import os

import dearpygui.dearpygui as dpg

# Redirect all print statements to a log file
log_file = open("app.log", "a")
# sys.stdout = log_file

dpg.create_context()
dpg.configure_app(docking=False, docking_space=False)
dpg.create_viewport(title='Nython Editor', width=1280, height=720, decorated=True)

# Import path for font file
path = os.path.dirname(abspath(getsourcefile(lambda:0))) + "/res/OpenSans-Regular.ttf"
example_path = os.path.dirname(abspath(getsourcefile(lambda:0))) + "/_examples/flow.json"

print("Import font from", path)

load_font(path)

with NodeEditor(example_path) as editor:
    theme = get_theme()
    dpg.bind_theme(theme)

    dpg.set_primary_window(editor.window_tag, True)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()