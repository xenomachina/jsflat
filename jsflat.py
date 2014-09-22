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

You can also add prefixes which will be converted just like JavaScript
attribute names and pre-pended onto each line. For example:

    jsflat.py --prefix hello --prefix ":-)" --prefix world < input

Will generate lines like:

    hello[":-)"].world.baz[0] = "quux"
    hello[":-)"].world.baz[1] = "snoo"
    hello[":-)"].world.foo = "bar"
"""

import argparse
import json
import re
import sys
import flatten

__author__  = 'Laurence Gonsalves <laurence@xenomachina.com>'


class UserError(Exception):
  def __init__(self, message):
    self.message = message

def create_parser():
    description, epilog = __doc__.strip().split('\n', 1)
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--prefix', default=[], action='append',
            help="Prefix for all output lines.")
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
    while args.prefix:
        js = {args.prefix.pop(): js}
    for name, value in flatten.Flattener(json.dumps).flatten(js):
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
