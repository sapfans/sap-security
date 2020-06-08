import pythoncom
import win32com.client
pythoncom.CoInitialize()

SAP_GUI_APPLICATION = "SAPGUI"
SAP_LOGON = "SAP Logon"
GUI_TYPES_WITH_TEXT_PROPERTY = ("GuiTextField",
                                "GuiOkCodeField",
                                "GuiCTextField",
                                "GuiLabel",
                                "GuiStatusbar",
                                "GuiTitlebar")

GUI_TYPES_WITH_PRESS_METHOD = ("GuiButton",
                               )
GUI_TYPES_WITH_SELECT_METHOD = ("GuiMenu",
                                "GuiTab",
                                "GuiRadioButton")
GUI_TYPES_WITH_SELECTED_PROPERTY = (
    "GuiCheckBox")
GUI_TYPES_WITH_SENDVKEY_METHOD = ("GuiMainWindow",
                                  "GuiModalWindow"
                                  )
GUI_GRID_TYPES = ("GuiShell",)
GUI_GRID_SUBTYPES = ("GridView", )
GUI_SCROLL_TYPES = ("GuiUserArea", )

GUI_MAIN_WINDOW = "wnd[0]"
GUI_MAIN_USER_AREA = "wnd[0]/usr"
GUI_CHILD_WINDOW1 = "wnd[1]"
GUI_CHILD_USERAREA1 = "wnd[1]/usr"
STATUS_BAR = "{window}/sbar"
MENU = "{window}/mbar"

TRANSACTION_TEXT_FIELD = "{window}/tbar[0]/okcd"
TRANSACTION_PREFIX = "/N"

GUI_VKEYS = {
    "Enter": 0,
    "F8": 8,
    "Shift+F4": 16,
    "Ctrl+F7": 31,
    "Ctrl+Shift+F9": 45
}
TRY_TEXT_TYPES = ['ctxt', 'txt']


