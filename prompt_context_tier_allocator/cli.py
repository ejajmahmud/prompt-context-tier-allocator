"""CLI for Prompt Context Tier Allocator."""
import argparse
import json
from .core import ContextTierAllocator, ContextItem


def main():
    parser = argparse.ArgumentParser(description="Prompt Context Tier Allocator CLI")
    parser.add_argument("--budget", type=int, default=120, help="Total token budget")
    args = parser.parse_args()

    alloc = ContextTierAllocator(max_tokens=args.budget, reserve_output=20)
    res = alloc.allocate([
        ContextItem("rules", "AGENTS.md", tokens=35, priority=100, mandatory=True),
        ContextItem("ast", "Target AST slice", tokens=45, priority=85),
        ContextItem("logs", "Verbose build log", tokens=60, priority=15),
    ])
    print(json.dumps({
        "used_tokens": res["used_tokens"],
        "selected": [i.item_id for i in res["selected"]],
        "dropped": [i.item_id for i in res["dropped"]],
    }, indent=2))


if __name__ == "__main__":
    main()
