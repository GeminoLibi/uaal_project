# uaal_engine/browser_driver.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import logging

class BrowserDriver:
    KEY_MAP = {
        "ctrl": "Control", "alt": "Alt", "shift": "Shift", "win": "Meta",
        "esc": "Escape", "del": "Delete", "ret": "Enter", "ent": "Enter",
        "tab": "Tab", "arr_up": "ArrowUp", "arr_down": "ArrowDown", 
        "arr_left": "ArrowLeft", "arr_right": "ArrowRight"
    }

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.dom_cache = {}

    def connect_to_app(self, url):
        return self.navigate(url)

    def _wait_for_load(self):
        try:
            self.page.wait_for_load_state('networkidle', timeout=5000)
        except PlaywrightTimeoutError:
            logging.warning("Page network did not fully settle.")

    def _get_css_selector(self, element):
        path = []
        for parent in element.parents:
            if parent.name == 'body': break
            if parent.get('id'):
                path.insert(0, f'#{parent.get("id")}')
                break 
            siblings = parent.find_previous_siblings(parent.name)
            selector = f'{parent.name}:nth-of-type({len(siblings) + 1})'
            path.insert(0, selector)
        siblings = element.find_previous_siblings(element.name)
        final_selector = f'{element.name}:nth-of-type({len(siblings) + 1})'
        path.append(final_selector)
        return ' > '.join(path)

    def _get_browser_chrome_actions(self):
        return [
            {"tag": "browser_action", "text": "Go back", "short_selector": "back", "internal_selector": None},
            {"tag": "browser_action", "text": "Go forward", "short_selector": "forward", "internal_selector": None},
            {"tag": "browser_action", "text": "Refresh page", "short_selector": "refresh", "internal_selector": None},
        ]

    def _invalidate_cache(self):
        if self.dom_cache:
            self.dom_cache.clear()
            logging.info("UI action performed. Invalidating DOM cache.")

    def get_ui_dom(self, context_window=4096, apply_limits=True):
        if self.page.url in self.dom_cache:
            return {"dom": self.dom_cache[self.page.url], "captcha_detected": False}

        html_content = self.page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        captcha_detected = False
        iframes = soup.find_all('iframe')
        if iframes:
            for iframe in iframes:
                iframe_src = iframe.get('src', '').lower()
                if 'recaptcha' in iframe_src or 'hcaptcha' in iframe_src:
                    captcha_detected = True
                    break
        
        main_content = soup.find('main') or soup.find('body')
        if not main_content:
            return {"dom": self._get_browser_chrome_actions(), "captcha_detected": captcha_detected}
            
        page_elements = []
        tag_counts = {}
        INTERACTIVE_TAGS = ['a', 'button', 'input', 'textarea', 'select']
        CONTENT_TAGS = ['h1', 'h2', 'h3', 'p', 'li', 'span']
        max_elements = (context_window // 50) if apply_limits else float('inf')

        for element in main_content.find_all(INTERACTIVE_TAGS + CONTENT_TAGS):
            if len(page_elements) >= max_elements: break
            
            element_text = ""
            if element.name == 'input':
                placeholder = element.get('placeholder', '')
                aria_label = element.get('aria-label', '')
                value = element.get('value', '')
                element_text = placeholder or aria_label or value or ""
            else:
                element_text = element.get_text(strip=True)

            if element_text or element.name in ['input', 'textarea']:
                tag_char = element.name[0]
                tag_counts[tag_char] = tag_counts.get(tag_char, 0) + 1
                
                node = {
                    "tag": element.name, 
                    "text": element_text, 
                    "short_selector": f"{tag_char}{tag_counts[tag_char]}",
                    "internal_selector": self._get_css_selector(element)
                }
                page_elements.append(node)
        
        final_dom = self._get_browser_chrome_actions() + page_elements
        self.dom_cache[self.page.url] = final_dom
        
        return {"dom": final_dom, "captcha_detected": captcha_detected}

    def back(self):
        self.page.go_back(); self._wait_for_load(); self._invalidate_cache()

    def forward(self):
        self.page.go_forward(); self._wait_for_load(); self._invalidate_cache()
        
    def refresh(self):
        self.page.reload(); self._wait_for_load(); self._invalidate_cache()
        
    def navigate(self, url):
        self.page.goto(url); self._wait_for_load(); self._invalidate_cache()

    def click(self, selector):
        self.page.click(selector, timeout=5000)
        self._wait_for_load()
        self._invalidate_cache()

    def type_text(self, selector, text):
        self.page.fill(selector, text, timeout=5000)
        self._invalidate_cache()

    def press_key(self, key_combination):
        keys = key_combination.lower().split('+')
        translated_keys = [self.KEY_MAP.get(key, key) for key in keys]
        final_combination = "+".join(translated_keys)
        self.page.keyboard.press(final_combination)
        self._wait_for_load()
        self._invalidate_cache()

    def cleanup(self):
        self.browser.close()
        self.playwright.stop()
        logging.info("Cleaning up Browser driver resources (closing browser).")
        self.browser.close()
        self.playwright.stop()