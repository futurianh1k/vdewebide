import json
from pathlib import Path
import sys
from fastapi.testclient import TestClient

# Make `services/gateway` importable when running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app

OUT = ROOT / "openapi" / "openapi.json"

def main():
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated: {OUT}")

if __name__ == "__main__":
    main()
