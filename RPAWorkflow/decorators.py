from .actions import *


class exception_handler(object):
    def __init__(self, priority=None, exceptions=None, invocation_limit=None, dependencies=None):
        self.exceptions       = exceptions       or []
        self.priority         = priority         or Priority.Lowest
        self.dependencies     = dependencies     or []
        self.invocation_limit = invocation_limit or 999999

    def __call__(self, f):
        f.exceptions       = self.exceptions
        f.priority         = self.priority
        f.dependencies     = self.dependencies
        f.invocation_count = 0
        f.invocation_limit = self.invocation_limit

        return f

class document_handler(object):
    def __init__(self, priority=None, rulesets=None, invocation_limit=None, modifiers=None, dependencies=None):
        self.rulesets         = rulesets         or []
        self.priority         = priority         or Priority.Lowest
        self.modifiers        = modifiers        or []
        self.dependencies     = dependencies     or []
        self.invocation_limit = invocation_limit or 999999

        for modifier in self.modifiers:
            if modifier not in [ContinueEvaluating, StopEvaluating]:
                raise ValueError('Invalid ruleset modifier %s' % (str(modifier)))

    def __call__(self, f):
        f.rulesets         = self.rulesets
        f.priority         = self.priority
        f.modifiers        = self.modifiers
        f.dependencies     = self.dependencies
        f.invocation_count = 0
        f.invocation_limit = self.invocation_limit

        return f
