import textwrap

from .browser_handler import BrowserHandler
from .decorators import *
from .constants import *

class BrowserDebugHandler(BrowserHandler):
    @document_handler(Priority.LOWEST)
    def unrecogniced_page_handler(self):
        actions = []

        while True:
            print(textwrap.dedent("""Actions : 
                                     0 - Exit
                                     1 - Reload (decrementing the scoreboard entry for the last handler)
                                     2 - Reload
                                     3 - Decrement scoreboard entry for the last handler
                                     4 - Wipe scoreboard
                                     5 - Dump handler call stack and scoreboard
                                     6 - Abort
                                     """))

            action = input('Action : ').strip()

            if action == '0':
                break

            if action in ('1', '3'):
                proper_call_stack = [handler for handler in self.handler_call_stack if handler != 'unrecogniced_page_handler']

                if len(proper_call_stack):
                    handler_invocation_count = self.scoreboard.get(proper_call_stack[0], 0)

                    if handler_invocation_count > 0:
                        handler_invocation_count -= 1
                    else:
                        handler_invocation_count = 0

                    self.scoreboard[proper_call_stack[0]] = handler_invocation_count

                if action == '1':
                    action = '2'

            if action == '2':
                new_module = reload(sys.modules.get(self.__module__))
                new_class = getattr(new_module, self.__class__.__name__)
                new_instance = new_class(self.backend, self.context)

                self.migrate(new_instance) # this raises a migration request exception
            
            if action == '4':
                self.scoreboard = {}

            if action == '5':
                print("HANDLER CALL STACK\n")

                for entry in self.handler_call_stack:
                    print(entry)

                print()

                print("SCOREBOARD\n")

                for entry in self.handler_call_stack:
                    print('%s %s' % (entry, self.scoreboard.get(entry, 0)))

                print()

            if action == '6':
                self.stop_dispatching()

                return True

    @exception_handler(Priority.LOW, [KeyboardInterrupt], invocation_limit=1)
    def user_abort_handler(self, ex):
        print("KeyboardInterrupt handler")

        self.stop_dispatching()

        return True

    @exception_handler(Priority.LOWEST, [Exception])
    def generic_exception_handler(self, ex):
        print()
        print(traceback.format_exc())
        print()

        self.unrecogniced_page_handler()

        return True

