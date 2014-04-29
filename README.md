jsflat.py
=========

A simple tool for flattening JSON.

Nested JSON structures are flattened into a set of JavaScript assignments, one per
line. This helps when trying to manually query with line-based tools
like grep. Often the output is also easier to read, as you don't have to
mentally match up braces. Each line is one value along with its "fully
qualified name".

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
