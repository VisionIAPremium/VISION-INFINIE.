"""Command-line interface for the VISION INFINIE foundation."""
import argparse
from core.intelligence.engine import add_entry, list_entries, search_entries

def main() -> int:
    parser = argparse.ArgumentParser(prog="vision-infinie", description="Local knowledge tools for VISION INFINIE.")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add a knowledge entry")
    add.add_argument("--title", required=True)
    add.add_argument("--content", required=True)
    add.add_argument("--tag", action="append", default=[])
    search = commands.add_parser("search", help="Search knowledge")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    commands.add_parser("list", help="List knowledge entries")
    args = parser.parse_args()
    if args.command == "add":
        entry = add_entry(args.title, args.content, args.tag)
        print(f"Added {entry['id']}: {entry['title']}")
    elif args.command == "search":
        for entry in search_entries(args.query, args.limit):
            print(f"{entry['id']} | {entry['title']} | {', '.join(entry['tags'])}")
    else:
        for entry in list_entries():
            print(f"{entry['id']} | {entry['title']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
