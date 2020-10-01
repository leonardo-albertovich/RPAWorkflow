from .actions import *
from .rule import *

class RuleSet(list):
    def __init__(self, *args, **kwargs):
        for rule in args:
            if not isinstance(rule, Rule):
                raise ValueError('Incorrect rule element [%s]' % (str(rule)))

        self.rules = args
        self.modifiers = []
        self.dependencies = []

        if 'modifiers' in kwargs:
            self.modifiers = kwargs['modifiers']

        if 'dependencies' in kwargs:
            self.dependencies = kwargs['dependencies']

        for modifier in self.modifiers:
            if modifier not in [ContinueEvaluating, StopEvaluating]:
                raise ValueError('Invalid ruleset modifier %s' % (str(modifier)))

        if StopEvaluating not in self.modifiers and ContinueEvaluating not in self.modifiers:
            self.modifiers.append(StopEvaluating)
