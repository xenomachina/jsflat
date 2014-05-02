#!/usr/bin/env python3
# coding=utf-8

"""
Flattens JSON-like structures.

Nested JSON-like structures are flattened into a sequence of name-value pairs.
Names use a JSON-like syntax.
"""

import re
import sys

__author__  = 'Laurence Gonsalves <laurence@xenomachina.com>'

# This is intentionally very conservative. There are many valid JavaScript
# identifiers that are not matched by this, but that's okay -- we'll just use
# subscript notation for them.
VALID_IDENTIFIER_RE = re.compile(r'^[$A-Za-z_][$A-Za-z_0-9]*$')

class Flattener:
    def __init__(self, repr=repr):
        self.__repr = repr

    def _add_key(self, prefix, key):
        if VALID_IDENTIFIER_RE.match(key):
            if prefix:
                return prefix + '.' + key
            else:
                return key
        else:
            return self._add_subscript(prefix, key)

    def _add_subscript(self, prefix, index):
        return prefix + '[' + self.__repr(index) + ']'

    def flatten(self, x, prefix=''):
        if isinstance(x, dict):
            for key, value in sorted(x.items()):
                for item in self.flatten(value, self._add_key(prefix, key)):
                    yield item
        elif isinstance(x, list):
            for index, value in enumerate(x):
                for item in self.flatten(value,
                        self._add_subscript(prefix, index)):
                    yield item
        else:
            yield (prefix, x)
