#!/usr/bin/env python3
"""Validate the versioned Sagamore radio station TSV with Python stdlib only."""
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "# sagamore-stations-v1"
HEADER = "id\tname\turl\tcountry\tgenre"
MAX_BYTES = 256 * 1024
MAX_ROWS = 2000
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(content: str) -> int:
    lines = content.splitlines()
    if len(content.encode("utf-8")) > MAX_BYTES:
        raise ValueError("catalog exceeds 256 KiB")
    if len(lines) < 2 or lines[0] != VERSION or lines[1] != HEADER:
        raise ValueError("unsupported catalog version or TSV header")

    ids: set[str] = set()
    count = 0
    for number, line in enumerate(lines[2:], start=3):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 5:
            raise ValueError(f"line {number}: expected 5 tab-separated fields")
        station_id, name, url, country, genre = fields
        if not (1 <= len(station_id) <= 64 and SLUG.fullmatch(station_id)):
            raise ValueError(f"line {number}: invalid id")
        if station_id in ids:
            raise ValueError(f"line {number}: duplicate id {station_id!r}")
        ids.add(station_id)
        for label, value, limit in [("name", name, 120), ("genre", genre, 80)]:
            if not value or len(value) > limit or any(ord(c) < 32 for c in value):
                raise ValueError(f"line {number}: invalid {label}")
        if not (len(country) == 2 and country.isascii() and country.isupper()
                and country.isalpha()):
            raise ValueError(f"line {number}: invalid country code")
        try:
            parsed = urlsplit(url)
            if (len(url) > 2048 or parsed.scheme not in ("http", "https")
                    or not parsed.hostname or parsed.username or parsed.password
                    or any(ch.isspace() or ord(ch) < 32 for ch in url)):
                raise ValueError("invalid stream URL")
        except ValueError as exc:
            raise ValueError(f"line {number}: invalid stream URL") from exc
        count += 1
        if count > MAX_ROWS:
            raise ValueError("catalog exceeds 2,000 stations")
    if not count:
        raise ValueError("catalog has zero valid stations")
    return count


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "stations/v1.tsv")
    try:
        count = validate(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Catalog invalid: {exc}", file=sys.stderr)
        return 1
    print(f"Catalog valid: {count} station(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
