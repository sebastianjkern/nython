from _runtime.node import NodeData

import dearpygui.dearpygui as dpg

class IMGuiNode:
    def __init__(self, parent: str|int, node: NodeData) -> None:
        self._parent = parent
        self._data: NodeData = node

        self.tag: str | int = node.uuid

        # Tags for UI Elements
        self._title_tag = f"node_title_{self.tag}"
        self._popup_tag = f"rename_popup_{self.tag}"
        self._input_tag = f"rename_input_{self.tag}"

    def show(self):
        # Node selbst: zeige aktuellen Namen und einen Rename-Button
        with dpg.node(parent=self._parent, tag=self.tag):
            # Titel / Name des Node
            dpg.add_text(getattr(self._data, "name", "Node"), tag=self._title_tag)
            # Button öffnet das modale Rename-Fenster
            dpg.add_button(label="Rename", callback=lambda s,a,u=None: dpg.configure_item(self._popup_tag, show=True))

            with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_text(label="Code", width=150, multiline=True)

        # Popup (modal) zum Umbenennen — nur einmal anlegen
        if not dpg.does_item_exist(self._popup_tag):
            with dpg.window(label="Rename Node", modal=True, show=False, tag=self._popup_tag):
                # Vorbelegungswert aus NodeData
                dpg.add_input_text(label="New name", default_value=getattr(self._data, "name", ""), tag=self._input_tag)
                # OK: übernimmt den Namen und schließt das Fenster
                dpg.add_button(label="OK", callback=self._on_rename)
                # Abbrechen: schließt das Fenster ohne Änderung
                dpg.add_button(label="Cancel", callback=lambda s,a,u=None: dpg.configure_item(self._popup_tag, show=False))

    # Callback zum Übernehmen des neuen Namens
    def _on_rename(self, sender, app_data, user_data):
        new_name = dpg.get_value(self._input_tag)
        if new_name:
            # NodeData aktualisieren (wenn Attribut vorhanden)
            try:
                setattr(self._data, "name", new_name)
            except Exception:
                # falls kein Attribut vorhanden, still fail-safe
                pass
            # sichtbaren Titel aktualisieren
            if dpg.does_item_exist(self._title_tag):
                dpg.set_value(self._title_tag, new_name)
        # Popup schließen
        if dpg.does_item_exist(self._popup_tag):
            dpg.configure_item(self._popup_tag, show=False)


