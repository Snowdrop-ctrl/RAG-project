"""Command line helpers: `uv run python -m app.cli ingest [path]`, `list`, `clear`."""

import argparse
import sys
from pathlib import Path

from app.config import settings
from app.services import ingest, vector_store


def cmd_ingest(target: Path) -> int:
    if not target.exists():
        print(f"Not found: {target}", file=sys.stderr)
        return 1

    results = [ingest.ingest_path(target)] if target.is_file() else ingest.ingest_directory(target)
    if not results:
        print(f"No supported files in {target} ({', '.join(sorted(ingest.SUPPORTED_EXTENSIONS))})")
        return 1

    for r in results:
        print(f"  {r.source}: {r.chunks} chunks")
    print(f"Indexed {len(results)} file(s); {vector_store.count()} chunks total.")
    return 0


def cmd_list() -> int:
    docs = vector_store.list_sources()
    if not docs:
        print("No documents indexed yet.")
        return 0
    for d in docs:
        print(f"  {d['source']}: {d['chunks']} chunks")
    return 0


def cmd_clear() -> int:
    vector_store.reset()
    print("Index cleared.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="app.cli", description="RAG document index tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Index a file or a folder of files")
    p_ingest.add_argument("path", nargs="?", default=settings.docs_dir, type=Path)

    sub.add_parser("list", help="List indexed documents")
    sub.add_parser("clear", help="Delete everything from the index")

    args = parser.parse_args()
    if args.command == "ingest":
        return cmd_ingest(args.path)
    if args.command == "list":
        return cmd_list()
    return cmd_clear()


if __name__ == "__main__":
    raise SystemExit(main())
