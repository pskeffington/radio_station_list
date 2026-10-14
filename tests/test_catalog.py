"""Schema tests for the public station manifest."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_catalog import validate  # noqa: E402

HEADER = "# sagamore-stations-v1\nid\tname\turl\tcountry\tgenre\n"
STATION = "skylab-uk\tSkylab Radio (UK)\thttps://example.org/live\tGB\tAmbient\n"


class CatalogTests(unittest.TestCase):
    def test_canonical_file(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "stations" / "v1.tsv").read_text(encoding="utf-8")
        self.assertGreaterEqual(validate(text), 1)

    def test_example_valid(self):
        self.assertEqual(validate(HEADER + STATION), 1)

    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(HEADER + STATION + STATION)

    def test_invalid_scheme(self):
        with self.assertRaisesRegex(ValueError, "stream URL"):
            validate(HEADER + STATION.replace("https://example.org/live", "file:///etc/passwd"))

    def test_invalid_id(self):
        with self.assertRaisesRegex(ValueError, "invalid id"):
            validate(HEADER + STATION.replace("skylab-uk", "../unsafe"))

    def test_empty(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            validate(HEADER)

    def test_incorrect_header(self):
        with self.assertRaisesRegex(ValueError, "header"):
            validate(HEADER.replace("genre", "category") + STATION)


if __name__ == "__main__":
    unittest.main()
