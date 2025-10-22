import dearpygui.dearpygui as dpg

from pathlib import Path

def load_font():
    # add a font registry
    with dpg.font_registry():
        path = Path(__file__).parent / "/res/OpenSans-Regular.ttf"

        # first argument ids the path to the .ttf or .otf file
        default_font = dpg.add_font(path.absolute().as_uri(), 18)
        dpg.bind_font(default_font)

def get_theme(accent=(99, 179, 237, 255)):
    """
    Returns a DearPyGui theme id with a modern dark appearance and a soft accent color.
    Call dpg.bind_theme(theme_id) to apply globally or dpg.bind_item_theme(item, theme_id) for a specific item.
    """
    dark0 = (18, 20, 23, 255)      # main window bg
    dark1 = (28, 30, 34, 255)      # panel bg
    dark2 = (40, 44, 52, 255)      # frames
    mid   = (64, 72, 84, 255)      # borders / muted elements
    text  = (230, 233, 237, 255)   # primary text
    sub   = (160, 170, 180, 255)   # secondary text / placeholders
    accent_hover = tuple(min(255, int(accent[i] * 1.12)) if i<3 else accent[3] for i in range(4))

    with dpg.theme() as theme_id:
        with dpg.theme_component(dpg.mvAll):
            # Core colors
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, dark0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Border, mid, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, dark2, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, dark2, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, mid, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, dark2, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Header, dark2, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Tab, dark1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, text, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, sub, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PlotLines, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PlotLinesHovered, accent_hover, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (120, 120, 120, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, mid, category=dpg.mvThemeCat_Core)

            # Styles: rounding, padding, spacing, border sizes
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10, category=dpg.mvThemeCat_Core)  # (x,y)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6, category=dpg.mvThemeCat_Core)
            # dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)

            # Optional: subtle checkbox/radio contrast
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, accent, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, accent, category=dpg.mvThemeCat_Core)

    return theme_id


if __name__ == "__main__":
    import dearpygui.dearpygui as dpg

    dpg.create_context()

    load_font()

    with dpg.window(label="Tutorial", pos=(20, 50), width=275, height=225) as win1:
        t1 = dpg.add_input_text(default_value="some text")
        t2 = dpg.add_input_text(default_value="some text")
        with dpg.child_window(height=100):
            t3 = dpg.add_input_text(default_value="some text")
            dpg.add_input_int()
        dpg.add_input_text(default_value="some text")

    with dpg.window(label="Tutorial", pos=(320, 50), width=275, height=225) as win2:
        dpg.add_input_text(default_value="some text")
        dpg.add_input_int()

    global_theme = get_theme()
    dpg.bind_theme(global_theme)

    dpg.show_style_editor()

    dpg.create_viewport(title='Custom Title', width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()