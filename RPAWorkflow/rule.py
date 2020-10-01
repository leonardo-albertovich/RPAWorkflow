from .modifiers import *

class Rule(object):
    sequence = 0

    def __init__(self, rule_text, *rule_modifiers):
        if type(rule_text) != str:
            raise ValueError('Invalid rule text value')

        for rule_modifier in rule_modifiers:
            if rule_modifier not in [Mandatory, Optional, PlainText, CaseLess, Regex, Inverse, Body, Url]:
                raise ValueError('Invalid rule modifier %s' % (str(rule_modifier)))

        Rule.sequence += 1

        self.rule_id = Rule.sequence
        self.rule_text = rule_text
        self.rule_modifiers = list(rule_modifiers)

        if Mandatory not in self.rule_modifiers and Optional not in self.rule_modifiers:
            self.rule_modifiers.append(Mandatory)

        if Regex not in self.rule_modifiers and PlainText not in self.rule_modifiers:
            self.rule_modifiers.append(Regex)

        if Url not in self.rule_modifiers and Body not in self.rule_modifiers:
            self.rule_modifiers.append(Body)
