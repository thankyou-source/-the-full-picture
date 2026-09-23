from pathlib import Path
from datetime import datetime, timezone
import json

DATA_FILE = Path("data/events.json")

def main():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    else:
        data = {
            "updated": None,
            "events": []
        }

    data["collector_checked_at"] = datetime.now(timezone.utc).isoformat()

    DATA_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("The Full Picture monitor completed successfully.")
    print(f"Events currently stored: {len(data['events'])}")

if __name__ == "__main__":
    main()
