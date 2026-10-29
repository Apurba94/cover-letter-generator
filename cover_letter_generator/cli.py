"""Command-line interface for cover-letter-generator."""
import argparse
import json
import sys

from .core import TEMPLATES, render, validate


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cover-letter-generator", description="Generate a journal cover letter.")
    ap.add_argument("metadata", help="JSON file with letter fields (see examples/initial.json)")
    ap.add_argument("-t", "--type", choices=sorted(TEMPLATES), default="initial")
    ap.add_argument("--template", help="custom template file using $field placeholders")
    ap.add_argument("-o", "--output")
    ap.add_argument("--strict", action="store_true", help="fail if validation finds problems")
    args = ap.parse_args(argv)
    with open(args.metadata, encoding="utf-8") as fh:
        meta = json.load(fh)
    problems = validate(meta, args.type)
    for p in problems:
        print("warning: " + p, file=sys.stderr)
    if problems and args.strict:
        return 1
    if args.template:
        with open(args.template, encoding="utf-8") as fh:
            TEMPLATES["custom"] = fh.read()
        text = render(meta, "custom")
    else:
        text = render(meta, args.type)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0
