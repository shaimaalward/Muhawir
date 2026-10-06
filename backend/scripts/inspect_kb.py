from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config


def main():
    p = argparse.ArgumentParser(description="Inspect stored Muhawir KB chunks.")
    p.add_argument("--source", default=None, help="Filter by source_key")
    p.add_argument("--contains", default=None, help="Filter text containing a phrase")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()

    con = sqlite3.connect(config.KB_PATH)
    con.row_factory = sqlite3.Row
    clauses=[]
    values=[]
    if args.source:
        clauses.append("source_key = ?")
        values.append(args.source)
    if args.contains:
        clauses.append("text LIKE ?")
        values.append(f"%{args.contains}%")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = con.execute(
        "SELECT id, source_key, source_type, title, source_url, text FROM documents" + where + " ORDER BY source_key, id LIMIT ?",
        (*values, args.limit),
    ).fetchall()
    print(f"KB: {config.KB_PATH}")
    print(f"Rows shown: {len(rows)}\n")
    for i,row in enumerate(rows,1):
        print(f"[{i}] {row['source_key']} / {row['source_type']} / {row['title']}")
        print(row['source_url'])
        print(row['text'][:1200])
        print("-"*80)

if __name__ == "__main__":
    main()
