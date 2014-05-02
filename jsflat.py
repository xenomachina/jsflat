#!/usr/bin/env python3
# coding=utf-8

"""
Flattens JSON.

Nested JSON structures are flattened into a set of assignments, one per
line. This helps when trying to manually query with line-based tools
like grep.

For example:

    {
        "baz" : [
            "quux",
            "snoo"
            ],
        "foo" : "bar",
        "zarf" : {
            "albatross" : 42,
            "giant panda" : 2048,
            "zebra" : 1500
            }
    }

turns into:

    baz[0] = "quux"
    baz[1] = "snoo"
    foo = "bar"
    zarf.albatross = 42
    zarf["giant panda"] = 2048
    zarf.zebra = 1500

"""

import argparse
import json
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

class UserError(Exception):
  def __init__(self, message):
    self.message = message

def create_parser():
    description, epilog = __doc__.strip().split('\n', 1)
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input',
            help="Input file name. If not provided, input is read from stdin.",
            nargs='?')
    return parser

def main(args):
    if args.input is not None:
        with open(args.input) as f:
            js = json.load(f)
    else:
        js = json.load(sys.stdin)
    for name, value in Flattener(json.dumps).flatten(js):
        if isinstance(value, str) or isinstance(value, int):
            value = json.dumps(value)
        else:
            assert False, "Don't know what to do with a %r!" % type(value)
        if name:
            print(name + ' = ' + value)
        else:
            print(value)

if __name__ == '__main__':
    error = None
    parser = create_parser()
    try:
        main(parser.parse_args())
    except FileExistsError as exc:
        error = '%s: %r' % (exc.strerror, exc.filename)
    except UserError as exc:
        error = exc.message

    if error is not None:
        print(('%s: error: %s' % (parser.prog, error)), file=sys.stderr)
        sys.exit(1)
