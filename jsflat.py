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

def append_key(prefix, key):
    if VALID_IDENTIFIER_RE.match(key):
        if prefix:
            return prefix + '.' + key
        else:
            return key
    else:
        return append_subscript(prefix, key)

def append_subscript(prefix, index):
    return prefix + '[' + json.dumps(index) + ']'

def append_value(prefix, value):
    if prefix:
        return prefix + ' = ' + value
    else:
        return value

def flatten(js, file, prefix=''):
    if isinstance(js, dict):
        for key, value in sorted(js.items()):
            flatten(value, file, append_key(prefix, key))
    elif isinstance(js, list):
        for index, value in enumerate(js):
            flatten(value, file, append_subscript(prefix, index))
    elif isinstance(js, str) or isinstance(js, int):
        file.write(append_value(prefix, json.dumps(js)))
        file.write('\n')
    else:
        assert False, "Don't know what to do with a %r!" % type(js)

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
    flatten(js, file=sys.stdout)

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
