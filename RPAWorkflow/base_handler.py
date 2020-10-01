import inspect
import logging
import sys
import types
import traceback

from operator  import attrgetter

from .actions import *
from .constants import *
from .exceptions import *
from .modifiers import *


class BaseHandler(object):
    @property 
    def url(self):
        raise Exception("Unimplemented property")

    @property 
    def contents(self):
        raise Exception("Unimplemented property")

    @property 
    def session_id(self):
        raise Exception("Unimplemented property")

    def screenshot(self):
        raise Exception("Unimplemented method")

    def __getattribute__(self, attr):
        if attr != 'child':
            child = object.__getattribute__(self, 'child')

            if child:
                return child.__class__.__getattribute__(child, attr)

        return object.__getattribute__(self, attr)

    def migrate(self, child):
        child.status             = self.status
        child.status_            = self.status_
        child.backend            = self.backend
        child.context            = self.context
        child.notifications      = self.notifications
        child.page_dumps         = self.page_dumps
        child.handler_call_stack = self.handler_call_stack

        for entry in self.scoreboard.keys():
            child.scoreboard[entry] = self.scoreboard[entry]

        self.child               = child
        self.status              = None
        self.status_             = None
        self.backend             = None
        self.context             = None
        self.scoreboard          = None
        self.notifications       = None
        self.page_dumps          = None

        raise WorkflowHandlerMigration(child)

    def __init__(self, backend, context, log_level=logging.DEBUG):
        self.child              = None
        self.status             = WORKFLOW_WORKING
        self.status_            = {}
        self.backend            = backend
        self.context            = context
        self.exception_handlers = []
        self.document_handlers  = []
        self.scoreboard         = {}
        self.notifications      = {}
        self.page_dumps         = []
        self.handler_call_stack = []
        self.log_level          = log_level
        self.logger             = logging.getLogger('RPAWorkflow')

        self.logger.setLevel(self.log_level)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(self.log_level)

        self.logger.addHandler(self.stream_handler)

        for method in inspect.getmembers(self, predicate=inspect.ismethod):            
            if 'rulesets' in map(lambda m: m[0], inspect.getmembers(method[1])):
                handler = method[1]

                self.document_handlers.append(handler)

                self.scoreboard[handler.__name__] = 0

                self.logger.debug('Registering document handler %s : %s' % (handler.__name__, ''))

            elif 'exceptions' in map(lambda m: m[0], inspect.getmembers(method[1])):
                handler = method[1]

                self.exception_handlers.append(handler)

                self.scoreboard[handler.__name__] = 0

                self.logger.debug('Registering exception handler %s : %s' % (handler.__name__, ''))

        self.document_handlers = sorted(self.document_handlers, key=attrgetter('priority'))
        self.exception_handlers = sorted(self.exception_handlers, key=attrgetter('priority'))

    def decrement_scoreboard_entry(self, entry_identifier):
        self.scoreboard[entry_identifier] -= 1

    def reset_scoreboard_entry(self, entry_identifier):
        self.scoreboard[entry_identifier] = 0

    def set_dependency_status(self, dependency_name, dependency_status):
        if dependency_status:
            self.status_[dependency_name] = True
        else:
            del self.status_[dependency_name]

    def get_dependency_status(self, dependency_name):
        return self.status_.get(dependency_name.lstrip('!')) or False

    def set_notification(self, notification_name):
        self.notifications[notification_name] = True

    def unset_notification(self, notification_name):
        del self.notifications[notification_name]

    def stop_dispatching(self):
        self.status = WORKFLOW_FAILURE

    def dispatch_while_working(self, *args, **kwargs):
        while self.status == WORKFLOW_WORKING:
            try:
                self.logger.debug('DISPATCHING')
                self.dispatch(*args, **kwargs)

            except WorkflowHandlerMigration as ex:
                self.logger.debug('MIGRATED')
                raise

            except WorkflowFailure as ex:
                self.stop_dispatching()

            except:
                ex = sys.exc_info()
                eh = False

                for handler in self.exception_handlers:
                    if self.scoreboard[handler.__name__] < handler.invocation_limit:
                        if any([issubclass(ex[0], ex_c) for ex_c in handler.exceptions]):
                            self.scoreboard[handler.__name__] += 1

                            result = handler(ex[1])

                            if result:
                                eh = True
                                break

                if not eh:
                    raise

    def dispatch(self, *args, **kwargs):
        results = []
        ruleset_matches = 0

        for handler in self.document_handlers:
            if self.scoreboard[handler.__name__] < handler.invocation_limit:
                dependency_matches = 0

                for dependency in handler.dependencies:
                    dependency_status = self.get_dependency_status(dependency)

                    if dependency.startswith('!'):
                        dependency_status = not dependency_status

                    if dependency_status:
                        dependency_matches += 1

                if dependency_matches == len(handler.dependencies):
                    ruleset_matched = False
                    terminator_ruleset = False

                    if not handler.rulesets:
                        ruleset_matched = True
                        ruleset_matches = 1

                    else:
                        for ruleset in handler.rulesets:
                            if ruleset_matched:
                                break

                            dependency_matches = 0

                            for dependency in ruleset.dependencies:
                                dependency_status = self.get_dependency_status(dependency)

                                if dependency.startswith('!'):
                                    dependency_status = not dependency_status

                                if dependency_status:
                                    dependency_matches += 1

                            if dependency_matches == len(ruleset.dependencies):
                                ruleset_result = True

                                for rule in ruleset.rules:
                                    rule_text = rule.rule_text
                                    body_text = self.contents
                                    url_text  = self.url

                                    if ContextKey in rule.rule_modifiers:
                                        rule_text = self.context[rule_text]

                                    if CaseLess in rule.rule_modifiers:
                                        rule_text = rule_text.lower()
                                        body_text = body_text.lower()
                                        url_text  = url_text.lower()

                                    if Body in rule.rule_modifiers:
                                        if Regex in rule.rule_modifiers:
                                            rule_result = regex_test(rule_text, body_text)

                                        elif PlainText in rule.rule_modifiers:
                                            rule_result = rule_text in body_text

                                    elif Url in rule.rule_modifiers:
                                        if Regex in rule.rule_modifiers:
                                            rule_result = regex_test(rule_text, url_text)

                                        elif PlainText in rule.rule_modifiers:
                                            rule_result = rule_text in url_text

                                    if Inverse in rule.rule_modifiers:
                                        rule_result = not rule_result

                                    if Mandatory in rule.rule_modifiers and not rule_result:
                                        ruleset_result = False
                                        break

                                if ruleset_result:
                                    ruleset_matches += 1
                                    ruleset_matched = True

                                    if ContinueEvaluating not in ruleset.modifiers:
                                        terminator_ruleset = True

                    if ruleset_matched:
                        self.scoreboard[handler.__name__] += 1

                        self.handler_call_stack.insert(0, handler.__name__)
                        self.handler_call_stack = self.handler_call_stack[:HANDLER_CALL_STACK_SIZE_LIMIT]

                        results.append(handler(*args, **kwargs))

                        if ContinueEvaluating not in handler.modifiers:
                            if terminator_ruleset:
                                return

        if not ruleset_matches:
            self.status = WORKFLOW_FAILURE

            self.set_notification('PAGE_HANDLER_MISSING')

            self.logger.debug('THIS PAGE DID NOT MATCH ANY HANDLERS, REGULAR EXPRESSIONS MIGHT NEED TUNING')

