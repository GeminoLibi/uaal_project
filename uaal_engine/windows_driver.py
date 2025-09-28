# uaal_engine/windows_driver.py

from pywinauto.application import Application
import time
import logging
import os

class WindowsDriver:
    APP_INFO = {
        "notepad": {"launch": "notepad.exe", "process": "notepad.exe", "title_re": ".*Notepad"},
        "calculator": {"launch": "calc.exe", "process": "CalculatorApp.exe", "title_re": ".*Calculator"},
        "file explorer": {"launch": "explorer.exe", "process": "explorer.exe", "title_re": "File Explorer"},
    }

    KEY_MAP = {
        "ctrl": "^", "alt": "%", "shift": "+", "win": "{LWIN}", "esc": "{ESC}", 
        "del": "{DELETE}", "ins": "{INSERT}", "ret": "{ENTER}", "ent": "{ENTER}",
        "pgup": "{PGUP}", "pgdn": "{PGDN}", "tab": "{TAB}",
        "arr_up": "{UP}", "arr_down": "{DOWN}", "arr_left": "{LEFT}", "arr_right": "{RIGHT}",
    }

    def __init__(self):
        self.app = None
        self.main_window = None
        self.dom_cache = {}

    def connect_to_app(self, name):
        app_info = self.APP_INFO.get(name.lower())
        if not app_info:
            raise ConnectionError(f"'{name}' is not a known application.")
        
        title_re = app_info["title_re"]
        try:
            logging.info(f"Attempting to connect by title pattern: '{title_re}'...")
            self.app = Application(backend="uia").connect(title_re=title_re, timeout=3)
        except Exception:
            try:
                process_name = app_info["process"]
                logging.info(f"Attempting to connect by process name: '{process_name}'...")
                self.app = Application(backend="uia").connect(process_name=process_name, timeout=3)
            except Exception:
                logging.warning(f"App not found. Launching '{name}'...")
                os.system(f'start {app_info["launch"]}')
                self.app = Application(backend="uia").connect(title_re=title_re, timeout=30)

        self.main_window = self.app.window(title_re=title_re)
        self.main_window.wait('ready', timeout=30)
        logging.info("Main window is visible and ready.")
        return self

    def get_ui_dom(self, context_window=4096, apply_limits=True):
        if not self.main_window:
            return {"dom": [], "captcha_detected": False}
        
        window_handle = self.main_window.handle
        if window_handle in self.dom_cache:
            return {"dom": self.dom_cache[window_handle], "captcha_detected": False}
        
        dom_list = []
        tag_counts = {}
        max_elements = (context_window // 50) if apply_limits else float('inf')
        
        logging.info("Scanning all descendant controls...")
        # REVERTED to the simple, reliable .descendants() method
        all_controls = self.main_window.descendants()
        INTERESTING_TYPES = ["Button", "Text", "Edit", "DataGrid", "ListItem", "MenuItem", "ComboBox"]

        for element in all_controls:
            if apply_limits and len(dom_list) >= max_elements: break
            
            auto_id = element.automation_id()
            element_type = element.friendly_class_name()
            
            if auto_id and element_type in INTERESTING_TYPES:
                tag_char = element_type[0].lower()
                tag_counts[tag_char] = tag_counts.get(tag_char, 0) + 1
                
                node = {
                    "tag": element_type,
                    "text": element.window_text(),
                    "short_selector": f"{tag_char}{tag_counts[tag_char]}",
                    "internal_selector": auto_id,
                }
                dom_list.append(node)
        
        final_dom = self._get_window_chrome_actions() + dom_list
        self.dom_cache[window_handle] = final_dom
        
        return {"dom": final_dom, "captcha_detected": False}

    def _get_window_chrome_actions(self):
        return [
            {"tag": "window_action", "text": "Minimize", "short_selector": "minimize", "internal_selector": None},
            {"tag": "window_action", "text": "Maximize", "short_selector": "maximize", "internal_selector": None},
            {"tag": "window_action", "text": "Close", "short_selector": "close", "internal_selector": None},
        ]

    def _invalidate_cache(self):
        if self.main_window and self.main_window.handle:
            self.dom_cache.pop(self.main_window.handle, None)
            logging.info("UI action performed. Invalidating DOM cache.")

    def click(self, auto_id):
        self.main_window.child_window(auto_id=auto_id).click_input()
        self._invalidate_cache()

    def type_text(self, auto_id, text):
        self.main_window.child_window(auto_id=auto_id).type_keys(text, with_spaces=True)
        self._invalidate_cache()
    
    def type_global(self, text):
        self.main_window.type_keys(text, with_spaces=True)
        self._invalidate_cache()

    def press_key(self, key_combination):
        keys = key_combination.lower().split('+')
        output = ""
        for key in keys:
            if key in ['ctrl', 'alt', 'shift']:
                output += self.KEY_MAP.get(key)
            else:
                translated = self.KEY_MAP.get(key, key)
                if len(translated) > 1 and not translated.startswith('{'):
                    output += f"{{{translated.upper()}}}"
                else:
                    output += translated
        logging.info(f"Pressing key combination: '{key_combination}' -> '{output}'")
        self.main_window.type_keys(output)
        self._invalidate_cache()

    def minimize(self):
        self.main_window.minimize(); self._invalidate_cache()

    def maximize(self):
        self.main_window.maximize(); self._invalidate_cache()

    def close(self):
        self.main_window.close(); self.app = None; self.main_window = None
        
    def cleanup(self):
        self.app = None; self.main_window = None