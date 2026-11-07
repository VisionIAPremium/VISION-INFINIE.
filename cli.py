"""Command-line interface for VISION INFINIE."""
import argparse
import json

from core.intelligence.engine import add_entry, list_entries, search_entries
from core.ai.orchestrator import AICore
from core.memory.store import MemoryStore
from core.governance.system_audit import run_audit


def main() -> int:
    parser = argparse.ArgumentParser(prog="vision-infinie", description="Local tools for VISION INFINIE.")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add a knowledge entry")
    add.add_argument("--title", required=True)
    add.add_argument("--content", required=True)
    add.add_argument("--tag", action="append", default=[])
    search = commands.add_parser("search", help="Search knowledge")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    commands.add_parser("list", help="List knowledge entries")
    commands.add_parser("audit", help="Run a read-only operational system audit")
    ask = commands.add_parser("ask", help="Ask the local AI Core")
    ask.add_argument("question")
    remember = commands.add_parser("remember", help="Save an authorized local memory")
    remember.add_argument("content")
    args = parser.parse_args()
    if args.command == "audit":
        report = run_audit()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["summary"]["FAIL"] else 0
    if args.command == "add":
        entry = add_entry(args.title, args.content, args.tag)
        print(f"Added {entry['id']}: {entry['title']}")
    elif args.command == "search":
        for entry in search_entries(args.query, args.limit):
            print(f"{entry['id']} | {entry['title']} | {', '.join(entry['tags'])}")
    elif args.command == "list":
        for entry in list_entries():
            print(f"{entry['id']} | {entry['title']}")
    elif args.command == "remember":
        item_id = MemoryStore().add(args.content)
        print(f"Saved local memory {item_id}")
    elif args.command == "ask":
        result = AICore(memory=MemoryStore()).ask(args.question)
        print(result["answer"])
        print(f"\\n[provider={result['provider']}; knowledge={result['knowledge_hits']}; memory={result['memory_hits']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
