from .base_handler import BaseHandler


class AndroidHandler(BaseHandler):
    @property 
    def url(self):
        return ''

    @property 
    def contents(self):
        return self.backend.uidump()

    @property 
    def session_id(self):
        return ''

    def screenshot(self):
        return None
