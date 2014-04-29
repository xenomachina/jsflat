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
    # TODO: actually flatten
    pprint(js)

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
