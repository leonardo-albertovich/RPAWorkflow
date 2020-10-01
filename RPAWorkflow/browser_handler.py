from .base_handler import BaseHandler


class BrowserHandler(BaseHandler):
    @property 
    def url(self):
        return self.backend.current_url

    @property 
    def contents(self):
        return self.backend.page_source

    @property 
    def session_id(self):
        return self.backend.session_id

    def screenshot(self):
        return self.backend.get_screenshot_as_png()
