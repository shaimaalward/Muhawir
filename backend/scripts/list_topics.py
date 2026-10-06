from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]/"knowledge"/"topics"
for p in sorted(ROOT.glob("*.json")):
    d=json.loads(p.read_text(encoding="utf-8"))
    print(f"{d.get('key',p.stem):24} {d.get('title_ar','')}")
