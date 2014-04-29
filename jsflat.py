#!/usr/bin/env python3
# coding=utf-8

"""
Flattens JSON.

Nested JSON structures are flattened into a set of assignments, one per
line. This helps when trying to manually query with line-based tools
like grep.

For example:

  {
    "foo" : "bar",
    "baz" : [
      "quux",
      "zarf"
      ]
  }

turns into:

  foo = "bar"
  baz[0] = "quux"
  baz[1] = "zarf"

"""

import argparse
import json
import os
import sys
from pprint import pprint

__author__  = 'Laurence Gonsalves <laurence@xenomachina.com>'

def append_key(prefix, key):
    # TODO use subscript notaiton for unsafe keys
    if prefix:
        return prefix + '.' + key
    else:
        return key

def append_index(prefix, index):
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
            flatten(value, file, append_index(prefix, index))
    elif isinstance(js, str) or isinstance(js, int):
        file.write(append_value(prefix, json.dumps(js)))
        file.write('\n')
    else:
        assert False, "Don't know what to do with a %r!" % type(js)

class UserError(Exception):
  def __init__(self, message):
    self.message = message

def ParseArgs():
    parser = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    parser.add_argument('input',
            help="Input file name.",
            nargs='?')
    args = parser.parse_args()
    return args

def main(args):
    if args.input is not None:
        with open(args.input) as f:
            js = json.load(f)
    else:
        js = json.load(sys.stdin)
    flatten(js, file=sys.stdout)

if __name__ == '__main__':
    error = None
    try:
        main(ParseArgs())
    except FileExistsError as exc:
        error = '%s: %r' % (exc.strerror, exc.filename)
    except UserError as exc:
        error = exc.message

    if error is not None:
        program_name = os.path.basename(sys.argv[0], error)
        print(('%s: error: %s' % program_name), file=sys.stderr)
        sys.exit(1)
