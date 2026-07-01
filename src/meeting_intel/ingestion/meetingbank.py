import json
from pathlib import Path
from urllib.request import urlretrieve

from meeting_intel.core.config import Settings
from meeting_intel.ingestion.parsers import normalize_meetingbank_record
from meeting_intel.schemas import MeetingDocument

DEFAULT_SAMPLE = {
    "id": "sample-001",
    "title": "MeetingBank Sample Council Meeting",
    "transcript": (
        "Chair: We need to finalize the public works budget today.\n"
        "Member Lee: The bridge repair should remain the top priority.\n"
        "Member Patel: I agree, but the vendor timeline is a risk.\n"
        "Chair: Lee will confirm vendor availability by Friday."
    ),
    "summary": "The council discussed public works budget priorities and bridge repair risk.",
}


def download_meetingbank(settings: Settings, destination: Path | None = None) -> Path:
    """Download a MeetingBank JSON/JSONL file when MEETINGBANK_URL is configured.

    In OFFLINE_MODE or when no URL is configured, this writes a deterministic sample dataset.
    """
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = destination or data_dir / "meetingbank.jsonl"

    if settings.offline_mode or not settings.meetingbank_url:
        output_path.write_text(json.dumps(DEFAULT_SAMPLE) + "\n", encoding="utf-8")
        return output_path

    urlretrieve(settings.meetingbank_url, output_path)
    return output_path


def load_meetingbank(path: Path) -> list[MeetingDocument]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    records: list[dict]
    if raw.startswith("["):
        records = json.loads(raw)
    else:
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return [normalize_meetingbank_record(record) for record in records]


def ingest_meetingbank(settings: Settings, path: Path | None = None) -> list[MeetingDocument]:
    dataset_path = path or download_meetingbank(settings)
    return load_meetingbank(dataset_path)