class SAPLogon:
    @staticmethod
    def get_sap_session():
        sap_error = ""
        pythoncom.CoInitialize()
        try:
            sap_gui = win32com.client.GetObject(SAP_GUI_APPLICATION)
            if not isinstance(sap_gui, win32com.client.CDispatch):
                sap_gui = None
        except pythoncom.com_error as error:
            sap_gui = None
            hr, msg, exc, arg = error.args
            sap_error = "COM: {0} ({1})".format(msg, hr)
        finally:
            if sap_gui is None:
                msg_list = list()
                msg_list.append("Application {0} not running.".format(SAP_LOGON))
                if sap_error:
                    msg_list.append(sap_error)
                raise RuntimeError(" ".join(msg_list))

        try:
            sap_application = sap_gui.GetScriptingEngine
            if not isinstance(sap_application, win32com.client.CDispatch):
                sap_application = None

            if sap_application is not None:
                sap_connection = sap_application.Children(0)
                if not isinstance(sap_connection, win32com.client.CDispatch):
                    sap_connection = None
        except pythoncom.com_error:
            sap_application = None
            sap_connection = None
            hr, msg, exc, arg = error.args
            sap_error = "COM: {0} ({1})".format(msg, hr)
        finally:
            if sap_application is None or sap_connection is None:
                msg_list = list()
                msg_list.append("Active connection(s) to SAP server not found in {0} application".format(SAP_LOGON))
                if sap_error:
                    msg_list.append(sap_error)
                raise RuntimeError(" ".join(msg_list))

        try:
            sap_session = sap_connection.Children(0)
            if not isinstance(sap_session, win32com.client.CDispatch):
                sap_session = None
        except pythoncom.com_error:
            sap_session = None
            hr, msg, exc, arg = error.args
            sap_error = "COM: {0} ({1})".format(msg, hr)
        finally:
            if sap_session is None:
                msg_list = list()
                msg_list.append("SAP GUI scripting disabled. Please set parameter sapgui/user_scripting to TRUE")
                if sap_error:
                    msg_list.append(sap_error)
                raise RuntimeError(" ".join(msg_list))

        return sap_session

    @staticmethod
    def get_sap_session_with_info():
        sap_session = SAPLogon.get_sap_session()
        outdict = dict()
        try:
            info = sap_session.Info
            outdict["sid"] = info.SystemName
            outdict["client"] = info.Client
            outdict["user"] = info.User
            outdict["app_server"] = info.applicationServer
        except pythoncom.com_error as error:
            hr, msg, exc, arg = error.args
            sap_error = "COM: {0} ({1})".format(msg, hr)
            msg_list = list()
            msg_list.append("Attached to not authorized session")
            if sap_error:
                msg_list.append(sap_error)
            raise RuntimeError(" ".join(msg_list))

        else:
            if outdict["user"]:
                return sap_session, outdict
            else:
                msg_list = list()
                msg_list.append("Attached to not authorized session. SID: {0}".format(outdict["sid"]))
                raise RuntimeError(" ".join(msg_list))

    @staticmethod
    def set_text(sap_session, text_element_id, text):
        text_element = SAPLogon.__get_element(sap_session, text_element_id)

        if text_element.type in GUI_TYPES_WITH_TEXT_PROPERTY:
            text_element.text = str(text)
        else:
            msg = "Text not be set for GUI element '{0}' (wrong GUI element type '{1}')".format(text_element_id,
                                                                                                text_element.type)
            raise TypeError(msg)

    @staticmethod
    def get_text(sap_session, text_element_id):
        text_element = SAPLogon.__get_element(sap_session, text_element_id)

        if text_element.type in GUI_TYPES_WITH_TEXT_PROPERTY:
            return text_element.text
        else:
            msg = "GUI element '{0}' has no 'text' property(wrong GUI element type '{1}')".format(text_element_id,
                                                                                                  text_element.type)
            raise TypeError(msg)

    @staticmethod
    def press_button(sap_session, button_element_id):
        button_element = SAPLogon.__get_element(sap_session, button_element_id)

        if button_element.type in GUI_TYPES_WITH_PRESS_METHOD:
            button_element.press()
        else:
            msg = "GUI element '{0}' has no press() method (wrong GUI element type '{1}')".format(button_element_id,
                                                                                                  button_element.type)
            raise TypeError(msg)

    @staticmethod
    def __get_element(sap_session, element_id):
        try:
            element = sap_session.findById(element_id)

        except pythoncom.com_error:
            msg = "GUI element with id '{0}' not found".format(element_id)
            raise AttributeError(msg)

        except AttributeError:
            msg = "Wrong sap session object received"
            raise AttributeError(msg)
        else:
            return element

    @staticmethod
    def set_checkbox(sap_session, element_id):
        selected_element = SAPLogon.__get_element(sap_session, element_id)

        if selected_element.type in GUI_TYPES_WITH_SELECTED_PROPERTY:
            selected_element.selected = True
        else:
            msg = "GUI element '{0}' has no select() method (wrong GIU element type '{1}')".format(
                element_id,
                selected_element.type)
            raise TypeError(msg)

    @staticmethod
    def select_element(sap_session, element_id):
        select_element = SAPLogon.__get_element(sap_session, element_id)

        if select_element.type in GUI_TYPES_WITH_SELECT_METHOD:
            select_element.select()
        else:
            msg = "GUI element '{0}' has no select() method (wrong GUI element type '{1}')".format(element_id,
                                                                                                   select_element.type)
            raise TypeError(msg)

    @staticmethod
    def press_keyboard_keys(sap_session, keys, window_id=GUI_MAIN_WINDOW):
        if keys in GUI_VKEYS.keys():
            SAPLogon.__send_vkey(sap_session, GUI_VKEYS[keys], window_id)
        else:
            msg = "Wrong vkey '{0}' received. Supported only {1}".format(keys, ", ".join(GUI_VKEYS.keys()))
            raise ValueError(msg)

    @staticmethod
    def __send_vkey(sap_session, vkey, window_id=GUI_MAIN_WINDOW):
        window_element = SAPLogon.__get_element(sap_session, window_id)

        if window_element.type in GUI_TYPES_WITH_SENDVKEY_METHOD:
            if vkey in GUI_VKEYS.values():
                window_element.sendVKey(vkey)
        else:
            msg = "GUI Element '{0}' has no sendvkey() method (wrong GUI element type '{1}')".format(
                window_id,
                window_element.type)
            raise TypeError(msg)

    @staticmethod
    def get_status_message(sap_session, window_id=GUI_MAIN_WINDOW):
        statusbar = SAPLogon.__get_element(sap_session, STATUS_BAR.format(window=window_id))

        if statusbar.text:
            return statusbar.MessageType, statusbar.MessageNumber, statusbar.text

    @staticmethod
    def call_transaction(sap_session, transaction, window_id=GUI_MAIN_WINDOW):
        transaction = TRANSACTION_PREFIX + transaction
        SAPLogon.set_text(sap_session, TRANSACTION_TEXT_FIELD.format(window=window_id), transaction)
        SAPLogon.press_keyboard_keys(sap_session, "Enter")

    @staticmethod
    def try_to_set_text(sap_session, element_template, text):
        for element_type in TRY_TEXT_TYPES:
            try:
                SAPLogon.set_text(sap_session, element_template.format(type=element_type), text)
            except AttributeError:
                pass
            else:
                return

        msg = "GUI elements with mask '{0}' not found".format(element_template)
        raise AttributeError(msg)

    @staticmethod
    def get_grid_rows_number(sap_session, grid_id):
        grid_element = SAPLogon.__get_element(sap_session, grid_id)

        if grid_element.type in GUI_GRID_TYPES and \
                grid_element.subtype in GUI_GRID_SUBTYPES:
            return grid_element.RowCount
        else:
            msg = "GIU element '{0}' has no rowcount() method (wrong GUI element type '{1}')".format(
                grid_id,
                grid_element.type)
            raise TypeError(msg)

    @staticmethod
    def get_value_from_grid(sap_session, grid_id, row, column):
        grid_element = SAPLogon.__get_element(sap_session, grid_id)

        if grid_element.type in GUI_GRID_TYPES and \
                grid_element.subtype in GUI_GRID_SUBTYPES:
            return grid_element.GetCellValue(row, grid_element.ColumnOrder(column))
        else:
            msg = "GUI element '{0}' has no rowcount() method (wrong GUI element type '{1}')".format(grid_id,
                                                                                                     grid_element.type)
            raise TypeError(msg)

    @staticmethod
    def get_scroll_position(sap_session, area_id=GUI_MAIN_USER_AREA):
        scroll_element = SAPLogon.__get_element(sap_session, area_id)
        if scroll_element.type in GUI_SCROLL_TYPES:
            return scroll_element.verticalScrollbar.position
        else:
            msg = "GUI element '{0}' has no verticalScrollbar object (wrong GUI element type '{1}')".format(
                area_id,
                scroll_element.type)
            raise TypeError(msg)

    @staticmethod
    def get_max_scroll_position(sap_session, area_id=GUI_MAIN_USER_AREA):
        scroll_element = SAPLogon.__get_element(sap_session, area_id)
        if scroll_element.type in GUI_SCROLL_TYPES:
            return scroll_element.verticalScrollbar.Maximum
        else:
            msg = "GUI element '{0}' has no verticalScrollbar object (wrong GUI element type '{1}')".format(
                area_id,
                scroll_element.type)
            raise TypeError(msg)

    @staticmethod
    def set_scroll_position(sap_session, position, area_id=GUI_MAIN_USER_AREA):
        scroll_element = SAPLogon.__get_element(sap_session, area_id)
        if scroll_element.type in GUI_SCROLL_TYPES:
            if not type(position) is int:
                msg = "Wrong position '{0}' to scroll received".format(position)
                raise TypeError(msg)
            scroll_element.verticalScrollbar.position = position
        else:
            msg = "GUI element '{0}' has no verticalScrollbar object (wrong GUI element type '{1}')".format(
                area_id,
                scroll_element.type)
            raise TypeError(msg)

    @staticmethod
    def __find_menu_element(menu, menu_names):
        if menu.text in menu_names:
            return menu.id

        for child_menu in menu.Children:
            found_element_id = SAPLogon.__find_menu_element(child_menu, menu_names)
            if found_element_id:
                return found_element_id

    @staticmethod
    def call_menu(sap_session, menu_names, window_id=GUI_MAIN_WINDOW):
        if not len(menu_names):
            msg = "Empty Menu names list received"
            raise ValueError(msg)
        main_menu = SAPLogon.__get_element(sap_session, MENU.format(window=window_id))
        menu_element_id = SAPLogon.__find_menu_element(main_menu, menu_names)

        if not menu_element_id:
            msg = "Menu GUI element not found by text {text}.".format(text=", ".join(menu_names))
            raise ValueError(msg)
        SAPLogon.select_element(sap_session, menu_element_id)

    @staticmethod
    def iter_elements_by_template(sap_session, root_element_id, id_template, start_index, max_index=50):
        root_area = SAPLogon.__get_element(sap_session, root_element_id)

        for index in range(start_index, max_index):
            try:
                element = SAPLogon.__get_element(root_area, id_template.format(index))
                yield index, element
            except AttributeError:
                break
